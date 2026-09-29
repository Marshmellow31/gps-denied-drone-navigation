"""Capture Point-LIO poses and retain the raw LiDAR frame ID in Header.seq."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import rospy
from nav_msgs.msg import Odometry


COLUMNS = (
    "timestamp_ns", "clock_id", "parent_frame_id", "body_frame_id",
    "x_m", "y_m", "z_m", "qx", "qy", "qz", "qw", "valid",
    "unavailable_reason", "segment_id", "event", "source_frame_id",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--topic", default="/aft_mapped_to_init")
    parser.add_argument("--clock-id", default="simulation_epoch")
    args = parser.parse_args(rospy.myargv()[1:])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    rospy.init_node("pointlio_pose_logger", anonymous=False)

    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        state = {"last_ns": None, "frames": None, "segment": 0,
                 "valid": 0, "invalid": 0, "resets": 0,
                 "write_error": None}

        def callback(message: Odometry) -> None:
            if state["write_error"] is not None:
                return
            try:
                timestamp_ns = message.header.stamp.to_nsec()
                frames = (message.header.frame_id, message.child_frame_id)
                if (state["last_ns"] is not None
                        and (timestamp_ns < state["last_ns"] or frames != state["frames"])):
                    state["segment"] += 1
                    state["resets"] += 1
                    writer.writerow((
                        timestamp_ns, args.clock_id, *frames, *("" for _ in range(7)),
                        "false", "POSE_RESET_BOUNDARY", state["segment"], "RESET",
                        message.header.seq,
                    ))
                position = message.pose.pose.position
                orientation = message.pose.pose.orientation
                values = (position.x, position.y, position.z, orientation.x,
                          orientation.y, orientation.z, orientation.w)
                valid = all(math.isfinite(value) for value in values)
                norm = math.sqrt(sum(value * value for value in values[3:])) if valid else math.nan
                valid = valid and abs(norm - 1.0) <= 1e-5
                writer.writerow((
                    timestamp_ns, args.clock_id, *frames,
                    *(format(value, ".17g") if valid else "" for value in values),
                    str(valid).lower(), "" if valid else "POSE_INVALID",
                    state["segment"], "POSE", message.header.seq,
                ))
                state["last_ns"] = timestamp_ns
                state["frames"] = frames
                state["valid" if valid else "invalid"] += 1
                if (state["valid"] + state["invalid"]) % 10 == 0:
                    handle.flush()
            except Exception as exc:
                state["write_error"] = f"{type(exc).__name__}: {exc}"
                rospy.logerr("Point-LIO pose logger callback failed: %s", state["write_error"])
                rospy.signal_shutdown("Point-LIO pose output failed")

        rospy.Subscriber(args.topic, Odometry, callback, queue_size=1000)
        rospy.on_shutdown(lambda: rospy.loginfo("Point-LIO pose logger counts: %s", state))
        rospy.spin()
        handle.flush()
        if state["write_error"] is not None:
            raise RuntimeError(state["write_error"])


if __name__ == "__main__":
    main()
