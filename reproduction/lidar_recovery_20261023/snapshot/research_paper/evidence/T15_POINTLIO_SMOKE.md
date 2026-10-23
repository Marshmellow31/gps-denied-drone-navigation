# T15 — Point-LIO development smoke and compatibility check

Updated: 27 September 2026. **T15 is complete as one development-only backend
smoke.** This verifies that the pinned Point-LIO candidate can consume the
same simulated LiDAR/IMU bag and produce the shared pose-file format. It is
not a recovery result, an estimator comparison study, or evidence about
real-world performance.

## What was tested

The smoke replayed the existing formal development input
`T14_FORMAL_DEV14_CORRIDOR_INPUT_XM6_V1`, seed 14, through the pinned Point-LIO
source. The sensor bag hash is
`89f4ac21b24a2b9dfc86b74cd3d082e48365ac1ed63207b08969e7aca25d4627`; the
input manifest records 600 LiDAR scans, 3,456,000 points and 12,021 IMU
messages over 60 seconds. It is a development input only. No held-out input
was opened.

Point-LIO produced 597 valid poses, all in the `camera_init`/`body` frame pair.
Their timestamps increase strictly, span 59.6 seconds and are spaced at a
median 0.1 seconds (10 Hz). All quaternion norms pass the logger's validity
check. There are no pose-stream reset boundaries. The backend log contains
one `Reset ImuProcess` message during initial IMU startup; Point-LIO's source
calls that reset on its first frame. It is not a later pose discontinuity.
The first published pose is at 0.4 seconds, so three initial LiDAR updates did
not produce an odometry row during startup.

The existing offline trajectory evaluator accepted the Point-LIO CSV and
returned 1,194 evaluation rows: 1,154 local-motion rows are valid, all 1,194
have a valid reference and pose record, and the reference has no gaps or
out-of-order samples. T15 deliberately leaves recovery labels blank; frozen
recovery analysis belongs to T16 and is not inferred from this smoke.

## Compatibility finding

| Check | Finding |
| --- | --- |
| Input sensor contract | PASS for this one smoke: `/sim/points` is interpreted as Point-LIO's 16-ring VELO16 `PointCloud2`, with point times in seconds; `/sim/imu` is 200 Hz. |
| Shared pose output | PASS: the pose logger wrote the T05 CSV columns and the offline evaluator read them. |
| Reset and time handling | PASS for this run: one expected startup initialization reset in the backend log, no pose reset marker, strictly increasing timestamps. |
| FAST-LIO minimum-eigenvalue (`G3`) health signal | Not comparable yet. |
| DCReg Schur-mask health signal | Not comparable yet. |

The last two rows are an important limit. T10/T13 compute these signals from
FAST-LIO's accepted point-to-plane correspondences. The Point-LIO smoke
exported poses but did not export an equivalent validated health/Hessian
stream. A pose trajectory is not a substitute for either online indicator.
R3 must keep any Point-LIO replication claim limited to the checks above
unless a separate, validated Point-LIO indicator adapter is implemented and
reviewed.

## Source, build and configuration

- Point-LIO repository revision: `4b86a469eb5572e70ed575af25b5f15dd06e8e3c`
  (pinned source; no moving branch reference is used for the run).
- Runtime stack: ROS Noetic/roscpp 1.17.4, catkin_tools 0.9.5, Python 3.12.14,
  GCC 15.2.0, CMake 4.2.3, PCL 1.15.1 and isolated glog 0.7.1.
- The two reversible upstream patches are build compatibility only:
  C++17 for the installed PCL toolchain, the glog export definition, and a
  missing standard `<deque>` include. They do not change Point-LIO's estimator
  or measurement-update algorithm. Their patch hashes and reverse-apply
  checks are in the [machine manifest](t15_point_lio_smoke_manifest.json).
- The smoke configuration is
  [`point_lio_simulation_development.yaml`](../configs/point_lio_simulation_development.yaml).
  It uses VELO16 fields (`time` in seconds, `ring`), 16 scan lines, the
  simulator's topics/rates and identity simulated sensor extrinsics.
- Point-LIO uses a private ROS node handle. The runner now loads its YAML under
  `/laserMapping`, verifies the required gravity parameter, fails if ROS or
  Point-LIO exits early, limits bag playback to 120 seconds and rejects an
  empty pose file.

The first attempt is retained, not erased. It failed because the initial
runner loaded parameters at the global ROS root. GDB located the resulting
startup crash at upstream `parameters.cpp:121`, where the missing private
gravity vector was read. After correcting the namespace, V2 and V3 both
completed. Their `poses.csv` files are byte-identical
(`a6373a10895e2449d99d663d59f444247865ea39a8d9768192cca2cdc1760abd`). V3 is
the final audited run, after adding fail-fast checks. The failed attempt's
debug trace is under the ignored generated run folder listed in the manifest.

## Reproduction

The exact successful replay command, from the repository root, was:

```bash
export LD_LIBRARY_PATH="/run/user/1000/point_lio_glog/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
bash research_paper/experiments/run_point_lio_smoke.sh \
  /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env \
  /run/user/1000/point_lio_ws \
  research_paper/experiments/generated/t14_retained_inputs/T14_FORMAL_DEV14_CORRIDOR_INPUT_XM6_V1/sensors.bag \
  research_paper/configs/point_lio_simulation_development.yaml \
  research_paper/experiments/generated/runs/T15_POINTLIO_DEV14_CORRIDOR_XM6_V3
```

Then the common offline evaluator was run as follows:

```bash
ln -s ../../t14_formal_input_provenance_v1/shared_reference.txt \
  research_paper/experiments/generated/runs/T15_POINTLIO_DEV14_CORRIDOR_XM6_V3/reference.txt
python3 research_paper/experiments/src/trajectory_eval.py \
  --poses research_paper/experiments/generated/runs/T15_POINTLIO_DEV14_CORRIDOR_XM6_V3/poses.csv \
  --reference research_paper/experiments/generated/runs/T15_POINTLIO_DEV14_CORRIDOR_XM6_V3/reference.txt \
  --output research_paper/experiments/generated/runs/T15_POINTLIO_DEV14_CORRIDOR_XM6_V3/evaluation.csv \
  --run-id T15_POINTLIO_DEV14_CORRIDOR_XM6_V3 \
  --event-id T14_GEOMETRY_EXIT_DEV14 \
  --body-transform-json research_paper/data/point_lio_simulation_reference_metadata.json \
  --development-only --entry-start-ns 1010500000000
```

The build workspace and isolated glog overlay currently live under
`/run/user/1000`, so they are session-local. They are not project data and are
not included in Git. The repository retains the pinned source revision,
reversible patches, configuration and runner needed to rebuild the smoke. The
machine-readable manifest records package versions, input/output hashes and
attempt history. The Acer partition was mounted read-only during this work,
so session-local build files could not be relocated there.

## Evidence and limits

- Successful output: ignored
  `experiments/generated/runs/T15_POINTLIO_DEV14_CORRIDOR_XM6_V3/`.
- Failed setup trace: ignored
  `experiments/generated/runs/T15_POINTLIO_DEV14_CORRIDOR_XM6_V1/gdb_startup_failure.log`.
- Input and artifact hashes, exact counts and attempt states:
  [machine-readable manifest](t15_point_lio_smoke_manifest.json).
- The ROS pose logger's shutdown message still says “FAST-LIO pose logger”
  because this shared logger was originally named for T08. The CSV itself is
  backend-neutral and its values/validity were independently audited; the
  misleading log label is not treated as a Point-LIO result.

One seed, one corridor, one configured run cannot establish Point-LIO
replication, indicator parity, recovery, generalization or publication
readiness. No threshold was selected and no held-out data were generated.

## Next task

Proceed to T16 using the frozen analysis rules and T14 **FAST-LIO** development
outputs only. Keep Point-LIO's single smoke as a separate compatibility check.
Then R3 must review the full implementation, the T14 repeat reconciliation and
the limitations above before any held-out data are generated or opened.
