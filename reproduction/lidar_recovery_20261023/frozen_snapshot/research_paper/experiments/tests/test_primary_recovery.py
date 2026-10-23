"""Adversarial provenance checks; never launch a native backend."""
import copy
from contextlib import ExitStack
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import recover_primary_development as recovery


class PrimaryRecoveryTests(unittest.TestCase):
    def fixture(self, root):
        native, inputs = root / "native_attempt", root / "input"
        (native / "stream").mkdir(parents=True)
        inputs.mkdir()
        for name in ("manifest.json", "sensors.bag", "reference.txt", "reference_metadata.json"):
            (inputs / name).write_text(name)
        stream = native / "stream/poses.csv"
        stream.write_text("preserved pose bytes")
        row = recovery.schedule()[0]
        backend = {"binary_sha256": "historical-binary"}
        sources = {"config": "configuration", "replay_script": "reviewed-wrapper"}
        runtime = {"python": "isolated"}
        manifest = {
            "status": "COMPLETED", "run_id": row["run_id"],
            "scheduled_run_id": row["run_id"], "seed": row["seed"],
            "scene": row["scene"], "control": row["control"],
            "route_profile": recovery.development.PROFILE_ID, "role": "development",
            "input_manifest": {"route_profile": {"profile_id": recovery.development.PROFILE_ID}},
            "fingerprint": {
                "input_manifest_file_sha256": recovery.lifecycle.sha256_file(inputs / "manifest.json"),
                "sensor_bag_sha256": recovery.lifecycle.sha256_file(inputs / "sensors.bag"),
                "reference_sha256": recovery.lifecycle.sha256_file(inputs / "reference.txt"),
                "reference_metadata_sha256": recovery.lifecycle.sha256_file(inputs / "reference_metadata.json"),
                "execution_identity": {"backend": backend, "sources": sources, "runtime": runtime},
                "backend_binary_sha256": backend["binary_sha256"],
                "configuration_sha256": sources["config"],
            },
            "outputs": {"stream/poses.csv": recovery.lifecycle.sha256_file(stream)},
            "elapsed_s": 1.0, "completion_validation": {"validated": True},
            "postprocess_summaries": [{}, {"valid": 597}, {"local_valid": 1154}],
        }
        (native / "run_manifest.json").write_text(json.dumps(manifest))
        return native, inputs, row, backend, sources, runtime, manifest

    def adapt(self, root, fixture):
        native, inputs, row, backend, sources, runtime = fixture[:6]
        return recovery.analysis_adapter(root / "adapter", native, row, inputs,
                                         backend, sources, runtime)

    def test_schedule_has_32_primary_pairs_and_only_prescribed_repeats(self):
        rows = recovery.schedule()
        self.assertEqual(len(rows), 68)
        primary = [(r["seed"], r["scene"]) for r in rows if not r["repeat"]]
        self.assertEqual(set(primary), {(s, c) for s in range(14, 46)
                                        for c in ("CORRIDOR", "CONTROL")})
        self.assertEqual(len(primary), 64)
        self.assertEqual({(r["seed"], r["scene"]) for r in rows if r["repeat"]},
                         {(s, c) for s in (14, 45) for c in ("CORRIDOR", "CONTROL")})

    def test_adapter_preserves_actual_native_attempt_and_output_identity(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture = self.fixture(root)
            actual, _, row, _, _, _, manifest = fixture
            manifest["run_id"] += "_TECHNICAL_RETRY1"
            (actual / "run_manifest.json").write_text(json.dumps(manifest))
            adapter = self.adapt(root, fixture)
            self.assertEqual(adapter["run_id"], row["run_id"])
            self.assertEqual(adapter["source_lifecycle_manifest_sha256"],
                             recovery.lifecycle.sha256_file(actual / "run_manifest.json"))
            self.assertEqual((root / "adapter/stream/poses.csv").resolve(),
                             actual / "stream/poses.csv")
            self.assertIn("not a recovered historical", adapter["provenance"])

    def test_post_replay_input_mutations_cannot_be_relabelled(self):
        for name in ("manifest.json", "sensors.bag", "reference.txt", "reference_metadata.json"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                fixture = self.fixture(root)
                (fixture[1] / name).write_text("changed after native fingerprint")
                with self.assertRaisesRegex(ValueError, "input identity changed"):
                    self.adapt(root, fixture)
                self.assertFalse((root / "adapter/run_manifest.json").exists())

    def test_changed_source_backend_or_runtime_cannot_be_attached_to_old_output(self):
        for index in (3, 4, 5):
            with self.subTest(identity=index), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                fixture = list(self.fixture(root))
                fixture[index] = {**fixture[index], "changed": "after replay"}
                with self.assertRaisesRegex(ValueError, "sources/backend differ"):
                    self.adapt(root, fixture)

    def test_native_slot_and_role_metadata_cannot_be_relabelled(self):
        for key, value in (("scheduled_run_id", "another-slot"), ("seed", 15),
                           ("scene", "CONTROL"), ("role", "heldout"),
                           ("control", True), ("route_profile", "different-route")):
            with self.subTest(key=key), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                fixture = self.fixture(root)
                manifest = copy.deepcopy(fixture[-1])
                manifest[key] = value
                (fixture[0] / "run_manifest.json").write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    self.adapt(root, fixture)

    def test_changed_completed_stream_is_rejected_before_adapter_publication(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture = self.fixture(root)
            (fixture[0] / "stream/poses.csv").write_text("corrupted")
            with self.assertRaisesRegex(ValueError, "completed output changed"):
                self.adapt(root, fixture)

    def test_source_change_during_native_work_is_rejected_even_at_bounded_checkpoint(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "source.py"
            source.write_text("reviewed")
            row = recovery.schedule()[0]
            args = SimpleNamespace(stop_after=1, input_root=root, ros_env=root, workspace=root)
            summary = {"runs": [{**row, "status": "PENDING"}]}
            backend = {"binary_sha256": "exact"}
            sources = {"replay_script": recovery.lifecycle.sha256_file(source)}

            def changed(*args):
                source.write_text("changed while replay was active")
                return {"status": "COMPLETED", "run_id": row["run_id"]}

            with patch.object(recovery, "validate_scientific_input"), \
                 patch.object(recovery.lifecycle, "_check_backend", return_value=backend), \
                 patch.object(recovery.lifecycle, "_run_scene", side_effect=changed), \
                 patch.object(recovery, "analysis_adapter") as adapter, \
                 patch.object(recovery.socket, "socket") as socket:
                socket.return_value.__enter__.return_value.connect_ex.return_value = 1
                with self.assertRaisesRegex(RuntimeError, "source changed during"):
                    recovery.recover_rows(args, root, [row], {(14, "CORRIDOR"): {}},
                        summary, root / "summary.json", {"replay_script": source},
                        sources, backend, root / "binary", {}, {})
                adapter.assert_not_called()

    def test_occupied_master_blocks_a_retry_as_well_as_a_fresh_slot(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            row = recovery.schedule()[0]
            prior = root / "native" / row["run_id"] / "run_manifest.json"
            prior.parent.mkdir(parents=True)
            prior.write_text(json.dumps({"status": "CRASHED"}))
            args = SimpleNamespace(stop_after=1, input_root=root, ros_env=root, workspace=root)
            backend = {"binary_sha256": "exact"}
            with patch.object(recovery, "validate_scientific_input"), \
                 patch.object(recovery.lifecycle, "_check_backend", return_value=backend), \
                 patch.object(recovery.lifecycle, "_run_scene") as replay, \
                 patch.object(recovery.socket, "socket") as socket:
                socket.return_value.__enter__.return_value.connect_ex.return_value = 0
                with self.assertRaisesRegex(RuntimeError, "port is occupied"):
                    recovery.recover_rows(args, root, [row], {(14, "CORRIDOR"): {}},
                        {"runs": [{**row, "status": "PENDING"}]}, root / "summary.json",
                        {}, {}, backend, root / "binary", {}, {})
                replay.assert_not_called()
                self.assertEqual(json.loads(prior.read_text())["status"], "CRASHED")

    def main_context(self, stack, root):
        anchor = root / "historical.json"
        records = [{"seed": s, "scene": c} for s in range(14, 46)
                   for c in ("CORRIDOR", "CONTROL")]
        anchor.write_text(json.dumps({"input_audit": {"primary_run_provenance": records}}))
        stack.enter_context(patch.object(recovery, "HISTORICAL", anchor))
        stack.enter_context(patch.object(recovery.lifecycle, "_r2_frozen_artifact_hashes"))
        stack.enter_context(patch.object(recovery.lifecycle, "_check_analysis_runtime", return_value={}))
        stack.enter_context(patch.object(recovery.lifecycle, "_check_backend", return_value={}))
        stack.enter_context(patch.object(sys, "argv", ["recovery", "--input-root", str(root),
            "--output-root", str(root / "output"), "--ros-env", str(root),
            "--workspace", str(root), "--stop-after", "1"]))
        stack.enter_context(patch.dict(recovery.os.environ, {}, clear=False))

    def test_preflight_exception_records_blocked_summary_and_preserves_native_ledger(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            self.main_context(stack, root)
            ledger = root / "output/native/failure_ledger.csv"
            ledger.parent.mkdir(parents=True)
            ledger.write_text("status\nCRASHED\n")
            stack.enter_context(patch.object(recovery, "recover_rows",
                                              side_effect=ValueError("input hash changed")))
            with self.assertRaisesRegex(ValueError, "input hash changed"):
                recovery.main()
            summary = json.loads((root / "output/recovery_schedule.json").read_text())
            self.assertEqual(summary["status"], "BLOCKED")
            self.assertIn("input hash changed", summary["reason"])
            self.assertEqual(ledger.read_text(), "status\nCRASHED\n")
            self.assertEqual((root / "output/analysis_contract/failure_ledger.csv").resolve(), ledger)

    def test_unrelated_analysis_ledger_is_rejected_before_any_native_work(self):
        for link in (False, True):
            with self.subTest(symlink=link), tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
                root = Path(folder)
                self.main_context(stack, root)
                path = root / "output/analysis_contract/failure_ledger.csv"
                path.parent.mkdir(parents=True)
                wrong = root / "unrelated.csv"
                wrong.write_text("status\nCOMPLETED\n")
                if link:
                    path.symlink_to(wrong)
                else:
                    path.write_text(wrong.read_text())
                replay = stack.enter_context(patch.object(recovery, "recover_rows"))
                with self.assertRaisesRegex(ValueError, "failure-ledger target"):
                    recovery.main()
                replay.assert_not_called()


if __name__ == "__main__":
    unittest.main()
