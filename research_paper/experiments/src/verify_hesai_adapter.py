"""Read-only validation of the Hesai adapter against every Exp18 cloud."""

import argparse
from pathlib import Path

from rosbags.rosbag1 import Reader
from rosbags.typesys import Stores, get_typestore

from hesai_time_adapter import adapt_payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bag", type=Path)
    args = parser.parse_args()
    typestore = get_typestore(Stores.ROS1_NOETIC)
    count, max_roundoff, max_header_delta_ns = 0, 0.0, 0
    with Reader(args.bag) as reader:
        connection = next(c for c in reader.connections if c.topic == "/hesai/pandar")
        for _, _, raw in reader.messages(connections=[connection]):
            msg = typestore.deserialize_ros1(raw, connection.msgtype)
            fields = [(f.name, f.offset, f.datatype) for f in msg.fields]
            start_ns, packed, roundoff = adapt_payload(
                msg.data, msg.width * msg.height, msg.point_step, fields, msg.is_bigendian)
            header_ns = msg.header.stamp.sec * 1_000_000_000 + msg.header.stamp.nanosec
            if abs(start_ns - header_ns) > 1_000_000:
                raise ValueError(f"cloud {count}: header differs from first point by >1 ms")
            if len(packed) != 22 * msg.width * msg.height:
                raise ValueError(f"cloud {count}: output size mismatch")
            count += 1
            max_roundoff = max(max_roundoff, roundoff)
            max_header_delta_ns = max(max_header_delta_ns, abs(start_ns - header_ns))
    print(f"validated_clouds={count} max_roundoff_s={max_roundoff:.9g} "
          f"max_header_delta_ns={max_header_delta_ns}")


if __name__ == "__main__":
    main()
