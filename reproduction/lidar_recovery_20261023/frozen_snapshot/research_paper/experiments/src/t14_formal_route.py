"""T14 formal x=-6 m route adapter around the R2-frozen simulator.

The frozen simulator starts the body at x=-5 m. This adapter shifts only its
world-x origin by -1 m, leaving the sensor model, motion derivatives, surface
geometry and random streams unchanged. Use the named T14 profile for every
formal development input; never use it to generate held-out data.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from typing import Sequence

import numpy as np


PROFILE_ID = "T14_FORMAL_X_MINUS_6_V1"
PROFILE_START_X_M = -6.0
LEGACY_START_X_M = -5.0
FORMAL_X_SHIFT_M = PROFILE_START_X_M - LEGACY_START_X_M
FORMAL_DURATION_S = 60.0
DEVELOPMENT_SEEDS = range(14, 46)
SRC_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SRC_DIR))

import simulate_lidar as _sim  # noqa: E402

_BASE_TRAJECTORY = _sim.trajectory
_BASE_RANDOMIZED_SCENE = _sim.randomized_straight_scene


def formal_crossing_time_x(x_m: float) -> float:
    """Time the formal body path crosses world x, from the frozen ramp model."""
    return 3.0 + (6.0 + float(x_m)) / 0.8


def formal_trajectory(times):
    """Frozen trajectory translated to start at x=-6 m; derivatives unchanged."""
    position, rotation, quaternion, specific_force, gyro = _BASE_TRAJECTORY(times)
    position = position.copy()
    position[:, 0] += FORMAL_X_SHIFT_M
    return position, rotation, quaternion, specific_force, gyro


def formal_randomized_scene(layout_seed: int, control: bool = False):
    """Return a frozen randomized development layout with formal-route times."""
    surfaces, source_metadata = _BASE_RANDOMIZED_SCENE(layout_seed, control)
    metadata = dict(source_metadata)
    metadata["entry_time_s"] = formal_crossing_time_x(0.0)
    metadata["exit_time_s"] = formal_crossing_time_x(metadata["corridor_length_m"])
    metadata["vehicle_start_x_m"] = PROFILE_START_X_M
    metadata["route_profile"] = PROFILE_ID
    return surfaces, metadata


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _activate_formal_profile():
    """Install wrappers into the existing CLI modules for this process only."""
    _sim.trajectory = formal_trajectory
    _sim.crossing_time_x = formal_crossing_time_x
    _sim.randomized_straight_scene = formal_randomized_scene

    import write_simulation_bag as bag_writer
    bag_writer.trajectory = formal_trajectory
    bag_writer.crossing_time_x = formal_crossing_time_x
    bag_writer.randomized_straight_scene = formal_randomized_scene

    import audit_simulation_scene as scene_audit
    scene_audit.trajectory = formal_trajectory
    scene_audit.randomized_straight_scene = formal_randomized_scene
    return bag_writer, scene_audit


def _parse_seed_range(text: str) -> list[int]:
    try:
        low_text, high_text = text.split("-", 1)
        low, high = int(low_text), int(high_text)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("use an inclusive range such as 14-45") from exc
    if low > high or low not in DEVELOPMENT_SEEDS or high not in DEVELOPMENT_SEEDS:
        raise argparse.ArgumentTypeError("T14 is restricted to development seeds 14-45")
    return list(range(low, high + 1))


def _screen(args) -> dict[str, object]:
    _, scene_audit = _activate_formal_profile()
    rows = [scene_audit.audit_randomized_layout(seed) for seed in args.seeds]
    return {
        "profile_id": PROFILE_ID,
        "role": "development_only",
        "vehicle_start_x_m": PROFILE_START_X_M,
        "duration_s": FORMAL_DURATION_S,
        "seed_range": [args.seeds[0], args.seeds[-1]],
        "eligible_count": sum(row["eligible_by_scene_only_rule"] for row in rows),
        "ineligible_seeds": [row["layout_seed"] for row in rows
                             if not row["eligible_by_scene_only_rule"]],
        "screen_source_sha256": _sha256(Path(scene_audit.__file__).resolve()),
        "route_adapter_sha256": _sha256(Path(__file__).resolve()),
        "frozen_simulator_sha256": _sha256(SRC_DIR / "simulate_lidar.py"),
        "results": rows,
    }


def _generate(args) -> dict[str, object]:
    bag_writer, _ = _activate_formal_profile()
    if args.seed not in DEVELOPMENT_SEEDS:
        raise ValueError("T14 generation is restricted to development seeds 14-45")
    if args.duration != FORMAL_DURATION_S:
        raise ValueError("the frozen T14 formal run duration is exactly 60 seconds")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{2,79}", args.run_id):
        raise ValueError("run_id must be 3-80 safe letters, digits, '_' or '-'")

    output_path = (args.output_root / args.run_id).resolve()
    if output_path.exists():
        raise FileExistsError(f"refusing to reuse existing run ID/path: {output_path}")
    writer_args = [
        "write_simulation_bag.py", "--output", str(output_path),
        "--duration", str(args.duration), "--seed", str(args.seed),
        "--layout-family", "randomized_straight_dev",
        "--layout-seed", str(args.seed),
    ]
    if args.control:
        writer_args.append("--control")

    previous_argv = sys.argv
    captured_output = io.StringIO()
    try:
        sys.argv = writer_args
        with contextlib.redirect_stdout(captured_output):
            bag_writer.main()
    finally:
        sys.argv = previous_argv

    manifest_path = output_path / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    geometry = manifest["scene_geometry"]
    expected_exit = formal_crossing_time_x(geometry["corridor_length_m"])
    if abs(geometry["entry_time_s"] - 10.5) > 1e-12:
        raise AssertionError("formal route entry must be at 10.5 seconds")
    if abs(geometry["exit_time_s"] - expected_exit) > 1e-12:
        raise AssertionError("formal route exit time does not match the frozen equation")
    manifest.update({
        "run_id": args.run_id,
        "route_profile": {
            "profile_id": PROFILE_ID,
            "vehicle_start_x_m": PROFILE_START_X_M,
            "corridor_entry_x_m": 0.0,
            "entry_time_s": 10.5,
            "exit_time_formula": "3 + (6 + corridor_length_m) / 0.8",
            "exit_time_s": expected_exit,
            "duration_s": FORMAL_DURATION_S,
            "world_x_translation_from_frozen_profile_m": FORMAL_X_SHIFT_M,
        },
        "route_adapter_sha256": _sha256(Path(__file__).resolve()),
        "frozen_simulator_sha256": _sha256(SRC_DIR / "simulate_lidar.py"),
        "frozen_bag_writer_sha256": _sha256(Path(bag_writer.__file__).resolve()),
        "frozen_scene_geometry_sha256": _sha256(Path(_sim.__file__).resolve()),
        "layout_seed_equals_sensor_seed": args.seed,
    })
    reference_metadata_path = output_path / "reference_metadata.json"
    reference_metadata = json.loads((
        REPOSITORY_ROOT / "research_paper/data/simulation_random_layout_reference_metadata.json"
    ).read_text(encoding="utf-8"))
    reference_metadata["source"]["sha256"] = manifest["reference.txt"]["sha256"]
    reference_metadata["route_profile"] = manifest["route_profile"]
    reference_metadata["event_annotation"] = {
        "entry_time_s": 10.5,
        "exit_time_s": expected_exit,
        "method": "analytic scene-plane crossing under the frozen formal route",
    }
    reference_metadata["limitations"].append(
        "formal x=-6 m development route; not physical reference data")
    reference_metadata_path.write_text(
        json.dumps(reference_metadata, indent=2) + "\n", encoding="utf-8")
    manifest["reference_metadata.json"] = {
        "size_bytes": reference_metadata_path.stat().st_size,
        "sha256": _sha256(reference_metadata_path),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    screen_parser = commands.add_parser("screen", help="run scene-only formal-route eligibility")
    screen_parser.add_argument("--seeds", type=_parse_seed_range, default=_parse_seed_range("14-45"))
    screen_parser.add_argument("--output-json", required=True, type=Path)
    screen_parser.add_argument("--require-all-eligible", action="store_true")

    generate_parser = commands.add_parser("generate", help="make one formal development-only input")
    generate_parser.add_argument("--run-id", required=True)
    generate_parser.add_argument("--output-root", required=True, type=Path)
    generate_parser.add_argument("--seed", required=True, type=int,
                                 help="same value is used for layout and sensor streams")
    generate_parser.add_argument("--duration", type=float, default=FORMAL_DURATION_S)
    generate_parser.add_argument("--control", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "screen":
        path = args.output_json
        if path.exists():
            raise FileExistsError(f"refusing to overwrite screen output: {path}")
        result = _screen(args)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({key: result[key] for key in (
            "profile_id", "seed_range", "eligible_count", "ineligible_seeds")},
            sort_keys=True))
        if args.require_all_eligible and result["ineligible_seeds"]:
            raise SystemExit("one or more formal development layouts failed the scene-only rule")
    else:
        result = _generate(args)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
