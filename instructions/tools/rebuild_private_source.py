#!/usr/bin/env python3
"""Rebuild full source inventories, Word and source-rich Markdown privately.

Install the licensed EPUB with install_source.py first. All new output is confined
to a fresh, Git-ignored private rebuild directory. Public task Markdown is never
replaced. Generated drafts and structural checks grant no review approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path
from typing import Any

from build_task_context import read_project_file, verified_task


def private_destination(root: Path, name: str) -> Path:
    """Validate a single build name and reject existing paths and symlink parents."""
    root = root.resolve()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}', name):
        raise ValueError('Use a new build name containing only letters, digits, - and _.')
    base = root / 'instructions/01-source/private/rebuilds'
    destination = base / name
    for component in (destination, *destination.parents):
        if component == root:
            break
        if component.is_symlink():
            raise ValueError('Private output paths must not use symlinks.')
    if destination.exists():
        raise FileExistsError('Refusing to overwrite a private rebuild: ' + name)
    if not destination.resolve().is_relative_to(root / 'instructions/01-source/private'):
        raise ValueError('Output escaped the private source directory.')
    return destination


def numbered_blueprints(catalog: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Reuse checked public descriptions; do not invent a second specification."""
    result: dict[str, dict[str, str]] = {}
    for row in catalog['rows']:
        record = dict(zip(catalog['columns'], row, strict=True))
        if record['id'].startswith('S-'):
            number = record['id'][2:]
            if number in result:
                raise ValueError('Duplicate source section number: ' + number)
            result[number] = {key: record[key] for key in ('work', 'caution')}
    if len(result) != 280:
        raise ValueError('The locked edition must supply all 280 numbered sections.')
    return result


def rebuild(root: Path, name: str) -> dict[str, Any]:
    """Build from the installed locked edition and publish the directory on success.

    The staging workspace is also private. On failure it is removed; existing
    source installations, public drafts and earlier rebuilds remain untouched.
    A successful Word rebuild still requires a separate full rendered layout review.
    """
    root = root.resolve()
    destination = private_destination(root, name)
    lock, _ = verified_task(root, 'CH-01')
    source_path = 'instructions/01-source/private/original.epub'
    source_bytes = read_project_file(root, source_path)
    if hashlib.sha256(source_bytes).hexdigest() != lock['source_epub_sha256']:
        raise ValueError('Installed EPUB differs from the locked source edition.')
    catalog = json.loads(read_project_file(root, 'instructions/01-source/public_tasks.json'))
    blueprints = numbered_blueprints(catalog)

    # Heavy document dependencies load only after the provenance/output preflight.
    from source_build.build_book_checklists import build as build_checklists
    from source_build.crosscheck import run as audit_source, save_report
    from source_build.export_word import WordExporter
    from source_build.inventory_epub import extract_source

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.rebuild-', dir=destination.parent) as folder:
        staging = Path(folder) / 'workspace'
        staging.mkdir(mode=0o700)
        copy_paths = set(lock['authority_files']) | {
            'instructions/00-governance/REQUIREMENTS_LOCK.json',
            'instructions/00-governance/REQUIREMENTS.md',
            'instructions/03-crosschecks/REVIEW_PROTOCOL.md',
            'instructions/03-crosschecks/ERRATA.md',
        }
        for relative in sorted(copy_paths):
            target = staging / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(read_project_file(root, relative))
        target = staging / 'instructions/02-book/section_blueprints.json'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(blueprints, indent=2, ensure_ascii=False) + '\n',
                          encoding='utf-8')
        # Use the verified bytes rather than reopen an input that could have changed.
        input_copy = Path(folder) / 'verified-input.epub'
        input_copy.write_bytes(source_bytes)
        extract_source(input_copy, staging)
        word = staging / 'instructions/01-source/private/AFML_Source_Transcription.docx'
        word_report = WordExporter(staging).export(word)
        task_report = build_checklists(staging)
        audit = audit_source(staging)
        save_report(staging, audit)
        if not audit['passed']:
            failed = [item['name'] for item in audit['checks'] if not item['passed']]
            raise ValueError('Private structural cross-check failed: ' + ', '.join(failed))
        tool_paths = [Path(__file__), *sorted((Path(__file__).parent / 'source_build').glob('*.py'))]
        report = {
            'schema_version': 1,
            'scope': 'Full private source/Word/draft preservation rebuild',
            'source_epub_sha256': lock['source_epub_sha256'],
            'spine_document_count': len(json.loads((staging / 'instructions/01-source/spine.json').read_text())),
            'word_sha256': word_report['docx_sha256'],
            'word_image_placements': word_report['word_image_placements'],
            'task_count': sum(task_report[key] for key in
                              ('section_task_count', 'equation_image_task_count',
                               'snippet_task_count', 'ancillary_document_task_count')),
            'structural_checks': audit['check_count'],
            'structural_checks_passed': audit['passed'],
            'visual_review': 'NOT_RUN_FOR_THIS_REBUILD',
            'independent_semantic_approval': False,
            'independent_mathematical_approval': False,
            'public_tasks_modified': False,
            'tool_sha256': {str(path.relative_to(Path(__file__).resolve().parents[2])): hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in tool_paths},
        }
        (staging / 'REBUILD_RESULT.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        (staging / 'PRIVATE_SOURCE_NOTICE.md').write_text(
            '# Private source rebuild\n\nThis directory includes the user-provided book, complete '
            'transcription, source images and verbatim paragraphs. Do not commit or publish it.\n\n'
            'A passing structural report is not semantic, mathematical or visual approval. '
            'Word reflows source layout; formula/code images retain pixels rather than becoming '
            'editable equations. Render and inspect every page before distributing a new Word file.\n',
            encoding='utf-8',
        )
        # A fresh destination is required throughout; no earlier outputs are overwritten.
        if destination.exists() or destination.is_symlink():
            raise FileExistsError('Output appeared during the rebuild; refusing replacement.')
        staging.rename(destination)
    return {**report, 'private_workspace': str(destination)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', required=True, help='Unique build name, e.g. source-v1.')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    arguments = parser.parse_args()
    try:
        print(json.dumps(rebuild(arguments.root, arguments.name), indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, 'Private rebuild failed closed: ' + str(error) + '\n')
