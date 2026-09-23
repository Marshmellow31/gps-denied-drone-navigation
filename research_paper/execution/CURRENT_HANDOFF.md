# Current research handoff

Updated: 23 September 2026. **Start here when resuming the LiDAR recovery-reliability study.** This is a snapshot, not a completed result. The authoritative task states are in [STATUS.md](STATUS.md); the original task requirements remain in the [execution plan](../AGENT_EXECUTION_PLAN.md).

## What the study is trying to learn

After a LiDAR system passes through a scene with weak geometric clues, can its existing health signals tell when its *short-term motion estimate* has become reliable again? Local recovery and previously accumulated position drift are different. See the [research goal](../RESEARCH_GOAL.md) and [scope decision](../SCOPE_DECISION.md). This is offline research with public LiDAR/IMU data, not a drone flight or safe-landing test.

## Actual progress

| Item | State on 23 September | Evidence |
| --- | --- | --- |
| Literature, data inventory, contracts, first recording and backend reproduction (T01–T06) | Done as execution tasks | [Status ledger](STATUS.md) and its linked handoffs |
| GEODE Urban_Tunnel01 | Retained development failure: two FAST-LIO runs produced unusable motion estimates; reference body is not verified | [T06](handoffs/T06.md), [T07](handoffs/T07.md) |
| Offline trajectory evaluator (T07) | Eight fixtures pass; formal GEODE errors remain unavailable, so task is **BLOCKED** | [T07 handoff](handoffs/T07.md) |
| Hilti-Oxford Exp18 replacement candidate | Publisher-hash-verified recording inspected; all 1,094 Hesai clouds pass adapter checks; first 55-second replay produced 546 valid poses | [Inspection](../data/HILTI_EXP18_INSPECTION.md), [replay](../data/HILTI_EXP18_REPLAY.md) |
| Indicator comparison, transition figure and first scientific review (T08, T09, R1) | Not complete | [Status ledger](STATUS.md) |

The Hilti replay is an encouraging **software smoke test**, not a measured localization error or recovery result. Its three displacement-length checks do not test turns or path accuracy. The possible scene change at 32–36 seconds is tentative. No indicator was measured, no recovery label was assigned, no final-test trajectory was evaluated, and no recovery threshold has been frozen.

## Data and boundaries

The Exp18 bag lives outside Git on the Acer Windows partition:

`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag`

It is 8,657,654,860 bytes; SHA-256 `98373b52f207b9ace3914792b5604a6642f89441190cabca6acbaf1d17249280`. The published reference and calibration are in the same directory. The exploratory run is under `runs/exp18_first55_exploratory/` there. Check that the partition is mounted before using these paths. Do not put the bag, raw outputs, or build environment into Git. The dataset is a **handheld** recording. Its dense reference has gaps, ends before the recording ends, and was produced partly by registering the mobile LiDAR to a surveyed map; it is not an independent physical tracking measurement. Cameras in the bag were not estimator inputs.

## Next bounded work, in order

1. **Verify reference and frames from publisher evidence.** Establish the released reference's quaternion column order and pose direction; establish whether its IMU body is the same physical frame as FAST-LIO `body`, ROS `imu_sensor_frame`, and calibration `imu`. Record an explicit, sourced transform and clock/coverage metadata. If any convention remains unproved, keep 6-DoF errors unavailable; do not guess an identity transform. The recorded IMU orientation field is zero and is not attitude truth.
2. **Repair T07 for this development stream.** Its current command path assumes the GEODE event; make sequence/event selection explicit. Implement the [contract's](../protocol/DATA_CONTRACT.md) partition-before-sort reference-gap rule, original row numbers, and reset-marker handling, with focused tests. Do not calculate event-anchored errors or use the held-out/final-test data yet.
3. **Audit and freeze the transition without outcome peeking.** Recheck the tentative 32–36 s change from LiDAR-only geometry and reference coverage. Freeze a scene-based event interval before viewing indicator/error peaks. If it is not demonstrably weak-to-rich geometry, reject it as a recovery event. Once this and the frame/evaluator gates pass, calculate provisional 1 s and 3 s development local-motion errors and fixed pre-event drift only where reference and frames are valid. Publish valid/unavailable counts and reasons, not just selected good rows.
4. **Finish T08 and T09 only after those gates.** Export an online-only conventional indicator with verified geometry and timing; create the reviewed transition pilot including failures and missing intervals.
5. **Hold R1 as a real go/no-go review.** Check novelty, usable recovery evidence, and the map-registration reference's independence. R1 must decide whether Exp18 supports only qualified development work and whether a separate independent-reference dataset or narrower question is required. Do not mark R1 PASS from the present smoke replay.

The [README](../../README.md) explains this in everyday language and shows the two data pictures. Historical GEODE notes and handoffs remain evidence of what was tried, not instructions to redo it by default. Preserve the `old_data/` archive and its held-out-seed rules; its synthetic safe-landing results are not evidence for this new paper.
