import json
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import final_evaluation_runner as final_run


class FinalEvaluationRunnerTests(unittest.TestCase):
    @staticmethod
    def freeze_text(inventory):
        return "# Freeze\n\n**Gate:** PASS\n\n```json\n" + json.dumps({
            "schema": "r3-implementation-freeze-v1", "artifacts": inventory,
            "FASTLIO_MIN_EIG_G3_threshold": final_run.LOCKED_DEVELOPMENT_THRESHOLD,
        }) + "\n```\n"

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
            freeze.write_text(self.freeze_text(inventory))
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
            freeze.write_text(self.freeze_text(inventory))
            with self.assertRaises(final_run.FinalEvaluationError):
                final_run._require_r3_pass(review, freeze)

    def test_inventory_labels_are_bound_to_hashes(self):
        with tempfile.TemporaryDirectory() as folder:
            review, freeze = Path(folder) / "review.md", Path(folder) / "freeze.md"
            review.write_text("**Gate:** PASS\n")
            inventory = final_run._r3_required_hashes(review)
            inventory["final runner"], inventory["T16 analyzer"] = inventory["T16 analyzer"], inventory["final runner"]
            freeze.write_text(self.freeze_text(inventory))
            with self.assertRaises(final_run.FinalEvaluationError):
                final_run._require_r3_pass(review, freeze)

    def make_screen_fixture(self, root):
        analysis = root / "analysis.json"
        analysis.write_text(final_run.T16_ANALYSIS_MANIFEST.read_text())
        plan = root / "plan.json"
        plan.write_text(json.dumps(final_run.build_plan(analysis, final_run.ROOT / "research_paper/data/SPLITS.csv")))
        gate = {"r3_review_sha256": "fixture-review", "implementation_freeze_sha256": "fixture-freeze",
                "reviewed_artifact_hashes": {"fixture": "fixed"}}
        selected = {name: list(range(bounds["seed_min"], bounds["seed_min"]+12))
                    for name, bounds in final_run.heldout.STRATA.items()}
        screen = {"status": "SCENE_SCREEN_PASS", "role": "heldout", **gate,
                  "plan_sha256": final_run.sha256_file(plan),
                  "development_analysis_sha256": final_run.sha256_file(analysis),
                  "screen_runner_sha256": final_run.sha256_file(Path(final_run.__file__)),
                  "heldout_generator_sha256": final_run.sha256_file(Path(final_run.heldout.__file__)),
                  "selected_seeds_by_stratum": selected,
                  "screened_layouts": [{"stratum": name, "seed": seed, "eligible": True}
                                       for name, seeds in selected.items() for seed in seeds]}
        return analysis, plan, gate, screen

    def test_stale_or_duplicated_screen_rejected_before_geometry_or_backend(self):
        for defect in ("duplicate", "review", "generator", "plan"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                analysis, plan, gate, screen = self.make_screen_fixture(root)
                if defect == "duplicate":
                    name = next(iter(screen["selected_seeds_by_stratum"]))
                    screen["selected_seeds_by_stratum"][name][1] = screen["selected_seeds_by_stratum"][name][0]
                elif defect == "review":
                    screen["r3_review_sha256"] = "stale"
                elif defect == "generator":
                    screen["heldout_generator_sha256"] = "stale"
                else:
                    changed = json.loads(plan.read_text())
                    changed["geometry_pairs_per_stratum"] = 11
                    plan.write_text(json.dumps(changed))
                    screen["plan_sha256"] = final_run.sha256_file(plan)
                screen_path, review, freeze = root / "screen.json", root / "review.md", root / "freeze.md"
                screen_path.write_text(json.dumps(screen))
                review.write_text("fixture review")
                freeze.write_text("FASTLIO_MIN_EIG_G3 " + str(final_run.LOCKED_DEVELOPMENT_THRESHOLD))
                with patch.object(final_run, "T16_ANALYSIS_MANIFEST", analysis), \
                     patch.object(final_run, "FINAL_PLAN", plan), \
                     patch.object(final_run, "_require_r3_pass", return_value=gate), \
                     patch.object(final_run, "_check_analysis_runtime", return_value={"fixture": "runtime"}), \
                     patch.object(final_run, "_check_backend") as backend, \
                     patch.object(final_run.heldout, "screen_layout") as geometry:
                    with self.assertRaises(final_run.FinalEvaluationError):
                        final_run.execute_final_batch(screen_path, plan, analysis, review, freeze,
                            root / "ros", root / "workspace", root / "binary", root / "scratch", root / "results")
                    backend.assert_not_called()
                    geometry.assert_not_called()
                self.assertFalse((root / "scratch").exists())

    def test_incomplete_batch_cli_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            arguments = ["runner", "run"]
            for name in ("screen", "plan", "analysis", "r3-review", "implementation-freeze",
                         "ros-env", "workspace", "fastlio-binary", "scratch-root", "results-root"):
                arguments.extend(["--" + name, str(root / name)])
            with patch.object(sys, "argv", arguments), \
                 patch.object(sys, "stdout", io.StringIO()), \
                 patch.object(final_run, "execute_final_batch", return_value={
                     "status": "INCOMPLETE_KEEP_FAILURES", "target_geometry_pairs": 48,
                     "completed_geometry_pairs": 47}):
                with self.assertRaises(SystemExit) as error:
                    final_run.main()
                self.assertEqual(error.exception.code, 2)

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
