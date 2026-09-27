"""Export descriptive T14 repeat-audit figures and their content hashes."""

import argparse
import hashlib
import json
from pathlib import Path
import platform

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(audit_path, output_dir):
    data = json.loads(audit_path.read_text())
    if data.get("role") != "development_only" or data.get("threshold_recalibrated") is not False:
        raise ValueError("figures require an unretuned development repeat audit")
    rows = data["comparisons"]
    labels = [f"Seed {row['seed']}\n{row['scene'].lower()}" for row in rows]
    x = np.arange(len(rows))
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = []

    def save(fig, name):
        fig.supxlabel("Four retained repeats from two development layouts; no new independent events or threshold tuning.",
                      fontsize=8)
        for extension in ("png", "pdf", "svg"):
            path = output_dir / f"{name}.{extension}"
            fig.savefig(path, dpi=220, bbox_inches="tight", metadata={"Creator": "plot_repeatability.py"})
            outputs.append(path)
        plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), layout="constrained")
    primary = [r["translation_error_1s_m"]["primary_median_jointly_available"] for r in rows]
    repeat = [r["translation_error_1s_m"]["repeat_median_jointly_available"] for r in rows]
    axes[0].bar(x-.18, primary, .36, label="Primary", color="#007175")
    axes[0].bar(x+.18, repeat, .36, label="Repeat", color="#884488")
    axes[0].set_ylabel("Median 1-second translation error (m)")
    axes[0].set_title("Whole-run medians: 587 valid windows each")
    axes[0].legend()
    changes = [r["translation_error_1s_m"]["maximum_absolute_change"] for r in rows]
    axes[1].bar(x, changes, color="#b06929")
    for i, value in enumerate(changes):
        axes[1].annotate(f"{value:.3f}", (i, value), xytext=(0, 4), textcoords="offset points", ha="center")
    axes[1].set_ylim(0, max(changes)*1.2)
    axes[1].set_ylabel("Largest aligned absolute error change (m)")
    axes[1].set_title("Same timestamps, different replay outputs")
    for axis in axes:
        axis.set_xticks(x, labels)
        axis.grid(axis="y", alpha=.2)
        axis.set_axisbelow(True)
    save(fig, "t14_repeat_motion_errors")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), layout="constrained")
    for axis, method, title in zip(axes, ("FASTLIO_MIN_EIG_G3", "DCREG_SCHUR_MASK"),
                                    ("FAST-LIO candidate cutoff", "DCReg fixed detector adaptation")):
        raw, confirmed = [], []
        for row in rows:
            values = row["methods"][method]
            denominator = values["jointly_available_ticks"]
            if not denominator:
                raise ValueError("no joint decision coverage for a repeat")
            raw.append(100*values["raw_healthy_disagreements_jointly_available"]/denominator)
            confirmed.append(100*values["confirmed_state_disagreements_jointly_available"]/denominator)
        axis.bar(x-.18, raw, .36, label="Raw healthy", color="#007175")
        axis.bar(x+.18, confirmed, .36, label="Confirmed healthy", color="#884488")
        axis.set_title(title)
        axis.set_ylabel("Disagreeing jointly available decision ticks (%)")
        axis.set_xticks(x, labels)
        axis.set_ylim(0, max(raw+confirmed+[1])*1.25)
        axis.grid(axis="y", alpha=.2)
        axis.set_axisbelow(True)
        axis.legend()
    save(fig, "t14_repeat_warning_disagreement")
    manifest = {
        "role": "development_only", "source_audit_sha256": sha(audit_path),
        "plot_script_sha256": sha(Path(__file__)),
        "python": platform.python_version(), "matplotlib": matplotlib.__version__, "numpy": np.__version__,
        "figures": {path.name: sha(path) for path in outputs},
        "note": "Rendering only; scientific values come from the frozen-environment audit JSON.",
    }
    (output_dir / "t14_repeat_figure_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    render(args.audit, args.output_dir)
