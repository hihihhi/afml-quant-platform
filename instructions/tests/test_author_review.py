"""Check the CH-01 author-note coverage record without granting review approval."""
from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class AuthorReviewCoverageTests(unittest.TestCase):
    def test_notes_match_all_chapter_tasks_in_order(self):
        catalog = json.loads((ROOT / 'instructions/01-source/public_tasks.json').read_text())
        rows = [dict(zip(catalog['columns'], row, strict=True)) for row in catalog['rows']]
        expected = [row['id'] for row in rows if row['document'] == 'OPS/c01.xhtml']
        record = json.loads((ROOT / 'instructions/reviews/ch-01/SOURCE_COVERAGE.json').read_text())
        notes = (ROOT / record['notes_path']).read_bytes()
        self.assertEqual(hashlib.sha256(notes).hexdigest(), record['notes_sha256'])
        self.assertEqual(record['covered_task_ids'], expected)
        self.assertEqual(re.findall(r'^### (\S+)$', notes.decode(), re.MULTILINE), expected)
        expected_locators = [{key: row[key] for key in
                             ('id', 'document', 'anchor', 'position', 'position_end_exclusive')}
                             for row in rows if row['document'] == 'OPS/c01.xhtml']
        self.assertEqual(record['source_locators'], expected_locators)
        self.assertEqual(record['source_epub_sha256'], catalog['source_epub_sha256'])

    def test_author_notes_do_not_claim_independent_approval(self):
        record = json.loads((ROOT / 'instructions/reviews/ch-01/SOURCE_COVERAGE.json').read_text())
        self.assertEqual(record['status'], 'author_review_draft')
        self.assertIs(record['independent_semantic_approval'], False)
        self.assertIs(record['independent_mathematical_approval'], False)


if __name__ == '__main__':
    unittest.main()
