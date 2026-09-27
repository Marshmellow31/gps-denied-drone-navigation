# 40-second paired simulation pilot (v3)

26 September 2026. **Development feasibility only; no recovery claim.** This
replay repairs the simulator issues recorded by R1: doorway shoulders are
closed and tested, motion includes smooth 3D attitude and a curved path, IMU
inputs include seeded bias drift, and each run continues for 15.75 seconds
after the body leaves the corridor. The full settings and exact hashes are in
the [machine-readable manifest](simulation_motion_v3_manifest.json).

![40-second paired simulation timelines](../figures/simulation_motion_v3_timeline.png)

## What changed

- Added wall shoulders at both room/corridor joins, leaving a 4 m doorway.
  Tests shoot rays through both jambs, both side walls and the open doorway.
- Replaced the sharp constant-acceleration start with a smooth speed ramp and
  added small lateral/vertical movement, roll and pitch alongside yaw. IMU
  acceleration and angular velocity are calculated from the analytic motion.
- Added seeded per-axis gyro and accelerometer bias with slow random walk.
  These values are development stress settings; they are not claimed to match
  a specific sensor. Both paired runs get exactly the same bias and noise.
- Extended the run from 32 to 40 seconds. The long post-corridor summary bin
  is 28–36 seconds, defined from the layout before inspecting v3 summaries.

The rooms span x=-12..0 and x=12..30 m. The corridor spans x=0..12 m. The
body crosses the two doorway planes at 9.25 and 24.25 seconds. These are
layout times, not the exact times when the estimator becomes observable.
The control uses the same movement and sensor inputs but adds four corridor
wall features.

## What the pilot measured

Both sensor bags contain 400 LiDAR scans and 8,021 IMU messages. The only bag
topics are `/sim/points` and `/sim/imu`; a byte-level check found the two IMU
streams identical. The [bag audit script](../experiments/src/audit_paired_simulation_bags.py)
rechecks topic counts and parity. The analytic answer path is stored separately
and was never supplied to FAST-LIO or its health diagnostic.

Each replay accounted for all 400 health groups: 397 valid and three
startup-unavailable. Each produced 397 positions. The evaluator wrote 794
local-motion windows per run; 754 were valid, 40 were incomplete windows,
and none crossed a reference gap.

The following numbers are medians from the plotted seed-10 scene pair. They
describe that run; neighboring time windows are not independent experiments.
Three additional seeds on the same fixed layout are summarized separately in
the [seed-sensitivity report](SIMULATION_SEED_SENSITIVITY.md).

| Layout period | Valid 1 s windows in each run | Corridor movement error | Feature-control movement error | Corridor smallest information value | Control smallest information value |
| --- | ---: | ---: | ---: | ---: | ---: |
| Before, 5–8 s | 30/30 | 0.0930 m | 0.0553 m | 107.5 | 160.5 |
| Inside, 14–20 s | 60/60 | 1.2175 m | 0.9159 m | 15.25 | 34.11 |
| Extended after, 28–36 s | 80/80 | 0.0207 m | 0.0181 m | 141.8 | 83.32 |

The information value is the backend's smallest online measurement-information
eigenvalue at a 3 m lever scale; it has no recovery threshold. Scene-only
ray-counting at 17 s found x-facing surfaces for 342/5,760 rays (5.94%) in the
corridor and 1,043/5,760 (18.11%) in the feature control. This shows the
intended geometric difference in this model, but does not prove complete
unobservability or predict other scenes.

Local movement errors rise inside the corridor and fall in the extended
post-corridor bin in this run. The plot also shows accumulated position error
remaining large after local errors fall. That illustrates why the two
questions must be measured separately; it does not show that a health signal
can reliably identify the right recovery time. No threshold, recovery label,
false-reassurance result or publication claim is assigned.

## Reproduction and checks

The paired 40-second inputs are retained locally under the ignored
`experiments/generated/simulation_bootstrap/` directory. The FAST-LIO replays,
health exports and evaluations are under ignored `experiments/generated/runs/`.
Raw bags and replay outputs are not committed. Exact SHA-256 values, source
hashes, realized biases and counts are in the linked manifest.

Reproduce the inputs, sequential replays, reference evaluation and exports
using the [simulation protocol](../protocol/SIMULATION.md). The replay used
FAST-LIO revision `7cc4175de6f8ba2edf34bab02a42195b141027e9` with the existing
diagnostic patch. Python was 3.12.14 and NumPy 2.5.3.

Verification: ten focused simulator tests passed; the full experiment suite
reported 40 passed and one SciPy-dependent scene test skipped (41 executed).
Both health audits, both reference hash checks and trajectory evaluations
passed. The paired 8,021-message IMU streams are byte-identical. Python and
shell syntax checks passed. The figure was inspected visually.

## Limits and next step

The simulation uses one hand-designed scene pair, repeated with four
noise/bias seeds, axis-aligned rectangular surfaces, ideal clock/extrinsic
calibration, a prescribed smooth motion and synthetic truth. The IMU noise
and bias values have not been calibrated against a physical unit. Four
repeats on one layout cannot establish scene generalization, recovery
reliability or publication novelty. There is still no frozen
recovery rule, published comparator, repeated-scene design or final-test
evaluation. Keep T12 running under its bootstrap-only exemption and keep R1
at **REVISE** until the literature overlap audit and independent review are
finished.
