#!/usr/bin/env bash
# Retained seed-14 development replay with the Point-LIO sidecar on or off.
set -euo pipefail

if [[ $# != 7 ]]; then
  echo 'usage: run_point_lio_indicator_feasibility.sh ROS_ENV CATKIN_WORKSPACE GLOG_PREFIX SENSOR_BAG CONFIG NEW_RUN_DIR on|off' >&2
  exit 2
fi

point_ros_env=$1
point_workspace=$2
point_glog_prefix=$3
point_sensor_bag=$4
point_config=$5
point_run=$6
point_mode=$7
point_repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
point_runner_helper="$point_repo_root/research_paper/experiments/src/pointlio_runner_helpers.sh"
source "$point_runner_helper"
point_binary="$point_workspace/devel/lib/point_lio/pointlio_mapping"
point_source="$point_workspace/src/point_lio"
point_sidecar="$point_run/sidecar"
point_expected_bag="$point_repo_root/research_paper/experiments/generated/t14_retained_inputs/T14_FORMAL_DEV14_CORRIDOR_INPUT_XM6_V1/sensors.bag"
point_expected_bag_sha256=89f4ac21b24a2b9dfc86b74cd3d082e48365ac1ed63207b08969e7aca25d4627
point_expected_config_sha256=d23bd8799c3834ac0acc1d23476a0a0c0cd72b09f7b7c542b5bfbe9813a4c98b
point_expected_source_commit=4b86a469eb5572e70ed575af25b5f15dd06e8e3c

[[ "$point_mode" == "on" || "$point_mode" == "off" ]] || { echo 'mode must be on or off' >&2; exit 2; }
[[ ! -e "$point_run" ]] || { echo 'output directory already exists' >&2; exit 2; }
[[ -x "$point_binary" && -f "$point_sensor_bag" && -f "$point_config" ]] || { echo 'binary, input bag, or config missing' >&2; exit 2; }
[[ -f "$point_glog_prefix/include/glog/logging.h" ]] || { echo 'glog overlay is missing' >&2; exit 2; }
[[ -x "$point_ros_env/bin/python3" ]] || { echo 'ROS environment Python is missing' >&2; exit 2; }
point_ros_master_port=$("$point_ros_env/bin/python3" -c 'import socket; s=socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1]); s.close()')
point_ros_master_uri="http://127.0.0.1:$point_ros_master_port"
[[ -f "$point_expected_bag" ]] || { echo 'retained seed-14 feasibility bag is missing' >&2; exit 2; }
point_actual_bag_path=$(realpath "$point_sensor_bag")
point_expected_bag_path=$(realpath "$point_expected_bag")
[[ "$point_actual_bag_path" == "$point_expected_bag_path" ]] || { echo 'this runner accepts only the retained seed-14 corridor bag' >&2; exit 2; }
point_actual_bag_sha256=$(sha256sum "$point_sensor_bag" | cut -d' ' -f1)
point_actual_config_sha256=$(sha256sum "$point_config" | cut -d' ' -f1)
point_actual_source_commit=$(git -C "$point_source" rev-parse HEAD)
[[ "$point_actual_bag_sha256" == "$point_expected_bag_sha256" ]] || { echo 'input is not the retained seed-14 corridor bag' >&2; exit 2; }
[[ "$point_actual_config_sha256" == "$point_expected_config_sha256" ]] || { echo 'Point-LIO config does not match the frozen development profile' >&2; exit 2; }
[[ "$point_actual_source_commit" == "$point_expected_source_commit" ]] || { echo 'Point-LIO source revision does not match the pinned T15 revision' >&2; exit 2; }
[[ -f "$point_source/src/IndicatorSidecar.cpp" && -f "$point_source/src/IndicatorSidecar.h" ]] || { echo 'native indicator sidecar patch is not applied' >&2; exit 2; }

mkdir -p "$point_run"
point_run_state=RUNNING
point_bag_status=-1
point_node_status=-1
point_pose_logger_status=-1
point_roscore_status=-1
point_export_status=-2
point_manifest_written=false
point_roscore_pid=
point_lio_pid=
point_pose_logger_pid=
point_bag_pid=
point_python="$point_ros_env/bin/python3"
point_recorder="$point_repo_root/research_paper/experiments/src/record_pointlio_attempt.py"

cleanup() {
  local point_original_status=$?
  local point_manifest_status
  trap - EXIT INT TERM
  set +e
  if [[ -n "$point_bag_pid" && $point_bag_status -lt 0 ]]; then
    point_stop_process "$point_bag_pid" "rosbag" 5 INT
    point_bag_status=$?
  fi
  if [[ -n "$point_lio_pid" && $point_node_status -lt 0 ]]; then
    point_stop_process "$point_lio_pid" "Point-LIO" 20 INT
    point_node_status=$?
  fi
  if [[ -n "$point_pose_logger_pid" && $point_pose_logger_status -lt 0 ]]; then
    point_stop_process "$point_pose_logger_pid" "pose logger" 10 INT
    point_pose_logger_status=$?
  fi
  if [[ -n "$point_roscore_pid" && $point_roscore_status -lt 0 ]]; then
    point_stop_process "$point_roscore_pid" "roscore" 5 INT
    point_roscore_status=$?
  fi
  set -e
  if [[ "$point_manifest_written" != true ]]; then
    if [[ "$point_run_state" == RUNNING || $point_original_status -ne 0 ]]; then
      point_run_state=RUN_FAILED
    fi
    set +e
    point_write_manifest
    point_manifest_status=$?
    set -e
    if (( point_manifest_status != 0 )); then
      echo "could not persist final attempt manifest for $point_run" >&2
      if (( point_original_status == 0 )); then point_original_status=1; fi
    fi
  fi
  exit "$point_original_status"
}
trap cleanup EXIT INT TERM
point_write_manifest
point_manifest_written=false
if [[ "$point_mode" == "on" ]]; then mkdir -p "$point_sidecar"; fi
export CONDA_PREFIX="$point_ros_env"
export PATH="$point_ros_env/bin:$PATH"
export CPATH="$point_glog_prefix/include${CPATH:+:$CPATH}"
export LIBRARY_PATH="$point_glog_prefix/lib${LIBRARY_PATH:+:$LIBRARY_PATH}"
export LD_LIBRARY_PATH="$point_glog_prefix/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
set +u
source "$point_ros_env/etc/conda/activate.d/ros-noetic-catkin_activate.sh"
source "$point_workspace/devel/setup.bash"
set -u
export ROS_MASTER_URI="$point_ros_master_uri"
export ROS_IP=127.0.0.1
unset ROS_HOSTNAME

"$point_python" "$point_repo_root/research_paper/experiments/src/audit_pointlio_input_frames.py" --bag "$point_sensor_bag" --output "$point_run/input_header_stamps.csv" >"$point_run/input_audit.log" 2>&1
point_write_manifest
point_manifest_written=false
roscore -p "$point_ros_master_port" >"$point_run/roscore.log" 2>&1 &
point_roscore_pid=$!
point_ros_ready=false
for point_attempt in {1..30}; do
  kill -0 "$point_roscore_pid" 2>/dev/null || { echo 'the isolated ROS master process exited during startup' >&2; exit 1; }
  if rosparam list >/dev/null 2>&1; then point_ros_ready=true; break; fi
  sleep 1
done
[[ "$point_ros_ready" == true ]] || { echo 'ROS master did not start' >&2; exit 1; }
kill -0 "$point_roscore_pid" 2>/dev/null || { echo 'the isolated ROS master exited after readiness' >&2; exit 1; }

rosparam set /use_sim_time true
rosparam load "$point_config" /laserMapping
rosparam get /laserMapping/mapping/gravity >/dev/null
if [[ "$point_mode" == "on" ]]; then
  rosparam set /laserMapping/indicator_sidecar_dir "$point_sidecar"
else
  rosparam set /laserMapping/indicator_sidecar_dir ""
fi

"$point_binary" >"$point_run/point_lio.log" 2>&1 &
point_lio_pid=$!
"$point_python" "$point_repo_root/research_paper/experiments/src/pointlio_pose_logger.py" --clock-id simulation_epoch --topic /aft_mapped_to_init --output "$point_run/poses.csv" >"$point_run/pose_logger.log" 2>&1 &
point_pose_logger_pid=$!
sleep 3
point_process_alive "$point_lio_pid" || { echo 'Point-LIO exited before playback' >&2; exit 1; }
point_process_alive "$point_pose_logger_pid" || { echo 'pose logger exited before playback' >&2; exit 1; }

set +e
rosbag play -q --clock -r 1 --wait-for-subscribers "$point_sensor_bag" --topics /sim/points /sim/imu >"$point_run/rosbag.log" 2>&1 &
point_bag_pid=$!

point_bag_deadline=$((SECONDS + 120))
while point_process_alive "$point_bag_pid"; do
  if ! point_process_alive "$point_lio_pid"; then
    echo "Point-LIO exited unexpectedly during playback" >&2
    point_stop_process "$point_bag_pid" "rosbag" 5 INT
    point_bag_status=1
    break
  fi
  if ! point_process_alive "$point_pose_logger_pid"; then
    echo "pose logger exited unexpectedly during playback" >&2
    point_stop_process "$point_bag_pid" "rosbag" 5 INT
    point_bag_status=1
    break
  fi
  if ! point_process_alive "$point_roscore_pid"; then
    echo "roscore exited unexpectedly during playback" >&2
    point_stop_process "$point_bag_pid" "rosbag" 5 INT
    point_bag_status=1
    break
  fi
  if (( SECONDS >= point_bag_deadline )); then
    echo "rosbag playback timed out after 120s" >&2
    point_stop_process "$point_bag_pid" "rosbag" 5 INT
    point_bag_status=124
    break
  fi
  sleep 0.2
done
if [[ $point_bag_status -lt 0 ]]; then
  if wait "$point_bag_pid" 2>/dev/null; then
    point_bag_status=0
  else
    point_bag_status=$?
  fi
fi
set -e
if [[ $point_bag_status == 0 ]]; then
  "$point_python" "$point_repo_root/research_paper/experiments/src/drain_sim_clock.py" --bag "$point_sensor_bag" >"$point_run/clock_drain.log" 2>&1
fi

# SIGINT sets a signal-safe stop flag; WallRate lets the loop reach its flush.
set +e
point_stop_process "$point_lio_pid" "Point-LIO" 20 INT
point_node_status=$?
point_stop_process "$point_pose_logger_pid" "pose logger" 10 INT
point_pose_logger_status=$?
point_stop_process "$point_roscore_pid" "roscore" 5 INT
point_roscore_status=$?
set -e

if [[ "$point_mode" == "on" && $point_bag_status == 0 && $point_node_status == 0 && $point_pose_logger_status == 0 ]]; then
  set +e
  "$point_python" "$point_repo_root/research_paper/experiments/src/pointlio_indicator_export.py" --frame-ledger "$point_sidecar/frame_ledger.csv" --group-ledger "$point_sidecar/measurement_groups.csv" --jacobian-rows "$point_sidecar/jacobian_rows.csv" --expected-header-stamps "$point_run/input_header_stamps.csv" --poses "$point_run/poses.csv" --reset-events "$point_sidecar/reset_events.csv" --output "$point_run/pointlio_indicators.csv" --segmented-poses "$point_run/poses_segmented.csv"
  point_export_status=$?
  set -e
fi

if [[ $point_bag_status != 0 || $point_node_status != 0 || $point_pose_logger_status != 0 || ( $point_roscore_status != 0 && $point_roscore_status != 130 ) || ( $point_export_status != 0 && $point_export_status != -2 ) ]]; then
  point_run_state=RUN_FAILED
  point_write_manifest
  echo "incomplete attempt (rosbag=$point_bag_status Point-LIO=$point_node_status); outputs retained at $point_run" >&2
  exit 1
fi
point_run_state=COMPLETED
point_write_manifest
trap - EXIT INT TERM
echo "Point-LIO $point_mode feasibility replay completed; output: $point_run"
