"""Convert Hilti Hesai clouds to FAST-LIO's Velodyne-shaped point input.

Only the sensor point payload is read. Reference poses are never an input.
The conversion preserves every point's acquisition time to float precision.
"""

import argparse
import copy

import numpy as np


INPUT_LAYOUT = {"x": (0, 7), "y": (4, 7), "z": (8, 7),
                "intensity": (16, 7), "timestamp": (24, 8), "ring": (32, 4)}
OUTPUT_LAYOUT = (("x", 0, 7), ("y", 4, 7), ("z", 8, 7),
                 ("intensity", 12, 7), ("ring", 16, 4), ("time", 18, 7))


def adapt_payload(data, count, point_step, fields, bigendian=False):
    """Return (scan_start_ns, packed_points, maximum_roundoff_s)."""
    if bigendian or point_step != 48 or count <= 0 or len(data) != count * point_step:
        raise ValueError("unexpected Hesai point dimensions/layout")
    found = {name: (offset, datatype) for name, offset, datatype in fields}
    if any(found.get(name) != expected for name, expected in INPUT_LAYOUT.items()):
        raise ValueError("missing or changed Hesai point field")
    source = np.ndarray((count,), dtype=np.dtype({
        "names": ["x", "y", "z", "intensity", "timestamp", "ring"],
        "formats": ["<f4", "<f4", "<f4", "<f4", "<f8", "<u2"],
        "offsets": [0, 4, 8, 16, 24, 32], "itemsize": 48,
    }), buffer=data)
    times = source["timestamp"]
    if not np.isfinite(times).all() or not np.isfinite(source["x"]).all() \
            or not np.isfinite(source["y"]).all() or not np.isfinite(source["z"]).all():
        raise ValueError("nonfinite time or coordinate")
    if (times[1:] < times[:-1]).any():
        raise ValueError("point acquisition times are not ordered")
    start_ns = round(float(times[0]) * 1e9)
    offsets = (times - start_ns / 1e9).astype("<f4")
    if offsets.min() < -1e-6 or offsets[-1] <= 0 or offsets[-1] > 0.2:
        raise ValueError("unexpected scan duration or time origin")
    output = np.empty((count,), dtype=np.dtype({
        "names": ["x", "y", "z", "intensity", "ring", "time"],
        "formats": ["<f4", "<f4", "<f4", "<f4", "<u2", "<f4"],
        "offsets": [0, 4, 8, 12, 16, 18], "itemsize": 22,
    }))
    for name in ("x", "y", "z", "intensity", "ring"):
        output[name] = source[name]
    output["time"] = offsets
    roundoff = float(np.max(np.abs(offsets.astype("<f8") - (times - times[0]))))
    return start_ns, output.tobytes(), roundoff


def main():
    import rospy
    from sensor_msgs.msg import PointCloud2, PointField

    parser = argparse.ArgumentParser()
    parser.add_argument("--input-topic", default="/hesai/pandar_raw")
    parser.add_argument("--output-topic", default="/velodyne_points")
    args = parser.parse_args(rospy.myargv()[1:])
    rospy.init_node("hilti_hesai_time_adapter", anonymous=False)
    publisher = rospy.Publisher(args.output_topic, PointCloud2, queue_size=10)
    counts = {"seen": 0, "published": 0, "rejected": 0}

    def callback(msg):
        counts["seen"] += 1
        try:
            if msg.height != 1 or msg.row_step != msg.width * msg.point_step:
                raise ValueError("unexpected organized cloud")
            fields = [(f.name, f.offset, f.datatype) for f in msg.fields]
            start_ns, packed, roundoff = adapt_payload(
                msg.data, msg.width, msg.point_step, fields, msg.is_bigendian)
            if abs(msg.header.stamp.to_nsec() - start_ns) > 1_000_000:
                raise ValueError("scan header differs from first point by >1 ms")
        except ValueError as exc:
            counts["rejected"] += 1
            rospy.logerr("Hilti cloud %d rejected: %s", counts["seen"], exc)
            return
        out = PointCloud2()
        out.header = copy.copy(msg.header)
        out.header.stamp.secs, out.header.stamp.nsecs = divmod(start_ns, 1_000_000_000)
        out.height, out.width = 1, msg.width
        out.fields = [PointField(name=name, offset=offset, datatype=datatype, count=1)
                      for name, offset, datatype in OUTPUT_LAYOUT]
        out.is_bigendian = False
        out.point_step, out.row_step = 22, 22 * msg.width
        out.is_dense, out.data = msg.is_dense, packed
        publisher.publish(out)
        counts["published"] += 1
        if counts["published"] == 1 or counts["published"] % 100 == 0:
            rospy.loginfo("Hilti clouds published=%d max_roundoff_s=%.9g",
                          counts["published"], roundoff)

    rospy.Subscriber(args.input_topic, PointCloud2, callback,
                     queue_size=10, buff_size=8 * 1024 * 1024)
    rospy.on_shutdown(lambda: rospy.loginfo("Hilti adapter counts: %s", counts))
    rospy.spin()


if __name__ == "__main__":
    main()
