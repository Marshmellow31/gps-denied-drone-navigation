"""Verify a completed D050 development replay without fitting a threshold."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from pointlio_information import join_emitted_pose_segments
from pointlio_indicator_export import verify_input_frame_coverage
from record_pointlio_attempt import sha256, REPO_SOURCE_FILES
from validate_pointlio_development_input import ROOT, validate_input, validate_native, glog_identity
from verify_pointlio_feasibility_pair import verify_manifest_outputs


def rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def verify(run_dir):
    manifest_path = run_dir / 'run_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    verify_manifest_outputs(run_dir, manifest)
    if (manifest['status'] != 'COMPLETED' or manifest['mode'] != 'on'
            or manifest['study_split'] != 'development_replication'
            or manifest['threshold_fit_performed'] is not False
            or manifest['heldout_inputs_opened'] is not False):
        raise ValueError('attempt is not a complete development-only sidecar replay')
    codes = manifest['process_exit_codes']
    if manifest['runtime']['python'] != '3.12.14' or manifest['runtime']['numpy'] != '2.5.3':
        raise ValueError('Point-LIO export did not use the frozen analysis runtime')
    interpreter = Path(manifest['runtime']['python_executable']).resolve()
    if (sha256(interpreter) != manifest['runtime']['python_binary_sha256'] or
            sha256(interpreter.parents[1] / 'conda-meta/history') != manifest['runtime']['conda_history_sha256']):
        raise ValueError('recorded Python/environment dependency identity changed')
    if (any(codes[k] != 0 for k in ('rosbag', 'pointlio', 'pose_logger', 'exporter'))
            or codes['roscore'] not in (0, 130)):
        raise ValueError('a required native process did not exit cleanly')
    slot = validate_input(Path(manifest['input_bag']['path']))
    if any(manifest[k] != slot[k] for k in slot):
        raise ValueError('recorded development input identity differs from verified current input')
    binary = Path(manifest['native_binary']['path'])
    config = Path(manifest['configuration']['path'])
    source_root = Path(manifest['native_source']['root'])
    if not source_root.is_dir():
        raise ValueError('recorded Point-LIO workspace source is unavailable')
    anchor = validate_native(binary, source_root, config)
    if glog_identity(Path(manifest['build_overlay']['glog_prefix'])) != manifest['build_overlay']:
        raise ValueError('recorded glog runtime overlay changed')
    if any(manifest['native_source'][key] != anchor['native_source'][key]
           for key in ('commit', 'dirty_patch_sha256', 'files')):
        raise ValueError('recorded native source does not match accepted implementation')
    bag = Path(manifest['input_bag']['path'])
    if sha256(bag) != manifest['input_bag']['sha256'] or bag.stat().st_size != manifest['input_bag']['bytes']:
        raise ValueError('recorded native input bag changed')
    if sha256(binary) != manifest['native_binary']['sha256'] or sha256(config) != manifest['configuration']['sha256']:
        raise ValueError('recorded native/config identity changed')
    if set(manifest['repository_sources']) != set(REPO_SOURCE_FILES):
        raise ValueError('native manifest omits required Point-LIO workflow sources')
    for relative, digest in manifest['repository_sources'].items():
        if sha256(ROOT / relative) != digest:
            raise ValueError(f'recorded repository source changed: {relative}')
    expected = rows(run_dir / 'input_header_stamps.csv')
    import rosbag
    with rosbag.Bag(str(bag)) as raw_bag:
        raw_stamps = [int(message.header.stamp.to_nsec())
                      for _, message, _ in raw_bag.read_messages(topics=['/sim/points'])]
    if [int(r['header_stamp_ns']) for r in expected] != raw_stamps:
        raise ValueError('preserved input audit differs from actual raw LiDAR message headers')
    frames = rows(run_dir / 'sidecar/frame_ledger.csv')
    indicators = rows(run_dir / 'pointlio_indicators.csv')
    if len(expected) != 600:
        raise ValueError('formal development input must have all600scans')
    verify_input_frame_coverage(frames, [int(r['header_stamp_ns']) for r in expected])
    ids = list(range(1, 601))
    if [int(r['frame_id']) for r in frames] != ids or [int(r['frame_id']) for r in indicators] != ids:
        raise ValueError('native/exported frame identities are incomplete or out of order')
    for row in indicators:
        if row['run_state'] != 'COMPLETE':
            raise ValueError('a native frame did not finish')
        if row['valid'].lower() == 'true':
            if any(not math.isfinite(float(row[name])) for name in
                   ('lambda_min_1m', 'lambda_min_3m', 'lambda_min_5m')):
                raise ValueError('valid frame lacks all three finite score scales')
            if row['DCREG_state'] not in ('HEALTHY', 'DEGENERATE'):
                raise ValueError('valid frame lacks a frozen DCReg state')
    poses = rows(run_dir / 'poses.csv')
    resets = rows(run_dir / 'sidecar/reset_events.csv')
    joined = join_emitted_pose_segments(poses, indicators, resets)
    required_pose_frames = {int(r['frame_id']) for r in frames if r['source_stage'] == 'MEASUREMENT'}
    emitted_pose_frames = {int(r['source_frame_id']) for r in poses if r['event'] == 'POSE'}
    if not required_pose_frames.issubset(emitted_pose_frames):
        raise ValueError('pose logger lost a frame that the pinned native measurement stage publishes')
    segmented = rows(run_dir / 'poses_segmented.csv')
    normalize = lambda row: {k: str(v).lower() if isinstance(v, bool) else str(v) for k, v in row.items()}
    if len(segmented) != len(joined) or any(normalize(a) != normalize(b) for a, b in zip(segmented, joined)):
        raise ValueError('recorded segmented pose stream differs from the truth-free native join')
    return {'status': 'PASS', 'development_only': True, 'heldout_inputs_opened': False,
            'seed': slot['seed'], 'scene': slot['scene'], 'input_frames': len(expected),
            'indicator_frames': len(indicators), 'pose_rows': len(poses),
            'valid_indicator_frames': sum(r['valid'].lower() == 'true' for r in indicators),
            'unavailable_indicator_frames': sum(r['valid'].lower() != 'true' for r in indicators),
            'reset_events': len(resets), 'native_manifest_sha256': sha256(manifest_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = verify(args.run_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
