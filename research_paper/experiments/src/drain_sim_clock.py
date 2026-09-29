"""Advance the ROS simulation clock briefly after a finite ROS bag replay."""

from __future__ import annotations

import argparse
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bag", type=Path, required=True)
    args = parser.parse_args()

    import rosbag
    import rospy
    from rosgraph_msgs.msg import Clock

    with rosbag.Bag(str(args.bag)) as bag:
        end_time = bag.get_end_time()
    rospy.init_node("point_lio_clock_drain", anonymous=True)
    publisher = rospy.Publisher("/clock", Clock, queue_size=1)
    time.sleep(0.25)
    for extra in (0.25, 0.5, 0.75, 1.0):
        publisher.publish(Clock(clock=rospy.Time.from_sec(end_time + extra)))
        time.sleep(0.25)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
