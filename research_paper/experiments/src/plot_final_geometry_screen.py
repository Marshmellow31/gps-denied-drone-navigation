"""Illustrate the fixed geometry screen; never read estimator outputs."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def plot(source, output):
    s = json.loads(source.read_text())
    if s['status'] != 'SCENE_SCREEN_PASS':
        raise ValueError('expected the accepted complete scene screen')
    output.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True, layout='constrained')
    groups = list(s['selected_seeds_by_stratum'])
    indices, labels = [], []
    rows = []
    for group in groups:
        block = [r for r in s['screened_layouts'] if r['stratum'] == group]
        start = len(rows);rows += block
        indices.append((start + len(rows) - 1)/2)
        labels.append(group.removeprefix('TEST_').replace('_',' / ').lower())
    for ax, (field, threshold, title) in zip(axes, [
        ('corridor_midpoint', .10, 'Corridor midpoint: at most 10%'),
        ('control_midpoint', .15, 'Control midpoint: at least 15%'),
        ('post_exit_plus5_s', .20, 'Five seconds after exit: at least 20%')]):
        for eligible, color, label in [(True, '#246a9c', 'Eligible (selected)'),
                                       (False, '#999999', 'Rejected')]:
            points = [(i,r[field]['axial_normal_fraction']) for i,r in enumerate(rows)
                      if r['eligible'] == eligible]
            ax.scatter([i for i,_ in points], [100*v for _,v in points],
                       s=30, color=color, label=label)
        ax.axhline(100*threshold, color='#e28413', linestyle='--')
        ax.set(ylabel='Axial-normal returns (%)', title=title)
        count = 0
        for group in groups[:-1]:
            count += sum(r['stratum'] == group for r in rows)
            ax.axvline(count-.5, color='#dddddd')
    axes[0].legend(loc='upper left', fontsize=9)
    axes[-1].set(xticks=indices, xticklabels=labels, xlabel='Candidates in fixed ascending order within each group')
    fig.suptitle('Final geometry screen: 48 selected from 64 checked — geometry only', fontsize=14)
    fig.savefig(output/'final_geometry_screen.png', dpi=170)
    plt.close(fig)
    manifest = {'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'plotter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'png_sha256': hashlib.sha256((output/'final_geometry_screen.png').read_bytes()).hexdigest(),
                'evidence_scope': 'geometry-only final selection; no estimator outcome'}
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--screen', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args();plot(a.screen,a.output)
