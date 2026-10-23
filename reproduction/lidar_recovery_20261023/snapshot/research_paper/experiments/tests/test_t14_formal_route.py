import argparse
import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import t14_formal_route as formal


class T14FormalRouteTests(unittest.TestCase):
    def test_formal_route_start_entry_and_exit_match_approved_times(self):
        surfaces, metadata = formal.formal_randomized_scene(14, control=False)
        exit_time = 3.0 + (6.0 + metadata["corridor_length_m"]) / 0.8
        sample_times = np.array([0.0, 1.5, 10.5, exit_time])
        position, rotation, quaternion, force, gyro = formal.formal_trajectory(sample_times)

        self.assertEqual(metadata["route_profile"], formal.PROFILE_ID)
        self.assertEqual(metadata["vehicle_start_x_m"], -6.0)
        self.assertAlmostEqual(metadata["entry_time_s"], 10.5)
        self.assertAlmostEqual(metadata["exit_time_s"], exit_time)
        self.assertAlmostEqual(position[0, 0], -6.0)
        self.assertAlmostEqual(position[1, 0], -6.0)
        self.assertAlmostEqual(position[2, 0], 0.0, places=10)
        self.assertAlmostEqual(position[3, 0], metadata["corridor_length_m"], places=10)
        self.assertTrue(np.isfinite(position).all())
        self.assertTrue(np.isfinite(rotation).all())
        self.assertTrue(np.isfinite(quaternion).all())
        self.assertTrue(np.isfinite(force).all())
        self.assertTrue(np.isfinite(gyro).all())

    def test_route_translation_preserves_imu_and_orientation(self):
        times = np.array([2.0, 7.0, 10.5, 25.0, 40.0])
        legacy = formal._BASE_TRAJECTORY(times)
        shifted = formal.formal_trajectory(times)
        np.testing.assert_allclose(shifted[0][:, 0], legacy[0][:, 0] - 1.0, atol=0.0)
        for index in range(1, 5):
            np.testing.assert_array_equal(shifted[index], legacy[index])

    def test_corridor_and_control_share_formal_route_and_base_surfaces(self):
        corridor, corridor_meta = formal.formal_randomized_scene(23, False)
        control, control_meta = formal.formal_randomized_scene(23, True)
        self.assertEqual(corridor, control[:len(corridor)])
        for key in ("corridor_length_m", "corridor_half_width_m", "room_half_width_m",
                    "entry_time_s", "exit_time_s", "vehicle_start_x_m", "route_profile"):
            self.assertEqual(corridor_meta[key], control_meta[key])
        self.assertFalse(corridor_meta["control_baffles"])
        self.assertTrue(control_meta["control_baffles"])
        self.assertEqual(len(control) - len(corridor), 4)

    def test_formal_crossing_formula(self):
        self.assertAlmostEqual(formal.formal_crossing_time_x(0.0), 10.5)
        self.assertAlmostEqual(formal.formal_crossing_time_x(18.0), 33.0)

    def test_seed_range_rejects_held_out_values(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            formal._parse_seed_range("100-119")
        self.assertEqual(formal._parse_seed_range("14-15"), [14, 15])


if __name__ == "__main__":
    unittest.main()
