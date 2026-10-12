"""Validate the separately identified v2 development fixture, never final IDs."""
import argparse
import json
from pathlib import Path

import heldout_simulation_v2 as geometry
from validate_pointlio_development_input import validate_native, glog_identity
from record_pointlio_attempt import sha256

ROOT = geometry.ROOT


def require_r2():
    review = ROOT / 'research_paper/reviews/R2_GEOMETRY_AMENDMENT_20261012.md'
    proposal = ROOT / 'research_paper/protocol/GEOMETRY_REVISION_PROPOSAL_20261012.json'
    text = review.read_text()
    if not text.startswith('**Gate:** PASS') or sha256(proposal) not in text:
        raise ValueError('v2 development native validation requires the accepted R2 proposal identity')


def validate_input(bag: Path):
    require_r2()
    folder = bag.resolve().parent
    m = json.loads((folder / 'manifest.json').read_text())
    if (bag.name != 'sensors.bag' or m.get('role') != 'development'
            or m.get('seed') != 14 or type(m.get('control')) is not bool
            or m.get('stratum') not in ('DEVELOPMENT_FIXED_LONG_NARROW', 'DEVELOPMENT_FIXED_LONG_WIDE')
            or m.get('geometry_profile') != geometry.GEOMETRY_PROFILE
            or m.get('truth_in_sensor_bag') is not False
            or m.get('scans') != 600 or m.get('imu_messages') != 12021):
        raise ValueError('input is not the prespecified v2 development fixture')
    expected = geometry.sample_development_fixture(14, m['stratum'], m['control'])[1]
    if m.get('scene_geometry') != expected:
        raise ValueError('development fixture dimensions/profile changed')
    for field, module in [('generator_sha256', geometry),
                          ('simulator_sha256', geometry.simulator),
                          ('formal_route_sha256', geometry.formal_route)]:
        if m.get(field) != sha256(Path(module.__file__)):
            raise ValueError('development generator source identity changed')
    for name in ('sensors.bag', 'reference.txt', 'reference_metadata.json'):
        if sha256(folder / name) != m.get(name, {}).get('sha256'):
            raise ValueError(f'development input hash mismatch: {name}')
    metadata = json.loads((folder/'reference_metadata.json').read_text())
    if (metadata.get('evaluation_scope') != 'development'
            or metadata.get('estimator_input_independence') is not True):
        raise ValueError('development truth isolation changed')
    return {'role': 'development', 'seed': 14,
            'scene': 'CONTROL' if m['control'] else 'CORRIDOR', 'control': m['control'],
            'geometry_profile': geometry.GEOMETRY_PROFILE,
            'input_manifest': {'path': str(folder/'manifest.json'),
                               'sha256': sha256(folder/'manifest.json')},
            'reference_sha256': m['reference.txt']['sha256'],
            'reference_metadata_sha256': m['reference_metadata.json']['sha256']}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--bag', type=Path, required=True)
    p.add_argument('--binary', type=Path, required=True)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    a = p.parse_args()
    validate_native(a.binary, a.source_root, a.config)
    print(json.dumps(validate_input(a.bag)))
