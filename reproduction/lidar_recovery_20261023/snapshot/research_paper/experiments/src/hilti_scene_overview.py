"""Make LiDAR-only top-down snapshots for independent scene annotation."""

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores, get_typestore


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bag", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--step-s", type=float, default=5.0)
    parser.add_argument("--start-s", type=float, default=0.0)
    parser.add_argument("--limit-s", type=float, default=90.0)
    parser.add_argument("--radius-m", type=float, default=15.0)
    args = parser.parse_args()
    typestore = get_typestore(Stores.ROS1_NOETIC)
    panels = []
    panel_counts = []
    with Reader(args.bag) as reader:
        connection = next(c for c in reader.connections if c.topic == "/hesai/pandar")
        start = reader.start_time
        next_time = start + round(args.start_s * 1e9)
        for _, _, raw in reader.messages(connections=[connection]):
            msg = typestore.deserialize_ros1(raw, connection.msgtype)
            stamp = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
            relative = (stamp - start) / 1e9
            if relative > args.limit_s:
                break
            if stamp < next_time:
                continue
            points = np.ndarray(
                shape=(msg.width * msg.height,),
                dtype=np.dtype({"names": ["x", "y", "z"], "formats": ["<f4"] * 3,
                                "offsets": [0, 4, 8], "itemsize": msg.point_step}),
                buffer=msg.data,
            )
            x, y, z = points["x"], points["y"], points["z"]
            good = (np.isfinite(x) & np.isfinite(y) & np.isfinite(z)
                    & (np.abs(x) < args.radius_m) & (np.abs(y) < args.radius_m)
                    & (z > -3) & (z < 3))
            distance = np.sqrt(x.astype("f8") ** 2 + y.astype("f8") ** 2 + z.astype("f8") ** 2)
            panel_counts.append((round(relative, 1), int(good.sum()), len(points),
                                 [round(float(v), 2) for v in np.percentile(distance, [50, 90, 99])]))
            hist, _, _ = np.histogram2d(
                y[good], x[good], bins=240,
                range=[[-args.radius_m, args.radius_m], [-args.radius_m, args.radius_m]],
            )
            pixels = np.minimum(255, np.log1p(hist) * 80).astype(np.uint8)
            panel = Image.fromarray(np.flipud(pixels), "L").convert("RGB")
            draw = ImageDraw.Draw(panel)
            draw.text((5, 5), f"+{relative:.1f}s", fill=(255, 210, 80))
            panels.append(panel)
            next_time = stamp + round(args.step_s * 1e9)
    cols = 4
    rows = (len(panels) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 240, rows * 240), (0, 0, 0))
    for index, panel in enumerate(panels):
        sheet.paste(panel, ((index % cols) * 240, (index // cols) * 240))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output)
    print(f"{len(panels)} LiDAR-only panels: {args.output}")
    print("time_s,visible_points,total_points,range_p50_p90_p99_m:", panel_counts)


if __name__ == "__main__":
    main()
