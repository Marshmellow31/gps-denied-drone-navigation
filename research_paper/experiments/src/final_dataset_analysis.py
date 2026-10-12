"""Read a frozen complete held-out primary cohort and apply locked outcomes.

No input is read until the R3 implementation gate passes. This module never
selects a threshold, generates a scene, or replaces a failed pair.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import json
import math
from pathlib import Path
import shutil

import final_evaluation_runner as execution
import r3_evaluation_workflow as workflow
import t16_development_analysis as common
import heldout_statistics as uncertainty


def load_scene(results_root, scene_result, seed, stratum, scene, gate, expected_identity):
    if scene_result.get('status') not in ('COMPLETED', 'CACHED'):
        raise ValueError('completed pair references a scene result without a completed status')
    run_id = scene_result.get('run_id')
    if not isinstance(run_id, str) or not run_id:
        raise ValueError('scene result is missing its native run ID')
    run_dir, native = _read_native_manifest(results_root, scene_result)
    if (native['status'] != 'COMPLETED' or native['role'] != 'heldout'
            or native.get('run_id') != run_id
            or scene_result.get('scheduled_run_id') !=
                f"FINAL_TEST_{stratum.removeprefix('TEST_')}_{seed}_{scene}_P1"
            or native['seed'] != seed or native['stratum'] != stratum or native['scene'] != scene
            or native.get('scheduled_run_id') !=
                f"FINAL_TEST_{stratum.removeprefix('TEST_')}_{seed}_{scene}_P1"):
        raise ValueError('final native result does not match its scientific slot')
    identity = native['fingerprint']['execution_identity']
    if identity != expected_identity:
        raise ValueError('final native execution identity differs from its reviewed batch')
    required_outputs = {'stream/poses.csv','stream/health.csv','stream/health.csv.hessian.csv',
                        'stream/dcreg.csv','stream/evaluation.csv','stream/rosbag.log'}
    if (not required_outputs.issubset(native['outputs'])
            or native['fingerprint']['configuration_sha256'] != execution.sha256_file(execution.CONFIG)
            or native['fingerprint']['backend_binary_sha256'] != execution.EXPECTED_BINARY_SHA256
            or native['fingerprint']['threshold_from_development_manifest'] != execution.LOCKED_DEVELOPMENT_THRESHOLD):
        raise ValueError('final output/configuration/backend/locked-threshold contract changed')
    for name in ('r3_review_sha256', 'implementation_freeze_sha256', 'reviewed_artifact_hashes'):
        if identity.get(name) != gate[name]:
            raise ValueError('final native result differs from the reviewed implementation')
    for relative, digest in native['outputs'].items():
        artifact = (run_dir / relative).resolve()
        if run_dir.resolve() not in artifact.parents or not artifact.is_file() \
                or execution.sha256_file(artifact) != digest:
            raise ValueError('final native output changed')
    input_dir = results_root / 'inputs' / f'{stratum}_{seed}' / scene
    declared = json.loads((input_dir / 'manifest.json').read_text())
    native_input_manifest = native.get('input_manifest')
    declared_identity = execution._input_manifest_identity(declared)
    recorded_raw_manifest_sha = native['fingerprint'].get('input_manifest_file_sha256')
    # Cache/archive resume intentionally allows runtime_s/code_revision to
    # change, so raw manifest bytes may differ while the scientific identity
    # and all sensor/reference hashes remain the same.
    if (not isinstance(native_input_manifest, dict)
            or execution._input_manifest_identity(native_input_manifest) != declared_identity
            or not isinstance(recorded_raw_manifest_sha, str)
            or len(recorded_raw_manifest_sha) != 64
            or any(c not in '0123456789abcdef' for c in recorded_raw_manifest_sha)
            or declared_identity != native['fingerprint']['input_manifest_sha256']
            or declared['role'] != 'heldout' or declared['seed'] != seed
            or declared['stratum'] != stratum or declared['control'] is not (scene == 'CONTROL')):
        raise ValueError('archived input provenance differs from replay identity')
    if declared['sensors.bag']['sha256'] != native['fingerprint']['sensor_bag_sha256']:
        raise ValueError('archived sensor identity differs from replay identity')
    completion = execution.validate_completed_streams(run_dir/'stream',declared,
                                                      *native['postprocess_summaries'])
    if completion != native['completion_validation']:
        raise ValueError('saved final stream/pose-flush validation no longer matches actual outputs')
    shared_reference_path = results_root / 'shared_reference.txt'
    metadata_path = input_dir / 'reference_metadata.json'
    if (execution.sha256_file(shared_reference_path) != native['fingerprint']['reference_sha256']
            or execution.sha256_file(metadata_path) != native['fingerprint']['reference_metadata_sha256']):
        raise ValueError('final reference/metadata changed')
    reference_path = _analysis_reference_alias(results_root, shared_reference_path)
    reference = common.trajectory.load_reference(reference_path)
    body = common.trajectory.load_body_transform(metadata_path, reference_path, False)
    poses = common.trajectory.load_estimates(run_dir / 'stream/poses.csv', 'simulation_epoch')
    exit_s = float(declared['route_profile']['exit_time_s'])
    windows, truth_ok, reason = common.build_primary_windows(poses, reference, body, exit_s)
    label = None if scene == 'CONTROL' else common.find_recovery(
        windows, exit_s, truth_eligible=truth_ok, truth_reason=reason)
    diagnostics = common._read_diagnostics(run_dir, poses)
    decisions = {method: common.associate_decision_ticks(records, poses)
                 for method, records in diagnostics.items()}
    return common.DevelopmentRun(run_dir.name, seed, scene, scene == 'CONTROL', exit_s,
        float(declared['scene_geometry']['corridor_length_m']), run_dir, native, declared,
        poses, reference, body, windows, label, diagnostics, decisions,
        common._read_csv(run_dir / 'stream/evaluation.csv'))


def _read_native_manifest(results_root, scene_result):
    run_id = scene_result.get('run_id')
    if not isinstance(run_id, str) or not run_id:
        raise ValueError('scene result is missing its native run ID')
    runs_root = (results_root / 'runs').resolve()
    run_dir = (runs_root / run_id).resolve()
    if runs_root not in run_dir.parents:
        raise ValueError('native run path escapes the results run directory')
    path = run_dir / 'run_manifest.json'
    return run_dir, json.loads(path.read_text())


def interior_pair(corridor, control):
    length = corridor.corridor_length_m
    if length != control.corridor_length_m:
        raise ValueError('paired scenes have different physical geometry')
    first = 3 + (6 + length/4)/.8
    last = 3 + (6 + 3*length/4)/.8
    starts = [s for s in range(60) if first <= s < last and s+1 <= 60]
    if len(starts) < 5:
        raise ValueError('fewer than five frozen interior windows')
    values = []
    for run in (corridor, control):
        windows = [common.window_at_integer_start(run.poses, run.reference, run.body_transform, s) for s in starts]
        if any(not w.valid for w in windows):
            raise ValueError('incomplete primary interior coverage')
        values.append(float(common.np.median([w.translation_error_m for w in windows])))
    difference = values[0] - values[1]
    if not common.np.isfinite(difference):
        raise ValueError('paired interior difference is non-finite')
    return difference


def _analysis_reference_alias(results_root, shared_reference):
    """Create a hash-checked `reference.txt` name required by frozen metadata."""
    expected = execution.sha256_file(shared_reference)
    alias = results_root / 'analysis_reference' / 'reference.txt'
    alias.parent.mkdir(parents=True, exist_ok=True)
    if alias.exists() or alias.is_symlink():
        if not alias.is_file() or execution.sha256_file(alias) != expected:
            raise ValueError('existing analysis reference alias is changed or invalid')
    else:
        shutil.copy2(shared_reference, alias)
        if execution.sha256_file(alias) != expected:
            raise ValueError('analysis reference copy differs from the verified shared reference')
    return alias


def curve_events(corridors, method):
    events = {}
    for run in corridors:
        if not run.label.truth_eligible:
            events[run.seed] = ([], [])
            continue
        begin, end = common._tick_bounds(run.exit_time_s, run.label.deadline_s)
        rows = [r for r in run.decisions[method][begin:end] if r.available and r.score is not None]
        events[run.seed] = ([float(r.score) for r in rows], [
            run.label.onset_s is not None and r.tick_index/10 >= run.label.onset_s
            and r.tick_index/10 < run.label.recovery_end_s for r in rows])
    return events


def _tolerance_summary(runs, limits):
    corridors = [run for run in runs if not run.control]
    rows = []
    for run in corridors:
        base = run.label
        label = common.find_recovery(
            run.windows, run.exit_time_s, limits=limits,
            truth_eligible=base.truth_eligible, truth_reason=base.reason)
        rows.append({
            'seed': run.seed, 'stratum': run.run_manifest['stratum'],
            'truth_eligible': label.truth_eligible,
            'recovered': label.truth_eligible and label.status == 'RECOVERED',
            'status': label.status, 'onset_s': label.onset_s,
            'confirmation_s': label.confirmation_s, 'relapse_s': label.relapse_s,
        })
    def summarize(items):
        eligible = [row for row in items if row['truth_eligible']]
        recovered = sum(row['recovered'] for row in eligible)
        return {
            'planned_events_loaded': len(items),
            'truth_eligible_events': len(eligible),
            'recovered_events': recovered,
            'non_recovery_events': len(eligible) - recovered,
            'recovery_fraction': recovered / len(eligible) if eligible else None,
            'recovery_wilson_95': common.wilson_interval(recovered, len(eligible)),
        }
    return {
        'pooled': summarize(rows),
        'by_stratum': {name: summarize([row for row in rows if row['stratum'] == name])
                       for name in uncertainty.STRATA},
        'event_rows': rows,
    }


def _stratum_method_metrics(runs, method, threshold, scalar_method):
    result = {}
    for stratum in uncertainty.STRATA:
        grouped = [run for run in runs if run.run_manifest.get('stratum') == stratum]
        summary = common.summarize_method(
            grouped, method, threshold, scalar_method=scalar_method)[0]
        summary['event_proportion_intervals'] = _event_proportion_intervals(
            grouped, method, threshold, scalar_method, summary)
        unconditional = summary['event_proportion_intervals']['initial_false_healthy_unconditional']
        summary['false_healthy_event_rate_unconditional'] = unconditional['fraction']
        summary['false_healthy_event_unconditional_denominator'] = unconditional['trials']
        result[stratum] = summary
    return result


def _event_proportion_intervals(runs, method, threshold, scalar_method, summary):
    counters = {
        'eligible': 0, 'recovered': 0,
        'initial_false_healthy': 0, 'initial_decision_events': 0,
        'initial_interval_events': 0,
        'detected': 0, 'relapsed': 0,
        'post_relapse_false_healthy': 0, 'post_relapse_decision_events': 0,
    }
    for run in runs:
        if run.control:
            continue
        label = run.label
        if label is None or not label.truth_eligible:
            continue
        counters['eligible'] += 1
        states, transitions, _ = common.debounce(
            run.decisions[method], method, threshold, scalar_method=scalar_method)
        available = common.np.asarray([row.available for row in run.decisions[method]], dtype=bool)
        initial = common._initial_mask(run)
        initial_end_s = label.onset_s if label.onset_s is not None else label.deadline_s
        counters['initial_interval_events'] += int(initial_end_s > run.exit_time_s)
        has_initial = bool(common.np.any(available & initial))
        counters['initial_decision_events'] += int(has_initial)
        counters['initial_false_healthy'] += int(bool(common.np.any(states & initial)))
        if label.onset_s is not None:
            counters['recovered'] += 1
            counters['detected'] += int(bool(common.np.any(
                transitions & common._recovery_mask(run))))
        if label.relapse_s is not None:
            counters['relapsed'] += 1
            post = common._post_relapse_mask(run)
            counters['post_relapse_decision_events'] += int(bool(common.np.any(available & post)))
            counters['post_relapse_false_healthy'] += int(bool(common.np.any(states & post)))
    if (counters['eligible'] != summary['truth_label_eligible_corridor_events']
            or counters['recovered'] != summary['truth_recovered_events']
            or counters['initial_false_healthy'] != summary['false_healthy_events']
            or counters['initial_decision_events'] != summary['false_healthy_conditional_denominator']
            or counters['detected'] != summary['detected_recovery_events']
            or counters['relapsed'] != summary['relapse_events']):
        raise ValueError('final event-proportion counters disagree with the shared frozen outcome summary')

    def interval(successes, trials):
        return {
            'successes': successes, 'trials': trials,
            'fraction': successes / trials if trials else None,
            'wilson_95': common.wilson_interval(successes, trials),
        }

    return {
        'truth_recovery': interval(counters['recovered'], counters['eligible']),
        'initial_false_healthy_conditional': interval(
            counters['initial_false_healthy'], counters['initial_decision_events']),
        'initial_false_healthy_unconditional': interval(
            counters['initial_false_healthy'], counters['initial_interval_events']),
        'recovery_detection_given_truth_recovered': interval(
            counters['detected'], counters['recovered']),
        'relapse_given_truth_recovered': interval(
            counters['relapsed'], counters['recovered']),
        'post_relapse_false_healthy_conditional': interval(
            counters['post_relapse_false_healthy'], counters['post_relapse_decision_events']),
        'post_relapse_false_healthy_unconditional': interval(
            counters['post_relapse_false_healthy'], counters['relapsed']),
    }


def _three_second_by_stratum(runs):
    return {
        stratum: common.summarize_three_second_sensitivity(
            [run for run in runs if run.run_manifest.get('stratum') == stratum])
        for stratum in uncertainty.STRATA
    }


def _three_second_rate_summary(runs, selected, allow_confirmatory_interval):
    """Summarize frozen 3 s rate outcomes by event and fixed geometry stratum."""
    run_index = {}
    for run in runs:
        key = (run.run_manifest['stratum'], run.seed, run.scene)
        if key in run_index:
            raise ValueError('duplicate native run in the three-second summary')
        run_index[key] = run
    output = {}
    metrics = (
        'median_translation_rate_mps',
        'median_rotation_rate_radps',
        'median_rotation_rate_degps',
        'passing_window_fraction',
    )
    for scene in ('CORRIDOR', 'CONTROL'):
        rows, per_seed = [], {metric: {} for metric in metrics}
        stratum_summaries = {}
        for stratum in uncertainty.STRATA:
            events = []
            for seed in selected[stratum]:
                run = run_index.get((stratum, seed, scene))
                if run is None:
                    event = {
                        'seed': seed, 'stratum': stratum, 'scene': scene,
                        'status': 'NATIVE_RUN_UNAVAILABLE',
                        'planned_post_exit_3s_windows': None,
                        'valid_post_exit_3s_windows': 0,
                        'unavailable_post_exit_3s_windows': None,
                        'unavailable_reason': 'NATIVE_RUN_NOT_COMPLETED',
                    }
                    events.append(event)
                    rows.append(event)
                    continue
                deadline_ns = common.EPOCH_NS + round((run.exit_time_s + 20.0) * 1e9)
                exit_ns = common.EPOCH_NS + round(run.exit_time_s * 1e9)
                planned = []
                for item in run.evaluation_rows:
                    if item.get('window_s') != '3.0':
                        continue
                    start_ns = int(item['timestamp_ns'])
                    end_ns = int(item['window_end_ns']) if item.get('window_end_ns') else None
                    if start_ns < exit_ns or start_ns + 3_000_000_000 > deadline_ns:
                        continue
                    if end_ns is not None and end_ns > deadline_ns:
                        continue
                    planned.append(item)
                valid = [item for item in planned
                         if item.get('local_valid', '').lower() == 'true'
                         and item.get('window_end_ns')]
                translation, rotation, passing = [], [], []
                for item in valid:
                    tr = float(item['local_translation_error_rate_mps'])
                    rr = float(item['local_rotation_error_rate_radps'])
                    if not math.isfinite(tr) or not math.isfinite(rr):
                        raise ValueError('valid three-second window has a non-finite error rate')
                    translation.append(tr)
                    rotation.append(rr)
                    passing.append(tr <= 0.20 and rr <= math.radians(5.0))
                event = {
                    'seed': seed, 'stratum': stratum, 'scene': scene,
                    'status': 'AVAILABLE' if valid else 'NO_VALID_3S_WINDOW',
                    'planned_post_exit_3s_windows': len(planned),
                    'valid_post_exit_3s_windows': len(valid),
                    'unavailable_post_exit_3s_windows': len(planned) - len(valid),
                    'unavailable_reasons': {
                        reason: sum(item.get('unavailable_reason', '') == reason
                                    for item in planned)
                        for reason in sorted({item.get('unavailable_reason', '') for item in planned
                                              if item.get('local_valid', '').lower() != 'true'})
                    },
                    'median_translation_rate_mps': float(common.np.median(translation)) if valid else None,
                    'median_rotation_rate_radps': float(common.np.median(rotation)) if valid else None,
                    'median_rotation_rate_degps': float(common.np.degrees(common.np.median(rotation))) if valid else None,
                    'passing_window_fraction': float(sum(passing) / len(passing)) if valid else None,
                }
                events.append(event)
                rows.append(event)
                for metric in metrics:
                    if event.get(metric) is not None:
                        per_seed[metric][seed] = event[metric]
            stratum_summaries[stratum] = {
                'selected_geometry_events': len(selected[stratum]),
                'events_with_valid_3s_windows': sum(event['status'] == 'AVAILABLE' for event in events),
                'events_without_native_run': sum(event['status'] == 'NATIVE_RUN_UNAVAILABLE' for event in events),
                'events_without_valid_3s_windows': sum(event['status'] == 'NO_VALID_3S_WINDOW' for event in events),
                **{
                    metric: (float(common.np.mean([event[metric] for event in events
                                                   if event.get(metric) is not None]))
                             if any(event.get(metric) is not None for event in events) else None)
                    for metric in metrics
                },
            }
        overall = {}
        for metric in metrics:
            stratum_means = {name: stratum_summaries[name][metric] for name in uncertainty.STRATA}
            all_strata_available = all(value is not None for value in stratum_means.values())
            planned_event_count = sum(len(v) for v in selected.values())
            complete_event_coverage = len(per_seed[metric]) == planned_event_count
            if complete_event_coverage and allow_confirmatory_interval:
                interval = uncertainty.paired_interval(selected, per_seed[metric])
            else:
                interval = {
                    'status': ('UNAVAILABLE_PRIMARY_CONFIRMATORY_GATE'
                               if not allow_confirmatory_interval
                               else 'UNAVAILABLE_INCOMPLETE_GEOMETRY_EVENTS'),
                    'usable_geometry_events': len(per_seed[metric]),
                    'planned_geometry_events': sum(len(v) for v in selected.values()),
                    'estimate': None, 'interval_95': None,
                }
            overall[metric] = {
                'status': ('AVAILABLE_COMPLETE' if complete_event_coverage
                           else 'DESCRIPTIVE_INCOMPLETE' if all_strata_available
                           else 'UNAVAILABLE_INCOMPLETE_STRATUM'),
                'equal_stratum_mean': (float(common.np.mean(list(stratum_means.values())))
                                       if all_strata_available else None),
                'stratum_means': stratum_means,
                'complete_geometry_event_coverage': complete_event_coverage,
                'geometry_seed_bootstrap': interval,
            }
        output[scene.lower()] = {
            'independent_unit': 'geometry seed within fixed stratum',
            'strata': stratum_summaries,
            'equal_stratum_estimates': overall,
            'event_rows': rows,
        }
    return output


def analyze(results_root, screen_path, plan_path, review_path, freeze_path, output):
    gate = workflow.require_r3_pass(review_path, freeze_path)
    runtime = execution._check_analysis_runtime()
    required_analysis_files = {
        'final dataset analysis caller': Path(__file__).resolve(),
        'T16 analyzer': Path(common.__file__).resolve(),
        'held-out statistics': Path(uncertainty.__file__).resolve(),
        'R3 evaluation workflow': Path(workflow.__file__).resolve(),
    }
    if any(gate['reviewed_artifact_hashes'].get(name) != execution.sha256_file(path)
           for name, path in required_analysis_files.items()):
        raise ValueError('final analysis/statistics/shared outcome code is not bound in the R3 inventory')
    # The gate above precedes all reads of held-out result/input/screen content.
    batch = json.loads((results_root / 'final_batch_summary.json').read_text())
    screen = json.loads(screen_path.read_text())
    plan = json.loads(plan_path.read_text())
    if plan != workflow.build_plan(workflow.FAST_ANALYSIS,execution.ROOT/'research_paper/data/SPLITS.csv'):
        raise ValueError('final plan differs from the frozen development-derived design')
    if (screen['status'] != 'SCENE_SCREEN_PASS' or screen['role'] != 'heldout'
            or screen['plan_sha256'] != execution.sha256_file(plan_path)
            or screen['development_analysis_sha256'] != plan['development_analysis_sha256']
            or any(screen[k] != gate[k] for k in ('r3_review_sha256','implementation_freeze_sha256','reviewed_artifact_hashes'))
            or batch['development_analysis_sha256'] != plan['development_analysis_sha256']
            or batch['target_geometry_pairs'] != plan['n_test_geometry_pairs']
            or batch['backend']['binary_sha256'] != execution.EXPECTED_BINARY_SHA256
            or batch['runner_sha256'] != execution.sha256_file(Path(execution.__file__))
            or batch['heldout_generator_sha256'] != execution.sha256_file(Path(execution.heldout.__file__))):
        raise ValueError('final plan/screen/batch/source identity changed')
    if (batch['role'] != 'heldout' or batch['scene_screen_sha256'] != execution.sha256_file(screen_path)
            or batch['heldout_inputs_or_results_used_for_tuning'] is not False
            or batch['threshold_locked_from_development'] != execution.LOCKED_DEVELOPMENT_THRESHOLD):
        raise ValueError('final batch/screen/locked operating-point contract changed')
    for name in ('r3_review_sha256', 'implementation_freeze_sha256'):
        if batch[name] != gate[name]: raise ValueError('final batch belongs to a different implementation freeze')
    selected = screen['selected_seeds_by_stratum']
    for name in uncertainty.STRATA:
        seeds = selected.get(name, [])
        bounds = execution.heldout.STRATA[name]
        rows = [r for r in screen['screened_layouts'] if r['stratum']==name]
        if (len(seeds) != plan['geometry_pairs_per_stratum'] or seeds != sorted(set(seeds))
                or any(not bounds['seed_min'] <= seed <= bounds['seed_max'] for seed in seeds)
                or [r['seed'] for r in rows] != list(range(bounds['seed_min'],seeds[-1]+1))
                or [r['seed'] for r in rows if r['eligible']][:len(seeds)] != seeds):
            raise ValueError('final screen does not preserve the balanced lowest-eligible reserved prefix')
    expected_identity = {**gate,'runtime':runtime,'backend':batch['backend'],
                         'plan_sha256':execution.sha256_file(plan_path),
                         'screen_sha256':execution.sha256_file(screen_path),
                         'analysis_sha256':plan['development_analysis_sha256']}
    expected = {(stratum, seed) for stratum, seeds in selected.items() for seed in seeds}
    if len(expected) != batch['target_geometry_pairs'] or set(selected) != set(uncertainty.STRATA):
        raise ValueError('final event inventory differs from the frozen screen')
    pair_results = batch.get('pair_results')
    if not isinstance(pair_results, list):
        raise ValueError('final batch lacks its complete planned pair ledger')
    pairs = {(r['stratum'], r['seed']): r for r in pair_results}
    if set(pairs) != expected or len(pairs) != len(pair_results):
        raise ValueError('final batch omitted or duplicated a planned geometry')
    if any(not isinstance(pair, dict)
           or pair.get('status') not in ('COMPLETED', 'FAILED_KEEP_INPUTS')
           or not isinstance(pair.get('scene_runs'), list) for pair in pair_results):
        raise ValueError('final batch contains an unknown or unresolved pair status')
    completed_pair_count = sum(pair.get('status') == 'COMPLETED' for pair in pair_results)
    scene_result_count = sum(len(pair['scene_runs']) for pair in pair_results)
    expected_batch_status = ('COMPLETED' if completed_pair_count == batch['target_geometry_pairs']
                             else 'INCOMPLETE_KEEP_FAILURES')
    if (batch.get('status') != expected_batch_status
            or batch.get('completed_geometry_pairs') != completed_pair_count
            or batch.get('scheduled_scene_runs') != 2 * batch['target_geometry_pairs']
            or batch.get('scene_runs') != scene_result_count):
        raise ValueError('final batch status and run counts do not reconcile with its pair ledger')
    runs, differences, incomplete = [], {}, []
    for stratum in uncertainty.STRATA:
        for seed in selected[stratum]:
            pair = pairs[(stratum, seed)]
            scene_rows = pair.get('scene_runs')
            if pair['status'] != 'COMPLETED' or not isinstance(scene_rows, list) or len(scene_rows) != 2:
                incomplete.append({'stratum': stratum, 'seed': seed, 'reason': 'INCOMPLETE_NATIVE_PAIR'})
                continue
            loaded = {}
            for result in scene_rows:
                _, m = _read_native_manifest(results_root, result)
                scene = m['scene']
                if scene not in ('CORRIDOR', 'CONTROL') or scene in loaded:
                    raise ValueError('final pair lost a unique corridor/control scene')
                loaded[scene] = load_scene(results_root, result, seed, stratum, scene, gate,expected_identity)
            runs.extend(loaded.values())
            try:
                if not loaded['CORRIDOR'].label.truth_eligible:
                    raise ValueError('corridor truth-label eligibility incomplete')
                difference = interior_pair(loaded['CORRIDOR'], loaded['CONTROL'])
                if not math.isfinite(difference):
                    raise ValueError('paired interior difference is non-finite')
                differences[seed] = difference
            except ValueError as exc:
                incomplete.append({'stratum': stratum, 'seed': seed, 'reason': str(exc)})
    corridors = [r for r in runs if not r.control]
    confirmatory = (not incomplete
        and batch['status'] == 'COMPLETED'
        and completed_pair_count == batch['target_geometry_pairs']
        and len(runs) == 2 * batch['target_geometry_pairs']
        and len(differences) == batch['target_geometry_pairs'])
    paired_difference = None
    if confirmatory:
        paired_difference = uncertainty.paired_interval(selected, differences)
        if paired_difference.get('status') != 'AVAILABLE':
            confirmatory = False
            incomplete.append({'reason': 'PAIRED_INTERVAL_INPUT_UNAVAILABLE'})
    metrics, events = {}, {}
    stratum_metrics = {}
    for method, threshold in [('FASTLIO_MIN_EIG_G3',execution.LOCKED_DEVELOPMENT_THRESHOLD), ('DCREG_SCHUR_MASK',None)]:
        metrics[method], events[method] = common.summarize_method(runs,method,threshold)
        intervals = _event_proportion_intervals(
            runs, method, threshold, 'FASTLIO_MIN_EIG_G3', metrics[method])
        metrics[method]['event_proportion_intervals'] = intervals
        metrics[method]['false_healthy_event_rate_unconditional'] = (
            intervals['initial_false_healthy_unconditional']['fraction'])
        metrics[method]['false_healthy_event_unconditional_denominator'] = (
            intervals['initial_false_healthy_unconditional']['trials'])
        metrics[method]['interpretation'] = ('Locked complete held-out evaluation; no test-data threshold selection.'
            if confirmatory else 'Descriptive successful-run subset of an incomplete planned cohort; no confirmatory interval/claim.')
        stratum_metrics[method] = _stratum_method_metrics(
            runs, method, threshold, 'FASTLIO_MIN_EIG_G3')
        for stratum_result in stratum_metrics[method].values():
            stratum_result['interpretation'] = metrics[method]['interpretation']
    half = _tolerance_summary(runs, (0.10, math.radians(2.5)))
    double = _tolerance_summary(runs, (0.40, math.radians(10.0)))
    three_second = common.summarize_three_second_sensitivity(runs)
    three_second_by_stratum = _three_second_by_stratum(runs)
    three_second_rates = _three_second_rate_summary(runs, selected, confirmatory)
    pair_completion_by_stratum = {
        stratum: {
            'planned_pairs': len(selected[stratum]),
            'completed_pairs': sum(pairs[(stratum, seed)]['status'] == 'COMPLETED'
                                   for seed in selected[stratum]),
            'failed_or_incomplete_pairs': sum(pairs[(stratum, seed)]['status'] != 'COMPLETED'
                                              for seed in selected[stratum]),
        }
        for stratum in uncertainty.STRATA
    }
    result = {'schema':'final-primary-analysis-v1','status':'CONFIRMATORY_COMPLETE' if confirmatory else 'DESCRIPTIVE_ONLY_INCOMPLETE_PLANNED_COHORT',
        'role':'heldout','planned_geometry_pairs':batch['target_geometry_pairs'],
        'completed_geometry_pairs':completed_pair_count,
        'pair_completion_by_stratum':pair_completion_by_stratum,
        'usable_interior_pairs':len(differences),'native_scene_runs_loaded':len(runs),'failed_or_unusable_pairs':incomplete,
        'planned_pair_results':batch['pair_results'],
        'method_metrics':metrics,'method_metrics_by_stratum':stratum_metrics,
        'event_metrics':events,'threshold_selected_on_test':False,
        'half_tolerance_recovery':half,'double_tolerance_recovery':double,
        'three_second_rate_sensitivity':three_second,
        'three_second_rate_sensitivity_by_stratum':three_second_by_stratum,
        'three_second_error_rates_by_stratum':three_second_rates,
        'truth_labels':[{'seed':r.seed,'stratum':r.run_manifest['stratum'],**asdict(r.label)} for r in corridors],
        'source_batch_sha256':execution.sha256_file(results_root/'final_batch_summary.json'),
        'source_screen_sha256':execution.sha256_file(screen_path),
        'analysis_reference_sha256':execution.sha256_file(results_root/'analysis_reference'/'reference.txt')
            if (results_root/'analysis_reference'/'reference.txt').is_file() else None,
        **gate,
        'source_hashes':{name:execution.sha256_file(path)
                         for name, path in required_analysis_files.items()}}
    if confirmatory:
        result['paired_interior_difference'] = paired_difference
        result['threshold_free_curves'] = {method:uncertainty.event_weighted_curve_interval(selected,curve_events(corridors,method)) for method in metrics}
    else:
        result['paired_interior_difference'] = {'status':'UNAVAILABLE_CONFIRMATORY_INTERVAL'}
        result['threshold_free_curves'] = {'status':'UNAVAILABLE_CONFIRMATORY_INTERVAL'}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results-root',type=Path,required=True);parser.add_argument('--screen',type=Path,required=True)
    parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--r3-review',type=Path,required=True);parser.add_argument('--freeze',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=analyze(args.results_root,args.screen,args.plan,args.r3_review,args.freeze,args.output)
    print(json.dumps({'status':result['status'],'planned_pairs':result['planned_geometry_pairs']}))


if __name__=='__main__':main()
