"""Read-only scientific transcription audit; writes only its own audit report."""
import csv
import hashlib
import json
from pathlib import Path
import re
from collections import Counter

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
EVIDENCE=REPO/'research_paper/evidence'
RESULTS=EVIDENCE/'final_geometry_v2_results_20261012'

def digest(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rows(p):
    with p.open(newline='') as f:return list(csv.DictReader(f))
def main():
    m=json.loads((HERE/'support/asset_manifest.json').read_text())
    for p,h in m['source_sha256'].items():assert digest(REPO/p)==h,p
    for p,h in m['output_sha256'].items():assert digest(HERE/p)==h,p
    tool=json.loads((HERE/'support/tooling_provenance.json').read_text())
    assert digest(HERE/'IEEEtran.cls')==tool['IEEEtran']['sha256']
    table=(HERE/'tables/primary.tex').read_text()
    intervals=(HERE/'tables/intervals.tex').read_text()
    diagnosis=rows(EVIDENCE/'final_failure_analysis_20261012/event_diagnosis.csv')
    verified=[]
    for b,label,methods in [('fastlio','FAST-LIO',['FASTLIO_MIN_EIG_G3','DCREG_SCHUR_MASK']),('pointlio','Point-LIO',['POINTLIO_MIN_EIG_G3','POINTLIO_DCREG_SCHUR_MASK'])]:
        a=json.loads((RESULTS/(b+'_analysis.json')).read_text())
        assert a['status']=='CONFIRMATORY_COMPLETE' and a['completed_geometry_pairs']==48 and a['native_scene_runs_loaded']==96
        assert not a.get('threshold_selected_on_test',False) and not a.get('threshold_fit_performed',False)
        for i,method in enumerate(methods):
            s=a['method_metrics'][method];s=s if b=='fastlio' else s['summary']
            f=s['false_healthy_events'];n=s['false_healthy_conditional_denominator'];d=s['detected_recovery_events'];r=s['truth_recovered_events'];delay=s['detection_delay_median_s_detected_only']
            policy=['Scalar','Fixed Schur'][i]
            expected=f'{label} & {policy} & {f}/{n} & {d}/{r} & {r-d} & {delay:.3f}'
            assert expected in table,expected
            vals=[]
            for key in ['initial_false_healthy_conditional','recovery_detection_given_truth_recovered']:
                z=s['event_proportion_intervals'][key];lo,hi=z['wilson_95']
                vals.append(f"{100*z['fraction']:.1f} [{100*lo:.1f}, {100*hi:.1f}]")
            assert f'{label} & {policy} & '+ ' & '.join(vals) in intervals
            cohort=[x for x in diagnosis if x['method']==method];assert len(cohort)==48
            counts=Counter(x['miss_pattern'] for x in cohort if x['missed_recovery']=='True');assert sum(counts.values())==r-d
            assert s['available_decision_ticks']==s['planned_decision_ticks']==9600
            verified.append({'method':method,'primary_row':expected,'miss_classes':dict(counts)})
        original=rows(RESULTS/'corridor_event_ledger.csv')
        printed=(HERE/('tables/events_'+b+'.tex')).read_text()
        assert printed.count('\\\\\n')>=96
    assert rows(HERE/'support/complete_diagnostic_event_ledger.csv')==original
    assert rows(HERE/'support/complete_exploratory_diagnosis.csv')==diagnosis
    native=rows(HERE/'support/complete_native_run_ledger.csv');assert len(native)==192
    receipts=json.loads((RESULTS/'native_attempt_receipts.json').read_text())
    assert native==[{k:str(r.get(k,'')) for k in native[0]} for r in receipts]
    screen=rows(HERE/'support/complete_geometry_screen.csv');assert len(screen)==64 and sum(r['selected']=='True' for r in screen)==48
    for name in ['fastlio_simulation_bootstrap.yaml','point_lio_simulation_development.yaml']:
        assert digest(HERE/'support'/name)==digest(REPO/'research_paper/configs'/name)
    texts={n:(HERE/(n+'.tex')).read_text() for n in ['recovery_transfer_ieee','recovery_transfer_supplement']}
    references=[]
    for name,tex in texts.items():
        for group in re.findall(r'\\cite\{([^}]+)\}',tex):
            for key in group.split(','):assert '\\bibitem{'+key+'}' in tex,key
        for key in re.findall(r'\\ref\{([^}]+)\}',tex):assert '\\label{'+key+'}' in tex,key
        for p in re.findall(r'\\(?:input|lstinputlisting|includegraphics(?:\[[^]]*\])?)\{([^}]+)\}',tex):
            assert (HERE/p).is_file(),p
            references.append(p)
        log=(REPO/'output/pdf/ieee_20261023'/(name+'.log')).read_text()
        for bad in ['Overfull','undefined references','undefined citations','Missing character','! LaTeX Error']:
            assert bad not in log,(name,bad)
    report={'status':'PASS','scope':'Transcription, retained source identities, figure/table inputs and compiler diagnostics; not novelty or acceptance review',
            'geometry_pairs':48,'native_runs':192,'diagnostic_event_rows':192,'screen_candidates':64,
            'verified_methods':verified,'hashed_sources':len(m['source_sha256']),'hashed_assets':len(m['output_sha256']),
            'referenced_inputs':references,'font':'IEEEtran default Times Roman; embedded Nimbus Roman implementation',
            'document_sha256':{n:digest(HERE/(n+'.tex')) for n in texts},
            'pdf_sha256':{n:digest(REPO/'output/pdf/ieee_20261023'/(n+'.pdf')) for n in texts}}
    (HERE/'support/ieee_audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','geometry_pairs','native_runs','diagnostic_event_rows','screen_candidates','hashed_sources','hashed_assets']}))

if __name__=='__main__':main()
