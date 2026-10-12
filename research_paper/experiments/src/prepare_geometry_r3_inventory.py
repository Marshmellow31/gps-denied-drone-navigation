"""Prepare a geometry-v2 R3 review inventory without sampling any final ID."""
import argparse
from pathlib import Path

import r3_evaluation_workflow as workflow


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    hashes = workflow._required_hashes(a.review)
    workflow.execution._write_json(a.output, {
        'schema': 'r3-review-input-inventory-v1',
        'status': 'PREPARED_FOR_INDEPENDENT_REVIEW',
        'original_geometry_screen_exposed': True,
        'fresh_v2_geometry_screened': False, 'fresh_v2_sensor_bags_generated': False,
        'fresh_v2_lio_replayed': False, 'artifact_count': len(hashes), 'artifacts': hashes})
    print('Prepared', len(hashes), 'hashes; no fresh final data accessed')
