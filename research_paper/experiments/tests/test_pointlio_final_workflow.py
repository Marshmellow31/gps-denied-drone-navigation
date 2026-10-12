"""No-data contracts for the gated Point-LIO final replication."""
from pathlib import Path
import json
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pointlio_final_analysis as analysis
import r3_evaluation_workflow as workflow
import run_pointlio_final_replication as runner
import validate_pointlio_final_input as input_validator
import verify_pointlio_final_attempt as verifier


class PointLioFinalWorkflowTests(unittest.TestCase):
    def test_input_archive_allows_only_non_scientific_manifest_revision_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, archive = root/'source', root/'archive'
            source.mkdir()
            archive.mkdir()
            for name in ('sensors.bag', 'reference.txt', 'reference_metadata.json'):
                (source/name).write_bytes(name.encode())
            manifest = {'seed': 100, 'scans': 600, 'code_revision': 'old', 'runtime_s': 2.0}
            (source/'manifest.json').write_text(json.dumps(manifest))
            for name in ('sensors.bag', 'reference.txt', 'reference_metadata.json', 'manifest.json'):
                (archive/name).write_bytes((source/name).read_bytes())
            manifest['code_revision'] = 'new'
            manifest['runtime_s'] = 5.0
            (source/'manifest.json').write_text(json.dumps(manifest))
            result = runner._archive_input(source, archive, runner.sha256(source/'sensors.bag'))
            self.assertEqual(result, archive)
            self.assertEqual(json.loads((archive/'manifest.json').read_text())['code_revision'], 'old')
            manifest['scans'] = 599
            (source/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, 'identity changed'):
                runner._archive_input(source, archive, runner.sha256(source/'sensors.bag'))

    def test_self_consistent_but_foreign_cached_evaluation_is_rejected(self):
        class Completed:
            def check_returncode(self):
                return None
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run_root = root/'runs'
            run_id = 'FINAL_TEST_SHORT_NARROW_100_CORRIDOR_POINTLIO_P1'
            run_dir = run_root/run_id
            run_dir.mkdir(parents=True)
            input_dir = root/'input'
            input_dir.mkdir()
            for name in ('reference.txt', 'reference_metadata.json'):
                (input_dir/name).write_text(name)
            runtime = {'python': '3.12.14', 'numpy': '2.5.3',
                       'python_executable': '/frozen/python', 'python_binary_sha256': 'a'*64,
                       'conda_history_sha256': 'b'*64}
            native = {'run_id': run_id, 'study_split': 'final_test_replication',
                      'execution_identity': {'study': 'frozen'}, 'status': 'COMPLETED',
                      'runtime': runtime, 'build_overlay': {'sha256': 'c'*64}}
            (run_dir/'run_manifest.json').write_text(json.dumps(native))
            (run_dir/'poses_segmented.csv').write_text('poses')
            evaluation_dir = root/'evaluation'/run_id
            evaluation_dir.mkdir(parents=True)
            csv_path = evaluation_dir/'evaluation.csv'
            csv_path.write_text('csv')
            (evaluation_dir/'evaluation_manifest.json').write_text(json.dumps({
                'role': 'foreign', 'identity': runner._evaluation_identity(native, run_dir, input_dir),
                'output_sha256': runner.sha256(csv_path)}))
            with patch.object(runner.subprocess, 'run', return_value=Completed()):
                with self.assertRaisesRegex(ValueError, 'preserving changed cached'):
                    runner._run_scene(run_id, 100, 'TEST_SHORT_NARROW', 'CORRIDOR',
                        input_dir, run_root, native['execution_identity'], root/'ros',
                        root/'workspace', root/'glog', root/'binary', root/'identity.json')

    def test_verified_slot_binds_native_bag_and_frozen_runtime(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            bag = root/'sensors.bag'
            bag.write_bytes(b'authorized bag')
            slot = {'control': False, 'input_manifest': {'seed': 100},
                    'reference_sha256': 'r', 'reference_metadata_sha256': 'm',
                    'sensor_bag_sha256': 'expected-bag-hash'}
            runtime = {'python': '3.12.14', 'numpy': '2.5.3',
                       'python_executable': '/frozen/python',
                       'python_binary_sha256': 'p', 'conda_history_sha256': 'c'}
            manifest = {'control': False, 'input_manifest': {'seed': 100},
                        'reference_sha256': 'r', 'reference_metadata_sha256': 'm',
                        'input_bag': {'path': str(bag), 'sha256': 'wrong'}, 'runtime': runtime}
            identity = {'runtime': dict(runtime)}
            with self.assertRaisesRegex(ValueError, 'authorized slot'):
                verifier._validate_recorded_slot(manifest, slot, root, identity)
            manifest['input_bag']['sha256'] = 'expected-bag-hash'
            verifier._validate_recorded_slot(manifest, slot, root, identity)
            manifest['runtime']['python_binary_sha256'] = 'stale'
            with self.assertRaisesRegex(ValueError, 'authorized slot'):
                verifier._validate_recorded_slot(manifest, slot, root, identity)

    def test_plan_binds_the_locked_point_threshold_and_final_interfaces(self):
        plan = workflow.build_plan(workflow.FAST_ANALYSIS,
                                   workflow.ROOT / 'research_paper/data/SPLITS.csv')
        point = workflow._validate_point_freeze()[1]
        self.assertEqual(plan['pointlio_locked_final_threshold'],
                         point['pointlio_threshold_selection']['threshold'])
        self.assertEqual(plan['pointlio_final_runner_sha256'],
                         workflow.execution.sha256_file(Path(runner.__file__)))
        self.assertEqual(plan['pointlio_final_analysis_sha256'],
                         workflow.execution.sha256_file(Path(analysis.__file__)))
        self.assertFalse(plan['heldout_inputs_generated'])
        self.assertFalse(plan['heldout_geometry_screened'])

    def test_runner_gate_precedes_any_primary_or_screen_read(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(workflow, 'require_r3_pass',
                              side_effect=RuntimeError('R3 gate closed')):
                with self.assertRaisesRegex(RuntimeError, 'R3 gate closed'):
                    runner.run(root/'screen', root/'plan', root/'primary', root/'review',
                               root/'freeze', root/'ros', root/'workspace', root/'glog',
                               root/'binary', root/'scratch', root/'point-output')

    def test_analysis_gate_precedes_any_batch_or_result_read(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            with patch.object(workflow, 'require_r3_pass',
                              side_effect=RuntimeError('R3 gate closed')):
                with self.assertRaisesRegex(RuntimeError, 'R3 gate closed'):
                    analysis.analyze(root/'point', root/'primary', root/'screen', root/'plan',
                                     root/'review', root/'freeze', root/'report')

    def test_input_validator_uses_frozen_control_flag_without_inventing_scene_field(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('sensors.bag', 'reference.txt'):
                (root/name).write_bytes(name.encode())
            (root/'reference_metadata.json').write_text(json.dumps({
                'evaluation_scope': 'heldout', 'estimator_input_independence': True}))
            manifest = {'role': 'heldout', 'seed': 100,
                        'stratum': 'TEST_SHORT_NARROW', 'control': False,
                        'truth_in_sensor_bag': False}
            identity = {'r3_review_path': 'review', 'implementation_freeze_path': 'freeze',
                        'r3_review_sha256': 'review-sha',
                        'implementation_freeze_sha256': 'freeze-sha',
                        'reviewed_artifact_hashes': {},
                        'pointlio_freeze_sha256': 'point-freeze-sha',
                        'pointlio_freeze_review_sha256': 'point-review-sha',
                        'pointlio_threshold': 123.8}
            identity_path = root/'execution_identity.json'
            identity_path.write_text(json.dumps(identity))
            point = {'pointlio_threshold_selection': {'threshold': 123.8}}
            with patch.object(input_validator.workflow, 'require_r3_pass',
                              return_value={k: identity[k] for k in (
                                  'r3_review_sha256', 'implementation_freeze_sha256',
                                  'reviewed_artifact_hashes')}), \
                 patch.object(input_validator.workflow, '_validate_point_freeze',
                              return_value=(None, point, 'point-freeze-sha', 'point-review-sha')), \
                 patch.object(input_validator.primary, '_verify_retained_input',
                              return_value=manifest):
                slot = input_validator.validate(root, 100, 'TEST_SHORT_NARROW',
                                                'CORRIDOR', identity_path)
            self.assertEqual(slot['scene'], 'CORRIDOR')
            self.assertFalse(slot['control'])

    def test_input_validator_closes_r3_gate_before_reading_any_input(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            identity_path = root/'execution_identity.json'
            identity_path.write_text(json.dumps({
                'r3_review_path': 'review', 'implementation_freeze_path': 'freeze'}))
            with patch.object(input_validator.workflow, 'require_r3_pass',
                              side_effect=ValueError('gate closed')), \
                 patch.object(input_validator.primary, '_verify_retained_input',
                              side_effect=AssertionError('input read before gate')):
                with self.assertRaisesRegex(ValueError, 'gate closed'):
                    input_validator.validate(root/'missing', 100, 'TEST_SHORT_NARROW',
                                             'CORRIDOR', identity_path)

    def test_failed_p1_is_retained_and_only_one_p2_retry_is_allowed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run_root = root/'runs'
            run_id = 'FINAL_TEST_SHORT_NARROW_100_CORRIDOR_POINTLIO_P1'
            p1 = run_root/run_id
            p1.mkdir(parents=True)
            identity = {'study': 'frozen'}
            (p1/'run_manifest.json').write_text(json.dumps({
                'run_id': run_id, 'study_split': 'final_test_replication',
                'execution_identity': identity, 'status': 'RUN_FAILED',
                'reason': 'synthetic retained failure'}))
            receipt_root = run_root/'receipts'
            receipt_root.mkdir()
            (receipt_root/f'{run_id}.json').write_text(json.dumps({
                'status': 'PROCESS_EXITED', 'process_pid': 99999999,
                'process_start_identity': 'stale-process-identity',
                'process_group_id': 99999999}))
            args = (run_id, 100, 'TEST_SHORT_NARROW', 'CORRIDOR', root/'input',
                    run_root, identity, root/'ros', root/'workspace', root/'glog',
                    root/'binary', root/'identity.json')
            first = runner._run_scene(*args, retry_failed=False)
            self.assertEqual(first['status'], 'FAILED_KEEP_OUTPUTS')
            self.assertEqual(first['run_id'], run_id)
            p2_id = run_id.rsplit('_P1', 1)[0] + '_P2'
            p2 = run_root/p2_id
            p2.mkdir()
            (p2/'run_manifest.json').write_text(json.dumps({
                'run_id': p2_id, 'study_split': 'final_test_replication',
                'execution_identity': identity, 'status': 'RUN_FAILED',
                'reason': 'retry failed'}))
            exhausted = runner._run_scene(*args, retry_failed=True,
                retry_diagnosis='Confirmed transient disk write failure; same frozen inputs retained.')
            self.assertEqual(exhausted['run_id'], p2_id)
            self.assertEqual(exhausted['previous_attempt']['run_id'], run_id)

    def test_completed_p2_is_reused_on_resumption_without_retry_failed_flag(self):
        class Completed:
            def check_returncode(self):
                return None
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run_root = root/'runs'
            run_id = 'FINAL_TEST_SHORT_NARROW_100_CORRIDOR_POINTLIO_P1'
            p1 = run_root/run_id
            p1.mkdir(parents=True)
            identity = {'study': 'frozen'}
            (p1/'run_manifest.json').write_text(json.dumps({
                'run_id': run_id, 'study_split': 'final_test_replication',
                'execution_identity': identity, 'status': 'RUN_FAILED',
                'reason': 'p1 failed'}))
            p2_id = run_id.rsplit('_P1', 1)[0] + '_P2'
            p2 = run_root/p2_id
            p2.mkdir()
            input_dir = root/'input'
            input_dir.mkdir()
            for name in ('reference.txt', 'reference_metadata.json'):
                (input_dir/name).write_text(name)
            runtime = {'python': '3.12.14', 'numpy': '2.5.3',
                       'python_executable': '/frozen/python', 'python_binary_sha256': 'a'*64,
                       'conda_history_sha256': 'b'*64}
            p2_manifest = {'run_id': p2_id, 'study_split': 'final_test_replication',
                           'execution_identity': identity, 'status': 'COMPLETED',
                           'runtime': runtime, 'build_overlay': {'sha256': 'c'*64}}
            (p2/'run_manifest.json').write_text(json.dumps(p2_manifest))
            (p2/'poses_segmented.csv').write_text('poses')
            eval_dir = root/'evaluation'/p2_id
            eval_dir.mkdir(parents=True)
            csv_path = eval_dir/'evaluation.csv'
            csv_path.write_text('csv')
            (eval_dir/'evaluation_manifest.json').write_text(json.dumps({
                'role': 'heldout_offline_evaluation',
                'identity': runner._evaluation_identity(p2_manifest, p2, input_dir),
                'output_sha256': runner.sha256(csv_path)}))
            args = (run_id, 100, 'TEST_SHORT_NARROW', 'CORRIDOR', input_dir,
                    run_root, identity, root/'ros', root/'workspace', root/'glog',
                    root/'binary', root/'identity.json')
            def fake_run(cmd, *a, **kw):
                if any('verify_pointlio_final_attempt.py' in str(arg) for arg in cmd):
                    out_path = Path(cmd[cmd.index('--output') + 1])
                    out_path.parent.mkdir(parents=True, exist_ok=True)
                    out_path.write_text('{"status": "PASS"}')
                return Completed()
            with patch.object(runner.subprocess, 'run', side_effect=fake_run):
                resumed = runner._run_scene(*args, retry_failed=False)
            self.assertEqual(resumed['status'], 'CACHED')
            self.assertEqual(resumed['run_id'], p2_id)
            self.assertEqual(resumed['previous_attempt']['run_id'], run_id)

    def test_p2_retry_requires_a_recorded_technical_diagnosis(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run_root = root/'runs'
            run_id = 'FINAL_TEST_SHORT_NARROW_100_CORRIDOR_POINTLIO_P1'
            run_dir = run_root/run_id
            run_dir.mkdir(parents=True)
            (run_dir/'run_manifest.json').write_text(json.dumps({
                'run_id': run_id, 'study_split': 'final_test_replication',
                'execution_identity': {'study': 'frozen'}, 'status': 'RUN_FAILED'}))
            args = (run_id, 100, 'TEST_SHORT_NARROW', 'CORRIDOR', root/'input',
                    run_root, {'study': 'frozen'}, root/'ros', root/'workspace',
                    root/'glog', root/'binary', root/'identity.json')
            with self.assertRaisesRegex(ValueError, 'diagnosed technical reason'):
                runner._run_scene(*args, retry_failed=True)

    def test_retry_refuses_a_live_or_unidentified_prior_process_group(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run_root = root/'runs'
            run_id = 'FINAL_TEST_SHORT_NARROW_100_CORRIDOR_POINTLIO_P1'
            p1 = run_root/run_id
            p1.mkdir(parents=True)
            identity = {'study': 'frozen'}
            (p1/'run_manifest.json').write_text(json.dumps({
                'run_id': run_id, 'study_split': 'final_test_replication',
                'execution_identity': identity, 'status': 'RUN_FAILED'}))
            receipts = run_root/'receipts'
            receipts.mkdir()
            (receipts/f'{run_id}.json').write_text(json.dumps({
                'status': 'RUNNING', 'process_pid': 123,
                'process_group_id': 123, 'process_start_identity': 'live'}))
            args = (run_id, 100, 'TEST_SHORT_NARROW', 'CORRIDOR', root/'input',
                    run_root, identity, root/'ros', root/'workspace', root/'glog',
                    root/'binary', root/'identity.json')
            with patch.object(runner.primary, '_process_identity', return_value='live'):
                with self.assertRaisesRegex(runner.primary.RunInProgressError, 'still live'):
                    runner._run_scene(*args, retry_failed=True,
                        retry_diagnosis='Confirmed transient process cleanup failure; same frozen inputs retained.')

    def test_existing_p2_startup_receipt_is_preserved_and_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            run_root = root/'runs'
            run_id = 'FINAL_TEST_SHORT_NARROW_100_CORRIDOR_POINTLIO_P1'
            p1 = run_root/run_id
            p1.mkdir(parents=True)
            identity = {'study': 'frozen'}
            (p1/'run_manifest.json').write_text(json.dumps({
                'run_id': run_id, 'study_split': 'final_test_replication',
                'execution_identity': identity, 'status': 'RUN_FAILED'}))
            receipts = run_root/'receipts'
            receipts.mkdir()
            (receipts/f'{run_id}.json').write_text(json.dumps({
                'status': 'PROCESS_EXITED', 'process_pid': 99999998,
                'process_start_identity': 'stale', 'process_group_id': 99999998}))
            p2_id = run_id.rsplit('_P1', 1)[0] + '_P2'
            p2_receipt = receipts/f'{p2_id}.json'
            original = json.dumps({'status': 'PROCESS_EXITED', 'process_pid': 99999997,
                                   'process_start_identity': 'stale',
                                   'process_group_id': 99999997}).encode() + b'\n'
            p2_receipt.write_bytes(original)
            logs = run_root/'launch_logs'
            logs.mkdir()
            (logs/f'{p2_id}.stdout.log').write_text('retained P2 startup log')
            args = (run_id, 100, 'TEST_SHORT_NARROW', 'CORRIDOR', root/'input',
                    run_root, identity, root/'ros', root/'workspace', root/'glog',
                    root/'binary', root/'identity.json')
            result = runner._run_scene(*args, retry_failed=True,
                retry_diagnosis='Confirmed transient startup issue; preserving original P1 evidence.')
            self.assertEqual(result['run_id'], p2_id)
            self.assertEqual(p2_receipt.read_bytes(), original)

    def test_partial_offline_evaluation_is_archived_before_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            evaluation = Path(folder)/'evaluation'
            evaluation.mkdir()
            (evaluation/'evaluation.csv').write_bytes(b'partial csv')
            (evaluation/'stdout.log').write_text('partial stdout')
            runner._archive_partial_evaluation(evaluation)
            self.assertFalse((evaluation/'evaluation.csv').exists())
            archive = evaluation/'attempts/offline_01'
            self.assertEqual((archive/'evaluation.csv').read_bytes(), b'partial csv')
            self.assertEqual((archive/'stdout.log').read_text(), 'partial stdout')


if __name__ == '__main__':
    unittest.main()
