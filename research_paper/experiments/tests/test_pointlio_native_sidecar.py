import csv
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
NATIVE_RESET_HARNESS = Path(__file__).resolve().parent / "native" / "pointlio_sidecar_reset.cpp"
sys.path.insert(0, str(EXPERIMENT_ROOT / "src"))
from pointlio_indicator_export import export_sidecar  # noqa: E402


class PointLioNativeSidecarTests(unittest.TestCase):
    @unittest.skipUnless(
        os.environ.get("POINTLIO_SOURCE_ROOT"),
        "set POINTLIO_SOURCE_ROOT to a patched Point-LIO source tree for the native fixture",
    )
    def test_cpp_sidecar_reset_and_pose_join_use_one_shared_segment_boundary(self):
        source_root = Path(os.environ["POINTLIO_SOURCE_ROOT"]).resolve()
        sidecar_cpp = source_root / "src" / "IndicatorSidecar.cpp"
        sidecar_header = source_root / "src" / "IndicatorSidecar.h"
        self.assertTrue(sidecar_cpp.is_file())
        self.assertTrue(sidecar_header.is_file())
        compiler = shutil.which("g++")
        self.assertIsNotNone(compiler)

        eigen_include = os.environ.get("POINTLIO_EIGEN_INCLUDE")
        cache_path = source_root.parents[1] / "build" / "CMakeCache.txt"
        if eigen_include is None and cache_path.is_file():
            cache_text = cache_path.read_text(encoding="utf-8", errors="replace")
            match = re.search(r"^Eigen3_INCLUDE_DIR:PATH=(.+)$", cache_text, re.MULTILINE)
            if match:
                eigen_include = match.group(1)
        self.assertIsNotNone(eigen_include, "Eigen include path was not found")
        self.assertTrue((Path(eigen_include) / "Eigen" / "Dense").is_file())

        with tempfile.TemporaryDirectory(prefix="pointlio-sidecar-reset-") as temp:
            temp_root = Path(temp)
            executable = temp_root / "sidecar_reset_fixture"
            output = temp_root / "native_output"
            output.mkdir()
            subprocess.run([
                compiler, "-std=c++17", f"-I{source_root / 'src'}",
                f"-I{eigen_include}", str(NATIVE_RESET_HARNESS),
                str(sidecar_cpp), "-o", str(executable),
            ], check=True, capture_output=True, text=True)
            subprocess.run([str(executable), str(output)], check=True,
                           capture_output=True, text=True)

            result = export_sidecar(
                output / "frame_ledger.csv",
                output / "measurement_groups.csv",
                output / "jacobian_rows.csv",
                output / "indicators.csv",
                expected_header_stamps_ns=[1000, 3000, 5000],
                pose_path=output / "poses.csv",
                reset_events_path=output / "reset_events.csv",
                segmented_poses_path=output / "poses_segmented.csv",
            )
            self.assertTrue(result[0]["valid"])
            self.assertEqual(result[1]["unavailable_reason"], "RESET_IN_FRAME")
            self.assertTrue(result[2]["valid"])

            with (output / "poses_segmented.csv").open(
                    newline="", encoding="utf-8") as stream:
                poses = list(csv.DictReader(stream))
            self.assertEqual([row["segment_id"] for row in poses], ["0", "0", "1"])
            self.assertEqual(poses[1]["valid"], "false")
            self.assertEqual(poses[1]["unavailable_reason"], "RESET_IN_FRAME")

            # Replacing the captured pre-update basis with a plausible later
            # identity rotation must fail row reconstruction, not pass silently.
            wrong_groups = output / "postupdate_groups.csv"
            with (output / "measurement_groups.csv").open(
                    newline="", encoding="utf-8") as stream:
                group_reader = csv.DictReader(stream)
                group_fields = list(group_reader.fieldnames or ())
                groups = list(group_reader)
            for row in groups:
                if row["frame_id"] == "1":
                    for r in range(3):
                        for c in range(3):
                            row[f"R{r}{c}"] = str(float(r == c))
            with wrong_groups.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=group_fields)
                writer.writeheader()
                writer.writerows(groups)

            wrong_rows = output / "postupdate_rows.csv"
            with (output / "jacobian_rows.csv").open(
                    newline="", encoding="utf-8") as stream:
                row_reader = csv.DictReader(stream)
                row_fields = list(row_reader.fieldnames or ())
                rows = list(row_reader)
            for row in rows:
                if row["frame_id"] == "1":
                    for r in range(3):
                        for c in range(3):
                            row[f"R{r}{c}"] = str(float(r == c))
            with wrong_rows.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=row_fields)
                writer.writeheader()
                writer.writerows(rows)
            wrong_basis = export_sidecar(
                output / "frame_ledger.csv", wrong_groups, wrong_rows,
                output / "wrong_basis_indicators.csv",
            )
            self.assertEqual(wrong_basis[0]["run_state"], "RUN_INCOMPLETE")
            self.assertIn("source-row reconstruction mismatch",
                          wrong_basis[0]["unavailable_reason"])


if __name__ == "__main__":
    unittest.main()
