#!/usr/bin/env bash
# One Point-LIO T15 development replay. Truth is consumed only afterward offline.
set -euo pipefail
if [[ $# != 5 ]]; then
  echo 'usage: run_point_lio_smoke.sh ROS_ENV CATKIN_WORKSPACE SENSOR_BAG CONFIG NEW_RUN_DIR' >&2
  exit 2
fi
point_ros_env=$1
point_workspace=$2
point_sensor_bag=$3
point_config=$4
point_run=$5
[[ ! -e "$point_run" ]] || { echo 'output exists' >&2; exit 2; }
[[ -f "$point_sensor_bag" && -f "$point_config" ]] || { echo 'input/config missing' >&2; exit 2; }
mkdir -p "$point_run"
export CONDA_PREFIX="$point_ros_env"
export PATH="$point_ros_env/bin:$PATH"
set +u
source "$point_ros_env/etc/conda/activate.d/ros-noetic-catkin_activate.sh"
source "$point_workspace/devel/setup.bash"
set -u
point_pids=()
cleanup() {
  for point_pid in "${point_pids[@]}"; do kill -TERM "$point_pid" 2>/dev/null || true; done
  for point_pid in "${point_pids[@]}"; do wait "$point_pid" 2>/dev/null || true; done
}
trap cleanup EXIT
roscore >"$point_run/roscore.log" 2>&1 &
point_pids+=("$!")
point_ros_ready=false
for point_attempt in {1..30}; do
  if rosparam list >/dev/null 2>&1; then point_ros_ready=true; break; fi
  sleep 1
done
if [[ "$point_ros_ready" != true ]]; then
  echo 'ROS master did not become ready within 30 seconds' >&2
  exit 1
fi
rosparam set /use_sim_time true
# Point-LIO constructs its NodeHandle as `~`, so settings must live below
# its default ROS node name (`/laserMapping`), not at the global root.
rosparam load "$point_config" /laserMapping
rosparam get /laserMapping/mapping/gravity >/dev/null
rosrun point_lio pointlio_mapping >"$point_run/point_lio.log" 2>&1 &
point_lio_pid=$!
point_pids+=("$point_lio_pid")
python3 research_paper/experiments/src/pose_logger.py \
  --clock-id simulation_epoch \
  --topic /aft_mapped_to_init \
  --output "$point_run/poses.csv" >"$point_run/pose_logger.log" 2>&1 &
point_pids+=("$!")
sleep 3
if ! kill -0 "$point_lio_pid" 2>/dev/null; then
  echo 'Point-LIO exited before bag playback; see point_lio.log' >&2
  exit 1
fi
timeout 120 rosbag play -q --clock -r 1 --wait-for-subscribers "$point_sensor_bag" \
  --topics /sim/points /sim/imu >"$point_run/rosbag.log" 2>&1
python3 - "$point_sensor_bag" <<'PY'
import sys, time
import rosbag, rospy
from rosgraph_msgs.msg import Clock
with rosbag.Bag(sys.argv[1]) as bag:
    end_time = bag.get_end_time()
rospy.init_node('point_lio_simulation_clock_drain', anonymous=True)
publisher = rospy.Publisher('/clock', Clock, queue_size=1)
time.sleep(.5)
for extra in (.25, .5, .75, 1.0):
    publisher.publish(Clock(clock=rospy.Time.from_sec(end_time + extra)))
    time.sleep(.25)
PY
sleep 3
if ! kill -0 "$point_lio_pid" 2>/dev/null; then
  echo 'Point-LIO exited during replay; see point_lio.log' >&2
  exit 1
fi
cleanup
trap - EXIT
python3 - "$point_run/poses.csv" <<'PY'
import csv, sys
from pathlib import Path

path = Path(sys.argv[1])
with path.open(newline="", encoding="utf-8") as stream:
    reader = csv.DictReader(stream)
    if not {"timestamp_ns", "valid", "event"}.issubset(reader.fieldnames or ()):
        raise SystemExit("pose output is missing required common-contract columns")
    rows = list(reader)
if not rows:
    raise SystemExit("Point-LIO produced no pose records")
print(f"Point-LIO pose records: {len(rows)}")
PY
