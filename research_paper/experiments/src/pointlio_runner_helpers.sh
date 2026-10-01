#!/usr/bin/env bash

point_process_alive() {
  local point_pid=$1
  local point_process_state
  [[ -n "$point_pid" ]] || return 1
  point_process_state=$(ps -o stat= -p "$point_pid" 2>/dev/null) || return 1
  point_process_state=${point_process_state//[[:space:]]/}
  [[ -n "$point_process_state" && "$point_process_state" != Z* ]]
}

point_kill_tree() {
  local point_target_pid=$1
  local point_sig=${2:-INT}
  local point_child
  local point_children
  local point_target_pgid
  local point_my_pgid

  point_target_pgid=$(ps -o pgid= -p "$point_target_pid" 2>/dev/null | tr -d ' ' || true)
  point_my_pgid=$(ps -o pgid= -p $$ 2>/dev/null | tr -d ' ' || true)
  if [[ -n "$point_target_pgid" && "$point_target_pgid" != "$point_my_pgid" && "$point_target_pgid" -gt 1 ]]; then
    kill -"$point_sig" -"$point_target_pgid" 2>/dev/null || true
  fi

  point_children=$(pgrep -P "$point_target_pid" 2>/dev/null || true)
  for point_child in $point_children; do
    point_kill_tree "$point_child" "$point_sig"
  done
  kill -"$point_sig" "$point_target_pid" 2>/dev/null || true
}

point_stop_process() {
  local point_pid=$1
  local point_name=$2
  local point_grace=$3
  local point_signal=${4:-INT}
  local point_deadline
  local point_status
  [[ -n "$point_pid" ]] || return 0

  if point_process_alive "$point_pid"; then
    point_kill_tree "$point_pid" "$point_signal"
  fi
  point_deadline=$((SECONDS + point_grace))
  while point_process_alive "$point_pid" && (( SECONDS < point_deadline )); do
    sleep 0.1
  done
  if point_process_alive "$point_pid"; then
    echo "$point_name did not stop after SIG$point_signal; escalating to SIGTERM" >&2
    point_kill_tree "$point_pid" TERM
    point_deadline=$((SECONDS + 5))
    while point_process_alive "$point_pid" && (( SECONDS < point_deadline )); do
      sleep 0.1
    done
  fi
  if point_process_alive "$point_pid"; then
    echo "$point_name did not stop after SIGTERM; escalating to SIGKILL" >&2
    point_kill_tree "$point_pid" KILL
    point_deadline=$((SECONDS + 2))
    while point_process_alive "$point_pid" && (( SECONDS < point_deadline )); do
      sleep 0.1
    done
    if point_process_alive "$point_pid"; then
      echo "$point_name remains present after SIGKILL; not waiting indefinitely" >&2
      return 137
    fi
  fi
  if wait "$point_pid" 2>/dev/null; then point_status=0; else point_status=$?; fi
  return "$point_status"
}

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
