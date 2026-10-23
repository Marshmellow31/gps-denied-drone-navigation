import sys
import unittest
from pathlib import Path

import numpy as np


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from fastlio_information import measurement_information  # noqa: E402


class FastlioInformationTests(unittest.TestCase):
    def calc(self, points, normals, scale=1.0):
        return measurement_information(points, normals, np.eye(3), np.eye(3),
                                       np.zeros(3), lever_scale_m=scale)

    def test_one_plane_has_unconstrained_directions(self):
        a, b = np.meshgrid(np.linspace(-2, 2, 8), np.linspace(-2, 2, 8))
        points = np.column_stack((a.ravel(), b.ravel(), np.full(a.size, 3.0)))
        normals = np.tile([0.0, 0.0, 1.0], (len(points), 1))
        result = self.calc(points, normals)
        self.assertTrue(result["valid"])
        self.assertLess(result["minimum_eigenvalue"], 1e-9)
        self.assertGreater(result["eigenvalues"][-1], 0)

    def test_three_orthogonal_planes_are_better_constrained(self):
        a, b = np.meshgrid(np.linspace(-2, 2, 8), np.linspace(-2, 2, 8))
        xy = np.column_stack((a.ravel(), b.ravel(), np.full(a.size, 3.0)))
        yz = np.column_stack((np.full(a.size, 3.0), a.ravel(), b.ravel()))
        xz = np.column_stack((a.ravel(), np.full(a.size, 3.0), b.ravel()))
        points = np.vstack((xy, yz, xz))
        normals = np.vstack((np.tile([0.0, 0.0, 1.0], (len(xy), 1)),
                             np.tile([1.0, 0.0, 0.0], (len(yz), 1)),
                             np.tile([0.0, 1.0, 0.0], (len(xz), 1))))
        result = self.calc(points, normals)
        self.assertTrue(result["valid"])
        self.assertGreater(result["minimum_eigenvalue"], 1.0)

    def test_jacobian_matches_pinned_backend_first_six_columns(self):
        points = np.tile([2.0, 0.0, 0.0], (6, 1))
        normals = np.tile([0.0, 1.0, 0.0], (6, 1))
        result = self.calc(points, normals, scale=2.0)
        expected = np.array([0.0, 1.0, 0.0, 0.0, 0.0, 1.0])
        np.testing.assert_allclose(result["information"],
                                   np.outer(expected, expected) / 0.001)

    def test_unavailable_not_zero(self):
        result = self.calc(np.zeros((0, 3)), np.zeros((0, 3)))
        self.assertFalse(result["valid"])
        self.assertNotIn("minimum_eigenvalue", result)


if __name__ == "__main__":
    unittest.main()
