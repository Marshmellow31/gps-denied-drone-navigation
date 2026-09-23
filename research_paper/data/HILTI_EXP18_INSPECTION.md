# Hilti-Oxford Exp18: actual-file inspection

Inspected 23 September 2026. **Development candidate only.** A subsequent [55-second FAST-LIO smoke replay](HILTI_EXP18_REPLAY.md) produced poses; no formal pose-error calculation, health-indicator export, or recovery finding has been made on this recording.

## Provenance and storage

- Recording: official [Hilti-Oxford 2022 Exp18 Corridor Lower Gallery 2](https://hilti-challenge.com/dataset-2022), downloaded from the publisher's [dataset repository](https://huggingface.co/datasets/Hilti-Research/hilti-slam-challenge-2022).
- Bag: `/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag`; 8,657,654,860 bytes; SHA-256 `98373b52f207b9ace3914792b5604a6642f89441190cabca6acbaf1d17249280`, matching the publisher's file hash. It stays outside Git and on the Acer partition.
- Dense IMU-frame reference: same folder, `exp18_corridor_lower_gallery_2_imu.txt`; 789 rows; SHA-256 `138def6a40884a87372a4f18938cce5180d6aa7ad4e705349abf47ac4ec9fa32`.
- Published calibration: same folder, `lidar_calibration.yaml`; SHA-256 `ea5127989317270d83d9a701318d7e284031a21bd9cbf466b8f9f169547db43c`.
- Small files were fetched from their official `resolve/main` paths. They are for offline inspection and are not to be passed to the online estimator except the relevant sensor calibration.

## Actual sensor streams

The bag begins `#ROSBAG V2.0` and opens as ROS 1. Its bag span is 109.405 s. A read-only pass with `rosbags==0.11.5` found:

| Topic | Messages | Header span (Unix ns) | Median / maximum adjacent gap | Frame observed |
| --- | ---: | --- | --- | --- |
| `/hesai/pandar` (`sensor_msgs/PointCloud2`) | 1,094 | 1649856227623466000–1649856336918471000 | 0.100 / 0.103486 s | `PandarXT-32` |
| `/alphasense/imu` (`sensor_msgs/Imu`) | 43,656 | 1649856227670770220–1649856337028370317 | 0.002505 / 0.0025356 s | `imu_sensor_frame` in first two samples |

Both stream header timestamp sequences are strictly increasing. The bag also contains five camera topics, each with 4,376 images, and three `/Point_name` strings. None were decoded or used. These camera streams must not become estimator inputs.

Eleven LiDAR samples at roughly 10 s spacing share the little-endian 48-byte point schema: `x,y,z` float32 at offsets 0,4,8; `intensity` float32 at 16; `timestamp` float64 at 24; `ring` uint16 at 32. The first cloud has 60,976 points. Its first/last stored point times are 1649856227.623467/1649856227.723469 s, while its cloud header is 1649856227.623466 s. This is an **absolute acquisition timestamp**, not the GEODE `time` offset. Sampled scans span about 0.1 s. A [Hesai-specific adapter](../experiments/src/hesai_time_adapter.py) now converts the actual point schema to the pinned FAST-LIO's expected shape while preserving point-relative acquisition times; the existing GEODE/Velodyne adapter is incompatible. All **1,094** real LiDAR clouds passed the adapter's offline schema/order/duration checks; maximum observed relative-time roundoff was `2.38418579e-7 s`, and maximum cloud-header/first-point difference was `1,120 ns`. The ROS publishing wrapper and backend replay have **not** yet been exercised. The official [Hilti FAQ](https://github.com/Hilti-Research/hilti-slam-challenge-2022#faq) confirms that the actual per-point time is in the point payload rather than a single cloud-wide field.

The first two IMU messages have angular velocity and acceleration values, but their orientation quaternion is all zero, so orientation must be treated as unavailable, not an identity attitude. The publisher's [same-platform hardware note](https://github.com/Hilti-Research/hilti-slam-challenge-2023/blob/main/documentation/hardware/Handheld.md) names `imu_sensor_frame` for this Alphasense IMU; the relation to the `imu` calibration-frame alias still needs explicit confirmation in the effective replay configuration. The calibration lists `PandarXT-32` as a child of `imu`, with translation `[-0.001,-0.00855,0.055]` m and xyzw quaternion `[0.7071068,-0.7071068,0,0]`; the IMU is identity under `base_link`. The publisher's [frame FAQ](https://github.com/Hilti-Research/hilti-slam-challenge-2022#faq) says the ground truth uses the installed IMU frame.

## Reference overlap and tentative scene event

Reference rows run from 1649856227.723471 to 1649856314.319139 s: 86.596 s, beginning about 0.100 s after the first cloud. Thus roughly the final 22.6 s of LiDAR has **no** released dense reference. The text rows are timestamp, position and quaternion; there are no per-row covariance or quality flags. Timestamp rows are monotonic. Five gaps exceed 0.5 s, with two 1.3 s gaps around relative 39–40 s and 75–76 s; several gaps just exceed the provisional 0.20 s association limit. No comparison may interpolate across an excluded gap.

LiDAR-only top-down snapshots at 5 s spacing, then 1 s around 25–45 s, were saved under ignored `experiments/generated/inspection/`. They were reviewed without estimator output, indicators or error curves. At 0–30 s, returns are mostly nearby (sampled 90th-percentile ranges about 1.1–2.1 m). Around 33–36 s larger curved/asymmetric structures enter the visible field; at 35.5 s the sampled 90th-percentile range is 13.4 m. A **tentative** near-structure-to-richer-structure transition lies around 32–36 s. This is not yet proof of a corridor exit or geometric degeneracy: scene annotation needs a more careful geometry check before T09, and must not be moved to fit backend errors. The 34.2–34.4 s reference gap may invalidate windows crossing it under the existing 0.20 s rule.

The publisher derives this dense reference by registering the mobile LiDAR scans to a surveyed map, so it is not fully independent of LiDAR geometry. Use it for exploratory development only unless R1 accepts a qualified protocol. It cannot by itself establish an independent-reference final result or drone performance; this is a handheld recording.

## Reproduction and next gate

From the repository root, with `rosbags==0.11.5`, NumPy and Pillow available:

```bash
python3 -m pip install --target /tmp/hilti_python 'rosbags==0.11.5'
PYTHONPATH=/tmp/hilti_python python3 research_paper/experiments/src/inspect_hilti_exp18.py '/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag'
PYTHONPATH=/tmp/hilti_python python3 research_paper/experiments/src/hilti_scene_overview.py '/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag' research_paper/experiments/generated/inspection/hilti_exp18_overview.png --limit-s 90
PYTHONPATH=/tmp/hilti_python python3 research_paper/experiments/src/verify_hesai_adapter.py '/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag'
PYTHONPATH=/tmp/hilti_python python3 -m unittest discover -s research_paper/experiments/tests -q
```

The `/tmp/hilti_python` target is an ephemeral inspection dependency, not a persistent environment; reinstall or use an equivalent isolated one when reproducing. The next bounded work after the [successful short replay](HILTI_EXP18_REPLAY.md) is frame/reference verification and offline development error calculation. If formal 6-DoF comparison cannot be justified, leave it unavailable and bring the dataset/backend choice to R1; do not silently tune against held-out sequences.
