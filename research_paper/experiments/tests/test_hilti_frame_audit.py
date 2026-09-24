"""Small independent checks for the Hilti frame diagnostic's quaternion math."""

import importlib.util
from pathlib import Path
import unittest

import numpy as np


MODULE = Path(__file__).resolve().parents[1] / "src" / "audit_hilti_gyro_reference.py"
SPEC = importlib.util.spec_from_file_location("audit_hilti_gyro_reference", MODULE)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class HiltiFrameAuditTests(unittest.TestCase):
    def test_positive_z_turn_in_world_from_body_pose(self):
        q = np.array([[0.0, 0.0, 0.0, 1.0],
                      [0.0, 0.0, np.sin(np.pi / 4), np.cos(np.pi / 4)]])
        rates, durations = AUDIT.reference_body_rates(np.array([0.0, 1.0]), q)
        np.testing.assert_allclose(rates[0], [0.0, 0.0, np.pi / 2], atol=1e-12)
        np.testing.assert_allclose(durations, [1.0])

    def test_inverse_pose_reverses_simple_z_turn(self):
        q = np.array([[0.0, 0.0, 0.0, 1.0],
                      [0.0, 0.0, np.sin(np.pi / 4), np.cos(np.pi / 4)]])
        q[:, :3] *= -1
        rates, _ = AUDIT.reference_body_rates(np.array([0.0, 1.0]), q)
        np.testing.assert_allclose(rates[0], [0.0, 0.0, -np.pi / 2], atol=1e-12)


if __name__ == "__main__":
    unittest.main()
