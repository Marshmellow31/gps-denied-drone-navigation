"""R3-gated Point-LIO replication on the exact primary 48 selected pairs."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

import final_evaluation_runner as primary
import r3_evaluation_workflow as workflow
from record_pointlio_attempt import sha256
from validate_pointlio_development_input import glog_identity, validate_native

ROOT = primary.ROOT
SCRIPT = ROOT / 'research_paper/experiments/run_point_lio_final_replication.sh'
CONFIG = ROOT / 'research_paper/configs/point_lio_simulation_development.yaml'
POINT_FREEZE = ROOT / 'research_paper/protocol/POINTLIO_REPLICATION_FREEZE_20261010.json'
POINT_ANALYSIS = workflow.POINT_ANALYSIS
REPO_SOURCES = (
    ROOT / 'research_paper/experiments/src/run_pointlio_final_replication.py',
    ROOT / 'research_paper/experiments/src/pointlio_final_analysis.py',
    ROOT / 'research_paper/experiments/src/record_pointlio_final_attempt.py',
    ROOT / 'research_paper/experiments/src/verify_pointlio_final_attempt.py',
    ROOT / 'research_paper/experiments/src/validate_pointlio_final_input.py',
    SCRIPT,
)


def _write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(obj, indent=2, sort_keys=True) + '\n')
    tmp.replace(path)


def _archive_input(source: Path, target: Path, expected_hash: str) -> Path:
    target.mkdir(parents=True, exist_ok=True)
    for name in ('sensors.bag', 'reference.txt', 'reference_metadata.json', 'manifest.json'):
        origin, saved = source / name, target / name
        if not origin.is_file():
            raise ValueError(f'Point-LIO final source input is missing: {origin}')
        if saved.exists():
            if name == 'manifest.json':
                archived_identity = primary._input_manifest_identity(json.loads(saved.read_text()))
                current_identity = primary._input_manifest_identity(json.loads(origin.read_text()))
                if archived_identity != current_identity:
                    raise ValueError(f'archived Point-LIO final input identity changed: {saved}')
            elif sha256(saved) != sha256(origin):
                raise ValueError(f'archived Point-LIO final input changed: {saved}')
        else:
            shutil.copy2(origin, saved)
            if sha256(saved) != sha256(origin):
                raise ValueError(f'Point-LIO final input archive copy mismatch: {saved}')
    if sha256(target / 'sensors.bag') != expected_hash:
        raise ValueError('archived Point-LIO sensor bag differs from primary pair identity')
    return target


def _assert_attempt_stopped(run_id: str, run_root: Path) -> None:
    receipt_path = run_root / 'receipts' / f'{run_id}.json'
    if not receipt_path.is_file():
        raise primary.RunInProgressError(f'cannot prove prior Point-LIO attempt is stopped: {run_id}')
    receipt = json.loads(receipt_path.read_text())
    pid = receipt.get('process_pid')
    group = receipt.get('process_group_id')
    start_id = receipt.get('process_start_identity')
    if receipt.get('status') in ('STARTING', 'RUNNING', 'INTERRUPTED_KEEP_OUTPUTS') and (
            not isinstance(pid, int) or not isinstance(group, int) or not isinstance(start_id, str)):
        raise primary.RunInProgressError(f'Point-LIO launch state is unknown; refusing retry: {run_id}')
    if isinstance(pid, int) and start_id and primary._process_identity(pid) == start_id:
        raise primary.RunInProgressError(f'prior Point-LIO process is still live: {run_id}')
    live = primary._process_group_members(group) if isinstance(group, int) else []
    if live:
        raise primary.RunInProgressError(f'prior Point-LIO process group is still live: {live}')


def _archive_partial_evaluation(evaluation_dir: Path) -> None:
    partials = [evaluation_dir / name for name in ('evaluation.csv', 'stdout.log', 'stderr.log')
                if (evaluation_dir / name).is_file()]
    if not partials:
        return
    attempts = evaluation_dir / 'attempts'
    attempts.mkdir(parents=True, exist_ok=True)
    index = 1
    while (attempts / f'offline_{index:02d}').exists():
        index += 1
    archive = attempts / f'offline_{index:02d}'
    archive.mkdir()
    for path in partials:
        shutil.move(str(path), str(archive / path.name))


def _evaluation_identity(native: dict, run_dir: Path, input_dir: Path) -> dict:
    evaluator = ROOT / 'research_paper/experiments/src/trajectory_eval.py'
    return {
        'native_manifest_sha256': sha256(run_dir / 'run_manifest.json'),
        'poses_sha256': sha256(run_dir / 'poses_segmented.csv'),
        'reference_sha256': sha256(input_dir / 'reference.txt'),
        'reference_metadata_sha256': sha256(input_dir / 'reference_metadata.json'),
        'evaluator_sha256': sha256(evaluator),
        'runtime': {k: native['runtime'][k] for k in
                    ('python', 'numpy', 'python_executable', 'python_binary_sha256')},
        'conda_history_sha256': native['runtime']['conda_history_sha256'],
        'build_overlay': native['build_overlay'],
    }


def _analysis_runtime(ros_env: Path) -> dict:
    runtime = primary._check_analysis_runtime()
    py = (ros_env / 'bin/python3').resolve()
    probe = json.loads(subprocess.check_output(
        [str(py), '-c', 'import json,platform,numpy;print(json.dumps(dict(python=platform.python_version(),numpy=numpy.__version__)))'],
        text=True))
    expected = workflow._validate_point_freeze()[1]['analysis_runtime']
    if (probe != {k: expected[k] for k in ('python', 'numpy')}
            or sha256(py) != expected['python_binary_sha256']
            or sha256(py.parents[1] / 'conda-meta/history') != expected['conda_history_sha256']):
        raise ValueError('Point-LIO final runtime differs from its accepted development freeze')
    runtime.update(python=probe['python'], numpy=probe['numpy'],
                   python_executable=str(py), python_binary_sha256=sha256(py),
                   conda_history_sha256=sha256(py.parents[1] / 'conda-meta/history'))
    return runtime


def _run_scene(run_id: str, seed: int, stratum: str, scene: str, input_dir: Path,
               run_root: Path, identity: dict, ros_env: Path, workspace: Path,
               glog: Path, binary: Path, identity_path: Path,
               retry_failed: bool = False, retry_diagnosis: str | None = None) -> dict:
    if retry_failed and (not isinstance(retry_diagnosis, str)
                         or len(retry_diagnosis.strip()) < 20):
        raise ValueError('a diagnosed technical reason of at least 20 characters is required for P2 retry')
    run_dir = run_root / run_id
    evaluation_dir = run_root.parent / 'evaluation' / run_id
    verification_path = run_root / 'verification' / f'{run_id}.json'
    verifier = ROOT / 'research_paper/experiments/src/verify_pointlio_final_attempt.py'
    verify_cmd = [str(ros_env / 'bin/python3'), str(verifier),
                  '--run-dir', str(run_dir), '--input-dir', str(input_dir),
                  '--output', str(verification_path),
                  '--execution-identity-json', str(identity_path)]
    if run_dir.exists():
        manifest_path = run_dir / 'run_manifest.json'
        if not manifest_path.is_file():
            old = None
        else:
            old = json.loads(manifest_path.read_text())
            if (old.get('run_id') != run_id or old.get('study_split') != 'final_test_replication'
                    or old.get('execution_identity') != identity):
                raise ValueError(f'prior Point-LIO attempt identity is incompatible: {run_dir}')
        if old and old.get('status') == 'COMPLETED':
            checked = subprocess.run(verify_cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
            checked.check_returncode()
            evaluation_manifest = evaluation_dir / 'evaluation_manifest.json'
            evaluation_csv = evaluation_dir / 'evaluation.csv'
            if evaluation_manifest.is_file():
                if not evaluation_csv.is_file():
                    raise ValueError(f'completed Point-LIO evaluation manifest lost its CSV: {run_id}')
                evaluation = json.loads(evaluation_manifest.read_text())
                expected_identity = _evaluation_identity(old, run_dir, input_dir)
                if (evaluation.get('role') == 'heldout_offline_evaluation'
                        and evaluation.get('identity') == expected_identity
                        and evaluation.get('output_sha256') == sha256(evaluation_csv)):
                    return {'status': 'CACHED', 'run_id': run_id,
                            'scene': scene, 'seed': seed, 'stratum': stratum,
                            'native_manifest_sha256': sha256(manifest_path),
                            'verification_sha256': sha256(verification_path),
                            'evaluation_manifest_sha256': sha256(evaluation_manifest)}
                raise ValueError(f'preserving changed cached Point-LIO evaluation artifacts: {run_id}')
            _archive_partial_evaluation(evaluation_dir)
            return _offline_evaluate(run_id, seed, stratum, scene, input_dir,
                run_root, run_dir, identity, ros_env, native=json.loads(manifest_path.read_text()),
                status='CACHED', verification_path=verification_path)
        failed_previous = {
            'status': 'FAILED_KEEP_OUTPUTS', 'run_id': run_id,
            'scene': scene, 'seed': seed, 'stratum': stratum,
            'reason': (old or {}).get('reason', 'prior attempt has no completed manifest'),
            'run_dir': str(run_dir),
        }
        if retry_failed:
            failed_previous['retry_diagnosis'] = retry_diagnosis.strip()
        retry_id = run_id.rsplit('_P1', 1)[0] + '_P2'
        retry_dir = run_root / retry_id
        if retry_id != run_id and retry_dir.exists():
            retry_manifest_path = retry_dir / 'run_manifest.json'
            if retry_manifest_path.is_file():
                retry_manifest = json.loads(retry_manifest_path.read_text())
                if retry_manifest.get('status') == 'COMPLETED':
                    retry_result = _run_scene(retry_id, seed, stratum, scene, input_dir,
                        run_root, identity, ros_env, workspace, glog, binary, identity_path,
                        retry_failed=False, retry_diagnosis=None)
                    retry_result['previous_attempt'] = failed_previous
                    return retry_result
        if not retry_failed:
            return failed_previous
        if retry_id == run_id:
            return failed_previous
        if retry_dir.exists():
            retry_result = _run_scene(retry_id, seed, stratum, scene, input_dir,
                run_root, identity, ros_env, workspace, glog, binary, identity_path,
                retry_failed=False, retry_diagnosis=None)
            retry_result['previous_attempt'] = failed_previous
            return retry_result
        retry_receipt_path = run_root / 'receipts' / f'{retry_id}.json'
        retry_logs_path = run_root / 'launch_logs'
        retry_has_logs = any((retry_logs_path / f'{retry_id}.{kind}.log').exists()
                             for kind in ('stdout', 'stderr'))
        if retry_receipt_path.exists() or retry_has_logs:
            _assert_attempt_stopped(retry_id, run_root)
            retry_receipt = json.loads(retry_receipt_path.read_text()) if retry_receipt_path.exists() else {}
            return {'status': 'FAILED_KEEP_OUTPUTS', 'run_id': retry_id,
                    'scene': scene, 'seed': seed, 'stratum': stratum,
                    'reason': retry_receipt.get('status', 'P2 startup evidence is incomplete'),
                    'previous_attempt': failed_previous,
                    'receipt_path': str(retry_receipt_path)}
        _assert_attempt_stopped(run_id, run_root)
        previous_attempt = failed_previous
        run_id = retry_id
        run_dir = retry_dir
        evaluation_dir = run_root.parent / 'evaluation' / run_id
        verification_path = run_root / 'verification' / f'{run_id}.json'
        verify_cmd = [str(ros_env / 'bin/python3'), str(verifier),
                      '--run-dir', str(run_dir), '--input-dir', str(input_dir),
                      '--output', str(verification_path),
                      '--execution-identity-json', str(identity_path)]
    else:
        previous_attempt = None
        old_receipt_path = run_root / 'receipts' / f'{run_id}.json'
        old_logs = run_root / 'launch_logs'
        old_log_exists = any((old_logs / f'{run_id}.{kind}.log').exists()
                             for kind in ('stdout', 'stderr'))
        if old_receipt_path.exists() or old_log_exists:
            old_receipt = json.loads(old_receipt_path.read_text()) if old_receipt_path.exists() else {}
            previous_attempt = {
                'status': 'FAILED_KEEP_OUTPUTS', 'run_id': run_id,
                'scene': scene, 'seed': seed, 'stratum': stratum,
                'reason': old_receipt.get('status', 'prior startup attempt has logs but no receipt'),
                'receipt_path': str(old_receipt_path),
            }
            retry_id = run_id.rsplit('_P1', 1)[0] + '_P2'
            retry_dir = run_root / retry_id
            if retry_id != run_id and retry_dir.exists():
                retry_manifest_path = retry_dir / 'run_manifest.json'
                if retry_manifest_path.is_file():
                    retry_manifest = json.loads(retry_manifest_path.read_text())
                    if retry_manifest.get('status') == 'COMPLETED':
                        retry_result = _run_scene(retry_id, seed, stratum, scene, input_dir,
                            run_root, identity, ros_env, workspace, glog, binary, identity_path,
                            retry_failed=False, retry_diagnosis=None)
                        retry_result['previous_attempt'] = previous_attempt
                        return retry_result
            if not retry_failed:
                return previous_attempt
            retry_receipt = run_root / 'receipts' / f'{retry_id}.json'
            retry_logs = run_root / 'launch_logs'
            retry_has_logs = any((retry_logs / f'{retry_id}.{kind}.log').exists()
                                 for kind in ('stdout', 'stderr'))
            if retry_id == run_id:
                return {**previous_attempt, 'reason': 'single technical retry is already exhausted'}
            if retry_dir.exists():
                retry_result = _run_scene(retry_id, seed, stratum, scene, input_dir,
                run_root, identity, ros_env, workspace, glog, binary, identity_path,
                    retry_failed=False, retry_diagnosis=None)
                retry_result['previous_attempt'] = previous_attempt
                return retry_result
            if retry_receipt.exists() or retry_has_logs:
                _assert_attempt_stopped(retry_id, run_root)
                old_retry = json.loads(retry_receipt.read_text()) if retry_receipt.exists() else {}
                return {'status': 'FAILED_KEEP_OUTPUTS', 'run_id': retry_id,
                    'scene': scene, 'seed': seed, 'stratum': stratum,
                    'reason': old_retry.get('status', 'P2 startup evidence is incomplete'),
                    'previous_attempt': previous_attempt,
                    'receipt_path': str(retry_receipt)}
            _assert_attempt_stopped(run_id, run_root)
            run_id, run_dir = retry_id, retry_dir
            evaluation_dir = run_root.parent / 'evaluation' / run_id
            verification_path = run_root / 'verification' / f'{run_id}.json'
            verify_cmd = [str(ros_env / 'bin/python3'), str(verifier),
                          '--run-dir', str(run_dir), '--input-dir', str(input_dir),
                          '--output', str(verification_path),
                          '--execution-identity-json', str(identity_path)]

    bag = input_dir / 'sensors.bag'
    command = ['bash', str(SCRIPT), str(ros_env), str(workspace), str(glog),
               str(bag), str(CONFIG), str(run_dir), str(seed), stratum, scene,
               str(input_dir), str(identity_path)]
    receipts = run_root / 'receipts'
    logs = run_root / 'launch_logs'
    receipts.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    receipt_path = receipts / f'{run_id}.json'
    receipt = {
        'status': 'STARTING', 'role': 'heldout', 'seed': seed, 'stratum': stratum,
        'scene': scene, 'command': command, 'input_bag_sha256': sha256(bag),
        'execution_identity': identity,
    }
    _write(receipt_path, receipt)
    started = time.monotonic()
    with (logs / f'{run_id}.stdout.log').open('w') as out, (logs / f'{run_id}.stderr.log').open('w') as err:
        process = subprocess.Popen(command, cwd=ROOT, stdout=out, stderr=err,
                                   start_new_session=True)
        process_start_identity = primary._process_identity(process.pid)
        receipt.update(status='RUNNING', process_pid=process.pid,
                       process_start_identity=process_start_identity,
                       process_group_id=process.pid)
        _write(receipt_path, receipt)
        try:
            code = process.wait(timeout=900)
        except BaseException:
            try:
                os.killpg(process.pid, signal.SIGINT)
                process.wait(timeout=30)
            except Exception:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            _write(receipt_path, {
                'status': 'INTERRUPTED_KEEP_OUTPUTS', 'role': 'heldout', 'seed': seed,
                'stratum': stratum, 'scene': scene, 'command': command,
                'input_bag_sha256': sha256(bag), 'execution_identity': identity,
                'process_pid': process.pid,
                'process_start_identity': process_start_identity,
                'process_group_id': process.pid,
                'elapsed_s': time.monotonic() - started,
            })
            raise
    receipt = {'status': 'PROCESS_EXITED', 'return_code': code, 'role': 'heldout',
               'seed': seed, 'stratum': stratum, 'scene': scene, 'command': command,
               'input_bag_sha256': sha256(bag), 'execution_identity': identity,
               'process_pid': process.pid,
               'process_start_identity': process_start_identity,
               'process_group_id': process.pid,
               'elapsed_s': time.monotonic() - started}
    _write(receipt_path, receipt)
    if code:
        return {'status': 'FAILED_KEEP_OUTPUTS', 'run_id': run_id,
                'scene': scene, 'seed': seed, 'stratum': stratum,
                'reason': f'native process returned {code}', 'run_dir': str(run_dir),
                **({'previous_attempt': previous_attempt} if previous_attempt else {})}

    manifest_path = run_dir / 'run_manifest.json'
    native = json.loads(manifest_path.read_text())
    if (native.get('role') != 'heldout' or native.get('seed') != seed
            or native.get('stratum') != stratum or native.get('scene') != scene
            or native.get('execution_identity') != identity
            or native.get('input_bag', {}).get('sha256') != receipt['input_bag_sha256']):
        raise ValueError('Point-LIO native manifest does not match the authorized execution slot')
    verified = subprocess.run(verify_cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
    verification_logs = run_root / 'verification_logs'
    verification_logs.mkdir(parents=True, exist_ok=True)
    (verification_logs / f'{run_id}.stdout.log').write_text(verified.stdout)
    (verification_logs / f'{run_id}.stderr.log').write_text(verified.stderr)
    verified.check_returncode()
    result = _offline_evaluate(run_id, seed, stratum, scene, input_dir,
        run_root, run_dir, identity, ros_env, native=native,
        status='COMPLETED', verification_path=verification_path)
    if previous_attempt:
        result['previous_attempt'] = previous_attempt
    return result


def _offline_evaluate(run_id: str, seed: int, stratum: str, scene: str,
                      input_dir: Path, run_root: Path, run_dir: Path,
                      identity: dict, ros_env: Path, native: dict,
                      status: str, verification_path: Path) -> dict:
    manifest_path = run_dir / 'run_manifest.json'
    evaluation_dir = run_root.parent / 'evaluation' / run_id
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    evaluation_csv = evaluation_dir / 'evaluation.csv'
    evaluator = ROOT / 'research_paper/experiments/src/trajectory_eval.py'
    eval_cmd = [str(ros_env / 'bin/python3'), str(evaluator),
        '--poses', str(run_dir / 'poses_segmented.csv'),
        '--reference', str(input_dir / 'reference.txt'), '--output', str(evaluation_csv),
        '--run-id', run_id, '--event-id', f'POINTLIO_FINAL_EXIT_{stratum}_{seed}',
        '--body-transform-json', str(input_dir / 'reference_metadata.json'),
        '--entry-start-ns', '1010500000000']
    evaluated = subprocess.run(eval_cmd, cwd=ROOT, capture_output=True, text=True, timeout=300)
    (evaluation_dir / 'stdout.log').write_text(evaluated.stdout)
    (evaluation_dir / 'stderr.log').write_text(evaluated.stderr)
    evaluated.check_returncode()
    evaluation_identity = _evaluation_identity(native, run_dir, input_dir)
    _write(evaluation_dir / 'evaluation_manifest.json', {
        'role': 'heldout_offline_evaluation', 'identity': evaluation_identity,
        'command': eval_cmd, 'summary': json.loads(evaluated.stdout),
        'output_sha256': sha256(evaluation_csv),
    })
    return {'status': status, 'run_id': run_id,
            'scene': scene, 'seed': seed, 'stratum': stratum,
            'native_manifest_sha256': sha256(manifest_path),
            'verification_sha256': sha256(verification_path),
            'evaluation_manifest_sha256': sha256(evaluation_dir / 'evaluation_manifest.json')}


def run(screen_path: Path, plan_path: Path, primary_root: Path, review_path: Path,
        implementation_freeze: Path, ros_env: Path, workspace: Path, glog: Path,
        binary: Path, scratch_root: Path, output_root: Path,
        minimum_free_mb: int = 1024, retry_failed: bool = False,
        retry_diagnosis: str | None = None) -> dict:
    gate = workflow.require_r3_pass(review_path, implementation_freeze)
    if retry_failed and (not isinstance(retry_diagnosis, str)
                         or len(retry_diagnosis.strip()) < 20):
        raise ValueError('P2 requires a recorded diagnosis of the technical failure')
    _, point_analysis, point_freeze_sha, point_review_sha = workflow._validate_point_freeze()
    point = json.loads(POINT_FREEZE.read_text())
    screen = json.loads(screen_path.read_text())
    plan = json.loads(plan_path.read_text())
    primary_batch = json.loads((primary_root / 'final_batch_summary.json').read_text())
    if (screen.get('status') != 'SCENE_SCREEN_PASS' or screen.get('role') != 'heldout'
            or screen.get('plan_sha256') != primary.sha256_file(plan_path)
            or plan != workflow.build_plan(workflow.FAST_ANALYSIS, primary.SPLITS_PATH)
            or primary_batch.get('role') != 'heldout'
            or primary_batch.get('target_geometry_pairs') != plan['n_test_geometry_pairs']
            or primary_batch.get('scene_screen_sha256') != primary.sha256_file(screen_path)
            or primary_batch.get('r3_review_sha256') != gate['r3_review_sha256']
            or primary_batch.get('implementation_freeze_sha256') != gate['implementation_freeze_sha256']
            or screen.get('r3_review_sha256') != gate['r3_review_sha256']
            or screen.get('implementation_freeze_sha256') != gate['implementation_freeze_sha256']
            or screen.get('reviewed_artifact_hashes') != gate['reviewed_artifact_hashes']
            or primary_batch.get('reviewed_artifact_hashes') != gate['reviewed_artifact_hashes']):
        raise ValueError('Point-LIO replication is not bound to the accepted primary final cohort')
    selected = screen.get('selected_seeds_by_stratum', {})
    if set(selected) != set(primary.heldout.STRATA):
        raise ValueError('Point-LIO screen omits a frozen stratum')
    for stratum, seeds in selected.items():
        bounds = primary.heldout.STRATA[stratum]
        screen_rows = [r for r in screen.get('screened_layouts', []) if r.get('stratum') == stratum]
        if (len(seeds) != plan['geometry_pairs_per_stratum'] or seeds != sorted(set(seeds))
                or any(not bounds['seed_min'] <= seed <= bounds['seed_max'] for seed in seeds)
                or [r.get('seed') for r in screen_rows] != list(range(bounds['seed_min'], seeds[-1] + 1))
                or [r['seed'] for r in screen_rows if r.get('eligible')][:len(seeds)] != seeds):
            raise ValueError('Point-LIO screen differs from the frozen lowest-eligible prefix')
    expected_pairs = {(name, seed) for name, seeds in selected.items() for seed in seeds}
    primary_pairs = {(r['stratum'], r['seed']): r for r in primary_batch.get('pair_results', [])}
    if (set(primary_pairs) != expected_pairs
            or len(primary_pairs) != len(primary_batch.get('pair_results', []))):
        raise ValueError('primary FAST-LIO ledger differs from the selected Point-LIO pair roster')
    if (not binary.is_file() or sha256(binary) != point['native_implementation']['native_binary_sha256']
            or sha256(CONFIG) != point['native_implementation']['configuration_sha256']):
        raise ValueError('Point-LIO native/configuration identity differs from its accepted freeze')
    native_anchor = validate_native(binary, workspace / 'src/point_lio', CONFIG)
    if native_anchor['native_source'] != point['native_implementation']['native_source']:
        raise ValueError('Point-LIO native source differs from its accepted freeze')
    overlay = glog_identity(glog)
    if overlay != point['native_implementation']['build_overlay']:
        raise ValueError('Point-LIO runtime overlay differs from its accepted freeze')
    runtime = _analysis_runtime(ros_env)
    source_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in REPO_SOURCES}
    identity = {
        **gate, 'pointlio_freeze_sha256': point_freeze_sha,
        'pointlio_freeze_review_sha256': point_review_sha,
        'r3_review_path': str(review_path.resolve()),
        'implementation_freeze_path': str(implementation_freeze.resolve()),
        'pointlio_development_analysis_sha256': primary.sha256_file(POINT_ANALYSIS),
        'pointlio_threshold': point['locked_development_selection']['threshold'],
        'runtime': runtime, 'native_binary_sha256': sha256(binary),
        'native_configuration_sha256': sha256(CONFIG),
        'native_source': native_anchor['native_source'], 'build_overlay': overlay,
        'final_plan_sha256': primary.sha256_file(plan_path),
        'scene_screen_sha256': primary.sha256_file(screen_path),
        'primary_final_batch_sha256': primary.sha256_file(primary_root / 'final_batch_summary.json'),
        'source_hashes': source_hashes,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    identity_path = output_root / 'execution_identity.json'
    if identity_path.exists() and json.loads(identity_path.read_text()) != identity:
        raise ValueError('existing Point-LIO final output belongs to another frozen execution identity')
    _write(identity_path, identity)
    run_root = output_root / 'runs'
    run_root.mkdir(exist_ok=True)
    rows = []
    primary_pairs = {(p['stratum'], p['seed']): p for p in primary_batch.get('pair_results', [])}
    stop_batch = False
    try:
        for stratum, seeds in screen['selected_seeds_by_stratum'].items():
            for seed in seeds:
                pair = primary_pairs.get((stratum, seed))
                row = {'stratum': stratum, 'seed': seed, 'scene_runs': [],
                       'retry_diagnosis': retry_diagnosis.strip() if retry_failed else None}
                try:
                    pair_scratch = scratch_root / f'pointlio_{stratum}_{seed}'
                    prepared = primary._prepare_pair(pair_scratch, output_root, run_root,
                        int(seed), stratum, ros_env, identity, minimum_free_mb)
                    pair_scratch, corridor, control, cm, xm, pair_audit = prepared
                    expected_hashes = (pair or {}).get('corridor_bag_sha256'), (pair or {}).get('control_bag_sha256')
                    if (not expected_hashes[0] or not expected_hashes[1]
                            or (cm['sensors.bag']['sha256'], xm['sensors.bag']['sha256']) != expected_hashes):
                        raise ValueError('regenerated Point-LIO inputs do not match the primary pair bag hashes')
                    row['corridor_bag_sha256'], row['control_bag_sha256'] = expected_hashes
                    row['pair_audit'] = pair_audit
                    archived = [
                        _archive_input(corridor, output_root / 'inputs' / f'{stratum}_{seed}' / 'CORRIDOR', expected_hashes[0]),
                        _archive_input(control, output_root / 'inputs' / f'{stratum}_{seed}' / 'CONTROL', expected_hashes[1]),
                    ]
                    for scene, input_dir in zip(('CORRIDOR', 'CONTROL'), archived):
                        run_id = f"FINAL_TEST_{stratum.removeprefix('TEST_')}_{seed}_{scene}_POINTLIO_P1"
                        try:
                            result = _run_scene(run_id, int(seed), stratum, scene, input_dir,
                                run_root, identity, ros_env, workspace, glog, binary,
                                output_root / 'execution_identity.json', retry_failed,
                                retry_diagnosis.strip() if retry_failed else None)
                        except Exception as exc:
                            row['scene_runs'].append({'status': 'FAILED_KEEP_OUTPUTS',
                                'run_id': run_id, 'scene': scene, 'seed': seed,
                                'stratum': stratum, 'reason': f'{type(exc).__name__}: {exc}'})
                            raise
                        previous_attempt = result.pop('previous_attempt', None)
                        if previous_attempt:
                            row['scene_runs'].append(previous_attempt)
                        row['scene_runs'].append(result)
                        if result['status'] not in ('COMPLETED', 'CACHED'):
                            row['status'] = 'FAILED_KEEP_INPUTS'
                            row['reason'] = result.get('reason', 'Point-LIO native attempt failed')
                            stop_batch = True
                            break
                    latest = {scene: next((x for x in reversed(row['scene_runs'])
                                           if x.get('scene') == scene), {})
                              for scene in ('CORRIDOR', 'CONTROL')}
                    if all(latest[s].get('status') in ('COMPLETED', 'CACHED')
                           for s in ('CORRIDOR', 'CONTROL')):
                        row['status'] = 'COMPLETED'
                    elif 'status' not in row:
                        row['status'] = 'FAILED_KEEP_INPUTS'
                    if row['status'] == 'COMPLETED' and pair_scratch.exists():
                        shutil.rmtree(pair_scratch)
                except Exception as exc:
                    row.update(status='FAILED_KEEP_INPUTS', reason=f'{type(exc).__name__}: {exc}')
                    stop_batch = True
                rows.append(row)
                _write(output_root / 'pointlio_final_progress.json', {
                    'schema': 'pointlio-final-progress-v1', 'role': 'heldout',
                    'status': 'RUNNING', **identity, 'pair_results': rows})
                if stop_batch:
                    break
            if stop_batch:
                break
    except KeyboardInterrupt:
        raise
    recorded_pairs = {(r['stratum'], r['seed']) for r in rows}
    for stratum, seeds in screen['selected_seeds_by_stratum'].items():
        for seed in seeds:
            if (stratum, seed) not in recorded_pairs:
                rows.append({'stratum': stratum, 'seed': seed, 'status': 'NOT_RUN',
                    'reason': 'batch stopped after an earlier retained failure',
                    'scene_runs': []})
    completed = sum(r.get('status') == 'COMPLETED' for r in rows)
    result = {'schema': 'pointlio-final-batch-v1', 'role': 'heldout',
        'status': 'COMPLETED' if completed == plan['n_test_geometry_pairs'] else 'INCOMPLETE_KEEP_FAILURES',
        'target_geometry_pairs': plan['n_test_geometry_pairs'],
        'completed_geometry_pairs': completed, 'scene_runs': sum(len(r['scene_runs']) for r in rows),
        'pair_results': rows, 'threshold_fit_performed': False,
        'threshold_locked_from_development': point['locked_development_selection']['threshold'],
        'execution_identity': identity,
        **identity}
    _write(output_root / 'pointlio_final_batch_summary.json', result)
    return result


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--screen', type=Path, required=True)
    p.add_argument('--plan', type=Path, required=True)
    p.add_argument('--primary-results-root', type=Path, required=True)
    p.add_argument('--r3-review', type=Path, required=True)
    p.add_argument('--implementation-freeze', type=Path, required=True)
    p.add_argument('--ros-env', type=Path, required=True)
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--glog-prefix', type=Path, required=True)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--scratch-root', type=Path, required=True)
    p.add_argument('--output-root', type=Path, required=True)
    p.add_argument('--minimum-free-mb', type=int, default=1024)
    p.add_argument('--retry-failed', action='store_true',
                   help='after diagnosis, use the single retained P2 technical retry for failed P1 attempts')
    p.add_argument('--retry-diagnosis',
                   help='required recorded technical reason when --retry-failed is used')
    a = p.parse_args()
    result = run(a.screen, a.plan, a.primary_results_root, a.r3_review,
        a.implementation_freeze, a.ros_env, a.workspace, a.glog_prefix,
        a.binary, a.scratch_root, a.output_root, a.minimum_free_mb, a.retry_failed,
        a.retry_diagnosis)
    print(json.dumps({'status': result['status'], 'completed_pairs': result['completed_geometry_pairs']}))


if __name__ == '__main__':
    main()
