# Cross-check and approval protocol

## Authority and scope

Read the complete locked initial and follow-up prompts for every task. The supplied
EPUB is the edition authority, not a web transcription or a current library API.
The source archive and extracted member hashes protect byte-level fidelity.
Word is a reflowed transcription, not publisher-layout facsimile or editable math.
Markdown is a task layer, never a substitute for reading the corresponding source.

## Independent checks, not repeated assertions

The producer inventories with lxml. `tools/source_build/crosscheck.py` independently reads the
EPUB with the standard-library XML parser and compares source order, headings,
page markers, image placements, MathML counts, tables, snippet titles and complete
visible text against the inventories and Word output. It also checks prompt locks,
MD hashes, parent relationships, local links and source asset pixels.
This is an independent **code path**, not an independent human or mathematical
reviewer. Checksums can reveal drift; they cannot prove a claim in the book true.

The structural audit has a limited interpretation: its PASS means that the stated
machine-checkable preservation properties match the uploaded source. Unmarked
print pages, inline HTML mathematics, editable equation transcription, interpretation
of prose, and proofs still require the specific review records below.

## Review layers

1. **Source preservation:** immutable archive/member hashes; all spine documents,
   headings, pages, tables, code and equation images retained. Inventory and
   export disagreements block further approval until resolved.
2. **Description cross-check:** read the full direct source span and all its lists,
   captions and notes; compare each proposed work/caution statement. Label every
   statement `book_original`, `engineering_requirement`, `proposed_correction`,
   or `external_verification`. Record omitted requirements and unsupported claims.
3. **Mathematical cross-check:** record every expression, including ordinary HTML
   symbols not stored as images. Compare image versus hidden MathML where present;
   define each symbol, index, domain, unit, estimator and assumption. Work the
   derivation, limiting cases, adversarial inputs and independent numerical oracle.
   A missing proof or ambiguous convention is a blocker, not a guessed default.
4. **Reference reproduction:** preserve book code separately, including errors.
   Document Python/library version dependencies and any compatibility edits. Match
   source examples, random seeds and train/test conventions. Do not execute source
   code automatically during extraction.
5. **Native implementation:** a readable C++ implementation must match approved
   reference behavior under a declared numerical contract. Compare edge cases,
   invariants, losslessness and deterministic replay; record permitted tolerances.
6. **Code review and measurement:** compile warnings, unit/property/regression tests,
   sanitizers, resource ownership, interfaces and dependency checks first. Measure
   latency distributions, throughput and memory on a stated workload and hardware.
   No universal fastest-language or zero-latency claim is inferred from one test.
7. **Independent approval:** a reviewer other than the implementer signs an evidence
   record bound to the exact source/specification/code/test hashes. A changed hash
   invalidates the affected approval. Parent completion requires direct-span and
   every child approval; component implementation cannot approve a whole chapter.

## States and transitions

`preserved -> draft -> source_reviewed -> math_reviewed -> reference_verified ->
native_verified -> performance_measured -> approved` describes applicable gates,
not an automatic script transition. A conceptual section may mark a computational
gate not applicable, but only with a reason and reviewer. `blocked` can apply at any
stage. Each gate has its own evidence; retain the earlier source unchanged.

All initial book tasks are `draft_pending_independent_review`. No generated file
is a signed review record. The review-record validator rejects empty evidence,
missing independent reviewer, and approval with unfinished required gates. For
section/chapter records it also recursively loads hashed child review files; a
list of child IDs or a self-declared boolean does not establish child approval. It
validates record structure and file hashes, not the truth or identity of a signature.
Actual enforcement against a malicious author also requires repository permissions
and human review; those remote controls are not configured by this scaffold.

## Source order and cross-chapter dependencies

Process chapter 1 onward and retain subheadings as encountered in the source. A
parent introduction may precede its children without being called complete. Record
cross-chapter dependencies as links; do not reorder the book to fit a preferred
software architecture. After all source review is complete, use the reviewed graph
to plan implementation ordering explicitly. The source-first queue starts at CH-01;
front matter and part dividers remain indexed and need their own read-through.

## Mandatory discrepancy record

Record the source ID, exact original statement/image, source hash, observed problem,
minimal counterexample or evidence, proposed correction, scope impact, author-
confirmation status, reviewer decision, and separate book-faithful/corrected fixtures.
Never call an assistant's proposed correction publisher-confirmed without evidence.
The initial register is [ERRATA.md](ERRATA.md).

## Completion reporting

Report counts separately for preserved, drafted, source-reviewed, mathematically
reviewed, implemented, tested and approved. Keep unticked gates visible. Passing
this audit does not make the platform implemented, profitable, production-ready,
deployable or mathematically infallible. Live trading is outside this phase.

## Rebuilding the private preservation package

The source-rich Word and Markdown generator is available in this repository, but
its output must remain private. Follow `instructions/01-source/PRIVATE_REBUILD.md` in the public project.
The wrapper builds under `instructions/01-source/private/rebuilds/`, checks the
locked edition and all numbered-section descriptions, then runs the independent
source/Word/Markdown audit. It never replaces the public task projection.
A new Word export remains visually unapproved until every rendered page is reviewed.
