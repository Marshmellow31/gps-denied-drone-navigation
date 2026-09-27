"""Summarize paired development seeds without treating frames as replicates."""
import argparse
import csv
import hashlib
import json
import statistics
from pathlib import Path


EPOCH_NS = 1_000_000_000_000
ROTATION_LIMIT_RAD = 5.0 * 3.141592653589793 / 180.0
BINS = {
    'pre_corridor': (5.0, 8.0),
    'corridor_interior': (14.0, 20.0),
    'post_corridor_extended': (28.0, 36.0),
}


def read_rows(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize_run(run_dir):
    errors = read_rows(run_dir / 'evaluation.csv')
    health = [row for row in read_rows(run_dir / 'health.csv')
              if row['lever_scale_m'] == '3' and row['valid'] == 'true']
    result = {}
    for bin_name, (low, high) in BINS.items():
        event_errors = [row for row in errors
                        if low <= (int(row['timestamp_ns']) - EPOCH_NS) / 1e9 < high]
        event_health = [row for row in health
                        if low <= (int(row['timestamp_ns']) - EPOCH_NS) / 1e9 < high]
        by_window = {}
        for duration in ('1.0', '3.0'):
            rows = [row for row in event_errors if row['window_s'] == duration]
            valid = [row for row in rows if row['local_valid'] == 'true']
            passing = []
            for row in valid:
                if duration == '1.0':
                    trans = float(row['local_translation_error_m'])
                    rot = float(row['local_rotation_error_rad'])
                else:
                    trans = float(row['local_translation_error_rate_mps'])
                    rot = float(row['local_rotation_error_rate_radps'])
                passing.append(trans <= .2 and rot <= ROTATION_LIMIT_RAD)
            by_window[duration] = {
                'planned': len(rows),
                'valid': len(valid),
                'joint_pass_count': sum(passing),
                'joint_pass_fraction': sum(passing) / len(passing) if passing else None,
                'translation_median': statistics.median(
                    float(row['local_translation_error_m']) for row in valid) if valid else None,
                'rotation_median_rad': statistics.median(
                    float(row['local_rotation_error_rad']) for row in valid) if valid else None,
            }
        eigenvalues = [float(row['eigenvalue_0']) for row in event_health]
        result[bin_name] = {
            'windows': by_window,
            'valid_health_rows_scale3': len(event_health),
            'eigenvalue_min_median_scale3': statistics.median(eigenvalues) if eigenvalues else None,
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-root', type=Path,
                        default=Path('research_paper/experiments/generated/runs'))
    parser.add_argument('--seeds', default='10,11,12,13')
    parser.add_argument('--output-json', type=Path)
    args = parser.parse_args()
    seeds = [int(value) for value in args.seeds.split(',')]
    runs = {}
    artifacts = {}
    for seed in seeds:
        for scene in ('corridor', 'control'):
            run_dir = args.runs_root / f'SIM40_v3_seed{seed}_{scene}'
            if seed == 10:
                run_dir = args.runs_root / f'SIM40_v3_{scene}'
            if not (run_dir / 'evaluation.csv').is_file() or not (run_dir / 'health.csv').is_file():
                raise FileNotFoundError(f'missing audited run outputs: {run_dir}')
            runs[f'{seed}:{scene}'] = summarize_run(run_dir)
            input_name = f'sim-recovery-{"control" if scene == "control" else "dev"}{seed}-v3'
            input_dir = Path('research_paper/experiments/generated/simulation_bootstrap') / input_name
            input_manifest = input_dir / 'manifest.json'
            if not input_manifest.is_file():
                raise FileNotFoundError(f'missing generator manifest: {input_manifest}')
            generated = json.loads(input_manifest.read_text(encoding='utf-8'))
            artifacts[f'{seed}:{scene}'] = {
                'input_directory': str(input_dir),
                'input_manifest_sha256': sha256(input_manifest),
                'sensor_bag_sha256': generated['sensors.bag']['sha256'],
                'reference_sha256': generated['reference.txt']['sha256'],
                'output_directory': str(run_dir),
                'pose_sha256': sha256(run_dir / 'poses.csv'),
                'health_sha256': sha256(run_dir / 'health.csv'),
                'evaluation_sha256': sha256(run_dir / 'evaluation.csv'),
            }
    aggregates = {}
    for scene in ('corridor', 'control'):
        aggregates[scene] = {}
        for bin_name in BINS:
            aggregates[scene][bin_name] = {}
            eigenvalues = [runs[f'{seed}:{scene}'][bin_name]['eigenvalue_min_median_scale3']
                           for seed in seeds
                           if runs[f'{seed}:{scene}'][bin_name]['eigenvalue_min_median_scale3'] is not None]
            for duration in ('1.0', '3.0'):
                rows = [runs[f'{seed}:{scene}'][bin_name]['windows'][duration]
                        for seed in seeds]
                fractions = [row['joint_pass_fraction'] for row in rows
                             if row['joint_pass_fraction'] is not None]
                translation = [row['translation_median'] for row in rows
                               if row['translation_median'] is not None]
                rotation = [row['rotation_median_rad'] for row in rows
                            if row['rotation_median_rad'] is not None]
                aggregates[scene][bin_name][duration] = {
                    'seed_count': len(fractions),
                    'joint_pass_fraction_mean_across_seeds': statistics.mean(fractions) if fractions else None,
                    'joint_pass_fraction_sample_sd_across_seeds': statistics.stdev(fractions) if len(fractions) > 1 else None,
                    'joint_pass_fraction_min_across_seeds': min(fractions) if fractions else None,
                    'joint_pass_fraction_max_across_seeds': max(fractions) if fractions else None,
                    'translation_median_mean_across_seeds_m': statistics.mean(translation) if translation else None,
                    'translation_median_sample_sd_across_seeds_m': statistics.stdev(translation) if len(translation) > 1 else None,
                    'translation_median_min_across_seeds_m': min(translation) if translation else None,
                    'translation_median_max_across_seeds_m': max(translation) if translation else None,
                    'rotation_median_mean_across_seeds_rad': statistics.mean(rotation) if rotation else None,
                    'rotation_median_sample_sd_across_seeds_rad': statistics.stdev(rotation) if len(rotation) > 1 else None,
                    'eigenvalue_min_median_mean_across_seeds_scale3': statistics.mean(eigenvalues) if eigenvalues else None,
                    'eigenvalue_min_median_sample_sd_across_seeds_scale3': statistics.stdev(eigenvalues) if len(eigenvalues) > 1 else None,
                    'eigenvalue_min_median_min_across_seeds_scale3': min(eigenvalues) if eigenvalues else None,
                    'eigenvalue_min_median_max_across_seeds_scale3': max(eigenvalues) if eigenvalues else None,
                }
    paired_differences = {}
    for bin_name in BINS:
        paired_differences[bin_name] = {}
        for duration in ('1.0', '3.0'):
            differences = []
            eigen_differences = []
            for seed in seeds:
                corridor = runs[f'{seed}:corridor'][bin_name]['windows'][duration]['translation_median']
                control = runs[f'{seed}:control'][bin_name]['windows'][duration]['translation_median']
                if corridor is not None and control is not None:
                    differences.append(corridor - control)
                eigen_corridor = runs[f'{seed}:corridor'][bin_name]['eigenvalue_min_median_scale3']
                eigen_control = runs[f'{seed}:control'][bin_name]['eigenvalue_min_median_scale3']
                if eigen_corridor is not None and eigen_control is not None:
                    eigen_differences.append(eigen_corridor - eigen_control)
            paired_differences[bin_name][duration] = {
                'seed_count': len(differences),
                'mean_corridor_minus_control_translation_median_m': statistics.mean(differences) if differences else None,
                'sample_sd_corridor_minus_control_translation_median_m': statistics.stdev(differences) if len(differences) > 1 else None,
                'min_corridor_minus_control_translation_median_m': min(differences) if differences else None,
                'max_corridor_minus_control_translation_median_m': max(differences) if differences else None,
                'mean_corridor_minus_control_eigenvalue_min_median_scale3': statistics.mean(eigen_differences) if eigen_differences else None,
                'min_corridor_minus_control_eigenvalue_min_median_scale3': min(eigen_differences) if eigen_differences else None,
                'max_corridor_minus_control_eigenvalue_min_median_scale3': max(eigen_differences) if eigen_differences else None,
            }
    source_root = Path('research_paper/experiments/src')
    source_names = ('simulate_lidar.py', 'write_simulation_bag.py',
                    'audit_health_export.py', 'audit_paired_simulation_bags.py',
                    'trajectory_eval.py', 'summarize_simulation_seed_sensitivity.py')
    result = {'date': '2026-09-26', 'role': 'development_only',
              'seeds': seeds, 'bins': BINS,
              'success_limits': {'translation_1s_m': .2,
                                 'rotation_1s_deg': 5.0,
                                 'translation_3s_rate_mps': .2,
                                 'rotation_3s_rate_degps': 5.0},
              'run_summaries': runs,
              'artifact_hashes': artifacts,
              'source_hashes': {name: sha256(source_root / name) for name in source_names},
              'across_seed_descriptives': aggregates,
              'paired_translation_differences': paired_differences,
              'warning': 'Development pilot only. Frames/windows are summarized within each seed; the four seeds share one fixed layout and are not independent scene clusters.'}
    serialized = json.dumps(result, indent=2) + '\n'
    if args.output_json:
        if args.output_json.exists():
            raise FileExistsError(args.output_json)
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(serialized, encoding='utf-8')
    else:
        print(serialized, end='')


if __name__ == '__main__':
    main()
