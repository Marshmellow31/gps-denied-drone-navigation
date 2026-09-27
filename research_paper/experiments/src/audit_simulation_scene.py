"""Scene-only surface-normal coverage; no backend/indicator/error inputs."""
import json
from pathlib import Path
import numpy as np
from simulate_lidar import (trajectory, scene, randomized_straight_scene,
                             raycast)


def coverage(t, control, surfaces=None):
    azimuth = np.repeat(np.arange(360) / 360 * 2 * np.pi, 16)
    elevation = np.tile(np.linspace(-15., 15., 16) * np.pi / 180., 360)
    directions = np.column_stack((np.cos(elevation) * np.cos(azimuth),
                                  np.cos(elevation) * np.sin(azimuth), np.sin(elevation)))
    p, r, _, _, _ = trajectory(t + np.repeat(np.arange(360) / 360 * .1, 16))
    world = np.einsum('nij,nj->ni', r, directions)
    surfaces = scene(control) if surfaces is None else surfaces
    distances = np.array([raycast(p, world, [surface]) for surface in surfaces])
    distances = np.where(np.isfinite(distances), distances, np.inf)
    visible = np.min(distances, axis=0) < np.inf
    nearest = np.argmin(distances, axis=0)
    axes = np.array([surface.axis for surface in surfaces])[nearest[visible]]
    counts = np.bincount(axes, minlength=3)
    return {'time_s': t, 'control': control, 'visible_rays': int(visible.sum()),
            'normal_axis_counts_xyz': counts.tolist(),
            'axial_normal_fraction': float(counts[0] / counts.sum())}


def audit_randomized_layout(layout_seed):
    degraded_surfaces, geometry = randomized_straight_scene(layout_seed, False)
    control_surfaces, _ = randomized_straight_scene(layout_seed, True)
    midpoint = (geometry['entry_time_s'] + geometry['exit_time_s']) / 2.
    post_exit = geometry['exit_time_s'] + 5.
    degraded = coverage(midpoint, False, degraded_surfaces)
    control = coverage(midpoint, True, control_surfaces)
    post = coverage(post_exit, False, degraded_surfaces)
    eligible = (degraded['axial_normal_fraction'] <= .10
                and control['axial_normal_fraction'] >= .15
                and post['axial_normal_fraction'] >= .20)
    return {'layout_seed': layout_seed, 'geometry': geometry,
            'midpoint_time_s': midpoint, 'degraded_midpoint': degraded,
            'control_midpoint': control, 'post_exit_plus5_s': post,
            'eligible_by_scene_only_rule': eligible,
            'rule': {'degraded_x_normal_max': .10,
                     'control_x_normal_min': .15,
                     'post_exit_x_normal_min': .20}}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--layout-family', choices=('fixed_v3', 'randomized_straight_dev'),
                        default='fixed_v3')
    parser.add_argument('--layout-seed', type=int)
    parser.add_argument('--layout-seeds', help='inclusive development seed range, e.g. 14-45')
    parser.add_argument('--output-json', type=Path)
    parser.add_argument('--require-eligible', action='store_true')
    args = parser.parse_args()
    if args.layout_family == 'fixed_v3':
        if args.layout_seed is not None or args.layout_seeds is not None:
            parser.error('layout seeds apply only to randomized_straight_dev')
        result = [coverage(t, control) for control in (False, True)
                  for t in (5., 12., 17., 22., 27., 30.)]
    else:
        if (args.layout_seed is None) == (args.layout_seeds is None):
            parser.error('provide exactly one of --layout-seed or --layout-seeds')
        if args.layout_seed is not None:
            result = audit_randomized_layout(args.layout_seed)
        else:
            try:
                low, high = (int(value) for value in args.layout_seeds.split('-', 1))
            except (ValueError, TypeError):
                parser.error('--layout-seeds must be an inclusive range such as 14-45')
            if low > high:
                parser.error('--layout-seeds range must be ascending')
            result = [audit_randomized_layout(seed) for seed in range(low, high + 1)]
    serialized = json.dumps(result, indent=2) + '\n'
    if args.output_json:
        if args.output_json.exists():
            raise FileExistsError(args.output_json)
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(serialized, encoding='utf-8')
    else:
        print(serialized, end='')
    if args.require_eligible and args.layout_family != 'fixed_v3' \
            and any(not row['eligible_by_scene_only_rule']
                    for row in (result if isinstance(result, list) else [result])):
        raise SystemExit('layout failed the predeclared scene-only eligibility rule')
