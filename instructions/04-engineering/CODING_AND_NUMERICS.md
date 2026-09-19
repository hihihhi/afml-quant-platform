# Readable code and numerical acceptance rules

**Phase:** engineering guardrails requested by Oscar; these are not claims that the
book specifies this exact software design. Final component designs remain deferred.

## Language policy

C++20 is the initial production-backend target. C is permitted for a justified ABI,
provider integration or constrained kernel; it is not presumed faster merely because
it is C. Python is allowed for source-faithful reference implementations, exact test
oracles, extraction, verification and prototypes. Moving a validated prototype into
the production path requires an explicit measured decision. Retain the reference
when porting; a port's correctness is not established by translating syntax.

A benchmark compares real workloads, build flags, data layout, dependencies,
parallelism, resource use and numerical results. Language choice alone is not a
performance guarantee. Do not trade intelligibility or correctness for unmeasured
micro-optimizations. Primary reference: C++ Core Guidelines,
https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines (consulted 2026-09-19).

## Style and interfaces

Use descriptive names, small cohesive functions, narrow interfaces, named units,
explicit ownership and RAII. Avoid global mutable state, unchecked casts, magic
numbers and compressed one-line book-style implementations in production. Comments
explain intent, mathematical assumptions and invariants rather than restating syntax.
Public APIs document units, index ranges, input validity, output meaning, failure
behavior, memory ownership, thread safety, and deterministic-state assumptions.

Use typed domain wrappers where ambiguity would create defects. Avoid raw owning
pointers. Do not hide I/O, random-number generation, allocations or mutable fit state
inside apparently pure feature calculations. Never train, normalize, select features,
calibrate thresholds or fit imputations on a held-out fold by accident.

Format with the checked-in policy. New code requires review and tests; legacy book
snippets remain separate source artifacts. Dependencies and toolchain versions must
be recorded. Do not turn a warning off without explaining why it is safe.

## Precision and exactness

Specify which quantities require exact representation (for example feed integers,
source bytes, counters and discrete event identities) and which require numerical
approximation (for example estimated probabilities). Do not silently round incoming
values or reinterpret timestamps. Select scales, overflow checks, rounding modes,
null/NaN rules and units explicitly during later data-contract design.

Exact integer/rational or higher-precision oracles should test manageable cases.
For floating algorithms, justify absolute/relative tolerances, cancellation handling,
conditioning, accumulation order and reproducibility requirements. Reject non-finite
or out-of-domain inputs according to the approved specification, not ad-hoc defaults.
Matrix dimension, indexing, endpoint inclusion, label overlap and time alignment are
logical correctness requirements separate from numeric tolerance.

Do not enable unsafe floating-point optimization (`fast-math`) by default. Test any
changed arithmetic or parallel reduction against the reference. An exact raw feed
archive and lossless compression do not imply zero arithmetic error in ML estimates.

## Required evidence before performance claims

Unit and adversarial tests; independent oracle comparisons; property/metamorphic
checks where appropriate; reproducibility and train/test leakage checks; round-trip
storage tests; fault-injection/replay tests for stateful components; thread safety;
compiler warnings; address/undefined-behavior sanitizers; actual benchmark artifacts.

Latency reports separate provider/network delivery, local receive, decode, durable
acknowledgment, normalization, feature calculation, inference and UI rendering.
Microsecond timestamp resolution is not microsecond end-to-end latency. No physical
system has zero delay; the user's latency ambition stays open until a numerical
service objective and workload are agreed and demonstrated. No benchmark exists yet.
