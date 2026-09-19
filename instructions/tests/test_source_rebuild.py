"""Source-free roundtrip fixtures and private-output rebuild boundary tests."""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZipInfo

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'instructions/tools'))
from rebuild_private_source import numbered_blueprints, private_destination
from source_build.crosscheck import Audit, check_source, check_word, visible, xml
from source_build.export_word import WordExporter
from source_build.inventory_epub import extract_source

def make_epub(path: Path) -> None:
    """Small source fixture with text, comments, math image, table and native code."""
    picture = io.BytesIO()
    Image.new('RGB', (20, 10), 'white').save(picture, format='PNG')
    body = '''<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Fixture</title></head><body><section><h1><span epub:type="pagebreak" id="Page_1" title="1"/>CHAPTER 1 Test</h1><section id="s1"><h2>1.1 Exact text</h2><p>Alpha <i>x</i><sub>1</sub> &amp; beta.</p><p><!-- <math location="c01_M0001.png"><mi>x</mi></math> --><img src="images/c01_M0001.png" alt="x"/></p><pre><code>def f(x):
    return x + 1
</code></pre><ol class="none"><li>No added number.</li></ol><ol><li>First<ol class="lower-latin"><li>Child</li></ol></li></ol><table><tr><td>Column</td><td>Value</td></tr><tr><td>A</td><td>1</td></tr></table></section></section></body></html>'''
    with ZipFile(path, 'w') as archive:
        archive.writestr('mimetype', 'application/epub+zip')
        archive.writestr('META-INF/container.xml', '<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles><rootfile full-path="OPS/book.opf"/></rootfiles></container>')
        archive.writestr('OPS/book.opf', '<package xmlns="http://www.idpf.org/2007/opf"><metadata/><manifest><item id="chapter" href="c01.xhtml" media-type="application/xhtml+xml"/></manifest><spine><itemref idref="chapter"/></spine></package>')
        archive.writestr('OPS/c01.xhtml', body)
        archive.writestr('OPS/images/c01_M0001.png', picture.getvalue())


class PrivateRebuildBoundaryTests(unittest.TestCase):
    def test_valid_destination(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            self.assertEqual(private_destination(root, 'source-v1'),
                             root / 'instructions/01-source/private/rebuilds/source-v1')

    def test_invalid_name(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in ['', '.', '..', '../public', '/tmp/output', 'nested/path', 'a' * 81]:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    private_destination(Path(folder), name)

    def test_existing_build_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            target = private_destination(root, 'existing')
            target.mkdir(parents=True)
            marker = target / 'note.md'
            marker.write_text('retain')
            with self.assertRaises(FileExistsError):
                private_destination(root, 'existing')
            self.assertEqual(marker.read_text(), 'retain')

    def test_symlink_parent_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / 'project'
            (root / 'instructions/01-source').mkdir(parents=True)
            external = Path(folder) / 'outside'
            external.mkdir()
            (root / 'instructions/01-source/private').symlink_to(external, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symlinks'):
                private_destination(root, 'bad')

    def test_complete_blueprints_reused(self):
        catalog = json.loads((ROOT / 'instructions/01-source/public_tasks.json').read_text())
        result = numbered_blueprints(catalog)
        self.assertEqual(len(result), 280)
        self.assertEqual(set(result['1.1']), {'work', 'caution'})

    def test_incomplete_blueprints_rejected(self):
        with self.assertRaises(ValueError):
            numbered_blueprints({'columns': ['id', 'work', 'caution'], 'rows': [['S-1.1', 'draft', 'pending']]})


class SourceRoundtripTests(unittest.TestCase):
    def fixture(self, root):
        epub = root / 'fixture.epub'
        make_epub(epub)
        workspace = root / 'workspace'
        with contextlib.redirect_stdout(io.StringIO()):
            extract_source(epub, workspace)
            word = workspace / 'instructions/01-source/private/AFML_Source_Transcription.docx'
            WordExporter(workspace).export(word)
        return workspace, {'source_epub_sha256': hashlib.sha256(epub.read_bytes()).hexdigest()}

    def test_text_image_math_table_code_roundtrip(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace, lock = self.fixture(Path(folder))
            audit = Audit()
            parsed = check_source(workspace, audit, lock)
            check_word(workspace, audit, parsed)
            self.assertTrue(audit.result()['passed'], audit.result())
            self.assertFalse(audit.result()['mathematical_review_complete'])

    def test_tampered_source_asset_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            workspace, lock = self.fixture(Path(folder))
            asset = workspace / 'instructions/01-source/private/epub/OPS/images/c01_M0001.png'
            asset.write_bytes(b'altered')
            audit = Audit()
            check_source(workspace, audit, lock)
            self.assertFalse(audit.result()['passed'])

    def test_entities_rejected(self):
        with self.assertRaises(ValueError):
            xml(b'<!DOCTYPE a [<!ENTITY x "expansion">]><a>&x;</a>')

    def test_comments_are_not_visible(self):
        node = xml(b'<p xmlns="http://www.w3.org/1999/xhtml">A<!-- hidden math --><b>B</b>C<br/>D</p>')
        self.assertEqual(visible(node), 'ABC\nD')

    def test_audit_never_masks_failures(self):
        audit = Audit()
        audit.check('one', False)
        audit.check('two', True)
        self.assertFalse(audit.result()['passed'])
        self.assertEqual(audit.result()['failed_check_count'], 1)

    def test_zip_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            epub = root / 'bad.epub'
            with ZipFile(epub, 'w') as archive:
                archive.writestr('../outside.txt', 'no')
            with self.assertRaises(ValueError):
                extract_source(epub, root / 'workspace')
            self.assertFalse((root / 'outside.txt').exists())

    def test_zip_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            epub = root / 'bad.epub'
            with ZipFile(epub, 'w') as archive:
                entry = ZipInfo('link')
                entry.external_attr = 0o120777 << 16
                archive.writestr(entry, '/outside')
            with self.assertRaises(ValueError):
                extract_source(epub, root / 'workspace')


if __name__ == '__main__':
    unittest.main()
