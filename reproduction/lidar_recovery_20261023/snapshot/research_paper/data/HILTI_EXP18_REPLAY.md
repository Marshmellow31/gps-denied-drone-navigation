# Hilti Exp18 first FAST-LIO development replay

23 September 2026. **Exploratory software smoke test, not a recovery result.** The 55-second replay contains the tentative 32–36 s scene change but was not tuned on a final-test sequence.

**24 September successor:** The [frame audit](HILTI_EXP18_FRAME_AUDIT.md) strongly supports the reference's `xyzw` world-from-IMU convention in the bag IMU axes using a raw-gyroscope check independent of FAST-LIO output. The evaluator still needs repair and no formal 6-DoF error has been calculated; the smoke observations below are unchanged.

## What ran

- Source: publisher-hash-verified [Hilti-Oxford Exp18 recording](HILTI_EXP18_INSPECTION.md), LiDAR and IMU topics only. Cameras and dense reference were not passed to FAST-LIO.
- Backend: pinned official FAST-LIO revision `7cc4175de6f8ba2edf34bab02a42195b141027e9`, with the existing C++17/PCL compatibility patch. A fresh RoboStack ROS Noetic environment and catkin build were placed on the Acer partition; the build succeeded (all three packages, with deprecation/runtime-path warnings).
- Input conversion: [Hesai timestamp adapter](../experiments/src/hesai_time_adapter.py), feeding the backend's Velodyne-shaped `PointCloud2` path. The adapter changes point packing and expresses absolute point times as scan-start offsets; it does not change coordinates or read truth.
- Effective parameters: [exploratory config](../configs/fastlio_hilti_exp18_exploratory.yaml). Published Hilti LiDAR pose in IMU coordinates is used as the proposed FAST-LIO extrinsic. `blind: 0.2 m` is a development setting motivated by the many sub-2 m returns during the early confined section; it is **not** a tuned or final threshold.
- Replay command: from the repository root, `timeout 150 bash research_paper/experiments/run_hilti_exp18_smoke.sh`. The script starts ROS, backend, adapter and pose logger, then plays only `/hesai/pandar` and `/alphasense/imu` for the first 55 s. It tears the processes down after playback. Logs, pose CSV and manifest are retained on the Acer partition under `GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/exp18_first55_exploratory/`.

## Observed outcome

- The ROS bag player exited normally. The adapter saw and published 551/551 LiDAR clouds, with zero rejections. FAST-LIO emitted 546 valid poses from +0.400 to +54.898 s relative to the first LiDAR header. The pose stream has one continuous segment, no reset rows and no invalid pose rows. FAST-LIO logged one `No point, skip this scan!` warning near the start and no later warning in its captured output.
- A **gross, alignment-independent distance sanity check** compares the length of displacement between nearby endpoints, not full trajectory error. For +10 to +30 s: estimate 7.819 m vs reference 7.848 m; +30 to +50 s: 12.016 vs 11.935 m; +35 to +54 s: 9.469 vs 9.457 m. These are exploratory checks using the published reference after the run. They do not establish coordinate-frame correctness, rotational accuracy, short-window reliability, or recovery. Matching total displacement can still hide local mistakes and drift.
- The Acer-side `manifest.json` records input/output hashes and the dirty repository state. It deliberately says `partial`: peak memory and exact wall timing were not measured, so this is not a canonical T06 performance run.

## Remaining scientific gate

The [publisher's 2022 page](https://hilti-challenge.com/dataset-2022) and [frame FAQ](https://github.com/Hilti-Research/hilti-slam-challenge-2022#faq) identify the dense reference as IMU-frame, and its calibration places the LiDAR under the IMU. Before formal 6-DoF error calculation, verify the released reference's quaternion order/pose direction and the exact equivalence of FAST-LIO's `body`, ROS `imu_sensor_frame`, and calibration `imu`. The first two recorded IMU orientation fields are zero; they cannot be treated as attitude truth. The reference is map-registration-derived, has gaps and ends at +86.7 s, so it remains development evidence with qualified independence. The tentative 32–36 s transition needs a stricter scene-geometry annotation independent of indicator and error curves.

Next: verify these frame/reference semantics, then run the offline evaluator on this **development** stream with explicit unavailable intervals. Do not set recovery labels or compare indicators yet. R1 must decide whether this reference supports a suitably qualified paper question or whether an independent-reference dataset is required.
