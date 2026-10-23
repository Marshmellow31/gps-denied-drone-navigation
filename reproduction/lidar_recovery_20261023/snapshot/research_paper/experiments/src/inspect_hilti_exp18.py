"""Inspect Hilti Exp18 sensor timing without using cameras or estimator output.

Run with rosbags 0.11.5 on the downloaded ROS 1 bag. Output is JSON on stdout.
"""

import argparse
import json
import statistics
import struct
from pathlib import Path

from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores, get_typestore


def summarize(stamps):
    gaps = [(b - a) / 1e9 for a, b in zip(stamps, stamps[1:])]
    return {
        "count": len(stamps),
        "first_ns": stamps[0],
        "last_ns": stamps[-1],
        "median_gap_s": statistics.median(gaps),
        "max_gap_s": max(gaps),
        "nonmonotonic_gaps": sum(g <= 0 for g in gaps),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bag", type=Path)
    args = parser.parse_args()
    typestore = get_typestore(Stores.ROS1_NOETIC)
    streams = {"/hesai/pandar": [], "/alphasense/imu": []}
    samples = []
    with Reader(args.bag) as reader:
        connections = [c for c in reader.connections if c.topic in streams]
        bag_start = reader.start_time
        next_sample_ns = bag_start
        topics = {c.topic: {"type": c.msgtype, "count": c.msgcount} for c in reader.connections}
        for connection, bag_stamp, raw in reader.messages(connections=connections):
            msg = typestore.deserialize_ros1(raw, connection.msgtype)
            stamp = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
            streams[connection.topic].append(stamp)
            if connection.topic != "/hesai/pandar" or stamp < next_sample_ns:
                continue
            fields = [(f.name, f.offset, f.datatype, f.count) for f in msg.fields]
            first = struct.unpack_from("<d", msg.data, 24)[0]
            last = struct.unpack_from("<d", msg.data, (msg.width - 1) * msg.point_step + 24)[0]
            samples.append({
                "relative_s": round((stamp - bag_start) / 1e9, 3),
                "frame": msg.header.frame_id,
                "points": msg.width * msg.height,
                "point_step": msg.point_step,
                "fields": fields,
                "first_point_time_s": first,
                "last_point_time_s": last,
                "header_time_s": stamp / 1e9,
            })
            next_sample_ns = stamp + 10_000_000_000
    print(json.dumps({
        "bag": str(args.bag),
        "topics": topics,
        "streams": {name: summarize(stamps) for name, stamps in streams.items()},
        "samples": samples,
    }, indent=2))


if __name__ == "__main__":
    main()
