"""Apply the locked Point-LIO threshold to its own poses on the final cohort."""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

import final_evaluation_runner as primary
import r3_evaluation_workflow as workflow
import t16_development_analysis as common
import heldout_statistics as uncertainty
from final_dataset_analysis import (
    _event_proportion_intervals, _stratum_method_metrics, _tolerance_summary,
    _three_second_by_stratum, _three_second_rate_summary, curve_events, interior_pair,
)
from record_pointlio_attempt import sha256
from verify_pointlio_final_attempt import verify

ROOT = primary.ROOT
SCALAR = 'POINTLIO_MIN_EIG_G3'
FIXED = 'POINTLIO_DCREG_SCHUR_MASK'


def load_run(run_root: Path, input_dir: Path, evaluation_root: Path, run_id: str,
             expected_identity: dict, execution_identity_path: Path):
    run_dir = run_root / run_id
    native = json.loads((run_dir / 'run_manifest.json').read_text())
    verification = verify(run_dir, input_dir, execution_identity_path)
    if (native.get('role') != 'heldout' or native.get('study_split') != 'final_test_replication'
            or native.get('execution_identity') != expected_identity):
        raise ValueError('Point-LIO result is not an authorized final replication run')
    manifest = json.loads((input_dir / 'manifest.json').read_text())
    reference_path = input_dir / 'reference.txt'
    metadata = input_dir / 'reference_metadata.json'
    reference = common.trajectory.load_reference(reference_path)
    body = common.trajectory.load_body_transform(metadata, reference_path, False)
    poses = common.trajectory.load_estimates(run_dir / 'poses_segmented.csv', 'simulation_epoch')
    evaluation_dir = evaluation_root / run_id
    evaluation_csv = evaluation_dir / 'evaluation.csv'
    evaluation_manifest = json.loads((evaluation_dir / 'evaluation_manifest.json').read_text())
    expected_eval = {
        'native_manifest_sha256': sha256(run_dir / 'run_manifest.json'),
        'poses_sha256': sha256(run_dir / 'poses_segmented.csv'),
        'reference_sha256': sha256(reference_path),
        'reference_metadata_sha256': sha256(metadata),
        'evaluator_sha256': sha256(ROOT / 'research_paper/experiments/src/trajectory_eval.py'),
        'runtime': {k: native['runtime'][k] for k in
                    ('python', 'numpy', 'python_executable', 'python_binary_sha256')},
        'conda_history_sha256': native['runtime']['conda_history_sha256'],
        'build_overlay': native['build_overlay'],
    }
    if (evaluation_manifest.get('identity') != expected_eval
            or evaluation_manifest.get('output_sha256') != sha256(evaluation_csv)):
        raise ValueError('Point-LIO final offline evaluation is not bound to its native/reference stream')
    exit_s = float(manifest['route_profile']['exit_time_s'])
    windows, truth_ok, reason = common.build_primary_windows(poses, reference, body, exit_s)
    control = manifest.get('control') is True
    scene = 'CONTROL' if control else 'CORRIDOR'
    label = None if control else common.find_recovery(
        windows, exit_s, truth_eligible=truth_ok, truth_reason=reason)
    indicators = common._read_csv(run_dir / 'pointlio_indicators.csv')
    diagnostics = {SCALAR: [], FIXED: []}
    import math
    for row in indicators:
        valid = row['valid'].lower() == 'true'
        score = float(row['lambda_min_3m']) if valid else None
        fixed_score = float(row['DCREG_HEALTH_SCORE']) if valid else None
        if valid and (not math.isfinite(score) or not math.isfinite(fixed_score)):
            raise ValueError('valid Point-LIO final diagnostic has non-finite values')
        stamp, segment = int(row['timestamp_ns']), int(row['segment_id'])
        diagnostics[SCALAR].append(common.DiagnosticRecord(
            stamp, valid, score, None, segment, row['unavailable_reason']))
        diagnostics[FIXED].append(common.DiagnosticRecord(
            stamp, valid, fixed_score, row['DCREG_state'] == 'HEALTHY' if valid else None,
            segment, row['unavailable_reason']))
    decisions = {name: common.associate_decision_ticks(records, poses)
                 for name, records in diagnostics.items()}
    run = common.DevelopmentRun(
        run_id, native['seed'], scene, control, exit_s,
        float(manifest['scene_geometry']['corridor_length_m']), run_dir, native,
        manifest, poses, reference, body, windows, label, diagnostics, decisions,
        common._read_csv(evaluation_csv))
    return run, verification


def analyze(point_root: Path, primary_root: Path, screen_path: Path, plan_path: Path,
            review_path: Path, freeze_path: Path, output: Path) -> dict:
    gate = workflow.require_r3_pass(review_path, freeze_path)
    runtime = primary._check_analysis_runtime()
    required = {
        'Point-LIO final analysis': Path(__file__).resolve(),
        'Point-LIO final replication runner': ROOT / 'research_paper/experiments/src/run_pointlio_final_replication.py',
        'final dataset analysis caller': ROOT / 'research_paper/experiments/src/final_dataset_analysis.py',
        'R3 evaluation workflow': Path(workflow.__file__).resolve(),
    }
    if any(gate['reviewed_artifact_hashes'].get(name) != sha256(path)
           for name, path in required.items()):
        raise ValueError('Point-LIO final analysis source is not bound to the R3 inventory')
    screen = json.loads(screen_path.read_text())
    plan = json.loads(plan_path.read_text())
    batch = json.loads((point_root / 'pointlio_final_batch_summary.json').read_text())
    primary_batch = json.loads((primary_root / 'final_batch_summary.json').read_text())
    _, point_analysis, point_freeze_sha, point_review_sha = workflow._validate_point_freeze()
    point = json.loads(workflow.POINT_FREEZE.read_text())
    batch_identity = batch.get('execution_identity')
    if (not isinstance(batch_identity, dict)
            or any(batch_identity.get(key) != gate.get(key)
                   for key in ('r3_review_sha256', 'implementation_freeze_sha256',
                               'reviewed_artifact_hashes'))
            or batch_identity.get('pointlio_freeze_sha256') != point_freeze_sha
            or batch_identity.get('pointlio_freeze_review_sha256') != point_review_sha
            or batch_identity.get('pointlio_threshold') != point['locked_development_selection']['threshold']
            or batch_identity.get('final_plan_sha256') != sha256(plan_path)
            or batch_identity.get('scene_screen_sha256') != sha256(screen_path)
            or batch_identity.get('primary_final_batch_sha256') != sha256(primary_root / 'final_batch_summary.json')):
        raise ValueError('Point-LIO execution identity is not bound to the current R3 and Point freezes')
    if (batch.get('role') != 'heldout'
            or batch.get('pointlio_freeze_sha256') != point_freeze_sha
            or batch.get('pointlio_freeze_review_sha256') != point_review_sha
            or batch.get('primary_final_batch_sha256') != sha256(primary_root / 'final_batch_summary.json')
            or batch.get('scene_screen_sha256') != sha256(screen_path)
            or batch.get('final_plan_sha256') != sha256(plan_path)
            or screen.get('status') != 'SCENE_SCREEN_PASS'
            or screen.get('role') != 'heldout'
            or primary_batch.get('r3_review_sha256') != gate['r3_review_sha256']
            or primary_batch.get('implementation_freeze_sha256') != gate['implementation_freeze_sha256']
            or primary_batch.get('reviewed_artifact_hashes') != gate['reviewed_artifact_hashes']
            or primary_batch.get('scene_screen_sha256') != sha256(screen_path)
            or primary_batch.get('target_geometry_pairs') != plan['n_test_geometry_pairs']
            or plan != workflow.build_plan(workflow.FAST_ANALYSIS, workflow.execution.SPLITS_PATH)
            or screen.get('r3_review_sha256') != gate['r3_review_sha256']
            or screen.get('implementation_freeze_sha256') != gate['implementation_freeze_sha256']
            or screen.get('reviewed_artifact_hashes') != gate['reviewed_artifact_hashes']
            or batch.get('reviewed_artifact_hashes') != gate['reviewed_artifact_hashes']
            or batch.get('r3_review_sha256') != gate['r3_review_sha256']
            or batch.get('implementation_freeze_sha256') != gate['implementation_freeze_sha256']):
        raise ValueError('Point-LIO final batch does not match the frozen primary cohort and plan')
    selected = screen['selected_seeds_by_stratum']
    expected = {(name, seed) for name, seeds in selected.items() for seed in seeds}
    pairs = {(r['stratum'], r['seed']): r for r in batch.get('pair_results', [])}
    if set(pairs) != expected or len(pairs) != len(batch.get('pair_results', [])):
        raise ValueError('Point-LIO final batch omitted or duplicated a frozen pair')
    primary_pairs = {(r['stratum'], r['seed']): r for r in primary_batch.get('pair_results', [])}
    if set(primary_pairs) != expected or len(primary_pairs) != len(primary_batch.get('pair_results', [])):
        raise ValueError('primary final batch omitted or duplicated a frozen pair')
    for stratum, seeds in selected.items():
        limits = primary.heldout.STRATA[stratum]
        screen_rows = [r for r in screen.get('screened_layouts', []) if r.get('stratum') == stratum]
        if (len(seeds) != plan['geometry_pairs_per_stratum'] or seeds != sorted(set(seeds))
                or any(not limits['seed_min'] <= s <= limits['seed_max'] for s in seeds)
                or [r.get('seed') for r in screen_rows] != list(range(limits['seed_min'], seeds[-1] + 1))
                or [r['seed'] for r in screen_rows if r.get('eligible')][:len(seeds)] != seeds):
            raise ValueError('Point-LIO screen is not the frozen lowest-eligible reserved prefix')
    if (batch.get('target_geometry_pairs') != len(expected)
            or batch.get('scene_runs') != sum(len(r.get('scene_runs', [])) for r in batch['pair_results'])
            or batch.get('completed_geometry_pairs') != sum(r.get('status') == 'COMPLETED' for r in batch['pair_results'])
            or batch.get('status') != ('COMPLETED' if batch.get('completed_geometry_pairs') == len(expected)
                                      else 'INCOMPLETE_KEEP_FAILURES')):
        raise ValueError('Point-LIO batch counts do not reconcile with its attempt ledger')
    runs, failures = [], []
    completed_pairs = 0
    differences = {}
    for stratum, seed in sorted(expected):
        pair = pairs[(stratum, seed)]
        if pair.get('status') != 'COMPLETED' or len(pair.get('scene_runs', [])) < 2:
            failures.append({'stratum': stratum, 'seed': seed, 'reason': pair.get('reason', 'INCOMPLETE_POINTLIO_PAIR')})
            continue
        scene_attempts = {'CORRIDOR': [], 'CONTROL': []}
        for row in pair['scene_runs']:
            if row.get('scene') not in scene_attempts:
                continue
            scene_attempts[row['scene']].append(row)
        if set(scene_attempts) != {'CORRIDOR', 'CONTROL'} or any(not v for v in scene_attempts.values()):
            failures.append({'stratum': stratum, 'seed': seed, 'reason': 'UNIQUE_SCENE_PAIR_MISSING'})
            continue
        loaded = []
        try:
            for scene in ('CORRIDOR', 'CONTROL'):
                result = scene_attempts[scene][-1]
                if result.get('status') not in ('COMPLETED', 'CACHED'):
                    raise ValueError('scene replay incomplete')
                run_id = result['run_id']
                inp = point_root / 'inputs' / f'{stratum}_{seed}' / scene
                run, verification = load_run(point_root / 'runs', inp,
                                              point_root / 'evaluation', run_id,
                                              batch['execution_identity'],
                                              point_root / 'execution_identity.json')
                if run.seed != seed or run.run_manifest['stratum'] != stratum:
                    raise ValueError('native result is assigned to the wrong frozen slot')
                if run.run_manifest.get('execution_identity') != batch['execution_identity']:
                    raise ValueError('native Point-LIO run is not bound to the current R3 execution identity')
                loaded.append((run, verification))
            if loaded[0][0].label is None or not loaded[0][0].label.truth_eligible:
                raise ValueError('corridor truth label unavailable')
            p_pair = primary_pairs[(stratum, seed)]
            if (pair.get('corridor_bag_sha256') != p_pair.get('corridor_bag_sha256')
                    or pair.get('control_bag_sha256') != p_pair.get('control_bag_sha256')):
                raise ValueError('Point-LIO pair does not use the primary FAST-LIO sensor-bag hashes')
            differences[seed] = interior_pair(loaded[0][0], loaded[1][0])
            runs.extend(item[0] for item in loaded)
            completed_pairs += 1
        except (OSError, ValueError, KeyError) as exc:
            failures.append({'stratum': stratum, 'seed': seed, 'reason': str(exc)})
    primary_complete = (primary_batch.get('status') == 'COMPLETED'
                        and all(primary_pairs[k].get('status') == 'COMPLETED' for k in expected))
    confirmatory = (not failures and primary_complete
                    and completed_pairs == plan['n_test_geometry_pairs']
                    and len(differences) == plan['n_test_geometry_pairs']
                    and len(runs) == 2 * plan['n_test_geometry_pairs']
                    and batch.get('status') == 'COMPLETED')
    threshold = float(point['locked_development_selection']['threshold'])
    metrics = {}
    for method, cutoff in ((SCALAR, threshold), (FIXED, None)):
        summary, events = common.summarize_method(
            runs, method, cutoff, scalar_method=SCALAR, backend_label='Point-LIO')
        intervals = _event_proportion_intervals(runs, method, cutoff, SCALAR, summary)
        summary['event_proportion_intervals'] = intervals
        summary['false_healthy_event_rate_unconditional'] = (
            intervals['initial_false_healthy_unconditional']['fraction'])
        summary['false_healthy_event_unconditional_denominator'] = (
            intervals['initial_false_healthy_unconditional']['trials'])
        summary['interpretation'] = ('Locked Point-LIO final replication; no final-data threshold selection.'
            if confirmatory else 'Descriptive successful-run subset; incomplete planned cohort, no confirmatory claim.')
        by_stratum = _stratum_method_metrics(runs, method, cutoff, SCALAR)
        for stratum_summary in by_stratum.values():
            stratum_interval = stratum_summary['event_proportion_intervals']['initial_false_healthy_unconditional']
            stratum_summary['false_healthy_event_rate_unconditional'] = stratum_interval['fraction']
            stratum_summary['false_healthy_event_unconditional_denominator'] = stratum_interval['trials']
            stratum_summary['interpretation'] = summary['interpretation']
        metrics[method] = {'summary': summary, 'event_rows': events,
                           'by_stratum': by_stratum}
    corridors = [run for run in runs if not run.control]
    limits_half = _tolerance_summary(runs, (0.10, __import__('math').radians(2.5)))
    limits_double = _tolerance_summary(runs, (0.40, __import__('math').radians(10.0)))
    three_second = common.summarize_three_second_sensitivity(runs)
    three_second_by_stratum = _three_second_by_stratum(runs)
    three_second_rates = _three_second_rate_summary(runs, selected, confirmatory)
    result = {
        'schema': 'pointlio-final-analysis-v1',
        'status': 'CONFIRMATORY_COMPLETE' if confirmatory else 'DESCRIPTIVE_ONLY_INCOMPLETE_PLANNED_COHORT',
        'role': 'heldout', 'planned_geometry_pairs': plan['n_test_geometry_pairs'],
        'completed_geometry_pairs': completed_pairs, 'native_scene_runs_loaded': len(runs),
        'failed_or_unusable_pairs': failures, 'threshold_fit_performed': False,
        'threshold_locked_from_development': threshold, 'method_metrics': metrics,
        'paired_interior_difference': (uncertainty.paired_interval(selected, differences)
            if confirmatory else {'status': 'UNAVAILABLE_CONFIRMATORY_INTERVAL'}),
        'threshold_free_curves': ({method: uncertainty.event_weighted_curve_interval(
            selected, curve_events(corridors, method)) for method in (SCALAR, FIXED)}
            if confirmatory else {'status': 'UNAVAILABLE_CONFIRMATORY_INTERVAL'}),
        'half_tolerance_recovery': limits_half, 'double_tolerance_recovery': limits_double,
        'three_second_rate_sensitivity': three_second,
        'three_second_rate_sensitivity_by_stratum': three_second_by_stratum,
        'three_second_error_rates_by_stratum': three_second_rates,
        'truth_labels': [{'seed': r.seed, 'stratum': r.run_manifest['stratum'], **asdict(r.label)}
                         for r in runs if not r.control],
        'source_pointlio_batch_sha256': sha256(point_root / 'pointlio_final_batch_summary.json'),
        'source_primary_batch_sha256': sha256(primary_root / 'final_batch_summary.json'),
        'source_hashes': {name: sha256(path) for name, path in required.items()}, **gate,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return result


def main() -> None:
    p = __import__('argparse').ArgumentParser(description=__doc__)
    for flag in ('point-root', 'primary-results-root', 'screen', 'plan', 'r3-review',
                 'implementation-freeze', 'output'):
        p.add_argument('--' + flag, type=Path, required=True)
    a = p.parse_args()
    result = analyze(a.point_root, a.primary_results_root, a.screen, a.plan,
                     a.r3_review, a.implementation_freeze, a.output)
    print(json.dumps({'status': result['status'], 'completed_pairs': result['completed_geometry_pairs']}))


if __name__ == '__main__':
    main()
