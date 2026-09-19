# Agent entry contract

This is a **book-first, source-traceable research-platform harness**, not permission
to invent a general trading platform or to trade. Read these files in this order
before every task, including after compaction or agent handoff:

1. `instructions/00-governance/INITIAL_PROMPT.md` (the user's original wording).
2. `instructions/00-governance/FOLLOWUP_PROMPT.md` (the user's additional wording).
3. `instructions/00-governance/REQUIREMENTS.md` and `REQUIREMENTS_LOCK.json`.
4. `instructions/03-crosschecks/REVIEW_PROTOCOL.md` and the current status report.
5. The exact chapter/section task, its original source span, assets, and any errata.

Do not replace the prompts with this summary. Hash checks detect prompt-file drift;
the task-context builder includes the complete prompts. Persistence in these files
is intentional: do not rely on an agent remembering a previous conversation.

## Non-negotiable working rules

- Preserve the uploaded edition's order, wording, equation images, code images,
  hierarchy, appendices, exercises, notes, references, and page markers.
- Keep `book_original`, `engineering_requirement`, `proposed_correction`, and
  `external_verification` explicitly distinguishable. Never silently fix the book.
- A generated MD is not a reviewed specification. An extracted equation is not a
  verified equation. An implementation passing its own tests is not an independent
  reproduction. Record what was actually checked, by whom, and against what hash.
- Work in source order. Cross-chapter dependencies may be recorded; they do not
  license skipping chapters or marking a whole chapter complete from one example.
- C++ is the preferred production backend. Python is permitted for source-aligned
  reference implementations, extraction tools, test oracles, and prototypes. A
  prototype is not a permanent language decision. Choose optimizations by measured
  workload results, with correctness and readable code as acceptance conditions.
- Write explicit interfaces, descriptive identifiers, small cohesive functions,
  documented units, ownership, preconditions, error behavior, and deterministic
  tests. Do not copy compressed book snippets as the production coding style.
- Never promise zero physical latency, universal fastest-language results, or
  mathematical infallibility. Preserve those user objectives and define measurable
  tests and exact-versus-approximate numerical contracts without weakening them
  silently. Unmet objectives remain open.
- Later architecture, database/vendor selection, live execution, UI and hot-swap
  design are deferred until the relevant book review gates have been passed.
- Do not read credentials, make trades, connect to a broker, deploy, upload the
  book publicly, rewrite existing Git history, or change repository visibility.
  The user has authorized publishing the source-free harness to the existing
  `hihihhi/afml-quant-platform` repository; that does not authorize public book uploads.
- Do not claim remote creation, CI, visual review, mathematical verification,
  performance benchmarks, or deployment occurred without evidence.

## Repository boundaries

`system/` holds the actual system code, reference implementations, interfaces,
fixtures, tests and benchmarks. `instructions/` holds book-derived MD, provenance,
agent tasks, cross-checks, coding rules and deferred requirements. Root metadata
and `.github/` are supporting infrastructure, not another application.

## Handoff requirements

Include source IDs, hashes, changed files, tests and commands actually run, precise
remaining gaps, and the next source-ordered task. Unchecked boxes remain unchecked.
Use `instructions/templates/REVIEW_RECORD.json` for review evidence. Do not mark
semantic review complete through an extraction or generator script.
