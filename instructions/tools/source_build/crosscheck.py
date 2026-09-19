#!/usr/bin/env python3
"""Independently audit source preservation and drafted MD coverage.

Uses ElementTree rather than importing the lxml producer. PASS is structural, not
semantic or mathematical approval. Reports explicitly retain unresolved review work.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from PIL import Image

H = '{http://www.w3.org/1999/xhtml}'
O = '{http://www.idpf.org/2007/opf}'
E = '{http://www.idpf.org/2007/ops}'
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def xml(data: bytes) -> ET.Element:
    # Sources are already bounded local files. Reject entity definitions explicitly.
    if b'<!ENTITY' in data.upper():
        raise ValueError('Custom XML entity declarations are not accepted.')
    return ET.fromstring(data, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))


def visible(node: ET.Element) -> str:
    if not isinstance(node.tag, str):
        return ''
    pieces = [node.text or '']
    for child in node:
        pieces.append('\n' if child.tag == H + 'br' else visible(child))
        pieces.append(child.tail or '')
    return ''.join(pieces)


def normalized(text: str) -> str:
    return ' '.join(text.split())


def without_whitespace(text: str) -> str:
    return ''.join(text.split())


def resolve(document: str, href: str) -> str:
    split = urlsplit(href)
    if split.scheme or split.netloc:
        raise ValueError('Expected a local source path.')
    return posixpath.normpath(posixpath.join(posixpath.dirname(document), unquote(split.path))) if split.path else document


class Audit:
    """Collect checks without hiding a failure behind successful later checks."""

    def __init__(self) -> None:
        self.checks: list[dict[str, Any]] = []
        self.limits: dict[str, Any] = {}

    def check(self, name: str, condition: bool, **details: Any) -> None:
        self.checks.append({'name': name, 'passed': bool(condition), **details})

    def result(self) -> dict[str, Any]:
        return {
            'schema_version': 1,
            'scope': 'machine-checkable source preservation and drafted-task coverage',
            'passed': all(check['passed'] for check in self.checks),
            'check_count': len(self.checks),
            'failed_check_count': sum(not check['passed'] for check in self.checks),
            'checks': self.checks,
            'limits': self.limits,
            'semantic_review_complete': False,
            'mathematical_review_complete': False,
            'implementation_complete': False,
            'remote_repository_verification': 'NOT_IN_SCOPE',
        }


def check_locks(root: Path, audit: Audit) -> dict[str, Any]:
    lock = read_json(root / 'instructions/00-governance/REQUIREMENTS_LOCK.json')
    for relative, expected in lock['authority_files'].items():
        path = root / relative
        audit.check('prompt_lock:' + relative, path.is_file() and digest(path.read_bytes()) == expected)
    requirements = (root / 'instructions/00-governance/REQUIREMENTS.md').read_text(encoding='utf-8')
    audit.check('requirement_ids_present', all(identifier in requirements for identifier in lock['required_requirement_ids']), count=len(lock['required_requirement_ids']))
    return lock


def check_source(root: Path, audit: Audit, lock: dict[str, Any]) -> dict[str, Any]:
    source = root / 'instructions/01-source'
    archive_path = source / 'private/original.epub'
    archive_bytes = archive_path.read_bytes()
    manifest = read_json(source / 'manifest.json')
    audit.check('source_epub_hash', digest(archive_bytes) == lock['source_epub_sha256'] == manifest['source_sha256'])
    expected_members = read_json(source / 'archive_members.json')
    expected_spine = read_json(source / 'spine.json')
    expected_headings = read_json(source / 'headings.json')
    headings: list[tuple[str, str, str]] = []
    pages: list[tuple[str, str, str]] = []
    images: list[tuple[str, str]] = []
    hyperlinks: list[tuple[str, str]] = []
    native_code: list[str] = []
    body_text: list[str] = []
    math_fragments: list[str] = []
    snippet_titles: list[str] = []
    table_count = 0
    source_anchors: set[tuple[str, str]] = set()
    with ZipFile(io.BytesIO(archive_bytes)) as archive:
        actual_files = [item for item in archive.infolist() if not item.is_dir()]
        audit.check('archive_member_set', {item.filename for item in actual_files} == {item['path'] for item in expected_members}, count=len(actual_files))
        bad_members = [item['path'] for item in expected_members if digest(archive.read(item['path'])) != item['sha256'] or not (source / 'private/epub' / item['path']).is_file() or (source / 'private/epub' / item['path']).read_bytes() != archive.read(item['path'])]
        audit.check('archive_and_extracted_bytes', not bad_members, mismatches=bad_members)
        container = xml(archive.read('META-INF/container.xml'))
        package_path = next(item.attrib['full-path'] for item in container.iter() if isinstance(item.tag, str) and item.tag.endswith('rootfile'))
        package = xml(archive.read(package_path))
        items = {node.attrib['id']: node for node in package.findall(O + 'manifest/' + O + 'item')}
        spine = [resolve(package_path, items[node.attrib['idref']].attrib['href']) for node in package.findall(O + 'spine/' + O + 'itemref')]
        audit.check('spine_order', spine == [item['path'] for item in expected_spine], count=len(spine))
        for member in spine:
            tree = xml(archive.read(member))
            body = tree.find(H + 'body')
            if body is None:
                raise ValueError(f'Missing body in {member}')
            text = visible(body)
            body_text.append(text)
            saved_text = source / 'private/text' / (Path(member).stem + '.txt')
            audit.check('visible_text_file:' + member, saved_text.read_text(encoding='utf-8') == text)
            for node in body.iter():
                if node.tag is ET.Comment:
                    math_fragments.extend(re.findall(r'<math\b.*?</math>', node.text or '', re.S))
                    continue
                if not isinstance(node.tag, str):
                    continue
                tag = node.tag.removeprefix(H)
                if node.get('id'):
                    source_anchors.add((member, node.attrib['id']))
                if tag in {'h1', 'h2', 'h3', 'h4', 'h5', 'h6'}:
                    title = normalized(visible(node))
                    headings.append((member, tag, title))
                    if re.match(r'^snippet\s+\d', title, re.I):
                        snippet_titles.append(title)
                if node.get(E + 'type') == 'pagebreak':
                    pages.append((member, node.get('id', ''), node.get('title') or node.get('id', '')))
                if tag == 'img':
                    images.append((member, resolve(member, node.get('src', ''))))
                if tag == 'a' and node.get('href'):
                    hyperlinks.append((member, node.attrib['href']))
                if tag == 'pre':
                    native_code.append(visible(node))
                table_count += tag == 'table'
        audit.check('heading_sequence_and_text', headings == [(item['document'], item['tag'], item['title']) for item in expected_headings], count=len(headings))
        numeric = [title for member, _, title in headings if re.match(r'^\d+(?:\.(?:\d+|A))+\s', title) and re.match(r'c\d+$', Path(member).stem)]
        audit.check('numbered_heading_coverage', len(numeric) == manifest['numbered_section_count'], count=len(numeric))
        audit.check('page_marker_sequence', pages == [(item['document'], item['anchor'], item['label']) for item in read_json(source / 'pages.json')], count=len(pages))
        audit.check('image_placement_sequence', images == [(item['document'], item['asset']) for item in read_json(source / 'images.json')], count=len(images))
        math_inventory = read_json(source / 'formulas.json')
        audit.check('commented_mathml_sequence', math_fragments == [item['mathml'] for item in math_inventory], count=len(math_fragments))
        audit.check('snippet_title_sequence', snippet_titles == [item['title'] for item in read_json(source / 'snippets.json')], count=len(snippet_titles))
        audit.check('native_table_count', table_count == len(read_json(source / 'tables.json')), count=table_count)
        numeric_pages = {int(label) for _, _, label in pages if label.isdigit()}
        absent_pages = sorted(set(range(min(numeric_pages), max(numeric_pages) + 1)) - numeric_pages)
        audit.limits['unmarked_numeric_page_labels'] = absent_pages
        audit.limits['unmarked_pages_interpretation'] = 'Boundary markers absent; not evidence that corresponding text is missing.'
        equation_assets = {item['asset'] for item in read_json(source / 'images.json') if item['kind'] in {'inline_equation', 'display_equation'}}
        math_assets = {item['rendered_asset'] for item in math_inventory}
        audit.limits['equation_images_without_matched_mathml'] = sorted(equation_assets - math_assets)
        audit.limits['ordinary_inline_html_math'] = 'Preserved with text/formatting; individual semantic formula inventory still requires review.'
    return {'text': ''.join(body_text), 'images': images, 'hyperlinks': hyperlinks, 'pages': pages, 'native_code': native_code, 'source_anchors': source_anchors}


def check_word(root: Path, audit: Audit, parsed: dict[str, Any]) -> None:
    source = root / 'instructions/01-source'
    word_path = source / 'private/AFML_Source_Transcription.docx'
    image_manifest = read_json(source / 'word_image_manifest.json')
    with ZipFile(word_path) as archive:
        document = xml(archive.read('word/document.xml'))
        body = document.find(W + 'body')
        if body is None:
            raise ValueError('Word body is absent.')
        word_text = ''.join(node.text or '' for node in body.iter(W + 't'))
        expected_text = without_whitespace(parsed['text'])
        audit.check('word_entire_visible_text_order', without_whitespace(word_text) == expected_text, non_whitespace_characters=len(expected_text))
        relationships = {item.attrib['Id']: item.attrib for item in xml(archive.read('word/_rels/document.xml.rels'))}
        drawings = list(body.iter(W + 'drawing'))
        assets = []
        pixel_errors: list[str] = []
        byte_errors: list[str] = []
        for index, drawing in enumerate(drawings):
            properties = drawing.find('.//' + WP + 'docPr')
            blip = drawing.find('.//' + A + 'blip')
            if properties is None or blip is None:
                raise ValueError('Word drawing lacks source provenance.')
            asset = properties.attrib['descr']
            assets.append(asset)
            relative = relationships[blip.attrib[R + 'embed']]['Target']
            embedded = archive.read(posixpath.normpath(posixpath.join('word', relative)))
            original = (source / 'private/epub' / asset).read_bytes()
            with Image.open(io.BytesIO(embedded)) as left, Image.open(io.BytesIO(original)) as right:
                if left.size != right.size or left.convert('RGBA').tobytes() != right.convert('RGBA').tobytes():
                    pixel_errors.append(asset)
            if index >= len(image_manifest) or digest(embedded) != image_manifest[index]['embedded_bytes_sha256'] or digest(original) != image_manifest[index]['source_bytes_sha256']:
                byte_errors.append(asset)
        audit.check('word_image_order', assets == [asset for _, asset in parsed['images']], count=len(assets))
        audit.check('word_original_image_pixels', not pixel_errors, mismatches=pixel_errors)
        audit.check('word_embedded_image_hashes', not byte_errors, mismatches=byte_errors)
        bookmarks = {node.attrib[W + 'name'] for node in body.iter(W + 'bookmarkStart')}
        expected_page_names = {'src_' + digest((member + '#' + anchor).encode())[:24] for member, anchor, _ in parsed['pages']}
        audit.check('word_print_page_bookmarks', expected_page_names <= bookmarks, count=len(expected_page_names))
        links = list(body.iter(W + 'hyperlink'))
        unresolved = [node.attrib[W + 'anchor'] for node in links if W + 'anchor' in node.attrib and node.attrib[W + 'anchor'] not in bookmarks]
        audit.check('word_internal_hyperlinks_resolve', not unresolved, unresolved=unresolved)
        actual_targets = [node.attrib.get(W + 'anchor') or relationships[node.attrib[R + 'id']]['Target'] for node in links]
        expected_targets = []
        for member, href in parsed['hyperlinks']:
            split = urlsplit(href)
            if split.scheme or split.netloc:
                expected_targets.append(href)
            else:
                expected_targets.append('src_' + digest((resolve(member, href) + '#' + unquote(split.fragment)).encode())[:24])
        audit.check('word_hyperlink_order_and_targets', actual_targets == expected_targets, count=len(actual_targets))
        # Each native <pre> is rendered into one Word paragraph; reconstruct its
        # tabs and breaks rather than declaring a whitespace-insensitive match enough.
        paragraph_text = []
        for paragraph in body.iter(W + 'p'):
            pieces = []
            for node in paragraph.iter():
                if node.tag == W + 't':
                    pieces.append(node.text or '')
                elif node.tag in {W + 'br', W + 'cr'}:
                    pieces.append('\n')
                elif node.tag == W + 'tab':
                    pieces.append('\t')
            paragraph_text.append(''.join(pieces))
        missing_code = [index for index, code in enumerate(parsed['native_code']) if code not in paragraph_text]
        audit.check('native_code_whitespace_preserved', not missing_code, code_blocks=len(parsed['native_code']), mismatches=missing_code)
        audit.check('word_native_table_count', len(list(body.iter(W + 'tbl'))) == len(read_json(source / 'tables.json')))
    report = read_json(source / 'word_export_report.json')
    audit.check('word_export_hash', digest(word_path.read_bytes()) == report['docx_sha256'])
    audit.limits['word_layout'] = 'Reflowed Word document; publisher CSS and byte-exact originals are retained separately.'
    audit.limits['editable_word_equations'] = False


def without_fenced_blocks(text: str) -> str:
    """Remove fenced code without confusing nested shorter fences with closers."""
    result = []
    fence_character = ''
    fence_length = 0
    for line in text.splitlines(keepends=True):
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence_character:
            if marker and marker.group(1)[0] == fence_character and len(marker.group(1)) >= fence_length:
                fence_character = ''
                fence_length = 0
            continue
        if marker:
            fence_character = marker.group(1)[0]
            fence_length = len(marker.group(1))
            continue
        result.append(line)
    return ''.join(result)


def check_tasks(root: Path, audit: Audit) -> None:
    source = root / 'instructions/01-source'
    tasks = read_json(root / 'instructions/02-book/task_index.json')
    sections = read_json(source / 'sections.json')
    audit.check('section_task_order', [item['id'] for item in tasks['sections']] == [item['id'] for item in sections], count=len(sections))
    source_by_id = {item['id']: item for item in sections}
    parent_errors = [item['id'] for item in sections if item['parent'] is not None and item['parent'] not in source_by_id]
    audit.check('all_section_parents_exist', not parent_errors, mismatches=parent_errors)
    descriptor_errors = []
    for item in tasks['sections']:
        original = source_by_id[item['id']]
        for target_key, source_key in [('source_document', 'document'), ('title', 'title'), ('parent', 'parent'), ('source_heading_sha256', 'source_sha256')]:
            if item[target_key] != original[source_key]:
                descriptor_errors.append(item['id'] + ':' + target_key)
    audit.check('task_source_metadata', not descriptor_errors, mismatches=descriptor_errors)
    hash_errors = []
    task_paths: set[str] = set()
    for category in ['sections', 'equation_images', 'snippets', 'ancillary_documents']:
        for item in tasks[category]:
            path = root / item['path']
            task_paths.add(item['path'])
            expected_hash = item.get('md_sha256')
            if not path.is_file() or (expected_hash and digest(path.read_bytes()) != expected_hash):
                hash_errors.append(item['path'])
    audit.check('all_task_files_and_hashes', not hash_errors, count=len(task_paths), mismatches=hash_errors)
    expected_equations = {item['id'] for item in read_json(source / 'images.json') if item['kind'] in {'inline_equation', 'display_equation'}}
    audit.check('all_equation_image_tasks', {item['id'] for item in tasks['equation_images']} == expected_equations, count=len(expected_equations))
    audit.check('all_snippet_tasks', {item['id'] for item in tasks['snippets']} == {item['id'] for item in read_json(source / 'snippets.json')}, count=len(tasks['snippets']))
    audit.check('all_ancillary_document_tasks', len(tasks['ancillary_documents']) == sum(item['chapter'] is None for item in read_json(source / 'spine.json')), count=len(tasks['ancillary_documents']))
    # Generated drafts cannot grant themselves independent review.
    audit.check('no_auto_approved_section_tasks', all(item['status'] == 'draft_pending_independent_review' for item in tasks['sections']))
    broken_links = []
    pattern = re.compile(r'!?\[[^\]\n]*\]\(([^)\n]+)\)')
    for path in root.rglob('*.md'):
        if any(part in {'.git', 'private', 'build'} for part in path.relative_to(root).parts):
            continue
        text = without_fenced_blocks(path.read_text(encoding='utf-8'))
        for match in pattern.finditer(text):
            target = match.group(1).strip().split(' "', 1)[0]
            split = urlsplit(target)
            if split.scheme or split.netloc or not split.path:
                continue
            actual = (path.parent / unquote(split.path)).resolve()
            if not actual.is_relative_to(root.resolve()) or not actual.exists():
                broken_links.append({'file': str(path.relative_to(root)), 'target': target})
    audit.check('markdown_local_file_links', not broken_links, mismatches=broken_links[:100], total_mismatches=len(broken_links))
    audit.limits['markdown_link_scope'] = 'File destinations checked; arbitrary Markdown heading anchors require contextual review.'
    audit.limits['reviewed_sections'] = 0
    audit.limits['reviewed_equations'] = 0


def run(root: Path) -> dict[str, Any]:
    audit = Audit()
    lock = check_locks(root, audit)
    parsed = check_source(root, audit, lock)
    check_word(root, audit, parsed)
    check_tasks(root, audit)
    return audit.result()


def save_report(root: Path, result: dict[str, Any]) -> None:
    report_dir = root / 'instructions/reports'
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / 'crosscheck.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    text = '# Cross-check report\n\n'
    text += f"**Structural result: {'PASS' if result['passed'] else 'FAIL'}** — {result['check_count']} checks; {result['failed_check_count']} failures.\n\n"
    text += 'This is not semantic, mathematical, implementation or production approval.\n\n'
    text += '| Check | Result | Detail |\n|---|---|---|\n'
    for check in result['checks']:
        details = {key: value for key, value in check.items() if key not in {'name', 'passed'}}
        text += f"| `{check['name']}` | {'PASS' if check['passed'] else 'FAIL'} | {json.dumps(details, ensure_ascii=False) if details else ''} |\n"
    text += '\n## Explicit limits\n\n```json\n' + json.dumps(result['limits'], indent=2, ensure_ascii=False) + '\n```\n'
    (report_dir / 'CROSSCHECK_REPORT.md').write_text(text, encoding='utf-8')

# CLI entry point: instructions/tools/rebuild_private_source.py.
