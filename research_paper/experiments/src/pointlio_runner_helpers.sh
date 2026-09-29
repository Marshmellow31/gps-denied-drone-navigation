#!/usr/bin/env bash

# Record a manifest command without masking its exit status with a later
# assignment. The runner and shell fixture share this exact function.
point_run_recorder() {
  local point_python=$1
  local point_recorder=$2
  shift 2
  if "$point_python" "$point_recorder" "$@"; then
    point_manifest_written=true
    return 0
  else
    local point_status=$?
    point_manifest_written=false
    return "$point_status"
  fi
}

point_write_manifest() {
  local point_manifest_args=(
    --run-dir "$point_run" --mode "$point_mode" --state "$point_run_state"
    --input-bag "$point_sensor_bag" --config "$point_config"
    --binary "$point_binary" --source-root "$point_workspace/src/point_lio"
    --glog-prefix "$point_glog_prefix" --repo-root "$point_repo_root"
    --ros-master-uri "$point_ros_master_uri"
    --rosbag-status "$point_bag_status" --node-status "$point_node_status"
    --pose-logger-status "$point_pose_logger_status"
    --roscore-status "$point_roscore_status"
    --exporter-status "$point_export_status"
  )
  point_run_recorder "$point_python" "$point_recorder" "${point_manifest_args[@]}"
}
