from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np

from .pipeline import run_simulation
from .terrain import SCENARIOS


def _json_ready(result: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if key != "arrays"}


def _save_arrays(output_dir: Path, result: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output_dir / "layers.npz", **result["arrays"])
    (output_dir / "manifest.json").write_text(json.dumps(_json_ready(result), indent=2), encoding="utf-8")


def _plot(output_dir: Path, result: dict[str, Any]) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as error:
        raise SystemExit("Plotting requires: pip install -e .[plot]") from error

    arrays = result["arrays"]
    figure, axes = plt.subplots(2, 3, figsize=(12, 8), constrained_layout=True)
    items = (
        ("Ground-truth terrain (m)", arrays["terrain"], "terrain"),
        ("Simulated ToF observation (m)", arrays["observation"], "terrain"),
        ("Observation confidence", arrays["confidence"], "viridis"),
        ("Estimated slope (deg)", arrays["slope_deg"], "magma"),
        ("Truth-safe centers", arrays["truth_safe"], "gray"),
        ("Predicted-safe centers", arrays["predicted_safe"], "gray"),
    )
    for axis, (title, data, cmap) in zip(axes.flat, items, strict=True):
        image = axis.imshow(data, origin="lower", cmap=cmap)
        axis.set_title(title)
        figure.colorbar(image, ax=axis, fraction=0.046)
    selected = result["selected"]
    if selected:
        axes[1, 2].plot(selected["col"], selected["row"], "r*", markersize=14)
    figure.suptitle(f"{result['scenario']} / seed {result['seed']}")
    figure.savefig(output_dir / "diagnostic.png", dpi=150)
    plt.close(figure)


def command_run(args: argparse.Namespace) -> int:
    result = run_simulation(args.scenario, args.seed)
    output_dir = Path(args.output)
    _save_arrays(output_dir, result)
    if args.plot:
        _plot(output_dir, result)
    print(json.dumps(_json_ready(result), indent=2))
    return 0


def command_benchmark(args: argparse.Namespace) -> int:
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        for seed in range(args.seed_start, args.seed_start + args.seeds):
            result = run_simulation(scenario, seed)
            record = {"scenario": scenario, "seed": seed, **result["metrics"]}
            records.append(record)

    fields = list(records[0])
    with (output_dir / "runs.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)

    finite_target_errors = [r["target_error_m"] for r in records if r["target_error_m"] not in (None, float("inf"))]
    safe_scene_records = [r for r in records if r["truth_safe_cells"] > 0]
    no_safe_scene_records = [r for r in records if r["truth_safe_cells"] == 0]
    produced_targets = [r for r in safe_scene_records if r["target_produced"]]
    predicted_safe_cells = sum(r["predicted_safe_cells"] for r in records)
    false_safe_cells = sum(r["false_positive_cells"] for r in records)
    true_safe_predictions = sum(r["true_positive_cells"] for r in records)
    summary = {
        "runs": len(records),
        "seed_start": args.seed_start,
        "seeds_per_scenario": args.seeds,
        "safe_scene_runs": len(safe_scene_records),
        "no_safe_scene_runs": len(no_safe_scene_records),
        "aggregate_precision": true_safe_predictions / predicted_safe_cells if predicted_safe_cells else 1.0,
        "aggregate_false_safe_rate": false_safe_cells / predicted_safe_cells if predicted_safe_cells else 0.0,
        "mean_safe_scene_recall": mean(r["recall"] for r in safe_scene_records),
        "target_availability_on_safe_scenes": len(produced_targets) / len(safe_scene_records),
        "target_validity_when_produced": mean(1.0 if r["target_is_truly_safe"] is True else 0.0 for r in produced_targets),
        "no_safe_scene_rejection_rate": mean(1.0 if not r["target_produced"] else 0.0 for r in no_safe_scene_records),
        "mean_target_error_m": mean(finite_target_errors) if finite_target_errors else None,
        "mean_runtime_ms": mean(r["runtime_ms"] for r in records),
        "p95_runtime_ms": float(np.percentile([r["runtime_ms"] for r in records], 95)),
        "max_peak_detector_memory_kib": max(r["peak_detector_memory_kib"] for r in records),
        "mean_coverage": mean(r["coverage"] for r in records),
        "mean_direct_measurement_coverage": mean(r["direct_measurement_coverage"] for r in records),
        "hardware_gate_note": "Desktop timing is indicative only; repeat on Raspberry Pi Zero 2 W before claiming deployment readiness.",
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Hardware-constrained landing-zone simulation")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("run", help="Run one deterministic scenario")
    run.add_argument("--scenario", choices=SCENARIOS, default="flat_obstacles")
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--output", default="results/generated/latest")
    run.add_argument("--plot", action="store_true")
    run.set_defaults(function=command_run)

    benchmark = subparsers.add_parser("benchmark", help="Run the five-family baseline")
    benchmark.add_argument("--seeds", type=int, default=5)
    benchmark.add_argument("--seed-start", type=int, default=0)
    benchmark.add_argument("--output", default="results/generated/baseline")
    benchmark.set_defaults(function=command_benchmark)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.function(args))


if __name__ == "__main__":
    raise SystemExit(main())
