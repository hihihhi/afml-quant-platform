"""Adversarial regression tests for the public task projection and numerical oracle."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'instructions/tools'))
sys.path.insert(0, str(ROOT / 'system/reference'))
from audit_public_view import audit, verify_source
from render_public_tasks import build, safe_path
from covariance_counterexample import counterexample, determinant, sample_covariance
from install_source import install
from validate_review import errors_for


class PublicViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        shutil.copytree(ROOT / 'instructions', cls.root / 'instructions',
                        ignore=shutil.ignore_patterns('private', '__pycache__', 'task-context'))
        for name in ('AGENTS.md',):
            shutil.copyfile(ROOT / name, cls.root / name)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    @contextlib.contextmanager
    def altered(self, relative, content):
        path = self.root / relative
        old = path.read_bytes() if path.exists() else None
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        try:
            yield path
        finally:
            if old is None:
                path.unlink()
            else:
                path.write_bytes(old)

    def test_public_view(self):
        result = audit(self.root)
        self.assertTrue(result['passed'], result['errors'])
        self.assertEqual(result['task_count'], 1138)
        self.assertFalse(result['semantic_approval'])

    def test_exact_regeneration(self):
        for name, data in build(self.root).items():
            self.assertEqual((self.root / name).read_bytes(), data, name)

    def test_prompt_tampering(self):
        with self.altered('instructions/00-governance/INITIAL_PROMPT.md', b'changed'):
            self.assertFalse(audit(self.root)['passed'])

    def test_changed_task(self):
        with self.altered('instructions/02-book/ch-01/README.md', b'approved'):
            self.assertFalse(audit(self.root)['passed'])

    def test_missing_task(self):
        path = self.root / 'instructions/02-book/ch-01/README.md'
        old = path.read_bytes()
        path.unlink()
        try:
            self.assertFalse(audit(self.root)['passed'])
        finally:
            path.write_bytes(old)

    def test_catalog_tampering(self):
        path = 'instructions/01-source/public_tasks.json'
        value = json.loads((self.root / path).read_text())
        value['rows'][0][1] = 'FAKE'
        with self.altered(path, json.dumps(value).encode()):
            self.assertFalse(audit(self.root)['passed'])

    def test_false_approval(self):
        path = 'instructions/02-book/task_index.json'
        value = json.loads((self.root / path).read_text())
        value['semantic_approvals'] = 1138
        with self.altered(path, json.dumps(value).encode()):
            self.assertFalse(audit(self.root)['passed'])

    def test_book_cannot_be_published(self):
        with self.altered('book.epub', b'private'):
            self.assertFalse(audit(self.root)['passed'])

    def test_private_directory_rejected(self):
        with self.altered('instructions/01-source/private/secret.txt', b'private'):
            self.assertFalse(audit(self.root)['passed'])

    def test_path_escape(self):
        with self.assertRaises(ValueError):
            safe_path(self.root, '../outside.md')
        with self.assertRaises(ValueError):
            safe_path(self.root, '/tmp/outside.md')

    def test_refuses_edited_task_overwrite(self):
        with self.altered('instructions/02-book/ch-01/README.md', b'edited'):
            with self.assertRaises(FileExistsError):
                build(self.root, write=True)

    def test_wrong_epub(self):
        with self.altered('wrong.txt', b'not the book') as wrong:
            with self.assertRaises(ValueError):
                install(self.root, wrong)
            with self.assertRaises(ValueError):
                verify_source(self.root, wrong)

    def test_fake_approval_record(self):
        record = {'schema_version': 1, 'status': 'approved', 'task_id': 'CH-01',
                  'implementer': 'same', 'reviewer': 'same', 'gates': {}, 'blockers': []}
        self.assertTrue(errors_for(record, self.root))


class NumericalOracleTests(unittest.TestCase):
    def test_exact_counterexample(self):
        result = counterexample()
        self.assertEqual(result['determinant'], '1/108')
        self.assertFalse(result['publisher_confirmation'])

    def test_covariance_entries(self):
        covariance = sample_covariance([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
        self.assertEqual(covariance[0][0], Fraction(1, 4))
        self.assertEqual(covariance[0][1], Fraction(-1, 12))
        self.assertEqual(determinant(covariance), Fraction(1, 108))

    def test_float_rejection(self):
        with self.assertRaises(TypeError):
            sample_covariance([[1.0], [2.0]])
        with self.assertRaises(TypeError):
            determinant([[1.0]])

    def test_pivot_and_singular(self):
        self.assertEqual(determinant([[0, 1], [1, 0]]), -1)
        self.assertEqual(determinant([[1, 1], [1, 1]]), 0)
        self.assertEqual(determinant([]), 1)

    def test_invalid_shape(self):
        with self.assertRaises(ValueError):
            determinant([[1, 2]])
        with self.assertRaises(ValueError):
            sample_covariance([[1]])


if __name__ == '__main__':
    unittest.main()
