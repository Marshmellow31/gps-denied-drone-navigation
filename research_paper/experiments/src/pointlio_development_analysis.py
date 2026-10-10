"""Apply the unchanged frozen outcome/selection rules to Point-LIO's own data."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import json
import math
from pathlib import Path
import sys

from final_evaluation_runner import _check_analysis_runtime, _r2_frozen_artifact_hashes

import t16_development_analysis as common
from validate_pointlio_development_input import validate_input
from verify_pointlio_development_attempt import verify

ROOT = common.ROOT
SCALAR = 'POINTLIO_MIN_EIG_G3'
FIXED = 'POINTLIO_DCREG_SCHUR_MASK'


def load_run(run_dir, input_dir, evaluation_dir):
    verification = verify(run_dir)
    native = json.loads((run_dir / 'run_manifest.json').read_text())
    manifest = json.loads((input_dir / 'manifest.json').read_text())
    slot = validate_input(input_dir / 'sensors.bag')
    if (native['seed'] != slot['seed'] or native['scene'] != slot['scene']
            or native['input_manifest'] != slot['input_manifest']):
        raise ValueError('Point-LIO pose/reference inputs do not match the declared development slot')
    reference_path = input_dir / 'reference.txt'
    metadata = input_dir / 'reference_metadata.json'
    reference = common.trajectory.load_reference(reference_path)
    body = common.trajectory.load_body_transform(metadata, reference_path, True)
    poses = common.trajectory.load_estimates(run_dir / 'poses_segmented.csv', 'simulation_epoch')
    evaluated = json.loads((evaluation_dir / 'evaluation_manifest.json').read_text())
    expected_identity = {
        'native_manifest_sha256': common.sha256_file(run_dir / 'run_manifest.json'),
        'poses_sha256': common.sha256_file(run_dir / 'poses_segmented.csv'),
        'reference_sha256': common.sha256_file(reference_path),
        'reference_metadata_sha256': common.sha256_file(metadata),
        'evaluator_sha256': common.sha256_file(ROOT / 'research_paper/experiments/src/trajectory_eval.py'),
        'runtime': {key: native['runtime'][key] for key in
                    ('python', 'numpy', 'python_executable', 'python_binary_sha256')},
        'conda_history_sha256': native['runtime']['conda_history_sha256']}
    expected_identity['build_overlay'] = native['build_overlay']
    if (evaluated['identity'] != expected_identity or evaluated['output_sha256'] !=
            common.sha256_file(evaluation_dir / 'evaluation.csv')):
        raise ValueError('Point-LIO offline evaluation does not match native/reference identities')
    exit_s = float(manifest['route_profile']['exit_time_s'])
    windows, truth_ok, reason = common.build_primary_windows(poses, reference, body, exit_s)
    label = None if slot['control'] else common.find_recovery(
        windows, exit_s, truth_eligible=truth_ok, truth_reason=reason)
    indicators = common._read_csv(run_dir / 'pointlio_indicators.csv')
    diagnostics = {SCALAR: [], FIXED: []}
    for row in indicators:
        valid = row['valid'].lower() == 'true'
        score = float(row['lambda_min_3m']) if valid else None
        fixed_score = float(row['DCREG_HEALTH_SCORE']) if valid else None
        if valid and (not math.isfinite(score) or not math.isfinite(fixed_score)):
            raise ValueError('valid Point-LIO diagnostic has non-finite scores')
        stamp, segment = int(row['timestamp_ns']), int(row['segment_id'])
        diagnostics[SCALAR].append(common.DiagnosticRecord(
            stamp, valid, score, None, segment, row['unavailable_reason']))
        diagnostics[FIXED].append(common.DiagnosticRecord(
            stamp, valid, fixed_score, row['DCREG_state'] == 'HEALTHY' if valid else None,
            segment, row['unavailable_reason']))
    for records in diagnostics.values():
        if any(b.timestamp_ns <= a.timestamp_ns for a, b in zip(records, records[1:])):
            raise ValueError('Point-LIO diagnostics are not strictly timestamp ordered')
    decisions = {name: common.associate_decision_ticks(rows, poses)
                 for name, rows in diagnostics.items()}
    run = common.DevelopmentRun(
        run_dir.name, slot['seed'], slot['scene'], slot['control'], exit_s,
        float(manifest['scene_geometry']['corridor_length_m']), run_dir, native,
        manifest, poses, reference, body, windows, label, diagnostics, decisions,
        common._read_csv(evaluation_dir / 'evaluation.csv'))
    return run, verification, indicators


def analyze(native_root, input_root, output):
    _r2_frozen_artifact_hashes()
    runtime = _check_analysis_runtime()
    interpreter = Path(sys.executable).resolve()
    runtime.update(python_executable=str(interpreter),
                   python_binary_sha256=common.sha256_file(interpreter),
                   conda_history_sha256=common.sha256_file(interpreter.parents[1] / 'conda-meta/history'))
    output.mkdir(parents=True, exist_ok=True)
    runs, provenance, availability, scales = [], [], Counter(), []
    for seed in range(14, 46):
        for scene in ('CORRIDOR', 'CONTROL'):
            run_id = f'POINTLIO_DEV{seed:02d}_{scene}_XM6_P1'
            input_id = f'T14_FORMAL_DEV{seed:02d}_{scene}_INPUT_XM6_V1'
            run_dir, input_dir = native_root / run_id, input_root / input_id
            evaluation_dir = native_root.parent / 'evaluation' / run_id
            run, verification, indicators = load_run(run_dir, input_dir, evaluation_dir)
            if run.run_manifest['runtime'] != runtime:
                raise ValueError('Point-LIO analysis runtime differs from its recorded export runtime')
            runs.append(run)
            availability.update(r['unavailable_reason'] or 'VALID' for r in indicators)
            provenance.append({'run_id': run_id, 'seed': seed, 'scene': scene,
                'native_manifest_sha256': common.sha256_file(run_dir / 'run_manifest.json'),
                'input_manifest_sha256': common.sha256_file(input_dir / 'manifest.json'),
                'pose_source': 'Point-LIO own segmented pose stream',
                'verification': verification,
                'key_output_sha256': {name: common.sha256_file(run_dir / name) for name in
                    ('poses.csv', 'poses_segmented.csv', 'pointlio_indicators.csv')},
                'evaluation_sha256': common.sha256_file(evaluation_dir / 'evaluation.csv'),
                'evaluation_manifest_sha256': common.sha256_file(evaluation_dir / 'evaluation_manifest.json')})
            for row in indicators:
                scales.append({'run_id': run_id, 'seed': seed, 'scene': scene,
                    **{key: row[key] for key in ('frame_id', 'timestamp_ns', 'valid', 'unavailable_reason',
                        'lambda_min_1m', 'lambda_min_3m', 'lambda_min_5m')}})
    corridors = [r for r in runs if not r.control]
    controls = [r for r in runs if r.control]
    if len(corridors) != 32 or len(controls) != 32 or any(r.label is not None for r in controls):
        raise ValueError('Point-LIO cohort is not exactly32 paired corridor/control scenes')
    if any(not r.label.truth_eligible for r in corridors):
        raise ValueError('corridor truth eligibility incomplete; report and review before selection')
    selection, candidates = common.select_fastlio_threshold(corridors, method=SCALAR)
    threshold = (float(selection['threshold'])
                 if selection.get('status') == 'SELECTED_DEVELOPMENT_THRESHOLD' else None)
    scalar, scalar_events = common.summarize_method(runs, SCALAR, threshold,
        scalar_method=SCALAR, backend_label='Point-LIO')
    fixed, fixed_events = common.summarize_method(runs, FIXED, None,
        scalar_method=SCALAR, backend_label='Point-LIO')
    labels = [{'run_id': r.run_id, 'seed': r.seed, **asdict(r.label)} for r in corridors]
    common._write_csv(output / 'pointlio_threshold_candidates.csv', candidates)
    common._write_csv(output / 'pointlio_truth_labels.csv', labels)
    common._write_csv(output / 'pointlio_scalar_event_metrics.csv', scalar_events)
    common._write_csv(output / 'pointlio_dcreg_event_metrics.csv', fixed_events)
    common._write_csv(output / 'pointlio_lever_scale_outputs.csv', scales)
    result = {'schema': 'pointlio-development-analysis-v1', 'status': 'DONE_DEVELOPMENT_ONLY',
        'heldout_inputs_opened': False, 'role': 'development_only',
        'geometry_pair_count': 32, 'native_run_count': 64,
        'threshold_fit_source': '32 formal corridor development slots only; controls and feasibility excluded',
        'pointlio_threshold_selection': selection, 'method_metrics': {SCALAR: scalar, FIXED: fixed},
        'truth_label_counts': dict(Counter(r.label.status for r in corridors)),
        'indicator_availability_counts': dict(availability),
        'run_provenance': provenance,
        'primary_final_sample_size_changed': False,
        'source_hashes': {p.name: common.sha256_file(p) for p in
                         (Path(__file__), Path(common.__file__))},
        'analysis_runtime': runtime,
        'metrics_sha256': common.sha256_file(ROOT / 'research_paper/protocol/METRICS.md'),
        'accepted_amendment_sha256': common.sha256_file(ROOT / 'research_paper/protocol/POINTLIO_REPLICATION_AMENDMENT_20260929.md'),
        'outputs': {p.name: common.sha256_file(p) for p in output.glob('*.csv')},
        'interpretation': 'Development-only threshold selection and description; not final performance.'}
    (output / 'pointlio_development_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-root', type=Path, required=True)
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(args.native_root, args.input_root, args.output_dir)
    print(json.dumps({k: result[k] for k in ('status', 'geometry_pair_count',
        'pointlio_threshold_selection', 'truth_label_counts')}))


if __name__ == '__main__':
    main()
