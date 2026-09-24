# Hilti Exp18 reference and frame audit

24 September 2026. **Development-only frame investigation; formal 6-DoF error has not yet been calculated.** The frame-axis ambiguity identified in the first source review was tested against raw gyroscope data without using FAST-LIO estimates. No recovery label or indicator was calculated here.

## What the published evidence establishes

| Question | Evidence and conclusion |
| --- | --- |
| Reference columns | The released `exp18_corridor_lower_gallery_2_imu.txt` has 789 eight-field rows: `timestamp_s x_m y_m z_m qx qy qz qw`. Its quaternion norms are 1.000000000 to nine decimal places. The [publisher's 2022 evaluator](https://github.com/Hilti-Research/hilti-slam-challenge-2022/blob/e4aacf7c111ab832a0bdffe3f069255454068540/evaluation-2022/evaluation.py#L190-L223) reads references as TUM trajectories, uses `scipy`'s `xyzw` order, constructs a pose matrix from orientation and translation, and composes a body offset on the right. This supports the active `T_reference_world_IMU` interpretation, not an inverse pose or `wxyz` file order. The publisher does not provide an Exp18-specific column header; this is an interpretation based on its evaluation code and the TUM format. |
| Reference body | The [2022 dataset page](https://hilti-challenge.com/dataset-2022) and [frame FAQ](https://github.com/Hilti-Research/hilti-slam-challenge-2022#how-are-the-frames-defined-on-the-sensor-setup) say ground truth is in the installed IMU frame. For filenames ending `_imu.txt`, the official evaluator uses an identity IMU-to-reference offset; for tip-frame files it composes the published IMU-to-tip offset. Thus this released file is intended as an IMU-body reference. |
| FAST-LIO output | Pinned FAST-LIO `7cc4175de6f8ba2edf34bab02a42195b141027e9` publishes `camera_init` to `body` odometry from `state_point.pos` and `state_point.rot` in `laserMapping.cpp` lines 575–595. The same code maps a LiDAR point into the IMU body using `offset_R_L_I * p_L + offset_T_L_I` (lines 210–218), then into world using `state_point.rot` and `state_point.pos` (lines 177–183). Therefore `body` is the backend's IMU-state frame, not its LiDAR frame. The [replay configuration](../configs/fastlio_hilti_exp18_exploratory.yaml) supplies the published `T_imu_PandarXT-32` translation and rotation with extrinsic estimation disabled. |
| Clocks and coverage | The pose CSV declares `hilti_ros_header_unix`; reference decimals are Unix seconds in the same epoch as the LiDAR/IMU headers. No time offset was fitted; replay used `time_sync_en: false` and `time_offset_lidar_to_imu: 0.0`. The reference spans 1649856227.723471–1649856314.319139 s, while LiDAR spans 1649856227.623466–1649856336.918471 s. Nineteen adjacent reference gaps exceed the provisional 0.20 s interpolation limit. Timestamp overlap is necessary but is not proof of sub-frame clock accuracy. The [publisher's same-platform hardware note](https://github.com/Hilti-Research/hilti-slam-challenge-2023/blob/main/documentation/hardware/Handheld.md#synchronization) reports LiDAR/camera clock alignment by PTP within 1 ms; it does not establish the dense reference's exact time uncertainty. |

## Estimator-independent sensor check

The actual bag's `/alphasense/imu` messages name their frame `imu_sensor_frame`, while the released `lidar_calibration.yaml` calls the IMU `imu`. The [publisher's same-platform hardware note](https://github.com/Hilti-Research/hilti-slam-challenge-2023/blob/main/documentation/hardware/Handheld.md#alphasenseimu) connects `/alphasense/imu` with `imu_sensor_frame`, but no inspected 2022 source explicitly states that the two names have identical axes. The [publisher's 2022 robot model](https://github.com/Hilti-Research/phasma_description/blob/79002026e9b229cf9b4e95a403eaec4f00acfd79/urdf/phasma.urdf.xacro#L49-L57) also defines a separate `base` frame at the IMU origin, rotated by pi around x, and comments that ground truth is generated in that frame.

To resolve this without relying on a reply, [`audit_hilti_gyro_reference.py`](../experiments/src/audit_hilti_gyro_reference.py) compared the body-frame turn rate implied by consecutive reference quaternions with the actual `/alphasense/imu` gyroscope average over the same intervals. The four candidate interpretations were fixed before inspecting FAST-LIO errors. Only reference intervals 0.05–0.15 s long with at least 20 IMU samples, actual turning of at least 0.15 rad/s, and no extreme reference turn above 6 rad/s entered the check. The script found 503 such intervals among 789 reference poses and 43,656 IMU messages.

| Fixed interpretation | Vector turn-rate RMSE (rad/s) | What it means |
| --- | ---: | --- |
| `xyzw`, world-from-IMU, same axes as bag gyro | 0.0104 | Strong match; per-axis correlations 0.9998, 0.9992, 0.99999 |
| Same file interpretation but robot `base` rotated 180° about x | 1.8640 | y and z turn signs are reversed |
| `xyzw`, inverse pose, same axes | 0.4906 | Inconsistent with x/y turning |
| `wxyz`, world-from-IMU, same axes | 1.3645 | Inconsistent with turn directions |

**Conclusion for development:** The released `_imu.txt` quaternion axes and direction are strongly supported as the same physical IMU axes used by the bag gyroscope; the robot-model `base` rotation must **not** be applied to this file. Together with the publisher's IMU-body reference statement, identity `_imu.txt` handling in its evaluator, published `T_imu_PandarXT-32`, and FAST-LIO source, this supplies an auditable common-body interpretation for a future **development-only** 6-DoF comparison. It is not a declaration that the reference is independently accurate. The dense reference was generated with LiDAR and IMU, so its close gyro agreement partly reflects shared input. The exact Exp18 production transformation and sub-frame clock uncertainty are still not documented; these remain limitations for R1, not reasons to fit a frame from FAST-LIO error. Do not infer attitude from the bag's all-zero IMU orientation field.

The reference is derived partly from registering mobile LiDAR to a surveyed map, so even after a frame resolution it remains qualified development evidence, not an independent final-test measurement. The 32–36 s scene change is still tentative.

## Reproducibility and next action

The small released files remain on the Acer partition and were rechecked read-only: reference SHA-256 `138def6a40884a87372a4f18938cce5180d6aa7ad4e705349abf47ac4ec9fa32`, calibration SHA-256 `ea5127989317270d83d9a701318d7e284031a21bd9cbf466b8f9f169547db43c`. The first 55-second replay retains 546 pose rows plus a CSV header. The partition was mounted read-only for this audit. The publisher source clones used for code review are temporary and not part of the research repository.

Reproduce the read-only axis check from the repository root using the isolated Acer-side ROS environment:

```bash
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python \
  research_paper/experiments/src/audit_hilti_gyro_reference.py \
  /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag \
  /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2_imu.txt
```

Two unit fixtures check quaternion turn direction; the full experiment test suite now has 21 passing tests after the T07 evaluator repairs. The [sequence-specific metadata](hilti_exp18_reference_metadata.json) records the identity comparison-body choice, file hash, clock, and measured 20 reference segments/19 gaps. Next, decide the tentative scene transition from LiDAR geometry alone before calculating event-anchored Exp18 errors. Keep reference gaps and reference-method dependence explicit; do not set recovery labels or claim a result from this frame diagnostic.
