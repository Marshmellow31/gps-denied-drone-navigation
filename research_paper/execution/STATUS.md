# LiDAR recovery-reliability execution status

Updated: 27 September 2026. Status values are `TODO`, `RUNNING`, `BLOCKED`, and `DONE`. A task is `DONE` only when its acceptance checks and handoff are complete. Review gates must audit the underlying artifacts rather than this ledger.

**Latest checks (27 September):** The repaired T16 analyzer reproduced the development threshold, 32/32 recovery count, one relapse and 48-pair final target. The [four-repeat audit](../evidence/T14_REPEATABILITY_AUDIT.md) now quantifies error, score, warning-state, label, delay and interior-statistic variation. A fresh isolated build reproduced T14's exact source diff and executable; the current-source development replay passed all completion checks. **119 tests ran in both Python environments: 118 passed, one optional SciPy check was skipped.** See the [saved repair verification](../evidence/R3_REPAIR_VERIFICATION.md). The initial independent R3 verdict remains **REVISE** pending focused re-review. No actual held-out geometry was generated or screened. Point-LIO still provides pose-format smoke evidence only; comparable indicators and replication remain part of the [full paper completion plan](PAPER_COMPLETION_PLAN.md).

**Current research gate:** R1 remains **PASS for protocol design only**; this does not establish novelty or publication readiness. R2 **PASSES for protocol content only** after two REVISE rounds and a fresh GPT-6 review. D036 refreshes only README/decision-log hashes; the [freeze bundle](../protocol/FREEZE.md) reads back **51/51 listed hashes**. R3's first independent review returned **REVISE**; the repair package is prepared for re-review and no implementation freeze exists. Held-out work remains gated, and the FAST-LIO threshold is not locked.

**Historical real-recording evidence:** the [LiDAR-only event audit](../data/HILTI_EXP18_EVENT.md) fixed a 31.6–33.6 s exit-only interval before event-anchored errors were summarized. The [T07 development pilot](../evidence/HILTI_EXP18_T07_PILOT.md) contains 1,092 rows with explicit availability reasons. Only 13/56 matched post-exit 1 s windows and **0/56** 3 s windows have usable reference. The reference is partly LiDAR map-registration-derived, so this remains a supporting illustration rather than independent recovery evidence. See the [alternative reference screen](../data/ALTERNATIVE_REFERENCE_AUDIT.md).

**Resume work from the [current handoff](CURRENT_HANDOFF.md).** The table preserves original task IDs; DONE records task acceptance and does not imply a publication result or R2 approval.

| ID | Status | Dependencies | Evidence / handoff |
| --- | --- | --- | --- |
| T01 | DONE | None | [Environment inventory](ENVIRONMENT.md); [handoff](handoffs/T01.md) |
| T02 | DONE | T01 | [Comparison matrix](../literature/COMPARISON.md), four paper notes, [search log](../literature/SEARCH_LOG.md); [handoff](handoffs/T02.md) |
| T03 | DONE | T01 | [Eligibility audit](../data/ELIGIBILITY.md), [66-record inventory](../data/inventory.csv); [handoff](handoffs/T03.md) |
| T04 | DONE | T03 | [Recording inspection](../data/DEVELOPMENT_SEQUENCE.md), [transition annotation](../data/transition_annotations.csv), retained verified LiDAR+IMU subset; [handoff](handoffs/T04.md) |
| T05 | DONE | T04 | [Data contract](../protocol/DATA_CONTRACT.md), [provisional metrics](../protocol/METRICS.md); [handoff](handoffs/T05.md) |
| T06 | DONE | T01, T04, T05 | Pinned FAST-LIO2 build, two development replays, manifests, pose streams and documented quality failure; [handoff](handoffs/T06.md) |
| T07 | DONE | T05, T06 | Evaluator plus 24 tests; frozen scene-defined Hilti development event, 1,092-row error stream with valid/invalid counts; [pilot](../evidence/HILTI_EXP18_T07_PILOT.md), [handoff](handoffs/T07.md). This is software acceptance, not a recovery result. |
| T08 | DONE | T02, T05, T06 | [Source derivation](../protocol/FASTLIO_INFORMATION_DIAGNOSTIC.md), [final audit](../evidence/T08_FINAL_PATCH_AUDIT.md) and [handoff](handoffs/T08.md); no recovery threshold claimed. |
| T09 | DONE | T04, T07, T08; approved amendment | Amended T09 v3 pilot has 400 scans per run, valid reference coverage and reviewed timeline; original real-reference criterion remains documented as failed. [Report](../evidence/SIMULATION_MOTION_V3.md), [handoff](handoffs/T09.md). |
| R1 | DONE | T02-T09; approved amendment | Fresh-model outcome **PASS for protocol design only**; no novelty/publication verdict. [Review](../reviews/R1_FEASIBILITY.md), [gap decision](../literature/GAP_DECISION.md), [handoff](handoffs/R1.md). |
| T10 | DONE | R1 PASS, T02, T08 | [DCReg directional detector specification](../protocol/INDICATORS.md); explicitly an adaptation on shared FAST-LIO correspondences, not full DCReg; [handoff](handoffs/T10.md). T13 implementation is now eligible. |
| T11 | DONE | R1 PASS, T05, T09, T10 | [Frozen v0.4 outcomes](../protocol/METRICS.md) and [development/held-out split manifest](../data/SPLITS.csv); [handoff](handoffs/T11.md). |
| T12 | DONE | R1 PASS, T05, T11 | [Simulation protocol](../protocol/SIMULATION.md), 60 s randomized feasibility smoke [report](../evidence/SIMULATION_RANDOM_LAYOUT_SMOKE.md) and [manifest](../evidence/simulation_random_layout_manifest.json). The formal x=-6 m implementation and batch are recorded under T14. |
| R2 | DONE | T10-T12 | PASS for protocol content only; [independent review](../reviews/R2_PROTOCOL.md), [hash-locked freeze](../protocol/FREEZE.md), read-back **51/51 hashes matched** |
| T13 | DONE | R2 PASS, T10 | [DCReg detector implementation and reproduction evidence](../evidence/INDICATOR_REPRODUCTION.md); [handoff](handoffs/T13.md). Detector adaptation only; no recovery result or threshold claim. |
| T14 | DONE | R2 PASS, T12, T13 | [Formal development batch report](../evidence/T14_DEVELOPMENT_BATCH.md), [32/32 scene screen](../evidence/randomized_layout_geometry_screen_t14_xminus6_dev14_45_v2.json), [hash audit](../evidence/t14_development_batch_manifest.json) and [handoff](handoffs/T14.md). Seed-14 repeat reconciliation is explicitly pending R3 acceptance; no recovery result or threshold claim. |
| T15 | DONE | R2 PASS, T13 | [Pinned Point-LIO smoke report](../evidence/T15_POINTLIO_SMOKE.md), [machine manifest](../evidence/t15_point_lio_smoke_manifest.json), common pose contract passed; FAST-LIO indicator parity not established; [handoff](handoffs/T15.md) |
| T16 | RUNNING | T14, T15 | Repaired development analysis, numerical repeats and fresh lifecycle verification are prepared; independent R3 acceptance remains. See [repair verification](../evidence/R3_REPAIR_VERIFICATION.md) and [T16 handoff](handoffs/T16.md). |
| R3 | RUNNING | T13-T16 | First independent review **REVISE**; current repair package is ready for focused re-review. No implementation freeze or held-out authorization. |

## Current gate

T01-T15 are complete as scoped tasks. T16's development analysis is complete, but its final-runner handoff remains RUNNING while R3 repairs are addressed. The first R3 review returned REVISE; see the repair IDs in [R3_IMPLEMENTATION.md](../reviews/R3_IMPLEMENTATION.md). T14's repeat reconciliation needs explicit R3 adjudication. T15 verifies one pinned Point-LIO pose-output smoke only; indicator parity is not established. T16's FAST-LIO threshold remains a candidate. No final-test result or publication conclusion exists. Held-out inputs/results remain untouched until R3 PASS.

## Next eligible work

**Next eligible work:** focused independent R3 re-review of the completed
repair package. Complete comparable Point-LIO indicator development and its
reviewed freeze before final-layout exposure for the complete paper. R3 PASS
is required for the primary 48-pair screen/batch; it does not complete the
paper or replication. See the [current handoff](CURRENT_HANDOFF.md) and
[paper completion plan](PAPER_COMPLETION_PLAN.md).
