#!/usr/bin/env bash
# Short, development-only Hilti FAST-LIO replay for T08 export/parity checks.
set -euo pipefail

if [[ $# -ne 4 ]]; then
  echo 'usage: run_hilti_health_smoke.sh WORKSPACE RUN_DIR DURATION_SECONDS on|off' >&2
  exit 2
fi
health_ws=$1
health_run=$2
health_duration=$3
health_mode=$4
if [[ $health_mode != on && $health_mode != off ]]; then
  echo 'health mode must be on or off' >&2
  exit 2
fi
if [[ -e $health_run ]]; then
  echo "run directory already exists: $health_run" >&2
  exit 2
fi

hilti_root=/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18
hilti_env="$hilti_root/ros_env"
hilti_bag="$hilti_root/exp18_corridor_lower_gallery_2.bag"
mkdir -p "$health_run"

export CONDA_PREFIX="$hilti_env"
export PATH="$hilti_env/bin:$PATH"
set +u
source "$hilti_env/etc/conda/activate.d/ros-noetic-catkin_activate.sh"
source "$health_ws/devel/setup.bash"
set -u

health_pids=()
cleanup() {
  for health_pid in "${health_pids[@]}"; do kill -TERM "$health_pid" 2>/dev/null || true; done
  for health_pid in "${health_pids[@]}"; do wait "$health_pid" 2>/dev/null || true; done
}
trap cleanup EXIT

roscore >"$health_run/roscore.log" 2>&1 &
health_pids+=("$!")
for health_attempt in {1..30}; do
  if rosparam list >/dev/null 2>&1; then break; fi
  sleep 1
done
rosparam set /use_sim_time true
rosparam load research_paper/configs/fastlio_hilti_exp18_exploratory.yaml
if [[ $health_mode == on ]]; then
  rosparam set /health/diagnostic_csv "$health_run/health.csv"
fi

rosrun fast_lio fastlio_mapping >"$health_run/fastlio.log" 2>&1 &
health_pids+=("$!")
python3 research_paper/experiments/src/hesai_time_adapter.py \
  --input-topic /hesai/pandar --output-topic /velodyne_points \
  >"$health_run/adapter.log" 2>&1 &
health_pids+=("$!")
python3 research_paper/experiments/src/pose_logger.py \
  --clock-id hilti_ros_header_unix --output "$health_run/poses.csv" \
  >"$health_run/pose_logger.log" 2>&1 &
health_pids+=("$!")
sleep 3

rosbag play -q --clock -r 1 -u "$health_duration" --wait-for-subscribers \
  "$hilti_bag" --topics /hesai/pandar /alphasense/imu \
  >"$health_run/rosbag.log" 2>&1
sleep 3
cleanup
trap - EXIT
printf 'run_dir=%s\n' "$health_run"
printf 'pose_rows=%s\n' "$(wc -l < "$health_run/poses.csv")"
if [[ $health_mode == on ]]; then
  printf 'health_rows=%s\n' "$(wc -l < "$health_run/health.csv")"
fi
