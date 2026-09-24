# LiDAR recovery-reliability execution status

Updated: 24 September 2026. Status values are `TODO`, `RUNNING`, `BLOCKED`, and `DONE`. A task is `DONE` only when its acceptance checks and handoff are complete. Review gates must audit the underlying artifacts rather than this ledger.

**Latest evidence:** The [LiDAR-only event audit](../data/HILTI_EXP18_EVENT.md) fixed a 31.6–33.6 s exit-only interval before event-anchored errors were summarized. The [T07 development pilot](../evidence/HILTI_EXP18_T07_PILOT.md) has 1,092 error-stream rows and explicit availability reasons. T07 closed with 24 passing tests; T08's new mathematical fixtures bring the full experiment suite to **28 passing tests**. Only 13/56 matched post-exit 1 s windows and **0/56** 3 s windows have usable reference. T07's software acceptance is DONE; a recovery result is **not** established. The reference is partly LiDAR map-registration-derived. See the [alternative reference screen](../data/ALTERNATIVE_REFERENCE_AUDIT.md) before downloading another bag.

**Resume work from the [current handoff](CURRENT_HANDOFF.md).** The table tracks the original task IDs; the completed T07 evaluator does not by itself complete T08, T09 or R1.

| ID | Status | Dependencies | Evidence / handoff |
| --- | --- | --- | --- |
| T01 | DONE | None | [Environment inventory](ENVIRONMENT.md); [handoff](handoffs/T01.md) |
| T02 | DONE | T01 | [Comparison matrix](../literature/COMPARISON.md), four paper notes, [search log](../literature/SEARCH_LOG.md); [handoff](handoffs/T02.md) |
| T03 | DONE | T01 | [Eligibility audit](../data/ELIGIBILITY.md), [66-record inventory](../data/inventory.csv); [handoff](handoffs/T03.md) |
| T04 | DONE | T03 | [Recording inspection](../data/DEVELOPMENT_SEQUENCE.md), [transition annotation](../data/transition_annotations.csv), retained verified LiDAR+IMU subset; [handoff](handoffs/T04.md) |
| T05 | DONE | T04 | [Data contract](../protocol/DATA_CONTRACT.md), [provisional metrics](../protocol/METRICS.md); [handoff](handoffs/T05.md) |
| T06 | DONE | T01, T04, T05 | Pinned FAST-LIO2 build, two development replays, manifests, pose streams and documented quality failure; [handoff](handoffs/T06.md) |
| T07 | DONE | T05, T06 | Evaluator plus 24 tests; frozen scene-defined Hilti development event, 1,092-row error stream with valid/invalid counts; [pilot](../evidence/HILTI_EXP18_T07_PILOT.md), [handoff](handoffs/T07.md). This is software acceptance, not a recovery result. |
| T08 | RUNNING | T02, T05, T06 | [Jacobian derivation, four synthetic checks, optional patch and preliminary replay](../protocol/FASTLIO_INFORMATION_DIAGNOSTIC.md) exist; final-patch full export audit and [in-progress handoff](handoffs/T08.md) remain. |
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

T01-T06 are complete as execution tasks. GEODE's two FAST-LIO2 replays grossly under-tracked motion and its common reference body is unverified, so their generated T07 rows retain zero formal local errors. The replacement Hilti-Oxford Exp18 bag was hash-verified and [inspected](../data/HILTI_EXP18_INSPECTION.md); all 1,094 clouds passed adapter checks, and the [55-second smoke replay](../data/HILTI_EXP18_REPLAY.md) yielded 546 valid poses. A [raw-gyro frame audit](../data/HILTI_EXP18_FRAME_AUDIT.md) supports a qualified common IMU body. The [scene-defined exit](../data/HILTI_EXP18_EVENT.md) and [T07 error pilot](../evidence/HILTI_EXP18_T07_PILOT.md) now exist, so T07's explicit real-development valid/invalid-count acceptance is met. **Exp18 is not accepted as sole recovery evidence:** its matched post-exit reference is mostly absent, the scan-structure measure is only a proxy, and the dense reference is not independent of LiDAR. T08/T09 and R1 are not satisfied. No final-test evaluation has been performed. Numerical recovery thresholds remain unset until T11.

## Next eligible work

Complete the clean 55 s replay and availability/provenance audit for T08's **actual online FAST-LIO scan-to-map** diagnostic; preliminary export-on/off pose parity passed, but the final patch's full replay was interrupted. The existing single-scan proxy is not T08. Screen alternative reference files and coverage before any large download. T09 may make a failure/availability timeline, not a recovered-motion claim from Hilti's sparse exit coverage. R1 must either find a qualifying independently referenced transition or record a transparent scope revision; it cannot PASS from Hilti alone. Follow the [current handoff](CURRENT_HANDOFF.md); do not use final-test data.
