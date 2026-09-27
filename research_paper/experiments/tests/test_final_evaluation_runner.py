import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import final_evaluation_runner as final_run


class FinalEvaluationRunnerTests(unittest.TestCase):
    def test_plan_uses_sample_size_without_screening_or_generating_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            analysis = root / "analysis.json"
            splits = root / "splits.csv"
            analysis.write_text(json.dumps({
                "status": "DONE", "role": "development_only",
                "heldout_inputs_opened": False,
                "sample_size": {"n_test_geometry_pairs": 48},
            }))
            splits.write_text(
                "split_id,seed_start,seed_end,role\n"
                "TEST_SHORT_NARROW,100,119,held_out\n"
                "TEST_SHORT_WIDE,120,139,held_out\n"
                "TEST_LONG_NARROW,140,159,held_out\n"
                "TEST_LONG_WIDE,160,179,held_out\n"
            )
            plan = final_run.build_plan(analysis, splits)
            self.assertEqual(plan["geometry_pairs_per_stratum"], 12)
            self.assertFalse(plan["heldout_inputs_generated"])
            self.assertFalse(plan["heldout_geometry_screened"])
            self.assertEqual(plan["strata"][0]["candidate_seeds_to_scene_screen_in_ascending_order"],
                             list(range(100, 120)))

    def test_r3_gate_rejects_missing_or_nonpass_documents(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            review, freeze = root / "review.md", root / "freeze.md"
            review.write_text("# R3\n\n**Gate:** REVISE\n")
            freeze.write_text("# Freeze\n\n**Gate:** PASS\n")
            with self.assertRaises(final_run.FinalEvaluationError):
                final_run._require_r3_pass(review, freeze)
            review.write_text("# R3\n\n**Gate:** PASS\n")
            inventory = final_run._r3_required_hashes(review)
            freeze.write_text("# Freeze\n\n**Gate:** PASS\n\nFASTLIO_MIN_EIG_G3 "
                              "166.16366016039856\n" + "\n".join(inventory.values()))
            hashes = final_run._require_r3_pass(review, freeze)
            self.assertEqual(hashes["r3_review_sha256"], final_run.sha256_file(review))
            self.assertEqual(hashes["implementation_freeze_sha256"], final_run.sha256_file(freeze))
            self.assertIn("reviewed_artifact_hashes", hashes)

    def test_r3_freeze_rejects_stale_runner_hash(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            review, freeze = root / "review.md", root / "freeze.md"
            review.write_text("# R3\n\n**Gate:** PASS\n")
            inventory = final_run._r3_required_hashes(review)
            inventory["final runner"] = "0" * 64
            freeze.write_text("# Freeze\n\n**Gate:** PASS\n\nFASTLIO_MIN_EIG_G3 "
                              "166.16366016039856\n" + "\n".join(inventory.values()))
            with self.assertRaises(final_run.FinalEvaluationError):
                final_run._require_r3_pass(review, freeze)

    def test_screen_mode_refuses_before_any_geometry_work_without_r3_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            review, freeze, plan = root / "review.md", root / "freeze.md", root / "plan.json"
            review.write_text("# R3\n\n**Gate:** REVISE\n")
            freeze.write_text("# Freeze\n\n**Gate:** PASS\n")
            plan.write_text("{}")
            with self.assertRaises(final_run.FinalEvaluationError):
                final_run.screen_reserved_layouts(plan, review, freeze)

    def test_final_batch_refuses_before_touching_data_without_r3_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            review, freeze = root / "review.md", root / "freeze.md"
            review.write_text("# R3\n\n**Gate:** REVISE\n")
            freeze.write_text("# Freeze\n\n**Gate:** PASS\n")
            with self.assertRaises(final_run.FinalEvaluationError):
                final_run.execute_final_batch(
                    root / "missing_screen.json", root / "missing_plan.json",
                    root / "missing_analysis.json",
                    review, freeze, root / "ros-env", root / "workspace",
                    root / "fastlio", root / "scratch", root / "results")
            self.assertFalse((root / "scratch").exists())
            self.assertFalse((root / "results").exists())


if __name__ == "__main__":
    unittest.main()
