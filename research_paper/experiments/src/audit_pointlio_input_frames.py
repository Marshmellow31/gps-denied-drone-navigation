"""Export only raw PointCloud2 header times for a one-to-one frame audit."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bag", type=Path, required=True)
    parser.add_argument("--topic", default="/sim/points")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    import rosbag

    stamps: list[int] = []
    with rosbag.Bag(str(args.bag)) as bag:
        for _, message, _ in bag.read_messages(topics=[args.topic]):
            stamps.append(int(message.header.stamp.to_nsec()))
    if not stamps:
        raise SystemExit(f"no raw LiDAR messages on {args.topic}")
    if len(set(stamps)) != len(stamps):
        raise SystemExit("input bag contains duplicate LiDAR header timestamps")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(("header_stamp_ns",))
        writer.writerows((stamp,) for stamp in stamps)
    print(f"raw_frames={len(stamps)} first_ns={stamps[0]} last_ns={stamps[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
