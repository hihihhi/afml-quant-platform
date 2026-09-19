# Feature specification — draft contract template

Do not implement from this template until the associated source section is reviewed.

| Field | Required content |
|---|---|
| Identity | Stable feature ID, source section IDs, algorithm/configuration version. |
| Meaning | Mathematical definition, symbols, units, assumptions and interpretation. |
| Inputs | Typed data, ordering, source/version identity, missing/correction behavior. |
| Availability | Event time versus knowledge/availability time; decision-time cutoff. |
| State | Window, warm-up, lookback, reset, fit-state scope and ownership. |
| Fitting | Train-only procedure, fold ownership, label dependence and seed controls. |
| Outputs | Type, shape, units, valid range, timestamp, validity/missing flags. |
| Errors | Preconditions, rejected states, non-finite values and overflow policy. |
| Storage | Content/configuration/dependency key, provenance and no-op criteria. |
| Reference | Source-faithful implementation, exact small oracle and approved errata. |
| Tests | Boundary, adversarial, no-future-data, batch/stream/replay equivalence. |
| Performance | Measured workload, hardware, build flags, p50/p95/p99 and allocations. |
| Review | Independent review record, source/spec/code/test hashes and blockers. |

Do not invent a plugin ABI or promise hot-swap safety from this document alone.
