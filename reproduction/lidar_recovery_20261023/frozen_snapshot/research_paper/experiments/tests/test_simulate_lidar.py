import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from simulate_lidar import (Surface, raycast, trajectory, scene, scan,
                            simulate_imu_biases, randomized_straight_scene,
                            crossing_time_x)


class SimulatorTests(unittest.TestCase):
    def test_plane_distance_and_parallel_missing(self):
        result = raycast(np.zeros((2, 3)), np.array([[1., 0, 0], [0, 1., 0]]),
                         [Surface(0, 3., ((-1., 1.), (-1., 1.)))])
        self.assertEqual(result[0], 3.)
        self.assertTrue(np.isnan(result[1]))

    def test_nearest_surface_occludes_far_surface(self):
        result = raycast(np.zeros((1, 3)), np.array([[1., 0, 0]]),
                         [Surface(0, x, ((-1., 1.), (-1., 1.))) for x in (5., 2.)])
        self.assertEqual(result[0], 2.)

    def test_rectangle_bounds_and_range_rejection(self):
        result = raycast(np.array([[0., 2., 0.]]), np.array([[1., 0, 0]]),
                         [Surface(0, 3., ((-1., 1.), (-1., 1.)))])
        self.assertTrue(np.isnan(result[0]))

    def test_doorway_shoulders_block_outside_portal_and_leave_opening_visible(self):
        for control in (False, True):
            surfaces = scene(control)
            for x, origin_x in ((0., -1.), (12., 11.)):
                ys = [-4., -2., 2., 4., 0.]
                origins = np.array([[origin_x, y, 0.] for y in ys])
                shoulder = raycast(origins, np.array([[1., 0., 0.]] * len(ys)), surfaces)
                for index in range(4):
                    self.assertAlmostEqual(shoulder[index], x - origin_x)
                self.assertGreater(shoulder[4], x - origin_x)  # clear doorway

    def test_randomized_scene_is_deterministic_and_control_shares_geometry(self):
        plain, meta = randomized_straight_scene(14, control=False)
        repeat, repeat_meta = randomized_straight_scene(14, control=False)
        control, control_meta = randomized_straight_scene(14, control=True)
        self.assertEqual(plain, repeat)
        self.assertEqual(meta, repeat_meta)
        self.assertEqual(plain, control[:len(plain)])
        self.assertEqual(meta['corridor_length_m'], control_meta['corridor_length_m'])
        self.assertEqual(meta['corridor_half_width_m'], control_meta['corridor_half_width_m'])
        self.assertEqual(len(control) - len(plain), 4)
        self.assertTrue(9. <= meta['corridor_length_m'] <= 13.)
        self.assertTrue(1.6 <= meta['corridor_half_width_m'] <= 2.4)
        self.assertTrue(4.5 <= meta['room_half_width_m'] <= 7.5)
        self.assertNotEqual(meta['corridor_length_m'],
                            randomized_straight_scene(15)[1]['corridor_length_m'])

    def test_randomized_portals_and_exit_time_match_trajectory(self):
        surfaces, meta = randomized_straight_scene(14, control=False)
        length = meta['corridor_length_m']
        origin = np.array([[-1., meta['room_half_width_m'] - .1, 0.],
                           [-1., meta['corridor_half_width_m'], 0.],
                           [-1., 0., 0.]])
        distance = raycast(origin, np.array([[1., 0., 0.]] * 3), surfaces)
        self.assertAlmostEqual(distance[0], 1.)  # opaque outside shoulder
        self.assertAlmostEqual(distance[1], 1.)  # inclusive doorway jamb
        self.assertGreater(distance[2], 1.)      # open portal
        position, *_ = trajectory(np.array([meta['exit_time_s']]))
        self.assertAlmostEqual(position[0, 0], length, places=9)
        self.assertAlmostEqual(meta['exit_time_s'], crossing_time_x(length))

    def test_full_attitude_and_imu_match_independent_pose_derivatives(self):
        times = np.array([7.3, 13.7, 24.8])
        p, r, q, force, gyro = trajectory(times)
        self.assertGreater(np.max(np.abs(r[:, 2, 0])), .005)  # pitch present
        self.assertGreater(np.max(np.abs(r[:, 2, 1])), .005)  # roll present
        np.testing.assert_allclose(np.linalg.norm(q, axis=1), 1., atol=1e-12)

        h = 1e-3
        pm, rm, *_ = trajectory(times - h)
        pp, rp, *_ = trajectory(times + h)
        numerical_acceleration = (pp - 2. * p + pm) / h**2
        gravity = np.array([0., 0., -9.80665])
        imu_acceleration = np.einsum('nij,nj->ni', r, force) + gravity
        np.testing.assert_allclose(imu_acceleration, numerical_acceleration,
                                   atol=2e-5, rtol=2e-5)

        step = 1e-5
        _, r_after, *_ = trajectory(times + step)
        relative = np.einsum('nji,njk->nik', r, r_after)
        numerical_gyro = np.column_stack((
            relative[:, 2, 1] - relative[:, 1, 2],
            relative[:, 0, 2] - relative[:, 2, 0],
            relative[:, 1, 0] - relative[:, 0, 1],
        )) / (2. * step)
        np.testing.assert_allclose(gyro, numerical_gyro, atol=2e-5, rtol=2e-4)

    def test_seeded_imu_biases_are_repeatable_and_drift_smoothly(self):
        times = np.arange(0., 2.005, .005)
        gyro_a, accel_a = simulate_imu_biases(times, np.random.default_rng(41))
        gyro_b, accel_b = simulate_imu_biases(times, np.random.default_rng(41))
        np.testing.assert_array_equal(gyro_a, gyro_b)
        np.testing.assert_array_equal(accel_a, accel_b)
        self.assertGreater(np.linalg.norm(gyro_a[0]), 0.)
        self.assertGreater(np.linalg.norm(accel_a[0]), 0.)
        self.assertLess(np.max(np.abs(np.diff(gyro_a, axis=0))), .0001)
        self.assertLess(np.max(np.abs(np.diff(accel_a, axis=0))), .001)

    def test_stationary_imu_is_specific_force_not_gravity(self):
        p, r, q, acc, gyro = trajectory(np.array([0., 1.]))
        np.testing.assert_allclose(acc, [[0, 0, 9.80665]] * 2)
        np.testing.assert_allclose(gyro, 0)
        np.testing.assert_allclose(r, np.broadcast_to(np.eye(3), r.shape))

    def test_stationary_segment_has_zero_motion_and_rest_transition_is_smooth(self):
        times = np.array([0., 1.5, 2.])
        position, rotation, _, force, gyro = trajectory(times)
        np.testing.assert_allclose(position[:, 0], -5.)
        np.testing.assert_allclose(rotation, np.broadcast_to(np.eye(3), rotation.shape))
        np.testing.assert_allclose(force, [[0., 0., 9.80665]] * 3, atol=1e-12)
        np.testing.assert_allclose(gyro, 0., atol=1e-12)

    def test_smooth_acceleration_transform(self):
        times = np.array([3., 3.001])
        p, r, q, force, gyro = trajectory(times)
        h = 1e-3
        pm, *_ = trajectory(times - h)
        pp, *_ = trajectory(times + h)
        numerical_acceleration = (pp - 2. * p + pm) / h**2
        gravity = np.array([0., 0., -9.80665])
        np.testing.assert_allclose(np.einsum('nij,nj->ni', r, force) + gravity,
                                   numerical_acceleration, atol=2e-5, rtol=2e-5)
        self.assertTrue(np.isfinite(gyro).all())
        np.testing.assert_allclose(np.linalg.norm(q, axis=1), 1)

    def test_scan_timing_determinism_and_sensor_frame(self):
        a = scan(5., scene(), np.random.default_rng(10), noise_sd=0.)
        b = scan(5., scene(), np.random.default_rng(10), noise_sd=0.)
        for x, y in zip(a, b): np.testing.assert_array_equal(x, y)
        self.assertTrue(np.all(np.diff(a[1]) >= 0))
        self.assertTrue(np.all((a[1] >= 0) & (a[1] < .1)))
        p, r, _, _, _ = trajectory(5. + a[1])
        world = p + np.einsum('nij,nj->ni', r, a[0])
        self.assertTrue(np.isfinite(world).all())
