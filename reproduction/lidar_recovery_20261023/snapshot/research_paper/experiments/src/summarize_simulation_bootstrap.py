"""Descriptive development-only scene bins; no recovery classification."""
import argparse
import csv
import json
import statistics
from pathlib import Path

BINS = {'pre_corridor': (5., 8.), 'corridor_interior': (14., 20.),
        'post_corridor_extended': (28., 36.)}


def summarize(run):
    with (run / 'evaluation.csv').open(newline='') as stream:
        errors = list(csv.DictReader(stream))
    with (run / 'health.csv').open(newline='') as stream:
        health = [r for r in csv.DictReader(stream) if r['lever_scale_m'] == '3']
    result = {}
    for name, (low, high) in BINS.items():
        inside = lambda r: low <= (int(r['timestamp_ns']) - 1000000000000) / 1e9 < high
        item = {}
        for window in (1., 3.):
            rows = [r for r in errors if float(r['window_s']) == window and inside(r)]
            valid = [r for r in rows if r['local_valid'] == 'true']
            median = lambda key: statistics.median(float(r[key]) for r in valid) if valid else None
            item[str(window)] = {'planned': len(rows), 'local_valid': len(valid),
                                 'translation_median_m': median('local_translation_error_m'),
                                 'rotation_median_rad': median('local_rotation_error_rad')}
        h = [float(r['eigenvalue_0']) for r in health if inside(r) and r['valid'] == 'true']
        item['eigenvalue_min_median_scale3'] = statistics.median(h) if h else None
        result[name] = item
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    print(json.dumps(summarize(args.run), indent=2))
