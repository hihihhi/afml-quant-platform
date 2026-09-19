# Deferred system-design requirements — do not forget, do not prematurely select

The initial prompt is authoritative. This backlog preserves design questions while
source review proceeds in book order. Nothing here selects a database, API provider,
UI framework, exchange, broker, topology or trading permission.

## Market data, durability and accessibility

Preserve raw provider payloads and identities without loss; source event time,
receive time, sequencing, corrections, duplicates and availability require explicit
contracts. Live capture, historical APIs and already stored data must eventually
share reproducible downstream semantics. Define provider limits and performance
budgets from evidence. Immediate durable acknowledgment and minimum latency may
conflict; measure and expose the chosen durability guarantee, never hide it.

Evaluate compressed storage and metadata/query access as one design. Keep stored
artifacts addressable, with provenance, versions and access methods. Distinguish raw,
cleaned, feature, model, backtest and audit layers. Lossless compression must round-trip
all represented information. Database selection follows reviewed workload and access
requirements; no claim is made that AFML prescribes a particular storage engine.

Unchanged input plus unchanged transformation version/configuration should allow a
no-op. New information, provider corrections, corporate actions, changes to cleansing
rules, calendars or dependency versions may require controlled recomputation even
without changing the target market. This is a design consideration to check, not a
silent rewrite of the user's instruction to avoid unnecessary updates.

## Research lifecycle

Support labels/sample weights, source-described validation and feature analysis,
model-based and non-ML strategies, walk-forward and book-specific backtesting methods.
Store all trials, including failed ideas, so multiple testing and selection are visible.
Feature caches need content/configuration/data/fit-state identity and point-in-time
availability. Train-only fitted transforms and source-derived leakage safeguards are
mandatory review subjects, not yet implemented guarantees.

## Extensibility and hot swapping

Features, strategies, models, markets and displayed information must be replaceable.
Later design must address interface/version compatibility, state migration, quiescence,
in-flight work, deterministic replay, rollback and fault isolation. Do not unload a
live library with outstanding references or claim a strategy can always be swapped
without state consequences. A deployment implementation is outside this phase.

## Market and industry hierarchy

The phrase `A stock` remains unresolved: it may mean a particular stock, a stock
universe or Chinese A-shares. Do not hard-code an exchange, trading restriction or
country. Preserve the desired market -> universe -> sector/industry -> instrument
views, their overview statistics and calculations. Sector membership, classifications
and universe membership need time/version semantics before research uses them.
WorldQuant BRAIN is a later UX/workflow reference, not a license to copy inaccessible
proprietary definitions or silently assume its implementation.

## Researcher/trader UX

A neat interface should make source lineage, stale data, fit/test partitions,
experiment comparisons, performance uncertainty, warnings and drill-down visible.
Specify user workflows before choosing widgets. Research and live-trading controls
must be distinguishable; no UI has been designed or built in this scaffold.

## Promotion and deployment boundary

Book review, code correctness, reproducibility and measurement come first. Production
permissions, market-data entitlements, security review and deployment remain explicit
later work. Do not connect to markets or execute trades while building this harness.
