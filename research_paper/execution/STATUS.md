# LiDAR recovery-reliability execution status

Updated: 27 September 2026. Status values are `TODO`, `RUNNING`, `BLOCKED`, and `DONE`. A task is `DONE` only when its acceptance checks and handoff are complete. Review gates must audit the underlying artifacts rather than this ledger.

**Latest checks (27 September):** T13 implementation/reproduction checks pass. T14's formal x=-6 m screen passed **32/32**, with all 64 primary runs hash-audited; its seed-14 repeat reconciliation remains for R3. T15's pinned Point-LIO smoke produced 597 valid poses and 1,154 valid local-motion rows; two successful pose files were byte-identical, but Point-LIO health-indicator parity is not established. T16's checked-in analysis reports 32/32 development recovery labels and a 48-pair final sample-size target; rerun the development analysis after the current R3 implementation repairs. **Latest full-suite recheck: 91 tests discovered, 88 passed, 2 errored because the required T14 repeat-audit files are not yet present, and 1 optional SciPy test was skipped. The suite is not green.** R2's checksum table matches 51/51 after the D035 documentation amendment. The first R3 review returned **REVISE** with repairs T16-R3-01 through -06 and T14-R3-01/T16-R3-07. No held-out geometry was generated or screened.

**Current research gate:** R1 remains **PASS for protocol design only**; this does not establish novelty or publication readiness. R2 **PASSES for protocol content only** after two REVISE rounds and a fresh GPT-6 review. D035 refreshes only README/decision-log hashes; the [freeze bundle](../protocol/FREEZE.md) reads back **51/51 listed hashes**. R3's first independent review returned **REVISE**; repairs are underway and no implementation freeze exists. Held-out work remains gated, and the FAST-LIO threshold is not locked.

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
| T16 | RUNNING | T14, T15 | Development analysis is complete; the R3 review found final-runner and repeatability repairs. See [R3 review](../reviews/R3_IMPLEMENTATION.md) and [T16 handoff](handoffs/T16.md). |
| R3 | RUNNING | T13-T16 | First independent review **REVISE**; repair T16-R3-01 through -06 and T14-R3-01/T16-R3-07, then request focused re-review. No implementation freeze or held-out authorization. |

## Current gate

T01-T15 are complete as scoped tasks. T16's development analysis is complete, but its final-runner handoff remains RUNNING while R3 repairs are addressed. The first R3 review returned REVISE; see the repair IDs in [R3_IMPLEMENTATION.md](../reviews/R3_IMPLEMENTATION.md). T14's repeat reconciliation needs explicit R3 adjudication. T15 verifies one pinned Point-LIO pose-output smoke only; indicator parity is not established. T16's FAST-LIO threshold remains a candidate. No final-test result or publication conclusion exists. Held-out inputs/results remain untouched until R3 PASS.

## Next eligible work

**Next eligible work:** repair the R3 findings—T16-R3-01 through T16-R3-06,
plus T14-R3-01/T16-R3-07—without changing frozen scientific choices. Rerun
development-only checks, then request a focused R3 re-review. Only after R3
PASS may the 48-pair geometry screen and final batch begin. See the [current
handoff](CURRENT_HANDOFF.md).
