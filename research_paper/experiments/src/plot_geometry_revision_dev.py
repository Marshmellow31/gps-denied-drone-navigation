"""Plot the development-only geometry repair audit; never read final results."""
import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['svg.hashsalt'] = 'geometry_revision_development_v1'
import matplotlib.pyplot as plt
import numpy as np

from geometry_revision_dev import control_positions


def plot(audit_path: Path, output: Path):
    audit = json.loads(audit_path.read_text())
    if audit['role'] != 'development' or audit['final_geometry_sampled']:
        raise ValueError('only the development audit is supported')
    output.mkdir(parents=True, exist_ok=False)
    fig = plt.figure(figsize=(11, 7), layout='constrained')
    grid = fig.add_gridspec(2, 2, height_ratios=[1, 1.4])
    for i, (title, positions) in enumerate([
        ('Original: 4 baffles; gaps = 3.3 m', [16.5 * k / 5 for k in range(1, 5)]),
        ('Candidate: 8 baffles; gaps = 1.83 m', control_positions(16.5))]):
        ax = fig.add_subplot(grid[0, i])
        ax.plot([0, 16.5], [1.4, 1.4], color='black')
        ax.plot([0, 16.5], [-1.4, -1.4], color='black')
        for x in positions:
            ax.plot([x, x], [.65 * 1.4, 1.4], color='#e28413', linewidth=3)
        ax.plot([0, 16.5], [0, 0], '--', color='#246a9c', label='Central route')
        ax.set(title=title, xlabel='Corridor x (m)', ylabel='y (m)', ylim=(-1.8, 1.8))
        ax.legend(loc='lower right', fontsize=8)
    ax = fig.add_subplot(grid[1, :])
    groups = list(audit['summary'])
    old = [audit['summary'][g]['original_eligible'] for g in groups]
    new = [audit['summary'][g]['candidate_eligible'] for g in groups]
    x = np.arange(len(groups))
    for bars in [ax.bar(x - .18, old, .36, label='Original geometry', color='#777777'),
                 ax.bar(x + .18, new, .36, label='Candidate geometry', color='#246a9c')]:
        ax.bar_label(bars, padding=3)
    ax.axhline(12, color='#e28413', linestyle='--', label='Final target per group (12)')
    ax.set(xticks=x, xticklabels=[g.replace('_', ' / ') for g in groups],
           ylabel='Eligible development fixtures (out of 32)', ylim=(0, 37),
           title='Same 10% / 15% / 20% geometry eligibility criteria')
    ax.legend(loc='upper right', fontsize=9)
    fig.suptitle('Geometry repair candidate — development evidence only', fontsize=15)
    for ext in ('png', 'svg'):
        export = output / f'geometry_revision_development.{ext}'
        fig.savefig(export, dpi=170, metadata={'Date': None} if ext == 'svg' else None)
        if ext == 'svg':
            export.write_text('\n'.join(line.rstrip() for line in export.read_text().splitlines()) + '\n')
    plt.close(fig)
    manifest = {'role': 'development', 'final_result': False,
                'audit_path': str(audit_path),
                'audit_sha256': hashlib.sha256(audit_path.read_bytes()).hexdigest(),
                'plot_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'outputs': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted(output.iterdir())}}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    plot(args.audit, args.output)
