"""Strict metadata adapter for geometry-v2's frozen FAST-LIO analysis.

The primary recorder uses the primary gate's eight-field execution identity.
The shared gate adds the Point-LIO threshold, which is bound in the common
freeze but absent from primary run identities. Adapt that expectation alone;
retain every original scientific computation and provenance check.
"""
import argparse
import json
from pathlib import Path
import re

import final_dataset_analysis as original

KEY = 'POINTLIO_MIN_EIG_G3_threshold'


def primary_identity(expected, validated_gate):
    if KEY not in expected or KEY not in validated_gate or expected[KEY] != validated_gate[KEY]:
        raise ValueError('missing or inconsistent validated Point-LIO threshold metadata')
    return {k:v for k,v in expected.items() if k != KEY}


def require_compatibility_review(review, r3_review, freeze):
    body=review.read_text()
    if not re.search(r'^\*\*Gate:\*\* PASS\s*$',body,re.MULTILINE):
        raise ValueError('independent compatibility review has not passed')
    bundles=[json.loads(s) for s in re.findall(r'```json\s*(.*?)```',body,re.DOTALL)]
    bundles=[b for b in bundles if b.get('schema') == 'r3-analysis-compatibility-v1']
    if len(bundles) != 1:raise ValueError('missing unambiguous compatibility inventory')
    expected={'compatibility_wrapper_sha256':original.execution.sha256_file(Path(__file__)),
              'original_analyzer_sha256':original.execution.sha256_file(Path(original.__file__)),
              'r3_review_sha256':original.execution.sha256_file(r3_review),
              'implementation_freeze_sha256':original.execution.sha256_file(freeze)}
    if bundles[0].get('artifacts') != expected:
        raise ValueError('compatibility review does not bind the exact adapter and frozen bundle')
    return {'compatibility_review_sha256':original.execution.sha256_file(review),**expected}


def analyze(results_root, screen, plan, r3_review, freeze, compatibility_review, output):
    accepted=require_compatibility_review(compatibility_review,r3_review,freeze)
    # Validate the unchanged full 197-entry scientific bundle before results.
    original.workflow.require_r3_pass(r3_review,freeze)
    saved=original.load_scene
    def adapted_load(root,result,seed,stratum,scene,gate,expected):
        return saved(root,result,seed,stratum,scene,gate,primary_identity(expected,gate))
    original.load_scene=adapted_load
    try:
        result=original.analyze(results_root,screen,plan,r3_review,freeze,output)
    finally:
        original.load_scene=saved
    result['analysis_compatibility']={**accepted,'operation':'Remove only the shared Point-LIO threshold from the expected primary execution identity; retain its validation in the unchanged shared freeze. No input, output, threshold or metric is modified.'}
    output.write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ('results-root','screen','plan','r3-review','freeze','compatibility-review','output'):
        p.add_argument('--'+flag,type=Path,required=True)
    a=p.parse_args()
    result=analyze(a.results_root,a.screen,a.plan,a.r3_review,a.freeze,a.compatibility_review,a.output)
    print(json.dumps({'status':result['status'],'planned_pairs':result['planned_geometry_pairs']}))
