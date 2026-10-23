import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from audit_hilti_scene_structure import normal_information  # noqa: E402


@unittest.skipUnless(importlib.util.find_spec("scipy"), "SciPy is an isolated scene-audit dependency")
class SceneStructureTests(unittest.TestCase):
    def test_single_plane_has_weaker_normal_direction_than_three_planes(self):
        grid = np.linspace(-2, 2, 40)
        a, b = np.meshgrid(grid, grid)
        horizontal = np.column_stack((a.ravel(), b.ravel(), np.full(a.size, 3.0)))
        yz = np.column_stack((np.full(a.size, 3.0), a.ravel(), b.ravel()))
        xz = np.column_stack((a.ravel(), np.full(a.size, 3.0), b.ravel()))
        one = normal_information(horizontal, 20.0)
        three = normal_information(np.concatenate((horizontal, yz, xz)), 20.0)
        self.assertGreater(one["usable_normals"], 100)
        self.assertGreater(three["usable_normals"], 100)
        self.assertLess(one["eig_min"], 0.01)
        self.assertGreater(three["eig_min"], 0.1)


if __name__ == "__main__":
    unittest.main()
