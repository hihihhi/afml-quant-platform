# Requirements ledger

**Authority:** `INITIAL_PROMPT.md` and `FOLLOWUP_PROMPT.md`, preserved in their original wording. This ledger is an interpretation, not a substitute. Python permission supplements the C/C++ preference.

| ID | User requirement | Required evidence / constraint |
|---|---|---|
| U001 | AFML is the blueprint; book before remaining design | Edition fingerprint; ordered full-source capture; source-linked section tasks |
| U002 | C/C++ preferred throughout backend; fastest best language | C++ production target; Python references permitted; equivalence and workload benchmarks before promotion |
| U003 | Database included; compressed data remains callable | Raw/clean/features lineage; lossless round trips; selective reads and update benchmarks; source review before storage selection |
| U004 | Plug-in and hot-swap features, strategies, models, markets, displayed information | Versioned interfaces; state handover; capability checks; in-flight work policy; shadow validation and rollback |
| U005 | Neat UI and useful quant research/trading UX | Research/trading workflows, drill-down context, lineage, experiment comparison; evaluation with user tasks |
| U006 | Lossless ticks, microsecond objective, continuous operation | Preserve sequence/precision; replay, deduplication and gap accounting; distinguish exchange/network/capture/durability/processing latency; burst and failure tests |
| U007 | Local history without API; API history; immediate live storage | Three input modes; schema equivalence; documented durability acknowledgment; bounded backlog |
| U008 | Clean and store data without rewriting unchanged data | Immutable raw source; transformation/version/content hash; point-in-time corrections; idempotency and no-op writes |
| U009 | Store/cache generated features | Feature version, source snapshot, parameters and as-of lineage; cache invalidation tests |
| U010 | Train then backtest, or backtest strategies directly | Model and non-ML paths with the same causal execution assumptions |
| U011 | All book testing methods, not only walk-forward | Chapters 7, 9, 11–16 and dependencies: purging/embargo, CPCV, synthetic tests and selection-bias metrics; no single-test substitute |
| U012 | Reusable feature and strategy templates | Source locator; inputs, outputs, parameters, units, availability time, state, numerical contract, fixtures and validation interfaces |
| U013 | Start with A stock; expandable markets and sector/industry drill-down | Retain the phrase A stock; confirm interpretation before exchange-specific rules; point-in-time membership |
| U014 | WorldQuant BRAIN-style hierarchical overviews | User inspiration, not a claim of book coverage or a copied proprietary specification |
| U015 | Extract every format/formula into Word | Full text/image order; original archive/XHTML/CSS; equation images and MathML register; visual review |
| U016 | Every chapter/subchapter to any actual supplied depth | No hard-coded heading-depth cap; parent/child links; unnumbered apparatus retained |
| U017 | Descriptions, work and cautions as TODOs | Source-specific scope, equations/snippets, independent review before implementation |
| U018 | Page by page, word by word, book order | Page anchors and explicit missing markers; full text/image sequences; no invented page spans |
| U019 | Find book errors; strictly preserve original first | Immutable original, separate errata, counterexamples, explicit correction acceptance |
| U020 | Good engineering and computer-science practice | Readability, ownership, types/contracts, reproducible builds and CI |
| U021 | Quick precise mathematics without logic/precision errors | Exact representations where defined; overflow checks; analytical tests; high-precision oracles; declared tolerances elsewhere |
| U022 | Evaluate and test code | Unit, integration, property, differential, adversarial, replay, soak and benchmark evidence as applicable; independent review |
| U023 | GitHub repository and development there | Existing hihihhi/afml-quant-platform verified; actual commits and readback required; publication progress is not complete system delivery |
| U024 | One actual system root and one instructions root | system/ and instructions/; root metadata and .github/ only support infrastructure |
| U025 | Cross-check Markdown | Independent source parsing, hierarchy and coverage, links, provenance and review gates |
| U026 | Retain initial wording across agents | Verbatim prompts, SHA-256 locks, complete prompts in every generated task packet |
| U027 | Python first allowed where appropriate | Explicit oracle/prototype labels; source parity and tests before production migration |
| U028 | Readable code and good practice | Formatting/lint rules, small named functions and documented decisions |
| U029 | Templates extend to deployment boundary; deployment excluded | Research/build/test artifacts only; no broker, live order submission or deployment |

## Objectives must not be silently redefined

Timestamp resolution is not end-to-end latency. The microsecond objective remains unproven until topology, workload, hardware, durability policy, percentiles and burst conditions are measured. C++ alone does not certify zero delay.

Preserve raw bytes and exact source-valued prices, sizes, sequence IDs and timestamps. Statistical real-valued arithmetic needs explicit error bounds; matching Python and C++ values is not proof when both share a bug.

A market change is not the only potential invalidation cause: source revisions, corporate actions, schema/cleaning/feature changes and corrected availability times must be assessed. This is an engineering proposal, not replacement book content.

Preserve and reproduce the book first. Suspected errors block the affected implementation's approval; they never authorize silently changing the transcription.

A stock remains the user's exact term. Mainland China A-shares are a possible interpretation, not yet a confirmed exchange-specific specification. Calendars, settlement, lots, price limits and shorting rules remain deferred.
