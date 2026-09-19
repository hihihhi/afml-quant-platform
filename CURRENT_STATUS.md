# Current status — 2026-09-19

## Published and verified

The public GitHub harness contains 1,138 generated source-ordered task Markdown
files: 369 chapter/section tasks, 653 equation-image tasks, 100 snippet tasks and
16 ancillary-document tasks. It preserves the uploaded edition's 22 chapters and
280 numbered sections, the two working roots, the complete original prompts,
29 requirement IDs, prompt hashes, review validation and private task packets.

The full tree was published in commit
`4e450d3311f911b3d82811d6d5eafc7b38884368`. GitHub Actions
[publication run 35412630338](https://github.com/hihihhi/afml-quant-platform/actions/runs/35412630338)
completed successfully: 18 Python tests, public integrity auditing, exact Markdown
regeneration, four GCC CTest cases and four Clang CTest cases with address/undefined-
behavior sanitizers. After removing the temporary importer and bootstrap bypass,
[ordinary CI run 35412823452](https://github.com/hihihhi/afml-quant-platform/actions/runs/35412823452)
also completed successfully on commit `2f24427133941c9a4adeefe55421a7af5576bea3`.

The current suite has **30 Python tests** after task-packet provenance hardening
and Chapter 1 note-coverage checks. All 30 passed locally; the current revision's
remote outcome must be read from its own GitHub Actions run. The earlier 18-test
runs are not evidence that later changes passed remotely. Native suites remain
four tests per compiler configuration. They test a non-trading C++20 scaffold,
not completed financial algorithms.

Locally, all 1,138 source locators were compared against the exact uploaded EPUB
across all 38 reading-order documents. Source installation using the actual EPUB
and Word file, followed by generation of CH-01's private context packet, succeeded.
The hardened packet was also checked for the complete three authority documents,
four project contracts and original chapter XHTML. See
[the source-integration report](instructions/reports/private-context-integration.json).
Public CI has no licensed book and does not repeat private Word/pixel checks.
The earlier full local package has separate source/Word verification reports;
its larger test suite is not the public suite.

## Authored book review

[Chapter 1 first-pass notes](instructions/reviews/ch-01/REVIEW_NOTES.md) now cover
all 29 chapter tasks, both tables, eleven FAQ questions and eight exercises in
source order. Source/notes hashes and locators are recorded and checked by tests.
These are authored review notes, not independent approval or solved exercises.
They identify constraints for evaluation-result access, parallel strategy versions,
chapter-local notation, prototype/native parity and the limits of the book's
coverage of data curation. No remaining architecture was silently invented.

## Outstanding — do not mark complete

- Independent word-by-word semantic approval and mathematical approval: zero
  recorded. Source preservation and generated coverage are not substitutes.
- Source-specific authored reviews beyond Chapter 1, including all formula/code
  image transcriptions, ordinary inline expressions, assumptions and derivations.
- Fully implementation-ready specifications and book-faithful algorithms,
  followed by verified native implementations and measured benchmarks.
- Actual ingestion, cleansing, compressed storage/access, feature/model pipelines,
  all backtesting paradigms, execution, plug-ins/hot swapping, market hierarchy
  and UI. Their requirements remain recorded, not silently dropped.
- Demonstrations of latency, durability, throughput and numerical accuracy.

## Next source-ordered work

Privately install the source, read Chapter 1 notes with the full original, and
resolve its review requirements before advancing approval gates. Read chapter
parents for context and process their children in source order. Parent approval
requires child approval; this does not require pretending a chapter heading's
short direct locator contains the whole chapter. The context builder retains the
entire source document and rejects changed prompts, catalogs, indexes and task MD.

The exact covariance counterexample in ERR-0001 remains a separate local finding;
it does not authorize changing the original or approving Chapter 16.

No live trades, broker access, deployment, visibility changes or history rewrites
have been performed. The repository is public; source-containing files stay local.
