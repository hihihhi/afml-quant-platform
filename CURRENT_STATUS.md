# Current status — 2026-09-19

## Published and verified

The public GitHub harness contains 1,138 generated source-ordered task Markdown
files: 369 chapter/section tasks, 653 equation-image tasks, 100 snippet tasks and
16 ancillary-document tasks. It preserves the uploaded edition's 22 chapters and
280 numbered sections, the two working roots, the complete original prompts,
29 requirement IDs, prompt hashes, review validation and private task packets.

The full tree was published in commit
`4e450d3311f911b3d82811d6d5eafc7b38884368`. GitHub Actions
[run 35412630338](https://github.com/hihihhi/afml-quant-platform/actions/runs/35412630338)
completed successfully: 18 public-harness Python tests, public integrity auditing,
exact Markdown regeneration, four GCC CTest cases and four Clang CTest cases
with address/undefined-behavior sanitizers. These are checks of the harness and
non-trading C++20 scaffold, not completed financial algorithms.

Locally, all 1,138 source locators were compared against the exact uploaded EPUB
across all 38 reading-order documents. Source installation using the actual EPUB
and Word file, followed by generation of CH-01's private context packet, also
succeeded. Public CI has no licensed book and does not repeat private Word/pixel
checks. The earlier full local package has separate source/Word verification
reports; its larger test suite is not the 18-test public suite.

## Outstanding — do not mark complete

- Independent word-by-word semantic approval and mathematical approval: zero
  recorded. Source-preservation and generated-coverage checks are not substitutes.
- Editable transcription and verification of all formula/code images, ordinary
  inline expressions, assumptions, derivations and numerical oracles.
- Fully implementation-ready specifications and book-faithful algorithms,
  followed by verified native implementations and measured benchmarks.
- Actual ingestion, cleansing, compressed storage/access, feature/model pipelines,
  all backtesting paradigms, execution, plug-ins/hot swapping, market hierarchy
  and UI. Their requirements remain recorded, not silently dropped.
- Demonstrations of latency, durability, throughput and numerical accuracy.

## Next source-ordered work

Use `python instructions/tools/build_task_context.py CH-01` after privately
installing the source. Review the complete chapter and its child tasks in source
order. Authored review notes and proposed corrections must be kept separate from
the original, with explicit scope and unchecked independent approval gates.
The exact covariance counterexample in ERR-0001 does not authorize changing the
original text or approving any unrelated chapter.

No live trades, broker access, deployment, visibility changes or history rewrites
have been performed. The repository is public; source-containing files stay local.
