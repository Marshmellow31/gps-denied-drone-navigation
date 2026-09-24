import sys
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from trajectory_eval import (  # noqa: E402
    NSEC, Pose, ReferenceIndex, accumulated_error, alignment, evaluate,
    load_body_transform, load_estimates, load_reference, local_error, slerp, timestamp_ns,
)


IDENTITY_Q = np.array([0.0, 0.0, 0.0, 1.0])
IDENTITY_T = np.eye(4)


def pose(t, x=0.0, y=0.0, z=0.0, q=IDENTITY_Q, segment=0):
    return Pose(round(t*NSEC), np.array([x, y, z], dtype=float), np.array(q, dtype=float), segment)


class TrajectoryEvaluationTests(unittest.TestCase):
    def test_identical_trajectories_have_zero_local_and_accumulated_error(self):
        poses = [pose(t, x=t) for t in (0, 1, 2, 3)]
        reference = ReferenceIndex(poses, max_bracket_ns=2*NSEC)
        rows = evaluate(poses, reference, IDENTITY_T, 5*NSEC, "e", "r", windows_s=(1.0,))
        self.assertEqual(sum(row["local_valid"] for row in rows), 3)
        for row in rows:
            if row["local_valid"]:
                self.assertAlmostEqual(row["local_translation_error_m"], 0)
                self.assertAlmostEqual(row["local_rotation_error_rad"], 0)
            self.assertTrue(row["alignment_valid"])
            self.assertAlmostEqual(row["accumulated_translation_error_m"], 0)

    def test_known_increment_translation_and_rotation_error(self):
        q90 = np.array([0.0, 0.0, np.sqrt(0.5), np.sqrt(0.5)])
        ref = ReferenceIndex([pose(0), pose(1, x=1)], max_bracket_ns=2*NSEC)
        result, reason = local_error(pose(0), pose(1, x=2, q=q90), ref, IDENTITY_T)
        self.assertIsNone(reason)
        self.assertAlmostEqual(result[0], 1.0)
        self.assertAlmostEqual(result[1], np.pi/2)

    def test_constant_world_frame_change_is_removed_once(self):
        ref = ReferenceIndex([pose(0), pose(1, x=1), pose(2, x=2)], max_bracket_ns=2*NSEC)
        # World change is a 90-degree yaw plus a fixed translation.
        q90 = np.array([0.0, 0.0, np.sqrt(0.5), np.sqrt(0.5)])
        estimates = [pose(t, x=10, y=t, q=q90) for t in (0, 1, 2)]
        local, reason = local_error(estimates[0], estimates[1], ref, IDENTITY_T)
        self.assertIsNone(reason)
        self.assertAlmostEqual(local[0], 0, places=12)
        align, reason = alignment(estimates[0], ref, IDENTITY_T)
        self.assertIsNone(reason)
        for estimate in estimates:
            accumulated, reason = accumulated_error(estimate, ref, IDENTITY_T, align)
            self.assertIsNone(reason)
            self.assertAlmostEqual(accumulated[0], 0, places=12)

    def test_quaternion_sign_equivalence(self):
        q90 = np.array([0.0, 0.0, np.sqrt(0.5), np.sqrt(0.5)])
        halfway = slerp(q90, -q90, 0.5)
        self.assertAlmostEqual(abs(float(np.dot(halfway, q90))), 1.0)
        reference = ReferenceIndex([pose(0, q=q90), pose(1, q=-q90)], max_bracket_ns=2*NSEC)
        result, reason = local_error(pose(0, q=q90), pose(1, q=q90), reference, IDENTITY_T)
        self.assertIsNone(reason)
        self.assertAlmostEqual(result[1], 0)

    def test_reset_boundary_is_not_bridged(self):
        reference = ReferenceIndex([pose(0), pose(1, x=1)], max_bracket_ns=2*NSEC)
        result, reason = local_error(pose(0), pose(1, x=1, segment=1), reference, IDENTITY_T)
        self.assertIsNone(result)
        self.assertEqual(reason, "WINDOW_CROSSES_RESET")

    def test_reference_gaps_extrapolation_and_ambiguity(self):
        reference = ReferenceIndex([pose(0), pose(0.1, x=0.1), pose(0.1, x=0.1),
                                    pose(1, x=1), pose(1.1, x=1.1)])
        self.assertEqual(reference.associate(-1)[1], "REFERENCE_UNCOVERED")
        self.assertEqual(reference.associate(round(0.5*NSEC))[1], "REFERENCE_GAP")
        self.assertEqual(reference.associate(round(0.05*NSEC))[1], None)
        ambiguous = ReferenceIndex([pose(0), pose(0, x=1), pose(0.1)])
        self.assertEqual(ambiguous.associate(0)[1], "REFERENCE_AMBIGUOUS")
        result, reason = local_error(pose(0), pose(1, x=1), reference, None)
        self.assertIsNone(result)
        self.assertEqual(reason, "REFERENCE_GAP")

    def test_metric_scale_error_is_visible(self):
        reference = ReferenceIndex([pose(0), pose(1, x=1)], max_bracket_ns=2*NSEC)
        result, reason = local_error(pose(0), pose(1, x=2), reference, IDENTITY_T)
        self.assertIsNone(reason)
        self.assertAlmostEqual(result[0], 1.0)

    def test_decimal_timestamp_rounds_once(self):
        self.assertEqual(timestamp_ns("1.0000000005"), 1_000_000_000)
        self.assertEqual(timestamp_ns("1.0000000015"), 1_000_000_002)

    def test_reference_source_order_boundary_prevents_sort_bridging(self):
        # Global sorting would invent continuity at 0.1--0.2 seconds.
        reference = ReferenceIndex([pose(0), pose(0.1, x=1), pose(0.31, x=3),
                                    pose(0.2, x=2), pose(0.4, x=4)])
        self.assertEqual(reference.source_order_decreases, 1)
        self.assertEqual(reference.associate(round(0.15*NSEC))[1], "REFERENCE_GAP")
        self.assertIsNone(reference.associate(round(0.05*NSEC))[1])

    def test_reference_file_preserves_original_line_numbers(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ref.txt"
            path.write_text("0 0 0 0 0 0 0 1\n0.1 1 0 0 0 0 0 1\n")
            reference = load_reference(path)
            self.assertEqual([item.source_row for item in reference.poses], [1, 2])

    def test_reset_marker_is_retained_and_blocks_window_and_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "poses.csv"
            path.write_text("timestamp_ns,x_m,y_m,z_m,qx,qy,qz,qw,valid,unavailable_reason,segment_id,event\n"
                            "0,0,0,0,0,0,0,1,true,,0,POSE\n"
                            "1000000000,,,,,,,,false,POSE_RESET_BOUNDARY,1,RESET\n"
                            "1000000000,1,0,0,0,0,0,1,true,,1,POSE\n"
                            "2000000000,2,0,0,0,0,0,1,true,,1,POSE\n")
            estimates = load_estimates(path)
            reference = ReferenceIndex([pose(t, x=t) for t in (0, 1, 2)], max_bracket_ns=2*NSEC)
            rows = evaluate(estimates, reference, IDENTITY_T, 5*NSEC, "e", "r", windows_s=(1.0,))
            self.assertEqual(len(rows), 4)
            self.assertEqual(rows[0]["unavailable_reason"], "WINDOW_CROSSES_RESET")
            self.assertEqual(rows[1]["unavailable_reason"], "POSE_RESET_BOUNDARY")
            self.assertFalse(rows[1]["pose_valid"])
            self.assertTrue(rows[2]["local_valid"])
            self.assertFalse(rows[2]["alignment_valid"])

    def test_development_metadata_requires_explicit_scope_and_matching_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "ref.txt"
            reference.write_text("0 0 0 0 0 0 0 1\n")
            metadata_path = Path(directory) / "metadata.json"
            metadata_path.write_text(json.dumps({
                "verified": True, "evaluation_scope": "development_only", "clock_id": "test_clock",
                "source": {"artifact_name": "ref.txt", "sha256": hashlib.sha256(reference.read_bytes()).hexdigest()},
                "comparison_body": {"T_est_body_to_ref_body": IDENTITY_T.tolist()},
            }))
            with self.assertRaisesRegex(ValueError, "development-only"):
                load_body_transform(metadata_path, reference, False)
            np.testing.assert_array_equal(load_body_transform(metadata_path, reference, True), IDENTITY_T)
            reference.write_text("changed\n")
            with self.assertRaisesRegex(ValueError, "hash"):
                load_body_transform(metadata_path, reference, True)

    def test_window_uses_first_same_segment_endpoint(self):
        estimates = [pose(0), pose(0.96, x=0.96, segment=0),
                     pose(1.0, x=1, segment=1), pose(1.03, x=1.03, segment=0)]
        reference = ReferenceIndex([pose(t, x=t) for t in (0, 0.96, 1.0, 1.03)],
                                   max_bracket_ns=2*NSEC)
        rows = evaluate(estimates, reference, IDENTITY_T, 5*NSEC, "e", "r", windows_s=(1.0,))
        self.assertEqual(rows[0]["window_end_ns"], round(0.96*NSEC))
        self.assertTrue(rows[0]["local_valid"])

    def test_pose_clock_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "poses.csv"
            path.write_text("timestamp_ns,clock_id,x_m,y_m,z_m,qx,qy,qz,qw,valid,unavailable_reason,segment_id,event\n"
                            "0,wrong,0,0,0,0,0,0,1,true,,0,POSE\n")
            with self.assertRaisesRegex(ValueError, "POSE_CLOCK_UNMAPPED"):
                load_estimates(path, "expected")

    def test_explicit_pre_exit_anchor_is_not_confused_with_pre_entry(self):
        estimates = [pose(t, x=t) for t in (0, 1, 2)]
        reference = ReferenceIndex(estimates, max_bracket_ns=2*NSEC)
        rows = evaluate(estimates, reference, IDENTITY_T, None, "exit_only", "run",
                        windows_s=(1.0,), alignment_target_ns=0)
        self.assertTrue(all(row["alignment_valid"] for row in rows))
        without_anchor = evaluate(estimates, reference, IDENTITY_T, None, "exit_only", "run",
                                  windows_s=(1.0,))
        self.assertTrue(all(not row["alignment_valid"] for row in without_anchor))
        with self.assertRaisesRegex(ValueError, "either pre-entry"):
            evaluate(estimates, reference, IDENTITY_T, 5*NSEC, "e", "r",
                     alignment_target_ns=0)


if __name__ == "__main__":
    unittest.main()
