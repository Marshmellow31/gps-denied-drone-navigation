"""Final caller contracts on mocked metadata only; no final geometry or data."""
from contextlib import ExitStack
from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import hashlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import final_dataset_analysis as final


class FinalDatasetAnalysisTests(unittest.TestCase):
    def fixture(self, root):
        results = root / 'mock_results'
        results.mkdir()
        plan = {'n_test_geometry_pairs': 48, 'geometry_pairs_per_stratum': 12,
                'development_analysis_sha256': 'frozen-development',
                'pointlio_development_analysis_sha256': 'frozen-point-development',
                'pointlio_replication_freeze_sha256': 'point-freeze',
                'pointlio_replication_freeze_review_sha256': 'point-freeze-review',
                'r3_evaluation_workflow_sha256': 'workflow'}
        plan_path = root / 'mock_plan.json'
        plan_path.write_text(json.dumps(plan))
        gate = {'r3_review_sha256': 'review', 'implementation_freeze_sha256': 'freeze',
                'reviewed_artifact_hashes': {
                    'final dataset analysis caller': final.execution.sha256_file(Path(final.__file__)),
                    'T16 analyzer': final.execution.sha256_file(Path(final.common.__file__)),
                    'held-out statistics': final.execution.sha256_file(Path(final.uncertainty.__file__)),
                    'R3 evaluation workflow': final.execution.sha256_file(Path(final.workflow.__file__)),
                }}
        selected = {name: list(range(final.execution.heldout.STRATA[name]['seed_min'],
                                     final.execution.heldout.STRATA[name]['seed_min']+12))
                    for name in final.uncertainty.STRATA}
        screen = {'status': 'SCENE_SCREEN_PASS', 'role': 'heldout', **gate,
            'plan_sha256': final.execution.sha256_file(plan_path),
            'development_analysis_sha256': plan['development_analysis_sha256'],
            'selected_seeds_by_stratum': selected,
            'screened_layouts': [{'stratum': name, 'seed': seed, 'eligible': True}
                for name, seeds in selected.items() for seed in seeds]}
        screen_path = root / 'mock_screen.json'
        screen_path.write_text(json.dumps(screen))
        pairs = []
        for name, seeds in selected.items():
            for seed in seeds:
                runs = []
                for scene in ('CORRIDOR', 'CONTROL'):
                    run_id = f'SYNTHETIC_METADATA_{seed}_{scene}'
                    path = results / 'runs' / run_id / 'run_manifest.json'
                    path.parent.mkdir(parents=True)
                    path.write_text(json.dumps({'scene': scene}))
                    runs.append({'run_id': run_id, 'status': 'COMPLETED'})
                pairs.append({'stratum': name, 'seed': seed, 'status': 'COMPLETED', 'scene_runs': runs})
        batch = {'role': 'heldout', **gate, 'status': 'COMPLETED',
            'target_geometry_pairs': 48, 'completed_geometry_pairs': 48,
            'scheduled_scene_runs': 96, 'scene_runs': 96,
            'scene_screen_sha256': final.execution.sha256_file(screen_path),
            'development_analysis_sha256': plan['development_analysis_sha256'],
            'backend': {'binary_sha256': final.execution.EXPECTED_BINARY_SHA256},
            'runner_sha256': final.execution.sha256_file(Path(final.execution.__file__)),
            'heldout_generator_sha256': final.execution.sha256_file(Path(final.execution.heldout.__file__)),
            'heldout_inputs_or_results_used_for_tuning': False,
            'threshold_locked_from_development': final.execution.LOCKED_DEVELOPMENT_THRESHOLD,
            'pair_results': pairs}
        (results / 'final_batch_summary.json').write_text(json.dumps(batch))
        return results, plan_path, screen_path, plan, screen, batch, gate

    def context(self, stack, fixture, truth_missing_seed=None):
        results, plan_path, screen_path, plan, screen, batch, gate = fixture
        stack.enter_context(patch.object(final.execution, '_require_r3_pass', return_value=gate))
        stack.enter_context(patch.object(final.execution, '_check_analysis_runtime', return_value={'python': 'frozen'}))
        stack.enter_context(patch.object(final.workflow, 'build_plan', return_value=plan))

        def loaded(root, result, seed, stratum, scene, *args):
            label = None if scene == 'CONTROL' else final.common.RecoveryLabel(
                'RECOVERED', seed != truth_missing_seed, '', .2, 20.2, .5, 1., None, 20.2, (1, 2, 3), 19)
            decisions = [final.common.DecisionTick(
                tick, final.common.EPOCH_NS + tick * final.common.TICK_NS,
                True, 0.0, False,
                final.common.EPOCH_NS + tick * final.common.TICK_NS, 0, '')
                for tick in range(600)]
            return SimpleNamespace(run_id=f'SYNTHETIC_{seed}_{scene}',
                control=scene == 'CONTROL', label=label, seed=seed,
                run_manifest={'stratum': stratum}, scene=scene, windows=[],
                exit_time_s=.2, evaluation_rows=[{
                    'window_s': '3.0', 'timestamp_ns': str(final.common.EPOCH_NS + 1_000_000_000),
                    'window_end_ns': str(final.common.EPOCH_NS + 4_000_000_000),
                    'local_valid': 'true', 'local_translation_error_rate_mps': '0.1',
                    'local_rotation_error_rate_radps': '0.01', 'unavailable_reason': ''}],
                decisions={'FASTLIO_MIN_EIG_G3': decisions, 'DCREG_SCHUR_MASK': decisions})

        stack.enter_context(patch.object(final, 'load_scene', side_effect=loaded))
        stack.enter_context(patch.object(final, 'interior_pair', return_value=1.))
        stack.enter_context(patch.object(final, 'curve_events', return_value={}))
        paired = stack.enter_context(patch.object(final.uncertainty, 'paired_interval', return_value={'status': 'AVAILABLE'}))
        curve = stack.enter_context(patch.object(final.uncertainty, 'event_weighted_curve_interval', return_value={'status': 'AVAILABLE'}))
        return paired, curve

    def call(self, root, fixture):
        return final.analyze(fixture[0], fixture[2], fixture[1], root/'review', root/'freeze', root/'report.json')

    def test_unconditional_false_healthy_denominator_excludes_empty_initial_interval(self):
        unavailable = [final.common.DecisionTick(i, i, False, None, None, None, None, 'UNAVAILABLE')
                       for i in range(600)]
        no_recovery = final.common.RecoveryLabel(
            'NO_RECOVERY', True, '', 0.0, 20.0, None, None, None, 20.0, (), 0)
        immediate = final.common.RecoveryLabel(
            'RECOVERED', True, '', 0.0, 20.0, 0.0, 0.0, None, 20.0, (), 0)
        runs = [SimpleNamespace(control=False, label=no_recovery,
                                decisions={'FASTLIO_MIN_EIG_G3': unavailable}, seed=1, exit_time_s=0.0),
                SimpleNamespace(control=False, label=immediate,
                                decisions={'FASTLIO_MIN_EIG_G3': unavailable}, seed=2, exit_time_s=0.0)]
        summary = {'truth_label_eligible_corridor_events': 2,
                   'truth_recovered_events': 1,
                   'false_healthy_events': 0,
                   'false_healthy_conditional_denominator': 0,
                   'detected_recovery_events': 0,
                   'relapse_events': 0}
        result = final._event_proportion_intervals(
            runs, 'FASTLIO_MIN_EIG_G3', 100.0, 'FASTLIO_MIN_EIG_G3', summary)
        self.assertEqual(result['initial_false_healthy_unconditional']['trials'], 1)

    def test_stratum_unconditional_false_healthy_rate_uses_interval_event_denominator(self):
        unavailable = [final.common.DecisionTick(i, i, False, None, None, None, None, 'UNAVAILABLE')
                       for i in range(600)]
        eligible = final.common.RecoveryLabel(
            'NO_RECOVERY', True, '', 0.0, 20.0, None, None, None, 20.0, (), 0)
        recovered = final.common.RecoveryLabel(
            'RECOVERED', True, '', 0.0, 20.0, 0.0, 0.0, None, 20.0, (), 0)
        runs = [SimpleNamespace(control=False, label=eligible, decisions={'M': unavailable},
                                run_manifest={'stratum': final.uncertainty.STRATA[0]}, seed=1,
                                exit_time_s=0.0),
                SimpleNamespace(control=False, label=recovered, decisions={'M': unavailable},
                                run_manifest={'stratum': final.uncertainty.STRATA[0]}, seed=2,
                                exit_time_s=0.0)]
        summary = {'truth_label_eligible_corridor_events': 2, 'truth_recovered_events': 1,
                   'false_healthy_events': 1, 'false_healthy_conditional_denominator': 1,
                   'detected_recovery_events': 0, 'relapse_events': 0}
        with patch.object(final.common, 'summarize_method', return_value=(summary, [])), \
             patch.object(final, '_event_proportion_intervals', return_value={
                 'initial_false_healthy_unconditional': {
                     'successes': 1, 'trials': 1, 'fraction': 1.0, 'wilson_95': (0.2, 1.0)}}):
            result = final._stratum_method_metrics(runs, 'M', 1.0, 'M')
        output = result[final.uncertainty.STRATA[0]]
        self.assertEqual(output['false_healthy_event_rate_unconditional'], 1.0)
        self.assertEqual(output['false_healthy_event_unconditional_denominator'], 1)

    def test_continuous_initial_interval_counts_without_a_sampled_decision_tick(self):
        unavailable = [final.common.DecisionTick(i, i, False, None, None, None, None, 'UNAVAILABLE')
                       for i in range(600)]
        early_recovery = final.common.RecoveryLabel(
            'RECOVERED', True, '', 0.01, 20.01, 0.05, 0.05, None, 20.01, (), 0)
        run = SimpleNamespace(control=False, label=early_recovery,
                              decisions={'FASTLIO_MIN_EIG_G3': unavailable},
                              seed=1, exit_time_s=0.01)
        summary = {'truth_label_eligible_corridor_events': 1,
                   'truth_recovered_events': 1, 'false_healthy_events': 0,
                   'false_healthy_conditional_denominator': 0,
                   'detected_recovery_events': 0, 'relapse_events': 0}
        result = final._event_proportion_intervals(
            [run], 'FASTLIO_MIN_EIG_G3', 100.0, 'FASTLIO_MIN_EIG_G3', summary)
        self.assertEqual(result['initial_false_healthy_unconditional']['trials'], 1)
        self.assertEqual(result['initial_false_healthy_unconditional']['fraction'], 0.0)
        self.assertEqual(result['initial_false_healthy_conditional']['trials'], 0)

    def test_gate_failure_precedes_every_result_screen_or_input_read(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(final.execution, '_require_r3_pass', side_effect=final.execution.FinalEvaluationError('sealed')):
                with self.assertRaisesRegex(final.execution.FinalEvaluationError, 'sealed'):
                    final.analyze(root/'absent_results', root/'absent_screen', root/'absent_plan',
                                  root/'review', root/'freeze', root/'report.json')
            self.assertFalse((root/'report.json').exists())

    def test_full_mocked_48_pair_coverage_is_required_for_confirmatory_dispatch(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            fixture = self.fixture(root)
            paired, curve = self.context(stack, fixture)
            result = self.call(root, fixture)
            self.assertEqual(result['status'], 'CONFIRMATORY_COMPLETE')
            self.assertEqual(result['usable_interior_pairs'], 48)
            self.assertEqual(result['native_scene_runs_loaded'], 96)
            self.assertEqual(len(paired.call_args.args[1]), 48)
            self.assertEqual(curve.call_count, 2)
            self.assertFalse(result['threshold_selected_on_test'])
            self.assertIn('recovery_detection_given_truth_recovered',
                          result['method_metrics']['FASTLIO_MIN_EIG_G3']['event_proportion_intervals'])
            rates = result['three_second_error_rates_by_stratum']['corridor']['equal_stratum_estimates']
            self.assertEqual(rates['median_translation_rate_mps']['status'], 'AVAILABLE_COMPLETE')
            self.assertAlmostEqual(rates['median_translation_rate_mps']['equal_stratum_mean'], .1)

    def test_missing_pair_is_visible_and_cannot_receive_a_confirmatory_interval(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            fixture = self.fixture(root)
            fixture[5]['pair_results'][0].update(status='FAILED_KEEP_INPUTS', scene_runs=[])
            fixture[5]['status'] = 'INCOMPLETE_KEEP_FAILURES'
            fixture[5]['completed_geometry_pairs'] = 47
            fixture[5]['scene_runs'] = 94
            (fixture[0]/'final_batch_summary.json').write_text(json.dumps(fixture[5]))
            paired, curve = self.context(stack, fixture)
            result = self.call(root, fixture)
            self.assertEqual(result['status'], 'DESCRIPTIVE_ONLY_INCOMPLETE_PLANNED_COHORT')
            self.assertEqual(len(result['planned_pair_results']), 48)
            self.assertEqual(len(result['failed_or_unusable_pairs']), 1)
            self.assertEqual(result['native_scene_runs_loaded'], 94)
            paired.assert_not_called()
            curve.assert_not_called()
            self.assertTrue(all('Descriptive' in m['interpretation'] for m in result['method_metrics'].values()))

    def test_truth_unavailable_pair_cannot_claim_complete_confirmatory_coverage(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            fixture = self.fixture(root)
            seed = fixture[5]['pair_results'][0]['seed']
            paired, curve = self.context(stack, fixture, truth_missing_seed=seed)
            result = self.call(root, fixture)
            self.assertEqual(result['status'], 'DESCRIPTIVE_ONLY_INCOMPLETE_PLANNED_COHORT')
            self.assertEqual(result['usable_interior_pairs'], 47)
            self.assertIn('truth-label', result['failed_or_unusable_pairs'][0]['reason'])
            paired.assert_not_called()
            curve.assert_not_called()

    def test_self_declared_small_complete_roster_cannot_replace_frozen_48_pair_plan(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            fixture = self.fixture(root)
            fixture[5]['target_geometry_pairs'] = 4
            (fixture[0]/'final_batch_summary.json').write_text(json.dumps(fixture[5]))
            self.context(stack, fixture)
            with self.assertRaisesRegex(ValueError, 'plan/screen/batch/source'):
                self.call(root, fixture)

    def test_inconsistent_batch_status_and_run_counts_cannot_be_confirmatory(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            fixture = self.fixture(root)
            fixture[5]['completed_geometry_pairs'] = 47
            (fixture[0]/'final_batch_summary.json').write_text(json.dumps(fixture[5]))
            self.context(stack, fixture)
            with self.assertRaisesRegex(ValueError, 'status and run counts do not reconcile'):
                self.call(root, fixture)

    def test_nonfinite_interior_difference_cannot_receive_a_confirmatory_interval(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            fixture = self.fixture(root)
            paired, curve = self.context(stack, fixture)
            stack.enter_context(patch.object(final, 'interior_pair', return_value=float('nan')))
            result = self.call(root, fixture)
            self.assertEqual(result['status'], 'DESCRIPTIVE_ONLY_INCOMPLETE_PLANNED_COHORT')
            self.assertIn('non-finite', result['failed_or_unusable_pairs'][0]['reason'])
            paired.assert_not_called()
            curve.assert_not_called()

    def test_unreviewed_final_caller_cannot_read_a_dataset_after_a_mock_gate_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            gate = {'reviewed_artifact_hashes': {}}
            with patch.object(final.execution, '_require_r3_pass', return_value=gate), \
                 patch.object(final.execution, '_check_analysis_runtime', return_value={}):
                with self.assertRaisesRegex(ValueError, 'not bound in the R3 inventory'):
                    final.analyze(root/'absent_results', root/'absent_screen', root/'absent_plan',
                                  root/'review', root/'freeze', root/'report.json')

    def test_unmocked_scene_loader_uses_hash_checked_reference_filename_alias(self):
        with tempfile.TemporaryDirectory() as folder, ExitStack() as stack:
            root = Path(folder)
            results = root / 'results'
            run_id = 'FINAL_TEST_SHORT_NARROW_100_CORRIDOR_P1'
            run_dir = results / 'runs' / run_id
            stream = run_dir / 'stream'
            stream.mkdir(parents=True)
            input_dir = results / 'inputs' / 'TEST_SHORT_NARROW_100' / 'CORRIDOR'
            input_dir.mkdir(parents=True)
            shared_reference = results / 'shared_reference.txt'
            shared_reference.write_bytes(b'synthetic reference bytes\n')
            reference_sha = hashlib.sha256(shared_reference.read_bytes()).hexdigest()
            bag = input_dir / 'sensors.bag'
            bag.write_bytes(b'synthetic bag identity')
            bag_sha = hashlib.sha256(bag.read_bytes()).hexdigest()
            metadata = {
                'verified': True, 'evaluation_scope': 'heldout', 'clock_id': 'simulation_epoch',
                'source': {'artifact_name': 'reference.txt', 'sha256': reference_sha},
                'comparison_body': {'T_est_body_to_ref_body': final.common.np.eye(4).tolist()},
            }
            metadata_path = input_dir / 'reference_metadata.json'
            metadata_path.write_text(json.dumps(metadata))
            manifest = {
                'role': 'heldout', 'seed': 100, 'stratum': 'TEST_SHORT_NARROW',
                'scene': 'CORRIDOR', 'control': False, 'truth_in_sensor_bag': False,
                'sensors.bag': {'sha256': bag_sha},
                'route_profile': {'exit_time_s': 10.0},
                'scene_geometry': {'corridor_length_m': 8.0},
            }
            manifest_path = input_dir / 'manifest.json'
            manifest_path.write_text(json.dumps(manifest))
            outputs = {}
            for name in ('poses.csv', 'health.csv', 'health.csv.hessian.csv',
                         'dcreg.csv', 'evaluation.csv', 'rosbag.log'):
                path = stream / name
                path.write_text('synthetic output\n')
                outputs[f'stream/{name}'] = final.execution.sha256_file(path)
            identity = {
                'r3_review_sha256': 'review', 'implementation_freeze_sha256': 'freeze',
                'reviewed_artifact_hashes': {}, 'runtime': {'python': 'frozen'},
                'backend': {'binary_sha256': final.execution.EXPECTED_BINARY_SHA256},
                'plan_sha256': 'plan', 'screen_sha256': 'screen', 'analysis_sha256': 'analysis',
            }
            completion = {'completion_status': 'FULL_SENSOR_INPUT_AND_FLUSHED_POSE_LOG'}
            native = {
                'status': 'COMPLETED', 'role': 'heldout', 'seed': 100,
                'stratum': 'TEST_SHORT_NARROW', 'scene': 'CORRIDOR', 'run_id': run_id,
                'scheduled_run_id': 'FINAL_TEST_SHORT_NARROW_100_CORRIDOR_P1',
                'fingerprint': {
                    'execution_identity': identity,
                    'configuration_sha256': final.execution.sha256_file(final.execution.CONFIG),
                    'backend_binary_sha256': final.execution.EXPECTED_BINARY_SHA256,
                    'threshold_from_development_manifest': final.execution.LOCKED_DEVELOPMENT_THRESHOLD,
                    'input_manifest_sha256': final.execution._input_manifest_identity(manifest),
                    'input_manifest_file_sha256': final.execution.sha256_file(manifest_path),
                    'sensor_bag_sha256': bag_sha,
                    'reference_sha256': reference_sha,
                    'reference_metadata_sha256': final.execution.sha256_file(metadata_path),
                },
                'input_manifest': manifest, 'outputs': outputs,
                'postprocess_summaries': [], 'completion_validation': completion,
            }
            (run_dir / 'run_manifest.json').write_text(json.dumps(native))
            scene_result = {'run_id': run_id, 'scheduled_run_id': native['scheduled_run_id'],
                            'status': 'COMPLETED'}
            stack.enter_context(patch.object(final.execution, 'validate_completed_streams', return_value=completion))
            reference_object = object()
            stack.enter_context(patch.object(final.common.trajectory, 'load_reference', return_value=reference_object))
            stack.enter_context(patch.object(final.common.trajectory, 'load_estimates', return_value=[]))
            stack.enter_context(patch.object(final.common, 'build_primary_windows', return_value=([], True, '')))
            stack.enter_context(patch.object(final.common, '_read_diagnostics', return_value={
                'FASTLIO_MIN_EIG_G3': [], 'DCREG_SCHUR_MASK': []}))
            stack.enter_context(patch.object(final.common, 'associate_decision_ticks', return_value=[]))
            stack.enter_context(patch.object(final.common, '_read_csv', return_value=[]))

            loaded = final.load_scene(results, scene_result, 100, 'TEST_SHORT_NARROW',
                                     'CORRIDOR', identity, identity)
            alias = results / 'analysis_reference' / 'reference.txt'
            self.assertTrue(alias.is_file())
            self.assertEqual(alias.name, 'reference.txt')
            self.assertEqual(final.execution.sha256_file(alias), reference_sha)
            final.common.np.testing.assert_array_equal(loaded.body_transform, final.common.np.eye(4))


if __name__ == '__main__':
    unittest.main()
