# Current research handoff

Updated: 27 September 2026. **Start here when resuming the LiDAR recovery-reliability study.** This is a snapshot, not a completed result. The authoritative task states are in [STATUS.md](STATUS.md); the original task requirements remain in [the execution plan](../AGENT_EXECUTION_PLAN.md).

**Historical 26 September verification:** T08 is DONE: after fixing shutdown clock draining, full 55 s on/off runs yield 547 byte-identical poses and 550 audited groups (547 valid, three startup-unavailable). The remaining delivered scan lacks IMU through its end at the replay cutoff. See the [audit](../evidence/T08_FINAL_PATCH_AUDIT.md). The original real-reference T09 criterion remains blocked; the later simulation-primary T09 feasibility task is complete. At that checkpoint the suite had **42 passed, 1 skipped** (43 executed); the latest count is in the R3 repair update below. Outputs: ignored `experiments/generated/runs/T08_20260926/`.

**Current scope:** the user approved simulation-primary evidence on 26 September.
The [amendment](../SCOPE_AMENDMENT_SIMULATION.md) preserves the LiDAR recovery
question and allowed the pre-R1 T12 feasibility bootstrap. R1 now passes for
protocol design only. Seeds 10–13 test one fixed geometry; seed 14 adds one
60 s randomized straight-corridor layout/control smoke. That pair has 600
scans, 597 valid health groups/poses, 1,154/1,194 valid local windows, zero
reference gaps and byte-identical paired IMU. See the [fixed-layout report](../evidence/SIMULATION_MOTION_V3.md),
[seed sensitivity](../evidence/SIMULATION_SEED_SENSITIVITY.md),
[random-layout smoke](../evidence/SIMULATION_RANDOM_LAYOUT_SMOKE.md),
[manifests](../evidence/simulation_motion_v3_manifest.json) and
[simulation protocol](../protocol/SIMULATION.md).
The current fixed-v3 generator reproduced the seed-10 corridor/control sensor
bags and reference files byte-for-byte; the four-seed manifest preserves the
original generator hashes and records this narrower reproduction check. All
retained run/input hashes were rechecked. The randomized-layout manifest's
geometry-screen filename reference was corrected to match the checked-in file.

**R1 re-review (26 September):** PASS for protocol design only, after a fresh
GPT-6 audit of the primary papers, available official implementation material,
DCReg supplement and retained v3 outputs. This is not a novelty or publication
verdict. The [review](../reviews/R1_FEASIBILITY.md) and
[gap decision](../literature/GAP_DECISION.md) narrow the candidate to whether
online health predicts sustained reference-defined local motion after a
geometry exit, with false-healthy decisions and delay measured separately.
The first REVISE outcome remains recorded historically.

**R2 update (26 September):** two independent GPT-6 protocol audits returned
REVISE; the latest fresh review returned **PASS for protocol content**. The user
approved the full-triple-within-20-seconds rule and formal x=-6 m route. T11 is
frozen at proposal v0.4, with shared nearest-pose time boundaries and explicit
debounce, relapse and confidence-interval rules. [`FREEZE.md`](../protocol/FREEZE.md)
was re-read after editorial decision D036 with **51/51 hashes matching**.
The current freeze-file SHA-256 is
`7073114152fd3b7b248e43cbb0b016d0a330d1b0e81ede5b4cf7d907c4f90f02`.
D034–D036 refresh only the README and append-only decision-log checksum entries; the
protocol methods and splits are unchanged. The original freeze-file hash is
preserved there. R2 is PASS for protocol content only; R3 and publication
novelty are not passed.

**T13 update (27 September):** the Schur detector adaptation is implemented and
validated against the official DCReg minimal example and the FAST-LIO T08
measurement export. The 600-scan feasibility replay has 597 valid Hessian
groups and three explicit startup-unavailable groups; sidecar-on/off pose and
T08 health files are byte-identical. The complete test suite now reports 57
passed, 1 skipped. See the [reproduction report](../evidence/INDICATOR_REPRODUCTION.md)
and [T13 handoff](handoffs/T13.md). This is implementation evidence only, not a
recovery finding.

**T14 update (27 September):** the formal x=-6 m route, 32/32 scene-only screen
and development batch are complete. All 64 primary corridor/control outputs
and both seed-45 repeats are present and hash-audited. The scheduled seed-14
repeat launches hit the `/tmp` quota even after the allowed retry; the earlier
pre-batch pair has the exact same input/backend fingerprint and is disclosed
as repeat evidence, with differing control outputs preserved for R3 review.
The complete suite is 68 passed, 1 skipped. See the [T14 report](../evidence/T14_DEVELOPMENT_BATCH.md),
[machine-readable audit](../evidence/t14_development_batch_manifest.json) and
[handoff](handoffs/T14.md). Small provenance manifests and the analytic
reference are archived in `experiments/generated/t14_formal_input_provenance_v1`.
Eleven sensor bags are retained under `experiments/generated/t14_retained_inputs`;
the other 53 are session-local under `/tmp` and `/run/user`.

**T15 update (27 September):** Point-LIO commit
`4b86a469eb5572e70ed575af25b5f15dd06e8e3c` built with reversible compatibility
patches and completed a smoke on the exact seed-14 corridor bag. The final
replay produced 597 valid, monotonic 10 Hz poses; an identical second replay
produced byte-identical pose output. The common evaluator accepted the output
and reported 1,154 valid local-motion rows with no reference gaps. One initial
setup attempt failed because the configuration was loaded outside Point-LIO's
private ROS namespace; its GDB trace is retained and the runner now validates
configuration/startup/output. Point-LIO health-indicator parity with FAST-LIO
is **not established**. See the [T15 report](../evidence/T15_POINTLIO_SMOKE.md),
[machine manifest](../evidence/t15_point_lio_smoke_manifest.json) and
[handoff](handoffs/T15.md). The build workspace remains session-local under
`/run/user/1000`; the Acer partition is read-only.

**T16 update (27 September):** all 64 completed T14 primary outputs were
re-hash-verified and analyzed using the frozen 1-second triple rule. All 32
corridor events were truth-label-eligible and recovered; one later relapsed.
The development-only FAST-LIO candidate threshold is `166.16366016039856`
(13/32 recovery detections, 1/31 conditional false-healthy events). The
fixed-rule DCReg comparator detected 29/32 and had 0/31 initial false-healthy
events, but remained healthy after the one relapse. The interior variance
rule gives `n_test=48` geometry pairs, 12 per stratum. Because the FAST-LIO
threshold was selected on these same events, these are not final performance
estimates. The [T16 report](../evidence/DEVELOPMENT_REPORT.md), [analysis
manifest](../evidence/t16_development_analysis_manifest.json), [no-data final
plan](../evidence/FINAL_HELDOUT_PLAN.json) and [handoff](handoffs/T16.md)
preserve exact values and hashes. Final screen/run commands are implemented
but gated on R3 PASS and were not executed.

**R3 first review (27 September): REVISE.** The independent audit verified the
development provenance and results but found repairs needed before a freeze:
the final runner's success path, complete-stream checks, reviewed-hash/screen
lineage, threshold-sweep reset parity, 3-second missing-window accounting,
resumable failure ledger, and quantitative repeatability. Exact IDs and
counterexamples are in [R3_IMPLEMENTATION.md](../reviews/R3_IMPLEMENTATION.md).
It did not create `IMPLEMENTATION_FREEZE.md`, and no held-out data were
generated or screened.

**R3 repair update (27 September):** the full repair package is now prepared
for independent re-review. The [verification report](../evidence/R3_REPAIR_VERIFICATION.md)
maps every repair ID to its source, fixtures and real development checks.
The analyzer rerun reproduces the threshold and sample size; the
[repeat audit](../evidence/T14_REPEATABILITY_AUDIT.md) quantifies all four
retained repeats. The source and executable were rebuilt identically to T14;
a current-source development replay passed the real completion validator.
Both environments now run **119 tests: 118 passed, one optional SciPy skip**.
Saved plots include PNG/PDF/SVG and a figure hash manifest. The initial R3
review remains REVISE until independently audited again.

**Current next step:** obtain focused R3 re-review. For the user's full paper
objective, develop and freeze comparable Point-LIO indicators before any
final-layout exposure; a pose-only smoke does not satisfy replication.
The [paper completion plan](PAPER_COMPLETION_PLAN.md) preserves the broader
objective through final evaluation, replication, novelty audit, analysis and
manuscript verification. No actual held-out geometry has been generated or
screened. The final-evaluation handoff supplies the primary commands and
resource estimates; they remain gated.

**Historical real-data checkpoint:** T07 closed software acceptance, but Hilti
has only 13/56 valid matched post-exit 1 s windows and 0/56 3 s windows.
Its map-derived reference is not independent; it remains a supporting
illustration. T08 is now complete, superseding the interrupted-run notes.
No real-data recovery result or final-test evaluation exists.

The earlier frame, range and evaluator checks remain in the linked artifacts and [append-only decisions](DECISIONS.md). The frame choice is supported by 503 raw-gyroscope/reference turning intervals, not by fitted estimator errors. That validates a development comparison convention, **not** independent reference accuracy.

## What the study is trying to learn

After a LiDAR system passes through a scene with weak geometric clues, can its existing health signals tell when its *short-term motion estimate* has become reliable again? Local recovery and previously accumulated position drift are different. See the [research goal](../RESEARCH_GOAL.md) and [scope decision](../SCOPE_DECISION.md). This is offline research with public LiDAR/IMU data, not a drone flight or safe-landing test.

## Actual progress

| Item | Current state | Evidence |
| --- | --- | --- |
| Literature, data inventory, contracts, first recording and backend reproduction (T01–T06) | Done as execution tasks | [Status ledger](STATUS.md) and its linked handoffs |
| GEODE Urban_Tunnel01 | Retained development failure: two FAST-LIO runs produced unusable motion estimates; reference body is not verified | [T06](handoffs/T06.md), [T07](handoffs/T07.md) |
| Offline trajectory evaluator (T07) | **DONE as software/evaluation task:** development Exp18 error stream retains valid/unavailable reasons; Hilti recovery evidence remains inadequate. | [T07 handoff](handoffs/T07.md), [pilot](../evidence/HILTI_EXP18_T07_PILOT.md) |
| Hilti-Oxford Exp18 replacement candidate | Publisher-hash-verified recording inspected; all 1,094 Hesai clouds pass adapter checks; first 55-second replay produced 546 valid poses | [Inspection](../data/HILTI_EXP18_INSPECTION.md), [replay](../data/HILTI_EXP18_REPLAY.md) |
| Hilti Exp18 frame convention | Development common-body interpretation strongly supported by 503 raw-gyroscope/reference turning intervals; no FAST-LIO error used | [Frame audit](../data/HILTI_EXP18_FRAME_AUDIT.md) |
| Indicator comparison, transition pilot, protocol and comparator implementation | T08–T13 completed as engineering/evidence tasks; R1 PASS for design, R2 PASS for protocol content. R3/final evaluation remain. | [T13 reproduction](../evidence/INDICATOR_REPRODUCTION.md), [R1](../reviews/R1_FEASIBILITY.md), [R2](../reviews/R2_PROTOCOL.md), [freeze](../protocol/FREEZE.md) |
| Formal simulation implementation | T14 DONE as development execution; 64 primaries, seed-45 repeats and transparent seed-14 smoke-repeat reconciliation. R3 must adjudicate the deviation. | [T14 batch report](../evidence/T14_DEVELOPMENT_BATCH.md), [audit manifest](../evidence/t14_development_batch_manifest.json), [handoff](handoffs/T14.md) |
| Point-LIO backend smoke | T15 DONE for a pinned, repeated pose-output smoke; no FAST-LIO indicator parity or replication result. | [T15 report](../evidence/T15_POINTLIO_SMOKE.md), [machine manifest](../evidence/t15_point_lio_smoke_manifest.json), [handoff](handoffs/T15.md) |
| Frozen development-label/threshold analysis | Analysis and repairs prepared; T16 remains RUNNING pending independent R3 acceptance. Candidate threshold and `n_test=48` reproduce; no held-out geometry/results. | [Development report](../evidence/DEVELOPMENT_REPORT.md), [repair checks](../evidence/R3_REPAIR_VERIFICATION.md), [handoff](handoffs/T16.md) |

The Hilti replay is a software/development illustration, not an independent
recovery benchmark. The backend's actual online diagnostic has been measured
separately from the scene-only annotation proxy. Formal simulation now has
development-only recovery labels and a candidate FAST-LIO threshold; no final
test result exists and the threshold is not locked until R3.

## Data and boundaries

The Exp18 bag lives outside Git on the Acer Windows partition:

`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag`

It is 8,657,654,860 bytes; SHA-256 `98373b52f207b9ace3914792b5604a6642f89441190cabca6acbaf1d17249280`. The published reference and calibration are in the same directory. The exploratory run is under `runs/exp18_first55_exploratory/` there. Check that the partition is mounted before using these paths. Do not put the bag, raw outputs, or build environment into Git. The dataset is a **handheld** recording. Its dense reference has gaps, ends before the recording ends, and was produced partly by registering the mobile LiDAR to a surveyed map; it is not an independent physical tracking measurement. Cameras in the bag were not estimator inputs.

## Next bounded work, in order

1. T09 amended v3 and the simulator fixes are complete as feasibility work.
   v1/v2 attempts remain preserved; v3 raw inputs/results are under ignored
   `experiments/generated/` and are not committed.
2. R2 content/file-hash freeze, T14 execution, T15 Point-LIO smoke and T16
   development analysis are complete. T14's repeat reconciliation, Point-LIO
   indicator limit and verified T16-R3 repairs are explicit. Obtain a focused
   independent re-review, then complete the replication development freeze
   required by the full-paper plan. Do not generate or inspect
   held-out inputs/results before R3 PASS. The literature basis is in
   [RECOVERY_OVERLAP_UPDATE.md](../literature/RECOVERY_OVERLAP_UPDATE.md).

The [README](../../README.md) explains this in everyday language and shows the two data pictures. Historical GEODE notes and handoffs remain evidence of what was tried, not instructions to redo it by default. Preserve the `old_data/` archive and its held-out-seed rules; its synthetic safe-landing results are not evidence for this new paper.
