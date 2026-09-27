#!/usr/bin/env bash
# Rebuild the frozen backend in a new workspace; never modifies retained upstream.
set -euo pipefail
[[ $# == 2 ]] || { echo 'usage: restore_fastlio_workspace.sh ROS_ENV NEW_WORKSPACE' >&2; exit 2; }
restore_env=$1
restore_ws=$2
restore_repo=$(cd "$(dirname "$0")/../.." && pwd)
[[ ! -e "$restore_ws" ]] || { echo 'workspace already exists; refusing overwrite' >&2; exit 2; }
mkdir -p "$restore_ws/src"
git clone --no-hardlinks --recurse-submodules \
  "$restore_repo/research_paper/experiments/generated/upstream/FAST_LIO" "$restore_ws/src/fast_lio"
git -C "$restore_ws/src/fast_lio" checkout 7cc4175de6f8ba2edf34bab02a42195b141027e9
for restore_patch in fast_lio_pcl17.patch fast_lio_health_diagnostic.patch fast_lio_hessian_sidecar.patch fast_lio_cmake_final_newline.patch; do
  git -C "$restore_ws/src/fast_lio" apply "$restore_repo/research_paper/experiments/patches/$restore_patch"
done
restore_diff=$(git -C "$restore_ws/src/fast_lio" diff HEAD --binary | sha256sum | cut -d' ' -f1)
[[ "$restore_diff" == 1397219a8765c2bc8c49adaf7e94dcc1e6006788acac06467e28e660876e51a0 ]] || {
  echo "source diff differs from T14: $restore_diff" >&2; exit 2;
}
ln -s "$restore_repo/research_paper/experiments/ros/livox_ros_driver" "$restore_ws/src/livox_ros_driver"
export CONDA_PREFIX="$restore_env"
export PATH="$restore_env/bin:$PATH"
set +u
source "$restore_env/etc/conda/activate.d/ros-noetic-catkin_activate.sh"
set -u
catkin config --workspace "$restore_ws" --cmake-args \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_BUILD_TYPE=Release
catkin build --workspace "$restore_ws" livox_ros_driver -j 1 --no-status
# Upstream omits a dependency edge from its executable to its generated header.
# Generate the declared messages first without changing the frozen source.
catkin build --workspace "$restore_ws" fast_lio --no-deps --no-status \
  --make-args fast_lio_generate_messages
catkin build --workspace "$restore_ws" -j 1 --no-status
sha256sum "$restore_ws/devel/.private/fast_lio/lib/fast_lio/fastlio_mapping"
