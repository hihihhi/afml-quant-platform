#!/usr/bin/env python3
"""Independent public-view checks; optional source-locator verification.

Passing public checks does not imply that the private EPUB, Word pixels,
mathematical arguments or financial implementations have been reviewed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any
from zipfile import ZipFile

CATEGORIES = ('sections', 'equation_images', 'snippets', 'ancillary_documents')
EXPECTED_COUNTS = {'sections': 369, 'equation_images': 653, 'snippets': 100,
                   'ancillary_documents': 16}
FORBIDDEN = {'.epub', '.docx', '.pdf', '.gif', '.png', '.jpg', '.jpeg', '.zip', '.xz', '.b64'}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def contained(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if Path(relative).is_absolute() or not path.is_relative_to(root.resolve()):
        raise ValueError('Path outside repository.')
    return path


def audit(root: Path, *, tracked_only: bool = False) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    lock = read_json(root / 'instructions/00-governance/REQUIREMENTS_LOCK.json')
    for name, expected in lock['authority_files'].items():
        if digest(contained(root, name).read_bytes()) != expected:
            errors.append('Prompt hash mismatch: ' + name)
    requirements = (root / 'instructions/00-governance/REQUIREMENTS.md').read_text()
    if not set(lock['required_requirement_ids']) <= set(re.findall(r'\bU\d{3}\b', requirements)):
        errors.append('Required user requirement ID missing.')
    catalog_path = root / 'instructions/01-source/public_tasks.json'
    catalog = read_json(catalog_path)
    publication_lock = read_json(root / 'instructions/01-source/PUBLICATION_LOCK.json')
    if digest(catalog_path.read_bytes()) != publication_lock['catalog_sha256']:
        errors.append('Catalog differs from its publication lock.')
    records = [dict(zip(catalog['columns'], row, strict=True)) for row in catalog['rows']]
    if catalog['source_epub_sha256'] != lock['source_epub_sha256']:
        errors.append('Source identity mismatch.')
    if Counter(row['category'] for row in records) != EXPECTED_COUNTS:
        errors.append('Source task category coverage differs from the reviewed inventory.')
    ids = [row['id'] for row in records]
    if len(ids) != len(set(ids)):
        errors.append('Duplicate task ID.')
    if digest('\n'.join(ids).encode()) != publication_lock['ordered_task_ids_sha256']:
        errors.append('Task order or exact ID coverage changed.')
    by_id = {record['id']: record for record in records}
    if len({row['path'] for row in records}) != len(records):
        errors.append('Duplicate task path.')
    for record in records:
        contained(root, record['path'])
        if record['parent'] and record['parent'] not in by_id:
            errors.append('Unknown parent: ' + record['id'])
        seen: set[str] = set()
        node = record
        while node['parent']:
            if node['id'] in seen or node['parent'] not in by_id:
                errors.append('Cyclic or missing parent: ' + record['id'])
                break
            seen.add(node['id'])
            node = by_id[node['parent']]
    index = read_json(root / 'instructions/02-book/task_index.json')
    if (index['source_epub_sha256'] != lock['source_epub_sha256']
            or index['catalog_sha256'] != digest(catalog_path.read_bytes())):
        errors.append('Index source/catalog identity mismatch.')
    if index.get('semantic_approvals') != 0 or index.get('mathematical_approvals') != 0:
        errors.append('Generated index must not award approvals.')
    indexed = [item for category in CATEGORIES for item in index[category]]
    if [row['id'] for row in indexed] != ids:
        errors.append('Index order differs from source catalog.')
    for item in indexed:
        source = by_id.get(item['id'])
        if source is None:
            errors.append('Unknown index task.')
            continue
        if any(item.get(key) != value for key, value in source.items()):
            errors.append('Index metadata differs from catalog: ' + item['id'])
        path = contained(root, item['path'])
        if not path.is_file() or digest(path.read_bytes()) != item['md_sha256']:
            errors.append('Missing or altered task: ' + item['id'])
        if item.get('status') != 'draft_pending_independent_review':
            errors.append('Generated task claims approval: ' + item['id'])
    if tracked_only:
        result = subprocess.run(['git', 'ls-files', '-z'], cwd=root, check=True,
                                capture_output=True, text=True)
        paths = [root / name for name in result.stdout.split('\0') if name]
    else:
        paths = [path for path in root.rglob('*') if path.is_file()
                 and not any(part in {'.git', 'build', '__pycache__', '.venv', '.ruff_cache'}
                             for part in path.relative_to(root).parts)]
    for path in paths:
        relative = path.relative_to(root)
        if ('private' in relative.parts or 'task-context' in relative.parts
                or path.suffix.lower() in FORBIDDEN or path.is_symlink()
                or path.name.startswith(('.env', 'credentials'))):
            errors.append('Forbidden public file: ' + str(relative))
    return {'scope': 'public task view and prompt integrity only', 'passed': not errors,
            'task_count': len(records), 'category_counts': dict(Counter(r['category'] for r in records)),
            'errors': errors, 'private_word_pixel_audit': 'NOT_RUN',
            'semantic_approval': False, 'mathematical_approval': False}


def visible_text(element: Any) -> str:
    pieces: list[str] = []
    def visit(node: Any) -> None:
        if not isinstance(node.tag, str):
            return
        if node.text:
            pieces.append(node.text)
        for child in node:
            visit(child)
            if child.tail:
                pieces.append(child.tail)
    visit(element)
    return ' '.join(''.join(pieces).split())


def verify_source(root: Path, epub: Path) -> dict[str, Any]:
    from lxml import etree
    lock = read_json(root / 'instructions/00-governance/REQUIREMENTS_LOCK.json')
    if digest(epub.read_bytes()) != lock['source_epub_sha256']:
        raise ValueError('Wrong source edition or altered EPUB.')
    catalog = read_json(root / 'instructions/01-source/public_tasks.json')
    records = [dict(zip(catalog['columns'], row, strict=True)) for row in catalog['rows']]
    errors: list[str] = []
    documents: dict[str, list[Any]] = {}
    with ZipFile(epub) as archive:
        if len(archive.namelist()) != len(set(archive.namelist())):
            raise ValueError('Duplicate ZIP members.')
        for record in records:
            document = record['document']
            if document not in documents:
                tree = etree.fromstring(archive.read(document), etree.XMLParser(
                    resolve_entities=False, no_network=True, remove_comments=False))
                bodies = tree.xpath('//*[local-name()="body"]')
                if len(bodies) != 1:
                    raise ValueError('Source requires one XHTML body.')
                documents[document] = list(bodies[0].iter())
            nodes = documents[document]
            start, end = record['position'], record['position_end_exclusive']
            if not 0 <= start < end <= len(nodes):
                errors.append('Invalid source span: ' + record['id'])
                continue
            node = nodes[start]
            if record['category'] in {'sections', 'snippets'}:
                if visible_text(node) != record['title']:
                    errors.append('Heading differs from source: ' + record['id'])
            if record['category'] == 'equation_images':
                if not isinstance(node.tag, str) or etree.QName(node).localname != 'img':
                    errors.append('Equation locator does not identify an image: ' + record['id'])
            for asset in record['assets']:
                if asset not in archive.namelist():
                    errors.append('Missing original asset: ' + asset)
    return {'scope': 'locked EPUB and public source locators', 'passed': not errors,
            'source_sha256': lock['source_epub_sha256'], 'locators_checked': len(records),
            'documents_checked': len(documents), 'errors': errors,
            'semantic_approval': False, 'mathematical_approval': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--tracked-only', action='store_true')
    parser.add_argument('--epub', type=Path)
    args = parser.parse_args()
    try:
        result = audit(args.root, tracked_only=args.tracked_only)
        if args.epub:
            result['source_locators'] = verify_source(args.root, args.epub)
            result['passed'] = result['passed'] and result['source_locators']['passed']
        print(json.dumps(result, indent=2))
        raise SystemExit(0 if result['passed'] else 1)
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        print(json.dumps({'passed': False, 'error': str(error)}))
        raise SystemExit(2) from error
