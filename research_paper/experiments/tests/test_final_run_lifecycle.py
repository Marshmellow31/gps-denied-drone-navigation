"""Lifecycle fixtures use development-shaped data; no reserved layout is sampled."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import final_evaluation_runner as runner
import run_r3_development_validation as validation


def write_csv(path, fields, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def complete_streams(path, invalid=0):
    path.mkdir(parents=True, exist_ok=True)
    times = [1_000_000_000_000 + (i+1)*100_000_000 for i in range(600)]
    write_csv(path / "health.csv", ["timestamp_ns", "lever_scale_m"],
              [{"timestamp_ns": t, "lever_scale_m": scale} for t in times for scale in (1, 3, 5)])
    write_csv(path / "dcreg.csv", ["timestamp_ns"], [{"timestamp_ns": t} for t in times])
    poses = [{"timestamp_ns": t, "event": "POSE", "segment_id": 0,
              "valid": "false" if i < invalid else "true"} for i, t in enumerate(times[3:])]
    write_csv(path / "poses.csv", ["timestamp_ns", "event", "segment_id", "valid"], poses)
    write_csv(path / "evaluation.csv", ["timestamp_ns", "window_s"],
              [{"timestamp_ns": p["timestamp_ns"], "window_s": w} for p in poses for w in (1, 3)])
    (path / "health.csv.hessian.csv").write_text("raw fixture; Hessian mathematics tested separately\n")
    (path / "rosbag.log").write_text("Done.\n")
    (path / "pose_logger.log").write_text("pose logger counts: " + repr({
        "valid": len(poses)-invalid, "invalid": invalid, "resets": 0}) + "\n")
    return [{"timestamp_groups": 600, "row_counts": {"VALID": 1800}},
            {"rows": 600, "valid": 0, "unavailable": 600},
            {"rows": len(poses)*2, "local_valid": 0, "reference_gaps": 0,
             "out_of_order_source_rows": 0, "body_transform_verified": True}]


class CompletionValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary.name)
        self.summaries = complete_streams(self.path, invalid=200)

    def tearDown(self):
        self.temporary.cleanup()

    def validate(self):
        return runner.validate_completed_streams(self.path, {"scans": 600}, *self.summaries)

    def test_complete_unfavorable_and_unavailable_estimates_are_accounted(self):
        result = self.validate()
        self.assertEqual(result["invalid_pose_records"], 200)
        self.assertEqual(result["evaluation_rows"], 1194)

    def test_header_only_pose_stream_is_incomplete(self):
        write_csv(self.path / "poses.csv", ["timestamp_ns", "event"], [])
        with self.assertRaises(runner.RunIncompleteError):
            self.validate()

    def test_partial_groups_are_incomplete_even_with_successful_wrapper(self):
        self.summaries[0]["timestamp_groups"] = 200
        with self.assertRaises(runner.RunIncompleteError):
            self.validate()

    def test_early_backend_exit_prefix_is_incomplete(self):
        rows = runner._read_tsv_or_csv(self.path / "poses.csv")[:100]
        write_csv(self.path / "poses.csv", list(rows[0]), rows)
        with self.assertRaises(runner.RunIncompleteError):
            self.validate()

    def test_missing_playback_completion_is_incomplete(self):
        (self.path / "rosbag.log").write_text("playback terminated\n")
        with self.assertRaises(runner.RunIncompleteError):
            self.validate()

    def test_truncated_evaluation_is_incomplete(self):
        (self.path / "evaluation.csv").write_text("timestamp_ns,window_s\n")
        with self.assertRaises(runner.RunIncompleteError):
            self.validate()

    def test_development_smoke_rejects_other_data_before_backend_access(self):
        (self.path / "manifest.json").write_text(json.dumps({"role": "heldout", "seed": 100, "control": False}))
        arguments = ["validation", "--ros-env", str(self.path / "ros"),
                     "--workspace", str(self.path / "ws"), "--input-dir", str(self.path),
                     "--run-root", str(self.path / "runs"), "--run-id", "fixture",
                     "--output-manifest", str(self.path / "result.json")]
        with patch.object(sys, "argv", arguments), patch.object(runner, "_check_backend") as backend:
            with self.assertRaises(runner.FinalEvaluationError):
                validation.main()
            backend.assert_not_called()
        self.assertFalse((self.path / "runs").exists())


class ReplayLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.inputs = self.root / "input"
        self.inputs.mkdir()
        (self.inputs / "sensors.bag").write_bytes(b"development-shaped fixture")
        (self.inputs / "manifest.json").write_text(json.dumps({"scans": 600, "role": "development"}))
        (self.inputs / "reference.txt").write_text("fixture truth\n")
        (self.inputs / "reference_metadata.json").write_text("{}")
        self.runs = self.root / "runs"
        self.runs.mkdir()
        self.launches = 0
        self.exit_codes = [0]
        self.summary_index = 0

    def tearDown(self):
        self.temporary.cleanup()

    def launch(self, command, **kwargs):
        run_dir = Path(command[-1]).parent
        saved = json.loads((run_dir / "run_manifest.json").read_text())
        self.assertEqual(saved["status"], "RUNNING")
        self.assertEqual(saved["stage"], "REPLAY")
        code = self.exit_codes[min(self.launches, len(self.exit_codes)-1)]
        self.launches += 1
        self.summaries = complete_streams(Path(command[-1]))
        process = SimpleNamespace(pid=99999999, returncode=code,
                                  communicate=lambda **kwargs: ("wrapper output", "crash" if code else ""))
        return process

    def postprocess(self, command, **kwargs):
        value = self.summaries[self.summary_index % 3]
        self.summary_index += 1
        return subprocess.CompletedProcess(command, 0, json.dumps(value), "")

    def execute(self, identity=None):
        return runner._run_scene("DEV_FIXTURE", 14, "DEVELOPMENT_FIXTURE", "CORRIDOR",
            self.inputs, self.runs, self.root / "ros", self.root / "ws", "fixture-binary",
            runner.LOCKED_DEVELOPMENT_THRESHOLD, identity or {"development_fixture": "v1"})

    def ledger(self):
        return runner._read_tsv_or_csv(self.runs / "failure_ledger.csv")

    def test_success_cache_and_changed_identity(self):
        with patch.object(runner.subprocess, "Popen", side_effect=self.launch), \
             patch.object(runner.subprocess, "run", side_effect=self.postprocess):
            self.assertEqual(self.execute()["status"], "COMPLETED")
            self.assertEqual(self.execute()["status"], "CACHED")
            self.assertEqual(self.launches, 1)
            self.assertEqual(self.ledger()[-1]["status"], "COMPLETED")
            with self.assertRaises(runner.FinalEvaluationError):
                self.execute({"development_fixture": "changed"})

    def test_crash_retries_once_and_preserves_failure(self):
        self.exit_codes = [1, 0]
        with patch.object(runner.subprocess, "Popen", side_effect=self.launch), \
             patch.object(runner.subprocess, "run", side_effect=self.postprocess):
            result = self.execute()
            self.assertEqual(result["status"], "COMPLETED")
            self.assertEqual(self.launches, 2)
            self.assertIn("CRASHED", [r["status"] for r in self.ledger()])
            self.assertEqual(self.execute()["status"], "CACHED")

    def test_timeout_is_recorded_and_retried_once(self):
        normal_launch = self.launch
        def launch(command, **kwargs):
            process = normal_launch(command, **kwargs)
            if self.launches == 1:
                from unittest.mock import Mock
                process.communicate = Mock(side_effect=[subprocess.TimeoutExpired(command, 900), ("", "")])
            return process
        with patch.object(runner.subprocess, "Popen", side_effect=launch), \
             patch.object(runner.subprocess, "run", side_effect=self.postprocess), \
             patch.object(runner.os, "killpg") as kill:
            self.assertEqual(self.execute()["status"], "COMPLETED")
            self.assertEqual(self.launches, 2)
            kill.assert_called_once()
        saved = json.loads((self.runs / "DEV_FIXTURE/run_manifest.json").read_text())
        self.assertEqual(saved["return_code"], 124)

    def test_truncated_success_is_not_completed_and_uses_one_replay_retry(self):
        normal_launch = self.launch
        def launch(command, **kwargs):
            process = normal_launch(command, **kwargs)
            if self.launches == 1:
                write_csv(Path(command[-1]) / "poses.csv", ["timestamp_ns", "event"], [])
            return process
        with patch.object(runner.subprocess, "Popen", side_effect=launch), \
             patch.object(runner.subprocess, "run", side_effect=self.postprocess):
            self.assertEqual(self.execute()["status"], "COMPLETED")
        first = json.loads((self.runs / "DEV_FIXTURE/run_manifest.json").read_text())
        self.assertEqual(first["status"], "INCOMPLETE_EXECUTION")
        self.assertEqual(self.launches, 2)

    def test_exhausted_replay_retries_do_not_launch_a_third_attempt(self):
        self.exit_codes = [1, 1]
        with patch.object(runner.subprocess, "Popen", side_effect=self.launch):
            self.assertEqual(self.execute()["status"], "CRASHED")
            self.assertEqual(self.execute()["status"], "CRASHED")
            self.assertEqual(self.launches, 2)

    def test_interrupted_processing_resumes_without_replaying_estimator(self):
        with patch.object(runner.subprocess, "Popen", side_effect=self.launch), \
             patch.object(runner.subprocess, "run", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.execute()
        raw = self.runs / "DEV_FIXTURE/stream/poses.csv"
        previous = runner.sha256_file(raw)
        with patch.object(runner.subprocess, "Popen") as launch, \
             patch.object(runner.subprocess, "run", side_effect=self.postprocess):
            self.assertEqual(self.execute()["status"], "COMPLETED")
            launch.assert_not_called()
        self.assertEqual(runner.sha256_file(raw), previous)

    def test_confirmed_live_postprocessor_prevents_duplicate_processing(self):
        with patch.object(runner.subprocess, "Popen", side_effect=self.launch), \
             patch.object(runner.subprocess, "run", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.execute()
        with patch.object(runner, "_live_postprocess_pid", return_value=99999999), \
             patch.object(runner.subprocess, "Popen") as launch, \
             patch.object(runner.subprocess, "run") as processing:
            self.assertEqual(self.execute()["status"], "IN_PROGRESS")
            launch.assert_not_called()
            processing.assert_not_called()

    def test_interrupted_replay_retains_original_directory_and_retries(self):
        with patch.object(runner.subprocess, "Popen", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.execute()
        with patch.object(runner.subprocess, "Popen", side_effect=self.launch), \
             patch.object(runner.subprocess, "run", side_effect=self.postprocess):
            self.assertEqual(self.execute()["status"], "COMPLETED")
            self.assertIn("INTERRUPTED_REPLAY", [r["status"] for r in self.ledger()])
        self.assertTrue((self.runs / "DEV_FIXTURE/run_manifest.json").is_file())


if __name__ == "__main__":
    unittest.main()
