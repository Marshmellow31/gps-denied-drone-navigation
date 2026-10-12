# Final revised geometry evaluation — 12 October 2026

**Evaluation status: complete under the accepted revised protocol. Publication novelty and manuscript completion remain outstanding.**

Both frozen analyses returned `CONFIRMATORY_COMPLETE`: 48 geometry pairs per backend, 96 native scene runs each, 192 in total. All 48 paired corridor/control sensor-bag identities agree across backends. No native replay failed and no native retry/repeat was selected. Two workflow failures are retained separately: Point-LIO preflight stopped before any native attempt because its scratch root was absent; the original FAST analyzer rejected an extra shared Point threshold in its expected primary identity before loading final reference/poses/labels. The former required creating the directory; the latter required the independently accepted metadata-only adapter. Original frozen scientific sources and all 197 bound hashes remain unchanged.

## Design and provenance

The geometry screen selected 12 pairs in each of four frozen length/width groups from 64 checked candidates, using geometry criteria only, before estimator execution. Its hash is `f088c5cbe539da1624b638148662362ecab6a74a1de861094664df097a99b886`. IDs 100–179 from the failed earlier screen were excluded. The revised control spacing and larger pools were informed by that failed geometry screen; these fresh instances must not be described as a wholly unadapted test design. No final accuracy, indicator or recovery result selected a geometry or changed an operating point.

FAST-LIO's scalar cutoff remains `166.16366016039856`; Point-LIO's remains `123.80876977779258`. Fixed DCReg adaptations remain unchanged. Reference-defined recovery requires three consecutive non-overlapping one-second movement windows within 0.20 m translation error and 5 degrees rotation error, fully confirmed within 20 s of the predefined exit. Reference labels are offline, backend-specific, and separate from causal diagnostic decisions.

Sources: [FAST analysis](fastlio_analysis.json), [Point analysis](pointlio_analysis.json), [export audit](export_audit.json), [every native attempt receipt](native_attempt_receipts.json), [R3 review](../../reviews/R3_GEOMETRY_V2_IMPLEMENTATION_20261012.md), [original new freeze](../../protocol/IMPLEMENTATION_FREEZE_GEOMETRY_V2_20261012.md), [supplemental compatibility review](../../reviews/R3_GEOMETRY_V2_ANALYSIS_COMPATIBILITY_20261012.md). Raw bags, diagnostics, poses, evaluations and logs remain at the external paths recorded in these manifests.

## Locked diagnostic operating points

| Backend / diagnostic | Initial false-healthy conditional; Wilson 95% | Initial false-healthy unconditional | Recovery detections; Wilson 95% | Median delay, detected only | Available/planned horizon ticks |
| --- | --- | --- | --- | --- | --- |
| FAST-LIO / Minimum eigenvalue | 1/46 (2.2%); 0.4–11.3% | 1/48 (2.1%) | 14/46 (30.4%); 19.1–44.8% | 0.850 s | 9600/9600 |
| FAST-LIO / Fixed DCReg adaptation | 4/46 (8.7%); 3.4–20.3% | 4/48 (8.3%) | 38/46 (82.6%); 69.3–90.9% | 6.800 s | 9600/9600 |
| Point-LIO / Minimum eigenvalue | 4/47 (8.5%); 3.4–19.9% | 4/48 (8.3%) | 27/32 (84.4%); 68.2–93.1% | 3.400 s | 9600/9600 |
| Point-LIO / Fixed DCReg adaptation | 16/47 (34.0%); 22.2–48.3% | 16/48 (33.3%) | 25/32 (78.1%); 61.2–89.0% | 3.000 s | 9600/9600 |

The conditional false-healthy denominator counts initial unrecovered intervals with at least one available diagnostic decision tick. The unconditional denominator includes all 48 non-empty initial intervals. Having 100% availability across the overall 20 s horizon does not guarantee a tick exists inside an extremely short initial interval. Recovery-detection denominators are 46 FAST-LIO and 32 Point-LIO truth-recovered events, rather than all 48 planned corridors. These are different own-pose labels; diagnostic sensitivities are not a direct estimator leaderboard.

FAST-LIO scalar missed 32 of 46 recoveries; its fixed DCReg adaptation missed 8. Point-LIO scalar missed 5 of 32; its fixed DCReg adaptation missed 7. Delay medians condition on detection: misses have no observed delay, and non-recoveries remain right-censored at the20 s deadline. No synthetic zero/infinite delay was assigned to them. Short median delay does not establish better overall responsiveness.

The scalar conditional false-healthy point estimates are below the development selection ceiling of 10%, but their 95% upper bounds are11.3% (FAST) and19.9% (Point). This dataset therefore does not establish a population false-healthy guarantee below 10%. Point-LIO's fixed DCReg adaptation has 16/47 initial false-healthy events, 34.0%, indicating limited transfer at that fixed rule.

## Recovery, non-recovery and geometry dependence

FAST-LIO truth recovery: 46/48 (95.8%; Wilson 95% 86.0–98.8%), two non-recoveries. Point-LIO: 32/48 (66.7%; 52.5–78.3%), 16 non-recoveries. Every corridor has usable truth; no corridor was discarded from these denominators.

| Backend | Geometry group | Recovered / planned | Non-recovered | Relapse events |
| --- | --- | --- | --- | --- |
| FAST-LIO | short / narrow | 12/12 | 0 | 0 |
| FAST-LIO | short / wide | 10/12 | 2 | 0 |
| FAST-LIO | long / narrow | 12/12 | 0 | 0 |
| FAST-LIO | long / wide | 12/12 | 0 | 1 |
| Point-LIO | short / narrow | 12/12 | 0 | 0 |
| Point-LIO | short / wide | 4/12 | 8 | 1 |
| Point-LIO | long / narrow | 12/12 | 0 | 0 |
| Point-LIO | long / wide | 4/12 | 8 | 0 |

Both backends have one relapse. Neither FAST diagnostic produced a post-relapse false-healthy event (0/1). Point-LIO scalar is 0/1; fixed DCReg is 1/1. These secondary endpoints have only one relapsed event per backend: the zero-event Wilson upper bound is 79.3%, so they do not establish robust relapse reliability.

Point-LIO recovered in all 24 narrow corridors but only 8/24 wide corridors. Its scalar's four initial false-healthy events all occur in long/narrow (4/12); the aggregate 8.5% conditional rate hides this group dependence. FAST scalar detects only 1/12 long/wide recoveries. These are observed interactions under this screened simulation design; each group has only 12 independent geometries. Group Wilson intervals and complete per-event rows are retained in the analysis JSON/CSV.

## Paired interior movement error and uncertainty

For each geometry, the frozen analysis subtracts the control's median interior one-second translation error from the corridor's median error. It averages these paired differences with equal group weights. Positive values mean higher corridor error.

| Backend | Mean corridor minus control | Geometry bootstrap 95% |
| --- | --- | --- |
| FAST-LIO | 0.194 m | [0.086, 0.311] m |
| Point-LIO | 0.149 m | [0.068, 0.230] m |

The frozen bootstrap resamples paired geometry seeds within the four fixed groups, 10000 times, PCG64 seed 20260926. All48 pairs are used. Both aggregate intervals exclude zero. Group means vary: Point-LIO short/narrow is−0.087 m, while short/wide is+0.374 m. The aggregate cannot establish uniform benefit from control features in every group; within-group means plotted alone have no displayed confidence interval. The two backend aggregate intervals do not constitute a predeclared between-estimator superiority test.

Event-weighted threshold-free ROC/AP and their geometry bootstrap intervals are included in the full JSON. They describe score discrimination and must not substitute for performance at the fixed operating points. No threshold was chosen from final ROC/AP curves. Half/double tolerance and three-second-window sensitivity analyses are retained separately in those exports; they do not replace the primary endpoints.

## Visual evidence and reproduction

The [README](../../README.md) embeds and explains every retained research illustration, including the final operating points, group estimates, full 48-event ledger for each backend, and paired geometry effect. [Figure manifest](../../figures/final_geometry_v2_results_20261012/manifest.json) binds source exports, plotter and PNG hashes. [CSV summaries](method_summary.csv), [group summaries](stratum_summary.csv) and [complete diagnostic event rows](corridor_event_ledger.csv) retain numerical values. Four diagnostic rows per geometry in the last CSV are repeated analyses of shared geometry/own-backend labels; they are not 192 independent geometries.

On the current host, run the accepted primary adapter with the supplemental compatibility review and unchanged original review/freeze; run the unchanged Point analysis separately. Exact executed commands, exits and source identities are retained in [resumed driver state](analysis_resume_state.json). The original failed driver [state](pipeline_state.json) and failed Point [batch](pointlio_preflight_failed_batch.json) remain visible. Initialize scratch directories before native execution. Reuse validated native outputs for offline reanalysis; do not rerun or resample final scenes to improve results.

The compact export and plots can be reproduced from their scripts with a fresh output directory. A Git clone contains small evidence/figures and native patches, but does not include the external native environments, binaries, sensor bags or raw streams. Full native reproduction needs the recorded versions/configuration, source/binary hashes and external artifact paths.

## Verification, completion and novelty

The unchanged 197-entry freeze passed after integration and supplementation. Five focused adapter tests passed independently. Full current regression: 249 tests, 248 passed, one optional SciPy skip; compiled native reset fixture enabled. Unit/contract/native feasibility checks support implementation validity; the separate complete final cohort supplies the experimental findings reported here.

The planned controlled two-backend evaluation is complete. The evidence supports geometry-dependent transfer trade-offs and a positive aggregate paired interior error effect under the revised screened simulation design. It does not prove a novel detector, universal reliability, real-world recovery, physical flight safety or estimator superiority.

[OCE](https://link.springer.com/article/10.1007/s43684-026-00144-1) already evaluates ground-truth short-window motion usability and recovery hysteresis/delay. The narrower candidate contribution here is the frozen transfer assessment across randomized length/width groups with independently instrumented FAST-LIO and Point-LIO, complete event/failure accounting and geometry uncertainty. Publication novelty requires a precise comparison and a finished reviewed manuscript. The current main manuscript remains a proposal abstract. Hilti Exp18 remains development-only with insufficient sustained independent reference; GEODE failures remain retained. The earlier screening digest discrepancy is unresolved and is not repaired by this fresh cohort.
