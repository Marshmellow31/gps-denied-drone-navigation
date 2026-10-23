"""Exploratory failure diagnosis of exposed final recordings; never tune policy.

Read only accepted native manifests/pose/diagnostic/reference streams. Reuse
the frozen time association, labels and debounce; reconcile every corridor
event against the accepted exports before publishing derived observations.
"""
import argparse
import csv
from dataclasses import asdict
import gzip
import json
import math
from pathlib import Path

import numpy as np
import t16_development_analysis as common
import r3_evaluation_workflow as workflow
import final_dataset_analysis_geometry_v2_compat as compat

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'research_paper/evidence/final_geometry_v2_results_20261012'
METHODS = {'fastlio': ('FASTLIO_MIN_EIG_G3', 'DCREG_SCHUR_MASK'),
           'pointlio': ('POINTLIO_MIN_EIG_G3', 'POINTLIO_DCREG_SCHUR_MASK')}
CUTOFFS = {'fastlio': 166.16366016039856, 'pointlio': 123.80876977779258}


def checked(path, expected, sources):
    digest = common.sha256_file(path)
    if digest != expected:
        raise ValueError(f'Changed input: {path}')
    sources[str(path)] = digest
    return path


def write_csv(path, rows):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'wt', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def median(values):
    return float(np.median(values)) if values else None


def miss_pattern(recovered_event, detected, states, recovery_mask, raw_healthy, available):
    """Partition misses by observable decision behavior, not inferred cause."""
    if not recovered_event or detected:
        return 'NOT_A_MISSED_RECOVERY'
    relevant = recovery_mask & available
    if not np.any(relevant):
        return 'NO_AVAILABLE_TICK_IN_RECOVERY_INTERVAL'
    if np.any(states & recovery_mask):
        return 'ACTIVE_STATE_WITHOUT_NEW_POST_ONSET_TRANSITION'
    if not np.any(raw_healthy & relevant):
        return 'NO_RAW_HEALTHY_TICK_IN_RECOVERY_INTERVAL'
    return 'RAW_HEALTHY_TICKS_WITHOUT_THREE_RECORD_CONFIRMATION'


def load(receipt, base, sources, reference):
    run_dir = Path(receipt['manifest_path']).parent
    native_path = checked(run_dir/'run_manifest.json', receipt['manifest_sha256'], sources)
    native = json.loads(native_path.read_text())
    b = receipt['backend']
    inp = native['input_manifest']
    input_dir = base/b/'inputs'/f"{receipt['stratum']}_{receipt['seed']}"/receipt['scene']
    metadata = checked(input_dir/'reference_metadata.json',
                       inp['reference_metadata.json']['sha256'], sources)
    reference_path = base/'fastlio/analysis_reference/reference.txt'
    checked(reference_path, inp['reference.txt']['sha256'], sources)
    body = common.trajectory.load_body_transform(metadata, reference_path, False)
    pose_rel = 'stream/poses.csv' if b == 'fastlio' else 'poses_segmented.csv'
    pose_path = checked(run_dir/pose_rel, receipt['outputs'][pose_rel], sources)
    poses = common.trajectory.load_estimates(pose_path, 'simulation_epoch')
    exit_s = float(inp['route_profile']['exit_time_s'])
    windows, truth_ok, reason = common.build_primary_windows(poses, reference, body, exit_s)
    label = None if receipt['control'] else common.find_recovery(
        windows, exit_s, truth_eligible=truth_ok, truth_reason=reason)
    scalar, fixed = METHODS[b]
    if b == 'fastlio':
        for name in ('stream/health.csv', 'stream/dcreg.csv'):
            checked(run_dir/name, receipt['outputs'][name], sources)
        diagnostics = common._read_diagnostics(run_dir, poses)
        frames = [r for r in common._read_csv(run_dir/'stream/health.csv')
                  if float(r['lever_scale_m']) == 3]
        fixed_rows = common._read_csv(run_dir/'stream/dcreg.csv')
    else:
        path = checked(run_dir/'pointlio_indicators.csv',
                       receipt['outputs']['pointlio_indicators.csv'], sources)
        frames = common._read_csv(path)
        fixed_rows = frames
        diagnostics = {scalar: [], fixed: []}
        for row in frames:
            valid = row['valid'].lower() == 'true'
            stamp, segment = int(row['timestamp_ns']), int(row['segment_id'])
            diagnostics[scalar].append(common.DiagnosticRecord(stamp, valid,
                float(row['lambda_min_3m']) if valid else None, None, segment, row['unavailable_reason']))
            diagnostics[fixed].append(common.DiagnosticRecord(stamp, valid,
                float(row['DCREG_HEALTH_SCORE']) if valid else None,
                row['DCREG_state'] == 'HEALTHY' if valid else None, segment, row['unavailable_reason']))
    decisions = {m: common.associate_decision_ticks(d, poses) for m, d in diagnostics.items()}
    run = common.DevelopmentRun(receipt['run_id'], receipt['seed'], receipt['scene'],
        receipt['control'], exit_s, float(inp['scene_geometry']['corridor_length_m']),
        run_dir, native, inp, poses, reference, body, windows, label,
        diagnostics, decisions, [])
    return run, frames, fixed_rows


def analyze(base, output):
    review = ROOT/'research_paper/reviews/R3_GEOMETRY_V2_IMPLEMENTATION_20261012.md'
    freeze = ROOT/'research_paper/protocol/IMPLEMENTATION_FREEZE_GEOMETRY_V2_20261012.md'
    gate = workflow.require_r3_pass(review, freeze)
    compat.require_compatibility_review(
        ROOT/'research_paper/reviews/R3_GEOMETRY_V2_ANALYSIS_COMPATIBILITY_20261012.md', review, freeze)
    sources = {}
    accepted = {}
    # The independently audited exports bind numerical outcomes; refresh their
    # hashes from the result audit, not a new outcome-selected expectation.
    import re
    audit_text = (ROOT/'research_paper/reviews/FINAL_GEOMETRY_V2_RESULT_AUDIT_20261012.md').read_text()
    inventory = json.loads(re.search(r'```json\s*(.*?)```', audit_text, re.S)[1])['artifacts']
    for b in METHODS:
        path = checked(EVIDENCE/f'{b}_analysis.json', inventory[f'{b}_analysis.json'], sources)
        accepted[b] = json.loads(path.read_text())
        if accepted[b]['status'] != 'CONFIRMATORY_COMPLETE':
            raise ValueError('Incomplete accepted analysis')
    path = checked(EVIDENCE/'native_attempt_receipts.json', inventory['native_attempt_receipts.json'], sources)
    receipts = json.loads(path.read_text())
    if len(receipts) != 192 or len({r['manifest_path'] for r in receipts}) != 192:
        raise ValueError('Expected 192 unique native slots')
    reference_path = base/'fastlio/analysis_reference/reference.txt'
    reference = common.trajectory.load_reference(reference_path)
    runs = {}
    frames_by_run = {}
    for i, receipt in enumerate(receipts):
        run, frames, fixed_rows = load(receipt, base, sources, reference)
        runs[(receipt['backend'], run.seed, run.scene)] = run
        frames_by_run[(receipt['backend'], run.seed, run.scene)] = (frames, fixed_rows)
        if i % 24 == 23:
            print(f'Loaded/hash-checked {i+1}/192 native slots', flush=True)
    expected_labels = {b: {r['seed']: {k:v for k,v in r.items() if k not in ('seed','stratum')}
                          for r in d['truth_labels']} for b, d in accepted.items()}
    events, windows_out, ticks_out, observations, frame_out = [], [], [], [], []
    for (b, _, scene), run in runs.items():
        frames, fixed_rows = frames_by_run[(b, run.seed, scene)]
        for row, fixed_row in zip(frames, fixed_rows):
            valid = row['valid'].lower() == 'true'
            frame_out.append({'backend': b, 'seed': run.seed, 'scene': scene,
                'time_s': (int(row['timestamp_ns'])-common.EPOCH_NS)/1e9,
                'valid': valid, 'accepted_count': int(row['accepted_count']),
                'scalar_score': float(row['eigenvalue_0' if b == 'fastlio' else 'lambda_min_3m']) if valid else None,
                'fixed_score': float(fixed_row['DCREG_HEALTH_SCORE']) if valid else None,
                'fixed_flagged_directions': sum(fixed_row[f'kappa_{part}_{j}_flagged'].lower()=='true'
                                               for part in ('R','t') for j in range(3)) if valid else None})
    for b, methods in METHODS.items():
        corridors = [r for (backend, _, scene), r in runs.items() if backend == b and scene == 'CORRIDOR']
        for run in corridors:
            actual = asdict(run.label)
            actual['triple_window_starts_s'] = list(actual['triple_window_starts_s'])
            if actual != expected_labels[b][run.seed]:
                raise ValueError(f'Recovery label mismatch {b} {run.seed}')
            for window in run.windows:
                windows_out.append({'backend': b, 'seed': run.seed, 'stratum': run.input_manifest['stratum'],
                    **asdict(window), 'passes_frozen_limits': window.passes(common.PRIMARY_LIMITS)})
        for m in methods:
            _, rows = common.summarize_method(corridors, m, CUTOFFS[b], methods[0], b)
            saved = accepted[b]['event_metrics'][m] if b == 'fastlio' else accepted[b]['method_metrics'][m]['event_rows']
            if {r['seed']:r for r in rows} != {r['seed']:r for r in saved}:
                raise ValueError(f'Event metric mismatch {b} {m}')
            for event in rows:
                run = runs[(b, event['seed'], 'CORRIDOR')]
                control = runs[(b, event['seed'], 'CONTROL')]
                states, transitions, alarms = common.debounce(run.decisions[m], m, CUTOFFS[b], methods[0])
                initial = common._initial_mask(run)
                recovered = common._recovery_mask(run)
                available = np.array([d.available for d in run.decisions[m]])
                raw = np.array([d.available and (d.score >= CUTOFFS[b] if m == methods[0]
                               else d.fixed_healthy is True) for d in run.decisions[m]])
                relevant = recovered & available
                fraction = lambda mask: float(np.count_nonzero(raw & mask)/np.count_nonzero(mask)) if np.any(mask) else None
                missed = event['truth_status']=='RECOVERED' and not event['detected_post_onset']
                mechanism = miss_pattern(event['truth_status']=='RECOVERED',
                    event['detected_post_onset'], states, recovered, raw, available)
                initial_indices = np.flatnonzero(initial)
                initial_active_at_start = bool(len(initial_indices) and states[initial_indices[0]])
                post_frames = [r for r in frame_out if r['backend']==b and r['seed']==run.seed and r['scene']=='CORRIDOR'
                               and run.exit_time_s <= r['time_s'] < run.exit_time_s+20 and r['valid']]
                control_records = [d for d in control.diagnostics[methods[0]] if d.valid and
                                   run.exit_time_s <= (d.timestamp_ns-common.EPOCH_NS)/1e9 < run.exit_time_s+20]
                control_frames = frames_by_run[(b, run.seed, 'CONTROL')][0]
                control_counts = [int(r['accepted_count']) for r in control_frames if r['valid'].lower()=='true'
                                  and run.exit_time_s <= (int(r['timestamp_ns'])-common.EPOCH_NS)/1e9 < run.exit_time_s+20]
                observation = {'backend': b, 'method': m, 'seed': run.seed,
                    'stratum': run.input_manifest['stratum'], 'truth_status': event['truth_status'],
                    'false_healthy': event['false_healthy_in_initial_unrecovered_interval'],
                    'missed_recovery': missed, 'miss_pattern': mechanism,
                    'initial_state_active_at_first_tick': initial_active_at_start,
                    'new_initial_transitions': int(np.count_nonzero(transitions & initial)),
                    'raw_healthy_fraction_during_recovery': fraction(relevant),
                    'post_exit_accepted_count_median': median([r['accepted_count'] for r in post_frames]),
                    'control_post_exit_accepted_count_median': median(control_counts),
                    'post_exit_fixed_flagged_fraction': float(np.mean([r['fixed_flagged_directions']>0 for r in post_frames])) if post_frames else None,
                    'post_exit_scalar_score_median': median([r['scalar_score'] for r in post_frames]),
                    'control_post_exit_scalar_score_median': median([r.score for r in control_records]),
                    'corridor_half_width_m': run.input_manifest['scene_geometry']['corridor_half_width_m'],
                    'corridor_length_m': run.corridor_length_m}
                observations.append(observation)
                events.append({'backend': b, 'method': m, 'stratum': observation['stratum'], **event})
                for i,d in enumerate(run.decisions[m]):
                    ticks_out.append({'backend': b, 'method': m, 'seed': run.seed,
                        'time_s': (d.timestamp_ns-common.EPOCH_NS)/1e9, 'available': d.available,
                        'score': d.score, 'source_timestamp_ns': d.source_timestamp_ns,
                        'confirmed_healthy': bool(states[i]), 'new_alarm': bool(transitions[i]),
                        'initial_interval': bool(initial[i]), 'recovered_interval': bool(recovered[i])})
    output.mkdir(parents=True, exist_ok=False)
    write_csv(output/'event_diagnosis.csv', observations)
    write_csv(output/'primary_windows.csv', windows_out)
    write_csv(output/'decision_ticks.csv.gz', ticks_out)
    write_csv(output/'diagnostic_frames.csv.gz', frame_out)
    (output/'reconciled_events.json').write_text(json.dumps(events, indent=2)+'\n')
    selection = []
    for b, methods in METHODS.items():
        for m in methods:
            cohort = sorted([o for o in observations if o['backend']==b and o['method']==m], key=lambda o:o['seed'])
            for kind, predicate in [('false_healthy',lambda o:o['false_healthy']),
                                    ('missed_recovery',lambda o:o['missed_recovery']),
                                    ('successful_detection',lambda o:o['truth_status']=='RECOVERED' and not o['missed_recovery'] and not o['false_healthy']),
                                    ('non_recovery',lambda o:o['truth_status']!='RECOVERED')]+[(pattern,lambda o,p=pattern:o['missed_recovery'] and o['miss_pattern']==p) for pattern in sorted({o['miss_pattern'] for o in cohort if o['missed_recovery']})]:
                candidates = [o for o in cohort if predicate(o)]
                if candidates:
                    first = candidates[0]
                    selection.append({'backend':b,'method':m,'category':kind,'seed':first['seed']})
    (output/'case_selection.json').write_text(json.dumps({'rule':'Lowest selected seed per backend/method/category; illustrative post-result selection, never used to estimate prevalence','cases':selection},indent=2)+'\n')
    summary = {'scope':'Exploratory exposed-data diagnosis; no tuning or new confirmatory test',
        'native_slots_read':len(receipts),'corridor_labels_reconciled':96,'diagnostic_event_rows_reconciled':len(events),
        'frozen_inventory_entries':len(gate['reviewed_artifact_hashes']),
        'miss_patterns':{m:{kind:sum(o['method']==m and o['miss_pattern']==kind for o in observations)
                            for kind in sorted({o['miss_pattern'] for o in observations if o['missed_recovery']})}
                         for methods in METHODS.values() for m in methods},
        'source_sha256':sources,'script_sha256':common.sha256_file(Path(__file__)),
        'output_sha256':{p.name:common.sha256_file(p) for p in output.iterdir() if p.is_file()},
        'verification_scope':'Consumed native manifests, poses, diagnostics, reference/metadata rehashed; raw bags/Jacobian rows and offline evaluation CSV not reread. All labels and event rows reproduced with frozen routines.'}
    (output/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k not in ('source_sha256','output_sha256')},indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    analyze(a.root, a.output)
