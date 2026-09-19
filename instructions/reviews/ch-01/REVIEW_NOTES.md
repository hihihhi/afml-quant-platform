# Chapter 1 — source-ordered author review

**Status:** first-pass authored analysis; not independent approval. **Author:** ChatGPT.
**Date:** 2026-09-19. The complete chapter, its two native tables, exercises,
references, bibliography and notes were read. This document interprets the supplied
source; it neither edits the book nor certifies its historical or empirical claims.

Source: `OPS/c01.xhtml` in the supplied EPUB. XHTML SHA-256:
`e81ce1482aa83a8c304d06d9f234099686da6db0cc9eb9357b6693cbb76c9330`.
EPUB identity and exact task locators are in `SOURCE_COVERAGE.json` beside this file.
These notes cover the chapter's 29 existing task IDs in order; they do not create
extra numbered subsections in the book or replace any generated task.

## Source-derived findings with immediate implications

**Evaluation confidentiality (§1.3.1.4).** The book explicitly directs backtest
results to management rather than back into the other research stations. A shared
UI that gives strategists unrestricted access to final evaluation results would
conflict with that stated separation. A later access-control design must preserve
it, or document a deliberate deviation separately. This is more restrictive than
merely having a different person run the backtest.

**Version lifecycle (§1.3.1.6).** The book prefers running new strategy variations
in parallel with older versions, with each version completing its own lifecycle.
The user's hot-swap requirement must not silently become replacement of an already
validated strategy by an untested version. State transfer, switching mechanics and
resource budgets are later engineering decisions, not specified by this section.

**Two meanings of embargo.** Here the oversight lifecycle starts on observations
after the backtest end date. Do not identify that lifecycle step with a validation
split's embargo mechanism simply because the same word appears later. Preserve
chapter-local definitions and later compare them explicitly.

**Scope of the blueprint (§1.3.1.1 and §1.6).** The source expressly leaves the
specialized data-curation problem largely outside its scope and is agnostic about
the particular ML algorithm. It does not select a database engine, feed supplier,
UI framework, tick-latency SLA or full cleansing rulebook. Those user requirements
stay on the deferred ledger; they cannot be presented as extracted book mandates.

## Ordered task notes

### CH-01

The chapter establishes a specialized financial-ML research process rather than
an executable trading recipe. Preserve its organizational argument, dependencies
and limitations. An implementation milestone here is an auditable work/handoff
contract; it is not an alpha or performance claim.

### S-1.1

Retain all three motivations: connect rigorous analysis with practice, improve the
purpose and conduct of investment work, and explain why financial applications
need more than off-the-shelf ML. The author's predictions and experience-based
judgments are motivating assertions, not accepted empirical tests of this system.
A mathematical result and a plausible observed backtest are each insufficient
alone to establish a financially useful method.

### S-1.2

The proposed main failure mechanism is organizational. Keep that framing separate
from the statistical mechanisms introduced later. Do not transform the passage
into a universal measured failure rate or a claim that every unsuccessful project
has the same cause.

### S-1.2.1

The criticized arrangement assigns isolated researchers whole-strategy discovery
under a deadline, inviting false positives or familiar crowded factors. Preserve
the source's comparison with discretionary-management silos without assuming that
all discretionary investors fail. For this harness, a set of independent agents
with no shared provenance is not automatically a research factory.

### S-1.2.2

The alternative is specialization with a shared understanding of the production
chain. Reusable infrastructure and findings should survive any individual strategy.
Concrete agent-role assignments and evidence formats are project interpretations;
they must not be attributed verbatim to the book.

### S-1.3

Keep the five-part reading sequence: data analysis, modeling/research, evaluation,
additional features, and computing. The author states that chapters assume prior
reading. Record dependencies to later chapters without skipping the earlier
validation and overfitting material.

### S-1.3.1

The production-chain analogy motivates systematic collaboration. Its historical
and alpha-abundance illustrations are not platform benchmarks. Preserve six
stations rather than collapsing all responsibilities into a strategy agent.

### S-1.3.1.1

Curation covers collection, cleaning, indexing, storage, adjustment and delivery.
The meaning of cancellations/replacements and asset-specific events matters; a
syntactically valid record can still be interpreted incorrectly. The section
explicitly excludes much of the needed specialization. Record the source's chapter
reference as supplied even if its wording seems unexpected; do not silently fix it.
Future feed schemas and correction rules require separate, documented decisions.

### S-1.3.1.2

A feature finding can support execution, liquidity monitoring, market making or
position-taking; it is not necessarily a strategy. Catalogue findings independently
of one model or market. Preserve the named labeling, weighting and importance
responsibilities and the references to Chapters 2–9 and 17–19.

### S-1.3.1.3

The strategist must connect informative observations through a theory, including
an economic explanation of the prospective advantage. A combination of predictive
features does not itself supply that explanation. The submitted prototype must
represent the full strategy being evaluated. The book does not disclose a ready-made
profitable strategy; templates must not imply otherwise.

### S-1.3.1.4

Evaluation includes alternative scenarios and meta-information about the search,
not merely the final historical equity curve. Preserve the number of trials and
how the strategy was selected. Record the management-only result flow exactly in
the specification; an analyst must not quietly modify a strategy in response to
reserved evaluation results and treat the same test as untouched evidence.

### S-1.3.1.5

The deployment station must preserve prototype logic while minimizing production
latency and reusing appropriate components. This supports reference/native parity
as a later acceptance criterion. The listed technologies are examples in the
source, not mandatory current products. Record interfaces only: the user's present
scope excludes deployment and live trading.

### S-1.3.1.6

Keep the five stages in order: embargo, paper trading, graduation, re-allocation,
and decommission. Paper trading uses live input and considers parsing, calculation
and execution delays, but the text does not provide a numeric pass threshold.
Graduation involves real positions and is out of current execution scope. The
allocation discussion is qualitative, not an executable formula. Parallel versions
retain separate histories and lifecycle evidence.

### S-1.3.2

Table 1.1 maps Chapters 2–22 across six challenge categories. It is a many-to-many
reading map, not a complete dependency graph or a module boundary declaration.
All 21 chapter rows and eight columns, including Part and Chapter, must remain
in the private transcription. A blank entry does not prove that a topic can never
matter to that chapter's implementation.

### S-1.3.2.1

Preserve the emphasis on informative data and the links to structuring, labeling,
non-IID treatment and feature extraction. Uniqueness of a data source does not
prove its quality or authorize a data licence. Acquisition and lawful use remain
separate user/vendor requirements for the later design phase.

### S-1.3.2.2

The source advocates task-specific functions/classes. For this project, readable
source-faithful references may use Python, while production language selection
follows the user's preference and measured evidence. Do not interpret customized
research tools as permission to rewrite every dependency without justification.

### S-1.3.2.3

Retain parallel-callable function design and the cross-references to Chapters
20–22. Supercomputing and quantum-computing discussion is not an order to procure
hardware, subscribe to services or claim a demonstrated speedup.

### S-1.3.2.4

The argument favors experimental investigation of difficult problems and empirical
out-of-sample evaluation. It does not make mathematical proofs unnecessary where
available, nor turn repeated numerical experiments into universal proofs. Record
which claims are analytical, computational or empirical and preserve assumptions.

### S-1.3.2.5

The meta-strategy objective is a repeatable discovery process, including feature
research across assets, combining predictions and allocation. Acceptance should
check that artifacts can be reused with their original evidence, not merely count
how many strategies an agent generated.

### S-1.3.2.6

Retain the stated three-paradigm backtesting scope and the obligation to question
selection bias. No single historical simulation satisfies this section. The
source's ethical judgments are its framing; the operational project requirement
is an honest trial history and evidence that distinguishes exploration from tests.

### S-1.3.3

Table 1.2 contains ten pitfall/solution mappings. Cross-check every mapping and
chapter reference rather than merging labeling, dependence, leakage and selection
bias into one generic overfitting warning. Purging/embargo, combinatorial paths,
synthetic scenarios and deflated performance measures address different questions;
the source does not say one eliminates the need for all the others.

### S-1.4

The intended audience already has substantial ML and investment knowledge.
Advanced means finance-specific challenges, not merely the newest model class.
Record prerequisite gaps for each implementation rather than filling them silently
with unsourced assumptions or removing difficult material.

### S-1.5

Preserve the multidisciplinary prerequisites and the original Python-library
conventions. A later reproducible environment must identify compatible versions
and changed behavior. The mention of library bugs is a caution to investigate,
not blanket evidence that any particular current version is defective.

### S-1.6

The FAQ contains eleven distinct questions. Keep separate review items for:

1. Financial uses of learned judgment versus predefined-rule automation.
2. Claims about recognizing complex patterns compared with humans.
3. Human/ML combinations and the pointer to meta-labeling.
4. The author's comparison with econometrics and the need for theory.
5. The author's interpretation of black-box criticism.
6. Model-family agnosticism and the shared financial modeling problems.
7. Scope relative to other literature and the edition's stated ambitions.
8. Reading references and recognizing practitioner-specific prerequisites.
9. Backtest overfitting, selection effects and limited financial evidence.
10. Chapter-local notation and the instruction to consult code in ambiguity.
11. Chapter 22's contributors and the production-chain research model.

These are not eleven newly numbered source sections. The chapter's broad claims
about human/ML superiority, compliance, scientific progress and historical events
remain attributed source assertions, not independently verified system properties.
The direction to consult code does not justify concealing a formula/code conflict:
retain both originals, reproduce their behavior, then record a proposed resolution
and its evidence separately.

### S-1.7

Preserve acknowledgments and contributor attributions. They do not imply current
institutional endorsement of this project, permission to reuse every referenced
work, or validation of an agent's implementation.

### CH-01-exercises

Keep all eight numbered exercises and their subquestions. For Exercises 1.1,
1.3 and 1.4, external firm/outcome/ranking evidence is not supplied by this chapter;
record that dependency rather than invent examples or replace dated figures with
current ones. Exercise 1.2 is a hypothetical about resolving overfitting, not a
claim that it is resolved. Exercise 1.5 asks for a methodological comparison;
1.6 asks about attitudes to black boxes. Exercise 1.7 is a key reasoning test:
reproducing a selected result using the same dataset does not account for unseen
research trials. Exercise 1.8's assumptions about conflicts, logs and recourse
must stay explicit; the source is not a complete legal or compliance specification.
No exercise is marked solved merely because its prompt was extracted.

### CH-01-references

Retain the supplied citation order and bibliographic details. Reading a citation
in this chapter is not reading the cited paper. Later mathematical claims requiring
those papers need separately recorded retrieval, derivation and verification.

### CH-01-bibliography

Retain recommended background works separately from works directly referenced.
Do not promote their contents to authoritative project requirements without a
source-specific task and explicit separation from this book's supplied edition.

### CH-01-notes

Retain all three notes and their targets as historical source apparatus. Their
presence is not a successful current-link check or proof of the linked content.
No links were automatically followed while importing the source.

## Proposed checks for later implementations — not yet implemented

- [ ] Reject a strategy submission without theory, prototype identity and trial history.
- [ ] Verify that reserved backtest output is not available to the strategy-development role.
- [ ] Keep feature findings independent from their consuming strategies.
- [ ] Bind every variant to its own version, evidence and oversight stage.
- [ ] Reject promotion based only on a repeated test of an already selected dataset.
- [ ] Distinguish lifecycle embargo from cross-validation embargo in names and interfaces.
- [ ] Treat all unresolved formula/narrative/code disagreements as explicit records.

These checks are engineering interpretations motivated by Chapter 1. They do not
select a database, architecture, UI layout or exchange rule set ahead of the
book-first process. Independent review of these notes and the original remains
open, including both table mappings and the factual scope of the author's claims.
