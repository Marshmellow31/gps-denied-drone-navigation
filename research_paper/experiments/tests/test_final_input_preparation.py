"""Mock bag creation only; never call the held-out layout generator."""
import json
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import final_evaluation_runner as runner


class InputPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.results = self.root / "results"
        self.runs = self.results / "runs"
        self.runs.mkdir(parents=True)
        self.folder = self.root / "fixture_pair"
        self.identity = {"development_fixture": "fixed"}
        self.generated = 0
        self.changed_artifact = None

    def tearDown(self):
        self.temporary.cleanup()

    def generate(self, path, seed, stratum, control):
        self.generated += 1
        path.mkdir(parents=True)
        bag_bytes = b"changed bag" if self.changed_artifact == "bag" else b"mock bag"
        reference_text = ("changed analytic fixture\n" if self.changed_artifact == "reference"
                          else "same analytic fixture\n")
        (path / "sensors.bag").write_bytes(bag_bytes)
        (path / "reference.txt").write_text(reference_text)
        (path / "reference_metadata.json").write_text("{}")
        manifest = {"seed": seed, "stratum": stratum, "control": control, "role": "heldout",
                    "truth_in_sensor_bag": False, "scans": 600, "imu_messages": 12021,
                    "runtime_s": float(self.generated),
                    "code_revision": f"fixture-revision-{(self.generated - 1) // 2 + 1}",
                    "route_profile": {"profile_id": runner.PROFILE_ID},
                    "generator_sha256": runner.sha256_file(Path(runner.heldout.__file__)),
                    "simulator_sha256": runner.sha256_file(runner.ROOT / "research_paper/experiments/src/simulate_lidar.py"),
                    "formal_route_sha256": runner.sha256_file(runner.ROOT / "research_paper/experiments/src/t14_formal_route.py")}
        for filename in ("sensors.bag", "reference.txt", "reference_metadata.json"):
            manifest[filename] = {"sha256": runner.sha256_file(path / filename)}
        (path / "manifest.json").write_text(json.dumps(manifest))
        return manifest

    def audit(self, command, **kwargs):
        return subprocess.CompletedProcess(command, 0, json.dumps({"paired_imu_identical": True}), "")

    def prepare(self):
        return runner._prepare_pair(self.folder, self.results, self.runs, 14,
                                    "DEVELOPMENT_FIXTURE", self.root / "ros", self.identity, 0)

    def test_completed_inputs_resume_without_regenerating(self):
        with patch.object(runner.heldout, "write_sensor_input", side_effect=self.generate), \
             patch.object(runner.subprocess, "run", side_effect=self.audit):
            self.prepare()
            self.prepare()
            self.assertEqual(self.generated, 2)
        record = json.loads((self.results / "input_attempts/DEVELOPMENT_FIXTURE_14_A1.json").read_text())
        self.assertEqual(record["status"], "INPUTS_VERIFIED")

    def test_completed_inputs_rebuild_after_scratch_cleanup_and_keep_first_archive(self):
        with patch.object(runner.heldout, "write_sensor_input", side_effect=self.generate), \
             patch.object(runner.subprocess, "run", side_effect=self.audit):
            self.prepare()
            archive_paths = {
                scene: self.results / f"inputs/DEVELOPMENT_FIXTURE_14/{scene}/manifest.json"
                for scene in ("CORRIDOR", "CONTROL")
            }
            first_bytes = {scene: path.read_bytes() for scene, path in archive_paths.items()}
            first_hashes = {
                scene: runner.sha256_file(self.folder / scene.lower() / "manifest.json")
                for scene in archive_paths
            }
            shutil.rmtree(self.folder)
            self.prepare()
            second_hashes = {
                scene: runner.sha256_file(self.folder / scene.lower() / "manifest.json")
                for scene in archive_paths
            }
            shutil.rmtree(self.folder)
        self.assertEqual(self.generated, 4)
        self.assertEqual({scene: path.read_bytes() for scene, path in archive_paths.items()}, first_bytes)
        record = json.loads((self.results / "input_attempts/DEVELOPMENT_FIXTURE_14_A1.json").read_text())
        self.assertEqual(record["status"], "INPUTS_VERIFIED")
        self.assertEqual(len(record["generation_history"]), 2)
        first, second = record["generation_history"]
        self.assertTrue(all(item["runtime_s"] >= 0 for item in (first, second)))
        self.assertEqual(first["manifest_sha256"], first_hashes)
        self.assertEqual(second["manifest_sha256"], second_hashes)
        self.assertEqual(first["manifest_bookkeeping"], {
            "CORRIDOR": {"code_revision": "fixture-revision-1", "runtime_s": 1.0},
            "CONTROL": {"code_revision": "fixture-revision-1", "runtime_s": 2.0},
        })
        self.assertEqual(second["manifest_bookkeeping"], {
            "CORRIDOR": {"code_revision": "fixture-revision-2", "runtime_s": 3.0},
            "CONTROL": {"code_revision": "fixture-revision-2", "runtime_s": 4.0},
        })
        self.assertEqual(set(first["manifest_sha256"]), {"CORRIDOR", "CONTROL"})
        self.assertEqual(set(second["manifest_sha256"]), {"CORRIDOR", "CONTROL"})

    def test_regenerated_changed_bag_or_reference_is_rejected(self):
        for altered in ("bag", "reference"):
            with self.subTest(altered=altered), tempfile.TemporaryDirectory(dir=self.root) as folder:
                base = Path(folder)
                self.results = base / "results"
                self.runs = self.results / "runs"
                self.runs.mkdir(parents=True)
                self.folder = base / "fixture_pair"
                self.generated = 0
                self.changed_artifact = None
                with patch.object(runner.heldout, "write_sensor_input", side_effect=self.generate), \
                     patch.object(runner.subprocess, "run", side_effect=self.audit):
                    self.prepare()
                    shutil.rmtree(self.folder)
                    self.changed_artifact = altered
                    with self.assertRaises(runner.FinalEvaluationError):
                        self.prepare()

    def test_completed_pair_regenerates_after_scratch_cleanup_without_changing_provenance(self):
        with patch.object(runner.heldout, "write_sensor_input", side_effect=self.generate), \
             patch.object(runner.subprocess, "run", side_effect=self.audit):
            self.prepare()
            archive_manifest = (self.results / "inputs/DEVELOPMENT_FIXTURE_14/CORRIDOR/manifest.json").read_bytes()
            shutil.rmtree(self.folder)
            self.prepare()
        self.assertEqual(self.generated, 4)
        self.assertEqual((self.results / "inputs/DEVELOPMENT_FIXTURE_14/CORRIDOR/manifest.json").read_bytes(),
                         archive_manifest)
        record = json.loads((self.results / "input_attempts/DEVELOPMENT_FIXTURE_14_A1.json").read_text())
        self.assertEqual(record["status"], "INPUTS_VERIFIED")
        self.assertEqual(len(record["generation_history"]), 2)
        self.assertTrue(all(row["runtime_s"] >= 0 for row in record["generation_history"]))

    def test_regenerated_changed_bag_or_reference_is_rejected(self):
        for altered in ("bag", "reference"):
            with self.subTest(altered=altered), tempfile.TemporaryDirectory(dir=self.root) as folder:
                base = Path(folder)
                self.results = base / "results"
                self.runs = self.results / "runs"
                self.runs.mkdir(parents=True)
                self.folder = base / "fixture_pair"
                self.generated = 0
                self.changed_artifact = None
                with patch.object(runner.heldout, "write_sensor_input", side_effect=self.generate), \
                     patch.object(runner.subprocess, "run", side_effect=self.audit):
                    self.prepare()
                    shutil.rmtree(self.folder)
                    self.changed_artifact = altered
                    with self.assertRaises(runner.FinalEvaluationError):
                        self.prepare()

    def test_interrupted_partial_generation_is_preserved_and_retried(self):
        def interrupt(path, *args):
            path.mkdir(parents=True)
            (path / "sensors.bag").write_bytes(b"retained partial")
            raise KeyboardInterrupt
        with patch.object(runner.heldout, "write_sensor_input", side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.prepare()
        record_path = self.results / "input_attempts/DEVELOPMENT_FIXTURE_14_A1.json"
        record = json.loads(record_path.read_text())
        record["owner_pid"] = 99999999
        record_path.write_text(json.dumps(record))
        with patch.object(runner.heldout, "write_sensor_input", side_effect=self.generate), \
             patch.object(runner.subprocess, "run", side_effect=self.audit):
            result = self.prepare()
        self.assertIn("TECHNICAL_RETRY1", result[0].name)
        self.assertEqual((self.folder / "corridor/sensors.bag").read_bytes(), b"retained partial")
        self.assertEqual(json.loads(record_path.read_text())["status"], "FAILED_INPUT")

    def test_pair_audit_failure_retains_attempt_and_retries_once(self):
        calls = 0
        def audit(command, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                return subprocess.CompletedProcess(command, 1, "", "audit failed")
            return self.audit(command, **kwargs)
        with patch.object(runner.heldout, "write_sensor_input", side_effect=self.generate), \
             patch.object(runner.subprocess, "run", side_effect=audit):
            result = self.prepare()
        self.assertEqual(self.generated, 4)
        self.assertIn("TECHNICAL_RETRY1", result[0].name)
        failed = json.loads((self.results / "input_attempts/DEVELOPMENT_FIXTURE_14_A1.json").read_text())
        self.assertEqual(failed["stage"], "PAIRED_BAG_AUDIT")
        self.assertEqual(failed["audit_stderr"], "audit failed")

    def test_exhausted_failures_never_generate_a_third_input_pair(self):
        with patch.object(runner.heldout, "write_sensor_input", side_effect=self.generate), \
             patch.object(runner.subprocess, "run", side_effect=subprocess.CalledProcessError(1, "fixture")):
            for _ in range(2):
                with self.assertRaises(runner.FinalEvaluationError):
                    self.prepare()
        self.assertEqual(self.generated, 4)

    def test_archive_failure_retries_processing_without_regenerating_bags(self):
        original = runner.shutil.copy2
        failed = False
        def copy(source, target):
            nonlocal failed
            if not failed:
                failed = True
                raise OSError("fixture archive interruption")
            return original(source, target)
        with patch.object(runner.heldout, "write_sensor_input", side_effect=self.generate), \
             patch.object(runner.subprocess, "run", side_effect=self.audit), \
             patch.object(runner.shutil, "copy2", side_effect=copy):
            self.prepare()
        self.assertEqual(self.generated, 2)
        record = json.loads((self.results / "input_attempts/DEVELOPMENT_FIXTURE_14_A1.json").read_text())
        self.assertEqual(record["status"], "INPUTS_VERIFIED")
        self.assertIn("fixture archive interruption", record["prior_failed_archive_record"]["reason"])


if __name__ == "__main__":
    unittest.main()
