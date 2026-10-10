"""Run all32 D050 development corridor/control pairs, preserving every attempt."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time

import final_evaluation_runner as process_identity
from record_pointlio_attempt import REPO_SOURCE_FILES, sha256
import t14_development_runner as development
from validate_pointlio_development_input import validate_input, validate_native, glog_identity
from verify_pointlio_development_attempt import verify

ROOT = Path(__file__).resolve().parents[3]
RUNNER = ROOT / 'research_paper/experiments/run_point_lio_indicator_feasibility.sh'
CONFIG = ROOT / 'research_paper/configs/point_lio_simulation_development.yaml'


def schedule():
    return [{'seed': seed, 'scene': scene, 'control': scene == 'CONTROL',
             'run_id': f'POINTLIO_DEV{seed:02d}_{scene}_XM6_P1'}
            for seed in range(14, 46) for scene in ('CORRIDOR', 'CONTROL')]


def stop_group(process):
    for sig, grace in ((signal.SIGINT, 45), (signal.SIGTERM, 10), (signal.SIGKILL, 5)):
        if process.poll() is not None and not process_identity._process_group_members(process.pid):
            return
        try:
            os.killpg(process.pid, sig)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + grace
        while time.monotonic() < deadline:
            if process.poll() is not None and not process_identity._process_group_members(process.pid):
                return
            time.sleep(0.1)
    raise RuntimeError('Point-LIO native process group did not terminate')


def source_identity():
    paths = {name: ROOT / name for name in REPO_SOURCE_FILES}
    paths.update({str(Path(__file__).relative_to(ROOT)): Path(__file__),
                  'research_paper/experiments/src/verify_pointlio_development_attempt.py':
                  Path(__file__).with_name('verify_pointlio_development_attempt.py'),
                  'research_paper/experiments/src/trajectory_eval.py':
                  Path(__file__).with_name('trajectory_eval.py')})
    return {name: sha256(path) for name, path in paths.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-root', required=True, type=Path)
    parser.add_argument('--output-root', required=True, type=Path)
    parser.add_argument('--ros-env', required=True, type=Path)
    parser.add_argument('--workspace', required=True, type=Path)
    parser.add_argument('--glog-prefix', required=True, type=Path)
    parser.add_argument('--stop-after', type=int)
    args = parser.parse_args()
    if args.stop_after is not None and not 1 <= args.stop_after <= 64:
        parser.error('--stop-after must be1..64')
    binary = args.workspace / 'devel/lib/point_lio/pointlio_mapping'
    anchor = validate_native(binary, args.workspace / 'src/point_lio', CONFIG)
    process_identity._r2_frozen_artifact_hashes()
    overlay = glog_identity(args.glog_prefix)
    runtime = process_identity._check_analysis_runtime()
    runtime['python_executable'] = str(Path(runtime['python_executable']).resolve())
    runtime['python_binary_sha256'] = sha256(Path(runtime['python_executable']))
    probe = json.loads(subprocess.check_output([
        str(args.ros_env / 'bin/python'), '-c',
        'import json,platform,numpy;print(json.dumps(dict(python=platform.python_version(),numpy=numpy.__version__)))'
    ], text=True))
    if probe != {key: runtime[key] for key in ('python', 'numpy')}:
        raise ValueError('selected ROS Python differs from the frozen analysis runtime')
    sources = source_identity()
    output = args.output_root.resolve()
    output.mkdir(parents=True, exist_ok=True)
    rows = schedule()
    summary_path = output / 'development_schedule.json'
    identity = {'sources': sources, 'native_binary_sha256': sha256(binary),
                'config_sha256': sha256(CONFIG), 'native_source': anchor['native_source'],
                'runtime': runtime, 'conda_history_sha256': sha256(args.ros_env / 'conda-meta/history'),
                'paths': {name: str(getattr(args, name).resolve()) for name in
                          ('input_root', 'ros_env', 'workspace', 'glog_prefix')},
                'build_overlay': overlay}
    if summary_path.exists():
        old = json.loads(summary_path.read_text())
        if old['execution_identity'] != identity:
            raise ValueError('Point-LIO cohort identity changed; retain old folder and review a new cohort')
    summary = {'schema': 'pointlio-development-cohort-v1', 'status': 'RUNNING',
               'development_only': True, 'heldout_inputs_opened': False,
               'threshold_fit_performed': False, 'execution_identity': identity,
               'scheduled_geometry_pairs': 32, 'scheduled_native_runs': 64,
               'runs': [{**r, 'status': 'PENDING'} for r in rows]}
    development._write_json(summary_path, summary)
    try:
        for index, row in enumerate(rows):
            if args.stop_after is not None and index >= args.stop_after:
                summary['status'] = 'BOUNDED_CHECKPOINT'
                break
            summary['current_slot'] = row['run_id']
            development._write_json(summary_path, summary)
            if source_identity() != sources:
                raise RuntimeError('reviewed Point-LIO workflow source changed')
            validate_native(binary, args.workspace / 'src/point_lio', CONFIG)
            if glog_identity(args.glog_prefix) != overlay:
                raise RuntimeError('glog runtime overlay changed during the cohort')
            if shutil.disk_usage(ROOT).free < 1024**3 or shutil.disk_usage(output).free < 1024**3:
                raise RuntimeError('required free-space floor is not satisfied')
            input_id = f"T14_FORMAL_DEV{row['seed']:02d}_{row['scene']}_INPUT_XM6_V1"
            bag = args.input_root / input_id / 'sensors.bag'
            slot = validate_input(bag)
            if any(slot[k] != row[k] for k in ('seed', 'scene', 'control')):
                raise ValueError('Point-LIO schedule/input identity mismatch')
            run_dir = output / 'native' / row['run_id']
            verification_path = output / 'verification' / f"{row['run_id']}.json"
            receipt = output / 'launch_records' / f"{row['run_id']}.json"
            command = ['bash', str(RUNNER), str(args.ros_env), str(args.workspace),
                       str(args.glog_prefix), str(bag), str(CONFIG), str(run_dir),
                       'on', 'development_replication']
            if run_dir.exists():
                prior = json.loads(receipt.read_text())
                if (prior['execution_identity'] != identity or prior['command'] != command
                        or prior['input_manifest'] != slot['input_manifest']):
                    raise ValueError('retained native launch does not match current cohort/input identity')
                actual = process_identity._process_identity(prior.get('pid'))
                group_members = process_identity._process_group_members(prior.get('process_group_id'))
                if ((actual is not None and actual == prior.get('process_start_identity')) or group_members):
                    summary['status'] = 'WAITING_FOR_LIVE_NATIVE_ATTEMPT'
                    summary['live_attempt'] = {**prior, 'live_process_group_members': group_members}
                    development._write_json(summary_path, summary)
                    print(json.dumps(summary['live_attempt']), flush=True)
                    return
                result = verify(run_dir)
                summary['runs'][index] = {**row, 'status': 'CACHED', 'verification': result}
            else:
                existing_logs = output / 'launch_logs'
                if receipt.exists() or any((existing_logs / f"{row['run_id']}.{suffix}.log").exists()
                                          for suffix in ('stdout', 'stderr')):
                    raise RuntimeError('prior startup attempt exists without a native directory; preserve it and diagnose before retry')
                run_dir.parent.mkdir(parents=True, exist_ok=True)
                log_root = output / 'launch_logs'
                log_root.mkdir(exist_ok=True)
                started = time.monotonic()
                record = {**row, 'status': 'STARTING', 'command': command,
                          'input_manifest': slot['input_manifest'],
                          'input_bag_sha256': sha256(bag), 'execution_identity': identity}
                development._write_json(receipt, record)
                with (log_root / f"{row['run_id']}.stdout.log").open('w') as stdout, \
                        (log_root / f"{row['run_id']}.stderr.log").open('w') as stderr:
                    process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True)
                    record.update(status='RUNNING', pid=process.pid,
                                  process_start_identity=process_identity._process_identity(process.pid),
                                  process_group_id=process.pid)
                    development._write_json(receipt, record)
                    try:
                        code = process.wait(timeout=240)
                    except BaseException:
                        stop_group(process)
                        record.update(status='INTERRUPTED_OR_TIMEOUT', return_code=process.returncode,
                                      elapsed_s=time.monotonic() - started)
                        development._write_json(receipt, record)
                        raise
                record.update(status='PROCESS_EXITED', return_code=code,
                              elapsed_s=time.monotonic() - started)
                development._write_json(receipt, record)
                if code:
                    raise RuntimeError(f"native Point-LIO attempt failed; retained logs: {log_root}")
                if source_identity() != sources:
                    raise RuntimeError('Point-LIO sources changed during the native attempt')
                result = verify(run_dir)
                summary['runs'][index] = {**row, 'status': 'COMPLETED', 'verification': result}
            native = json.loads((run_dir / 'run_manifest.json').read_text())
            if (native['run_id'] != row['run_id'] or any(native[k] != row[k] for k in ('seed', 'scene', 'control'))
                    or native['input_manifest'] != slot['input_manifest']
                    or native['input_bag']['sha256'] != sha256(bag)
                    or native['repository_sources'] != {name: sources[name] for name in REPO_SOURCE_FILES}
                    or any(native['runtime'][k] != runtime[k] for k in ('python', 'numpy', 'python_executable', 'python_binary_sha256'))
                    or native['runtime']['conda_history_sha256'] != identity['conda_history_sha256']):
                raise ValueError('completed/cached native attempt differs from scheduled cohort identity')
            if native['build_overlay'] != overlay or glog_identity(args.glog_prefix) != overlay:
                raise ValueError('completed/cached native overlay differs from cohort identity')
            development._write_json(verification_path, result)
            evaluation_root = output / 'evaluation' / row['run_id']
            evaluation_root.mkdir(parents=True, exist_ok=True)
            evaluation_path = evaluation_root / 'evaluation.csv'
            evaluation_identity = {
                'native_manifest_sha256': sha256(run_dir / 'run_manifest.json'),
                'poses_sha256': sha256(run_dir / 'poses_segmented.csv'),
                'reference_sha256': sha256(bag.parent / 'reference.txt'),
                'reference_metadata_sha256': sha256(bag.parent / 'reference_metadata.json'),
                'evaluator_sha256': sha256(ROOT / 'research_paper/experiments/src/trajectory_eval.py'),
                'runtime': runtime, 'conda_history_sha256': identity['conda_history_sha256'],
                'build_overlay': overlay,
            }
            evaluation_manifest = evaluation_root / 'evaluation_manifest.json'
            reusable = False
            if evaluation_manifest.exists() and evaluation_path.exists():
                prior = json.loads(evaluation_manifest.read_text())
                reusable = (prior['identity'] == evaluation_identity
                            and prior['output_sha256'] == sha256(evaluation_path))
            if not reusable:
                command = [str(args.ros_env / 'bin/python'),
                    str(ROOT / 'research_paper/experiments/src/trajectory_eval.py'),
                    '--poses', str(run_dir / 'poses_segmented.csv'),
                    '--reference', str(bag.parent / 'reference.txt'), '--output', str(evaluation_path),
                    '--run-id', row['run_id'], '--event-id', f"POINTLIO_DEVELOPMENT_EXIT_{row['seed']}",
                    '--body-transform-json', str(bag.parent / 'reference_metadata.json'),
                    '--development-only', '--entry-start-ns', '1010500000000']
                process = subprocess.run(command, capture_output=True, text=True, timeout=180)
                (evaluation_root / 'stdout.log').write_text(process.stdout)
                (evaluation_root / 'stderr.log').write_text(process.stderr)
                process.check_returncode()
                if (source_identity() != sources
                        or sha256(args.ros_env / 'conda-meta/history') != identity['conda_history_sha256']
                        or glog_identity(args.glog_prefix) != overlay):
                    raise RuntimeError('Point-LIO evaluation source/runtime changed during postprocessing')
                development._write_json(evaluation_manifest, {
                    'role': 'development_only_offline_evaluation', 'identity': evaluation_identity,
                    'command': command, 'summary': json.loads(process.stdout),
                    'output_sha256': sha256(evaluation_path)})
            summary['runs'][index]['evaluation_manifest_sha256'] = sha256(evaluation_manifest)
            development._write_json(summary_path, summary)
            print(f"{index+1}/64 {row['run_id']} {summary['runs'][index]['status']}", flush=True)
        else:
            summary['status'] = 'COMPLETE_NATIVE_COHORT_PENDING_ANALYSIS'
        summary['counts'] = dict(Counter(r['status'] for r in summary['runs']))
        development._write_json(summary_path, summary)
    except BaseException as exc:
        summary.update(status='INTERRUPTED' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'BLOCKED',
                       reason=f'{type(exc).__name__}: {exc}')
        development._write_json(summary_path, summary)
        raise


if __name__ == '__main__':
    main()
