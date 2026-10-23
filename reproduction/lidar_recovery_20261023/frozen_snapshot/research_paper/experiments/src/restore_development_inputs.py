"""Regenerate development inputs and verify against preserved T16 identities.

This never recreates old runtime manifests or estimator results. New generator
manifests retain the current revision/runtime. Only seeds 14--45 are accepted.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
SRC = Path(__file__).resolve().parent


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def save(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(report, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    original = ROOT / 'research_paper/evidence/t16_development_analysis_manifest.json'
    historical = json.loads(original.read_text())
    records = historical['input_audit']['primary_run_provenance']
    expected_schedule = {(seed, scene) for seed in range(14, 46)
                         for scene in ('CORRIDOR', 'CONTROL')}
    if (len(records) != 64 or {(r['seed'], r['scene']) for r in records}
            != expected_schedule):
        raise ValueError('historical provenance is not exactly 32 development pairs')
    report = {
        'schema': 'development-input-restoration-v1',
        'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
        'development_only': True, 'heldout_inputs_opened': False,
        'historical_provenance_sha256': sha256(original),
        'status': 'RUNNING', 'inputs': [],
        'scope': 'Scientific input bytes only; historical run manifests/results are not recreated.',
    }
    save(args.report, report)
    args.output_root.mkdir(parents=True, exist_ok=True)
    for record in sorted(records, key=lambda row: (row['seed'], row['scene'])):
        # Large files must remain on the requested output filesystem.
        if shutil.disk_usage(ROOT).free < 1024**3:
            raise RuntimeError('Linux free space is below the 1 GiB floor')
        if shutil.disk_usage(args.output_root).free < 1024**3:
            raise RuntimeError('Output filesystem free space is below 1 GiB')
        seed, scene = record['seed'], record['scene']
        run_id = f'T14_FORMAL_DEV{seed:02d}_{scene}_INPUT_XM6_V1'
        folder = args.output_root / run_id
        row = {'seed': seed, 'scene': scene, 'path': str(folder.resolve()),
               'status': 'RUNNING', 'original_input_manifest_sha256':
               record['input_manifest_sha256']}
        report['inputs'].append(row)
        save(args.report, report)
        try:
            if not folder.exists():
                command = [sys.executable, str(SRC / 't14_formal_route.py'),
                           'generate', '--run-id', run_id, '--output-root',
                           str(args.output_root), '--seed', str(seed)]
                if scene == 'CONTROL':
                    command.append('--control')
                result = subprocess.run(command, capture_output=True, text=True,
                                        timeout=180)
                row['generation_return_code'] = result.returncode
                if result.returncode:
                    row['generation_error'] = result.stderr[-4000:]
                    raise RuntimeError(f'generator failed for {run_id}')
            expected = {'sensors.bag': record['sensor_bag_sha256'],
                        'reference.txt': record['reference_sha256'],
                        'reference_metadata.json': record['reference_metadata_sha256']}
            row['artifacts'] = {}
            for name, digest in expected.items():
                actual = sha256(folder / name)
                row['artifacts'][name] = {'expected_sha256': digest,
                                          'actual_sha256': actual,
                                          'match': actual == digest}
                if actual != digest:
                    raise ValueError(f'historical input hash differs: {run_id}/{name}')
            manifest = json.loads((folder / 'manifest.json').read_text())
            if (manifest['role'] != 'development' or manifest['seed'] != seed
                    or manifest['layout_seed'] != seed
                    or manifest['control'] is not (scene == 'CONTROL')
                    or manifest['truth_in_sensor_bag'] is not False):
                raise ValueError(f'development identity mismatch: {run_id}')
            row['new_generator_manifest_sha256'] = sha256(folder / 'manifest.json')
            row['historical_runtime_manifest_restored'] = False
            row['status'] = 'MATCH'
            print(f'{seed} {scene}: all three historical input hashes match', flush=True)
        except Exception as exc:
            row['status'] = 'FAILED'
            row['error'] = str(exc)
            report['status'] = 'BLOCKED'
            save(args.report, report)
            raise
        save(args.report, report)
    report['status'] = 'PASS'
    report['status_counts'] = dict(Counter(row['status'] for row in report['inputs']))
    save(args.report, report)
    print('64 development inputs match historical scientific bytes; no estimator result restored.')


if __name__ == '__main__':
    main()
