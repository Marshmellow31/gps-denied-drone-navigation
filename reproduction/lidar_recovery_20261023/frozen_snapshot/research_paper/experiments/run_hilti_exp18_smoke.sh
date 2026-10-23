#!/usr/bin/env bash
# One development-only Hilti Exp18 replay, first 55 s including transition.
set -euo pipefail

hilti_root=/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18
hilti_env="$hilti_root/ros_env"
hilti_ws="$hilti_root/fastlio_ws"
hilti_run="$hilti_root/runs/exp18_first55_exploratory"
hilti_bag="$hilti_root/exp18_corridor_lower_gallery_2.bag"
mkdir -p "$hilti_run"

export CONDA_PREFIX="$hilti_env"
export PATH="$hilti_env/bin:$PATH"
set +u
source "$hilti_env/etc/conda/activate.d/ros-noetic-catkin_activate.sh"
source "$hilti_ws/devel/setup.bash"
set -u

hilti_pids=()
cleanup() {
  for hilti_pid in "${hilti_pids[@]}"; do
    kill "$hilti_pid" 2>/dev/null || true
  done
  for hilti_pid in "${hilti_pids[@]}"; do
    wait "$hilti_pid" 2>/dev/null || true
  done
}
trap cleanup EXIT

roscore >"$hilti_run/roscore.log" 2>&1 &
hilti_pids+=("$!")
for hilti_attempt in {1..30}; do
  if rosparam list >/dev/null 2>&1; then break; fi
  sleep 1
done
rosparam set /use_sim_time true
rosparam load research_paper/configs/fastlio_hilti_exp18_exploratory.yaml

rosrun fast_lio fastlio_mapping >"$hilti_run/fastlio.log" 2>&1 &
hilti_pids+=("$!")
python3 research_paper/experiments/src/hesai_time_adapter.py \
  --input-topic /hesai/pandar --output-topic /velodyne_points \
  >"$hilti_run/adapter.log" 2>&1 &
hilti_pids+=("$!")
python3 research_paper/experiments/src/pose_logger.py \
  --clock-id hilti_ros_header_unix --output "$hilti_run/poses.csv" \
  >"$hilti_run/pose_logger.log" 2>&1 &
hilti_pids+=("$!")
sleep 3

rosbag play -q --clock -r 1 -u 55 --wait-for-subscribers \
  "$hilti_bag" --topics /hesai/pandar /alphasense/imu \
  >"$hilti_run/rosbag.log" 2>&1
sleep 3
printf 'run_dir=%s\n' "$hilti_run"
printf 'pose_rows=%s\n' "$(wc -l < "$hilti_run/poses.csv")"
