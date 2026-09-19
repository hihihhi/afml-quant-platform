#!/usr/bin/env python3
"""Compare every generated task byte without overwriting local edits."""
from pathlib import Path
from render_public_tasks import build


def verify(root: Path) -> list[str]:
    expected = build(root)
    failures = [name for name, data in expected.items()
                if not (root / name).is_file() or (root / name).read_bytes() != data]
    actual = {path.relative_to(root).as_posix()
              for path in (root / 'instructions/02-book').rglob('*') if path.is_file()}
    failures.extend(sorted(actual - expected.keys()))
    return failures


if __name__ == '__main__':
    errors = verify(Path(__file__).resolve().parents[2])
    print('Public task regeneration: ' + ('FAIL' if errors else 'PASS'))
    for error in errors:
        print(error)
    raise SystemExit(1 if errors else 0)
