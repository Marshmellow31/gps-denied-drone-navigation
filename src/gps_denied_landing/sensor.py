from __future__ import annotations

import math
import warnings

import numpy as np

from .models import GridMap, Observation, SensorProfile


def _nearest_height(terrain: GridMap, x_m: float, y_m: float) -> float | None:
    col = int((x_m - terrain.origin_xy_m[0]) / terrain.resolution_m)
    row = int((y_m - terrain.origin_xy_m[1]) / terrain.resolution_m)
    if row < 0 or col < 0 or row >= terrain.height_m.shape[0] or col >= terrain.height_m.shape[1]:
        return None
    return float(terrain.height_m[row, col])


def _fill_small_holes(height: np.ndarray, confidence: np.ndarray, passes: int) -> None:
    for _ in range(passes):
        missing = ~np.isfinite(height)
        if not missing.any():
            return
        padded_h = np.pad(height, 1, constant_values=np.nan)
        padded_c = np.pad(confidence, 1, constant_values=0.0)
        values: list[np.ndarray] = []
        confs: list[np.ndarray] = []
        for dr in range(3):
            for dc in range(3):
                if dr == 1 and dc == 1:
                    continue
                values.append(padded_h[dr : dr + height.shape[0], dc : dc + height.shape[1]])
                confs.append(padded_c[dr : dr + height.shape[0], dc : dc + height.shape[1]])
        stack = np.stack(values)
        valid_count = np.isfinite(stack).sum(axis=0)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            estimate = np.nanmedian(stack, axis=0)
        fill = missing & (valid_count >= 3)
        height[fill] = estimate[fill]
        confidence[fill] = np.max(np.stack(confs), axis=0)[fill] * 0.55


def simulate_multizone_scan(
    terrain: GridMap,
    profile: SensorProfile,
    seed: int,
    altitude_m: float = 1.50,
    scan_rows: int = 5,
    scan_span_m: float = 1.60,
    acquisition_duration_s: float = 10.0,
    interpolation_passes: int = 3,
) -> Observation:
    """Simulate a downward multizone ToF sensor accumulated during a short raster scan.

    The model intentionally includes range quantization, dropout, outliers, pose error,
    altitude error, and attitude error. It outputs the same local elevation-grid contract
    that a future hardware adapter must produce.
    """

    rng = np.random.default_rng(seed)
    rows, cols = terrain.height_m.shape
    sums = np.zeros((rows, cols), dtype=np.float64)
    sums_sq = np.zeros((rows, cols), dtype=np.float64)
    counts = np.zeros((rows, cols), dtype=np.int16)

    half_x = math.radians(profile.horizontal_fov_deg / 2)
    half_y = math.radians(profile.vertical_fov_deg / 2)
    angles_x = np.linspace(-half_x, half_x, profile.zones_x, dtype=np.float64)
    angles_y = np.linspace(-half_y, half_y, profile.zones_y, dtype=np.float64)
    frame_total = max(scan_rows, int(round(profile.frame_rate_hz * acquisition_duration_s)))
    row_positions = np.linspace(-scan_span_m / 2, scan_span_m / 2, scan_rows)
    frames_per_row = int(math.ceil(frame_total / scan_rows))
    scan_poses: list[tuple[float, float]] = []
    for row_index, pose_y in enumerate(row_positions):
        x_positions = np.linspace(-scan_span_m / 2, scan_span_m / 2, frames_per_row)
        if row_index % 2:
            x_positions = x_positions[::-1]
        scan_poses.extend((float(pose_x), float(pose_y)) for pose_x in x_positions)
    scan_poses = scan_poses[:frame_total]
    raw_samples = 0
    frame_count = 0
    drift_x = 0.0
    drift_y = 0.0
    yaw_drift = 0.0
    time_step_s = 1.0 / profile.frame_rate_hz

    for pose_x, pose_y in scan_poses:
        frame_count += 1
        drift_step = profile.pose_random_walk_m_sqrt_s * math.sqrt(time_step_s)
        drift_x += rng.normal(0.0, drift_step)
        drift_y += rng.normal(0.0, drift_step)
        yaw_drift += math.radians(
            rng.normal(0.0, profile.yaw_random_walk_deg_sqrt_s * math.sqrt(time_step_s))
        )
        estimated_pose_x = pose_x + drift_x + rng.normal(0.0, profile.pose_xy_std_m)
        estimated_pose_y = pose_y + drift_y + rng.normal(0.0, profile.pose_xy_std_m)
        estimated_altitude = altitude_m + rng.normal(0.0, profile.altitude_std_m)
        roll_error = math.radians(rng.normal(0.0, profile.attitude_std_deg))
        pitch_error = math.radians(rng.normal(0.0, profile.attitude_std_deg))

        for ay in angles_y:
            for ax in angles_x:
                true_x = pose_x + altitude_m * math.tan(ax)
                true_y = pose_y + altitude_m * math.tan(ay)
                true_height = _nearest_height(terrain, true_x, true_y)
                if true_height is None or rng.random() < profile.dropout_probability:
                    continue

                ray_scale = math.sqrt(1.0 + math.tan(ax) ** 2 + math.tan(ay) ** 2)
                true_range = (altitude_m - true_height) * ray_scale
                if true_range <= 0 or true_range > profile.max_range_m:
                    continue

                measured = true_range + rng.normal(0.0, profile.range_noise_std_m)
                if rng.random() < profile.outlier_probability:
                    measured += rng.choice((-1.0, 1.0)) * rng.uniform(0.08, 0.25)
                measured = round(measured / profile.range_quantization_m) * profile.range_quantization_m

                offset_x = estimated_altitude * math.tan(ax)
                offset_y = estimated_altitude * math.tan(ay)
                estimated_x = estimated_pose_x + math.cos(yaw_drift) * offset_x - math.sin(yaw_drift) * offset_y
                estimated_y = estimated_pose_y + math.sin(yaw_drift) * offset_x + math.cos(yaw_drift) * offset_y
                attitude_height_error = (
                    (estimated_x - estimated_pose_x) * math.tan(pitch_error)
                    + (estimated_y - estimated_pose_y) * math.tan(roll_error)
                )
                estimated_height = estimated_altitude - measured / ray_scale + attitude_height_error

                col = int((estimated_x - terrain.origin_xy_m[0]) / terrain.resolution_m)
                row = int((estimated_y - terrain.origin_xy_m[1]) / terrain.resolution_m)
                if 0 <= row < rows and 0 <= col < cols:
                    sums[row, col] += estimated_height
                    sums_sq[row, col] += estimated_height * estimated_height
                    counts[row, col] += 1
                    raw_samples += 1

    height = np.full((rows, cols), np.nan, dtype=np.float32)
    measured_cells = counts > 0
    height[measured_cells] = (sums[measured_cells] / counts[measured_cells]).astype(np.float32)
    variance = np.zeros((rows, cols), dtype=np.float32)
    variance[measured_cells] = np.maximum(
        0.0,
        sums_sq[measured_cells] / counts[measured_cells] - height[measured_cells] ** 2,
    )
    confidence = np.zeros((rows, cols), dtype=np.float32)
    confidence[measured_cells] = np.clip(counts[measured_cells] / 3.0, 0.0, 1.0) * np.exp(
        -variance[measured_cells] / max(profile.range_noise_std_m**2 * 4, 1e-9)
    )
    _fill_small_holes(height, confidence, interpolation_passes)

    return Observation(
        height_m=height,
        confidence=confidence,
        sample_count=counts,
        resolution_m=terrain.resolution_m,
        origin_xy_m=terrain.origin_xy_m,
        raw_sample_count=raw_samples,
        frame_count=frame_count,
    )
