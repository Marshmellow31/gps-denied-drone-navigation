"""Development ray-cast LiDAR/IMU model. Truth is not an estimator input.

Rectangular surfaces are opaque, double-sided, static, and Lambertian.
No intensity/material model. This module is independent of ROS.
"""
from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Surface:
    axis: int
    coordinate: float
    bounds: tuple


def raycast(origins, directions, surfaces, min_range=.2, max_range=60.):
    """Nearest positive ray/rectangle intersection; missing returns are NaN."""
    origins = np.broadcast_to(np.asarray(origins, dtype=float), directions.shape)
    directions = np.asarray(directions, dtype=float)
    if not np.allclose(np.linalg.norm(directions, axis=1), 1., atol=1e-10):
        raise ValueError('directions must be unit vectors')
    distances = np.full(len(directions), np.inf)
    for surface in surfaces:
        others = [i for i in range(3) if i != surface.axis]
        denominator = directions[:, surface.axis]
        candidate = np.full(len(directions), np.inf)
        np.divide(surface.coordinate - origins[:, surface.axis], denominator,
                  out=candidate, where=np.abs(denominator) > 1e-12)
        good = np.isfinite(candidate) & (candidate >= min_range) & (candidate <= max_range)
        for index, (low, high) in zip(others, surface.bounds):
            crossing = origins[:, index] + np.where(np.isfinite(candidate), candidate, 0.) * directions[:, index]
            good &= (crossing >= low) & (crossing <= high)
        distances = np.minimum(distances, np.where(good, candidate, np.inf))
    return np.where(np.isfinite(distances), distances, np.nan)


def scene(control=False):
    """Two rooms joined through 4 m doorways by a 12 m corridor.

    The wall shoulders close the room/corridor joins outside the open doorway.
    The matched control adds corridor baffles without changing the trajectory.
    """
    surfaces = []
    for xmin, xmax, width in [(-12., 0., 6.), (0., 12., 2.), (12., 30., 6.)]:
        surfaces += [Surface(1, side * width, ((xmin, xmax), (-1., 2.))) for side in (-1, 1)]
        surfaces += [Surface(2, height, ((xmin, xmax), (-width, width))) for height in (-1., 2.)]
    # End walls and asymmetric, partial-width baffles in rich rooms.
    surfaces += [Surface(0, -12., ((-6., 6.), (-1., 2.))),
                 Surface(0, 30., ((-6., 6.), (-1., 2.)))]
    # Close each doorway plane outside the corridor opening. Bounds are
    # (y,z), and the inclusive edges make the wall visible at the jamb joins.
    for x in (0., 12.):
        surfaces += [Surface(0, x, (interval, (-1., 2.)))
                     for interval in ((-6., -2.), (2., 6.))]
    for x, side in [(-8., -1), (-2., 1), (15., -1), (19., 1), (24., -1)]:
        bounds = (-5., -2.5) if side < 0 else (2.5, 5.)
        surfaces.append(Surface(0, x, (bounds, (-1., 1.5))))
    if control:
        for x in (2., 5., 8., 11.):
            surfaces.append(Surface(0, x, ((1.3, 2.), (-1., 1.5))))
    return surfaces


def randomized_straight_scene(layout_seed, control=False):
    """Seeded straight-corridor geometry for the T12 development split.

    Corridor length and half-width are drawn from the central development
    ranges in data/SPLITS.csv. The control shares every sampled dimension and
    rich-room surface, then adds four corridor baffles.
    """
    if int(layout_seed) != layout_seed or layout_seed < 0:
        raise ValueError('layout_seed must be a non-negative integer')
    rng = np.random.default_rng(np.random.SeedSequence([int(layout_seed), 0x4C494441]))
    length = float(rng.uniform(9., 13.))
    corridor_half_width = float(rng.uniform(1.6, 2.4))
    room_half_width = float(rng.uniform(4.5, 7.5))
    surfaces = []
    regions = [(-12., 0., room_half_width),
               (0., length, corridor_half_width),
               (length, 50., room_half_width)]
    for xmin, xmax, width in regions:
        surfaces += [Surface(1, side * width, ((xmin, xmax), (-1., 2.)))
                     for side in (-1, 1)]
        surfaces += [Surface(2, height, ((xmin, xmax), (-width, width)))
                     for height in (-1., 2.)]
    surfaces += [Surface(0, -12., ((-room_half_width, room_half_width), (-1., 2.))),
                 Surface(0, 50., ((-room_half_width, room_half_width), (-1., 2.)))]
    for x in (0., length):
        surfaces += [Surface(0, x, (interval, (-1., 2.)))
                     for interval in ((-room_half_width, -corridor_half_width),
                                      (corridor_half_width, room_half_width))]
    # Asymmetric, partial-width rich-room baffles, scaled to room width.
    baffle_specs = [(-8., -1), (-2., 1), (length + 3., -1),
                    (length + 7., 1), (length + 12., -1)]
    for x, side in baffle_specs:
        low, high = .42 * room_half_width, .83 * room_half_width
        bounds = (-high, -low) if side < 0 else (low, high)
        surfaces.append(Surface(0, x, (bounds, (-1., 1.5))))
    if control:
        for index in range(1, 5):
            x = length * index / 5.
            surfaces.append(Surface(0, x,
                                    ((.65 * corridor_half_width, corridor_half_width),
                                     (-1., 1.5))))
    metadata = {
        'layout_family': 'straight_randomized_development',
        'layout_seed': int(layout_seed),
        'corridor_length_m': length,
        'corridor_half_width_m': corridor_half_width,
        'room_half_width_m': room_half_width,
        'entry_plane_x_m': 0.,
        'exit_plane_x_m': length,
        'entry_time_s': crossing_time_x(0.),
        'exit_time_s': crossing_time_x(length),
        'control_baffles': bool(control),
        'corridor_baffle_x_m': [length * index / 5. for index in range(1, 5)] if control else [],
    }
    return surfaces, metadata


def crossing_time_x(x_m):
    """Body-path time at a longitudinal plane x after the smooth speed ramp."""
    return 3. + (5. + float(x_m)) / .8


def trajectory(times):
    """Analytic world-from-body pose and ideal body IMU; sensors are collocated.

The body rests for 2 s, follows a quintic smoothstep speed ramp to 0.8 m/s
over 2 s, then travels with small lateral/vertical path curvature and smooth
roll, pitch and yaw. Acceleration and body angular velocity are analytic.
World axes are right-handed z-up; gravity is (0,0,-9.80665) m/s^2.
"""
    times = np.asarray(times, dtype=float)
    u = np.maximum(0., times - 2.)
    ramp = np.clip(u / 2., 0., 1.)
    smooth = 10. * ramp**3 - 15. * ramp**4 + 6. * ramp**5
    integrated_smooth = 2.5 * ramp**4 - 3. * ramp**5 + ramp**6
    distance = np.where(u < 2., 1.6 * integrated_smooth, .8 * (u - 1.))
    speed = np.where(u < 2., .8 * smooth, .8)
    speed = np.where(times < 2., 0., speed)
    acceleration_x = np.where(
        (u > 0.) & (u < 2.),
        .4 * (30. * ramp**2 - 60. * ramp**3 + 30. * ramp**4),
        0.,
    )

    lateral_k = .25
    lateral = .20 * (1. - np.cos(lateral_k * distance))
    lateral_velocity = .20 * lateral_k * np.sin(lateral_k * distance) * speed
    lateral_acceleration = (
        .20 * lateral_k**2 * np.cos(lateral_k * distance) * speed**2
        + .20 * lateral_k * np.sin(lateral_k * distance) * acceleration_x
    )
    vertical_k = .25
    vertical = .04 * np.sin(vertical_k * distance)
    vertical_velocity = .04 * vertical_k * np.cos(vertical_k * distance) * speed
    vertical_acceleration = (
        -.04 * vertical_k**2 * np.sin(vertical_k * distance) * speed**2
        + .04 * vertical_k * np.cos(vertical_k * distance) * acceleration_x
    )

    yaw = .08 * (1. - np.cos(.4 * u))
    yaw_rate = .032 * np.sin(.4 * u)
    roll = .035 * np.sin(.20 * distance)
    pitch = .045 * np.sin(.13 * distance)
    roll_rate = .007 * np.cos(.20 * distance) * speed
    pitch_rate = .00585 * np.cos(.13 * distance) * speed

    cr, sr = np.cos(roll), np.sin(roll)
    cp, sp = np.cos(pitch), np.sin(pitch)
    cy, sy = np.cos(yaw), np.sin(yaw)
    rotation = np.zeros((len(times), 3, 3))
    rotation[:, 0, 0] = cy * cp
    rotation[:, 0, 1] = cy * sp * sr - sy * cr
    rotation[:, 0, 2] = cy * sp * cr + sy * sr
    rotation[:, 1, 0] = sy * cp
    rotation[:, 1, 1] = sy * sp * sr + cy * cr
    rotation[:, 1, 2] = sy * sp * cr - cy * sr
    rotation[:, 2, 0] = -sp
    rotation[:, 2, 1] = cp * sr
    rotation[:, 2, 2] = cp * cr

    position = np.column_stack((-5. + distance, lateral, vertical))
    acceleration_world = np.column_stack((acceleration_x, lateral_acceleration,
                                           vertical_acceleration))
    gravity_world = np.array([0., 0., -9.80665])
    specific_force = np.einsum('nji,nj->ni', rotation,
                               acceleration_world - gravity_world)
    gyro = np.column_stack((
        roll_rate - yaw_rate * sp,
        pitch_rate * cr + yaw_rate * sr * cp,
        -pitch_rate * sr + yaw_rate * cr * cp,
    ))

    half_roll, half_pitch, half_yaw = roll / 2., pitch / 2., yaw / 2.
    crh, srh = np.cos(half_roll), np.sin(half_roll)
    cph, sph = np.cos(half_pitch), np.sin(half_pitch)
    cyh, syh = np.cos(half_yaw), np.sin(half_yaw)
    quaternion = np.column_stack((
        srh * cph * cyh - crh * sph * syh,
        crh * sph * cyh + srh * cph * syh,
        crh * cph * syh - srh * sph * cyh,
        crh * cph * cyh + srh * sph * syh,
    ))
    return position, rotation, quaternion, specific_force, gyro


def simulate_imu_biases(times, rng, gyro_initial_sd=.003,
                        accel_initial_sd=.03, gyro_walk_sd=.0001,
                        accel_walk_sd=.001):
    """Seeded constant bias plus per-axis random walk at supplied sample times.

    Random-walk increments scale with sqrt(elapsed seconds). Parameters are
    explicit development stress settings, not a calibration claim.
    """
    times = np.asarray(times, dtype=float)
    if times.ndim != 1 or len(times) == 0 or not np.isfinite(times).all():
        raise ValueError('times must be a non-empty finite one-dimensional array')
    if np.any(np.diff(times) <= 0.):
        raise ValueError('times must be strictly increasing')
    gyro_bias = np.empty((len(times), 3), dtype=float)
    accel_bias = np.empty((len(times), 3), dtype=float)
    gyro_bias[0] = rng.normal(0., gyro_initial_sd, 3)
    accel_bias[0] = rng.normal(0., accel_initial_sd, 3)
    for index, dt in enumerate(np.diff(times), start=1):
        gyro_bias[index] = gyro_bias[index - 1] + rng.normal(
            0., gyro_walk_sd * np.sqrt(dt), 3)
        accel_bias[index] = accel_bias[index - 1] + rng.normal(
            0., accel_walk_sd * np.sqrt(dt), 3)
    return gyro_bias, accel_bias


def scan(start_s, surfaces, rng, azimuth_count=360, ring_count=16, noise_sd=.01):
    offsets = np.repeat(np.arange(azimuth_count) / azimuth_count * .1, ring_count)
    azimuth = np.repeat(np.arange(azimuth_count) / azimuth_count * 2 * np.pi, ring_count)
    elevation = np.tile(np.linspace(-15., 15., ring_count) * np.pi / 180., azimuth_count)
    directions = np.column_stack((np.cos(elevation) * np.cos(azimuth),
                                  np.cos(elevation) * np.sin(azimuth), np.sin(elevation)))
    position, rotation, _, _, _ = trajectory(start_s + offsets)
    world_directions = np.einsum('nij,nj->ni', rotation, directions)
    ranges = raycast(position, world_directions, surfaces)
    good = np.isfinite(ranges)
    # Draw per emitted ray before visibility masking so paired scenes preserve
    # noise for shared rays even when their return counts differ.
    ranges[good] += rng.normal(0., noise_sd, len(ranges))[good]
    points = directions[good] * ranges[good, None]
    rings = np.tile(np.arange(ring_count), azimuth_count)[good]
    return points, offsets[good], rings
