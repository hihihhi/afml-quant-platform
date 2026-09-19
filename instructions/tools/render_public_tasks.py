#!/usr/bin/env python3
"""Render the public book-ordered task view without publishing book contents.

The view has the same task IDs and paths as the full local extraction package.
It is a source-locator and draft-work projection, not the private byte/pixel
catalog or a substitute for reading the book. No review approval is generated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

CATEGORIES = ('sections', 'equation_images', 'snippets', 'ancillary_documents')


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_catalog(root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    catalog = json.loads((root / 'instructions/01-source/public_tasks.json').read_text('utf-8'))
    records = [dict(zip(catalog['columns'], row, strict=True)) for row in catalog['rows']]
    return catalog, records


def safe_path(root: Path, name: str) -> Path:
    candidate = Path(name)
    destination = (root / candidate).resolve()
    if candidate.is_absolute() or not destination.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes repository: {name}')
    if not name.startswith('instructions/02-book/') or '..' in candidate.parts:
        raise ValueError(f'Not a book task path: {name}')
    return destination


def relative_link(start: Path, target: Path) -> str:
    return os.path.relpath(target, start.parent).replace(os.sep, '/')


def render(record: dict[str, Any], records: list[dict[str, Any]], root: Path,
           source_hash: str) -> str:
    path = safe_path(root, record['path'])
    original = root / 'instructions/01-source/private/epub' / record['document']
    source_link = relative_link(path, original)
    if record['anchor']:
        source_link += '#' + record['anchor']
    text = f"# {record['title']}\n\n"
    text += f"**Task:** `{record['id']}`. **Status:** draft; independent review pending.\n\n"
    text += f"**Source:** [{record['document']}]({source_link}); source EPUB SHA-256 `{source_hash}`.\n\n"
    text += (f"**Direct source locator:** body-iterator positions {record['position']} to "
             f"{record['position_end_exclusive']} (end exclusive); printed markers "
             f"{record['page_start']}–{record['page_end']}. These are not Word page numbers.\n\n")
    text += ('The complete source and pixel-level catalogs remain in the private working package. '
             'This public view preserves task IDs, locators and draft engineering interpretations, '
             'not verbatim book paragraphs or approved mathematical transcriptions.\n\n')
    if record['work']:
        text += '## Description and proposed work\n\n' + record['work'] + '\n\n'
        text += '## Cautions to cross-check\n\n' + record['caution'] + '\n\n'
    elif record['category'] == 'equation_images':
        text += ('## Required mathematical review\n\nCompare every symbol, index, subscript, '
                 'superscript, operator, limit and boundary in the rendered source with any hidden '
                 'MathML and surrounding narrative. Define domains, units and assumptions; derive '
                 'or independently test the claim. Preserve suspected errors separately.\n\n')
    elif record['category'] == 'snippets':
        text += ('## Required code review\n\nTranscribe tokens and indentation; identify imports, '
                 'library versions, inputs, outputs and unhandled cases. Keep literal source separate '
                 'from readable reference code. Cross-check narrative, formula and executable behavior. '
                 'No snippet is executed during extraction.\n\n')
    else:
        text += ('## Required apparatus review\n\nReview every retained document in spine order, '
                 'including covers, part dividers, contents, index and end matter. Preserve navigation '
                 'and attribution without inventing product requirements from publishing apparatus.\n\n')
    for asset in record['assets']:
        target = root / 'instructions/01-source/private/epub' / asset
        text += f"Original asset: [{asset}]({relative_link(path, target)}).\n\n"
    text += ('## TODO and acceptance gates\n\n'
             '- [ ] Read the entire original span, children, lists, tables, images, notes and exercises.\n'
             '- [ ] Cross-check this task description and caution; record omissions and unsupported claims.\n'
             '- [ ] Inventory ordinary inline mathematics as well as equation images; verify notation and domains.\n'
             '- [ ] Establish independent analytical or high-precision test oracles and boundary cases.\n'
             '- [ ] Where applicable, reproduce the reference before a readable C++ implementation.\n'
             '- [ ] Record numerical tolerances, measured performance, failure behavior and remaining blockers.\n'
             '- [ ] Obtain distinct reviewer evidence; bind approvals to source, specification and evidence hashes.\n\n')
    related = [item for item in records if item['parent'] == record['id']]
    if related:
        text += '## Direct child tasks\n\n'
        for child in related:
            text += f"- [{child['id']} — {child['title']}]({relative_link(path, root / child['path'])})\n"
    return text


def build(root: Path, *, write: bool = False) -> dict[str, bytes]:
    root = root.resolve()
    catalog, records = read_catalog(root)
    outputs: dict[str, bytes] = {}
    index: dict[str, Any] = {'schema_version': 2, 'publication_mode': 'source_locator_view',
                            'source_epub_sha256': catalog['source_epub_sha256'],
                            'catalog_sha256': sha256((root / 'instructions/01-source/public_tasks.json').read_bytes()),
                            'semantic_approvals': 0, 'mathematical_approvals': 0}
    for category in CATEGORIES:
        index[category] = []
    for record in records:
        content = render(record, records, root, catalog['source_epub_sha256']).encode('utf-8')
        if record['path'] in outputs:
            raise ValueError('Duplicate task path.')
        outputs[record['path']] = content
        entry = dict(record, md_sha256=sha256(content), status='draft_pending_independent_review')
        index[record['category']].append(entry)
    outputs['instructions/02-book/task_index.json'] = (json.dumps(index, ensure_ascii=False, indent=2) + '\n').encode()
    listing = '# Book-ordered task index\n\nPublic locator view; no semantic or mathematical approval.\n\n'
    for record in records:
        if record['id'].startswith('CH-'):
            listing += f"- [{record['title']}]({record['path'].removeprefix('instructions/02-book/')})\n"
    listing += '\nAll equation images, snippets and ancillary documents are included in `task_index.json`.\n'
    outputs['instructions/02-book/README.md'] = listing.encode()
    if write:
        # Preflight all conflicts before modifying any generated file.
        for name, content in outputs.items():
            path = safe_path(root, name)
            if path.exists() and path.read_bytes() != content:
                raise FileExistsError(f'Refusing to overwrite an edited task: {name}')
        for name, content in outputs.items():
            path = safe_path(root, name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    return outputs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = build(args.root, write=args.write)
    print(json.dumps({'generated_files': len(result), 'task_files': len(result) - 2,
                      'wrote_files': args.write, 'semantic_approval': False}))
