"""Recover the frozen development cohort in fresh, supervised run folders.

Historical files are never overwritten. The existing lifecycle owns native
attempts/retries; separate hash-bound analysis adapters expose its new evidence
to the unchanged T16 evaluator. Only the 32 declared development pairs enter.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import shutil
import socket
import sys

import final_evaluation_runner as lifecycle
import t14_development_runner as development

ROOT = lifecycle.ROOT
SRC = Path(__file__).resolve().parent
HISTORICAL = ROOT / 'research_paper/evidence/t16_development_analysis_manifest.json'


def schedule():
    return development.build_schedule(list(range(14, 46)))


def validate_scientific_input(input_dir, row, expected):
    manifest = development._validate_input(input_dir, row['seed'], row['control'])
    for filename, key in [('sensors.bag', 'sensor_bag_sha256'),
                          ('reference.txt', 'reference_sha256'),
                          ('reference_metadata.json', 'reference_metadata_sha256')]:
        if lifecycle.sha256_file(input_dir / filename) != expected[key]:
            raise ValueError(f"historical scientific input changed: {row['run_id']}/{filename}")
    return manifest


def analysis_adapter(destination, actual_dir, row, input_dir, backend, sources, runtime):
    path = actual_dir / 'run_manifest.json'
    original = json.loads(path.read_text())
    if original['status'] != 'COMPLETED':
        raise ValueError('cannot expose an incomplete native attempt for analysis')
    if (original['scheduled_run_id'] != row['run_id'] or original['seed'] != row['seed']
            or original['scene'] != row['scene'] or original['role'] != 'development'
            or original['control'] is not row['control']
            or original['route_profile'] != development.PROFILE_ID
            or original['input_manifest']['route_profile']['profile_id'] != development.PROFILE_ID):
        raise ValueError('native slot identity does not match the analysis slot')
    inputs = {
        'input_manifest': input_dir / 'manifest.json',
        'sensor_bag': input_dir / 'sensors.bag',
        'reference': input_dir / 'reference.txt',
        'reference_metadata': input_dir / 'reference_metadata.json',
    }
    fingerprint = original['fingerprint']
    input_hashes = {
        'input_manifest': fingerprint['input_manifest_file_sha256'],
        'sensor_bag': fingerprint['sensor_bag_sha256'],
        'reference': fingerprint['reference_sha256'],
        'reference_metadata': fingerprint['reference_metadata_sha256'],
    }
    if any(lifecycle.sha256_file(p) != input_hashes[name] for name, p in inputs.items()):
        raise ValueError('input identity changed after native replay')
    native_identity = fingerprint['execution_identity']
    if (native_identity['sources'] != sources or native_identity['backend'] != backend
            or native_identity['runtime'] != runtime
            or fingerprint['backend_binary_sha256'] != backend['binary_sha256']
            or fingerprint['configuration_sha256'] != sources['config']):
        raise ValueError('analysis sources/backend differ from the native replay identity')
    for name, digest in original['outputs'].items():
        if lifecycle.sha256_file(actual_dir / name) != digest:
            raise ValueError(f'completed output changed: {actual_dir}/{name}')
    destination.mkdir(parents=True, exist_ok=True)
    for name in original['outputs']:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            if target.resolve() != (actual_dir / name).resolve():
                raise ValueError(f'analysis adapter target changed: {target}')
        else:
            target.symlink_to((actual_dir / name).resolve())
    adapter = {
        'schema': 't14-restored-analysis-contract-v1',
        'provenance': 'New supervised replay; not a recovered historical runtime manifest.',
        'role': 'development', 'run_id': row['run_id'], 'status': 'COMPLETED',
        'seed': row['seed'], 'scene': row['scene'], 'control': row['control'],
        'repeat': row['repeat'], 'route_profile': development.PROFILE_ID,
        'source_lifecycle_manifest': str(path),
        'source_lifecycle_manifest_sha256': lifecycle.sha256_file(path),
        'fingerprint': {
            'input_hashes': input_hashes,
            'backend': backend, 'sources': sources, 'runtime': runtime,
        },
        'outputs': original['outputs'],
        'sensor_bag_sha256': input_hashes['sensor_bag'],
        'reference_sha256': input_hashes['reference'],
        'reference_metadata_sha256': input_hashes['reference_metadata'],
        'elapsed_s': original['elapsed_s'], 'completion_validation': original['completion_validation'],
        'dcreg_summary': original['postprocess_summaries'][1],
        'evaluation_local_valid_rows': original['postprocess_summaries'][2]['local_valid'],
    }
    development._write_json(destination / 'run_manifest.json', adapter)
    return adapter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-root', required=True, type=Path)
    parser.add_argument('--output-root', required=True, type=Path)
    parser.add_argument('--ros-env', required=True, type=Path)
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--stop-after', type=int, help='Bounded lifecycle trial; resume keeps the full schedule.')
    args = parser.parse_args()
    if args.stop_after is not None and not 1 <= args.stop_after <= 68:
        parser.error('--stop-after must be 1..68')
    os.environ['ROS_MASTER_URI'] = 'http://127.0.0.1:11311'
    os.environ['ROS_IP'] = '127.0.0.1'
    os.environ.pop('ROS_HOSTNAME', None)
    historical = json.loads(HISTORICAL.read_text())
    records = historical['input_audit']['primary_run_provenance']
    expected = {(r['seed'], r['scene']): r for r in records}
    required = {(seed, scene) for seed in range(14, 46) for scene in ('CORRIDOR', 'CONTROL')}
    if len(records) != 64 or set(expected) != required:
        raise ValueError('historical input inventory must contain exactly 32 development pairs')
    lifecycle._r2_frozen_artifact_hashes()
    runtime = lifecycle._check_analysis_runtime()
    binary = args.workspace / 'devel/.private/fast_lio/lib/fast_lio/fastlio_mapping'
    backend = lifecycle._check_backend(args.ros_env, args.workspace, binary)
    source_paths = dict(lifecycle._t14_source_paths())
    source_paths['replay_script'] = lifecycle.FINAL_RUN_SCRIPT
    source_paths.update(runner=Path(__file__), lifecycle=Path(lifecycle.__file__),
                        development_runner=Path(development.__file__))
    sources = {name: lifecycle.sha256_file(path) for name, path in source_paths.items()}
    identity = {'role': 'primary_development_recovery', 'backend': backend,
                'runtime': runtime, 'sources': sources,
                'historical_input_inventory_sha256': lifecycle.sha256_file(HISTORICAL),
                'supervised_wrapper_sha256': lifecycle.sha256_file(lifecycle.FINAL_RUN_SCRIPT)}
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=True)
    analysis_root = output / 'analysis_contract'
    analysis_root.mkdir(exist_ok=True)
    ledger_target = analysis_root / 'failure_ledger.csv'
    if ledger_target.exists() or ledger_target.is_symlink():
        if not ledger_target.is_symlink() or ledger_target.resolve() != (output / 'native/failure_ledger.csv').resolve():
            raise ValueError('analysis failure-ledger target is not the native lifecycle ledger')
    else:
        ledger_target.symlink_to(output / 'native/failure_ledger.csv')
    summary_path = output / 'recovery_schedule.json'
    rows = schedule()
    summary = {'schema': 'primary-development-recovery-v1', 'development_only': True,
               'heldout_inputs_opened': False, 'threshold_fit_performed': False,
               'status': 'RUNNING', 'execution_identity': identity,
               'scheduled_primary_runs': 64, 'scheduled_repeats': 4,
               'runs': [{**r, 'status': 'PENDING'} for r in rows]}
    if summary_path.exists():
        previous = json.loads(summary_path.read_text())
        if previous['execution_identity'] != identity:
            raise ValueError('recovery identity changed; use a separately reviewed fresh output root')
    development._write_json(summary_path, summary)
    count = 0
    try:
        recover_rows(args, output, rows, expected, summary, summary_path, source_paths,
                     sources, backend, binary, runtime, identity)
    except Exception as exc:
        summary.update(status='BLOCKED', reason=str(exc))
        development._write_json(summary_path, summary)
        raise


def recover_rows(args, output, rows, expected, summary, summary_path, source_paths,
                 sources, backend, binary, runtime, identity):
    count = 0
    for index, row in enumerate(rows):
        summary['current_slot'] = row['run_id']
        if args.stop_after is not None and count >= args.stop_after:
            summary['status'] = 'BOUNDED_CHECKPOINT'
            break
        if shutil.disk_usage(ROOT).free < 1024**3 or shutil.disk_usage(output).free < 1024**3:
            raise RuntimeError('required free-space floor is not satisfied')
        if any(lifecycle.sha256_file(path) != sources[name] for name, path in source_paths.items()):
            raise RuntimeError('reviewed recovery source changed while the cohort was running')
        if lifecycle._check_backend(args.ros_env, args.workspace, binary) != backend:
            raise RuntimeError('native backend identity changed during recovery')
        input_id = f"T14_FORMAL_DEV{row['seed']:02d}_{row['scene']}_INPUT_XM6_V1"
        input_dir = args.input_root / input_id
        validate_scientific_input(input_dir, row, expected[(row['seed'], row['scene'])])
        with socket.socket() as probe:
            if probe.connect_ex(('127.0.0.1', 11311)) == 0:
                raise RuntimeError('default ROS master port is occupied; refusing to alter another session')
        result = lifecycle._run_scene(row['run_id'], row['seed'], 'DEVELOPMENT_RECOVERY',
            row['scene'], input_dir, output / 'native', args.ros_env, args.workspace,
            backend['binary_sha256'], None, identity)
        summary['runs'][index] = {**row, **result}
        development._write_json(summary_path, summary)
        if result['status'] not in ('COMPLETED', 'CACHED'):
            summary['status'] = 'BLOCKED'
            summary['blocking_run'] = row['run_id']
            development._write_json(summary_path, summary)
            raise RuntimeError(f"native attempt failed or still active: {result}")
        actual = output / 'native' / result['run_id']
        if any(lifecycle.sha256_file(path) != sources[name] for name, path in source_paths.items()):
            raise RuntimeError('reviewed recovery source changed during the native replay')
        if lifecycle._check_backend(args.ros_env, args.workspace, binary) != backend:
            raise RuntimeError('native backend identity changed during replay')
        adapter = analysis_adapter(output / 'analysis_contract' / row['run_id'], actual,
                                   row, input_dir, backend, sources, runtime)
        old = expected[(row['seed'], row['scene'])]['key_output_sha256']
        summary['runs'][index]['historical_raw_output_matches'] = {
            name: lifecycle.sha256_file(actual / 'stream' / name) == digest
            for name, digest in old.items() if name != 'evaluation.csv'}
        summary['runs'][index]['analysis_adapter_sha256'] = lifecycle.sha256_file(
            output / 'analysis_contract' / row['run_id'] / 'run_manifest.json')
        development._write_json(summary_path, summary)
        count += 1
        print(f"{index+1}/68 {row['run_id']} {result['status']}", flush=True)
    else:
        summary['status'] = 'COMPLETE_NATIVE_COHORT_PENDING_ANALYSIS'
    summary['counts'] = dict(Counter(r['status'] for r in summary['runs']))
    development._write_json(summary_path, summary)
    print(summary['status'], flush=True)


if __name__ == '__main__':
    main()
