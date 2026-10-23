"""Development-only candidate for the failed geometry protocol.

No final seed sampling, ROS bag writer, or estimator runner is provided here.
The accepted heldout_simulation module remains unchanged until a new review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np

import heldout_simulation as original
from simulate_lidar import Surface

PROFILE = "R2_GEOMETRY_SPACING_CANDIDATE_V2"
MAX_CONTROL_SPACING_M = 2.0
DEVELOPMENT_SEEDS = range(14, 46)
DIMENSION_GRID = {
    "short_narrow": ((8., 9.), (1.3, 1.5)),
    "short_wide": ((8., 9.), (2.5, 3.)),
    "long_narrow": ((15., 18.), (1.3, 1.5)),
    "long_wide": ((15., 18.), (2.5, 3.)),
}


def control_positions(length_m: float) -> list[float]:
    if not math.isfinite(length_m) or length_m <= 0:
        raise ValueError("length must be finite and positive")
    count = max(4, math.ceil(length_m / MAX_CONTROL_SPACING_M) - 1)
    return [length_m * i / (count + 1) for i in range(1, count + 1)]


def build_candidate(length_m: float, half_width_m: float,
                    room_half_width_m: float, control: bool = False):
    if not all(math.isfinite(x) for x in (length_m, half_width_m, room_half_width_m)):
        raise ValueError("dimensions must be finite")
    base = original.build_straight_surfaces(
        length_m, half_width_m, room_half_width_m, False)
    if control:
        base += [Surface(0, x, ((.65 * half_width_m, half_width_m), (-1., 1.5)))
                 for x in control_positions(length_m)]
    return base


def audit_dimensions(length: float, width: float, room: float) -> dict:
    """Compare old/new controls on explicit development dimensions only."""
    midpoint = (10.5 + original.formal_route.formal_crossing_time_x(length)) / 2
    post_time = original.formal_route.formal_crossing_time_x(length) + 5
    base = build_candidate(length, width, room)
    degraded = original._scene_coverage(midpoint, False, base)["axial_normal_fraction"]
    post = original._scene_coverage(post_time, False, base)["axial_normal_fraction"]
    old = original._scene_coverage(midpoint, True, original.build_straight_surfaces(
        length, width, room, True))["axial_normal_fraction"]
    new = original._scene_coverage(midpoint, True, build_candidate(
        length, width, room, True))["axial_normal_fraction"]
    return {"length_m": length, "half_width_m": width, "room_half_width_m": room,
            "corridor_fraction": degraded, "post_exit_fraction": post,
            "original_control_fraction": old, "candidate_control_fraction": new,
            "candidate_control_positions_m": control_positions(length),
            "original_eligible": degraded <= .10 and old >= .15 and post >= .20,
            "candidate_eligible": degraded <= .10 and new >= .15 and post >= .20}


def development_audit() -> dict:
    rows = []
    # Fresh development fixtures: these are not old final layouts or future test IDs.
    for group, (length_bounds, width_bounds) in DIMENSION_GRID.items():
        for seed in DEVELOPMENT_SEEDS:
            rng = np.random.default_rng(np.random.SeedSequence([seed, 0x52324732]))
            row = audit_dimensions(float(rng.uniform(*length_bounds)),
                                   float(rng.uniform(*width_bounds)),
                                   float(rng.uniform(4.5, 7.5)))
            rows.append({"development_seed": seed, "dimension_group": group, **row})
    summary = {}
    for group in DIMENSION_GRID:
        subset = [r for r in rows if r["dimension_group"] == group]
        summary[group] = {"fixtures": len(subset),
                          "original_eligible": sum(r["original_eligible"] for r in subset),
                          "candidate_eligible": sum(r["candidate_eligible"] for r in subset),
                          "original_control_pass": sum(r["original_control_fraction"] >= .15 for r in subset),
                          "candidate_control_pass": sum(r["candidate_control_fraction"] >= .15 for r in subset)}
    sources = [Path(__file__), Path(original.__file__),
               Path(original.simulator.__file__), Path(original.formal_route.__file__),
               Path(__file__).with_name("audit_simulation_scene.py")]
    return {"schema": "geometry-revision-development-audit-v1", "role": "development",
            "status": "CANDIDATE_REQUIRES_NEW_R2_R3_REVIEW", "profile": PROFILE,
            "sensor_bags_generated": False, "lio_runs_executed": False,
            "final_geometry_sampled": False,
            "rule": {"corridor_max": .10, "control_min": .15, "post_exit_min": .20},
            "max_control_spacing_m": MAX_CONTROL_SPACING_M,
            "runtime": {"numpy": np.__version__, "python": __import__('platform').python_version()},
            "source_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            "summary": summary, "fixtures": rows}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = development_audit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["summary"], indent=2))
