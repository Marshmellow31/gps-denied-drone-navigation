"""Capture FAST-LIO's /Odometry stream in the T05 pose CSV format."""

import argparse
import csv
import math
from pathlib import Path

import rospy
from nav_msgs.msg import Odometry


COLUMNS = (
    "timestamp_ns", "clock_id", "parent_frame_id", "body_frame_id",
    "x_m", "y_m", "z_m", "qx", "qy", "qz", "qw", "valid",
    "unavailable_reason", "segment_id", "event",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--topic", default="/Odometry")
    parser.add_argument("--clock-id", default="geode_ros_header_unix")
    args = parser.parse_args(rospy.myargv()[1:])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rospy.init_node("fastlio_pose_logger", anonymous=False)

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        state = {"last_ns": None, "frames": None, "segment": 0, "valid": 0, "invalid": 0, "resets": 0}

        def callback(msg: Odometry) -> None:
            ns = msg.header.stamp.to_nsec()
            frames = (msg.header.frame_id, msg.child_frame_id)
            if state["last_ns"] is not None and (ns < state["last_ns"] or frames != state["frames"]):
                state["segment"] += 1
                state["resets"] += 1
                writer.writerow((ns, args.clock_id, *frames, *("" for _ in range(7)),
                                 "false", "POSE_RESET_BOUNDARY", state["segment"], "RESET"))
            position = msg.pose.pose.position
            rotation = msg.pose.pose.orientation
            values = (position.x, position.y, position.z, rotation.x, rotation.y, rotation.z, rotation.w)
            valid = all(math.isfinite(value) for value in values)
            qnorm = math.sqrt(sum(value * value for value in values[3:])) if valid else math.nan
            valid = valid and abs(qnorm - 1.0) <= 1e-5
            writer.writerow((ns, args.clock_id, *frames,
                             *(format(value, ".17g") if valid else "" for value in values),
                             str(valid).lower(), "" if valid else "POSE_INVALID", state["segment"], "POSE"))
            state["last_ns"] = ns
            state["frames"] = frames
            state["valid" if valid else "invalid"] += 1
            if (state["valid"] + state["invalid"]) % 10 == 0:
                handle.flush()

        rospy.Subscriber(args.topic, Odometry, callback, queue_size=1000)
        rospy.on_shutdown(lambda: rospy.loginfo("FAST-LIO pose logger counts: %s", state))
        rospy.spin()
        handle.flush()


if __name__ == "__main__":
    main()
