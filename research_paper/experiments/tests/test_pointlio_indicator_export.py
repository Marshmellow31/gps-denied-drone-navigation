import csv
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pointlio_indicator_export import export_sidecar  # noqa: E402


def write_rows(path, fields, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class PointLioIndicatorExportTests(unittest.TestCase):
    def fixture_files(self, root, *, common_rows=None, nonfinite_body=False,
                      rotation=None):
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
            {"frame_id": 2, "input_header_stamp_ns": 1100, "timestamp_ns": 100001100,
             "timestamp_source": "NOMINAL", "segment_id": 0,
             "source_stage": "CALLBACK", "frame_state": "UNAVAILABLE",
             "run_state": "COMPLETE", "unavailable_reason": "EMPTY_OR_FILTERED_INPUT",
             "expected_group_count": 0, "processed_group_count": 0,
             "empty_group_count": 0, "accepted_count": 0},
        ]
        group_fields = (
            "frame_id", "group_index", "group_timestamp_ns", "callback_count",
            "accepted_count", "rotation_snapshot_present",
            *(f"R{r}{c}" for r in range(3) for c in range(3)),
        )
        identity = np.eye(3) if rotation is None else np.asarray(rotation, dtype=float)
        group = {"frame_id": 1, "group_index": 0, "group_timestamp_ns": 1050,
                 "callback_count": 1, "accepted_count": 6,
                 "rotation_snapshot_present": "true"}
        group.update({f"R{r}{c}": identity[r, c] for r in range(3) for c in range(3)})

        row_fields = (
            "frame_id", "group_index", "group_timestamp_ns", "row_index",
            *(f"R{r}{c}" for r in range(3) for c in range(3)),
            *(f"J_body{i}" for i in range(6)),
            *(f"J_common{i}" for i in range(6)),
        )
        jacobians = []
        rows = np.eye(6)
        for index, row in enumerate(rows):
            body = row.copy()
            if nonfinite_body and index == 0:
                body[0] = float("nan")
            common = row.copy() if common_rows is None else common_rows[index]
            item = {"frame_id": 1, "group_index": 0,
                    "group_timestamp_ns": 1050, "row_index": index}
            item.update({f"R{r}{c}": identity[r, c]
                         for r in range(3) for c in range(3)})
            item.update({f"J_body{i}": body[i] for i in range(6)})
            item.update({f"J_common{i}": common[i] for i in range(6)})
            jacobians.append(item)

        frame_path = root / "frame_ledger.csv"
        group_path = root / "measurement_groups.csv"
        jacobian_path = root / "jacobian_rows.csv"
        write_rows(frame_path, frame_fields, frames)
        write_rows(group_path, group_fields, [group])
        write_rows(jacobian_path, row_fields, jacobians)
        return frame_path, group_path, jacobian_path

    def test_exports_one_diagnostic_per_raw_frame_and_fixed_scales(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frame, groups, rows = self.fixture_files(root)
            output = root / "indicators.csv"
            exported = export_sidecar(
                frame, groups, rows, output,
                expected_header_stamps_ns=[1000, 1100],
            )

            self.assertEqual(len(exported), 2)
            self.assertTrue(exported[0]["valid"])
            self.assertEqual(exported[0]["accepted_count"], 6)
            self.assertTrue(np.isfinite(exported[0]["lambda_min_3m"]))
            self.assertFalse(exported[1]["valid"])
            self.assertEqual(exported[1]["unavailable_reason"],
                             "EMPTY_OR_FILTERED_INPUT")
            with output.open(newline="", encoding="utf-8") as stream:
                text = output.read_text(encoding="utf-8")
                csv_rows = list(csv.DictReader(stream))
            self.assertEqual(len(csv_rows), 2)
            self.assertNotIn("Infinity", text)
            self.assertNotIn(",inf", text.lower())

    def test_raw_input_coverage_mismatch_fails_before_export(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frame, groups, rows = self.fixture_files(root)
            output = root / "indicators.csv"
            with self.assertRaisesRegex(ValueError, "frame count mismatch"):
                export_sidecar(frame, groups, rows, output,
                               expected_header_stamps_ns=[1000])
            self.assertFalse(output.exists())

    def test_source_row_reconstruction_mismatch_is_run_incomplete(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wrong_common = np.eye(6)
            wrong_common[0, 0] = 2.0
            frame, groups, rows = self.fixture_files(
                root, common_rows=wrong_common,
            )
            result = export_sidecar(frame, groups, rows, root / "out.csv")
            self.assertEqual(result[0]["run_state"], "RUN_INCOMPLETE")
            self.assertTrue(result[0]["unavailable_reason"].startswith(
                "SIDECAR_CONTRACT_FAILURE:"))

    def test_nonfinite_measurement_is_invalid_but_keeps_known_row_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frame, groups, rows = self.fixture_files(root, nonfinite_body=True)
            result = export_sidecar(frame, groups, rows, root / "out.csv")
            self.assertFalse(result[0]["valid"])
            self.assertEqual(result[0]["unavailable_reason"],
                             "INDICATOR_NUMERIC_FAILURE")
            self.assertEqual(result[0]["accepted_count"], 6)

    def test_nonfinite_captured_common_row_invalidates_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            common = np.eye(6)
            common[0, 0] = float("nan")
            frame, groups, rows = self.fixture_files(root, common_rows=common)
            result = export_sidecar(frame, groups, rows, root / "out.csv")
            self.assertFalse(result[0]["valid"])
            self.assertEqual(result[0]["unavailable_reason"],
                             "INDICATOR_NUMERIC_FAILURE")
            self.assertEqual(result[0]["accepted_count"], 6)

    def test_finite_improper_rotation_is_numeric_failure_not_run_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            improper = np.diag([2.0, 1.0, 1.0])
            frame, groups, rows = self.fixture_files(root, rotation=improper)
            result = export_sidecar(frame, groups, rows, root / "out.csv")
            self.assertEqual(result[0]["run_state"], "COMPLETE")
            self.assertFalse(result[0]["valid"])
            self.assertEqual(result[0]["unavailable_reason"],
                             "INDICATOR_NUMERIC_FAILURE")
            self.assertEqual(result[0]["accepted_count"], 6)


if __name__ == "__main__":
    unittest.main()
