#!/usr/bin/env python3
"""Rebuild saved results in a NEW directory; never run native estimators."""
import argparse
import csv
import gzip
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent
SNAPSHOT = PACKAGE / 'frozen_snapshot'
SCRIPTS = SNAPSHOT / 'research_paper/experiments/src'
FINAL = Path('research_paper/evidence/final_geometry_v2_results_20261012')
FAILURE = Path('research_paper/evidence/final_failure_analysis_20261012')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify():
    inventory = json.loads((PACKAGE / 'SHA256SUMS.json').read_text())
    for name, expected in inventory.items():
        if sha(PACKAGE / name) != expected:
            raise ValueError('Package file changed: ' + name)
    print(f'Verified {len(inventory)} package files', flush=True)
    return len(inventory)


def rows(path):
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'rt', newline='') as stream:
        return list(csv.DictReader(stream))


def compare_windows(a, b):
    left, right = rows(a), rows(b)
    if len(left) != len(right):
        raise ValueError('Primary-window row count differs')
    changed, maximum = 0, 0.0
    for x, y in zip(left, right):
        if x.keys() != y.keys():
            raise ValueError('Primary-window columns differ')
        for key in x:
            if x[key] == y[key]:
                continue
            if key not in ('translation_error_m', 'rotation_error_rad'):
                raise ValueError('Non-error window field differs: ' + key)
            u, v = float(x[key]), float(y[key])
            if not math.isclose(u, v, rel_tol=1e-12, abs_tol=1e-12):
                raise ValueError('Window error differs beyond numerical tolerance')
            changed += 1
            maximum = max(maximum, abs(u - v))
    return {'match': True, 'comparison': 'Error values: rtol=1e-12, atol=1e-12; all other fields exact',
            'roundoff_differences': changed, 'max_absolute_difference': maximum}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--reanalyze-streams', action='store_true',
                        help='Also recompute labels/events from copied native pose/health streams')
    args = parser.parse_args()
    count = verify()
    if args.verify_only:
        return
    if args.output is None:
        parser.error('--output must name a new directory')
    out = args.output.resolve()
    if out == PACKAGE or PACKAGE in out.parents:
        parser.error('Choose output outside the package so its checksums remain valid')
    out.mkdir(parents=True, exist_ok=False)
    os.environ['MPLCONFIGDIR'] = str(out / 'matplotlib-cache')
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(SCRIPTS))
    table_dir = out / 'tables' / FINAL
    table_dir.mkdir(parents=True)
    for name in ('fastlio_analysis.json', 'pointlio_analysis.json'):
        shutil.copy2(SNAPSHOT / FINAL / name, table_dir / name)
    subprocess.run([sys.executable, '-B', str(SCRIPTS / 'write_final_geometry_report.py')],
                   cwd=out / 'tables', check=True)
    matches = {}
    for name in ('method_summary.csv', 'stratum_summary.csv',
                 'corridor_event_ledger.csv', 'RESULTS_REPORT.md'):
        matches[name] = sha(table_dir / name) == sha(SNAPSHOT / FINAL / name)
        if not matches[name]:
            raise ValueError('Regenerated report differs: ' + name)
    primary = importlib.import_module('plot_final_recovery_results')
    primary.plot(SNAPSHOT / FINAL / 'fastlio_analysis.json',
                 SNAPSHOT / FINAL / 'pointlio_analysis.json', out / 'primary_figures')
    # Add path aliases ONLY in a disposable transport copy of the manifest.
    # Every aliased source must match its original frozen SHA-256 first.
    diagnostic = out / 'diagnostic_transport'
    shutil.copytree(SNAPSHOT / FAILURE, diagnostic)
    manifest = json.loads((diagnostic / 'manifest.json').read_text())
    relocation = json.loads((PACKAGE / 'path_map.json').read_text())
    aliases = {}
    for original, digest in list(manifest['source_sha256'].items()):
        relative = Path(relocation[original])
        if relative.parts[0] == 'snapshot':
            relative = Path('frozen_snapshot', *relative.parts[1:])
        local = (PACKAGE / relative).resolve()
        if sha(local) != digest:
            raise ValueError('Relocated source mismatch: ' + original)
        aliases[str(local)] = digest
    shutil.copy2(diagnostic / 'manifest.json', diagnostic / 'manifest.original.json')
    manifest['source_sha256'].update(aliases)
    (diagnostic / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (diagnostic / 'relocation_receipt.json').write_text(json.dumps({
        'operation': 'Add local path aliases after verifying original source digests; no scientific field changed',
        'aliases': aliases}, indent=2) + '\n')
    failure_plotter = importlib.import_module('plot_final_failure_cases')
    failure_plotter.plot(diagnostic, out / 'failure_figures')
    report = {'package_files_verified': count, 'byte_identical_reports': matches,
              'primary_figures': len(list((out / 'primary_figures').glob('*.png'))),
              'failure_figures': len(list((out / 'failure_figures').glob('*.png'))),
              'native_estimators_executed': False, 'stream_reanalysis': 'NOT_REQUESTED'}
    if args.reanalyze_streams:
        analysis = importlib.import_module('analyze_final_failure_cases')
        original_load = analysis.load

        def relocated_load(receipt, base, sources, reference):
            relocated = dict(receipt)
            relocated['manifest_path'] = str(PACKAGE / relocation[receipt['manifest_path']])
            return original_load(relocated, base, sources, reference)

        analysis.load = relocated_load
        base = PACKAGE / 'native_streams/final_heldout_geometry_v2_20261012'
        try:
            analysis.analyze(base, out / 'stream_reanalysis')
        finally:
            analysis.load = original_load
        compared = {}
        original_manifest = json.loads((SNAPSHOT / FAILURE / 'manifest.json').read_text())
        for name in original_manifest['output_sha256']:
            a, b = SNAPSHOT / FAILURE / name, out / 'stream_reanalysis' / name
            if name == 'primary_windows.csv':
                compared[name] = compare_windows(a, b)
                continue
            if name.endswith('.csv.gz'):
                same = rows(a) == rows(b)  # gzip headers contain creation times
            else:
                same = a.read_bytes() == b.read_bytes()
            compared[name] = same
            if not same:
                raise ValueError('Recomputed stream result differs: ' + name)
        report['stream_reanalysis'] = compared
    import numpy
    import matplotlib
    report['environment'] = {'python': sys.version, 'numpy': numpy.__version__,
                             'matplotlib': matplotlib.__version__}
    (out / 'REPRODUCTION_REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
