"""Plot exploratory final-event diagnosis with retrospective truth clearly marked."""
import argparse
import csv
import gzip
import json
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import numpy as np

from analyze_final_failure_cases import CUTOFFS, METHODS, EVIDENCE as ACCEPTED
from t16_development_analysis import sha256_file, EPOCH_NS


def read(path):
    opener = gzip.open if path.suffix=='.gz' else open
    with opener(path, 'rt') as f:
        return list(csv.DictReader(f))


def value(row, key):
    return float(row[key]) if row[key] else np.nan


def plot(evidence, output):
    manifest = json.loads((evidence/'manifest.json').read_text())
    for name, digest in manifest['output_sha256'].items():
        if sha256_file(evidence/name) != digest:
            raise ValueError('Changed exploratory source: '+name)
    for b in METHODS:
        source = ACCEPTED/f'{b}_analysis.json'
        if sha256_file(source) != manifest['source_sha256'][str(source.resolve())]:
            raise ValueError('Changed accepted analysis source')
    observations = read(evidence/'event_diagnosis.csv')
    frames = read(evidence/'diagnostic_frames.csv.gz')
    ticks = read(evidence/'decision_ticks.csv.gz')
    windows = read(evidence/'primary_windows.csv')
    events = json.loads((evidence/'reconciled_events.json').read_text())
    selection = json.loads((evidence/'case_selection.json').read_text())
    output.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), layout='constrained')
    patterns = [('NO_RAW_HEALTHY_TICK_IN_RECOVERY_INTERVAL', 'No raw healthy tick', '#a44544'),
                ('RAW_HEALTHY_TICKS_WITHOUT_THREE_RECORD_CONFIRMATION', 'No three-record confirmation', '#d69c32'),
                ('ACTIVE_STATE_WITHOUT_NEW_POST_ONSET_TRANSITION', 'Active state, no new transition', '#246a9c')]
    for ax, b in zip(axes[0], METHODS):
        for i,m in enumerate(METHODS[b]):
            left = 0
            for key,label,color in patterns:
                n = manifest['miss_patterns'][m][key]
                ax.barh(i,n,left=left,color=color)
                if n: ax.text(left+n/2,i,str(n),ha='center',va='center',color='white',fontweight='bold')
                left += n
        ax.set(title=b+' — decomposition of missed recoveries', xlabel='Missed event count',
               yticks=[0,1],yticklabels=['Scalar','Fixed Schur'])
        ax.invert_yaxis()
    for ax,b in zip(axes[1],METHODS):
        cohort = [r for r in observations if r['backend']==b and r['method']==METHODS[b][0]]
        for row in cohort:
            fail = row['false_healthy']=='True'
            miss = row['missed_recovery']=='True'
            color = '#a44544' if fail else '#d69c32' if miss else '#246a9c'
            marker = 'x' if row['truth_status']!='RECOVERED' else 'o'
            ax.scatter(value(row,'post_exit_accepted_count_median'),value(row,'post_exit_scalar_score_median'),
                       c=color,marker=marker,s=32,alpha=.8)
        ax.axhline(CUTOFFS[b],ls='--',color='black',lw=1)
        ax.set(title=b+' — all 48 corridor events, scalar outcome',
               xlabel='Median accepted measurements in post-exit horizon',
               ylabel='Median scalar geometry score',yscale='log')
        ax.grid(alpha=.2)
    fig.legend(handles=[Patch(color=c,label=l) for _,l,c in patterns],
               loc='outside lower center',ncol=3,fontsize=9)
    fig.suptitle('Exploratory diagnosis: distinct reasons for missing a new recovery declaration\n'
                 'Scatter: red = initial false-healthy; amber = missed recovery; blue = neither; × = non-recovery',fontsize=12)
    fig.savefig(output/'failure_patterns.png',dpi=160)
    plt.close(fig)
    selected = sorted({(c['backend'],c['seed']) for c in selection['cases']})
    captions = []
    for b,seed in selected:
        f = sorted([r for r in frames if r['backend']==b and int(r['seed'])==seed and r['scene']=='CORRIDOR'],key=lambda r:float(r['time_s']))
        ctrl = sorted([r for r in frames if r['backend']==b and int(r['seed'])==seed and r['scene']=='CONTROL'],key=lambda r:float(r['time_s']))
        ee = [r for r in events if r['backend']==b and r['seed']==seed]
        ww = [r for r in windows if r['backend']==b and int(r['seed'])==seed]
        # Exit/deadline are available in the truth-label export, not inferred
        # from favorable error curves.
        root = ACCEPTED
        label = next(r for r in json.loads((root/f'{b}_analysis.json').read_text())['truth_labels'] if r['seed']==seed)
        exit_s = label['exit_time_s']
        x = np.array([float(r['time_s'])-exit_s for r in f])
        cx = np.array([float(r['time_s'])-exit_s for r in ctrl])
        fig, aa = plt.subplots(5,1,figsize=(12,11),sharex=True,layout='constrained')
        aa[0].plot(x,[value(r,'accepted_count') if r['valid']=='True' else np.nan for r in f],label='Corridor',color='#246a9c')
        aa[0].plot(cx,[value(r,'accepted_count') if r['valid']=='True' else np.nan for r in ctrl],label='Paired control',color='#777777',alpha=.7)
        aa[0].set(ylabel='Accepted count');aa[0].legend(loc='upper right',ncol=2)
        aa[1].plot(x,[value(r,'scalar_score') if r['valid']=='True' else np.nan for r in f],color='#246a9c',label='Corridor scalar')
        aa[1].plot(cx,[value(r,'scalar_score') if r['valid']=='True' else np.nan for r in ctrl],color='#777777',alpha=.7,label='Control scalar')
        aa[1].axhline(CUTOFFS[b],color='black',ls='--',label=f'Locked cutoff {CUTOFFS[b]:.3f}')
        aa[1].set(ylabel='Scalar score',yscale='log');aa[1].legend(loc='upper right',ncol=3,fontsize=8)
        aa[2].plot(x,[value(r,'fixed_score') if r['valid']=='True' else np.nan for r in f],color='#a44544')
        aa[2].axhline(.1,color='black',ls='--')
        aa[2].set(ylabel='Schur score\n1 / max κ',ylim=(-.02,1.02))
        for key,limit,color,name in [('translation_error_m',.2,'#246a9c','Translation / 0.20 m'),
                                     ('rotation_error_rad',np.deg2rad(5),'#a44544','Rotation / 5°')]:
            wx=[(float(r['end_ns'])-EPOCH_NS)/1e9-exit_s if r['end_ns'] else np.nan for r in ww]
            wy=[value(r,key)/limit if r['valid']=='True' else np.nan for r in ww]
            aa[3].plot(wx,wy,'o-',ms=3,color=color,label=name)
        aa[3].axhline(1,color='black',ls='--')
        aa[3].set_ylabel('Window error / limit\n(at window end)')
        aa[3].set_yscale('symlog',linthresh=1)
        aa[3].legend(loc='upper right',ncol=2,fontsize=8)
        for i,(m,color) in enumerate(zip(METHODS[b],['#246a9c','#a44544'])):
            tt=[r for r in ticks if r['backend']==b and int(r['seed'])==seed and r['method']==m]
            tx=np.array([float(r['time_s'])-exit_s for r in tt])
            state=np.array([float(r['confirmed_healthy']=='True') for r in tt])
            state[[r['available']!='True' for r in tt]]=np.nan
            aa[4].step(tx,state*.7+i,where='post',color=color,label='Scalar' if i==0 else 'Fixed Schur')
            alarms=[float(r['time_s'])-exit_s for r in tt if r['new_alarm']=='True']
            aa[4].scatter(alarms,[i+.7]*len(alarms),marker='v',s=25,color=color)
        aa[4].set(ylabel='Confirmed health\ntriangles = new alarm',yticks=[0,.7,1,1.7],yticklabels=['off','on','off','on'],xlabel='Seconds relative to frozen geometry exit')
        aa[4].legend(loc='upper right',ncol=2,fontsize=8)
        for ax in aa:
            ax.axvline(0,color='black',lw=1)
            if label['onset_s'] is not None:
                ax.axvline(label['onset_s']-exit_s,color='#48813f',ls='--',lw=1)
                ax.axvline(label['confirmation_s']-exit_s,color='#48813f',ls=':',lw=1)
            if label['relapse_s'] is not None:
                ax.axvline(label['relapse_s']-exit_s,color='#8b4598',ls='-.',lw=1)
            ax.set_xlim(-10,20);ax.grid(alpha=.2)
        short_category={'NO_RAW_HEALTHY_TICK_IN_RECOVERY_INTERVAL':'no raw healthy tick',
                        'RAW_HEALTHY_TICKS_WITHOUT_THREE_RECORD_CONFIRMATION':'no confirmation',
                        'ACTIVE_STATE_WITHOUT_NEW_POST_ONSET_TRANSITION':'active state without new alarm'}
        categories=[short_category.get(c['category'],c['category'])+' ('+('scalar' if c['method']==METHODS[b][0] else 'Schur')+')'
                    for c in selection['cases'] if c['backend']==b and c['seed']==seed]
        fig.suptitle(textwrap.fill(f'{b} seed {seed}: '+', '.join(categories),width=115)+'\n'
                     'Black = exit; green dashed = retrospective onset; green dotted = truth confirmation; purple = relapse',fontsize=11)
        filename=f'{b}_{seed}_timeline.png'
        fig.savefig(output/filename,dpi=140)
        plt.close(fig)
        captions.append({'image':filename,'backend':b,'seed':seed,'selection_categories':categories,
                         'truth_status':label['status'],'events':ee})
    (output/'case_captions.json').write_text(json.dumps(captions,indent=2)+'\n')
    (output/'manifest.json').write_text(json.dumps({'scope':'Exploratory post-result illustrations; retrospective truth is not online input',
        'plotter_sha256':sha256_file(Path(__file__)),
        'source_manifest_sha256':sha256_file(evidence/'manifest.json'),
        'outputs':{p.name:sha256_file(p) for p in output.iterdir() if p.is_file()},
        'selection_rule':selection['rule'],'illustrated_unique_backend_seed_pairs':len(selected)},indent=2)+'\n')
    print('Plotted overview and',len(selected),'deterministically selected timelines')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();plot(a.evidence,a.output)
