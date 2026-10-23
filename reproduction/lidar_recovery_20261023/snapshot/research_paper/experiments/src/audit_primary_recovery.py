"""Audit all fresh primary recovery slots and their native/analysis lineage."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import json
from pathlib import Path

import recover_primary_development as recovery
import t14_development_runner as development
from final_evaluation_runner import sha256_file


def audit(root, input_root):
    summary_path = root / 'recovery_schedule.json'
    summary = json.loads(summary_path.read_text())
    if (summary['status'] != 'COMPLETE_NATIVE_COHORT_PENDING_ANALYSIS'
            or summary['heldout_inputs_opened'] is not False
            or summary['threshold_fit_performed'] is not False):
        raise ValueError('primary native recovery is not complete and development-only')
    expected = recovery.schedule()
    if len(summary['runs']) != len(expected):
        raise ValueError('native schedule lost an expected slot')
    provenance = []
    historical = json.loads(recovery.HISTORICAL.read_text())['input_audit']['primary_run_provenance']
    history = {(r['seed'], r['scene']): r for r in historical}
    old_matches = Counter()
    for requested, row in zip(expected, summary['runs']):
        if (row.get('scheduled_run_id', row['run_id']) != requested['run_id']
                or any(row[k] != requested[k] for k in ('seed', 'scene', 'control', 'repeat'))
                or row['status'] not in ('COMPLETED', 'CACHED')):
            raise ValueError('completed schedule differs from the frozen scientific slots')
        actual = root / 'native' / row['run_id']
        native_path = actual / 'run_manifest.json'
        native = json.loads(native_path.read_text())
        adapter_path = root / 'analysis_contract' / requested['run_id'] / 'run_manifest.json'
        adapter = json.loads(adapter_path.read_text())
        if (native['status'] != 'COMPLETED' or native['role'] != 'development'
                or native['scheduled_run_id'] != requested['run_id']
                or native['fingerprint']['execution_identity'] != summary['execution_identity']
                or native['fingerprint']['threshold_from_development_manifest'] is not None
                or adapter['source_lifecycle_manifest_sha256'] != sha256_file(native_path)
                or Path(adapter['source_lifecycle_manifest']).resolve() != native_path.resolve()
                or adapter['outputs'] != native['outputs']
                or any(adapter[k] != requested[k] for k in ('run_id', 'seed', 'scene', 'control', 'repeat'))):
            raise ValueError('analysis adapter is not bound to its completed native scientific slot')
        input_id = f"T14_FORMAL_DEV{requested['seed']:02d}_{requested['scene']}_INPUT_XM6_V1"
        input_dir = input_root / input_id
        recovery.validate_scientific_input(input_dir, requested, history[(requested['seed'], requested['scene'])])
        field_map = {'sensor_bag': 'sensor_bag_sha256', 'input_manifest': 'input_manifest_file_sha256',
                     'reference': 'reference_sha256', 'reference_metadata': 'reference_metadata_sha256'}
        paths = {'sensor_bag': input_dir / 'sensors.bag', 'input_manifest': input_dir / 'manifest.json',
                 'reference': input_dir / 'reference.txt', 'reference_metadata': input_dir / 'reference_metadata.json'}
        for key, native_key in field_map.items():
            digest = sha256_file(paths[key])
            if native['fingerprint'][native_key] != digest or adapter['fingerprint']['input_hashes'][key] != digest:
                raise ValueError('native/adapter scientific inputs changed')
        if (adapter['fingerprint']['backend'] != summary['execution_identity']['backend']
                or adapter['fingerprint']['sources'] != summary['execution_identity']['sources']
                or adapter['fingerprint']['runtime'] != summary['execution_identity']['runtime']):
            raise ValueError('adapter relabelled native execution identities')
        for name, digest in native['outputs'].items():
            target = root / 'analysis_contract' / requested['run_id'] / name
            if (sha256_file(actual / name) != digest or not target.is_symlink()
                    or target.resolve() != (actual / name).resolve() or sha256_file(target) != digest):
                raise ValueError(f'native/analysis output lineage changed: {requested["run_id"]}/{name}')
        if sha256_file(adapter_path) != row['analysis_adapter_sha256']:
            raise ValueError('published analysis adapter changed after recovery checkpoint')
        matches = {}
        if not requested['repeat']:
            for name, digest in history[(requested['seed'], requested['scene'])]['key_output_sha256'].items():
                matches[name] = sha256_file(actual / 'stream' / name) == digest
                old_matches['MATCH' if matches[name] else 'DIFFERENT'] += 1
        provenance.append({**requested, 'actual_native_run_id': row['run_id'],
            'native_manifest_sha256': sha256_file(native_path),
            'analysis_adapter_sha256': sha256_file(adapter_path),
            'completion_validation': native['completion_validation'],
            'historical_output_hash_matches': matches})
    ledger = root / 'native/failure_ledger.csv'
    bridge = root / 'analysis_contract/failure_ledger.csv'
    if not bridge.is_symlink() or bridge.resolve() != ledger.resolve():
        raise ValueError('analysis failure-ledger bridge lost its native source')
    with ledger.open(newline='') as stream:
        transitions = Counter(r['status'] for r in csv.DictReader(stream))
    attempts = []
    for p in sorted((root / 'native').glob('*/run_manifest.json')):
        m = json.loads(p.read_text())
        if (m['scheduled_run_id'] not in {r['run_id'] for r in expected}
                or m['role'] != 'development' or m['attempt'] not in (1, 2)
                or m['fingerprint']['execution_identity'] != summary['execution_identity']):
            raise ValueError('unaccounted native attempt or changed recovery identity')
        attempts.append({'run_id': m['run_id'], 'scheduled_run_id': m['scheduled_run_id'],
                         'status': m['status'], 'attempt': m['attempt'], 'manifest_sha256': sha256_file(p)})
    primary = [r for r in provenance if not r['repeat']]
    return {'schema': 'primary-recovery-complete-audit-v1', 'status': 'PASS_NATIVE_LINEAGE',
        'heldout_data_opened': False, 'role': 'development_only',
        'scheduled_runs': 68, 'completed_primary_runs': len(primary),
        'development_layout_clusters': len({r['seed'] for r in primary}),
        'batch_status_counts': dict(Counter(r['status'] for r in summary['runs'])),
        'completed_repeat_runs': sum(r['repeat'] for r in provenance),
        'unique_native_attempt_count': len(attempts),
        'native_attempt_status_counts': dict(Counter(r['status'] for r in attempts)),
        'failure_ledger_transition_status_counts': dict(transitions),
        'native_attempts': attempts, 'scientific_slots': provenance,
        'historical_four_key_output_hash_comparison_counts': dict(old_matches),
        'recovery_schedule_sha256': sha256_file(summary_path),
        'audit_source_sha256': sha256_file(Path(__file__)),
        'interpretation': 'Fresh recovery provenance; not recreated historical manifests. Hash differences include changed run/event identifiers and require outcome reanalysis.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--recovery-root', type=Path, required=True)
    parser.add_argument('--input-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.recovery_root, args.input_root)
    development._write_json(args.output, result)
    print(json.dumps({k: result[k] for k in ('status', 'completed_primary_runs',
        'completed_repeat_runs', 'unique_native_attempt_count')}))


if __name__ == '__main__':
    main()
