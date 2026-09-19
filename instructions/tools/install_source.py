#!/usr/bin/env python3
"""Install a verified, user-supplied EPUB locally; never download or publish it."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from zipfile import ZipFile


def install(root: Path, epub: Path, word: Path | None = None) -> Path:
    root = root.resolve()
    lock = json.loads((root / 'instructions/00-governance/REQUIREMENTS_LOCK.json').read_text())
    data = epub.read_bytes()
    if hashlib.sha256(data).hexdigest() != lock['source_epub_sha256']:
        raise ValueError('Source EPUB hash differs from the locked edition.')
    if word:
        publication = json.loads((root / 'instructions/01-source/PUBLICATION_LOCK.json').read_text())
        if hashlib.sha256(word.read_bytes()).hexdigest() != publication['private_word_sha256']:
            raise ValueError('Word transcription hash differs from the retained export.')
    destination = root / 'instructions/01-source/private'
    if destination.exists():
        raise FileExistsError('Refusing to overwrite an existing private source workspace.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.source-install-', dir=destination.parent) as folder:
        staging = Path(folder) / 'private'
        staging.mkdir()
        with ZipFile(epub) as archive:
            entries = archive.infolist()
            if len({entry.filename for entry in entries}) != len(entries):
                raise ValueError('Duplicate archive members.')
            if sum(entry.file_size for entry in entries) > 200_000_000:
                raise ValueError('Expanded source exceeds the safety limit.')
            for entry in entries:
                member = PurePosixPath(entry.filename)
                if (member.is_absolute() or '..' in member.parts or '\\' in entry.filename
                        or (entry.external_attr >> 16) & 0o170000 == 0o120000):
                    raise ValueError('Unsafe archive member.')
                target = staging / 'epub' / Path(*member.parts)
                if entry.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.read(entry))
        (staging / 'original.epub').write_bytes(data)
        if word:
            shutil.copyfile(word, staging / 'AFML_Source_Transcription.docx')
        staging.rename(destination)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('epub', type=Path)
    parser.add_argument('--word', type=Path)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    arguments = parser.parse_args()
    print(install(arguments.root, arguments.epub, arguments.word))
