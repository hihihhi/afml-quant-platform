#!/usr/bin/env python3
"""Validate source-bound review evidence without pretending to authenticate it.

An approval must bind the current specification and every applicable gate to
hashed evidence. Parent approval additionally requires valid child review files.
This is a structural check, not a proof of the evidence or a digital signature.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

GATES = ("source_review", "math_review", "reference", "native", "performance")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def checked_evidence(
    evidence: dict[str, Any], root: Path, errors: list[str]
) -> Path | None:
    """Resolve a repository-local file only after checking its stated digest."""
    relative = evidence.get("path", "")
    if not isinstance(relative, str) or not relative:
        errors.append("Evidence requires a nonempty relative path.")
        return None
    candidate = Path(relative)
    path = (root / candidate).resolve()
    if candidate.is_absolute() or not path.is_relative_to(root) or not path.is_file():
        errors.append(f"Invalid evidence path: {relative!r}.")
        return None
    if digest(path) != evidence.get("sha256"):
        errors.append(f"Evidence hash mismatch: {relative}.")
        return None
    return path


def _validate(
    record: dict[str, Any],
    root: Path,
    tasks: dict[str, dict[str, Any]],
    source_hash: str,
    ancestors: frozenset[str],
) -> list[str]:
    errors: list[str] = []
    if record.get("schema_version") != 1:
        errors.append("Unsupported schema version.")
    if record.get("status") not in {"draft", "blocked", "approved"}:
        errors.append("Unsupported aggregate status.")
    if record.get("status") != "approved":
        return errors

    task_id = record.get("task_id", "")
    if task_id in ancestors:
        return [f"Cyclic child-review dependency: {task_id}."]
    next_ancestors = ancestors | {task_id}
    implementer = record.get("implementer", "").strip()
    reviewer = record.get("reviewer", "").strip()
    if not implementer or not reviewer or implementer.casefold() == reviewer.casefold():
        errors.append("Approval requires named, distinct implementer and reviewer.")
    if record.get("blockers"):
        errors.append("An approved record cannot retain blockers.")
    if record.get("source_epub_sha256") != source_hash:
        errors.append("Source hash does not match the requirement lock.")

    task = tasks.get(task_id)
    if task is None:
        errors.append("Task ID is not in the source inventory.")
    elif record.get("specification_path") != task["path"]:
        errors.append("Specification path does not belong to this task.")
    elif record.get("specification_sha256") != task["md_sha256"]:
        errors.append("Specification hash does not match the task index.")

    expected_children = sorted(
        item["id"] for item in tasks.values() if item["parent"] == task_id
    )
    if sorted(record.get("child_task_ids", [])) != expected_children:
        errors.append("Child task inventory must match the source hierarchy.")
    children = record.get("child_reviews", [])
    if sorted(child.get("task_id", "") for child in children) != expected_children:
        errors.append("Parent approval requires one hashed review for every child.")
    else:
        for child in children:
            path = checked_evidence(child, root, errors)
            if path is None:
                continue
            try:
                child_record = json.loads(path.read_text(encoding="utf-8"))
                if child_record.get("task_id") != child["task_id"]:
                    errors.append(f"Child review task mismatch: {path.name}.")
                    continue
                if child_record.get("status") != "approved":
                    errors.append(f"Child is not approved: {child['task_id']}.")
                    continue
                child_errors = _validate(
                    child_record, root, tasks, source_hash, next_ancestors
                )
                errors.extend(f"Child {child['task_id']}: {error}" for error in child_errors)
            except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
                errors.append(f"Unreadable child review: {path.name}: {error}.")

    evidence_records = [
        {
            "path": record.get("specification_path", ""),
            "sha256": record.get("specification_sha256", ""),
        }
    ]
    for gate in GATES:
        state = record.get("gates", {}).get(gate, {})
        if state.get("state") == "not_applicable":
            if not state.get("reason", "").strip():
                errors.append(f"{gate}: not-applicable needs a reason.")
            if gate == "source_review":
                errors.append("Source review is never not applicable.")
        elif state.get("state") != "passed" or not state.get("evidence"):
            errors.append(
                f"{gate}: approval requires passed evidence or justified not-applicable."
            )
        evidence_records.extend(state.get("evidence", []))
    for evidence in evidence_records:
        checked_evidence(evidence, root, errors)
    return errors


def errors_for(record: dict[str, Any], root: Path) -> list[str]:
    """Return validation errors; malformed or unreadable records fail closed."""
    root = root.resolve()
    try:
        lock = json.loads(
            (root / "instructions/00-governance/REQUIREMENTS_LOCK.json").read_text()
        )
        index = json.loads((root / "instructions/02-book/task_index.json").read_text())
        tasks = {task["id"]: task for category in ("sections", "equation_images", "snippets", "ancillary_documents") for task in index[category]}
        return _validate(record, root, tasks, lock["source_epub_sha256"], frozenset())
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        return [f"Invalid record or local inventory: {error}."]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        errors = errors_for(json.loads(args.record.read_text()), args.root)
    except (OSError, ValueError) as error:
        errors = [str(error)]
    print(
        json.dumps(
            {
                "valid_record_structure": not errors,
                "errors": errors,
                "semantic_authentication": False,
            },
            indent=2,
        )
    )
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
