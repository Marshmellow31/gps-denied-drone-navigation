# Development replay: GEODE Urban_Tunnel01 with FAST-LIO2

Status: FAST-LIO2 build and two development replays completed on 23 September 2026. Their execution manifests and pose streams are retained under ignored `generated/runs/`. Both replays produced poses, but neither provided a trustworthy motion estimate for the selected exit. The offline T07 evaluator is implemented and its eight fixtures pass; generated real-data rows explicitly mark formal errors unavailable because the reference body is unverified. A completed software run is not an accuracy result.

## Pinned inputs and source

- GEODE LiDAR/IMU-only ROS 1 bag: `generated/raw/geode/Urban_Tunnel01/bag/Urban_Tunnel01_lidar_imu.bag`; SHA-256 `4d479cefb4e5dd1a5b14de95b0dc50377b2ab431135b9c5a766112869597cc17`; 2,857 Velodyne clouds and 28,570 IMU messages. Complete stream, including initialization before the second tunnel exit.
- FAST-LIO: official `hku-mars/FAST_LIO` revision `7cc4175de6f8ba2edf34bab02a42195b141027e9` with ikd-Tree submodule `e2e3f4e9d3b95a9e66b1ba83dc98d4a05ed8a3c4`. The only backend source change is [`patches/fast_lio_pcl17.patch`](patches/fast_lio_pcl17.patch), selecting C++17 required by the available PCL 1.15.1. It does not change estimator algorithms.
- Livox message schema: official `Livox-SDK/livox_ros_driver` revision `3d240d5666129e1a3052e78ee8487a04b08fdda3`; the checked-in [`ros/livox_ros_driver`](ros/livox_ros_driver) package includes its two message definitions only. FAST-LIO's Velodyne build requires these types, but the device driver and SDK are unnecessary for this recording.
- Dataset calibration: official GEODE `cali/alpha_config.yaml` at revision `c6e930623d4fed450d7fc50e16e3ffe0288b692b`, SHA-256 `b5749fcc59ad57b33136c82769c635cd9c4e6f28318c191920abde2f564d8802`. Its `T_IMU_LiDAR` name is consistent with FAST-LIO's requested LiDAR pose in IMU coordinates, but GEODE does not define the matrix direction in inspected documentation. The [effective exploratory configuration](../configs/fastlio_geode_alpha_exploratory.yaml) uses the published matrix directly and records this unverified interpretation.

## Isolated build

Host: Ubuntu 26.04.1, x86-64, no system ROS or container runtime. The Conda environment must use a path without spaces because ROS scripts contain unquoted interpreter/prefix paths. The repository path has spaces; `/tmp` paths below worked for the build. The package cache is under ignored `generated/`. At least 6 GiB of temporary free disk is advisable for the ROS package cache/build; its compressed tarballs can be cleaned after installation.

```bash
cd '/home/harshil/Desktop/GPS Denied Drone navigation'
mkdir -p research_paper/experiments/generated/tools
curl -L --fail https://micro.mamba.pm/api/micromamba/linux-64/latest \
  -o research_paper/experiments/generated/tools/micromamba.tar.bz2
tar -xjf research_paper/experiments/generated/tools/micromamba.tar.bz2 \
  -C research_paper/experiments/generated/tools bin/micromamba
export MAMBA_ROOT_PREFIX="$PWD/research_paper/experiments/generated/mamba"
research_paper/experiments/generated/tools/bin/micromamba create -y \
  -p /tmp/fastlio2_ros_env_replay \
  -c https://prefix.dev/robostack-noetic -c conda-forge \
  --strict-channel-priority python=3.12 ros-noetic-ros-base \
  ros-noetic-pcl-ros ros-noetic-eigen-conversions \
  ros-noetic-message-generation ros-noetic-tf ros-noetic-rosbag \
  catkin_tools pcl eigen cmake make pkg-config 'empy<4'
research_paper/experiments/generated/tools/bin/micromamba clean --tarballs -y
```

The combined dependency specification passed a fresh dry solve. The successful local installation used the same package set, then installed `empy<4` after ROS message generation exposed an Empy 4 incompatibility. The micromamba archive SHA-256 in this run is `8761c382127e6363bd9e0a2451aa3ef90d071a79133f736e2f759a3bf13040dd` (tool version 2.9.0). The first local installation under the space-containing repository path was removed after its generated script shebangs proved unusable.

```bash
git clone --filter=blob:none --depth=1 https://github.com/hku-mars/FAST_LIO.git \
  research_paper/experiments/generated/upstream/FAST_LIO
git -C research_paper/experiments/generated/upstream/FAST_LIO checkout \
  7cc4175de6f8ba2edf34bab02a42195b141027e9
git -C research_paper/experiments/generated/upstream/FAST_LIO \
  submodule update --init --depth=1
git -C research_paper/experiments/generated/upstream/FAST_LIO apply \
  "$PWD/research_paper/experiments/patches/fast_lio_pcl17.patch"
mkdir -p /tmp/fastlio2_ws_replay/src
ln -s "$PWD/research_paper/experiments/generated/upstream/FAST_LIO" \
  /tmp/fastlio2_ws_replay/src/fast_lio
ln -s "$PWD/research_paper/experiments/ros/livox_ros_driver" \
  /tmp/fastlio2_ws_replay/src/livox_ros_driver
export CONDA_PREFIX=/tmp/fastlio2_ros_env_replay
export PATH="$CONDA_PREFIX/bin:$PATH"
source "$CONDA_PREFIX/etc/conda/activate.d/ros-noetic-catkin_activate.sh"
catkin config --workspace /tmp/fastlio2_ws_replay --cmake-args \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_BUILD_TYPE=Release
catkin build --workspace /tmp/fastlio2_ws_replay -j 2 --no-status
source /tmp/fastlio2_ws_replay/devel/setup.bash
```

This build completed with both packages successful. It emitted CMake/Boost deprecation and `libgomp` search-path warnings; no runtime inference is made from the build alone.

## Point-time adaptation

The released cloud is little-endian, 22 bytes per point, with float32 `time` at offset 18. The first actual cloud has 29,152 points, `time` from `-0.099532999` to `+0.001306368` s, and header stamp `1693022008716670513` ns. FAST-LIO's Velodyne handler expects a positive end-point offset and uses the final point offset to derive scan end. [`src/velodyne_time_adapter.py`](src/velodyne_time_adapter.py) shifts the header backward by the minimum point offset and adds the same duration to all offsets. It preserves absolute point acquisition times. On the first actual cloud, the maximum point-time difference after this float32 operation was 3.824 ns. No reference trajectory is read by this adapter.

The adapter publishes `/velodyne_points` from `/velodyne_points_raw`; the effective configuration sets `preprocess/timestamp_unit: 0` (seconds), `preprocess/lidar_type: 2`, `preprocess/scan_line: 16`, the actual `/imu/data` topic, and `pcd_save_en: false`.

## Development replay commands and results

With the isolated environment and catkin workspace sourced as above, run the following from the repository root. Keep the four long-running processes in separate terminals. The first three commands start ROS, load the effective parameters, and start FAST-LIO; then start the adapter and pose logger before the bag player. Use a new output directory and fresh backend process for every run.

```bash
roscore
rosparam load research_paper/configs/fastlio_geode_alpha_exploratory.yaml
rosrun fast_lio fastlio_mapping
python research_paper/experiments/src/velodyne_time_adapter.py
python research_paper/experiments/src/pose_logger.py \
  --output research_paper/experiments/generated/runs/T06_full/poses.csv
rosbag play -q --clock -r 1 \
  research_paper/experiments/generated/raw/geode/Urban_Tunnel01/bag/Urban_Tunnel01_lidar_imu.bag \
  /velodyne_points:=/velodyne_points_raw
python research_paper/experiments/src/finalize_t06.py \
  --run-dir research_paper/experiments/generated/runs/T06_full
```

The second run restarted FAST-LIO and the adapter/logger, preserving 130 seconds of pre-entry sensor history before the 168–174 second annotated entry. Its bag command added `-s 130`, its output directory was `generated/runs/T06_event_local`, and manifest finalization added `--start-seconds 130`. Exact command arrays and content hashes are in each run's `manifest.json`; backend/player resource files were captured with GNU `/usr/bin/time -v`. Reference data were absent from all online processes.

| Run | LiDAR clouds delivered | Valid poses | Backend peak RSS | Backend wall runtime | Backend warnings |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full stream (`T06_full`) | 2,857/2,857 | 2,852 | 270,860,288 B | 5:32.10 | 631; 627 say “No Effective Points” |
| Start at +130 s (`T06_event_local`) | 1,557/1,557 | 1,553 | 213,237,760 B | 3:19.39 | 3; none say “No Effective Points” |

Both players and backends exited with status 0 after the players finished and the ROS nodes were shut down. The full stream's estimate exceeds 1 km displacement at relative 128.5 s and ends about 158 km from its initial pose. The event-local estimate stays finite but covers only about 4.3 m from relative 244 to 284 s, while the released reference positions move about 264 m in that interval. This distance-only comparison is a gross diagnostic independent of world-frame alignment, not a formal T07 error metric. Reference body convention and calibration direction remain unverified. The run manifests' `completed` state means only that execution and stream coverage completed.

## Current limits

The GEODE trajectory has a long tunnel reference gap, so evaluation can use only covered intervals. GEODE does not publish sequence-level reference covariance or fix status. Backend body-frame and calibration direction must be established before interpreting formal pose error; no identity transform or post-event re-alignment is a substitute. Both development replays show motion-tracking failure, and no final-test or recovery claim is supported. After two attempts with the same gross under-tracking problem, parameter retries stopped pending scientific review of the backend/data choice. This sequence is development-only and cannot be used to tune final-test outcomes.

The offline evaluator is `src/trajectory_eval.py`. Its standard-library test runner is `python3 -m unittest discover -s research_paper/experiments/tests -v` from the repository root. With the retained inputs above, run `python3 research_paper/experiments/src/trajectory_eval.py --poses research_paper/experiments/generated/runs/T06_event_local/poses.csv --reference research_paper/experiments/generated/raw/geode/Urban_Tunnel01/reference/Urban_Tunnel01.txt --output research_paper/experiments/generated/runs/T06_event_local/evaluation.csv --run-id T06_event_local`; repeat with `T06_full` for the full replay. Both output streams contain zero valid formal local errors by design. The [T07 handoff](../execution/handoffs/T07.md) records counts and remaining acceptance gaps.
