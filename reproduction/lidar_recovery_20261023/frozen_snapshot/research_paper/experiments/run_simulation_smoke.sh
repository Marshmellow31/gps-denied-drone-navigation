#!/usr/bin/env bash
# Isolated development bootstrap. Sensor bag contains no reference trajectory.
set -euo pipefail
if [[ $# != 4 ]]; then
  echo 'usage: run_simulation_smoke.sh ROS_ENV WORKSPACE SENSOR_BAG NEW_RUN_DIR' >&2
  exit 2
fi
sim_env=$1
sim_ws=$2
sim_bag=$3
sim_run=$4
[[ ! -e "$sim_run" ]] || { echo 'output exists' >&2; exit 2; }
mkdir -p "$sim_run"
export CONDA_PREFIX="$sim_env"
export PATH="$sim_env/bin:$PATH"
set +u
source "$sim_env/etc/conda/activate.d/ros-noetic-catkin_activate.sh"
source "$sim_ws/devel/setup.bash"
set -u
sim_pids=()
cleanup() {
  for sim_pid in "${sim_pids[@]}"; do kill -TERM "$sim_pid" 2>/dev/null || true; done
  for sim_pid in "${sim_pids[@]}"; do wait "$sim_pid" 2>/dev/null || true; done
}
trap cleanup EXIT
roscore >"$sim_run/roscore.log" 2>&1 &
sim_pids+=("$!")
for sim_attempt in {1..30}; do
  if rosparam list >/dev/null 2>&1; then break; fi
  sleep 1
done
rosparam set /use_sim_time true
rosparam load research_paper/configs/fastlio_simulation_bootstrap.yaml
rosparam set /health/diagnostic_csv "$sim_run/health.csv"
rosrun fast_lio fastlio_mapping >"$sim_run/fastlio.log" 2>&1 &
sim_pids+=("$!")
python3 research_paper/experiments/src/pose_logger.py --clock-id simulation_epoch \
  --output "$sim_run/poses.csv" >"$sim_run/pose_logger.log" 2>&1 &
sim_pids+=("$!")
sleep 3
rosbag play -q --clock -r 1 --wait-for-subscribers "$sim_bag" \
  --topics /sim/points /sim/imu >"$sim_run/rosbag.log" 2>&1
python3 - "$sim_bag" <<'PY'
import sys, time
import rosbag, rospy
from rosgraph_msgs.msg import Clock
with rosbag.Bag(sys.argv[1]) as bag: end = bag.get_end_time()
rospy.init_node('simulation_clock_drain', anonymous=True)
publisher = rospy.Publisher('/clock', Clock, queue_size=1)
time.sleep(.5)
for extra in (.25, .5, .75, 1.):
    publisher.publish(Clock(clock=rospy.Time.from_sec(end + extra)))
    time.sleep(.25)
PY
sleep 3
cleanup
trap - EXIT
wc -l "$sim_run/poses.csv" "$sim_run/health.csv"
