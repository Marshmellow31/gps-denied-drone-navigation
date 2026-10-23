import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import heldout_simulation as original
import heldout_simulation_v2 as revised
import final_evaluation_runner as runner
import r3_evaluation_workflow as workflow


class GeometryV2WorkflowTests(unittest.TestCase):
    def test_old_final_ids_rejected_before_random_sampling(self):
        for seed in (100, 120, 140, 160):
            with self.assertRaises(ValueError):
                revised.sample_layout(seed, 'TEST_SHORT_NARROW')

    def test_fresh_pools_are_disjoint_and_exact(self):
        ids = set()
        for name, bounds in revised.STRATA.items():
            pool = set(range(bounds['seed_min'], bounds['seed_max'] + 1))
            self.assertEqual(len(pool), 80)
            self.assertFalse(pool & ids)
            self.assertFalse(pool & set(range(100, 180)))
            self.assertEqual(revised.stratum_for_seed(bounds['seed_min']), name)
            ids |= pool

    def test_short_control_surfaces_are_structurally_unchanged(self):
        for length in (8., 8.5, 9.):
            for width in (1.3, 1.5, 2.5, 3.):
                self.assertEqual(revised.build_candidate(length, width, 6., True),
                                 original.build_straight_surfaces(length, width, 6., True))

    def test_development_fixture_cannot_sample_a_final_seed(self):
        with self.assertRaises(ValueError):
            revised.sample_development_fixture(10000, 'DEVELOPMENT_FIXED_LONG_NARROW', True)
        with self.assertRaises(ValueError):
            revised.sample_development_fixture(14, 'TEST_LONG_NARROW', True)

    def test_old_freeze_cannot_authorize_new_screen(self):
        with patch.object(revised, 'screen_layout', side_effect=AssertionError('final geometry touched')):
            with self.assertRaises(runner.FinalEvaluationError):
                with workflow.corrected_runner_context():
                    runner.screen_reserved_layouts(workflow.FINAL_PLAN,
                        runner.ROOT/'research_paper/reviews/R3_IMPLEMENTATION.md',
                        runner.ROOT/'research_paper/protocol/IMPLEMENTATION_FREEZE.md')

    def test_no_data_plan_binds_amendment_and_exposure(self):
        with patch.object(revised, 'sample_layout', side_effect=AssertionError('final geometry touched')):
            plan = workflow.build_plan(workflow.FAST_ANALYSIS, runner.SPLITS_PATH)
        self.assertEqual(plan['n_test_geometry_pairs'], 48)
        self.assertTrue(plan['geometry_design_adapted_to_failed_screen'])
        self.assertEqual(plan['original_geometry_ids_excluded'], [100, 179])
        self.assertEqual(plan['geometry_profile'], revised.GEOMETRY_PROFILE)
        self.assertFalse(plan['heldout_geometry_screened'])


if __name__ == '__main__':
    unittest.main()
