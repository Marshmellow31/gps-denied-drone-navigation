"""LiDAR-only surface-normal diversity check under HILTI_SCENE_STRUCTURE.md."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np


TARGETS_S = (26, 27, 28, 29, 30, 35, 36, 37, 38, 39)
MAX_POINTS = 8000
NEIGHBORS = 20


def normal_information(xyz: np.ndarray, max_range_m: float) -> dict:
    from scipy.spatial import cKDTree

    xyz = np.asarray(xyz, dtype=np.float64)
    ranges = np.linalg.norm(xyz, axis=1)
    good = np.isfinite(xyz).all(axis=1) & np.isfinite(ranges) & (ranges >= 0.3) & (ranges <= max_range_m)
    points = xyz[good]
    if len(points) > MAX_POINTS:
        points = points[np.linspace(0, len(points)-1, MAX_POINTS, dtype=int)]
    if len(points) < NEIGHBORS:
        return {"selected_points": len(points), "usable_normals": 0, "usable_fraction": 0.0,
                "range_p50_m": None, "range_p90_m": None, "eig_min": None, "eig_mid": None, "eig_max": None,
                "eig6_min_scale1": None, "eig6_min_scale3": None, "eig6_min_scale5": None}
    selected_ranges = np.linalg.norm(points, axis=1)
    distances, indices = cKDTree(points).query(points, k=NEIGHBORS, workers=1)
    neighbors = points[indices]
    centered = neighbors - neighbors.mean(axis=1, keepdims=True)
    covariances = np.einsum("nki,nkj->nij", centered, centered) / NEIGHBORS
    eigenvalues, eigenvectors = np.linalg.eigh(covariances)
    traces = eigenvalues.sum(axis=1)
    usable = ((distances[:, -1] <= 1.5) & (traces > 0) &
              (eigenvalues[:, 0] / np.maximum(traces, 1e-12) <= 0.02) &
              (eigenvalues[:, 1] / np.maximum(traces, 1e-12) >= 0.03))
    result = {"selected_points": len(points), "usable_normals": int(usable.sum()),
              "usable_fraction": float(usable.mean()),
              "range_p50_m": float(np.percentile(selected_ranges, 50)),
              "range_p90_m": float(np.percentile(selected_ranges, 90))}
    if not usable.any():
        result.update(eig_min=None, eig_mid=None, eig_max=None,
                      eig6_min_scale1=None, eig6_min_scale3=None, eig6_min_scale5=None)
        return result
    normals = eigenvectors[usable, :, 0]
    normal_matrix = normals.T @ normals / len(normals)
    information = np.linalg.eigvalsh(normal_matrix)
    result.update(eig_min=float(information[0]), eig_mid=float(information[1]),
                  eig_max=float(information[2]))
    lever = np.cross(points[usable], normals)
    for scale in (1, 3, 5):
        jacobian = np.column_stack((lever / scale, normals))
        matrix = jacobian.T @ jacobian / len(normals)
        result[f"eig6_min_scale{scale}"] = float(np.linalg.eigvalsh(matrix)[0])
    return result


def point_xyz(message) -> np.ndarray:
    points = np.ndarray(
        (message.width * message.height,),
        dtype=np.dtype({"names": ["x", "y", "z"], "formats": ["<f4"] * 3,
                        "offsets": [0, 4, 8], "itemsize": message.point_step}),
        buffer=message.data,
    )
    return np.column_stack((points["x"], points["y"], points["z"]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bag", type=Path)
    args = parser.parse_args()
    import rosbag  # Isolated Acer-side ROS environment, not needed by unit tests.

    selected: dict[int, tuple[float, np.ndarray]] = {}
    origin_ns = None
    with rosbag.Bag(str(args.bag)) as bag:
        for _, message, _ in bag.read_messages(topics=["/hesai/pandar"]):
            stamp_ns = message.header.stamp.to_nsec()
            if origin_ns is None:
                origin_ns = stamp_ns
            time_s = (stamp_ns - origin_ns) / 1e9
            if time_s > max(TARGETS_S) + 0.06:
                break
            for target in TARGETS_S:
                difference = abs(time_s - target)
                if difference <= 0.06 and (target not in selected or difference < abs(selected[target][0]-target)):
                    selected[target] = (time_s, point_xyz(message))
    print("target_s,actual_s,max_range_m,selected_points,usable_normals,usable_fraction,range_p50_m,range_p90_m,eig_min,eig_mid,eig_max,eig6_min_scale1,eig6_min_scale3,eig6_min_scale5")
    for target in TARGETS_S:
        for max_range_m in (10.0, 20.0):
            if target not in selected:
                print(f"{target},,,0,0,,,,,,,,,")
                continue
            actual_s, xyz = selected[target]
            result = normal_information(xyz, max_range_m)
            fields = [target, f"{actual_s:.6f}", max_range_m] + [result[key] for key in (
                "selected_points", "usable_normals", "usable_fraction", "range_p50_m",
                "range_p90_m", "eig_min", "eig_mid", "eig_max",
                "eig6_min_scale1", "eig6_min_scale3", "eig6_min_scale5")]
            print(",".join("" if value is None or (isinstance(value, float) and not math.isfinite(value))
                           else str(value) for value in fields))


if __name__ == "__main__":
    main()
