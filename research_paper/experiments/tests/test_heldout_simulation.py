import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import heldout_simulation as heldout


class HeldoutSimulationSafetyTests(unittest.TestCase):
    def test_reserved_seed_strata_are_disjoint_and_cover_exact_protocol_ranges(self):
        expected = {
            100: "TEST_SHORT_NARROW", 119: "TEST_SHORT_NARROW",
            120: "TEST_SHORT_WIDE", 139: "TEST_SHORT_WIDE",
            140: "TEST_LONG_NARROW", 159: "TEST_LONG_NARROW",
            160: "TEST_LONG_WIDE", 179: "TEST_LONG_WIDE",
        }
        for seed, stratum in expected.items():
            self.assertEqual(heldout.stratum_for_seed(seed), stratum)
        for seed in (99, 180):
            with self.assertRaises(heldout.HeldoutContractError):
                heldout.stratum_for_seed(seed)

    def test_parameterized_development_fixture_shares_geometry_with_control(self):
        corridor = heldout.build_straight_surfaces(12.0, 2.0, 6.0, False)
        control = heldout.build_straight_surfaces(12.0, 2.0, 6.0, True)
        self.assertEqual(control[:len(corridor)], corridor)
        self.assertEqual(len(control) - len(corridor), 4)

    def test_development_fixture_doorway_is_open_and_shoulders_are_closed(self):
        import numpy as np
        from simulate_lidar import raycast

        surfaces = heldout.build_straight_surfaces(12.0, 2.0, 6.0, False)
        origins = np.array([[-1.0, 4.0, 0.0], [-1.0, 0.0, 0.0]])
        ranges = raycast(origins, np.array([[1.0, 0.0, 0.0]] * 2), surfaces)
        self.assertAlmostEqual(ranges[0], 1.0)
        self.assertGreater(ranges[1], 1.0)

    def test_out_of_stratum_seed_is_rejected_before_layout_sampling(self):
        with self.assertRaises(heldout.HeldoutContractError):
            heldout.sample_layout(14, "TEST_SHORT_NARROW")


if __name__ == "__main__":
    unittest.main()
