"""Validate one D050 development slot and the accepted native implementation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import t14_development_runner as development
from record_pointlio_attempt import sha256

ROOT = Path(__file__).resolve().parents[3]
ANCHOR = ROOT / 'research_paper/evidence/pointlio_native_identity_20261009.json'
ANCHOR_SHA256 = '13c9aa68e4c55cd3336839548fc48b9be140863908ab1debdc4e5c5236321583'


def validate_input(bag: Path):
    folder = bag.resolve().parent
    manifest = json.loads((folder / 'manifest.json').read_text())
    seed, control = manifest.get('seed'), manifest.get('control')
    if (manifest.get('role') != 'development' or type(seed) is not int
            or seed not in range(14, 46) or type(control) is not bool
            or bag.name != 'sensors.bag'):
        raise ValueError('Point-LIO development replication accepts only frozen seeds14--45')
    development._validate_input(folder, seed, control)
    historical = json.loads((ROOT / 'research_paper/evidence/t16_development_analysis_manifest.json').read_text())
    scene = 'CONTROL' if control else 'CORRIDOR'
    matches = [r for r in historical['input_audit']['primary_run_provenance']
               if r['seed'] == seed and r['scene'] == scene]
    if len(matches) != 1:
        raise ValueError('development slot has no unique historical input identity')
    expected = matches[0]
    for filename, key in [('sensors.bag', 'sensor_bag_sha256'),
                          ('reference.txt', 'reference_sha256'),
                          ('reference_metadata.json', 'reference_metadata_sha256')]:
        if sha256(folder / filename) != expected[key]:
            raise ValueError(f'frozen development input differs: {filename}')
    return {'seed': seed, 'scene': scene, 'control': control,
            'input_manifest': {'path': str(folder / 'manifest.json'),
                               'sha256': sha256(folder / 'manifest.json')},
            'reference_sha256': expected['reference_sha256'],
            'reference_metadata_sha256': expected['reference_metadata_sha256']}


def validate_native(binary: Path, source: Path, config: Path):
    if sha256(ANCHOR) != ANCHOR_SHA256:
        raise ValueError('accepted Point-LIO native identity changed')
    anchor = json.loads(ANCHOR.read_text())
    if sha256(ROOT / anchor['one_seed_review_path']) != anchor['one_seed_review_sha256']:
        raise ValueError('one-seed independent acceptance record changed')
    if sha256(binary) != anchor['native_binary_sha256'] or sha256(config) != anchor['configuration_sha256']:
        raise ValueError('Point-LIO binary/config differs from accepted one-seed implementation')
    commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    dirty = hashlib.sha256(subprocess.check_output(['git', '-C', str(source), 'diff', 'HEAD', '--binary'])).hexdigest()
    expected = anchor['native_source']
    if commit != expected['commit'] or dirty != expected['dirty_patch_sha256']:
        raise ValueError('Point-LIO native revision/patch differs from accepted implementation')
    for name, digest in expected['files'].items():
        if sha256(source / name) != digest:
            raise ValueError(f'accepted native source changed: {name}')
    for name, digest in anchor['accepted_python_producer_hashes'].items():
        if sha256(ROOT / name) != digest:
            raise ValueError(f'accepted Point-LIO indicator/pose producer changed: {name}')
    return anchor


def glog_identity(prefix):
    anchor = json.loads(ANCHOR.read_text())
    records = sorted((prefix / 'conda-meta').glob('glog-*.json'))
    if len(records) != 1 or sha256(records[0]) != anchor['accepted_glog_metadata']['sha256']:
        raise ValueError('glog overlay package identity differs from accepted implementation')
    libraries = sorted({p.resolve() for pattern in ('libglog.so*', 'libgflags*.so*')
                        for p in (prefix / 'lib').glob(pattern) if p.is_file()})
    if not libraries:
        raise ValueError('glog runtime libraries are unavailable')
    return {'glog_prefix': str(prefix.resolve()),
            'glog_metadata': {'path': str(records[0]), 'sha256': sha256(records[0])},
            'runtime_library_hashes': {str(p): sha256(p) for p in libraries}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bag', type=Path, required=True)
    parser.add_argument('--binary', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    slot = validate_input(args.bag)
    validate_native(args.binary, args.source_root, args.config)
    print(json.dumps({'status': 'PASS', 'study_split': 'development_replication', **slot}))


if __name__ == '__main__':
    main()
