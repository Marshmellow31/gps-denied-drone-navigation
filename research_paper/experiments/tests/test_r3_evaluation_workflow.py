"""No-data tests for the corrected R3 plan and Point-LIO freeze bindings."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import r3_evaluation_workflow as workflow


class R3EvaluationWorkflowTests(unittest.TestCase):
    def test_no_data_plan_binds_corrected_analysis_and_both_backend_freezes(self):
        plan = workflow.build_plan(
            workflow.FAST_ANALYSIS, workflow.ROOT / 'research_paper/data/SPLITS.csv')
        self.assertEqual(plan['status'], 'PENDING_R3_SCENE_SCREEN')
        self.assertEqual(plan['n_test_geometry_pairs'], 48)
        self.assertEqual(plan['geometry_pairs_per_stratum'], 12)
        self.assertFalse(plan['heldout_inputs_generated'])
        self.assertFalse(plan['heldout_geometry_screened'])
        self.assertEqual(plan['development_analysis_sha256'],
                         workflow.execution.sha256_file(workflow.FAST_ANALYSIS))
        self.assertEqual(plan['pointlio_development_analysis_sha256'],
                         workflow.execution.sha256_file(workflow.POINT_ANALYSIS))
        self.assertEqual(plan['pointlio_replication_freeze_sha256'],
                         workflow.execution.sha256_file(workflow.POINT_FREEZE))
        self.assertEqual(plan['pointlio_replication_freeze_review_sha256'],
                         workflow.execution.sha256_file(workflow.POINT_FREEZE_REVIEW))
        self.assertEqual(plan['r3_evaluation_workflow_sha256'],
                         workflow.execution.sha256_file(Path(workflow.__file__).resolve()))

    def test_exact_r3_inventory_includes_corrected_and_point_freeze_artifacts(self):
        captured = {}
        original = workflow.execution._require_r3_pass

        def audit(review, freeze):
            captured['t16'] = workflow.execution.T16_ANALYSIS_MANIFEST
            captured['plan'] = workflow.execution.FINAL_PLAN
            hashes = workflow._required_hashes(review)
            captured['hashes'] = hashes
            return {'reviewed_artifact_hashes': hashes}

        try:
            with tempfile.TemporaryDirectory() as folder:
                review = Path(folder) / 'review.md'
                review.write_text('synthetic review inventory input')
                with patch.object(workflow.execution, '_require_r3_pass', side_effect=audit):
                    result = workflow.require_r3_pass(review, Path('synthetic-freeze'))
            self.assertEqual(result['reviewed_artifact_hashes'], captured['hashes'])
            self.assertEqual(captured['t16'], workflow.FAST_ANALYSIS)
            self.assertEqual(captured['plan'], workflow.FINAL_PLAN)
            for name in (
                'corrected FAST-LIO development manifest',
                'corrected Point-LIO development manifest',
                'Point-LIO replication freeze',
                'Point-LIO replication freeze review',
                'final dataset analysis caller',
                'held-out statistics',
                'R3 evaluation workflow',
                'Point-LIO launch helper',
                'Point-LIO development input validator',
                'Point-LIO feasibility output verifier',
                'Point-LIO simulation clock drain helper',
                'Point-LIO accepted native identity anchor',
                'Point-LIO simulation development config',
                'Point-LIO build compatibility patch',
                'Point-LIO deque header patch',
                'Point-LIO indicator sidecar patch',
                'Point-LIO development runner',
                'Point-LIO development analysis',
                'Point-LIO development attempt verifier',
                'Point-LIO indicator feasibility script',
                'Point-LIO smoke script',
                'Point-LIO development workflow tests',
                'Point-LIO indicator export tests',
                'Point-LIO information adapter tests',
                'Point-LIO native sidecar tests',
                'Point-LIO pose logger tests',
                'Point-LIO runner helpers tests',
                'Point-LIO feasibility pair tests',
                'Point-LIO attempt recorder tests',
                'Point-LIO one-seed acceptance',
                'Point-LIO indicator parity audit',
                'Point-LIO development workflow full suite log',
                'primary recovery audit script',
                'primary recovery runner',
                'primary recovery tests',
                'development signal comparison plotter',
                'POINTLIO_BINARY_SHA256',
                'POINTLIO_UPSTREAM_COMMIT',
            ):
                self.assertIn(name, captured['hashes'])
            self.assertFalse(captured['hashes']['Point-LIO replication freeze'] == '')
            self.assertEqual(captured['hashes']['POINTLIO_BINARY_SHA256'],
                             '80516da9cafba98262d56c17cc26ec4da76e214049d3af7776248b4c3a342b17')
            self.assertEqual(captured['hashes']['POINTLIO_UPSTREAM_COMMIT'],
                             '4b86a469eb5572e70ed575af25b5f15dd06e8e3c')
        finally:
            workflow.execution._require_r3_pass = original

    def test_require_r3_pass_validates_both_locked_thresholds(self):
        import json
        with tempfile.TemporaryDirectory() as folder:
            review_path = Path(folder) / 'review.md'
            freeze_path = Path(folder) / 'freeze.md'
            review_path.write_text("# R3 Review\n\n**Gate:** PASS\n")
            inventory = workflow._required_hashes(review_path)

            # Freeze with matching thresholds
            freeze_bundle = {
                "schema": "r3-implementation-freeze-v1",
                "artifacts": inventory,
                "FASTLIO_MIN_EIG_G3_threshold": workflow.execution.LOCKED_DEVELOPMENT_THRESHOLD,
                "POINTLIO_MIN_EIG_G3_threshold": 123.80876977779258,
            }
            freeze_path.write_text("# Freeze\n\n**Gate:** PASS\n\n```json\n" +
                                   json.dumps(freeze_bundle) + "\n```\n")

            res = workflow.require_r3_pass(review_path, freeze_path)
            self.assertIn("r3_review_sha256", res)
            self.assertIn("implementation_freeze_sha256", res)
            self.assertEqual(res["POINTLIO_MIN_EIG_G3_threshold"], 123.80876977779258)

            # Freeze with invalid Point-LIO threshold
            bad_bundle = dict(freeze_bundle, POINTLIO_MIN_EIG_G3_threshold=99.99)
            freeze_path.write_text("# Freeze\n\n**Gate:** PASS\n\n```json\n" +
                                   json.dumps(bad_bundle) + "\n```\n")
            with self.assertRaises(workflow.execution.FinalEvaluationError):
                workflow.require_r3_pass(review_path, freeze_path)


if __name__ == '__main__':
    unittest.main()
