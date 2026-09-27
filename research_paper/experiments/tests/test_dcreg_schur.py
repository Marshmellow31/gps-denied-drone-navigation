import csv
import math
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import dcreg_schur


PERM = dcreg_schur.ROTATION_FIRST_PERMUTATION


def hessian_fastlio_order(h_dcreg):
    """Convert [rotation, translation] into FAST-LIO [translation, rotation]."""
    return np.asarray(h_dcreg)[np.ix_(PERM, PERM)]


class DcregSchurTests(unittest.TestCase):
    def test_official_dcreg_minimal_example_spectrum_and_conditions(self):
        # Reconstruct BuildSyntheticWeakAxisSystem() from DCReg commit
        # 8ce8451b15491a4bbe17cf85ab02a8bed6696861. The upstream README
        # reports these Schur spectra and condition numbers to six decimals.
        basis = np.eye(6)
        basis[0, 2] = 0.35
        basis[1, 5] = 0.15
        basis[2, 5] = 0.45
        basis[3, 2] = 0.20
        basis[4, 5] = 0.25
        stiffness = np.array([6.0, 4.5, 1.1, 5.0, 3.5, 0.18])
        jacobian = basis @ np.diag(stiffness)
        hessian_dcreg_order = jacobian.T @ jacobian

        result = dcreg_schur.compute_dcreg(
            hessian_fastlio_order(hessian_dcreg_order), accepted_count=20)

        self.assertTrue(result.valid)
        np.testing.assert_allclose(
            result.rotation_eigenvalues,
            [1.001796, 19.881966, 36.152505], atol=5.1e-7, rtol=0.0)
        np.testing.assert_allclose(
            result.translation_eigenvalues,
            [0.032394, 12.252030, 24.038714], atol=5.1e-7, rtol=0.0)
        self.assertAlmostEqual(result.rotation_kappas[0], 36.087707, places=5)
        self.assertAlmostEqual(result.translation_kappas[0], 742.066396, places=4)

    def test_isotropic_hessian_is_healthy(self):
        result = dcreg_schur.compute_dcreg(hessian_fastlio_order(3.0 * np.eye(6)), 20)
        self.assertTrue(result.valid)
        self.assertEqual(result.state, "HEALTHY")
        self.assertEqual(result.rotation_kappas, (1.0, 1.0, 1.0))
        self.assertEqual(result.translation_kappas, (1.0, 1.0, 1.0))
        self.assertEqual(result.health_score, 1.0)

    def test_weak_rotation_direction_is_flagged(self):
        h_d = np.diag([0.01, 1.0, 1.0, 1.0, 1.0, 1.0])
        result = dcreg_schur.compute_dcreg(hessian_fastlio_order(h_d), 20)
        self.assertEqual(result.state, "DEGENERATE")
        self.assertEqual(result.rotation_flags, (True, False, False))
        self.assertEqual(result.translation_flags, (False, False, False))
        self.assertAlmostEqual(result.rotation_kappas[0], 100.0)

    def test_weak_translation_direction_is_flagged(self):
        h_d = np.diag([1.0, 1.0, 1.0, 0.01, 1.0, 1.0])
        result = dcreg_schur.compute_dcreg(hessian_fastlio_order(h_d), 20)
        self.assertEqual(result.rotation_flags, (False, False, False))
        self.assertEqual(result.translation_flags, (True, False, False))
        self.assertAlmostEqual(result.translation_kappas[0], 100.0)

    def test_schur_conditioning_exposes_rotation_translation_coupling(self):
        identity = np.eye(3)
        coupling = np.diag([0.99, 0.0, 0.0])
        h_d = np.block([[identity, coupling], [coupling, identity]])
        result = dcreg_schur.compute_dcreg(hessian_fastlio_order(h_d), 20)
        self.assertEqual(result.state, "DEGENERATE")
        self.assertGreater(result.rotation_kappas[0], 10.0)
        self.assertGreater(result.translation_kappas[0], 10.0)

    def test_exact_threshold_is_not_flagged_but_above_is(self):
        at_threshold = np.diag([0.1, 1.0, 1.0, 1.0, 1.0, 1.0])
        result_equal = dcreg_schur.compute_dcreg(hessian_fastlio_order(at_threshold), 20)
        self.assertAlmostEqual(result_equal.rotation_kappas[0], 10.0)
        self.assertFalse(result_equal.rotation_flags[0])

        above_threshold = np.diag([0.099, 1.0, 1.0, 1.0, 1.0, 1.0])
        result_above = dcreg_schur.compute_dcreg(hessian_fastlio_order(above_threshold), 20)
        self.assertTrue(result_above.rotation_flags[0])

    def test_rank_deficiency_is_unbounded_not_unavailable(self):
        h_d = np.diag([0.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        result = dcreg_schur.compute_dcreg(hessian_fastlio_order(h_d), 20)
        self.assertTrue(result.valid)
        self.assertEqual(result.state, "DEGENERATE")
        self.assertTrue(math.isinf(result.rotation_kappas[0]))
        self.assertEqual(result.health_score, 0.0)

    def test_zero_subspace_is_fully_degenerate(self):
        h_d = np.diag([0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
        result = dcreg_schur.compute_dcreg(hessian_fastlio_order(h_d), 20)
        self.assertTrue(result.valid)
        self.assertTrue(all(math.isinf(value) for value in result.rotation_kappas))
        self.assertEqual(result.health_score, 0.0)

    def test_moore_penrose_handles_singular_complementary_block(self):
        h_d = np.diag([1.0, 2.0, 3.0, 0.0, 1.0, 2.0])
        result = dcreg_schur.compute_dcreg(hessian_fastlio_order(h_d), 20)
        self.assertTrue(result.valid)
        self.assertTrue(math.isinf(result.translation_kappas[0]))
        self.assertAlmostEqual(result.rotation_kappas[0], 3.0)

    def test_small_negative_roundoff_is_clamped_and_large_negative_rejected(self):
        small = np.diag([-1e-12, 1.0, 2.0, 1.0, 1.0, 1.0])
        result_small = dcreg_schur.compute_dcreg(hessian_fastlio_order(small), 20)
        self.assertTrue(result_small.valid)
        self.assertTrue(math.isinf(result_small.rotation_kappas[0]))

        large = np.diag([-1e-4, 1.0, 2.0, 1.0, 1.0, 1.0])
        result_large = dcreg_schur.compute_dcreg(hessian_fastlio_order(large), 20)
        self.assertFalse(result_large.valid)
        self.assertEqual(result_large.unavailable_reason, "INDICATOR_NUMERIC_FAILURE")
        self.assertIn("MATERIALLY_NEGATIVE", result_large.detail)

    def test_nonfinite_hessian_and_fewer_than_six_rows_are_unavailable(self):
        nonfinite = np.eye(6)
        nonfinite[0, 0] = np.nan
        result_nonfinite = dcreg_schur.compute_dcreg(nonfinite, 12)
        self.assertFalse(result_nonfinite.valid)
        self.assertEqual(result_nonfinite.detail, "NONFINITE_HESSIAN")

        result_few = dcreg_schur.compute_dcreg(np.eye(6), 5)
        self.assertFalse(result_few.valid)
        self.assertEqual(result_few.unavailable_reason, "INSUFFICIENT_CORRESPONDENCES")

    def test_rotating_bases_within_blocks_preserves_subspace_spectra(self):
        rng = np.random.default_rng(31)
        q_r, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        q_t, _ = np.linalg.qr(rng.normal(size=(3, 3)))
        q = np.block([[q_r, np.zeros((3, 3))], [np.zeros((3, 3)), q_t]])
        h_d = np.array([[3.0, 0.2, 0.0, 0.5, 0.0, 0.0],
                        [0.2, 2.0, 0.1, 0.0, 0.2, 0.0],
                        [0.0, 0.1, 1.0, 0.0, 0.0, 0.1],
                        [0.5, 0.0, 0.0, 2.0, 0.2, 0.0],
                        [0.0, 0.2, 0.0, 0.2, 1.5, 0.1],
                        [0.0, 0.0, 0.1, 0.0, 0.1, 1.0]])
        base = dcreg_schur.compute_dcreg(hessian_fastlio_order(h_d), 20)
        rotated = dcreg_schur.compute_dcreg(hessian_fastlio_order(q.T @ h_d @ q), 20)
        self.assertEqual(base.valid, rotated.valid)
        np.testing.assert_allclose(base.rotation_kappas, rotated.rotation_kappas, rtol=1e-10)
        np.testing.assert_allclose(base.translation_kappas, rotated.translation_kappas, rtol=1e-10)

    def test_output_serializes_unbounded_ratios_without_inf_or_nan(self):
        h_d = np.diag([0.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        result = dcreg_schur.compute_dcreg(hessian_fastlio_order(h_d), 20)
        row = dcreg_schur._result_row(123, "test_fixture", result)
        self.assertEqual(row["kappa_R_0"], "")
        self.assertEqual(row["kappa_R_0_unbounded"], "true")
        self.assertEqual(row["DCREG_HEALTH_SCORE"], 0.0)
        text = ",".join(str(row[field]) for field in dcreg_schur.OUTPUT_FIELDS).lower()
        self.assertNotIn("inf", text)
        self.assertNotIn("nan", text)

    def test_g3_parity_reproduces_t08_eigenvalues_and_preserves_rows(self):
        h_d = np.diag([0.7, 1.1, 1.8, 2.2, 3.1, 4.0])
        h_f = hessian_fastlio_order(h_d)
        count = 20
        scale = np.diag([1.0, 1.0, 1.0, 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
        g3 = scale @ h_f @ scale / (count * 0.001)
        eigenvalues = np.linalg.eigvalsh(g3)
        fields = ["timestamp_ns", "accepted_count", "valid", "unavailable_reason",
                  "source_stage", *dcreg_schur.hessian_column_names()]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            hessian_path = root / "health.csv.hessian.csv"
            with hessian_path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.DictWriter(stream, fieldnames=fields)
                writer.writeheader()
                row = {"timestamp_ns": 1000123456, "accepted_count": count,
                       "valid": "true", "unavailable_reason": "",
                       "source_stage": "last_scan_to_map_linearization"}
                row.update({name: value for name, value in zip(
                    dcreg_schur.hessian_column_names(), h_f.reshape(-1))})
                writer.writerow(row)

            health_path = root / "health.csv"
            with health_path.open("w", newline="", encoding="utf-8") as stream:
                health_fields = ["timestamp_ns", "lever_scale_m", "accepted_count",
                                 *(f"eigenvalue_{i}" for i in range(6)),
                                 "valid", "unavailable_reason"]
                writer = csv.DictWriter(stream, fieldnames=health_fields)
                writer.writeheader()
                for lever in (1.0, 3.0, 5.0):
                    matrix_scale = np.diag([1, 1, 1, 1 / lever, 1 / lever, 1 / lever])
                    vals = np.linalg.eigvalsh(matrix_scale @ h_f @ matrix_scale / (count * 0.001))
                    writer.writerow({"timestamp_ns": 1000123456, "lever_scale_m": lever,
                                     "accepted_count": count, "valid": "true",
                                     "unavailable_reason": "", **{
                                         f"eigenvalue_{i}": float(max(0.0, vals[i]))
                                         for i in range(6)}})

            output_path = root / "dcreg.csv"
            summary = dcreg_schur.process_hessian_csv(hessian_path, output_path, health_path)
            self.assertEqual(summary["rows"], 1)
            self.assertEqual(summary["valid"], 1)
            self.assertEqual(summary["g3_parity"]["timestamps"], 1)
            with output_path.open(newline="", encoding="utf-8") as stream:
                output = next(csv.DictReader(stream))
            self.assertEqual(output["state"], "HEALTHY")
            self.assertEqual(output["timestamp_ns"], "1000123456")


if __name__ == "__main__":
    unittest.main()
