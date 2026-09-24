"""Read-only LiDAR range summary for scene annotation; no poses or truth."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np


def range_metrics(xyz: np.ndarray) -> tuple[int, float, float, float]:
    xyz = np.asarray(xyz, dtype=np.float64)
    ranges = np.linalg.norm(xyz, axis=1)
    usable = ranges[np.isfinite(ranges) & (ranges > 0.2)]
    if not len(usable):
        return 0, math.nan, math.nan, math.nan
    return (len(usable), float(np.mean(usable < 3.0)),
            float(np.percentile(usable, 50)), float(np.percentile(usable, 90)))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bag", type=Path)
    parser.add_argument("--start-s", type=float, default=29.5)
    parser.add_argument("--end-s", type=float, default=40.5)
    parser.add_argument("--step-s", type=float, default=0.45)
    args = parser.parse_args()
    import rosbag  # Installed in the isolated Acer-side ROS environment.

    origin_ns = None
    last_selected_s = -math.inf
    print("relative_s,usable_points,fraction_under_3m,range_p50_m,range_p90_m")
    with rosbag.Bag(str(args.bag)) as bag:
        for _, message, _ in bag.read_messages(topics=["/hesai/pandar"]):
            stamp_ns = message.header.stamp.to_nsec()
            if origin_ns is None:
                origin_ns = stamp_ns
            relative_s = (stamp_ns - origin_ns) / 1e9
            if relative_s < args.start_s:
                continue
            if relative_s > args.end_s:
                break
            if relative_s - last_selected_s < args.step_s:
                continue
            points = np.ndarray(
                (message.width * message.height,),
                dtype=np.dtype({"names": ["x", "y", "z"], "formats": ["<f4"] * 3,
                                "offsets": [0, 4, 8], "itemsize": message.point_step}),
                buffer=message.data,
            )
            xyz = np.column_stack((points["x"], points["y"], points["z"]))
            count, near, p50, p90 = range_metrics(xyz)
            print(f"{relative_s:.3f},{count},{near:.6f},{p50:.6f},{p90:.6f}")
            last_selected_s = relative_s


if __name__ == "__main__":
    main()
