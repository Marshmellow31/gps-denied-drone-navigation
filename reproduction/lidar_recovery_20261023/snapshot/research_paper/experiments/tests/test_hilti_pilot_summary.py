import sys
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from summarize_hilti_pilot import ORIGIN_NS, group_name, summarize  # noqa: E402


class PilotSummaryTests(unittest.TestCase):
    def test_half_open_scene_bins_and_unavailable_not_zero(self):
        self.assertEqual(group_name(ORIGIN_NS + 26_000_000_000), "pre_scene")
        self.assertEqual(group_name(ORIGIN_NS + 31_600_000_000), "transition")
        self.assertEqual(group_name(ORIGIN_NS + 33_600_000_000), "other")
        rows = [
            {"window_s": "1.0", "timestamp_ns": str(ORIGIN_NS + 26_000_000_000),
             "local_valid": "true", "alignment_valid": "false", "unavailable_reason": "",
             "local_translation_error_m": "2", "local_rotation_error_rad": "0.2",
             "local_translation_error_rate_mps": "2", "local_rotation_error_rate_radps": "0.2"},
            {"window_s": "1.0", "timestamp_ns": str(ORIGIN_NS + 26_100_000_000),
             "local_valid": "false", "alignment_valid": "false", "unavailable_reason": "REFERENCE_GAP"},
        ]
        result = summarize(rows)["1.0"]["pre_scene"]
        self.assertEqual(result["planned"], 2)
        self.assertEqual(result["local_valid"], 1)
        self.assertEqual(result["invalid_reasons"], {"REFERENCE_GAP": 1})
        self.assertEqual(result["translation_error_m"]["median"], 2)


if __name__ == "__main__":
    unittest.main()
