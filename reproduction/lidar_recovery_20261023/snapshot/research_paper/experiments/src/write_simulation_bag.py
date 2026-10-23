"""Generate one development sensor-only ROS bag plus separate truth artifacts."""
import argparse
import csv
import hashlib
import json
import subprocess
import time
from pathlib import Path
import numpy as np
from simulate_lidar import (scan, scene, randomized_straight_scene,
                            simulate_imu_biases, trajectory, crossing_time_x)


def main():
    import rosbag
    import rospy
    from sensor_msgs.msg import PointCloud2, PointField, Imu
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--duration', type=float, default=40.)
    parser.add_argument('--seed', type=int, default=10)
    parser.add_argument('--layout-family', choices=('fixed_v3', 'randomized_straight_dev'),
                        default='fixed_v3')
    parser.add_argument('--layout-seed', type=int)
    parser.add_argument('--control', action='store_true')
    args = parser.parse_args()
    if args.layout_family == 'fixed_v3':
        if args.seed not in range(10, 30):
            raise ValueError('fixed_v3 generator accepts development sensor seeds 10–29')
        surfaces = scene(args.control)
        layout_seed = None
        scene_geometry = {'layout_family': 'straight_v3_fixed',
                          'layout_seed': None, 'corridor_length_m': 12.,
                          'corridor_half_width_m': 2., 'room_half_width_m': 6.,
                          'entry_plane_x_m': 0., 'exit_plane_x_m': 12.,
                          'entry_time_s': crossing_time_x(0.),
                          'exit_time_s': crossing_time_x(12.),
                          'control_baffles': args.control}
    else:
        if args.seed not in range(14, 46):
            raise ValueError('randomized development layouts use seeds 14–45 only')
        layout_seed = args.layout_seed if args.layout_seed is not None else args.seed
        if layout_seed not in range(14, 46):
            raise ValueError('layout_seed must be a reserved development seed 14–45')
        surfaces, scene_geometry = randomized_straight_scene(layout_seed, args.control)
        if args.duration < scene_geometry['exit_time_s'] + 20.:
            raise ValueError('randomized development runs require at least 20 s after layout exit')
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=False)
    started = time.time()
    imu_noise_seed, lidar_seed, bias_seed = np.random.SeedSequence(args.seed).spawn(3)
    imu_noise_rng = np.random.default_rng(imu_noise_seed)
    lidar_rng = np.random.default_rng(lidar_seed)
    bias_rng = np.random.default_rng(bias_seed)
    imu_times = np.arange(round(args.duration * 200) + 21) / 200.
    gyro_bias, accel_bias = simulate_imu_biases(imu_times, bias_rng)
    epoch = 1000.
    point_fields = [PointField(name=n, offset=o, datatype=d, count=1)
                    for n, o, d in [('x', 0, 7), ('y', 4, 7), ('z', 8, 7),
                                    ('intensity', 12, 7), ('ring', 16, 4), ('time', 18, 7)]]
    dtype = np.dtype({'names': ['x', 'y', 'z', 'intensity', 'ring', 'time'],
                      'formats': ['<f4', '<f4', '<f4', '<f4', '<u2', '<f4'],
                      'offsets': [0, 4, 8, 12, 16, 18], 'itemsize': 22})
    scans = 0; points_total = 0
    with rosbag.Bag(str(root / 'sensors.bag'), 'w') as bag:
        for imu_index, t in enumerate(imu_times):
            _, _, _, force, gyro = trajectory(np.array([t]))
            msg = Imu(); msg.header.stamp = rospy.Time.from_sec(epoch + t)
            msg.header.frame_id = 'sim_body'
            msg.orientation_covariance[0] = -1
            msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z = force[0]
            msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z = gyro[0]
            gyro_measurement = gyro[0] + gyro_bias[imu_index] + imu_noise_rng.normal(0., .002, 3)
            accel_measurement = force[0] + accel_bias[imu_index] + imu_noise_rng.normal(0., .02, 3)
            msg.angular_velocity.x, msg.angular_velocity.y, msg.angular_velocity.z = gyro_measurement
            msg.linear_acceleration.x, msg.linear_acceleration.y, msg.linear_acceleration.z = accel_measurement
            bag.write('/sim/imu', msg, msg.header.stamp)
            if imu_index % 20 == 0 and t < args.duration:
                points, offsets, rings = scan(t, surfaces, lidar_rng)
                payload = np.empty(len(points), dtype=dtype)
                for index, name in enumerate(('x', 'y', 'z')): payload[name] = points[:, index]
                payload['intensity'] = 1.; payload['ring'] = rings; payload['time'] = offsets
                cloud = PointCloud2(); cloud.header.stamp = rospy.Time.from_sec(epoch + t)
                cloud.header.frame_id = 'sim_body'; cloud.height = 1; cloud.width = len(points)
                cloud.fields = point_fields; cloud.point_step = 22; cloud.row_step = len(points) * 22
                cloud.is_dense = True; cloud.data = payload.tobytes()
                # Deliver only once the rotating scan is acquired.
                bag.write('/sim/points', cloud, rospy.Time.from_sec(epoch + t + .1))
                scans += 1; points_total += len(points)
    with (root / 'reference.txt').open('w') as stream:
        times = np.arange(0, args.duration + .11, .005)
        p, _, q, _, _ = trajectory(times)
        for t, position, quaternion in zip(times, p, q):
            stream.write(f'{epoch + t:.9f} ' + ' '.join(f'{v:.17g}' for v in [*position, *quaternion]) + '\n')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
    diff = subprocess.check_output(['git', 'diff', 'HEAD', '--', 'research_paper'])
    manifest = {'role': 'development', 'seed': args.seed,
                'layout_family': args.layout_family, 'layout_seed': layout_seed,
                'scene_geometry': scene_geometry,
                'duration_s': args.duration,
                'control': args.control, 'scans': scans, 'points': points_total,
                'clock_id': 'simulation_epoch', 'epoch_s': epoch,
                'imu_model': {
                    'rate_hz': 200,
                    'gyro_white_noise_sd_rad_s': .002,
                    'accel_white_noise_sd_m_s2': .02,
                    'gyro_initial_bias_sd_rad_s': .003,
                    'accel_initial_bias_sd_m_s2': .03,
                    'gyro_bias_random_walk_sd_rad_s_per_sqrt_s': .0001,
                    'accel_bias_random_walk_sd_m_s2_per_sqrt_s': .001,
                    'gyro_bias_initial_rad_s': gyro_bias[0].tolist(),
                    'accel_bias_initial_m_s2': accel_bias[0].tolist(),
                    'gyro_bias_final_rad_s': gyro_bias[-1].tolist(),
                    'accel_bias_final_m_s2': accel_bias[-1].tolist(),
                    'bias_stream_seed': args.seed,
                },
                'runtime_s': time.time() - started, 'code_revision': revision,
                'dirty_diff_sha256': hashlib.sha256(diff).hexdigest(),
                'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'sensor_model_sha256': hashlib.sha256(Path(__file__).with_name('simulate_lidar.py').read_bytes()).hexdigest(),
                'truth_in_sensor_bag': False, 'status': 'completed',
                'limitations': ['ideal clocks and sensor extrinsics', 'prescribed smooth path and attitude',
                                'seeded Gaussian noise and random-walk bias settings are development stress values',
                                'axis-aligned rectangular surfaces', 'not final protocol']}
    for name in ('sensors.bag', 'reference.txt'):
        manifest[name] = {'size_bytes': (root / name).stat().st_size,
                          'sha256': hashlib.sha256((root / name).read_bytes()).hexdigest()}
    (root / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
