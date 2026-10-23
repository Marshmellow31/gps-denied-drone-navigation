"""Development-only workflow adversarial fixtures; no native replay or real bag."""
from contextlib import ExitStack, redirect_stdout
import io
import csv
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import run_pointlio_development as cohort
import verify_pointlio_development_attempt as check
import validate_pointlio_development_input as inputs
import pointlio_development_analysis as point_analysis
import t16_development_analysis as common


def csv_write(path, rows, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields or list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


class PointLioDevelopmentWorkflowTests(unittest.TestCase):
    def fixture(self, root):
        run = root / "POINTLIO_DEV14_CORRIDOR_XM6_P1"
        run.mkdir()
        source = root / "source"
        source.mkdir()
        binary, config, bag = root / "binary", root / "config", root / "sensors.bag"
        for p in (binary, config, bag, root / "fixture-source.py"):
            p.write_text(p.name)
        interpreter = root / "runtime/bin/python"
        interpreter.parent.mkdir(parents=True)
        interpreter.write_text("isolated interpreter")
        history = root / "runtime/conda-meta/history"
        history.parent.mkdir()
        history.write_text("frozen dependencies")
        stamps = list(range(1, 601))
        csv_write(run / "input_header_stamps.csv", [{"header_stamp_ns": s} for s in stamps])
        frame_rows = [{"frame_id": s, "input_header_stamp_ns": s, "timestamp_ns": s + 1000,
            "timestamp_source": "ACTUAL", "segment_id": 0, "source_stage": "MEASUREMENT",
            "run_state": "COMPLETE"} for s in stamps]
        csv_write(run / "sidecar/frame_ledger.csv", frame_rows)
        indicators = [{**r, "valid": "true", "unavailable_reason": "",
            "lambda_min_1m": 1, "lambda_min_3m": 1, "lambda_min_5m": 1,
            "DCREG_state": "HEALTHY", "DCREG_HEALTH_SCORE": 1} for r in frame_rows]
        csv_write(run / "pointlio_indicators.csv", indicators)
        poses = [{"source_frame_id": s, "timestamp_ns": s + 1000, "segment_id": 0,
                  "event": "POSE", "valid": "true", "unavailable_reason": ""} for s in stamps]
        csv_write(run / "poses.csv", poses)
        csv_write(run / "poses_segmented.csv", poses)
        csv_write(run / "sidecar/reset_events.csv", [], fields=["affected_frame_id"])
        slot = {"seed": 14, "scene": "CORRIDOR", "control": False,
                "input_manifest": {"path": str(root / "manifest.json"), "sha256": "manifest"},
                "reference_sha256": "reference", "reference_metadata_sha256": "metadata"}
        manifest = {
            "run_id": run.name, "status": "COMPLETED", "mode": "on",
            "study_split": "development_replication", "threshold_fit_performed": False,
            "heldout_inputs_opened": False, **slot,
            "process_exit_codes": dict.fromkeys(("rosbag", "pointlio", "pose_logger", "exporter", "roscore"), 0),
            "runtime": {"python": "3.12.14", "numpy": "2.5.3", "python_executable": str(interpreter),
                "python_binary_sha256": check.sha256(interpreter), "conda_history_sha256": check.sha256(history)},
            "input_bag": {"path": str(bag), "bytes": bag.stat().st_size, "sha256": check.sha256(bag)},
            "native_binary": {"path": str(binary), "sha256": check.sha256(binary)},
            "configuration": {"path": str(config), "sha256": check.sha256(config)},
            "native_source": {"root": str(source), "commit": "pinned", "dirty_patch_sha256": "patch", "files": {}},
            "build_overlay": {"glog_prefix": str(root / "glog"),
                "glog_metadata": {"path": "fixture-package", "sha256": "glog"},
                "runtime_library_hashes": {"fixture-library": "library"}},
            "repository_sources": {"fixture-source.py": check.sha256(root / "fixture-source.py")},
        }
        self.save_manifest(run, manifest)
        return run, manifest, slot, stamps

    def save_manifest(self, run, manifest):
        manifest["output_sha256"] = {str(p.relative_to(run)): check.sha256(p)
            for p in run.rglob("*") if p.is_file() and p.name != "run_manifest.json"}
        (run / "run_manifest.json").write_text(json.dumps(manifest))

    def verify_fixture(self, root, fixture):
        run, manifest, slot, stamps = fixture
        messages = [("/sim/points", SimpleNamespace(header=SimpleNamespace(
            stamp=SimpleNamespace(to_nsec=lambda s=s: s))), None) for s in stamps]
        with ExitStack() as stack:
            stack.enter_context(patch.object(check, "ROOT", root))
            stack.enter_context(patch.object(check, "REPO_SOURCE_FILES", ("fixture-source.py",)))
            stack.enter_context(patch.object(check, "validate_input", return_value=slot))
            stack.enter_context(patch.object(check, "validate_native", return_value={"native_source": manifest["native_source"]}))
            stack.enter_context(patch.object(check, "glog_identity", return_value=manifest["build_overlay"]))
            stack.enter_context(patch.dict(sys.modules, {"rosbag": SimpleNamespace(Bag=MagicMock())}))
            fake = sys.modules["rosbag"].Bag.return_value.__enter__.return_value
            fake.read_messages.return_value = messages
            return check.verify(run)

    def test_complete_native_fixture_passes_without_real_ros_or_geometry(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            result = self.verify_fixture(root, self.fixture(root))
            self.assertEqual((result["input_frames"], result["pose_rows"]), (600, 600))

    def test_omitted_repository_identity_is_rejected_even_with_valid_output_hashes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture = self.fixture(root)
            fixture[1]["repository_sources"] = {}
            self.save_manifest(fixture[0], fixture[1])
            with self.assertRaisesRegex(ValueError, "omits required"):
                self.verify_fixture(root, fixture)

    def test_measurement_pose_truncation_is_rejected_even_when_hashes_are_updated(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture = self.fixture(root)
            for name in ("poses.csv", "poses_segmented.csv"):
                with (fixture[0] / name).open() as stream:
                    rows = list(csv.DictReader(stream))
                csv_write(fixture[0] / name, rows[:-1])
            self.save_manifest(fixture[0], fixture[1])
            with self.assertRaisesRegex(ValueError, "pose logger lost"):
                self.verify_fixture(root, fixture)

    def test_changed_dependency_history_cannot_be_accepted_as_same_runtime(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture = self.fixture(root)
            (root / "runtime/conda-meta/history").write_text("changed")
            with self.assertRaisesRegex(ValueError, "dependency identity changed"):
                self.verify_fixture(root, fixture)

    def test_feasibility_and_failed_processes_cannot_enter_development_selection(self):
        for key in ("feasibility", "pose_logger", "roscore"):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                fixture = self.fixture(root)
                if key == "feasibility":
                    fixture[1]["study_split"] = "development_seed14_feasibility_only"
                else:
                    fixture[1]["process_exit_codes"][key] = 1
                self.save_manifest(fixture[0], fixture[1])
                with self.assertRaises(ValueError):
                    self.verify_fixture(root, fixture)

    def test_point_schedule_is_exactly32_formal_pairs_and_no_feasibility_or_repeats(self):
        rows = cohort.schedule()
        self.assertEqual(len(rows), 64)
        self.assertEqual({(r["seed"], r["scene"]) for r in rows},
                         {(s, c) for s in range(14, 46) for c in ("CORRIDOR", "CONTROL")})
        self.assertTrue(all(r["run_id"].startswith("POINTLIO_DEV") for r in rows))

    def test_point_scalar_uses_the_same_three_distinct_record_reset_rule(self):
        sources = [10, 20, 20, 30, 40, 50, 60, 70, 80]
        decisions = [common.DecisionTick(i, i * common.TICK_NS, True, 10., None,
                     source, 0 if i < 6 else 1, "") for i, source in enumerate(sources)]
        primary = common.debounce(decisions, "FASTLIO_MIN_EIG_G3", 5.)
        point = common.debounce(decisions, point_analysis.SCALAR, 5., scalar_method=point_analysis.SCALAR)
        np.testing.assert_array_equal(primary[0], point[0])
        np.testing.assert_array_equal(primary[1], point[1])
        self.assertEqual(np.flatnonzero(point[1]).tolist(), [5, 8])

    def test_separate_point_scalar_threshold_preserves_frozen_candidate_rule(self):
        decisions = [common.DecisionTick(i, common.EPOCH_NS + i * common.TICK_NS,
            True, 0. if i < 5 else 10., None, common.EPOCH_NS + i * common.TICK_NS, 0, "")
            for i in range(600)]
        label = common.RecoveryLabel("RECOVERED", True, "", .2, 20.2, .5, 1., None,
                                     20.2, (1, 2, 3), 19)
        raw_scores = [
            common.DiagnosticRecord(common.EPOCH_NS, True, 0., None, 0, ""),
            common.DiagnosticRecord(common.EPOCH_NS + 50_000_000, True, 8.5, None, 0, ""),
            common.DiagnosticRecord(common.EPOCH_NS + 100_000_000, True, 10., None, 0, ""),
            common.DiagnosticRecord(common.EPOCH_NS + 150_000_000, False, 99., None, 0, "RESET"),
        ]
        run = common.DevelopmentRun("POINTLIO_DEV14_CORRIDOR_XM6_P1", 14, "CORRIDOR",
            False, .2, 10., Path("."), {}, {}, [], None, np.eye(4), [], label,
            {point_analysis.SCALAR: raw_scores},
            {point_analysis.SCALAR: decisions}, [])
        selected, candidates = common.select_fastlio_threshold([run], method=point_analysis.SCALAR)
        self.assertEqual(selected["threshold"], 10.)
        self.assertEqual([r["threshold"] for r in candidates], [0., 8.5, 10., "NO_ALARMS"])
        self.assertEqual(selected["conditional_false_healthy_rate"], 0.)
        self.assertEqual(selected["recovery_sensitivity"], 1.)

    def test_dead_wrapper_does_not_hide_a_live_owned_process_group(self):
        process = MagicMock(pid=12345)
        process.poll.return_value = 0
        with patch.object(cohort.process_identity, "_process_group_members", side_effect=[[99], []]), \
             patch.object(cohort.os, "killpg") as kill:
            cohort.stop_group(process)
            kill.assert_called_once_with(12345, cohort.signal.SIGINT)

    def cached_main_fixture(self, root, fixture):
        run, manifest, slot, _ = fixture
        output = root / "cohort"
        (output / "native").mkdir(parents=True)
        target = output / "native" / run.name
        run.rename(target)
        workspace = root / "workspace"
        binary = workspace / "devel/lib/point_lio/pointlio_mapping"
        binary.parent.mkdir(parents=True)
        binary.write_text("binary")
        input_root = root / "inputs"
        bag = input_root / "T14_FORMAL_DEV14_CORRIDOR_INPUT_XM6_V1/sensors.bag"
        bag.parent.mkdir(parents=True)
        bag.write_text("sensors.bag")
        runtime = {k: manifest["runtime"][k] for k in
                   ("python", "numpy", "python_executable", "python_binary_sha256")}
        sources = manifest["repository_sources"]
        paths = {"input_root": str(input_root), "ros_env": str(root / "runtime"),
                 "workspace": str(workspace), "glog_prefix": str(root / "glog")}
        identity = {"sources": sources, "native_binary_sha256": check.sha256(binary),
            "config_sha256": check.sha256(root / "config"), "native_source": manifest["native_source"],
            "runtime": runtime, "conda_history_sha256": manifest["runtime"]["conda_history_sha256"],
            "paths": paths, "build_overlay": manifest["build_overlay"]}
        command = ["bash", str(cohort.RUNNER), paths["ros_env"], paths["workspace"],
            paths["glog_prefix"], str(bag), str(root / "config"), str(target), "on", "development_replication"]
        receipt = output / "launch_records" / f"{run.name}.json"
        receipt.parent.mkdir()
        receipt.write_text(json.dumps({"command": command, "execution_identity": identity,
            "input_manifest": slot["input_manifest"], "pid": 12345,
            "process_start_identity": "old", "process_group_id": 12345}))
        return output, target, workspace, input_root, runtime, sources, paths

    def cached_context(self, stack, root, fixture, data):
        output, target, workspace, input_root, runtime, sources, paths = data
        stack.enter_context(patch.object(cohort, "CONFIG", root / "config"))
        stack.enter_context(patch.object(cohort, "REPO_SOURCE_FILES", ("fixture-source.py",)))
        stack.enter_context(patch.object(cohort, "source_identity", return_value=sources))
        stack.enter_context(patch.object(cohort, "validate_native", return_value={"native_source": fixture[1]["native_source"]}))
        stack.enter_context(patch.object(cohort, "glog_identity", return_value=fixture[1]["build_overlay"]))
        stack.enter_context(patch.object(cohort.process_identity, "_r2_frozen_artifact_hashes", return_value={}))
        stack.enter_context(patch.object(cohort, "validate_input", return_value=fixture[2]))
        stack.enter_context(patch.object(cohort.process_identity, "_check_analysis_runtime", return_value=dict(runtime)))
        stack.enter_context(patch.object(cohort.process_identity, "_process_identity", return_value=None))
        stack.enter_context(patch.object(cohort.subprocess, "check_output", return_value=json.dumps(
            {k: runtime[k] for k in ("python", "numpy")})))
        stack.enter_context(patch.object(sys, "argv", ["point", "--input-root", str(input_root),
            "--output-root", str(output), "--ros-env", paths["ros_env"], "--workspace", str(workspace),
            "--glog-prefix", paths["glog_prefix"], "--stop-after", "1"]))
        stack.enter_context(patch.object(cohort, "schedule", return_value=[cohort.schedule()[0]]))

    def test_cached_wrong_slot_is_rejected_instead_of_relabelled_as_scheduled_slot(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            fixture = self.fixture(root)
            data = self.cached_main_fixture(root, fixture)
            self.cached_context(stack, root, fixture, data)
            manifest = fixture[1]
            manifest["seed"] = 15
            self.save_manifest(data[1], manifest)
            stack.enter_context(patch.object(cohort.process_identity, "_process_group_members", return_value=[]))
            stack.enter_context(patch.object(cohort, "verify", return_value={"status": "PASS", "seed": 15, "scene": "CORRIDOR"}))
            launch = stack.enter_context(patch.object(cohort.subprocess, "Popen"))
            with self.assertRaisesRegex(ValueError, "scheduled cohort identity"):
                cohort.main()
            launch.assert_not_called()
            self.assertEqual(json.loads((data[0] / "development_schedule.json").read_text())["status"], "BLOCKED")

    def test_cached_resume_waits_for_live_descendants_even_when_wrapper_pid_is_absent(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            fixture = self.fixture(root)
            data = self.cached_main_fixture(root, fixture)
            self.cached_context(stack, root, fixture, data)
            stack.enter_context(patch.object(cohort.process_identity, "_process_group_members", return_value=[987]))
            verify = stack.enter_context(patch.object(cohort, "verify"))
            launch = stack.enter_context(patch.object(cohort.subprocess, "Popen"))
            with redirect_stdout(io.StringIO()):
                cohort.main()
            verify.assert_not_called()
            launch.assert_not_called()
            self.assertEqual(json.loads((data[0] / "development_schedule.json").read_text())["status"],
                             "WAITING_FOR_LIVE_NATIVE_ATTEMPT")

    def test_startup_failure_without_native_directory_cannot_erase_its_receipt_or_logs(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            fixture = self.fixture(root)
            data = self.cached_main_fixture(root, fixture)
            self.cached_context(stack, root, fixture, data)
            data[1].rename(root / "unused_fixture")
            receipt = data[0] / "launch_records" / f"{fixture[0].name}.json"
            before = receipt.read_bytes()
            logs = data[0] / "launch_logs"
            logs.mkdir()
            old_log = logs / f"{fixture[0].name}.stderr.log"
            old_log.write_text("retained startup failure")
            launch = stack.enter_context(patch.object(cohort.subprocess, "Popen"))
            with self.assertRaisesRegex(RuntimeError, "prior startup attempt exists"):
                cohort.main()
            launch.assert_not_called()
            self.assertEqual(receipt.read_bytes(), before)
            self.assertEqual(old_log.read_text(), "retained startup failure")
            self.assertEqual(json.loads((data[0] / "development_schedule.json").read_text())["status"], "BLOCKED")

    def test_keyboard_interrupt_persists_interrupted_receipt_and_summary(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            fixture = self.fixture(root)
            data = self.cached_main_fixture(root, fixture)
            self.cached_context(stack, root, fixture, data)
            data[1].rename(root / "unused_fixture")
            receipt = data[0] / "launch_records" / f"{fixture[0].name}.json"
            receipt.unlink()
            process = MagicMock(pid=12345, returncode=None)
            process.wait.side_effect = KeyboardInterrupt
            stack.enter_context(patch.object(cohort.subprocess, "Popen", return_value=process))
            stop = stack.enter_context(patch.object(cohort, "stop_group"))
            with self.assertRaises(KeyboardInterrupt):
                cohort.main()
            stop.assert_called_once_with(process)
            self.assertEqual(json.loads(receipt.read_text())["status"], "INTERRUPTED_OR_TIMEOUT")
            self.assertEqual(json.loads((data[0] / "development_schedule.json").read_text())["status"], "INTERRUPTED")

    def test_analysis_selects_only_formal_point_corridors_and_excludes_controls(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)

            def load(native, *args):
                _, seed_text, scene, _, _ = native.name.split("_")
                seed = int(seed_text[3:])
                label = None if scene == "CONTROL" else common.RecoveryLabel(
                    "RECOVERED", True, "", .2, 20.2, .5, 1., None, 20.2, (1, 2, 3), 19)
                return SimpleNamespace(run_id=native.name, seed=seed, scene=scene,
                    control=scene == "CONTROL", label=label,
                    run_manifest={"runtime": {"python": "3.12.14", "numpy": "2.5.3",
                        "python_executable": str(Path(sys.executable).resolve()),
                        "python_binary_sha256": "fixture", "conda_history_sha256": "fixture"}}), {}, []

            selected = {"status": "SELECTED_DEVELOPMENT_THRESHOLD", "threshold": 10.}
            with patch.object(point_analysis, "load_run", side_effect=load), \
                 patch.object(point_analysis, "_r2_frozen_artifact_hashes", return_value={}), \
                 patch.object(common, "sha256_file", return_value="fixture"), \
                 patch.object(common, "select_fastlio_threshold", return_value=(selected, [])) as fit, \
                 patch.object(common, "summarize_method", return_value=({}, [])):
                result = point_analysis.analyze(root / "native", root / "inputs", root / "analysis")
            fitted = fit.call_args.args[0]
            self.assertEqual(len(fitted), 32)
            self.assertEqual({r.seed for r in fitted}, set(range(14, 46)))
            self.assertTrue(all(not r.control and r.run_id.startswith("POINTLIO_DEV") for r in fitted))
            self.assertEqual(fit.call_args.kwargs["method"], point_analysis.SCALAR)
            self.assertEqual(result["geometry_pair_count"], 32)
            self.assertFalse(result["primary_final_sample_size_changed"])


if __name__ == "__main__":
    unittest.main()
