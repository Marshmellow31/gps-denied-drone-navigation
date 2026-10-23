"""Typeset accepted evidence for the IEEE manuscript; no estimator or tuning runs."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import os
from collections import Counter
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EVIDENCE = ROOT / 'evidence'
RESULTS = EVIDENCE / 'final_geometry_v2_results_20261012'
FAILURE = EVIDENCE / 'final_failure_analysis_20261012'
REPOSITORY = ROOT.parent
STRATA = ['TEST_SHORT_NARROW', 'TEST_SHORT_WIDE', 'TEST_LONG_NARROW', 'TEST_LONG_WIDE']
LABELS = ['Short/narrow', 'Short/wide', 'Long/narrow', 'Long/wide']
METHODS = [('fastlio', 'FASTLIO_MIN_EIG_G3', 'FAST-LIO', 'Scalar'),
           ('fastlio', 'DCREG_SCHUR_MASK', 'FAST-LIO', 'Fixed Schur'),
           ('pointlio', 'POINTLIO_MIN_EIG_G3', 'Point-LIO', 'Scalar'),
           ('pointlio', 'POINTLIO_DCREG_SCHUR_MASK', 'Point-LIO', 'Fixed Schur')]
SOURCES: dict[str, str] = {}


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def source(path):
    SOURCES[str(path.relative_to(REPOSITORY))] = sha(path)
    return path


def load(path):
    return json.loads(source(path).read_text())


def rows(path):
    source(path)
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(name, data):
    with (HERE / 'support' / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(data)


def table(name, columns, header, data):
    content = ['\\begin{tabular}{@{}' + columns + '@{}}', '\\toprule',
               ' & '.join(header) + r'\\\midrule']
    content += [' & '.join(map(str, row)) + r'\\' for row in data]
    content += ['\\bottomrule', '\\end{tabular}', '']
    (HERE / 'tables' / (name + '.tex')).write_text('\n'.join(content))


def summary(a, backend, method):
    d = a[backend]['method_metrics'][method]
    return d if backend == 'fastlio' else d['summary']


def escape(value):
    return str(value).replace('_', r'\_').replace('%', r'\%').replace('&', r'\&')


def longtable(name, spec, header, data, caption):
    n = len(header)
    text = [r'\begingroup\footnotesize', '\\begin{longtable}{@{}' + spec + '@{}}',
            '\\caption{' + caption + r'}\\', r'\toprule',
            ' & '.join(header) + r'\\\midrule\endfirsthead',
            r'\multicolumn{' + str(n) + r'}{c}{\tablename\ \thetable{} -- continued}\\',
            r'\toprule', ' & '.join(header) + r'\\\midrule\endhead',
            '\\midrule\\multicolumn{' + str(n) + r'}{r}{Continued on next page}\\\endfoot',
            r'\bottomrule\endlastfoot']
    text += [' & '.join(escape(x) for x in row) + r'\\' for row in data]
    text += [r'\end{longtable}\endgroup', '']
    (HERE / 'tables' / (name + '.tex')).write_text('\n'.join(text))


def main():
    a = {b: load(RESULTS / (b + '_analysis.json')) for b in ['fastlio', 'pointlio']}
    for d in a.values():
        assert d['status'] == 'CONFIRMATORY_COMPLETE'
        assert d['completed_geometry_pairs'] == d['planned_geometry_pairs'] == 48
        assert d['native_scene_runs_loaded'] == 96
    assert a['fastlio']['threshold_selected_on_test'] is False
    assert a['pointlio']['threshold_fit_performed'] is False
    diagnoses = rows(FAILURE / 'event_diagnosis.csv')
    event_ledger = rows(RESULTS / 'corridor_event_ledger.csv')
    assert len(diagnoses) == len(event_ledger) == 192
    primary, intervals, misses, auc, tolerance, window3 = [], [], [], [], [], []
    export = []
    for backend, method, label, policy in METHODS:
        s = summary(a, backend, method)
        fh, den = s['false_healthy_events'], s['false_healthy_conditional_denominator']
        detected, recovered = s['detected_recovery_events'], s['truth_recovered_events']
        primary.append([label, policy, f'{fh}/{den}', f'{detected}/{recovered}',
                        recovered-detected, f"{s['detection_delay_median_s_detected_only']:.3f}"])
        ci = s['event_proportion_intervals']
        def interval(which):
            x = ci[which]
            return f"{100*x['fraction']:.1f} [{100*x['wilson_95'][0]:.1f}, {100*x['wilson_95'][1]:.1f}]"
        intervals.append([label, policy, interval('initial_false_healthy_conditional'),
                          interval('recovery_detection_given_truth_recovered')])
        cohort = [r for r in diagnoses if r['method'] == method]
        assert len(cohort) == 48
        counts = Counter(r['miss_pattern'] for r in cohort if r['missed_recovery'] == 'True')
        parts = [counts[k] for k in ['NO_RAW_HEALTHY_TICK_IN_RECOVERY_INTERVAL',
                 'RAW_HEALTHY_TICKS_WITHOUT_THREE_RECORD_CONFIRMATION',
                 'ACTIVE_STATE_WITHOUT_NEW_POST_ONSET_TRANSITION']]
        assert sum(parts) == recovered-detected
        misses.append([('FAST' if backend == 'fastlio' else 'Point') + ' ' +
                       ('scalar' if policy == 'Scalar' else 'Schur'), *parts, sum(parts)])
        curve = a[backend]['threshold_free_curves'][method]
        assert curve['status'] == 'AVAILABLE' and curve['undefined_replicates'] == 0
        assert curve['bootstrap_replicates'] == 10000
        fmt = lambda key: f"{curve[key]:.3f} [{curve[key+'_interval_95'][0]:.3f}, {curve[key+'_interval_95'][1]:.3f}]"
        auc.append([label, policy, fmt('roc_auc'), fmt('average_precision')])
        export.append({'backend': backend, 'method': method, 'primary': s,
                       'curve': curve, 'miss_partition': parts})
    table('primary', 'llrrrr', ['Backend', 'Policy', 'Initial FH', 'Declarations', 'Misses', 'Delay (s)'], primary)
    table('intervals', 'llrr', ['Backend', 'Policy', r'Conditional FH (\%; 95\% CI)', r'Declarations (\%; 95\% CI)'], intervals)
    table('misses', 'lrrrr', ['Policy', 'No raw', 'No confirm.', 'Active', 'Total'], misses)
    table('curves', 'llrr', ['Backend', 'Policy', r'ROC-AUC [95\% CI]', r'AP [95\% CI]'], auc)
    for backend, label in [('fastlio', 'FAST-LIO'), ('pointlio', 'Point-LIO')]:
        for key, name in [('half_tolerance_recovery', 'Half'), (None, 'Primary'), ('double_tolerance_recovery', 'Double')]:
            if key:
                d = a[backend][key]['pooled']
                num, den, ci = d['recovered_events'], d['truth_eligible_events'], d['recovery_wilson_95']
            else:
                d = summary(a, backend, METHODS[0 if backend == 'fastlio' else 2][1])
                num, den, ci = d['truth_recovered_events'], 48, d['truth_recovery_wilson_95']
            tolerance.append([label, name, f'{num}/{den}', f'{100*num/den:.1f}',
                              f'[{100*ci[0]:.1f}, {100*ci[1]:.1f}]'])
        for scene in ['corridor', 'control']:
            d = a[backend]['three_second_rate_sensitivity'][scene]
            window3.append([label, scene.capitalize(), d['events_with_valid_windows'],
                            f"{d['valid_window_count_total']}/{d['planned_window_count_total']}",
                            f"{100*d['equal_event_mean_pass_fraction']:.2f}"])
    table('tolerance', 'llrrr', ['Backend', 'Tolerance', 'Recovered', r'Rate (\%)', r'Wilson 95\%'], tolerance)
    table('window3', 'llrrr', ['Backend', 'Scene', 'Events', 'Valid/planned', r'Mean pass (\%)'], window3)
    write_csv('complete_diagnostic_event_ledger.csv', event_ledger)
    write_csv('complete_exploratory_diagnosis.csv', diagnoses)
    # The screen is read, never generated or rerun.
    screen = load(EVIDENCE / 'final_geometry_screen_v2_20261012.json')
    selected = {x for group in screen['selected_seeds_by_stratum'].values() for x in group}
    assert len(selected) == 48 and len(screen['screened_layouts']) == 64
    candidates = []
    short = dict(zip(STRATA, ['SN', 'SW', 'LN', 'LW']))
    for r in screen['screened_layouts']:
        g = r['geometry']
        candidates.append({'group': short[r['stratum']], 'seed': r['seed'],
            'length_m': g['corridor_length_m'], 'half_width_m': g['corridor_half_width_m'],
            'corridor_axial_fraction': r['corridor_midpoint']['axial_normal_fraction'],
            'control_axial_fraction': r['control_midpoint']['axial_normal_fraction'],
            'post_exit_axial_fraction': r['post_exit_plus5_s']['axial_normal_fraction'],
            'eligible': r['eligible'], 'selected': r['seed'] in selected})
    write_csv('complete_geometry_screen.csv', candidates)
    longtable('screen_ledger', 'llrrrrrll', ['Group', 'Seed', '$L$', '$w$', '$f_c$', '$f_u$', '$f_{+5}$', 'Eligible', 'Used'],
              [[r['group'], r['seed'], f"{r['length_m']:.3f}", f"{r['half_width_m']:.3f}",
                f"{r['corridor_axial_fraction']:.3f}", f"{r['control_axial_fraction']:.3f}",
                f"{r['post_exit_axial_fraction']:.3f}", 'yes' if r['eligible'] else 'no',
                'yes' if r['selected'] else 'no'] for r in candidates],
              'All 64 revised-screen candidates. Length and half-width are in metres; fractions are rounded for display only.')
    # Every scientific event row is typeset; full-precision CSV remains adjacent.
    for backend, label in [('fastlio', 'FAST-LIO'), ('pointlio', 'Point-LIO')]:
        diag = {(int(r['seed']), r['method']): r for r in diagnoses if r['backend'] == backend}
        data = []
        for r in sorted([r for r in event_ledger if r['backend'] == label], key=lambda r:(int(r['seed']), r['method'])):
            d = diag[(int(r['seed']), r['method'])]
            reason = {'NOT_A_MISSED_RECOVERY':'--', 'NO_RAW_HEALTHY_TICK_IN_RECOVERY_INTERVAL':'raw',
                      'RAW_HEALTHY_TICKS_WITHOUT_THREE_RECORD_CONFIRMATION':'confirm',
                      'ACTIVE_STATE_WITHOUT_NEW_POST_ONSET_TRANSITION':'active'}[d['miss_pattern']]
            data.append([short[r['stratum']], r['seed'], 'S' if 'MIN_EIG' in r['method'] else 'D',
                         'R' if r['truth_status'] == 'RECOVERED' else 'NR',
                         'yes' if r['false_healthy_in_initial_unrecovered_interval'] == 'True' else 'no',
                         'yes' if r['detected_post_onset'] == 'True' else 'no',
                         f"{float(r['detection_delay_s']):.3f}" if r['detection_delay_s'] else '--', reason])
        assert len(data) == 96
        longtable('events_' + backend, 'llclllrl', ['Group', 'Seed', 'Policy', 'Truth', 'FH', 'Declared', 'Delay (s)', 'Miss class'], data,
                  label + ': all 96 policy-event rows (48 shared geometries; S = scalar, D = adapted directional rule).')
    receipts = load(RESULTS / 'native_attempt_receipts.json')
    assert len(receipts) == 192 and all(r['status'] == 'COMPLETED' for r in receipts)
    write_csv('complete_native_run_ledger.csv', [{k:r.get(k,'') for k in
        ['backend','seed','stratum','scene','run_id','status','return_code','elapsed_s','manifest_sha256','manifest_path']}
        for r in receipts])
    package = REPOSITORY / 'reproduction/lidar_recovery_20261023'
    path_map = load(package / 'path_map.json')
    identity = {}
    for b in ['fastlio', 'pointlio']:
        all_ids = []
        for r in receipts:
            if r['backend'] != b: continue
            path = package / path_map[r['manifest_path']]
            assert sha(path) == r['manifest_sha256']
            m = load(path)
            if b == 'fastlio':
                z = m['fingerprint']['execution_identity']['backend']
                item = {'upstream_commit':z['upstream_commit'], 'binary_sha256':z['binary_sha256'],
                    'configuration_sha256':z['configuration_sha256'], 'worktree_diff_sha256':z['worktree_diff_sha256']}
            else:
                item = {'upstream_commit':m['native_source']['commit'], 'binary_sha256':m['native_binary']['sha256'],
                    'configuration_sha256':m['configuration']['sha256'], 'worktree_diff_sha256':m['native_source']['dirty_patch_sha256']}
            all_ids.append(item)
        assert len(all_ids) == 96 and all(x == all_ids[0] for x in all_ids)
        identity[b] = all_ids[0]
    (HERE/'support/native_build_identities.json').write_text(json.dumps(identity,indent=2)+'\n')
    for filename in ['fastlio_simulation_bootstrap.yaml','point_lio_simulation_development.yaml']:
        config = source(ROOT/'configs'/filename)
        shutil.copy2(config, HERE/'support'/filename)
    from build_supplement_tables import main as supplement_tables
    supplement_tables()
    source(EVIDENCE/'t14_repeatability_audit.json')
    # Publication graphics reuse saved estimates and exported timeline samples.
    os.environ.setdefault('MPLCONFIGDIR', '/tmp/lidar-ieee-matplotlib-20261023')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, FancyArrowPatch
    import numpy as np
    plt.rcParams.update({'font.family':'serif','font.serif':['Liberation Serif'], 'font.size':9,
        'axes.titlesize':10,'axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':8,
        'legend.fontsize':8,'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,
        'axes.spines.right':False,'mathtext.fontset':'stix'})
    colors = ['#17649a', '#a43a35']
    def save(fig, name):
        fig.savefig(HERE/'assets'/(name+'.pdf'),bbox_inches='tight',pad_inches=.03)
        fig.savefig(HERE/'assets'/(name+'.png'),dpi=220,bbox_inches='tight',pad_inches=.03)
        plt.close(fig)
    fig, ax = plt.subplots(2,2,figsize=(7.05,4.4),layout='constrained')
    x = np.arange(4)
    names = ['FAST\nScalar','FAST\nSchur','Point\nScalar','Point\nSchur']
    for k,which in enumerate(['initial_false_healthy_conditional','recovery_detection_given_truth_recovered']):
        for i,(b,m,_,_) in enumerate(METHODS):
            s = summary(a,b,m);v=s['event_proportion_intervals'][which];y=100*v['fraction'];lo,hi=[100*q for q in v['wilson_95']]
            ax[0,k].errorbar(i,y,yerr=[[y-lo],[hi-y]],fmt='o',capsize=3,color=colors[i//2])
            ax[0,k].annotate(f"{v['successes']}/{v['trials']}",(i,y),(0,9),textcoords='offset points',ha='center',fontsize=8)
        ax[0,k].set(xticks=x,xticklabels=names,ylim=(-4,111),ylabel='Events (%)',title=['(a) Initial false-healthy','(b) New recovery declarations'][k]);ax[0,k].grid(axis='y',alpha=.2)
    ss=[summary(a,b,m) for b,m,_,_ in METHODS]
    ax[1,0].bar(x,[s['detection_delay_median_s_detected_only'] for s in ss],color=[colors[i//2] for i in x])
    for i,s in enumerate(ss):ax[1,0].text(i,s['detection_delay_median_s_detected_only']+.08,f"{s['detection_delay_median_s_detected_only']:.2f}",ha='center',fontsize=8)
    ax[1,0].set(xticks=x,xticklabels=names,ylim=(0,8),ylabel='Seconds',title='(c) Delay among declarations only')
    ax[1,1].bar(x,[100*s['decision_availability_primary_horizon'] for s in ss],color=[colors[i//2] for i in x]);ax[1,1].set(xticks=x,xticklabels=names,ylim=(0,112),ylabel='Available ticks (%)',title='(d) Diagnostic availability')
    for i in x:ax[1,1].text(i,102,'9600/9600',ha='center',fontsize=7)
    save(fig,'operating_points')
    fig, ax = plt.subplots(1,2,figsize=(7.05,2.55),layout='constrained')
    for i,b in enumerate(['fastlio','pointlio']):
        for j,st in enumerate(STRATA):
            labels=[r for r in a[b]['truth_labels'] if r['stratum']==st]
            ax[0].bar(j+(i-.5)*.35,sum(r['onset_s'] is not None for r in labels),width=.33,color=colors[i],label=['FAST-LIO','Point-LIO'][i] if j==0 else None)
        d=a[b]['paired_interior_difference'];v=d['estimate'];lo,hi=d['interval_95']
        ax[1].errorbar(v,i,xerr=[[v-lo],[hi-v]],fmt='o',capsize=4,color=colors[i])
        ax[1].annotate(f'{v:.3f} [{lo:.3f}, {hi:.3f}]',(v,i),(0,12),textcoords='offset points',ha='center',fontsize=8)
    ax[0].set(xticks=range(4),xticklabels=['Short\nnarrow','Short\nwide','Long\nnarrow','Long\nwide'],ylim=(0,14),yticks=[0,4,8,12],ylabel='Recovered / 12',title='(a) Reference-defined recovery');ax[0].legend(loc='upper right',fontsize=7)
    ax[1].set(yticks=[0,1],yticklabels=['FAST-LIO','Point-LIO'],ylim=(-.5,1.6),xlabel='Corridor minus control error (m)',title='(b) Paired geometry mean and 95% interval');ax[1].axvline(0,color='grey',lw=.8,ls='--');ax[1].grid(axis='x',alpha=.2)
    save(fig,'geometry_effects')
    # Schematic uses an existing selected layout's exact recorded dimensions.
    sample=next(r for r in screen['screened_layouts'] if r['seed']==10000)
    g=sample['geometry'];L=g['corridor_length_m'];w=g['corridor_half_width_m'];room=g['room_half_width_m']
    n=max(4,math.ceil(L/2)-1);positions=np.linspace(0,L,n+2)[1:-1]
    fig,axes=plt.subplots(1,2,figsize=(7.05,2.15),layout='constrained')
    for i,axis in enumerate(axes):
        vertices=[(-6,-room),(0,-room),(0,-w),(L,-w),(L,-room),(L+6,-room),
                  (L+6,room),(L,room),(L,w),(0,w),(0,room),(-6,room)]
        v=np.array(vertices+[vertices[0]]);axis.plot(v[:,0],v[:,1],color='#333333',lw=1)
        if i:
            for t in positions:axis.plot([t,t],[.65*w,w],color=colors[1],lw=3)
        axis.axvline(0,color='grey',lw=.7,ls=':');axis.axvline(L,color='grey',lw=.7,ls=':')
        axis.annotate('',(L+4,0),(-4,0),arrowprops={'arrowstyle':'->','color':colors[0],'lw':1.2})
        axis.annotate('',(L,-w-.65),(0,-w-.65),arrowprops={'arrowstyle':'<->','lw':.8})
        axis.text(L/2,-w-1.15,f'L = {L:.3f} m',ha='center',fontsize=8)
        axis.text(L/2,w+.8,f'Full width 2w = {2*w:.3f} m',ha='center',fontsize=8)
        axis.set(title=['(a) Corridor','(b) Matched control'][i],xlim=(-6.3,L+6.3),ylim=(-room-.4,room+.4),aspect='equal');axis.axis('off')
        axis.text(0,-room-.2,'entry',ha='center',fontsize=7);axis.text(L,-room-.2,'exit',ha='center',fontsize=7)
    save(fig,'geometry_schematic')
    # Conceptual example, explicitly separate from native timelines.
    fig,ax=plt.subplots(figsize=(3.4,1.65),layout='constrained')
    for start in [2,3,4]:ax.add_patch(Rectangle((start,1.45),1,.35,facecolor='#dfebdf',edgecolor='#548154',lw=.7));ax.text(start+.5,1.62,'pass',ha='center',va='center',fontsize=8)
    ax.step([-1,0,.7,5.8],[.3,.3,.95,.95],where='post',color=colors[0],lw=1.5)
    ax.axvline(2,color='black',ls='--',lw=.8);ax.axvline(5,color='black',ls=':',lw=.8)
    ax.text(2,2.05,'onset',ha='center',fontsize=8);ax.text(5,2.05,'truth confirmation',ha='center',fontsize=8)
    ax.text(3.8,.65,'active; no new transition',ha='center',fontsize=8)
    ax.plot(.7,.95,'v',color=colors[0],ms=5);ax.set(xlim=(-.2,6),ylim=(0,2.3),xticks=[0,2,5],xticklabels=['exit','2 s','5 s'],yticks=[],xlabel='Illustrative time after exit');ax.spines['left'].set_visible(False)
    save(fig,'endpoint_timing')
    ticks=rows(FAILURE/'decision_ticks.csv.gz');windows=rows(FAILURE/'primary_windows.csv');frames=rows(FAILURE/'diagnostic_frames.csv.gz')
    selection=load(FAILURE/'case_selection.json')
    examples=[('fastlio',10001,'FASTLIO_MIN_EIG_G3','NO_RAW_HEALTHY_TICK_IN_RECOVERY_INTERVAL'),
              ('pointlio',10002,'POINTLIO_DCREG_SCHUR_MASK','ACTIVE_STATE_WITHOUT_NEW_POST_ONSET_TRANSITION')]
    fig,axes=plt.subplots(3,2,figsize=(7.05,4.25),sharex='col',layout='constrained')
    example_receipts=[]
    for col,(b,seed,method,category) in enumerate(examples):
        assert any(c['backend']==b and c['seed']==seed and c['method']==method and c['category']==category for c in selection['cases'])
        label=next(r for r in a[b]['truth_labels'] if r['seed']==seed);exit_s=label['exit_time_s']
        f=[r for r in frames if r['backend']==b and int(r['seed'])==seed and r['scene']=='CORRIDOR']
        t=[r for r in ticks if r['backend']==b and int(r['seed'])==seed and r['method']==method]
        ww=[r for r in windows if r['backend']==b and int(r['seed'])==seed]
        score='scalar_score' if col==0 else 'fixed_score';cutoff=166.16366016039856 if col==0 else .1
        yy=[float(r[score]) if r['valid']=='True' and r[score] else np.nan for r in f]
        axes[0,col].plot([float(r['time_s'])-exit_s for r in f],yy,color=colors[col],lw=.8)
        axes[0,col].axhline(cutoff,ls='--',lw=.8,color='black');axes[0,col].set_ylabel('Scalar score' if col==0 else '1 / max condition ratio')
        if col==0:axes[0,col].set_yscale('log')
        axes[0,col].set_title(['(a) FAST scalar: seed 10001','(b) Point Schur: seed 10002'][col])
        xw=[(float(r['end_ns'])-1e12)/1e9-exit_s if r['end_ns'] else np.nan for r in ww]
        for key,lim,color,labelname in [('translation_error_m',.2,colors[0],'Translation / limit'),('rotation_error_rad',math.radians(5),colors[1],'Rotation / limit')]:
            axes[1,col].plot(xw,[float(r[key])/lim if r['valid']=='True' and r[key] else np.nan for r in ww],'.-',ms=2,lw=.7,color=color,label=labelname)
        axes[1,col].axhline(1,color='black',ls='--',lw=.8);axes[1,col].set_yscale('symlog',linthresh=1);axes[1,col].set_ylabel('Window error / limit');axes[1,col].legend(fontsize=6,loc='upper right')
        xt=[float(r['time_s'])-exit_s for r in t]
        axes[2,col].step(xt,[float(r['confirmed_healthy']=='True') if r['available']=='True' else np.nan for r in t],where='post',lw=1,color=colors[col])
        alarms=[float(r['time_s'])-exit_s for r in t if r['new_alarm']=='True'];axes[2,col].scatter(alarms,[1]*len(alarms),marker='v',s=20,color='black',zorder=5)
        axes[2,col].set(ylim=(-.1,1.25),yticks=[0,1],yticklabels=['off','on'],ylabel='Confirmed health',xlabel='Seconds relative to exit')
        for axis in axes[:,col]:
            axis.axvline(0,color='grey',lw=.7)
            axis.axvline(label['onset_s']-exit_s,color='#397449',ls='--',lw=.9)
            axis.axvline(label['confirmation_s']-exit_s,color='#397449',ls=':',lw=.9)
            axis.set_xlim(-3,20);axis.grid(alpha=.17)
        example_receipts.append({'backend':b,'seed':seed,'method':method,'original_selection_category':category,
                                 'exit_time_s':exit_s,'onset_s':label['onset_s'],'confirmation_s':label['confirmation_s']})
    save(fig,'native_examples')
    (HERE/'support/timeline_selection.json').write_text(json.dumps(example_receipts,indent=2)+'\n')
    # Compact all-event ledger retains all 48 geometries per backend.
    from matplotlib.colors import ListedColormap
    fig,axes=plt.subplots(2,1,figsize=(7.05,3.8),layout='constrained')
    for axis,b in zip(axes,['fastlio','pointlio']):
        seeds=[s for st in STRATA for s in screen['selected_seeds_by_stratum'][st]];labelmap={r['seed']:r for r in a[b]['truth_labels']}
        methodkeys=[m for bb,m,_,_ in METHODS if bb==b];matrix=np.zeros((5,48))
        for j,seed in enumerate(seeds):
            lab=labelmap[seed];matrix[0,j]=int(lab['onset_s'] is not None)
            for i,m in enumerate(methodkeys):
                d=next(r for r in diagnoses if r['backend']==b and int(r['seed'])==seed and r['method']==m)
                matrix[1+i,j]=int(d['false_healthy']=='True')
                matrix[3+i,j]=int(d['missed_recovery']=='True') if lab['onset_s'] is not None else 2
        axis.imshow(matrix,cmap=ListedColormap(['#f2f2f2','#17649a','#9d9d9d']),vmin=0,vmax=2,aspect='auto',interpolation='nearest')
        axis.set(yticks=range(5),yticklabels=['Recovered','Scalar FH','Schur FH','Scalar miss','Schur miss'],xticks=range(48),xticklabels=seeds,title='FAST-LIO' if b=='fastlio' else 'Point-LIO');axis.tick_params(axis='x',labelrotation=90,labelsize=5)
        for x in [11.5,23.5,35.5]:axis.axvline(x,color='black',lw=.8)
    save(fig,'all_event_ledger')
    for path in [ROOT/'protocol/METRICS.md',ROOT/'protocol/INDICATORS.md',ROOT/'protocol/IMPLEMENTATION_FREEZE_GEOMETRY_V2_20261012.md',
                 ROOT/'reviews/FINAL_GEOMETRY_V2_RESULT_AUDIT_20261012.md', EVIDENCE/'screening_provenance_reconciliation_20261012.json',
                 EVIDENCE/'simulation_seed_sensitivity_manifest.json', package/'VALIDATION.json']:
        source(path)
    (HERE/'support/accepted_values.json').write_text(json.dumps({'methods':export,'tolerance_rows':tolerance,
        'three_second_rows':window3,'paired_interior_difference':{b:a[b]['paired_interior_difference'] for b in a}},indent=2)+'\n')
    outputs={str(p.relative_to(HERE)):sha(p) for folder in ['assets','tables','support']
             for p in (HERE/folder).rglob('*') if p.is_file() and p.name not in ['asset_manifest.json','tooling_provenance.json','ieee_audit.json']}
    (HERE/'support/asset_manifest.json').write_text(json.dumps({'scope':'Presentation of accepted exports; no estimator replay, threshold fit, bootstrap rerun or new hypothesis test',
        'source_sha256':SOURCES,'output_sha256':outputs,'geometry_pairs':48,'native_slots':192,'diagnostic_event_rows':192,
        'revised_candidates':64,'timeline_selection':'Original lowest-seed category rule; two illustrative cases, not prevalence estimates'},indent=2)+'\n')
    print('Built 6 vector figures, 12 tables, full screening/native/event CSVs and hash provenance')


if __name__ == '__main__':
    main()
