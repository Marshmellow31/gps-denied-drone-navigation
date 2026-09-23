import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from trajectory_eval import (  # noqa: E402
    NSEC, Pose, ReferenceIndex, accumulated_error, alignment, evaluate,
    local_error, slerp, timestamp_ns,
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


if __name__ == "__main__":
    unittest.main()
