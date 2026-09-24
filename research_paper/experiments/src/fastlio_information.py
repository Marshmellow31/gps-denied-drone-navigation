"""Measurement-only point-to-plane information used to verify T08 instrumentation.

This mirrors the first six columns of pinned FAST-LIO's ``h_share_model``. It
does not read a reference trajectory and is not an EKF posterior covariance.
"""

from __future__ import annotations

import numpy as np


def measurement_information(
    points_lidar_m: np.ndarray,
    normals_world: np.ndarray,
    rotation_world_imu: np.ndarray,
    rotation_imu_lidar: np.ndarray,
    translation_imu_lidar_m: np.ndarray,
    *,
    lever_scale_m: float = 1.0,
    residual_variance_m2: float = 0.001,
) -> dict[str, object]:
    """Return the normalized 6x6 accepted-correspondence information matrix.

    Column order is world translation (3), IMU-tangent rotation (3), matching
    FAST-LIO ``h_x``. Rotation columns divide by ``lever_scale_m`` so all six
    columns describe perturbations in metres. Only already accepted backend
    correspondences should enter this function; it does not select points.
    """
    points = np.asarray(points_lidar_m, dtype=np.float64)
    normals = np.asarray(normals_world, dtype=np.float64)
    world_imu = np.asarray(rotation_world_imu, dtype=np.float64)
    imu_lidar = np.asarray(rotation_imu_lidar, dtype=np.float64)
    offset = np.asarray(translation_imu_lidar_m, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3 or normals.shape != points.shape:
        raise ValueError("points and normals must be equal N x 3 arrays")
    if world_imu.shape != (3, 3) or imu_lidar.shape != (3, 3) or offset.shape != (3,):
        raise ValueError("rotations must be 3 x 3 and offset must be length 3")
    if not np.isfinite(lever_scale_m) or lever_scale_m <= 0:
        raise ValueError("lever_scale_m must be positive and finite")
    if not np.isfinite(residual_variance_m2) or residual_variance_m2 <= 0:
        raise ValueError("residual_variance_m2 must be positive and finite")
    if len(points) < 6 or not all(np.isfinite(a).all() for a in (points, normals, world_imu, imu_lidar, offset)):
        return {"valid": False, "reason": "INSUFFICIENT_OR_NONFINITE_CORRESPONDENCES", "accepted_count": len(points)}
    normal_norm = np.linalg.norm(normals, axis=1)
    if np.any(normal_norm < 0.99) or np.any(normal_norm > 1.01):
        return {"valid": False, "reason": "NONUNIT_NORMAL", "accepted_count": len(points)}
    points_imu = points @ imu_lidar.T + offset
    normals_imu = normals @ world_imu
    rotational = np.cross(points_imu, normals_imu) / lever_scale_m
    jacobian = np.column_stack((normals, rotational))
    information = (jacobian.T @ jacobian) / (len(points) * residual_variance_m2)
    eigenvalues = np.linalg.eigvalsh(information)
    if not np.isfinite(eigenvalues).all():
        return {"valid": False, "reason": "NONFINITE_INFORMATION", "accepted_count": len(points)}
    return {"valid": True, "reason": "", "accepted_count": len(points),
            "information": information, "eigenvalues": eigenvalues,
            "minimum_eigenvalue": float(max(0.0, eigenvalues[0]))}
