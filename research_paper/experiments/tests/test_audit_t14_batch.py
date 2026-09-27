import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import audit_t14_batch


class T14BatchAuditTests(unittest.TestCase):
    def test_output_hash_comparison_reports_changed_and_missing_files(self):
        result = audit_t14_batch.compare_output_hashes(
            {"poses.csv": "same", "health.csv": "before"},
            {"poses.csv": "same", "health.csv": "after", "dcreg.csv": "new"})
        self.assertEqual(result["common_artifacts"], 2)
        self.assertEqual(result["identical_artifacts"], 1)
        self.assertEqual(result["changed_artifacts"], ["health.csv"])
        self.assertEqual(result["missing_from_first"], ["dcreg.csv"])


if __name__ == "__main__":
    unittest.main()
