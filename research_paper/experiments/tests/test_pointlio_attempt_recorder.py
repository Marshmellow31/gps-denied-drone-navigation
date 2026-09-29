import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from record_pointlio_attempt import write_manifest_atomically  # noqa: E402


class PointLioAttemptRecorderTests(unittest.TestCase):
    def manifest(self):
        return {
            "run_id": "run-1",
            "mode": "on",
            "study_split": "development_seed14_feasibility_only",
            "input_bag": {"sha256": "bag"},
            "configuration": {"sha256": "config"},
            "native_binary": {"sha256": "binary"},
            "native_source": {"commit": "commit", "files": {}},
            "build_overlay": {"glog_prefix": "glog", "glog_metadata": None},
            "ros_master_uri": "http://127.0.0.1:41877",
            "repository_sources": {"runner": "source-hash"},
            "status": "RUNNING",
        }

    def test_manifest_replacement_is_valid_and_preserves_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            first = self.manifest()
            path = write_manifest_atomically(run, first)
            second = dict(first, status="COMPLETED", output_sha256={"poses.csv": "pose"})
            write_manifest_atomically(run, second)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), second)
            self.assertEqual(list(run.glob(".run_manifest.*.tmp")), [])

    def test_changed_identity_cannot_overwrite_attempt_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            first = self.manifest()
            path = write_manifest_atomically(run, first)
            original = path.read_bytes()
            changed = dict(first, input_bag={"sha256": "different"})
            with self.assertRaisesRegex(ValueError, "attempt identity changed"):
                write_manifest_atomically(run, changed)
            self.assertEqual(path.read_bytes(), original)

    def test_serialization_failure_leaves_previous_manifest_intact(self):
        with tempfile.TemporaryDirectory() as directory:
            run = Path(directory)
            first = self.manifest()
            path = write_manifest_atomically(run, first)
            original = path.read_bytes()
            failed = dict(first, status="COMPLETED", unsupported=object())
            with self.assertRaises(TypeError):
                write_manifest_atomically(run, failed)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(list(run.glob(".run_manifest.*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
