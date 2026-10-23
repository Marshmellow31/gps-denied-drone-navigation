"""Predeclared development-only native checks for the accepted R2 amendment."""
import argparse
import csv
import json
import os
from pathlib import Path
import signal
import subprocess
import time

import heldout_simulation_v2 as geometry
import final_evaluation_runner as fast
from validate_geometry_development_input import require_r2, validate_input
from validate_pointlio_development_input import validate_native, glog_identity
from pointlio_indicator_export import verify_input_frame_coverage
from verify_pointlio_feasibility_pair import verify_manifest_outputs

ROOT = geometry.ROOT


def rows(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))


def command(cmd, log, receipt):
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open('w') as f:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
        fast._write_json(receipt, {'role': 'development', 'command': cmd,
            'pid': p.pid, 'start_identity': fast._process_identity(p.pid), 'status': 'RUNNING'})
        try:
            code = p.wait(timeout=300)
        except BaseException:
            os.killpg(p.pid, signal.SIGTERM)
            try:
                p.wait(timeout=45)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
            fast._write_json(receipt, {'role': 'development', 'command': cmd,
                                      'status': 'FAILED_OR_INTERRUPTED_KEEP_OUTPUTS'})
            raise
    fast._write_json(receipt, {'role': 'development', 'command': cmd,
                              'exit_code': code, 'status': 'COMPLETED' if code == 0 else 'FAILED_KEEP_OUTPUTS'})
    if code:
        raise RuntimeError(f'command failed: {log}')


def run(a):
    require_r2()
    a.output_root.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    backend = fast._check_backend(a.ros_env, a.fast_workspace,
                                 a.fast_workspace/'devel/lib/fast_lio/fastlio_mapping')
    point_config = ROOT/'research_paper/configs/point_lio_simulation_development.yaml'
    validate_native(a.point_workspace/'devel/lib/point_lio/pointlio_mapping',
                    a.point_workspace/'src/point_lio', point_config)
    overlay = glog_identity(a.glog)
    identity = {'role': 'development_geometry_v2_validation', 'backend': backend,
                'r2_review_sha256': fast.sha256_file(ROOT/'research_paper/reviews/R2_GEOMETRY_AMENDMENT_20261012.md'),
                'generator_sha256': fast.sha256_file(Path(geometry.__file__)),
                'validation_source_sha256': fast.sha256_file(Path(__file__)),
                'runtime': fast._check_analysis_runtime(), 'heldout_inputs_opened': False}
    summary = {'status': 'RUNNING', 'role': 'development_only', 'identity': identity,
               'heldout_inputs_opened': False, 'threshold_fit_performed': False,
               'inputs': {}, 'pairs': {}, 'fastlio': {}, 'pointlio': {}, 'pointlio_overlay': overlay}
    state = a.output_root/'validation_summary.json'
    fast._write_json(state, summary)
    py = str(a.ros_env/'bin/python')
    for group in ('LONG_NARROW', 'LONG_WIDE'):
        for control in (False, True):
            scene = 'CONTROL' if control else 'CORRIDOR'
            key = f'{group}_{scene}'
            folder = a.output_root/'inputs'/key
            print('Generating development input', key, flush=True)
            m = geometry.write_sensor_input(folder, 14, f'DEVELOPMENT_FIXED_{group}', control,
                                            development_fixture=True)
            validate_input(folder/'sensors.bag')
            summary['inputs'][key] = {'path': str(folder), 'manifest_sha256': fast.sha256_file(folder/'manifest.json')}
            fast._write_json(state, summary)
        left = a.output_root/'inputs'/f'{group}_CORRIDOR'
        right = a.output_root/'inputs'/f'{group}_CONTROL'
        audit_cmd = [py, str(fast.PAIR_AUDIT), '--corridor', str(left/'sensors.bag'),
                     '--control', str(right/'sensors.bag'), '--expected-scans', '600', '--expected-imu', '12021']
        command(audit_cmd, a.output_root/'logs'/f'{group}_input_audit.log',
                a.output_root/'receipts'/f'{group}_input_audit.json')
        if fast.sha256_file(left/'reference.txt') != fast.sha256_file(right/'reference.txt'):
            raise ValueError('paired analytic references differ')
        summary['pairs'][group] = {'input_audit': 'PASS', 'reference_identity': 'PASS'}
    # Prespecified minimum: narrow pair and wide control on both backends.
    for group, scene in [('LONG_NARROW', 'CORRIDOR'), ('LONG_NARROW', 'CONTROL'), ('LONG_WIDE', 'CONTROL')]:
        key = f'{group}_{scene}';folder = a.output_root/'inputs'/key
        print('FAST-LIO development replay', key, flush=True)
        result = fast._run_scene(f'GEOMETRY_V2_DEV_{key}_FAST_P1', 14, f'DEVELOPMENT_FIXED_{group}',
            scene, folder, a.output_root/'fastlio', a.ros_env, a.fast_workspace,
            backend['binary_sha256'], fast.LOCKED_DEVELOPMENT_THRESHOLD, identity)
        summary['fastlio'][key] = result
        fast._write_json(state, summary)
        if result['status'] not in ('COMPLETED', 'CACHED'):
            raise ValueError(f'FAST-LIO validation failed: {result}')
    for group, scene, mode in [('LONG_NARROW', 'CORRIDOR', 'on'), ('LONG_NARROW', 'CONTROL', 'on'),
                              ('LONG_NARROW', 'CONTROL', 'off'), ('LONG_WIDE', 'CONTROL', 'on')]:
        key = f'{group}_{scene}_{mode}';folder = a.output_root/'inputs'/f'{group}_{scene}'
        output = a.output_root/'pointlio'/key
        print('Point-LIO development replay', key, flush=True)
        cmd = ['bash', str(ROOT/'research_paper/experiments/run_point_lio_geometry_development.sh'),
               str(a.ros_env), str(a.point_workspace), str(a.glog), str(folder/'sensors.bag'),
               str(point_config), str(output), mode]
        command(cmd, a.output_root/'logs'/f'{key}.log', a.output_root/'receipts'/f'{key}.json')
        native = json.loads((output/'run_manifest.json').read_text())
        verify_manifest_outputs(output, native)
        if native['status'] != 'COMPLETED' or len(rows(output/'poses.csv')) < 590:
            raise ValueError('Point-LIO native coverage incomplete')
        detail = {'manifest_sha256': fast.sha256_file(output/'run_manifest.json'),
                  'pose_rows': len(rows(output/'poses.csv')), 'status': 'PASS'}
        if mode == 'on':
            expected = [int(r['header_stamp_ns']) for r in rows(output/'input_header_stamps.csv')]
            frames = rows(output/'sidecar/frame_ledger.csv')
            if len(expected) != 600:
                raise ValueError('expected 600 development scans')
            verify_input_frame_coverage(frames, expected)
            detail.update(input_frames=len(expected), sidecar_frames=len(frames),
                          indicator_rows=len(rows(output/'pointlio_indicators.csv')))
            eval_file = a.output_root/'evaluation'/f'{key}.csv'
            eval_file.parent.mkdir(parents=True, exist_ok=True)
            cmd = [py, str(fast.EVALUATOR), '--poses', str(output/'poses_segmented.csv'),
                   '--reference', str(folder/'reference.txt'), '--output', str(eval_file),
                   '--run-id', key, '--event-id', f'DEV_{group}',
                   '--body-transform-json', str(folder/'reference_metadata.json'),
                   '--development-only', '--alignment-target-ns', '1005000000000']
            command(cmd, a.output_root/'logs'/f'{key}_evaluation.log',
                    a.output_root/'receipts'/f'{key}_evaluation.json')
            detail['evaluation_sha256'] = fast.sha256_file(eval_file)
        summary['pointlio'][key] = detail
        fast._write_json(state, summary)
    on = a.output_root/'pointlio/LONG_NARROW_CONTROL_on/poses.csv'
    off = a.output_root/'pointlio/LONG_NARROW_CONTROL_off/poses.csv'
    summary['pointlio_control_on_off_pose_identity'] = fast.sha256_file(on) == fast.sha256_file(off)
    if not summary['pointlio_control_on_off_pose_identity']:
        raise ValueError('Point-LIO sidecar-on/off pose streams differ; investigation required')
    summary.update(status='PASS_DEVELOPMENT_NATIVE_VALIDATION', runtime_s=time.monotonic()-started)
    fast._write_json(state, summary)
    print('Development native validation PASS', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for flag in ('output-root', 'ros-env', 'fast-workspace', 'point-workspace', 'glog'):
        p.add_argument('--'+flag, type=Path, required=True)
    args = p.parse_args()
    run(args)
