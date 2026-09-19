# Executed verification ledger

## Remote publication and normal CI

| Revision | Run | Observed result | Scope |
|---|---|---|---|
| Full tree published as `4e450d3311f911b3d82811d6d5eafc7b38884368` | [35412630338](https://github.com/hihihhi/afml-quant-platform/actions/runs/35412630338) | Completed, success | Seed checks, 18 Python tests, public audit/regeneration, GCC 4/4 and Clang ASAN+UBSAN 4/4 before publication |
| `2f24427133941c9a4adeefe55421a7af5576bea3` | [35412823452](https://github.com/hihihhi/afml-quant-platform/actions/runs/35412823452) | Completed, success | Ordinary mandatory public and native verification after removing bootstrap controls |

The skipped Verify instance on the bootstrap transport commit is not counted.
A run proves only what its steps actually executed, on that revision. Inspect the
run linked to a newer revision before claiming its tests passed remotely.

## Local post-publication additions

`python -m unittest discover -s instructions/tests -v` completed with **30/30 tests
passing** after ten new task-context provenance tests and two authored-note
coverage tests were added. Public auditing and deterministic regeneration passed.
The full licensed-source integration for the hardened context builder is recorded
in `private-context-integration.json`; its source-containing packet is not public.

## Explicit exclusions

No complete independent semantic or mathematical approval, full editable formula
transcription, financial algorithm completion, throughput/latency benchmark,
formatter/static-analysis run, live trading or deployment is claimed by this
ledger. Historical local full-source/Word checks belong to the earlier private
package and are not relabeled as public CI results.
