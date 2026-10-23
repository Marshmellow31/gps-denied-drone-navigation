"""Validate one R3-authorized Point-LIO final replay input before native use."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import final_evaluation_runner as primary
import r3_evaluation_workflow as workflow
from record_pointlio_attempt import sha256


def validate(input_dir: Path, seed: int, stratum: str, scene: str,
             execution_identity_path: Path) -> dict:
    identity = json.loads(execution_identity_path.read_text())
    gate = workflow.require_r3_pass(
        Path(identity['r3_review_path']), Path(identity['implementation_freeze_path']))
    _, point, point_freeze_sha, point_review_sha = workflow._validate_point_freeze()
    if (any(identity.get(key) != gate.get(key) for key in
            ('r3_review_sha256', 'implementation_freeze_sha256', 'reviewed_artifact_hashes'))
            or identity.get('pointlio_freeze_sha256') != point_freeze_sha
            or identity.get('pointlio_freeze_review_sha256') != point_review_sha
            or identity.get('pointlio_threshold') != point['pointlio_threshold_selection']['threshold']):
        raise ValueError('Point-LIO final input validator received a stale or unauthorized R3 identity')
    # R3 and both implementation freezes are verified before reading the input tree.
    input_dir = input_dir.resolve()
    control = scene == 'CONTROL'
    manifest = primary._verify_retained_input(input_dir, seed, stratum, control)
    if scene not in ('CORRIDOR', 'CONTROL'):
        raise ValueError('unknown Point-LIO final scene')
    if (manifest.get('role') != 'heldout' or manifest.get('seed') != seed
            or manifest.get('stratum') != stratum
            or (manifest.get('scene') is not None and manifest.get('scene') != scene)
            or manifest.get('control') is not control
            or manifest.get('truth_in_sensor_bag') is not False):
        raise ValueError('Point-LIO final input differs from its authorized held-out slot')
    metadata = json.loads((input_dir / 'reference_metadata.json').read_text())
    if (metadata.get('evaluation_scope') != 'heldout'
            or metadata.get('estimator_input_independence') is not True):
        raise ValueError('reference scope/truth isolation contract changed')
    return {
        'role': 'heldout', 'seed': seed, 'stratum': stratum,
        'scene': scene, 'control': control,
        'input_manifest': manifest,
        'input_manifest_identity_sha256': primary._input_manifest_identity(manifest),
        'sensor_bag_sha256': sha256(input_dir / 'sensors.bag'),
        'reference_sha256': sha256(input_dir / 'reference.txt'),
        'reference_metadata_sha256': sha256(input_dir / 'reference_metadata.json'),
        'truth_in_sensor_bag': False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-dir', required=True, type=Path)
    parser.add_argument('--seed', required=True, type=int)
    parser.add_argument('--stratum', required=True)
    parser.add_argument('--scene', required=True, choices=('CORRIDOR', 'CONTROL'))
    parser.add_argument('--execution-identity-json', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.input_dir, args.seed, args.stratum, args.scene,
                              args.execution_identity_json), sort_keys=True))


if __name__ == '__main__':
    main()
