# Hilti Exp18 T07 development pilot — local errors exist, recovery evidence is sparse

24 September 2026. This is a **provisional development-only** offline comparison of one 55-second FAST-LIO smoke replay against the publisher's dense IMU-body reference. It is not a final-test result, not an independent ground-truth validation, and not a recovery finding. The [scene event](../data/HILTI_EXP18_EVENT.md) and [analysis bins](../protocol/HILTI_PILOT_ANALYSIS.md) were fixed before error distributions were summarized.

## Reproducible inputs and checks

- Pose file: Acer-side `runs/exp18_first55_exploratory/poses.csv`, 546 valid poses, SHA-256 `412c4924a2726e1c04e6db88c55618c4c76295f1659c5d12e448a6334b6505eb`.
- Reference: `exp18_corridor_lower_gallery_2_imu.txt`, 789 rows, SHA-256 `138def6a40884a87372a4f18938cce5180d6aa7ad4e705349abf47ac4ec9fa32`; 20 coverage segments and 19 excluded gaps under the provisional 0.20 s association rule.
- Comparison body and clock: [qualified development metadata](../data/hilti_exp18_reference_metadata.json), checked against the actual file hash and pose clock. Identity body relation was chosen from publisher/backend evidence and raw gyroscope, not fitted to errors.
- Evaluator: [trajectory_eval.py](../experiments/src/trajectory_eval.py); 24 experiment tests passed in the compatible isolated Python environment. Synthetic tests cover relative transforms, world-frame changes, quaternion signs, gaps, resets, explicit anchors and scene summaries.
- Row-level result: ignored `research_paper/experiments/generated/runs/exp18_first55_exploratory/evaluation.csv`, 1,092 rows (546 starts × two windows), 254,830 bytes, SHA-256 `7b12873532201b6c770f41e015b0f26f927461bb78dada86046bddfa696c5159`. The [summary script](../experiments/src/summarize_hilti_pilot.py) recreates the counts below from this CSV.

Reproduce from the repository root after mounting Acer read-only:

```bash
python3 research_paper/experiments/src/trajectory_eval.py \
  --poses /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/exp18_first55_exploratory/poses.csv \
  --reference /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2_imu.txt \
  --body-transform-json research_paper/data/hilti_exp18_reference_metadata.json \
  --development-only --event-id HILTI_EXP18_EXIT_NEAR_TO_OPEN \
  --alignment-target-ns 1649856252623466000 \
  --run-id exp18_first55_exploratory \
  --output research_paper/experiments/generated/runs/exp18_first55_exploratory/evaluation.csv
python3 research_paper/experiments/src/summarize_hilti_pilot.py \
  research_paper/experiments/generated/runs/exp18_first55_exploratory/evaluation.csv
```

The explicit 25.0 s alignment target is **pre-exit**, because no preceding entry into weak geometry was identified. Its accumulated-error column cannot be called original pre-entry drift or pooled with an entry/exit study. No post-event alignment or scale fit was performed. Raw reference never entered FAST-LIO.

## Availability first

| Window and start-time bin | Planned | Local valid | Invalid reasons |
| --- | ---: | ---: | --- |
| 1 s, entire 55 s replay | 546 | 422 | 114 `REFERENCE_GAP`; 10 `WINDOW_INCOMPLETE` |
| 3 s, entire 55 s replay | 546 | 344 | 172 `REFERENCE_GAP`; 30 `WINDOW_INCOMPLETE` |
| 1 s, pre-scene 26.0–31.6 s | 56 | 56 | none |
| 1 s, transition 31.6–33.6 s | 20 | 17 | 3 `REFERENCE_GAP` |
| 1 s, matched post-scene 35.0–40.6 s | 56 | **13** | **43 `REFERENCE_GAP`** |
| 3 s, pre-scene | 56 | 53 | 3 `REFERENCE_GAP` |
| 3 s, transition | 20 | **0** | 20 `REFERENCE_GAP` |
| 3 s, matched post-scene | 56 | **0** | 56 `REFERENCE_GAP` |

The entire replay's pre-exit alignment was valid at 496 of 546 unique pose timestamps. It is a separate availability quantity from local windows. No reset occurred in this smoke replay; reset-crossing behavior was checked in fixtures.

## Descriptive errors, not a recovery claim

The table gives median translation error and median rotation error among *valid* windows only. Nearby start times are correlated and are not independent repetitions.

| Window | Pre-scene | Transition | Matched post-scene |
| --- | --- | --- | --- |
| 1 s | 0.0832 m; 0.0266 rad (56 rows) | 0.0575 m; 0.00413 rad (17 rows) | 0.0230 m; 0.00337 rad (**13/56 rows**) |
| 3 s | 0.2130 m; 0.0281 rad (53 rows) | unavailable (0/20) | unavailable (0/56) |

The valid 1 s rows look smaller after the scene change, but **77% of the planned matched post-scene 1 s rows and all 3 s rows are unavailable**. The surviving rows could be unrepresentative; this result cannot establish sustained recovery, a false-reassurance rate, or a detection delay. Pre-exit-aligned accumulated translation-error medians were 0.153 m pre-scene and 0.460 m matched post-scene (56 and 37 alignment-valid pose timestamps respectively), but these are descriptive and share the reference's map-registration dependence. They do not establish drift accumulated from before a degeneracy entry.

## Scientific decision

T07's evaluator has now produced and audited real development error streams with valid and invalid counts, so its **software/evaluation acceptance** can close. Exp18 does **not** clear the research-evidence gate for a 1 s/3 s sustained post-exit recovery study. R1 must reject it as sole quantitative real-data support for that claim or formally narrow the question. The logical workaround is an independently referenced, better-covered sequence and/or a controlled simulation with known scene truth—not an invented interpolation across missing reference, fitted time shift, or lowering the required validity standard after seeing these results.
