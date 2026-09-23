# Development sequence inspection: GEODE Urban_Tunnel01

**Historical T04 selection:** GEODE was selected and inspected for the original development attempt. Its later FAST-LIO runs were not usable for recovery analysis, and its reference body remains unverified. The current provisional replacement development candidate is [Hilti-Oxford Exp18](HILTI_EXP18_REPLAY.md). Start future work from the [current handoff](../execution/CURRENT_HANDOFF.md); retain this page as GEODE provenance.

Inspection completed: 22 September 2026. `Urban_Tunnel01` is accepted as the **development-only** real-recording candidate for a second tunnel exit. It supplies complete LiDAR/IMU initialization history and reference poses before and after the selected transition, but the reference is unavailable through most of the tunnel. This is ground-vehicle evidence, not aerial validation.

## Provenance and retained paths

- Official dataset: GEODE public Google Drive linked by the official project repository and project page.
- Sequence: `Urban_Tunnel01`, alpha rig, vehicle platform.
- Official bag object: Drive ID `1bJ14CFyXwfgSB2kUvwvZHslLZh1X4iHQ`; Drive displayed 3.19 GB and downloaded 3,426,578,909 bytes.
- Original bag SHA-256: `e00b8b7a320f5d6804e762df14f63553f1cb2d6578b6645119f220ada3fe6173`.
- Retained study subset: `experiments/generated/raw/geode/Urban_Tunnel01/bag/Urban_Tunnel01_lidar_imu.bag`, 1,830,321,130 bytes, SHA-256 `4d479cefb4e5dd1a5b14de95b0dc50377b2ab431135b9c5a766112869597cc17`.
- The subset contains the complete `/imu/data` and `/velodyne_points` streams and excludes only two camera topics, which are outside the active scope.
- Official separated files are retained beside the bag. Their Drive folder IDs are LiDAR `1_AFom1doK9Q5uOYgA9kfDvaTDUi58paU`, IMU `1yNnou5Zr82rmXLrrqOqXWBktfwXcLW_n`, and trajectories `1WdL7-TCDHwxC_wjASR3ncuDlV3_5E9XC`.

Checksums:

| File or set | SHA-256 | Size / count |
| --- | --- | --- |
| Full downloaded bag (provenance; removed after verified subsetting) | `e00b8b7a320f5d6804e762df14f63553f1cb2d6578b6645119f220ada3fe6173` | 3,426,578,909 bytes |
| Retained LiDAR+IMU bag | `4d479cefb4e5dd1a5b14de95b0dc50377b2ab431135b9c5a766112869597cc17` | 1,830,321,130 bytes; 31,427 messages |
| `IMU/imu.txt` | `b0a101a2f0c7a54919f4692806709c59124ccce0776e9019c4d00d8acb09203d` | 3,157,045 bytes; 28,570 rows |
| `reference/Urban_Tunnel01.txt` | `a5538a32a90b2e54a9f89051435804b9f32046a761f6f43d8b6452d052e227df` | 1,525,722 bytes; 10,633 rows |
| `calibration/alpha_config.yaml` | `b5749fcc59ad57b33136c82769c635cd9c4e6f28318c191920abde2f564d8802` | 4,801 bytes |
| Sorted checksum-list digest for 42 separately downloaded `.bin` files | `a6860c0a57f8315f2d517832501b8f246f7e3b8c0b7cd8b47c94d7399ee09c90` | 42 initial frames |

The two retained-bag topic digests include each message timestamp and serialized payload. They exactly matched the full bag:

- `/imu/data`: `a9dbbd632683ad2c6248960bffdd9f0c034df416f99003c539849ade92cf35f9`
- `/velodyne_points`: `cceba252ced25504246960878994f3aa4f864cbaae491747ddb3d1a3ffe89a5a`

## Actual bag inspection

The downloaded file begins `#ROSBAG V2.0`. This is a ROS 1 bag despite the paper saying the alpha rig collected with ROS 2; the current repository README separately says only ROS 1 bags are released. Downstream work must follow the actual file rather than assume collection middleware equals release format.

| Topic | Type | Messages | Header span | Median spacing | Maximum spacing | Frame |
| --- | --- | ---: | --- | ---: | ---: | --- |
| `/imu/data` | `sensor_msgs/Imu` | 28,570 | `1693022008.641275644`–`1693022294.312655449` | 0.010006 s | 0.032787 s | `imu_link` |
| `/velodyne_points` | `sensor_msgs/PointCloud2` | 2,857 | `1693022008.716670513`–`1693022294.320856094` | 0.099728 s | 0.132442 s | `velodyne` |

Both bag and header timestamps are strictly increasing. The largest observed absolute bag-time/header-time difference is below 0.24 microseconds, which is the float-conversion resolution used by the inspection; exact integer nanosecond values were retained in the bag.

The original bag also contains `/left_camera/compressed` (2,857 messages) and `/right_camera/compressed` (2,856 messages). They were inspected only as inventory and excluded from the study subset without decoding or use.

### IMU

The bag supplies orientation quaternion, angular velocity, and linear acceleration under standard `sensor_msgs/Imu` fields. All 28,570 orientation quaternions have norms from 0.9999996 to 1.0000003. Every orientation, angular-velocity, and linear-acceleration covariance array is all-zero; these covariances are therefore **unavailable**, not evidence of zero uncertainty.

The official paper (Section 4.3.1) defines separated `imu.txt` rows as timestamp, roll, pitch, yaw, angular velocities, and linear accelerations. The text file has ten numeric fields and exactly matches the bag timestamp span/count. Units follow the ROS message contract for the bag (`rad/s` angular velocity and `m/s^2` linear acceleration); T05 must state that the three separated attitude columns are not estimator inputs unless explicitly selected.

### LiDAR

Every point cloud uses the same little-endian 22-byte schema: `x/y/z/intensity` float32, `ring` uint16, and `time` float32 at offsets 0/4/8/12/16/18. Clouds contain 28,800–29,184 points (82,660,064 total), rings 0–15, and observed per-point `time` values -0.099533 to 0.001306 s. Shapes vary only among 1,800, 1,822, or 1,824 rows by 16 columns. No payload has a partial point record. The sign and reference instant of `time` remain a backend-compatibility item for T06; values indicate approximately one scan period ending near the message stamp, but that interpretation is not treated as proven here.

### Calibration

The official `alpha_config.yaml` declares VLP-16 resolution, `/velodyne_points`, `/imu/data`, and a numeric `T_IMU_LiDAR` 4x4 matrix. Its rotation is near-orthonormal (determinant 0.99999996). The key name alone does not prove transform direction, and the three published camera/LiDAR/IMU transforms do not close consistently (about 0.41 Frobenius discrepancy under the obvious composition), so cycle consistency cannot resolve it. The file also repeats `gyro_std`; a generic YAML parser could silently overwrite gyro white-noise density with the random-walk value. T05/T06 must use an explicit declared convention and preserve both noise values rather than ingest this YAML blindly.

## Reference trajectory and coverage

The official repository describes evaluation trajectories as TUM format, and `alpha2GT_gnss.py` at revision `c6e930623d4fed450d7fc50e16e3ffe0288b692b` reads columns as `timestamp x y z qx qy qz qw`. The paper, Section 4.4.2, states that urban-tunnel 6-DoF reference comes from a CHCNAV CGI610 RTK/INS refined by hand-eye calibration. The exact global axis/datum, pose transform direction, achieved uncertainty, fix status, and covariance are not included in the released trajectory file; the advertised 1 cm value is an instrument RTK specification, not demonstrated per-sample accuracy.

The file contains 10,633 rows from `1693022008.5467005` through `1693022294.1236045`. Quaternion norms are unity within floating-point precision. Raw file order contains 643 adjacent timestamp decreases below 0.094 s, so evaluation must sort within reference-valid segments and retain duplicate/out-of-order handling explicitly.

Three large reference gaps are unavailable intervals:

| Gap | Absolute interval | Relative to first LiDAR stamp |
| --- | --- | --- |
| 1 | `1693022065.8084671`–`1693022136.6091542` | 57.092–127.892 s (70.801 s) |
| 2 | `1693022152.0432425`–`1693022162.3720567` | 143.327–153.655 s (10.329 s) |
| 3 | `1693022181.7708526`–`1693022252.5867820` | 173.054–243.870 s (70.816 s) |

The selected second exit is usable because reference resumes during its scene-boundary interval and continues through the remaining 41.54 s. From relative 243.870 s to 285.407 s there are 3,323 reference samples, median spacing 0.010013 s and maximum spacing 0.170300 s. A pre-entry reference segment exists from relative 153.834 s to 173.054 s; it contains 1,474 samples but one 0.771 s gap that T05 must treat under its maximum-association-gap policy. No interpolation across the 70.816 s tunnel gap is permitted.

## Tentative scene annotation

The selected event is `UT01_TUNNEL2`, recorded in [transition_annotations.csv](transition_annotations.csv). It was annotated manually from LiDAR-only top-down snapshots at two-second spacing; no estimator output, health indicator, or reference error curve was consulted.

- **Entry boundary:** relative 168.003–174.010 s (`1693022176.719765425`–`1693022182.726409674`), nominal frame at 171.008 s. Distant/asymmetric lateral structure visible at 164–168 s gives way to close, parallel walls on both sides by 172–174 s.
- **Exit boundary:** relative 242.005–252.007 s (`1693022250.721660614`–`1693022260.723832607`), nominal frame at 247.005 s. Close parallel tunnel walls dominate at 238–242 s; distant/asymmetric exterior structure emerges from 244–250 s; by 252 s the opposing close wall is absent.
- **Weak-geometry interior for the pilot:** entry completion to exit onset, 174.010–242.005 s. This is a scene label, not a claim that every scan has identical observability.

The two-second visual resolution and manual interpretation make these intervals provisional development annotations. T11 may formalize annotation rules after the pilot, but must not move this development boundary using indicator or error peaks.

Reproducible visual-inspection files remain under ignored `experiments/generated/inspection/`; their SHA-256 values are:

- overview: `a7b42d8d1cd1c5a7194214780b6bc0e6efcc5ac79cad9adb8cd3591fc68556de`
- second entry: `8b1f468f195494c7aab4e06d364e29e1eac7f8f8a206cdd59c00be6179aad0a5`
- second exit: `15b6fb3d7c1f39c5a92b3c1d64fa16cec4a03131a4f9bd6f0612282b2b491036`

## Acceptance and limitations

- [x] Official recording provenance, hashes, retained storage path, and exact subset are recorded.
- [x] Actual ROS topics, message definitions, timestamps, frames, counts, LiDAR fields, and IMU fields were inspected.
- [x] Full initialization-to-transition LiDAR/IMU history is retained.
- [x] Published reference columns and actual coverage are documented without converting gaps to valid data.
- [x] A post-exit reference interval covers the selected recovery boundary and horizon.
- [x] Entry/exit intervals use scene evidence independent of indicators and estimator errors.
- [x] Calibration and reference uncertainties remain explicit.

Remaining limitations are material but do not prevent a development pilot: the data are vehicle-mounted; reference fix flags/covariance and achieved accuracy are absent; the global frame/datum and exact body convention are not published; reference is unavailable inside the tunnel; calibration direction is ambiguous; dataset reuse terms remain unstated. R1 must decide whether these limitations permit the full question after the pilot. This sequence is development data and must never be moved into a held-out split.
