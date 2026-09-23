"""ROS 1 replay adapter for GEODE's end-stamped Velodyne clouds.

Each point retains its absolute acquisition time within float32 precision:
new_header + new_offset = old_header + old_offset. The adapter never reads
reference trajectories.
"""

import argparse
import copy

import numpy as np
import rospy
from sensor_msgs.msg import PointCloud2


def adapt_cloud(msg: PointCloud2) -> tuple[PointCloud2, float]:
    if msg.is_bigendian or msg.point_step != 22 or msg.row_step != msg.width * 22:
        raise ValueError("unexpected GEODE Velodyne point layout")
    fields = {field.name: (field.offset, field.datatype) for field in msg.fields}
    if fields.get("time") != (18, 7):  # sensor_msgs/PointField.FLOAT32
        raise ValueError("missing float32 time field at byte offset 18")
    data = bytearray(msg.data)
    count = msg.width * msg.height
    times = np.ndarray((count,), dtype="<f4", buffer=data, offset=18, strides=(22,))
    if count == 0 or not np.isfinite(times).all():
        raise ValueError("empty cloud or nonfinite point offset")
    shift = min(float(times.min()), 0.0)
    if shift:
        times[:] = times - np.float32(shift)
    out = PointCloud2()
    out.header = copy.copy(msg.header)
    out.header.stamp = rospy.Time.from_sec(0)
    shifted_ns = msg.header.stamp.to_nsec() + round(shift * 1_000_000_000)
    out.header.stamp.secs, out.header.stamp.nsecs = divmod(shifted_ns, 1_000_000_000)
    out.height = msg.height
    out.width = msg.width
    out.fields = msg.fields
    out.is_bigendian = msg.is_bigendian
    out.point_step = msg.point_step
    out.row_step = msg.row_step
    out.is_dense = msg.is_dense
    out.data = bytes(data)
    return out, shift


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-topic", default="/velodyne_points_raw")
    parser.add_argument("--output-topic", default="/velodyne_points")
    args = parser.parse_args(rospy.myargv()[1:])
    rospy.init_node("geode_velodyne_time_adapter", anonymous=False)
    publisher = rospy.Publisher(args.output_topic, PointCloud2, queue_size=20)
    stats = {"seen": 0, "published": 0, "failed": 0}

    def callback(msg: PointCloud2) -> None:
        stats["seen"] += 1
        try:
            out, shift = adapt_cloud(msg)
        except ValueError as exc:
            stats["failed"] += 1
            rospy.logerr("GEODE cloud %d rejected: %s", stats["seen"], exc)
            return
        publisher.publish(out)
        stats["published"] += 1
        if stats["published"] == 1 or stats["published"] % 100 == 0:
            rospy.loginfo("GEODE cloud published=%d shift_s=%.9f", stats["published"], shift)

    rospy.Subscriber(args.input_topic, PointCloud2, callback, queue_size=20, buff_size=4 * 1024 * 1024)
    rospy.on_shutdown(lambda: rospy.loginfo("GEODE adapter counts: %s", stats))
    rospy.spin()


if __name__ == "__main__":
    main()
