"""Plot accepted final analysis exports without fitting or changing outcomes."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

STRATA = ('TEST_SHORT_NARROW', 'TEST_SHORT_WIDE', 'TEST_LONG_NARROW', 'TEST_LONG_WIDE')
METHODS = ('Minimum eigenvalue', 'Fixed DCReg adaptation')
COLORS = ('#246a9c', '#a44544')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unpack(data, backend):
    keys = ('FASTLIO_MIN_EIG_G3', 'DCREG_SCHUR_MASK') if backend == 'FAST-LIO' else ('POINTLIO_MIN_EIG_G3', 'POINTLIO_DCREG_SCHUR_MASK')
    if backend == 'FAST-LIO':
        return [(data['method_metrics'][k], data['event_metrics'][k], data['method_metrics_by_stratum'][k]) for k in keys]
    return [(data['method_metrics'][k]['summary'], data['method_metrics'][k]['event_rows'], data['method_metrics'][k]['by_stratum']) for k in keys]


def fraction_plot(ax, rows, field, title):
    for i, (label, summary, color) in enumerate(rows):
        value = summary['event_proportion_intervals'][field]
        if value['fraction'] is None:
            ax.text(i, 0.05, 'Unavailable', rotation=90, ha='center')
            continue
        v = value['fraction'] * 100
        lo, hi = np.asarray(value['wilson_95']) * 100
        ax.errorbar(i, v, yerr=[[v-lo], [hi-v]], fmt='o', color=color, capsize=4)
        ax.annotate(f"{value['successes']}/{value['trials']}", (i, v), xytext=(0, 9), textcoords='offset points', ha='center', fontsize=9)
    ax.set(title=title, ylim=(-5, 115), ylabel='Events (%)', xticks=range(len(rows)), xticklabels=[r[0] for r in rows])
    ax.tick_params(axis='x', labelrotation=20)
    ax.grid(axis='y', alpha=.2)


def plot(fast_path, point_path, output):
    data = [json.loads(p.read_text()) for p in (fast_path, point_path)]
    if any(d['status'] != 'CONFIRMATORY_COMPLETE' or d['completed_geometry_pairs'] != 48 for d in data):
        raise ValueError('Figures require both complete accepted 48-pair analyses')
    unpacked = [unpack(d, b) for d, b in zip(data, ('FAST-LIO', 'Point-LIO'))]
    output.mkdir(parents=True, exist_ok=False)
    rows = [(f'{backend}\n{method}', triple[0], COLORS[b]) for b, (backend, methods) in enumerate(zip(('FAST-LIO', 'Point-LIO'), unpacked)) for method, triple in zip(METHODS, methods)]
    fig, axes = plt.subplots(2, 2, figsize=(12, 9), layout='constrained')
    fraction_plot(axes[0, 0], rows, 'initial_false_healthy_unconditional', 'Initial false-healthy events / initial intervals')
    fraction_plot(axes[0, 1], rows, 'recovery_detection_given_truth_recovered', 'Detected recoveries / truth-recovered events')
    for i, (_, summary, color) in enumerate(rows):
        delay = summary['detection_delay_median_s_detected_only']
        if delay is not None:
            axes[1, 0].bar(i, delay, color=color)
            axes[1, 0].text(i, delay, f'{delay:.2f}', ha='center', va='bottom')
        else:
            axes[1, 0].text(i, .05, 'No detections', rotation=90, ha='center')
        available = summary['decision_availability_primary_horizon']
        if available is not None:
            axes[1, 1].bar(i, 100*available, color=color)
            axes[1, 1].text(i, 100*available, f'{100*available:.1f}%', ha='center', va='bottom')
    for ax in axes[1]:
        ax.set(xticks=range(len(rows)), xticklabels=[r[0] for r in rows]);ax.tick_params(axis='x', labelrotation=20)
    axes[1, 0].set(title='Median delay among detected recoveries only', ylabel='Delay (s)')
    axes[1, 1].set(title='Available decision ticks / planned horizon ticks', ylabel='Ticks (%)', ylim=(0, 110))
    fig.suptitle('Final locked diagnostic transfer — separate backend truth labels', fontsize=15)
    fig.savefig(output/'final_operating_points.png', dpi=170);plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(12, 9), layout='constrained')
    for b, (backend, methods) in enumerate(zip(('FAST-LIO', 'Point-LIO'), unpacked)):
        for j, field in enumerate(('initial_false_healthy_unconditional', 'recovery_detection_given_truth_recovered')):
            ax = axes[b, j]
            for m, (_, _, strata) in enumerate(methods):
                for k, stratum in enumerate(STRATA):
                    value = strata[stratum]['event_proportion_intervals'][field]
                    if value['fraction'] is None:
                        continue
                    x = k + (-.12 if m == 0 else .12);v = 100*value['fraction']
                    lo, hi = np.asarray(value['wilson_95']) * 100
                    ax.errorbar(x, v, yerr=[[v-lo], [hi-v]], fmt=('o' if m == 0 else 's'), color=COLORS[m], capsize=3, label=METHODS[m] if k == 0 else None)
                    ax.annotate(f"{value['successes']}/{value['trials']}", (x, v), xytext=(0, 8 if m == 0 else -14), textcoords='offset points', ha='center', fontsize=8)
            ax.set(title=f"{backend}: {'initial false-healthy' if j == 0 else 'recovery detection'}", ylabel='Events (%)', ylim=(-8, 116), xticks=range(4), xticklabels=[s.removeprefix('TEST_').replace('_', '\n') for s in STRATA])
    fig.legend(handles=[Line2D([],[],marker=marker,color=color,linestyle='none',label=label) for marker,color,label in zip(('o','s'),COLORS,METHODS)],loc='outside lower center',ncol=2)
    fig.suptitle('Geometry groups: 12 planned pairs each; event Wilson 95% intervals', fontsize=14)
    fig.savefig(output/'final_stratum_events.png', dpi=170);plt.close(fig)

    fig, axes = plt.subplots(2, 1, figsize=(15, 7), layout='constrained')
    seeds_by_stratum = {s: sorted(t['seed'] for t in data[0]['truth_labels'] if t['stratum'] == s) for s in STRATA}
    seeds = [seed for s in STRATA for seed in seeds_by_stratum[s]]
    cmap = ListedColormap(('#eeeeee', '#246a9c', '#999999'))
    rowlabels = ['Truth recovery', 'Truth relapse', 'Scalar false-healthy', 'DCReg false-healthy', 'Scalar recovery detected', 'DCReg recovery detected']
    for ax, backend, d, methods in zip(axes, ('FAST-LIO', 'Point-LIO'), data, unpacked):
        truth = {t['seed']: t for t in d['truth_labels']}
        events = [{e['seed']: e for e in method[1]} for method in methods]
        matrix = np.zeros((6, 48))
        for col, seed in enumerate(seeds):
            t = truth[seed];recovered = t['onset_s'] is not None
            matrix[0, col] = int(recovered);matrix[1, col] = int(t['relapse_s'] is not None)
            initial_end = t['onset_s'] if recovered else t['deadline_s']
            for m in range(2):
                e = events[m][seed]
                matrix[2+m, col] = int(e['false_healthy_in_initial_unrecovered_interval']) if initial_end > t['exit_time_s'] else 2
                matrix[4+m, col] = int(e['detected_post_onset']) if recovered else 2
        ax.imshow(matrix, cmap=cmap, vmin=0, vmax=2, aspect='auto', interpolation='nearest')
        ax.set(title=backend, yticks=range(6), yticklabels=rowlabels, xticks=range(48), xticklabels=seeds)
        ax.tick_params(axis='x', labelrotation=90, labelsize=7)
        for boundary in (11.5, 23.5, 35.5):ax.axvline(boundary, color='black', lw=1)
    fig.legend(handles=[Patch(color='#246a9c', label='Observed event'), Patch(color='#eeeeee', label='No observed event'), Patch(color='#999999', label='No applicable interval / recovery')], loc='outside lower center', ncol=3)
    fig.suptitle('Every planned corridor event, grouped short/narrow, short/wide, long/narrow, long/wide', fontsize=13)
    fig.savefig(output/'final_event_ledger.png', dpi=170);plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), layout='constrained')
    for b, (backend, d) in enumerate(zip(('FAST-LIO', 'Point-LIO'), data)):
        paired = d['paired_interior_difference']
        if paired['status'] != 'AVAILABLE' or paired['bootstrap_replicates'] != 10000:
            raise ValueError('Missing frozen geometry bootstrap interval')
        value=paired['estimate'];lo, hi=paired['interval_95']
        axes[0].plot([lo,hi], [b,b], color=COLORS[b], lw=3)
        axes[0].plot(value,b,'o',color=COLORS[b])
        for k, stratum in enumerate(STRATA):
            axes[1].plot(k+(-.08 if b == 0 else .08),paired['stratum_means'][stratum], 'o', color=COLORS[b], label=backend if k == 0 else None)
    axes[0].set(yticks=(0,1), yticklabels=('FAST-LIO','Point-LIO'), xlabel='Corridor minus control error (m)', title='Mean paired effect: geometry bootstrap 95% interval')
    axes[0].axvline(0,color='grey',ls='--')
    axes[1].set(xticks=range(4), xticklabels=[s.removeprefix('TEST_').replace('_','\n') for s in STRATA], ylabel='Corridor minus control error (m)', title='Within-group means: 12 pairs each')
    axes[1].axhline(0,color='grey',ls='--');axes[1].legend()
    fig.suptitle('Interior local translation error: per-scene medians, paired by geometry', fontsize=14)
    fig.savefig(output/'final_paired_geometry_effect.png',dpi=170);plt.close(fig)
    manifest = {'evidence_scope': 'complete revised final cohort; backend-specific reference outcomes', 'sources': {str(p):digest(p) for p in (fast_path, point_path)}, 'plotter_sha256':digest(Path(__file__)), 'outputs': {p.name:digest(p) for p in output.glob('*.png')}, 'intervals': 'event Wilson 95%; paired-effect geometry bootstrap 95%, 10000 resamples within fixed strata', 'delay_scope': 'detected events only; does not assign delays to missed or non-recovered events'}
    (output/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('fast-analysis', 'point-analysis', 'output'):p.add_argument('--'+arg, type=Path, required=True)
    a = p.parse_args();plot(a.fast_analysis, a.point_analysis, a.output)
