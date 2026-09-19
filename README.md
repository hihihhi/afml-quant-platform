# AFML Quant Platform

Book-first agent harness for a quantitative research, backtesting and trading
platform based on the user-supplied edition of Marcos López de Prado's *Advances
in Financial Machine Learning*. **This is not a completed trading platform.**

## Two working roots

- `system/`: readable C++20 scaffold, native tests, exact Python reference oracle
  and benchmark requirements. No feed, model, backtest or trading engine is enabled.
- `instructions/`: locked original prompts, 29 requirements, source-ordered task
  Markdown, review gates, reusable feature/strategy/model specifications and
  explicitly deferred engineering requirements.

Start with [AGENTS.md](AGENTS.md), then read the original prompts it references.
They are the authority, not this summary. Task packets include their complete text.

## Book coverage and public/private boundary

The public task view contains **1,138 task Markdown files**: 369 chapter/section
nodes (22 chapters, 280 numbered sections and 67 unnumbered chapter sections),
653 equation-image tasks, 100 snippet tasks and 16 ancillary-document tasks.
The source reading order contains 38 documents. Do not call 653 the total count of
mathematical expressions: ordinary inline mathematics still requires review.

Open [the book index](instructions/02-book/README.md). Each task records its source
XHTML document, body-iterator locator, supplied page markers, parent, work and
cautions. All descriptions remain **draft engineering interpretations**. No
semantic or mathematical approval has been generated.

This repository is public. The EPUB, Word transcription, images, verbatim
paragraphs, hidden MathML and full-source task packets must remain local. The
public view is a compact projection of the complete local working package: it
retains the same task IDs and source locators but does not copy the private
byte/pixel manifests or claim that its Markdown hashes equal the earlier private
extraction's hashes. The locked EPUB hash binds the source edition. The earlier
complete Word/source audit and the public-view audit are different checks.

## Run public tests and native scaffold

```sh
python -m pip install -r instructions/requirements-dev.txt
python -m unittest discover -s instructions/tests -v
python instructions/tools/audit_public_view.py --tracked-only
python instructions/tools/verify_generated.py
cmake -S system -B build/native -DCMAKE_BUILD_TYPE=Debug
cmake --build build/native --parallel 2
ctest --test-dir build/native --output-on-failure
./build/native/afml-platform --status
```

The status response deliberately reports `bootstrap_only`. Trading and backtest
commands fail rather than returning fabricated results.

## Install your licensed source locally

```sh
python instructions/tools/install_source.py /path/to/advances-in-financial-machine-learning.epub \
  --word /path/to/AFML_Source_Transcription.docx
python instructions/tools/audit_public_view.py --tracked-only \
  --epub instructions/01-source/private/original.epub
python instructions/tools/build_task_context.py CH-01
```

The Word argument is optional. The importer verifies the exact retained edition
and optional transcription hash, rejects unsafe archive paths, and refuses to
overwrite an existing source workspace. It does not fetch a book from the internet.
The packet is written to the Git-ignored `instructions/task-context/` directory.
It includes the entire source document so surrounding formulas, nested lists and
notes are not silently lost at a snippet boundary. Open the original image assets
as well; hidden markup alone is not mathematical verification.

The supplied Word transcription is reflowed, not a publisher-page facsimile; its
formula images preserve the source but are not all editable mathematical objects.
No new Word layout review is claimed by public CI.

## Review and implementation gates

Read [the review protocol](instructions/03-crosschecks/REVIEW_PROTOCOL.md) and
[the coding/numerics contract](instructions/04-engineering/CODING_AND_NUMERICS.md).
The review validator requires distinct named implementer/reviewer identities,
hashed evidence, exact specification/source binding and child reviews. Those
checks validate record structure, not the truth or identity of a reviewer.

C++ is preferred for production; Python is allowed for book-aligned references,
prototypes and independent exact/high-precision oracles. Readability, correctness
and measured workload performance govern promotion. No universal fastest-language,
zero-delay, zero-rounding or investment-performance guarantee is made.

Detailed database/vendor selection, feeds, feature/model implementations,
backtesting engines, hot swapping, A-stock hierarchy and UI remain gated behind
book review. Deployment and live orders are outside this task.

See [CURRENT_STATUS.md](CURRENT_STATUS.md) for executed checks and remaining work.
