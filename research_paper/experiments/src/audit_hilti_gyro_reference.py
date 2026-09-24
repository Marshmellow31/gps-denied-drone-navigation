"""Read-only, estimator-independent Hilti IMU/reference axis diagnostic.

Run with the isolated ROS Noetic environment's Python. The reference is never
passed to a backend. This diagnostic is not a trajectory-accuracy evaluator.
"""

import argparse
import json

import numpy as np


def quaternion_product(a, b):
    """Hamilton product of xyzw quaternion arrays."""
    av, aw = a[..., :3], a[..., 3]
    bv, bw = b[..., :3], b[..., 3]
    xyz = aw[..., None] * bv + bw[..., None] * av + np.cross(av, bv)
    w = aw * bw - np.sum(av * bv, axis=-1)
    return np.concatenate((xyz, w[..., None]), axis=-1)


def reference_body_rates(times, quaternions):
    """Body angular rate from consecutive world-from-body orientations."""
    q = quaternions / np.linalg.norm(quaternions, axis=1)[:, None]
    q0_inv = q[:-1].copy()
    q0_inv[:, :3] *= -1
    delta = quaternion_product(q0_inv, q[1:])
    delta[delta[:, 3] < 0] *= -1
    vector_norm = np.linalg.norm(delta[:, :3], axis=1)
    angle = 2 * np.arctan2(vector_norm, delta[:, 3])
    scale = np.divide(angle, vector_norm, out=np.full_like(angle, 2.0), where=vector_norm > 1e-12)
    dt = np.diff(times)
    return delta[:, :3] * (scale / dt)[:, None], dt


def main():
    import rosbag

    parser = argparse.ArgumentParser()
    parser.add_argument("bag")
    parser.add_argument("reference")
    args = parser.parse_args()

    reference = np.loadtxt(args.reference)
    if reference.ndim != 2 or reference.shape[1] != 8:
        raise ValueError("expected TUM timestamp xyz qx qy qz qw")
    times = reference[:, 0]
    rates, intervals = reference_body_rates(times, reference[:, 4:8])

    stamps, gyro = [], []
    with rosbag.Bag(args.bag, "r") as bag:
        for _, message, _ in bag.read_messages(topics=["/alphasense/imu"]):
            stamps.append(message.header.stamp.secs + message.header.stamp.nsecs * 1e-9)
            gyro.append((message.angular_velocity.x, message.angular_velocity.y, message.angular_velocity.z))
    stamps = np.asarray(stamps)
    gyro = np.asarray(gyro)
    if len(stamps) < 2 or np.any(np.diff(stamps) <= 0):
        raise ValueError("IMU timestamps must be strictly increasing")

    starts = np.searchsorted(stamps, times[:-1], side="left")
    ends = np.searchsorted(stamps, times[1:], side="left")
    counts = ends - starts
    prefix = np.vstack((np.zeros(3), np.cumsum(gyro, axis=0)))
    mean_gyro = (prefix[ends] - prefix[starts]) / np.maximum(counts[:, None], 1)
    valid = (intervals >= 0.05) & (intervals <= 0.15) & (counts >= 20)
    valid &= np.all(np.isfinite(rates), axis=1)
    valid &= np.linalg.norm(rates, axis=1) <= 6.0
    valid &= np.linalg.norm(mean_gyro, axis=1) >= 0.15
    if not np.any(valid):
        raise ValueError("no sufficiently sampled turning intervals")

    measured = rates[valid]
    imu = mean_gyro[valid]
    inverted = reference[:, 4:8].copy()
    inverted[:, :3] *= -1
    inverse_rates, _ = reference_body_rates(times, inverted)
    wxyz_rates, _ = reference_body_rates(times, reference[:, [5, 6, 7, 4]])
    candidates = {
        "xyzw_world_from_imu_same_axes": (measured, imu),
        "xyzw_world_from_base_x_180": (measured, imu * np.array([1.0, -1.0, -1.0])),
        "xyzw_inverse_pose_same_axes": (inverse_rates[valid], imu),
        "wxyz_world_from_imu_same_axes": (wxyz_rates[valid], imu),
    }
    results = {}
    for name, (reference_rate, imu_rate) in candidates.items():
        difference = reference_rate - imu_rate
        results[name] = {
            "vector_rmse_rad_s": float(np.sqrt(np.mean(np.sum(difference**2, axis=1)))),
            "axis_rmse_rad_s": np.sqrt(np.mean(difference**2, axis=0)).tolist(),
            "axis_correlation": [float(np.corrcoef(reference_rate[:, i], imu_rate[:, i])[0, 1]) for i in range(3)],
        }
    print(json.dumps({
        "reference_rows": len(reference), "imu_rows": len(stamps),
        "all_reference_intervals": len(intervals), "usable_turning_intervals": int(np.sum(valid)),
        "turning_axis_rms_rad_s": np.sqrt(np.mean(measured**2, axis=0)).tolist(),
        "fixed_candidate_comparison": results,
        "warning": "Frame diagnostic only: reference smoothing, IMU bias and reference LiDAR/IMU dependence prevent treating this as ground-truth accuracy.",
    }, indent=2))


if __name__ == "__main__":
    main()
