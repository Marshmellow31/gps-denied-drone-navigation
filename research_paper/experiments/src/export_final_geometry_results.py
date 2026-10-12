"""Export compact audited final evidence; leave raw native files in place."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):h.update(block)
    return h.hexdigest()


def export(root, output):
    paths = {'fastlio_analysis.json': root/'analysis_fastlio', 'pointlio_analysis.json': root/'analysis_pointlio', 'fastlio_batch.json': root/'fastlio/final_batch_summary.json', 'pointlio_batch.json': root/'pointlio/pointlio_final_batch_summary.json', 'pipeline_state.json': root/'pipeline_state.json', 'analysis_resume_state.json': root/'analysis_resume_state.json', 'pointlio_preflight_failed_batch.json': root/'pointlio_preflight_failure_20261012/pointlio_final_batch_summary.json'}
    data = {name:json.loads(path.read_text()) for name,path in paths.items()}
    for name in ('fastlio_analysis.json', 'pointlio_analysis.json'):
        d=data[name]
        if d['status'] != 'CONFIRMATORY_COMPLETE' or d['planned_geometry_pairs'] != 48 or d['completed_geometry_pairs'] != 48 or d['native_scene_runs_loaded'] != 96 or d['failed_or_unusable_pairs']:
            raise ValueError(f'{name} does not represent the complete accepted cohort')
    if data['analysis_resume_state.json']['status'] != 'ANALYSES_FINISHED_REQUIRES_RESULT_AUDIT':
        raise ValueError('sequential driver has not finished both analyses')
    fast_pairs = {(p['stratum'],p['seed']):p for p in data['fastlio_batch.json']['pair_results']}
    point_pairs = {(p['stratum'],p['seed']):p for p in data['pointlio_batch.json']['pair_results']}
    if len(fast_pairs) != 48 or set(point_pairs) != set(fast_pairs):
        raise ValueError('backend pair inventories differ')
    for key, fast in fast_pairs.items():
        point = point_pairs[key]
        for field in ('corridor_bag_sha256','control_bag_sha256'):
            if fast[field] != point[field]:raise ValueError('same-input backend identity mismatch')
    receipts = []
    counts = {}
    for backend in ('fastlio', 'pointlio'):
        counter=Counter()
        for path in sorted((root/backend/'runs').glob('*/run_manifest.json')):
            m=json.loads(path.read_text());counter[m['status']]+=1
            out=m.get('outputs',m.get('output_sha256',{}))
            if not isinstance(out,dict):raise ValueError('invalid native output identity')
            receipts.append({'backend':backend,'manifest_path':str(path),'manifest_sha256':digest(path), **{k:m[k] for k in ('run_id','scheduled_run_id','seed','stratum','scene','control','status','reason','return_code','elapsed_s','counts','completion_validation') if k in m}, 'outputs':out})
        if counter['COMPLETED'] != 96:
            raise ValueError(f'{backend}: unexpected completed native slot count')
        counts[backend]=dict(counter)
    output.mkdir(parents=True,exist_ok=False)
    copied = {}
    for name,path in paths.items():
        shutil.copyfile(path,output/name)
        copied[name]={'source_path':str(path),'sha256':digest(path)}
        if digest(output/name) != copied[name]['sha256']:raise ValueError('export byte identity failed')
    (output/'native_attempt_receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
    audit={'status':'PASS_COMPACT_EXPORT','complete_native_counts':counts,'same_sensor_input_pairs':48,'analysis_statuses':{name:data[name]['status'] for name in ('fastlio_analysis.json','pointlio_analysis.json')},'source_copies':copied,'native_attempt_receipts_sha256':digest(output/'native_attempt_receipts.json'),'exporter_sha256':digest(Path(__file__)),'retained_workflow_failures':['Point-LIO preflight: missing scratch root, zero native attempts','Original FAST-LIO analysis: shared secondary threshold metadata absent from primary identity; corrected only by independently accepted compatibility adapter'],'scope':'Compact export and complete-cohort reconciliation. Frozen analysis callers and independently reviewed compatibility adapter perform full native output/source validation; raw streams remain at recorded external paths.'}
    (output/'export_audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit['complete_native_counts']))


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();export(a.root,a.output)
