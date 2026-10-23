"""Render the corrected development-only FAST-LIO/Point-LIO signal figure."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import t16_development_analysis as analysis

ROOT = Path(__file__).resolve().parents[3]
INPUT_DIR = ROOT / "research_paper/evidence/development_analysis_20261010"
OUTPUT_DIR = ROOT / "research_paper/figures/development_signal_comparison_20261010"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_points():
    fast_path = INPUT_DIR / "fastlio_development_manifest.json"
    point_path = INPUT_DIR / "pointlio_development_manifest.json"
    fast = json.loads(fast_path.read_text())
    point = json.loads(point_path.read_text())
    if fast["heldout_gate"] != "READY_FOR_R3_REVIEW" or fast["heldout_inputs_opened"]:
        raise ValueError("FAST-LIO input is not a sealed development-only analysis")
    if point["status"] != "DONE_DEVELOPMENT_ONLY" or point["heldout_inputs_opened"]:
        raise ValueError("Point-LIO input is not a sealed development-only analysis")
    definitions = [
        ("FAST-LIO", "FASTLIO_MIN_EIG_G3", fast["method_metrics"]["FASTLIO_MIN_EIG_G3"],
         f"G3 threshold {fast['fastlio_threshold_selection']['threshold']:.2f}", "#1565c0", "o"),
        ("FAST-LIO", "DCREG_SCHUR_MASK", fast["method_metrics"]["DCREG_SCHUR_MASK"],
         "fixed DCReg", "#1565c0", "s"),
        ("Point-LIO", "POINTLIO_MIN_EIG_G3", point["method_metrics"]["POINTLIO_MIN_EIG_G3"],
         f"G3 threshold {point['pointlio_threshold_selection']['threshold']:.2f}", "#c62828", "o"),
        ("Point-LIO", "POINTLIO_DCREG_SCHUR_MASK", point["method_metrics"]["POINTLIO_DCREG_SCHUR_MASK"],
         "fixed DCReg", "#c62828", "s"),
    ]
    rows = []
    for backend, method, metric, operating_point, color, marker in definitions:
        x = metric["false_healthy_event_rate_conditional"]
        x_interval = metric["false_healthy_event_wilson_95_conditional"]
        y = metric["recovery_sensitivity"]
        y_interval = analysis.wilson_interval(
            metric["detected_recovery_events"], metric["truth_recovered_events"])
        if x is None or x_interval is None or y is None or y_interval is None:
            raise ValueError(f"{method} has unavailable event-rate denominators")
        rows.append({
            "backend": backend, "method": method, "operating_point": operating_point,
            "false_healthy_events": metric["false_healthy_events"],
            "false_healthy_denominator": metric["false_healthy_conditional_denominator"],
            "false_healthy_rate": x, "false_healthy_wilson_95": x_interval,
            "recovered_events_detected": metric["detected_recovery_events"],
            "truth_recovered_denominator": metric["truth_recovered_events"],
            "recovery_sensitivity": y, "recovery_sensitivity_wilson_95": y_interval,
            "color": color, "marker": marker,
        })
    return rows, {"fast": fast_path, "point": point_path}


def render(output_dir: Path = OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    rows, sources = load_points()
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    label_offsets = {
        "FASTLIO_MIN_EIG_G3": (8, -28),
        "DCREG_SCHUR_MASK": (8, 8),
        "POINTLIO_MIN_EIG_G3": (8, 8),
        "POINTLIO_DCREG_SCHUR_MASK": (8, -28),
    }
    for row in rows:
        x0, x1 = row["false_healthy_wilson_95"]
        y0, y1 = row["recovery_sensitivity_wilson_95"]
        x, y = row["false_healthy_rate"], row["recovery_sensitivity"]
        ax.errorbar(x, y,
            xerr=[[x - x0], [x1 - x]], yerr=[[y - y0], [y1 - y]],
            fmt=row["marker"], color=row["color"], markersize=8, capsize=3,
            markeredgecolor="white", markeredgewidth=0.8, linewidth=1.2,
            label=f"{row['backend']} · {row['operating_point']}")
        annotation = (f"{row['recovered_events_detected']}/{row['truth_recovered_denominator']} detected; "
                      f"{row['false_healthy_events']}/{row['false_healthy_denominator']} false healthy")
        ax.annotate(annotation, (x, y), xytext=label_offsets[row["method"]],
                    textcoords="offset points", fontsize=7.7, color="#222222")
    ax.axvline(0.10, color="#777777", linestyle="--", linewidth=1,
               label="Frozen 10% development ceiling")
    ax.set_xlim(-0.025, 0.62)
    ax.set_ylim(-0.05, 1.06)
    ax.set_xlabel("Initial false-healthy event rate (conditional denominator)")
    ax.set_ylabel("Recovery detection sensitivity among truth-recovered events")
    ax.set_title("Development-only operating points across 32 simulated corridor scenes")
    ax.grid(True, alpha=0.22)
    ax.legend(loc="lower left", fontsize=8, frameon=True, ncol=1)
    fig.text(0.01, 0.01,
        "Each threshold was fitted on that backend's own 32 corridor events; controls were excluded. "
        "Point-LIO and FAST-LIO recovery labels come from their own pose streams. "
        "Bars show 95% Wilson intervals; dots are development results, not final-test estimates.",
        ha="left", va="bottom", fontsize=7.6, wrap=True)
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    outputs = {}
    for suffix, kwargs in (("png", {"dpi": 240}), ("pdf", {}), ("svg", {})):
        path = output_dir / f"development_signal_comparison.{suffix}"
        fig.savefig(path, bbox_inches="tight", **kwargs)
        outputs[path.name] = sha256(path)
    plt.close(fig)
    source_script = Path(__file__).resolve()
    manifest = {
        "schema": "development-signal-figure-v1",
        "role": "development_only",
        "heldout_inputs_opened": False,
        "independent_unit": "corridor geometry event",
        "event_count_per_backend": 32,
        "uncertainty": "two-sided 95% Wilson intervals at event level",
        "figure_data": rows,
        "inputs": {label: {"path": str(path), "sha256": sha256(path)}
                   for label, path in sources.items()},
        "script": {"path": str(source_script), "sha256": sha256(source_script)},
        "runtime": {"python": platform.python_version(), "matplotlib": matplotlib.__version__},
        "outputs": outputs,
    }
    path = output_dir / "figure_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()
    result = render(args.output_dir)
    print(json.dumps({"outputs": result["outputs"], "heldout_inputs_opened": False}))


if __name__ == "__main__":
    main()
