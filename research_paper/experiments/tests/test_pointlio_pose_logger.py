import csv
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch


LOGGER_PATH = Path(__file__).resolve().parents[1] / "src" / "pointlio_pose_logger.py"


def fake_message(sequence, timestamp_ns):
    return types.SimpleNamespace(
        header=types.SimpleNamespace(
            seq=sequence,
            stamp=types.SimpleNamespace(to_nsec=lambda: timestamp_ns),
            frame_id="camera_init",
        ),
        child_frame_id="body",
        pose=types.SimpleNamespace(pose=types.SimpleNamespace(
            position=types.SimpleNamespace(x=1.0, y=2.0, z=3.0),
            orientation=types.SimpleNamespace(x=0.0, y=0.0, z=0.0, w=1.0),
        )),
    )


class PointLioPoseLoggerTests(unittest.TestCase):
    def load_logger(self, rospy_module):
        nav_msgs = types.ModuleType("nav_msgs")
        nav_msgs_msg = types.ModuleType("nav_msgs.msg")
        nav_msgs_msg.Odometry = type("Odometry", (), {})
        nav_msgs.msg = nav_msgs_msg
        spec = importlib.util.spec_from_file_location("pointlio_pose_logger_under_test",
                                                      LOGGER_PATH)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {
            "rospy": rospy_module,
            "nav_msgs": nav_msgs,
            "nav_msgs.msg": nav_msgs_msg,
        }):
            spec.loader.exec_module(module)
        return module

    def fake_rospy(self, messages):
        rospy = types.ModuleType("rospy")
        state = {"callback": None, "shutdown": None}
        rospy.myargv = lambda: sys.argv
        rospy.init_node = lambda *args, **kwargs: None
        rospy.Subscriber = lambda topic, msg_type, callback, queue_size: state.update(
            callback=callback)
        rospy.on_shutdown = lambda callback: state.update(shutdown=callback)
        rospy.spin = lambda: [state["callback"](message) for message in messages]
        rospy.loginfo = lambda *args, **kwargs: None
        rospy.logerr = lambda *args, **kwargs: None
        rospy.signal_shutdown = lambda reason: state.update(signal=reason)
        return rospy, state

    def test_logger_preserves_native_frame_sequence_and_flushes_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "poses.csv"
            rospy, _ = self.fake_rospy([fake_message(17, 1000), fake_message(18, 2000)])
            module = self.load_logger(rospy)
            with patch.object(sys, "argv", ["logger", "--output", str(output)]):
                module.main()
            with output.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual([row["source_frame_id"] for row in rows], ["17", "18"])
            self.assertEqual([row["timestamp_ns"] for row in rows], ["1000", "2000"])
            self.assertTrue(all(row["valid"] == "true" for row in rows))

    def test_callback_write_failure_requests_shutdown_and_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "poses.csv"
            rospy, state = self.fake_rospy([fake_message(17, 1000)])
            module = self.load_logger(rospy)

            class BrokenWriter:
                def __init__(self):
                    self.calls = 0

                def writerow(self, row):
                    self.calls += 1
                    if self.calls > 1:
                        raise OSError("disk write failed")

            with patch.object(module.csv, "writer", return_value=BrokenWriter()), \
                    patch.object(sys, "argv", ["logger", "--output", str(output)]):
                with self.assertRaisesRegex(RuntimeError, "disk write failed"):
                    module.main()
            self.assertEqual(state["signal"], "Point-LIO pose output failed")


if __name__ == "__main__":
    unittest.main()
