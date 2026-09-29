import sys
import unittest
from pathlib import Path

import numpy as np
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pointlio_information import (  # noqa: E402
    PointLioGroupRows,
    compute_pointlio_frame,
    join_emitted_pose_segments,
    transport_group_rows_to_world,
)


def rotation_z(angle_rad):
    cosine = np.cos(angle_rad)
    sine = np.sin(angle_rad)
    return np.array([[cosine, -sine, 0.0],
                     [sine, cosine, 0.0],
                     [0.0, 0.0, 1.0]], dtype=np.float64)


class PointLioInformationTests(unittest.TestCase):
    def test_rotation_transport_uses_exact_preupdate_snapshot(self):
        rows_body = np.array([[1, 2, 3, 4, 5, 6]], dtype=np.float64)
        rotation_pre = rotation_z(np.pi / 2.0)
        rotation_post = np.eye(3)

        actual = transport_group_rows_to_world(rows_body, rotation_pre)
        expected = np.array([[1, 2, 3, -5, 4, 6]], dtype=np.float64)
        wrong_postupdate = transport_group_rows_to_world(rows_body, rotation_post)

        np.testing.assert_allclose(actual, expected, atol=1e-14)
        self.assertFalse(np.allclose(actual, wrong_postupdate))

    def test_frame_pools_rows_after_group_specific_rotation_transport(self):
        rows0 = np.eye(6, dtype=np.float64)
        rows1 = np.eye(6, dtype=np.float64) * 2.0
        rotation0 = np.eye(3, dtype=np.float64)
        rotation1 = rotation_z(np.pi / 2.0)
        groups = [
            PointLioGroupRows(0, rows0, rotation0),
            PointLioGroupRows(1, rows1, rotation1),
        ]
        common = np.vstack((
            transport_group_rows_to_world(rows0, rotation0),
            transport_group_rows_to_world(rows1, rotation1),
        ))

        result = compute_pointlio_frame(
            groups, frame_id=7, expected_group_count=2,
            processed_group_count=2,
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["accepted_count"], 12)
        np.testing.assert_allclose(result["hessian_common"], common.T @ common)
        for lever_scale in (1, 3, 5):
            scale = np.diag([1, 1, 1, 1 / lever_scale,
                             1 / lever_scale, 1 / lever_scale])
            expected = scale @ (common.T @ common) @ scale / (12 * 0.001)
            np.testing.assert_allclose(result[f"G_{lever_scale}m"], expected)

    def test_zero_correspondence_groups_do_not_reject_otherwise_valid_frame(self):
        rows = np.tile(np.eye(6, dtype=np.float64)[:3], (1, 1))
        groups = [
            PointLioGroupRows(0, rows, np.eye(3)),
            PointLioGroupRows(1, np.empty((0, 6)), rotation_z(0.4)),
            PointLioGroupRows(2, rows, rotation_z(-0.2)),
        ]
        result = compute_pointlio_frame(
            groups, frame_id=8, expected_group_count=3,
            processed_group_count=3,
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["empty_group_count"], 1)
        self.assertEqual(result["accepted_count"], 6)

    def test_rank_deficient_finite_frame_is_valid_and_degenerate(self):
        row = np.array([[0.0, 1.0, 0.0, 0.0, 0.0, 0.0]])
        result = compute_pointlio_frame(
            [PointLioGroupRows(0, np.repeat(row, 6, axis=0), np.eye(3))],
            frame_id=9, expected_group_count=1,
            processed_group_count=1,
        )
        self.assertTrue(result["valid"])
        self.assertEqual(result["lambda_min_3m"], 0.0)
        self.assertTrue(result["dcreg"].valid)
        self.assertEqual(result["dcreg"].state, "DEGENERATE")
        self.assertEqual(result["dcreg"].health_score, 0.0)

    def test_frame_total_below_six_is_unavailable(self):
        rows = np.tile([1.0, 0, 0, 0, 1.0, 0], (5, 1))
        result = compute_pointlio_frame(
            [PointLioGroupRows(0, rows, np.eye(3))],
            frame_id=10, expected_group_count=1,
            processed_group_count=1,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["unavailable_reason"],
                         "INSUFFICIENT_CORRESPONDENCES")
        self.assertEqual(result["accepted_count"], 5)

    def test_partial_group_processing_is_run_incomplete(self):
        result = compute_pointlio_frame(
            [PointLioGroupRows(0, np.eye(6), np.eye(3))],
            frame_id=11, expected_group_count=2,
            processed_group_count=1,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["run_state"], "RUN_INCOMPLETE")
        self.assertEqual(result["unavailable_reason"],
                         "INCOMPLETE_GROUP_PROCESSING")

    def test_startup_and_empty_stages_require_zero_scheduled_groups(self):
        startup = compute_pointlio_frame(
            [], frame_id=1, expected_group_count=0,
            processed_group_count=0, source_stage="STARTUP",
            unavailable_reason="STARTUP_INITIALIZATION",
        )
        self.assertFalse(startup["valid"])
        self.assertEqual(startup["unavailable_reason"],
                         "STARTUP_INITIALIZATION")
        invalid_counts = compute_pointlio_frame(
            [], frame_id=2, expected_group_count=1,
            processed_group_count=0, source_stage="MAP_INITIALIZATION",
            unavailable_reason="MAP_INITIALIZATION",
        )
        self.assertEqual(invalid_counts["run_state"], "RUN_INCOMPLETE")

    def test_reset_in_frame_is_unavailable_even_with_valid_measurement_rows(self):
        result = compute_pointlio_frame(
            [PointLioGroupRows(0, np.eye(6), np.eye(3))],
            frame_id=3, expected_group_count=1,
            processed_group_count=1, unavailable_reason="RESET_IN_FRAME",
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["unavailable_reason"], "RESET_IN_FRAME")

    def test_scale_eigensolver_failure_invalidates_whole_frame(self):
        original = np.linalg.eigvalsh
        calls = 0

        def fail_on_first_scale(matrix):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise np.linalg.LinAlgError("fixture failure")
            return original(matrix)

        with patch("pointlio_information.np.linalg.eigvalsh",
                   side_effect=fail_on_first_scale):
            result = compute_pointlio_frame(
                [PointLioGroupRows(0, np.eye(6), np.eye(3))],
                frame_id=14, expected_group_count=1,
                processed_group_count=1,
            )
        self.assertFalse(result["valid"])
        self.assertEqual(result["unavailable_reason"],
                         "INDICATOR_NUMERIC_FAILURE")
        self.assertNotIn("G_3m", result)

    def test_numeric_failure_preserves_known_native_row_counts(self):
        good_rows = np.tile(np.eye(6, dtype=np.float64)[:3], (1, 1))
        bad_rows = good_rows.copy()
        bad_rows[0, 0] = np.nan
        groups = [
            PointLioGroupRows(0, good_rows, np.eye(3)),
            PointLioGroupRows(1, np.empty((0, 6)), np.eye(3)),
            PointLioGroupRows(2, bad_rows, np.eye(3)),
        ]
        result = compute_pointlio_frame(
            groups, frame_id=15, expected_group_count=3,
            processed_group_count=3,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["unavailable_reason"],
                         "INDICATOR_NUMERIC_FAILURE")
        self.assertEqual(result["accepted_count"], 6)
        self.assertEqual(result["empty_group_count"], 1)

    def test_nonfinite_rows_and_invalid_rotation_are_unavailable(self):
        nonfinite = np.eye(6, dtype=np.float64)
        nonfinite[0, 0] = np.nan
        result = compute_pointlio_frame(
            [PointLioGroupRows(0, nonfinite, np.eye(3))],
            frame_id=12, expected_group_count=1,
            processed_group_count=1,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["unavailable_reason"],
                         "INDICATOR_NUMERIC_FAILURE")

        bad_rotation = np.eye(3)
        bad_rotation[0, 0] = 2.0
        result = compute_pointlio_frame(
            [PointLioGroupRows(0, np.eye(6), bad_rotation)],
            frame_id=13, expected_group_count=1,
            processed_group_count=1,
        )
        self.assertFalse(result["valid"])
        self.assertEqual(result["unavailable_reason"],
                         "INDICATOR_NUMERIC_FAILURE")


class PointLioPoseJoinTests(unittest.TestCase):
    def frames(self):
        return [
            {"frame_id": 1, "timestamp_ns": 100, "timestamp_source": "ACTUAL",
             "segment_id": 0, "valid": True, "unavailable_reason": ""},
            {"frame_id": 2, "timestamp_ns": 201, "timestamp_source": "NOMINAL",
             "segment_id": 0, "valid": False,
             "unavailable_reason": "EMPTY_OR_FILTERED_INPUT"},
            {"frame_id": 3, "timestamp_ns": 300, "timestamp_source": "ACTUAL",
             "segment_id": 0, "valid": False, "unavailable_reason": "RESET_IN_FRAME"},
            {"frame_id": 4, "timestamp_ns": 400, "timestamp_source": "ACTUAL",
             "segment_id": 1, "valid": True, "unavailable_reason": ""},
        ]

    def test_missing_unavailable_pose_is_allowed_and_reset_is_shared(self):
        poses = [
            {"source_frame_id": 1, "timestamp_ns": 100},
            {"source_frame_id": 4, "timestamp_ns": 400},
        ]
        events = [{"affected_frame_id": 3, "old_segment_id": 0,
                   "new_segment_id": 1}]
        joined = join_emitted_pose_segments(poses, self.frames(), events)
        self.assertEqual([row["segment_id"] for row in joined], [0, 1])

    def test_pose_validity_is_not_replaced_by_health_validity(self):
        poses = [
            {"source_frame_id": 1, "timestamp_ns": 100,
             "valid": True, "unavailable_reason": ""},
            {"source_frame_id": 4, "timestamp_ns": 400,
             "valid": "false", "unavailable_reason": "POSE_INVALID"},
        ]
        joined = join_emitted_pose_segments(
            poses, self.frames(),
            [{"affected_frame_id": 3, "old_segment_id": 0,
              "new_segment_id": 1}],
        )
        self.assertTrue(joined[0]["valid"])
        self.assertEqual(joined[0]["unavailable_reason"], "")
        self.assertEqual(joined[1]["valid"], "false")
        self.assertEqual(joined[1]["unavailable_reason"], "POSE_INVALID")

    def test_pose_identity_timestamp_and_uniqueness_are_required(self):
        with self.assertRaisesRegex(ValueError, "no diagnostic row"):
            join_emitted_pose_segments(
                [{"source_frame_id": 8, "timestamp_ns": 100}],
                self.frames(), [],
            )
        with self.assertRaisesRegex(ValueError, "timestamp mismatch"):
            join_emitted_pose_segments(
                [{"source_frame_id": 1, "timestamp_ns": 101}],
                self.frames(), [],
            )
        with self.assertRaisesRegex(ValueError, "duplicate emitted pose"):
            join_emitted_pose_segments(
                [{"source_frame_id": 1, "timestamp_ns": 100},
                 {"source_frame_id": 1, "timestamp_ns": 100}],
                self.frames(), [],
            )

    def test_reset_ledger_requires_exact_event_frame_and_segment_changes(self):
        with self.assertRaisesRegex(ValueError, "missing frame_id"):
            join_emitted_pose_segments(
                [{"source_frame_id": 1, "timestamp_ns": 100}],
                self.frames(),
                [{"affected_frame_id": 3, "old_segment_id": 0,
                  "new_segment_id": 1},
                 {"affected_frame_id": 99, "old_segment_id": 1,
                  "new_segment_id": 2}],
            )

        jumped = self.frames()
        jumped[-1] = dict(jumped[-1], segment_id=2)
        with self.assertRaisesRegex(ValueError, "unexplained segment change"):
            join_emitted_pose_segments(
                [{"source_frame_id": 1, "timestamp_ns": 100}],
                jumped,
                [{"affected_frame_id": 3, "old_segment_id": 0,
                  "new_segment_id": 1}],
            )

        reset_frame_marked_valid = self.frames()
        reset_frame_marked_valid[2] = dict(
            reset_frame_marked_valid[2], valid=True
        )
        with self.assertRaisesRegex(ValueError, "not explicitly invalid"):
            join_emitted_pose_segments(
                [], reset_frame_marked_valid,
                [{"affected_frame_id": 3, "old_segment_id": 0,
                  "new_segment_id": 1}],
            )

    def test_reset_marker_without_matching_event_is_rejected(self):
        frames = self.frames()
        with self.assertRaisesRegex(ValueError, "has no reset event"):
            join_emitted_pose_segments([], frames, [])


if __name__ == "__main__":
    unittest.main()
