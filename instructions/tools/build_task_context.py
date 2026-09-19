#!/usr/bin/env python3
"""Build a private source-bound packet carrying the complete locked user prompts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def build(root: Path, task_id: str, output: Path) -> Path:
    root = root.resolve()
    output = output.resolve()
    allowed = root / 'instructions/task-context'
    if not output.is_relative_to(allowed):
        raise ValueError('Task packets contain private source and must stay in instructions/task-context/.')
    if output.exists():
        raise FileExistsError('Refusing to overwrite an existing task packet.')
    lock = json.loads((root / 'instructions/00-governance/REQUIREMENTS_LOCK.json').read_text())
    parts = ['# Private task context\n\nDo not commit or publish this source-containing packet.\n']
    for filename, expected in lock['authority_files'].items():
        content = (root / filename).read_bytes()
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError('Prompt lock mismatch: ' + filename)
        parts.append('\n## Complete authority file: ' + filename + '\n\n' + content.decode('utf-8'))
    catalog = json.loads((root / 'instructions/01-source/public_tasks.json').read_text())
    rows = [dict(zip(catalog['columns'], row, strict=True)) for row in catalog['rows']]
    matches = [row for row in rows if row['id'] == task_id]
    if len(matches) != 1:
        raise ValueError('Task ID must identify exactly one source-inventoried task.')
    record = matches[0]
    epub = root / 'instructions/01-source/private/original.epub'
    if hashlib.sha256(epub.read_bytes()).hexdigest() != lock['source_epub_sha256']:
        raise ValueError('Private EPUB differs from the locked edition.')
    parts.append('\n## Agent contract\n\n' + (root / 'AGENTS.md').read_text())
    parts.append('\n## Task specification\n\n' + (root / record['path']).read_text())
    with ZipFile(epub) as archive:
        source = archive.read(record['document']).decode('utf-8')
    # Include the full source document rather than silently dropping surrounding
    # equations, caption context, nested lists or notes at an arbitrary chunk edge.
    parts.append('\n## Entire original source document\n\n' + source)
    parts.append('\n\nOriginal image assets remain under instructions/01-source/private/epub/. '
                 'Open the rendered assets; XML comments alone do not verify mathematical notation.\n')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(parts), encoding='utf-8')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task_id')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    target = args.output or args.root / 'instructions/task-context' / (args.task_id + '.md')
    print(build(args.root, args.task_id, target))
