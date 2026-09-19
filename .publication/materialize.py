#!/usr/bin/env python3
"""Materialize the reviewed source-free seed; refuse conflicts or unsafe paths.

The transport contains project code and source metadata, never the EPUB or Word.
It is temporary transport, not an approval of the generated research tasks.
"""
from __future__ import annotations

import hashlib
import json
import lzma
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

MAX_COMPRESSED_BYTES = 2_000_000
MAX_UNCOMPRESSED_BYTES = 20_000_000
ROOT_FILES = {'.clang-format', '.editorconfig', '.gitignore', 'AGENTS.md',
              'README.md', 'CURRENT_STATUS.md', 'NOTICE.md'}
FORBIDDEN_SUFFIXES = {'.epub', '.docx', '.pdf', '.gif', '.png', '.jpg', '.jpeg', '.zip'}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def safe_relative(name: str) -> Path:
    pure = PurePosixPath(name)
    if (not name or '\\' in name or pure.is_absolute() or '..' in pure.parts
            or '.' in pure.parts or str(pure) != name):
        raise ValueError(f'Noncanonical relative path: {name}')
    if name not in ROOT_FILES and pure.parts[0] not in {'system', 'instructions'}:
        raise ValueError(f'Path is outside the seed allowlist: {name}')
    if ('private' in pure.parts or 'task-context' in pure.parts
            or pure.suffix.lower() in FORBIDDEN_SUFFIXES):
        raise ValueError(f'Private source path in publication: {name}')
    return Path(*pure.parts)


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def check_destination(root: Path, relative: Path, allowed: dict[str, str]) -> None:
    destination = root / relative
    for component in (destination, *destination.parents):
        if component == root.parent:
            break
        if component.is_symlink():
            raise ValueError(f'Symlink in destination path: {relative}')
    if destination.exists():
        expected = allowed.get(relative.as_posix())
        if not destination.is_file() or expected is None:
            raise FileExistsError(f'Refusing to replace an existing path: {relative}')
        if git_blob_sha(destination.read_bytes()) != expected:
            raise ValueError(f'Existing file changed since review: {relative}')


def materialize(root: Path) -> dict[str, Any]:
    root = root.resolve()
    transport = root / '.publication'
    manifest = json.loads((transport / 'manifest.json').read_text('utf-8'),
                          object_pairs_hook=unique_object)
    if manifest['schema_version'] != 1:
        raise ValueError('Unsupported seed schema.')
    parts = manifest['parts']
    if not parts or len(parts) > 100:
        raise ValueError('Invalid part count.')
    seen: set[str] = set()
    compressed = bytearray()
    for record in parts:
        name = record['path']
        path = PurePosixPath(name)
        if (len(path.parts) != 2 or path.parts[0] != '.publication'
                or not path.name.startswith('seed-') or path.suffix != '.part'
                or name in seen):
            raise ValueError('Unsafe or duplicate transport part.')
        seen.add(name)
        local = root / name
        if local.is_symlink():
            raise ValueError('Transport part must not be a symlink.')
        data = local.read_bytes()
        if len(data) != record['size'] or sha256(data) != record['sha256']:
            raise ValueError(f'Part hash/size mismatch: {name}')
        if git_blob_sha(data) != record['git_blob_sha']:
            raise ValueError(f'Part Git blob mismatch: {name}')
        compressed.extend(data)
        if len(compressed) > MAX_COMPRESSED_BYTES:
            raise ValueError('Compressed seed is too large.')
    if sha256(compressed) != manifest['compressed_sha256']:
        raise ValueError('Combined seed hash mismatch.')
    decoder = lzma.LZMADecompressor(memlimit=256 * 1024 * 1024)
    raw = decoder.decompress(compressed, max_length=MAX_UNCOMPRESSED_BYTES + 1)
    if (len(raw) > MAX_UNCOMPRESSED_BYTES or not decoder.eof or decoder.unused_data
            or len(raw) != manifest['uncompressed_bytes']):
        raise ValueError('Seed length, EOF or trailing-data validation failed.')
    files = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_object)
    if not isinstance(files, dict) or len(files) != manifest['seed_file_count']:
        raise ValueError('Seed file count differs from manifest.')
    allowed = manifest.get('allowed_existing_git_blobs', {})
    with tempfile.TemporaryDirectory(prefix='afml-publication-') as folder:
        temporary = Path(folder)
        for name, content in files.items():
            if not isinstance(content, str):
                raise ValueError('Seed values must be UTF-8 text.')
            relative = safe_relative(name)
            check_destination(root, relative, allowed)
            destination = temporary / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding='utf-8')
        subprocess.run([sys.executable, str(temporary / 'instructions/tools/render_public_tasks.py'),
                        '--root', str(temporary), '--write'], check=True, cwd=temporary)
        index_path = temporary / 'instructions/02-book/task_index.json'
        if sha256(index_path.read_bytes()) != manifest['expected_task_index_sha256']:
            raise ValueError('Regenerated task index differs from the locally checked index.')
        outputs = sorted(path for path in temporary.rglob('*') if path.is_file()
                         and '__pycache__' not in path.parts)
        for path in outputs:
            check_destination(root, safe_relative(path.relative_to(temporary).as_posix()), allowed)
        # All payload, generation and conflict checks have completed before writes.
        for path in outputs:
            destination = root / path.relative_to(temporary)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
        task_index = json.loads(index_path.read_text('utf-8'))
        task_count = sum(len(task_index[key]) for key in
                         ('sections', 'equation_images', 'snippets', 'ancillary_documents'))
    result = {'schema_version': 1, 'seed_sha256': manifest['compressed_sha256'],
              'seed_file_count': len(files), 'materialized_file_count': len(outputs),
              'task_count': task_count, 'semantic_approval': False,
              'mathematical_approval': False, 'runtime_scope': 'non-trading scaffold'}
    for record in parts:
        (root / record['path']).unlink()
    (transport / 'READY').unlink(missing_ok=True)
    (transport / 'IMPORT.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


if __name__ == '__main__':
    try:
        print(json.dumps(materialize(Path(__file__).resolve().parents[1]), indent=2))
    except (OSError, ValueError, KeyError, lzma.LZMAError, subprocess.CalledProcessError) as error:
        print(f'Publication failed closed: {error}', file=sys.stderr)
        raise SystemExit(2) from error
