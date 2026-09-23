# LiDAR recovery-reliability execution status

Updated: 23 September 2026. Status values are `TODO`, `RUNNING`, `BLOCKED`, and `DONE`. A task is `DONE` only when its acceptance checks and handoff are complete. Review gates must audit the underlying artifacts rather than this ledger.

| ID | Status | Dependencies | Evidence / handoff |
| --- | --- | --- | --- |
| T01 | DONE | None | [Environment inventory](ENVIRONMENT.md); [handoff](handoffs/T01.md) |
| T02 | DONE | T01 | [Comparison matrix](../literature/COMPARISON.md), four paper notes, [search log](../literature/SEARCH_LOG.md); [handoff](handoffs/T02.md) |
| T03 | DONE | T01 | [Eligibility audit](../data/ELIGIBILITY.md), [66-record inventory](../data/inventory.csv); [handoff](handoffs/T03.md) |
| T04 | DONE | T03 | [Recording inspection](../data/DEVELOPMENT_SEQUENCE.md), [transition annotation](../data/transition_annotations.csv), retained verified LiDAR+IMU subset; [handoff](handoffs/T04.md) |
| T05 | DONE | T04 | [Data contract](../protocol/DATA_CONTRACT.md), [provisional metrics](../protocol/METRICS.md); [handoff](handoffs/T05.md) |
| T06 | DONE | T01, T04, T05 | Pinned FAST-LIO2 build, two development replays, manifests, pose streams and documented quality failure; [handoff](handoffs/T06.md) |
| T07 | BLOCKED | T05, T06 | Offline evaluator and eight fixtures pass; two real-data streams retain unavailable results, because the reference body is unverified; [handoff](handoffs/T07.md) |
| T08 | TODO | T02, T05, T06 | Conventional indicator export, derivation and geometry checks; handoff T08 |
| T09 | TODO | T04, T07, T08 | Reviewed transition figure, manifest and `evidence/PILOT_REPORT.md`; handoff T09 |
| R1 | TODO | T02-T09 | `reviews/R1_FEASIBILITY.md` and `literature/GAP_DECISION.md`; handoff R1 |
| T10 | TODO | R1 PASS, T02, T08 | `protocol/INDICATORS.md`; handoff T10 |
| T11 | TODO | R1 PASS, T05, T09, T10 | Completed `protocol/METRICS.md` and `data/SPLITS.csv`; handoff T11 |
| T12 | TODO | R1 PASS, T05, T11 | `protocol/SIMULATION.md`, smoke implementation and checks; handoff T12 |
| R2 | TODO | T10-T12 | `reviews/R2_PROTOCOL.md` and `protocol/FREEZE.md`; handoff R2 |
| T13 | TODO | R2 PASS, T10 | Published comparator implementation and `evidence/INDICATOR_REPRODUCTION.md`; handoff T13 |
| T14 | TODO | R2 PASS, T12, T13 | Frozen simulator and resumable development-run evidence; handoff T14 |
| T15 | TODO | R2 PASS, T13 | Pinned Point-LIO development smoke run or evidenced blocker; handoff T15 |
| T16 | TODO | T14, T15 | `evidence/DEVELOPMENT_REPORT.md` and `execution/FINAL_EVALUATION_HANDOFF.md`; handoff T16 |
| R3 | TODO | T13-T16 | `reviews/R3_IMPLEMENTATION.md` and `protocol/IMPLEMENTATION_FREEZE.md`; handoff R3 |

## Current gate

T01-T06 are complete as execution tasks. T06's two FAST-LIO2 replays completed but grossly under-tracked motion, so neither supports a recovery claim. T07's offline math is implemented and tested, but its real-data acceptance is blocked: GEODE does not establish the reference body convention needed for defensible SE(3) errors. The generated streams explicitly contain zero valid local-error rows. T08/T09 and R1 are not being treated as satisfied. A supported data/backend repair choice is required before moving through the feasibility gate. `Urban_Tunnel01`'s second exit is development-only. No final-test evaluation has been performed. Numerical recovery thresholds remain deliberately unset until T11.
