"""Independent small fixtures for Hesai point-time conversion."""

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from hesai_time_adapter import adapt_payload  # noqa: E402


FIELDS = [("x", 0, 7), ("y", 4, 7), ("z", 8, 7),
          ("intensity", 16, 7), ("timestamp", 24, 8), ("ring", 32, 4)]


def cloud(times):
    points = np.zeros(len(times), dtype=np.dtype({
        "names": ["x", "y", "z", "intensity", "timestamp", "ring"],
        "formats": ["<f4", "<f4", "<f4", "<f4", "<f8", "<u2"],
        "offsets": [0, 4, 8, 16, 24, 32], "itemsize": 48,
    }))
    points["x"] = [1.0, 2.0, 3.0][:len(times)]
    points["timestamp"] = times
    points["ring"] = [0, 1, 31][:len(times)]
    return points.tobytes()


class HesaiAdapterTests(unittest.TestCase):
    def test_preserves_time_and_fields(self):
        times = np.array([1649856227.623467, 1649856227.673467, 1649856227.723469])
        start, packed, roundoff = adapt_payload(cloud(times), 3, 48, FIELDS)
        output = np.ndarray((3,), dtype=np.dtype({
            "names": ["x", "ring", "time"],
            "formats": ["<f4", "<u2", "<f4"],
            "offsets": [0, 16, 18], "itemsize": 22,
        }), buffer=packed)
        np.testing.assert_equal(output["x"], [1.0, 2.0, 3.0])
        np.testing.assert_equal(output["ring"], [0, 1, 31])
        self.assertLess(roundoff, 1e-7)
        np.testing.assert_allclose(start / 1e9 + output["time"].astype("f8"),
                                   times, atol=1e-6, rtol=0)

    def test_rejects_reversed_point_time(self):
        with self.assertRaisesRegex(ValueError, "not ordered"):
            adapt_payload(cloud([100.1, 100.0]), 2, 48, FIELDS)

    def test_rejects_wrong_schema(self):
        bad_fields = [f for f in FIELDS if f[0] != "timestamp"]
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            adapt_payload(cloud([100.0, 100.1]), 2, 48, bad_fields)

    def test_rejects_implausible_duration(self):
        with self.assertRaisesRegex(ValueError, "duration"):
            adapt_payload(cloud([100.0, 100.5]), 2, 48, FIELDS)


if __name__ == "__main__":
    unittest.main()
