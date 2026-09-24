# Current research handoff

Updated: 24 September 2026. **Start here when resuming the LiDAR recovery-reliability study.** This is a snapshot, not a completed result. The authoritative task states are in [STATUS.md](STATUS.md); the original task requirements remain in the [execution plan](../AGENT_EXECUTION_PLAN.md).

**Latest checkpoint:** T07's offline evaluator produced a complete **development-only** Exp18 error stream with valid/unavailable counts. The scene-defined exit was fixed using LiDAR-only structure before errors were summarized. This closes T07's software/evaluation acceptance, but **does not establish recovery**: matched post-exit reference supports only 13/56 one-second windows and 0/56 three-second windows. Exp18's map-registration-derived reference is also not independent. T08's [optional backend diagnostic](../protocol/FASTLIO_INFORMATION_DIAGNOSTIC.md) compiled and passed preliminary replay/pose-parity checks, but the final-patch full replay was interrupted and T08 remains RUNNING. The full experiment suite passes 28 tests. See the [T07 pilot](../evidence/HILTI_EXP18_T07_PILOT.md), [event audit](../data/HILTI_EXP18_EVENT.md), and [alternative reference screen](../data/ALTERNATIVE_REFERENCE_AUDIT.md). T09 and R1 remain open; no final test was run.

The earlier frame, range and evaluator checks remain in the linked artifacts and [append-only decisions](DECISIONS.md). The frame choice is supported by 503 raw-gyroscope/reference turning intervals, not by fitted estimator errors. That validates a development comparison convention, **not** independent reference accuracy.

## What the study is trying to learn

After a LiDAR system passes through a scene with weak geometric clues, can its existing health signals tell when its *short-term motion estimate* has become reliable again? Local recovery and previously accumulated position drift are different. See the [research goal](../RESEARCH_GOAL.md) and [scope decision](../SCOPE_DECISION.md). This is offline research with public LiDAR/IMU data, not a drone flight or safe-landing test.

## Actual progress

| Item | Current state | Evidence |
| --- | --- | --- |
| Literature, data inventory, contracts, first recording and backend reproduction (T01–T06) | Done as execution tasks | [Status ledger](STATUS.md) and its linked handoffs |
| GEODE Urban_Tunnel01 | Retained development failure: two FAST-LIO runs produced unusable motion estimates; reference body is not verified | [T06](handoffs/T06.md), [T07](handoffs/T07.md) |
| Offline trajectory evaluator (T07) | **DONE as software/evaluation task:** closed with 24 tests, now 28 in the full suite; development Exp18 error stream retains valid/unavailable reasons. Scientific recovery evidence remains inadequate. | [T07 handoff](handoffs/T07.md), [pilot](../evidence/HILTI_EXP18_T07_PILOT.md) |
| Hilti-Oxford Exp18 replacement candidate | Publisher-hash-verified recording inspected; all 1,094 Hesai clouds pass adapter checks; first 55-second replay produced 546 valid poses | [Inspection](../data/HILTI_EXP18_INSPECTION.md), [replay](../data/HILTI_EXP18_REPLAY.md) |
| Hilti Exp18 frame convention | Development common-body interpretation strongly supported by 503 raw-gyroscope/reference turning intervals; no FAST-LIO error used | [Frame audit](../data/HILTI_EXP18_FRAME_AUDIT.md) |
| Indicator comparison, transition figure and first scientific review (T08, T09, R1) | T08 is **RUNNING** with a compiled optional exporter and preliminary parity only; T09/R1 not complete. R1 cannot pass from Hilti-only evidence. | [T08 source audit](../protocol/FASTLIO_INFORMATION_DIAGNOSTIC.md), [status ledger](STATUS.md) |

The Hilti replay is a useful **software/development pilot**, not an independent localization benchmark or recovery result. Its scene-defined 31.6–33.6 s exit-only interval is supported by a single-scan structural proxy, not by the backend's actual scan-to-map Hessian. The 1 s valid-row errors cannot be promoted to sustained recovery when most matched post-exit rows and every 3 s row are unavailable. No online indicator was measured, no recovery label was assigned, no final-test trajectory was evaluated, and no recovery threshold has been frozen.

## Data and boundaries

The Exp18 bag lives outside Git on the Acer Windows partition:

`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag`

It is 8,657,654,860 bytes; SHA-256 `98373b52f207b9ace3914792b5604a6642f89441190cabca6acbaf1d17249280`. The published reference and calibration are in the same directory. The exploratory run is under `runs/exp18_first55_exploratory/` there. Check that the partition is mounted before using these paths. Do not put the bag, raw outputs, or build environment into Git. The dataset is a **handheld** recording. Its dense reference has gaps, ends before the recording ends, and was produced partly by registering the mobile LiDAR to a surveyed map; it is not an independent physical tracking measurement. Cameras in the bag were not estimator inputs.

## Next bounded work, in order

1. **Finish T08's final audit.** The [derivation, patch and preliminary checks](../protocol/FASTLIO_INFORMATION_DIAGNOSTIC.md) cover the pinned FAST-LIO `h_share_model`'s first six translation/rotation Jacobian columns. Replay the final patch for 55 s, validate initialization/unavailable rows, export-on/off pose parity and provenance. The previous final-patch replay was interrupted at the user's request; do not use its partial output. The existing single-scan structural proxy is **not** this online indicator. Do not use reference/error data as an online input.
2. **Seek usable independent reference before another large download.** Start from the [screen](../data/ALTERNATIVE_REFERENCE_AUDIT.md). Inspect small released reference files, timestamp coverage, orientation provenance, LiDAR/IMU topics and calibration. Reject position-only reference and long uncovered exits. A new bag needs a justified eligible transition, published size and storage check first.
3. **T09 only with honest evidence.** A Hilti timeline can show the scene exit, backend indicator and explicit error gaps, but cannot claim sustained 1 s/3 s recovery. Its report must retain the 13/56 and 0/56 post-exit denominators and map-registration limitation. A qualifying recovery plot needs a better-covered independent reference or a formally narrowed simulation outcome.
4. **R1 is a real go/no-go gate.** Audit overlap and actual pilot quality. If no qualifying real transition exists, record `REVISE` with a simulation-primary scope amendment, not a fictional PASS of the original real-data requirement. No final-test exposure or paper conclusion before the gates.

The [README](../../README.md) explains this in everyday language and shows the two data pictures. Historical GEODE notes and handoffs remain evidence of what was tried, not instructions to redo it by default. Preserve the `old_data/` archive and its held-out-seed rules; its synthetic safe-landing results are not evidence for this new paper.
