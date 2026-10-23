"""Present accepted final exports as CSV and prose; run from repository root."""
import csv,hashlib,json
from pathlib import Path
p=Path('research_paper/evidence/final_geometry_v2_results_20261012')
f=json.loads((p/'fastlio_analysis.json').read_text());q=json.loads((p/'pointlio_analysis.json').read_text())
strata=('TEST_SHORT_NARROW','TEST_SHORT_WIDE','TEST_LONG_NARROW','TEST_LONG_WIDE')
items=[]
for backend,d,keys in [('FAST-LIO',f,('FASTLIO_MIN_EIG_G3','DCREG_SCHUR_MASK')),('Point-LIO',q,('POINTLIO_MIN_EIG_G3','POINTLIO_DCREG_SCHUR_MASK'))]:
 for key in keys:
  m=d['method_metrics'][key]
  if backend=='FAST-LIO':s=m;e=d['event_metrics'][key];g=d['method_metrics_by_stratum'][key]
  else:s=m['summary'];e=m['event_rows'];g=m['by_stratum']
  items.append((backend,key,s,e,g,d))
def fraction(i):return f"{i['successes']}/{i['trials']} ({100*i['fraction']:.1f}%)" if i['fraction'] is not None else 'Unavailable'
def ci(i):return f"{100*i['wilson_95'][0]:.1f}–{100*i['wilson_95'][1]:.1f}%" if i['wilson_95'] else 'Unavailable'
def table(header,rows):return '\n'.join(['| '+' | '.join(header)+' |','| '+' | '.join(['---']*len(header))+' |']+['| '+' | '.join(map(str,r))+' |' for r in rows])
summary=[];groups=[];events=[];md=[]
for backend,key,s,e,g,d in items:
 name='Minimum eigenvalue' if 'MIN_EIG' in key else 'Fixed DCReg adaptation'
 i=s['event_proportion_intervals'];delay=s['detection_delay_median_s_detected_only']
 md.append([backend+' / '+name,fraction(i['initial_false_healthy_conditional'])+'; '+ci(i['initial_false_healthy_conditional']),fraction(i['initial_false_healthy_unconditional']),fraction(i['recovery_detection_given_truth_recovered'])+'; '+ci(i['recovery_detection_given_truth_recovered']),f'{delay:.3f} s',f"{s['available_decision_ticks']}/{s['planned_decision_ticks']}"])
 summary.append({'backend':backend,'method':key,**{k:v for k,v in s.items() if isinstance(v,(str,int,float,bool)) or v is None}})
 for st in strata:
  v=g[st];groups.append({'backend':backend,'method':key,'stratum':st,'planned_pairs':12,'recovered':v['truth_recovered_events'],'non_recovered':v['non_recovery_events'],'false_healthy':v['false_healthy_events'],'conditional_initial_denominator':v['false_healthy_conditional_denominator'],'unconditional_initial_denominator':v['false_healthy_event_unconditional_denominator'],'detected':v['detected_recovery_events'],'delay_median_s_detected_only':v['detection_delay_median_s_detected_only'],'availability':v['decision_availability_primary_horizon']})
 truth={r['seed']:r for r in d['truth_labels']}
 for r in e:
  events.append({'backend':backend,'method':key,'stratum':truth[r['seed']]['stratum'],**{k:v for k,v in r.items() if not isinstance(v,list)}})
for name,rows in [('method_summary.csv',summary),('stratum_summary.csv',groups),('corridor_event_ledger.csv',events)]:
 fields=list(dict.fromkeys(k for r in rows for k in r))
 with (p/name).open('w',newline='') as out:
  w=csv.DictWriter(out,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
truthrows=[]
for backend,d in [('FAST-LIO',f),('Point-LIO',q)]:
 for st in strata:
  rows=[r for r in d['truth_labels'] if r['stratum']==st];n=sum(r['onset_s'] is not None for r in rows)
  truthrows.append([backend,st.removeprefix('TEST_').replace('_',' / ').lower(),f'{n}/12',12-n,sum(r['relapse_s'] is not None for r in rows)])
paired=[]
for backend,d in [('FAST-LIO',f),('Point-LIO',q)]:
 v=d['paired_interior_difference'];paired.append([backend,f"{v['estimate']:.3f} m",f"[{v['interval_95'][0]:.3f}, {v['interval_95'][1]:.3f}] m"])
text='''# Final revised geometry evaluation — 12 October 2026

**Evaluation status: complete under the accepted revised protocol. Publication novelty and manuscript completion remain outstanding.**

Both frozen analyses returned `CONFIRMATORY_COMPLETE`: 48 geometry pairs per backend, 96 native scene runs each, 192 in total. All 48 paired corridor/control sensor-bag identities agree across backends. No native replay failed and no native retry/repeat was selected. Two workflow failures are retained separately: Point-LIO preflight stopped before any native attempt because its scratch root was absent; the original FAST analyzer rejected an extra shared Point threshold in its expected primary identity before loading final reference/poses/labels. The former required creating the directory; the latter required the independently accepted metadata-only adapter. Original frozen scientific sources and all 197 bound hashes remain unchanged.

## Design and provenance

The geometry screen selected 12 pairs in each of four frozen length/width groups from 64 checked candidates, using geometry criteria only, before estimator execution. Its hash is `f088c5cbe539da1624b638148662362ecab6a74a1de861094664df097a99b886`. IDs 100–179 from the failed earlier screen were excluded. The revised control spacing and larger pools were informed by that failed geometry screen; these fresh instances must not be described as a wholly unadapted test design. No final accuracy, indicator or recovery result selected a geometry or changed an operating point.

FAST-LIO's scalar cutoff remains `166.16366016039856`; Point-LIO's remains `123.80876977779258`. Fixed DCReg adaptations remain unchanged. Reference-defined recovery requires three consecutive non-overlapping one-second movement windows within 0.20 m translation error and 5 degrees rotation error, fully confirmed within 20 s of the predefined exit. Reference labels are offline, backend-specific, and separate from causal diagnostic decisions.

Sources: [FAST analysis](fastlio_analysis.json), [Point analysis](pointlio_analysis.json), [export audit](export_audit.json), [every native attempt receipt](native_attempt_receipts.json), [R3 review](../../reviews/R3_GEOMETRY_V2_IMPLEMENTATION_20261012.md), [original new freeze](../../protocol/IMPLEMENTATION_FREEZE_GEOMETRY_V2_20261012.md), [supplemental compatibility review](../../reviews/R3_GEOMETRY_V2_ANALYSIS_COMPATIBILITY_20261012.md). Raw bags, diagnostics, poses, evaluations and logs remain at the external paths recorded in these manifests.

## Locked diagnostic operating points

'''+table(['Backend / diagnostic','Initial false-healthy conditional; Wilson 95%','Initial false-healthy unconditional','Recovery detections; Wilson 95%','Median delay, detected only','Available/planned horizon ticks'],md)+'''

The conditional false-healthy denominator counts initial unrecovered intervals with at least one available diagnostic decision tick. The unconditional denominator includes all 48 non-empty initial intervals. Having 100% availability across the overall 20 s horizon does not guarantee a tick exists inside an extremely short initial interval. Recovery-detection denominators are 46 FAST-LIO and 32 Point-LIO truth-recovered events, rather than all 48 planned corridors. These are different own-pose labels; diagnostic sensitivities are not a direct estimator leaderboard.

FAST-LIO scalar missed 32 of 46 recoveries; its fixed DCReg adaptation missed 8. Point-LIO scalar missed 5 of 32; its fixed DCReg adaptation missed 7. Delay medians condition on detection: misses have no observed delay, and non-recoveries remain right-censored at the20 s deadline. No synthetic zero/infinite delay was assigned to them. Short median delay does not establish better overall responsiveness.

The scalar conditional false-healthy point estimates are below the development selection ceiling of 10%, but their 95% upper bounds are11.3% (FAST) and19.9% (Point). This dataset therefore does not establish a population false-healthy guarantee below 10%. Point-LIO's fixed DCReg adaptation has 16/47 initial false-healthy events, 34.0%, indicating limited transfer at that fixed rule.

## Recovery, non-recovery and geometry dependence

FAST-LIO truth recovery: 46/48 (95.8%; Wilson 95% 86.0–98.8%), two non-recoveries. Point-LIO: 32/48 (66.7%; 52.5–78.3%), 16 non-recoveries. Every corridor has usable truth; no corridor was discarded from these denominators.

'''+table(['Backend','Geometry group','Recovered / planned','Non-recovered','Relapse events'],truthrows)+'''

Both backends have one relapse. Neither FAST diagnostic produced a post-relapse false-healthy event (0/1). Point-LIO scalar is 0/1; fixed DCReg is 1/1. These secondary endpoints have only one relapsed event per backend: the zero-event Wilson upper bound is 79.3%, so they do not establish robust relapse reliability.

Point-LIO recovered in all 24 narrow corridors but only 8/24 wide corridors. Its scalar's four initial false-healthy events all occur in long/narrow (4/12); the aggregate 8.5% conditional rate hides this group dependence. FAST scalar detects only 1/12 long/wide recoveries. These are observed interactions under this screened simulation design; each group has only 12 independent geometries. Group Wilson intervals and complete per-event rows are retained in the analysis JSON/CSV.

## Paired interior movement error and uncertainty

For each geometry, the frozen analysis subtracts the control's median interior one-second translation error from the corridor's median error. It averages these paired differences with equal group weights. Positive values mean higher corridor error.

'''+table(['Backend','Mean corridor minus control','Geometry bootstrap 95%'],paired)+'''

The frozen bootstrap resamples paired geometry seeds within the four fixed groups, 10000 times, PCG64 seed 20260926. All48 pairs are used. Both aggregate intervals exclude zero. Group means vary: Point-LIO short/narrow is−0.087 m, while short/wide is+0.374 m. The aggregate cannot establish uniform benefit from control features in every group; within-group means plotted alone have no displayed confidence interval. The two backend aggregate intervals do not constitute a predeclared between-estimator superiority test.

Event-weighted threshold-free ROC/AP and their geometry bootstrap intervals are included in the full JSON. They describe score discrimination and must not substitute for performance at the fixed operating points. No threshold was chosen from final ROC/AP curves. Half/double tolerance and three-second-window sensitivity analyses are retained separately in those exports; they do not replace the primary endpoints.

## Visual evidence and reproduction

The [README](../../README.md) embeds and explains every retained research illustration, including the final operating points, group estimates, full 48-event ledger for each backend, and paired geometry effect. [Figure manifest](../../figures/final_geometry_v2_results_20261012/manifest.json) binds source exports, plotter and PNG hashes. [CSV summaries](method_summary.csv), [group summaries](stratum_summary.csv) and [complete diagnostic event rows](corridor_event_ledger.csv) retain numerical values. Four diagnostic rows per geometry in the last CSV are repeated analyses of shared geometry/own-backend labels; they are not 192 independent geometries.

On the current host, run the accepted primary adapter with the supplemental compatibility review and unchanged original review/freeze; run the unchanged Point analysis separately. Exact executed commands, exits and source identities are retained in [resumed driver state](analysis_resume_state.json). The original failed driver [state](pipeline_state.json) and failed Point [batch](pointlio_preflight_failed_batch.json) remain visible. Initialize scratch directories before native execution. Reuse validated native outputs for offline reanalysis; do not rerun or resample final scenes to improve results.

The compact export and plots can be reproduced from their scripts with a fresh output directory. A Git clone contains small evidence/figures and native patches, but does not include the external native environments, binaries, sensor bags or raw streams. Full native reproduction needs the recorded versions/configuration, source/binary hashes and external artifact paths.

## Verification, completion and novelty

The unchanged 197-entry freeze passed after integration and supplementation. Five focused adapter tests passed independently. Full current regression: 249 tests, 248 passed, one optional SciPy skip; compiled native reset fixture enabled. Unit/contract/native feasibility checks support implementation validity; the separate complete final cohort supplies the experimental findings reported here.

The planned controlled two-backend evaluation is complete. The evidence supports geometry-dependent transfer trade-offs and a positive aggregate paired interior error effect under the revised screened simulation design. It does not prove a novel detector, universal reliability, real-world recovery, physical flight safety or estimator superiority.

[OCE](https://link.springer.com/article/10.1007/s43684-026-00144-1) already evaluates ground-truth short-window motion usability and recovery hysteresis/delay. The narrower candidate contribution here is the frozen transfer assessment across randomized length/width groups with independently instrumented FAST-LIO and Point-LIO, complete event/failure accounting and geometry uncertainty. Publication novelty requires a precise comparison and a finished reviewed manuscript. The current main manuscript remains a proposal abstract. Hilti Exp18 remains development-only with insufficient sustained independent reference; GEODE failures remain retained. The earlier screening digest discrepancy is unresolved and is not repaired by this fresh cohort.
'''
(p/'RESULTS_REPORT.md').write_text(text)
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
manifest={'source_analysis_sha256':{x.name:sha(x) for x in (p/'fastlio_analysis.json',p/'pointlio_analysis.json')},'derived_output_sha256':{x.name:sha(x) for x in (p/'RESULTS_REPORT.md',p/'method_summary.csv',p/'stratum_summary.csv',p/'corridor_event_ledger.csv')},'report_generator_sha256':sha(Path(__file__)),'scope':'Presentation of accepted final exports; no recomputation, relabeling or threshold fitting'}
(p/'report_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
