# LiDAR recovery-reliability execution status

Updated: 29 September 2026. Status values are `TODO`, `RUNNING`, `BLOCKED`, and `DONE`. A task is `DONE` only when its acceptance checks and handoff are complete. Review gates must audit the underlying artifacts rather than this ledger.

**Latest checks (29 September):** The T16 development threshold, 32/32 recovery count, one relapse and 48-pair planning target still reproduce. The [four-repeat audit](../evidence/T14_REPEATABILITY_AUDIT.md) quantifies score, error, warning and label variation. FAST-LIO R3 software/provenance repairs and its native lifecycle were independently accepted. Point-LIO's bounded implementation workflow also received PASS, and the full suite ran 165 tests: 163 passed, two optional SciPy checks skipped, including a compiled native reset fixture and runner helper tests. The startup failure from the first sidecar-on attempt was diagnosed (prior-boot kernel ntfs3 iomap BUG); runner process cleanup was upgraded and tested. Both initial runs are preserved as development evidence. The fresh R2 sidecar-on/off feasibility replay completed cleanly on Acer: poses are byte-identical (`851e8b3709e26e2c1bc607d8d6507e1c303746129e8d2bd19c761f8efce727ee`), full raw frame coverage is verified (600/600 frames, 181,903 groups, 222,498 Jacobian rows), 3 startup frames are unavailable (matching FAST-LIO), and `verify_pointlio_feasibility_pair.py` returned PASS. No threshold was fitted on seed 14 and no held-out data were accessed. Overall R3 remains **REVISE**; no implementation freeze or held-out authorization exists. No final layout was generated or screened. See [Point-LIO verification evidence](../evidence/POINTLIO_IMPLEMENTATION_VERIFICATION_20260929.md), [FAST-LIO native evidence](../evidence/R3_NATIVE_SEED14_REPLAY_20260929.md), and the [latest R3 review](../reviews/R3_IMPLEMENTATION.md).

**Current research gate:** R1 remains **PASS for protocol design only**; this does not establish novelty or publication readiness. The original R2 protocol passed after two REVISE rounds; the Point-LIO measurement-adaptation amendment D050 has also received an independent **PASS for protocol content only**. The amended 53-file bundle now reads back **53/53 hashes matched**. The accepted amendment adds no FAST-LIO method change or sample-size change. Point-LIO's analytic fixtures, sidecar implementation, and fresh seed-14 feasibility pair are locally verified with `feasibility_pair=PASS`. Independent one-seed acceptance must be obtained before beginning the 32-pair development replication batch. Overall R3 remains **REVISE**; no implementation freeze exists, held-out work remains gated and the FAST-LIO threshold is not locked.

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
| R2 | DONE | T10-T12; D050 amendment | Original protocol and Point-LIO amendment PASS for protocol content only; current amended bundle read-back **53/53 hashes matched**; [R2 review](../reviews/R2_PROTOCOL.md), [Point-LIO review](../reviews/POINTLIO_INDICATOR_FEASIBILITY.md), [freeze](../protocol/FREEZE.md) |
| T13 | DONE | R2 PASS, T10 | [DCReg detector implementation and reproduction evidence](../evidence/INDICATOR_REPRODUCTION.md); [handoff](handoffs/T13.md). Detector adaptation only; no recovery result or threshold claim. |
| T14 | DONE | R2 PASS, T12, T13 | [Formal development batch report](../evidence/T14_DEVELOPMENT_BATCH.md), [32/32 scene screen](../evidence/randomized_layout_geometry_screen_t14_xminus6_dev14_45_v2.json), [hash audit](../evidence/t14_development_batch_manifest.json) and [handoff](handoffs/T14.md). R3 accepts seed-14 as a disclosed same-input repeat, not a new event; no recovery result or threshold claim. |
| T15 | DONE | R2 PASS, T13 | [Pinned Point-LIO smoke report](../evidence/T15_POINTLIO_SMOKE.md), [machine manifest](../evidence/t15_point_lio_smoke_manifest.json), common pose contract passed; FAST-LIO indicator parity not established; [handoff](handoffs/T15.md) |
| T16 | DONE | T14, T15 | Frozen development analysis, repeat audit, final handoff, and native seed-14 replay/cached-resume evidence are complete; [native evidence](../evidence/R3_NATIVE_SEED14_REPLAY_20260929.md) and [handoff](handoffs/T16.md). This is not a final performance result. |
| R3 | RUNNING | T13-T16 | FAST-LIO software fixes and native lifecycle accepted; overall **REVISE** remains because Point-LIO comparability and development replication readiness are not established. No implementation freeze or held-out authorization. |

## Current gate

T01-T16 are complete as scoped tasks. The T16 development analysis and native seed-14 lifecycle are accepted as development evidence, not a final performance result. T14's repeat reconciliation is accepted as a same-input repeat, not an additional event. T15 verifies one pinned Point-LIO pose-output smoke only; indicator parity is not established. The FAST-LIO threshold remains a candidate until the implementation freeze. No final-test result or publication conclusion exists. Held-out inputs/results remain untouched until R3 PASS.

## Next eligible work

**Next eligible work:** obtain independent one-seed acceptance of the
completed and verified seed-14 feasibility pair (`feasibility_pair=PASS`).
After that acceptance, execute the approved 32-pair Point-LIO development
replication batch and separate freeze. No threshold may be fitted on seed 14.
Overall R3 remains REVISE until the full readiness gate passes. Held-out work
stays blocked.
See the [current handoff](CURRENT_HANDOFF.md) and [paper completion plan](PAPER_COMPLETION_PLAN.md).
