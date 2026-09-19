#!/usr/bin/env python3
"""One-time integrity-checked import of source-free document tooling."""
from __future__ import annotations

import hashlib
import json
import lzma
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result


def destination(root: Path, name: str, allowed: dict[str, str]) -> Path:
    path = PurePosixPath(name)
    if (path.is_absolute() or str(path) != name or '\\' in name
            or '..' in path.parts or '.' in path.parts
            or not path.parts or path.parts[0] != 'instructions'
            or any(part in {'private', 'task-context'} for part in path.parts)
            or path.suffix not in {'.py', '.md', '.txt', '.json'}):
        raise ValueError('Invalid source-free destination: ' + name)
    result = root.joinpath(*path.parts)
    for part in (result, *result.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError('Symlink in destination: ' + name)
    if result.exists() and (not result.is_file() or name not in allowed
                            or git_sha(result.read_bytes()) != allowed[name]):
        raise FileExistsError('Refusing to overwrite a changed or unreviewed file: ' + name)
    return result


def materialize(root: Path) -> None:
    root = root.resolve()
    transport = root / '.source-import'
    manifest = json.loads((transport / 'manifest.json').read_text(), object_pairs_hook=unique)
    if manifest['schema_version'] != 1:
        raise ValueError('Unsupported schema.')
    parts = manifest['parts']
    if len(parts) != 3 or len({part['path'] for part in parts}) != 3:
        raise ValueError('Exactly three unique parts are required.')
    compressed = bytearray()
    for part in parts:
        name = PurePosixPath(part['path'])
        if len(name.parts) != 2 or name.parts[0] != '.source-import' or name.suffix != '.part':
            raise ValueError('Unsafe transport name.')
        local = root / str(name)
        if local.is_symlink():
            raise ValueError('Transport must not be a symlink.')
        data = local.read_bytes()
        if (len(data) != part['size'] or sha256(data) != part['sha256']
                or git_sha(data) != part['git_blob_sha']):
            raise ValueError('Transport integrity failure: ' + str(name))
        compressed.extend(data)
        if len(compressed) > 100000:
            raise ValueError('Transport exceeds expected bound.')
    if sha256(compressed) != manifest['compressed_sha256']:
        raise ValueError('Combined hash mismatch.')
    decoder = lzma.LZMADecompressor(memlimit=256 * 1024 * 1024)
    raw = decoder.decompress(compressed, max_length=1000000)
    if len(raw) != manifest['raw_bytes'] or not decoder.eof or decoder.unused_data:
        raise ValueError('Invalid decompressed size or trailing data.')
    files = json.loads(raw.decode('utf-8'), object_pairs_hook=unique)
    if set(files) != set(manifest['files']):
        raise ValueError('File inventory differs.')
    allowed = manifest['allowed_existing_git_blobs']
    with tempfile.TemporaryDirectory(prefix='afml-source-tools-') as folder:
        staging = Path(folder)
        for name, text in files.items():
            if not isinstance(text, str) or sha256(text.encode()) != manifest['files'][name]:
                raise ValueError('Source file hash mismatch: ' + name)
            destination(root, name, allowed)
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8')
        for name in files:
            target = destination(root, name, allowed)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(staging / name, target)
    print(json.dumps({'files_materialized': len(files), 'compressed_sha256': manifest['compressed_sha256'],
                      'book_bytes_included': False, 'test_result': 'NOT_YET_RUN'}, indent=2))


if __name__ == '__main__':
    materialize(Path(__file__).resolve().parents[1])
