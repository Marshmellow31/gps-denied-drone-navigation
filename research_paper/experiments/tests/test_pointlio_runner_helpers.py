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


if __name__ == "__main__":
    unittest.main()
