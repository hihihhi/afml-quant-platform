# GitHub publication status — 2026-09-19

**The public harness is published.** Repository: `hihihhi/afml-quant-platform`.

The full source-free file tree was committed as
`4e450d3311f911b3d82811d6d5eafc7b38884368`, after GitHub Actions run
[35412630338](https://github.com/hihihhi/afml-quant-platform/actions/runs/35412630338)
successfully verified the payload, regenerated all 1,138 task Markdown files,
ran 18 Python regression tests, audited the public files, and built/tested the
C++ scaffold with GCC and with Clang address/undefined-behavior sanitizers.
Both native configurations ran four CTest cases.

The import record is [archived here](reports/github-publication-import.json).
The temporary write-enabled importer and its bootstrap CI bypass were removed
after the successful import. The regular workflow now requires actual files and
runs checks on every main-branch push and pull request. A skipped workflow is not
a passed test. Later CI results must be read from the run for the relevant commit.

## What publication does not certify

This is a source-locator/task harness and a non-trading C++ scaffold, not a
completed quantitative trading platform. Generated task coverage does not prove
semantic, mathematical, algorithmic or performance correctness. Independent
semantic and mathematical approvals remain unrecorded. The book, full Word
transcription, source images, extracted paragraphs and complete chapter packets
remain private and are not included in this public repository.
