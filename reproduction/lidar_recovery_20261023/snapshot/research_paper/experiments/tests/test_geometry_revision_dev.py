import math
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import geometry_revision_dev as candidate
import heldout_simulation as original
from simulate_lidar import raycast


class GeometryRevisionDevelopmentTests(unittest.TestCase):
    def test_spacing_including_end_gaps_is_bounded(self):
        for length in (8., 9., 12., 15., 18.):
            gaps = np.diff([0., *candidate.control_positions(length), length])
            self.assertTrue(np.all(gaps <= 2. + 1e-12))
            self.assertTrue(np.all(gaps > 0))

    def test_control_only_adds_features_without_changing_corridor_or_rooms(self):
        base = original.build_straight_surfaces(16., 1.4, 6.)
        self.assertEqual(candidate.build_candidate(16., 1.4, 6.), base)
        control = candidate.build_candidate(16., 1.4, 6., True)
        self.assertEqual(control[:len(base)], base)
        self.assertGreater(len(control) - len(base), 4)

    def test_new_baffles_leave_the_central_route_open(self):
        surfaces = candidate.build_candidate(16., 1.4, 6., True)
        distance = raycast(np.array([[8., 0., 0.]]), np.array([[1., 0., 0.]]), surfaces)
        self.assertGreater(distance[0], 8.)

    def test_long_narrow_development_fixture_has_informative_control(self):
        row = candidate.audit_dimensions(16.5, 1.4, 6.)
        self.assertLess(row['original_control_fraction'], .15)
        self.assertGreaterEqual(row['candidate_control_fraction'], .15)
        self.assertLessEqual(row['corridor_fraction'], .10)
        self.assertGreaterEqual(row['post_exit_fraction'], .20)

    def test_invalid_dimensions_are_rejected(self):
        for value in (0, -1, math.nan, math.inf):
            with self.assertRaises(ValueError):
                candidate.control_positions(value)
        with self.assertRaises(ValueError):
            candidate.build_candidate(16., math.nan, 6.)


if __name__ == '__main__':
    unittest.main()
