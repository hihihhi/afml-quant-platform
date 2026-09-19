"""Fail-closed provenance checks before private source is put in agent packets."""
from __future__ import annotations

import contextlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'instructions/tools'))
from build_task_context import build, read_project_file, verified_task


class TaskContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        shutil.copytree(ROOT / 'instructions', cls.root / 'instructions',
                        ignore=shutil.ignore_patterns('private', '__pycache__', 'task-context'))
        shutil.copyfile(ROOT / 'AGENTS.md', cls.root / 'AGENTS.md')

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    @contextlib.contextmanager
    def altered(self, relative, data):
        path = self.root / relative
        original = path.read_bytes()
        path.write_bytes(data)
        try:
            yield
        finally:
            path.write_bytes(original)

    def test_valid_source_locator(self):
        lock, record = verified_task(self.root, 'CH-01')
        self.assertEqual(record['document'], 'OPS/c01.xhtml')
        self.assertEqual(len(lock['authority_files']), 3)

    def test_unknown_task(self):
        with self.assertRaises(ValueError):
            verified_task(self.root, 'NOT-A-BOOK-TASK')

    def test_altered_prompt(self):
        with self.altered('instructions/00-governance/FOLLOWUP_PROMPT.md', b'changed'):
            with self.assertRaisesRegex(ValueError, 'Prompt lock'):
                verified_task(self.root, 'CH-01')

    def test_altered_catalog(self):
        with self.altered('instructions/01-source/public_tasks.json', b'{}'):
            with self.assertRaisesRegex(ValueError, 'Catalog'):
                verified_task(self.root, 'CH-01')

    def test_altered_index(self):
        with self.altered('instructions/02-book/task_index.json', b'{}'):
            with self.assertRaisesRegex(ValueError, 'deterministic'):
                verified_task(self.root, 'CH-01')

    def test_altered_markdown(self):
        with self.altered('instructions/02-book/ch-01/README.md', b'silently changed'):
            with self.assertRaisesRegex(ValueError, 'deterministic'):
                verified_task(self.root, 'CH-01')

    def test_inconsistent_source_lock(self):
        name = 'instructions/01-source/PUBLICATION_LOCK.json'
        value = json.loads((self.root / name).read_text())
        value['source_epub_sha256'] = '0' * 64
        with self.altered(name, json.dumps(value).encode()):
            with self.assertRaisesRegex(ValueError, 'Source identity'):
                verified_task(self.root, 'CH-01')

    def test_packet_cannot_escape_private_output(self):
        with self.assertRaises(ValueError):
            build(self.root, 'CH-01', self.root / 'public-chapter.md')
        with self.assertRaises(ValueError):
            build(self.root, 'CH-01', self.root / 'instructions/task-context')

    def test_existing_packet_not_overwritten(self):
        target = self.root / 'instructions/task-context/existing.md'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('original')
        try:
            with self.assertRaises(FileExistsError):
                build(self.root, 'CH-01', target)
            self.assertEqual(target.read_text(), 'original')
        finally:
            target.unlink()

    def test_input_escape_and_symlink(self):
        with self.assertRaises(ValueError):
            read_project_file(self.root, '../outside')
        alias = self.root / 'linked-contract.md'
        alias.symlink_to(self.root / 'AGENTS.md')
        try:
            with self.assertRaisesRegex(ValueError, 'symlinks'):
                read_project_file(self.root, 'linked-contract.md')
        finally:
            alias.unlink()


if __name__ == '__main__':
    unittest.main()
