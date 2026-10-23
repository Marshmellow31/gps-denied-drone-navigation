import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from audit_health_export import audit


class ExportAuditTests(unittest.TestCase):
    def check_rows(self, rows):
        header = "timestamp_ns,lever_scale_m,accepted_count," + ",".join(
            f"eigenvalue_{i}" for i in range(6)) + ",valid,unavailable_reason,source_stage\n"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "health.csv"
            path.write_text(header + rows)
            return audit(path)

    def test_complete_valid_group(self):
        result = self.check_rows("".join(
            f"100,{scale},6,0,1,2,3,4,5,true,,stage\n" for scale in (1, 3, 5)))
        self.assertEqual(result["row_counts"], {"VALID": 3})

    def test_missing_scale_rejected(self):
        with self.assertRaises(AssertionError):
            self.check_rows("100,1,6,0,1,2,3,4,5,true,,stage\n")

    def test_unavailable_must_not_contain_zero(self):
        with self.assertRaises(AssertionError):
            self.check_rows("100,1,0,0,,,,,,false,INIT,stage\n")
