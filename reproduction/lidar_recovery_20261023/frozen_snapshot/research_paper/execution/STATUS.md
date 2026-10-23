# LiDAR recovery-reliability execution status

Updated: 10 October 2026. Status values are `TODO`, `RUNNING`, `BLOCKED`, and `DONE`. A task is `DONE` only when its acceptance checks and handoff are complete. Review gates must audit the underlying artifacts rather than this ledger.

**10 October R3 interface update:** The corrected FAST-LIO primary and
same-pair Point-LIO final replication runners/analyses are assembled. The
no-data plan rebuilds from corrected development evidence and the frozen
split; the current exact inventory has 151 entries. The full suite ran 231
tests: 229 passed, two optional fixtures skipped in frozen Python 3.12.14 /
NumPy 2.5.3. A follow-up readiness audit passed with the rebuilt plan and
151-item inventory rebuilt; the independent R3 freeze review is pending. No
implementation freeze, R3 PASS, held-out
screen or final input exists. See [R3 readiness handoff](handoffs/R3_READINESS_20261010.md).

**10 October novelty update:** The OCE paper published on 9 October already
evaluates ground-truth local-motion usability and recovery delay. Independent
review passed feasibility only for the narrower untouched corridor-strata
transfer and two-backend replication question. This is not a publication-
novelty result; the outcome-dependent audit remains due. See the [OCE review](../reviews/OCE_NOVELTY_FEASIBILITY_20261010.md)
and [literature addendum](../literature/RECOVERY_OVERLAP_ADDENDUM_20261010.md).

**Active complete-paper continuation:** Fresh primary recovery is complete for
64 FAST-LIO primary slots and four declared repeats; all 69 native attempts
remain recorded, including one interruption and its technical retry. The
Point-LIO development cohort has all 64 formal slots complete and its corrected
analysis passed independent review. A frozen-rule audit corrected candidate
enumeration for both backends; thresholds and event metrics are unchanged.
FAST-LIO is `166.16366016039856` (13/32 detections, 1/31 false-healthy events);
Point-LIO is `123.80876977779258` (21/27 detections, 3/32 false-healthy
events). FAST-LIO DCReg detects 30/32 and Point-LIO DCReg 20/27 on their own
pose-derived labels. The primary final target remains 48 geometry pairs.
The separate Point-LIO freeze passed independent review. The full suite ran
210 tests: 209 passed, one optional scene audit skipped. See
[10 October continuation](handoffs/DEVELOPMENT_CONTINUATION_20261010.md) and
[corrected analysis evidence](../evidence/DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md).
The complete-paper goal remains open; R3 is REVISE and held-out work is sealed.

**Historical 9 October restoration checkpoint:** The missing tracked checkout was restored
at `5583b9edbb57a6deefd1f1b00f2927aea4e924b9`, preserving existing ignored files.
The original R2 protocol bundle reads back **53/53 hashes matched**. Independent
[Point-LIO one-seed acceptance](../reviews/POINTLIO_ONE_SEED_ACCEPTANCE_20261009.md)
now **PASSES** for the preserved R2 feasibility pair. All 64 development inputs
were regenerated in a new Acer folder: **192/192 recording/reference/metadata
hashes match** their saved scientific identities; all 32 paired-IMU/coverage
audits pass. New generator manifests are new provenance, not restored historical
runtime manifests. See [input restoration](../evidence/development_input_restoration_20261009.json).

**At that checkpoint, primary reproducibility was still blocked:** Of the 320 historical T14 primary
run-manifest/key-stream artifacts checked, 67 match and 253 are missing;
no primary run has its complete checked artifact set. The moved Acer binaries
gave stable but materially different trajectories in two new repeats. Rebuilding
at the exact historical path recovered the original executable **byte-for-byte**.
A fourth attempt reproduces preserved native R3 poses/health/Hessian/DCReg
**byte-for-byte**; evaluated fields agree except for new run/event IDs. All
attempts are preserved. The precise cause of moved-build differences is not
established. See [build recovery](../evidence/fastlio_historical_build_restoration_20261009.json)
and [native reproduction](../evidence/fastlio_historical_binary_replay_20261009.json).
This closes the bounded native restoration problem; missing full primary
outputs still require fresh recovery with explicit new provenance. Backend
preflight now uses a hash-bound compact build/source identity extracted from a
verified surviving seed-31 manifest when the old seed-14 manifest is absent.
It supplies no scientific results and is included in the R3 freeze inventory.
The full isolated suite executes **167 tests: 166 pass, one optional scene test
skips, no failures**.
The separate focused Point-LIO suite passes all 40 tests including its native
reset fixture. Overall R3 remains **REVISE**; no implementation freeze or
held-out access is authorized. Historical DONE rows below describe past scoped
acceptance, not current completeness of the missing local evidence.

**Latest checks (29 September):** The T16 development threshold, 32/32 recovery count, one relapse and 48-pair planning target still reproduce. The [four-repeat audit](../evidence/T14_REPEATABILITY_AUDIT.md) quantifies score, error, warning and label variation. FAST-LIO R3 software/provenance repairs and its native lifecycle were independently accepted. Point-LIO's bounded implementation workflow also received PASS, and the full suite ran 165 tests: 163 passed, two optional SciPy checks skipped, including a compiled native reset fixture and runner helper tests. The startup failure from the first sidecar-on attempt was diagnosed (prior-boot kernel ntfs3 iomap BUG); runner process cleanup was upgraded and tested. Both initial runs are preserved as development evidence. The fresh R2 sidecar-on/off feasibility replay completed cleanly on Acer: poses are byte-identical (`851e8b3709e26e2c1bc607d8d6507e1c303746129e8d2bd19c761f8efce727ee`), full raw frame coverage is verified (600/600 frames, 181,903 groups, 222,498 Jacobian rows), 3 startup frames are unavailable (matching FAST-LIO), and `verify_pointlio_feasibility_pair.py` returned PASS. No threshold was fitted on seed 14 and no held-out data were accessed. Overall R3 remains **REVISE**; no implementation freeze or held-out authorization exists. No final layout was generated or screened. See [Point-LIO verification evidence](../evidence/POINTLIO_IMPLEMENTATION_VERIFICATION_20260929.md), [FAST-LIO native evidence](../evidence/R3_NATIVE_SEED14_REPLAY_20260929.md), and the [latest R3 review](../reviews/R3_IMPLEMENTATION.md).

**Current research gate:** R1 remains **PASS for protocol design only**; this does not establish novelty or publication readiness. The original R2 protocol passed after two REVISE rounds; the Point-LIO measurement-adaptation amendment D050 has also received an independent **PASS for protocol content only**. The amended 53-file bundle now reads back **53/53 hashes matched**. The accepted amendment adds no FAST-LIO method change or sample-size change. Point-LIO's analytic fixtures, sidecar implementation, and fresh seed-14 feasibility pair are locally verified with `feasibility_pair=PASS`. Independent one-seed acceptance passed on 9 October; its review is linked in the current restoration checkpoint. The 32-pair development replication batch remains unfinished. Overall R3 remains **REVISE**; no implementation freeze exists, held-out work remains gated and the FAST-LIO threshold is not locked.

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
| T14 | DONE | R2 PASS, T12, T13 | Historical T14 is recorded in the [T14 report](../evidence/T14_DEVELOPMENT_BATCH.md). Fresh primary recovery and repeat evidence is in [recovery evidence](../evidence/PRIMARY_DEVELOPMENT_RECOVERY_20261009.md); it remains development-only. |
| T15 | DONE | R2 PASS, T13 | [Pinned Point-LIO smoke report](../evidence/T15_POINTLIO_SMOKE.md), [machine manifest](../evidence/t15_point_lio_smoke_manifest.json), common pose contract passed; FAST-LIO indicator parity not established; [handoff](handoffs/T15.md) |
| T16 | DONE | T14, T15 | Original scoped T16 and seed-14 lifecycle are complete. Corrected FAST-LIO and Point-LIO development analysis is independently accepted; see [10 October analysis evidence](../evidence/DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md) and [Point-LIO review](../reviews/POINTLIO_DEVELOPMENT_ACCEPTANCE_20261010.md). No final performance result follows. |
| R3 | RUNNING | T13-T16 | Point-LIO replication, corrected threshold selection and its separate freeze are independently accepted as development evidence. Overall **REVISE** remains until the final runner/analysis interfaces and exact implementation inventory are accepted together. No held-out authorization. |

## Current gate

The FAST-LIO primary recovery and Point-LIO 32-pair development replication
are complete and independently reviewed. The corrected threshold sweep uses
every finite valid raw corridor score for both backends; both operating
thresholds and event outcomes match the earlier decision-grid sweep. The
Point-LIO development freeze is independently accepted. Overall R3 remains
**REVISE** until the corrected development evidence, final execution/analysis
interfaces and exact implementation inventory are accepted together. No
held-out geometry, screen or result has been generated or opened.

## Next eligible work

**Next eligible work:** finish the corrected final-evaluation and analysis interfaces and submit the
full package for R3 review. Preserve the historical native-producer snapshot
when updating code. Only after R3 PASS may the frozen 48-pair final screen and
paired estimator runs begin. See the
[10 October continuation](handoffs/DEVELOPMENT_CONTINUATION_20261010.md),
[current handoff](CURRENT_HANDOFF.md), and
[paper completion plan](PAPER_COMPLETION_PLAN.md).
