import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from audit_hilti_scene_ranges import range_metrics  # noqa: E402


class SceneRangeTests(unittest.TestCase):
    def test_nonfinite_and_too_near_points_are_excluded(self):
        xyz = np.array([[1, 0, 0], [2, 0, 0], [4, 0, 0], [0, 0, 0], [np.nan, 0, 0]])
        count, near, p50, p90 = range_metrics(xyz)
        self.assertEqual(count, 3)
        self.assertAlmostEqual(near, 2/3)
        self.assertAlmostEqual(p50, 2)
        self.assertAlmostEqual(p90, 3.6)


if __name__ == "__main__":
    unittest.main()
