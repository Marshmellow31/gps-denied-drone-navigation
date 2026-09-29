import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from verify_pointlio_feasibility_pair import (  # noqa: E402
    EXPECTED_POINTLIO_CONFIG_SHA256,
    EXPECTED_SEED14_BAG_SHA256,
    PINNED_POINTLIO_COMMIT,
    verify_pair,
)


def write_csv(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PointLioFeasibilityPairTests(unittest.TestCase):
    def create_run(self, root, name, mode):
        run = root / name
        run.mkdir()
        input_rows = [{"header_stamp_ns": 1000}, {"header_stamp_ns": 2000}]
        write_csv(run / "input_header_stamps.csv", ("header_stamp_ns",), input_rows)
        pose_fields = (
            "timestamp_ns", "clock_id", "parent_frame_id", "body_frame_id",
            "x_m", "y_m", "z_m", "qx", "qy", "qz", "qw", "valid",
            "unavailable_reason", "segment_id", "event", "source_frame_id",
        )
        pose_rows = [{
            "timestamp_ns": 1100, "clock_id": "simulation_epoch",
            "parent_frame_id": "camera_init", "body_frame_id": "body",
            "x_m": 0, "y_m": 0, "z_m": 0, "qx": 0, "qy": 0,
            "qz": 0, "qw": 1, "valid": "true",
            "unavailable_reason": "", "segment_id": 0, "event": "POSE",
            "source_frame_id": 1,
        }]
        write_csv(run / "poses.csv", pose_fields, pose_rows)
        manifest = {
            "status": "COMPLETED", "mode": mode,
            "study_split": "development_seed14_feasibility_only",
            "threshold_fit_performed": False, "heldout_inputs_opened": False,
            "input_bag": {
                "path": "/repo/research_paper/experiments/generated/t14_retained_inputs/T14_FORMAL_DEV14_CORRIDOR_INPUT_XM6_V1/sensors.bag",
                "sha256": EXPECTED_SEED14_BAG_SHA256,
            },
            "configuration": {
                "path": "/repo/research_paper/configs/point_lio_simulation_development.yaml",
                "sha256": EXPECTED_POINTLIO_CONFIG_SHA256,
            },
            "ros_master_uri": "http://127.0.0.1:41877",
            "native_binary": {"path": "/pointlio", "sha256": "binary"},
            "native_source": {"commit": PINNED_POINTLIO_COMMIT,
                              "files": {"source": "hash"}},
            "build_overlay": {"glog_prefix": "/glog", "glog_metadata": {"sha256": "glog"}},
            "repository_sources": {"runner": "runner-hash"},
            "process_exit_codes": {"rosbag": 0, "pointlio": 0,
                                   "pose_logger": 0, "roscore": 130,
                                   "exporter": 0 if mode == "on" else -2},
        }
        if mode == "on":
            sidecar = run / "sidecar"
            sidecar.mkdir()
            frame_fields = (
                "frame_id", "input_header_stamp_ns", "timestamp_ns", "timestamp_source",
                "segment_id", "source_stage", "frame_state", "run_state",
                "unavailable_reason", "expected_group_count", "processed_group_count",
                "empty_group_count", "accepted_count",
            )
            frames = [
                {"frame_id": 1, "input_header_stamp_ns": 1000, "timestamp_ns": 1100,
                 "timestamp_source": "ACTUAL", "segment_id": 0,
                 "source_stage": "MEASUREMENT", "frame_state": "READY",
                 "run_state": "COMPLETE", "unavailable_reason": "",
                 "expected_group_count": 1, "processed_group_count": 1,
                 "empty_group_count": 0, "accepted_count": 6},
                {"frame_id": 2, "input_header_stamp_ns": 2000, "timestamp_ns": 100002000,
                 "timestamp_source": "NOMINAL", "segment_id": 0,
                 "source_stage": "CALLBACK", "frame_state": "UNAVAILABLE",
                 "run_state": "COMPLETE", "unavailable_reason": "EMPTY_OR_FILTERED_INPUT",
                 "expected_group_count": 0, "processed_group_count": 0,
                 "empty_group_count": 0, "accepted_count": 0},
            ]
            write_csv(sidecar / "frame_ledger.csv", frame_fields, frames)
            write_csv(sidecar / "reset_events.csv", (
                "event_order", "affected_frame_id", "sensor_timestamp_ns",
                "reset_reason", "old_segment_id", "new_segment_id",
            ), [])
            indicator_fields = (
                "frame_id", "timestamp_ns", "timestamp_source", "segment_id",
                "valid", "unavailable_reason", "run_state",
            )
            write_csv(run / "pointlio_indicators.csv", indicator_fields, [
                {"frame_id": 1, "timestamp_ns": 1100, "timestamp_source": "ACTUAL",
                 "segment_id": 0, "valid": "true", "unavailable_reason": "",
                 "run_state": "COMPLETE"},
                {"frame_id": 2, "timestamp_ns": 100002000,
                 "timestamp_source": "NOMINAL", "segment_id": 0,
                 "valid": "false", "unavailable_reason": "EMPTY_OR_FILTERED_INPUT",
                 "run_state": "COMPLETE"},
            ])
        manifest["output_sha256"] = {
            str(path.relative_to(run)): sha256(path)
            for path in sorted(run.rglob("*"))
            if path.is_file()
        }
        (run / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return run

    def test_pass_requires_full_frame_coverage_and_byte_identical_poses(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            on = self.create_run(root, "on", "on")
            off = self.create_run(root, "off", "off")
            result = verify_pair(on, off)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["input_frame_count"], 2)
            self.assertEqual(result["indicator_row_count"], 2)
            self.assertEqual(result["pose_row_count"], 1)
            self.assertFalse(result["threshold_fit_performed"])
            self.assertFalse(result["heldout_inputs_opened"])

    def test_changed_pose_output_revises_the_pair(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            on = self.create_run(root, "on", "on")
            off = self.create_run(root, "off", "off")
            (off / "poses.csv").write_text("different", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed or are missing"):
                verify_pair(on, off)

    def test_changed_indicator_validity_revises_the_pair(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            on = self.create_run(root, "on", "on")
            off = self.create_run(root, "off", "off")
            indicator_path = on / "pointlio_indicators.csv"
            indicator_path.write_text(
                indicator_path.read_text(encoding="utf-8").replace(
                    "true,,COMPLETE", "false,INDICATOR_NUMERIC_FAILURE,COMPLETE"),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "changed or are missing"):
                verify_pair(on, off)

    def test_unmanifested_extra_output_revises_the_pair(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            on = self.create_run(root, "on", "on")
            off = self.create_run(root, "off", "off")
            (on / "unexpected.txt").write_text("extra", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "changed or are missing"):
                verify_pair(on, off)

    def test_failed_pose_logger_prevents_pair_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            on = self.create_run(root, "on", "on")
            off = self.create_run(root, "off", "off")
            manifest_path = on / "run_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["process_exit_codes"]["pose_logger"] = 1
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "required process"):
                verify_pair(on, off)

    def test_failed_roscore_prevents_pair_acceptance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            on = self.create_run(root, "on", "on")
            off = self.create_run(root, "off", "off")
            manifest_path = on / "run_manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["process_exit_codes"]["roscore"] = 1
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "ROS master"):
                verify_pair(on, off)


if __name__ == "__main__":
    unittest.main()
