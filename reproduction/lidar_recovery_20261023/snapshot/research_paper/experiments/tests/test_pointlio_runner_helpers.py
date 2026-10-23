import os
import signal
import subprocess
import unittest
from pathlib import Path


HELPER = (Path(__file__).resolve().parents[1] / "src" /
          "pointlio_runner_helpers.sh")


class PointLioRunnerHelperTests(unittest.TestCase):
    def call_recorder(self, command):
        script = (
            'source "$1"; point_manifest_written=false; '
            'point_python="$2"; point_recorder=/unused-recorder; '
            'point_run=/tmp/fixture; point_mode=on; point_run_state=RUN_FAILED; '
            'point_sensor_bag=/tmp/bag; point_config=/tmp/config; '
            'point_binary=/tmp/binary; point_workspace=/tmp/workspace; '
            'point_glog_prefix=/tmp/glog; point_repo_root=/tmp/repo; '
            'point_ros_master_uri=http://127.0.0.1:12345; '
            'point_bag_status=1; point_node_status=2; '
            'point_pose_logger_status=3; point_roscore_status=130; '
            'point_export_status=-2; '
            'set +e; point_write_manifest; status=$?; '
            'printf "%s %s\\n" "$status" '
            '"$point_manifest_written"'
        )
        return subprocess.run(
            ["bash", "-c", script, "runner-helper-test", str(HELPER), command],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    def test_recorder_failure_is_not_masked_by_successful_flag_assignment(self):
        self.assertEqual(self.call_recorder("/bin/false"), "1 false")

    def test_recorder_success_sets_the_manifest_written_flag(self):
        self.assertEqual(self.call_recorder("/bin/true"), "0 true")

    def test_point_process_alive_distinguishes_alive_dead_and_zombie(self):
        script = f"""
        source "{HELPER}"
        sleep 10 &
        alive_pid=$!
        res_alive=$(point_process_alive "$alive_pid" && echo yes || echo no)
        kill "$alive_pid" 2>/dev/null || true
        wait "$alive_pid" 2>/dev/null || true
        res_dead=$(point_process_alive "$alive_pid" && echo yes || echo no)
        res_nonexistent=$(point_process_alive 999999 && echo yes || echo no)
        printf "%s %s %s\\n" "$res_alive" "$res_dead" "$res_nonexistent"
        """
        out = subprocess.run(["bash", "-c", script], check=True,
                             capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, "yes no no")

    def test_child_cleanup_terminates_all_descendants(self):
        script = f"""
        source "{HELPER}"
        bash -c "sleep 100 & sleep 100 & wait" &
        parent=$!
        sleep 0.2
        children=$(pgrep -P "$parent" || true)
        point_stop_process "$parent" "parent" 1 INT
        parent_alive=$(point_process_alive "$parent" && echo alive || echo dead)
        any_child_alive=no
        for c in $children; do
          if point_process_alive "$c"; then any_child_alive=yes; fi
        done
        printf "%s %s\\n" "$parent_alive" "$any_child_alive"
        """
        out = subprocess.run(["bash", "-c", script], check=True,
                             capture_output=True, text=True).stdout.strip()
        self.assertEqual(out, "dead no")

    def test_point_stop_process_escalates_to_sigterm_if_sigint_ignored(self):
        script = f"""
        source "{HELPER}"
        bash -c 'trap "" INT; sleep 100' &
        pid=$!
        sleep 0.2
        point_stop_process "$pid" "ignoring-proc" 1 INT
        status=$?
        alive=$(point_process_alive "$pid" && echo alive || echo dead)
        printf "%s %s\\n" "$status" "$alive"
        """
        out = subprocess.run(["bash", "-c", script], check=True,
                             stdout=subprocess.PIPE, text=True,
                             stderr=subprocess.DEVNULL).stdout.strip()
        status, alive = out.split()
        self.assertEqual(alive, "dead")
        self.assertNotEqual(status, "0")

    def test_runner_interruption_stops_bag_and_records_run_failed(self):
        runner_script = f"""
        source "{HELPER}"
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

        point_run_recorder() {{
          printf "MANIFEST state=%s bag=%s node=%s\\n" "$point_run_state" "$point_bag_status" "$point_node_status"
          point_manifest_written=true
          return 0
        }}
        point_write_manifest() {{
          point_run_recorder
        }}

        cleanup() {{
          local point_original_status=$?
          trap - EXIT INT TERM
          set +e
          if [[ -n "$point_bag_pid" && $point_bag_status -lt 0 ]]; then
            point_stop_process "$point_bag_pid" "rosbag" 2 INT
            point_bag_status=$?
          fi
          if [[ -n "$point_lio_pid" && $point_node_status -lt 0 ]]; then
            point_stop_process "$point_lio_pid" "Point-LIO" 2 INT
            point_node_status=$?
          fi
          set -e
          if [[ "$point_manifest_written" != true ]]; then
            if [[ "$point_run_state" == RUNNING || $point_original_status -ne 0 ]]; then
              point_run_state=RUN_FAILED
            fi
            point_write_manifest
          fi
          exit "$point_original_status"
        }}
        trap cleanup EXIT INT TERM

        sleep 100 &
        point_lio_pid=$!
        bash -c "sleep 100 & wait" &
        point_bag_pid=$!

        printf "READY %d %d\\n" "$point_lio_pid" "$point_bag_pid"
        wait "$point_bag_pid"
        """

        proc = subprocess.Popen(["bash", "-c", runner_script],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        try:
            line = proc.stdout.readline()
            self.assertTrue(line.startswith("READY"))
            parts = line.strip().split()
            lio_pid, bag_pid = int(parts[1]), int(parts[2])

            proc.send_signal(signal.SIGINT)
            stdout, stderr = proc.communicate(timeout=5)

            self.assertIn("state=RUN_FAILED", stdout)
            self.assertFalse(self._pid_exists(lio_pid))
            self.assertFalse(self._pid_exists(bag_pid))
        finally:
            if proc.poll() is None:
                proc.kill()
                proc.communicate()

    def _pid_exists(self, pid: int) -> bool:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


if __name__ == "__main__":
    unittest.main()
