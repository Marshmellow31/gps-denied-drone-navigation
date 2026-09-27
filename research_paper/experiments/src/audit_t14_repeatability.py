"""Quantify four retained development repeats without recalibrating on them."""

from __future__ import annotations

import argparse
from dataclasses import asdict, replace
import json
from pathlib import Path
import platform

import numpy as np

import audit_t14_batch as batch_audit
import t16_development_analysis as analysis


ROOT = analysis.ROOT
GENERATED = ROOT / "research_paper/experiments/generated"
METHODS = ("FASTLIO_MIN_EIG_G3", "DCREG_SCHUR_MASK")


def numerical_comparison(first: dict, second: dict) -> dict:
    """Compare finite values at exact shared timestamps; disclose missing keys."""
    shared = sorted(set(first) & set(second))
    available = [key for key in shared if first[key] is not None and second[key] is not None]
    a = [first[key] for key in available]
    b = [second[key] for key in available]
    differences = np.asarray(b, dtype=float) - np.asarray(a, dtype=float)
    if not all(np.isfinite(value) for value in list(first.values()) + list(second.values())
               if value is not None):
        raise ValueError("nonfinite available value in repeat comparison")
    return {
        "primary_rows": len(first), "repeat_rows": len(second),
        "shared_timestamps": len(shared), "jointly_available": len(available),
        "primary_only_timestamps": len(set(first) - set(second)),
        "repeat_only_timestamps": len(set(second) - set(first)),
        "availability_disagreements": sum((first[k] is None) != (second[k] is None)
                                         for k in shared),
        "primary_median_jointly_available": float(np.median(a)) if a else None,
        "repeat_median_jointly_available": float(np.median(b)) if b else None,
        "mean_signed_repeat_minus_primary": float(np.mean(differences)) if a else None,
        "median_absolute_change": float(np.median(np.abs(differences))) if a else None,
        "maximum_absolute_change": float(np.max(np.abs(differences))) if a else None,
    }


def load_repeat(primary: analysis.DevelopmentRun, repeat_dir: Path) -> analysis.DevelopmentRun:
    manifest = json.loads((repeat_dir / "run_manifest.json").read_text())
    expected = (primary.run_id if primary.seed == 14 else
                primary.run_id.removesuffix("P1") + "REPEAT1")
    if (primary.seed not in (14, 45) or manifest.get("run_id") != expected
            or manifest.get("seed") != primary.seed or manifest.get("scene") != primary.scene
            or manifest.get("status") != "COMPLETED"
            or manifest.get("route_profile") != analysis.PROFILE_ID
            or manifest.get("repeat") is not (primary.seed == 45)):
        raise ValueError("repeat does not match the declared development slot")
    parity = batch_audit._compare_replays(primary.run_manifest, manifest)
    for key in ("same_full_input_fingerprint", "same_backend_fingerprint",
                "same_analysis_and_replay_sources_except_runner"):
        if parity[key] is not True:
            raise ValueError(f"repeat identity mismatch: {key}")
    batch_audit._verify_run_outputs(repeat_dir.parent, manifest)
    poses = analysis.trajectory.load_estimates(repeat_dir / "stream/poses.csv", "simulation_epoch")
    windows, truth_ok, truth_reason = analysis.build_primary_windows(
        poses, primary.reference, primary.body_transform, primary.exit_time_s)
    label = None if primary.control else analysis.find_recovery(
        windows, primary.exit_time_s, truth_eligible=truth_ok, truth_reason=truth_reason)
    diagnostics = analysis._read_diagnostics(repeat_dir, poses)
    decisions = {method: analysis.associate_decision_ticks(rows, poses)
                 for method, rows in diagnostics.items()}
    return replace(primary, run_id=expected, run_dir=repeat_dir, run_manifest=manifest,
                   poses=poses, windows=windows, label=label, diagnostics=diagnostics,
                   decisions=decisions,
                   evaluation_rows=analysis._read_csv(repeat_dir / "stream/evaluation.csv"))


def _errors(run, column):
    rows = [row for row in run.evaluation_rows if float(row["window_s"]) == 1.0]
    keys = [int(row["timestamp_ns"]) for row in rows]
    if len(set(keys)) != len(keys):
        raise ValueError("duplicate evaluation timestamps")
    return {key: float(row[column]) if row["local_valid"].lower() == "true" else None
            for key, row in zip(keys, rows)}


def decision_comparison(primary, repeat, method, threshold):
    left, right = primary.decisions[method], repeat.decisions[method]
    if [d.timestamp_ns for d in left] != [d.timestamp_ns for d in right]:
        raise ValueError("repeat decision grids differ")
    a, a_transitions, _ = analysis.debounce(left, method, threshold)
    b, b_transitions, _ = analysis.debounce(right, method, threshold)
    joint = np.asarray([x.available and y.available for x, y in zip(left, right)])
    def raw(rows):
        return np.asarray([(d.available and d.score is not None and d.score >= threshold)
                           if method == METHODS[0] else
                           (d.available and d.fixed_healthy is True) for d in rows])
    scores = numerical_comparison(
        {d.timestamp_ns: d.score if d.available else None for d in left},
        {d.timestamp_ns: d.score if d.available else None for d in right})
    result = {"score_comparison_full_run": scores, "planned_ticks": len(left),
              "jointly_available_ticks": int(joint.sum()),
              "raw_healthy_disagreements_jointly_available": int(np.count_nonzero((raw(left) != raw(right)) & joint)),
              "confirmed_state_disagreements_jointly_available": int(np.count_nonzero((a != b) & joint)),
              "confirmed_state_disagreements_all_ticks": int(np.count_nonzero(a != b)),
              "primary_alarm_times_s": (np.flatnonzero(a_transitions) / 10).tolist(),
              "repeat_alarm_times_s": (np.flatnonzero(b_transitions) / 10).tolist()}
    if not primary.control:
        first = analysis.summarize_method([primary], method, threshold)[1][0]
        second = analysis.summarize_method([repeat], method, threshold)[1][0]
        result["primary_event"] = first
        result["repeat_event"] = second
        result["event_decision_agreement"] = {
            key: first[key] == second[key] for key in
            ("false_healthy_in_initial_unrecovered_interval", "detected_post_onset")}
    return result


def audit(batch_root: Path, prebatch_root: Path, provenance: Path, manifest_path: Path,
          reference_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("role") != "development_only" or manifest.get("heldout_inputs_opened") is not False:
        raise ValueError("repeat audit requires a development-only analysis")
    threshold = float(manifest["fastlio_threshold_selection"]["threshold"])
    shared_reference = provenance / "shared_reference.txt"
    if reference_path.name != "reference.txt":
        raise ValueError("reference alias must preserve the frozen metadata filename")
    reference_path.parent.mkdir(parents=True, exist_ok=True)
    if reference_path.exists() or reference_path.is_symlink():
        if not reference_path.is_file() or analysis.sha256_file(reference_path) != analysis.sha256_file(shared_reference):
            raise ValueError("existing audit reference alias has the wrong content")
    else:
        reference_path.symlink_to(shared_reference.resolve())
    reference = analysis.trajectory.load_reference(reference_path)
    runs = [analysis._load_run(batch_root / f"T14_DEV{seed:02d}_{scene}_XM6_P1",
                              provenance, reference_path, reference)
            for seed in analysis.SEEDS for scene in analysis.SCENES]
    repeats, comparisons = {}, []
    for primary in runs:
        if primary.seed not in (14, 45):
            continue
        repeat_dir = (prebatch_root / primary.run_id if primary.seed == 14 else
                      batch_root / (primary.run_id.removesuffix("P1") + "REPEAT1"))
        repeat = load_repeat(primary, repeat_dir)
        repeats[(primary.seed, primary.scene)] = repeat
        comparisons.append({
            "seed": primary.seed, "scene": primary.scene,
            "primary_manifest_path": str(primary.run_dir / "run_manifest.json"),
            "repeat_manifest_path": str(repeat_dir / "run_manifest.json"),
            "primary_manifest_sha256": analysis.sha256_file(primary.run_dir / "run_manifest.json"),
            "repeat_manifest_sha256": analysis.sha256_file(repeat_dir / "run_manifest.json"),
            "input_and_backend_parity": batch_audit._compare_replays(primary.run_manifest, repeat.run_manifest),
            "translation_error_1s_m": numerical_comparison(
                _errors(primary, "local_translation_error_m"), _errors(repeat, "local_translation_error_m")),
            "rotation_error_1s_rad": numerical_comparison(
                _errors(primary, "local_rotation_error_rad"), _errors(repeat, "local_rotation_error_rad")),
            "primary_recovery_label": asdict(primary.label) if primary.label else None,
            "repeat_recovery_label": asdict(repeat.label) if repeat.label else None,
            "recovery_label_agreement": primary.label == repeat.label if not primary.control else None,
            "methods": {method: decision_comparison(primary, repeat, method, threshold)
                        for method in METHODS},
        })
    baseline = analysis.interior_sample_size(runs)
    sensitivity = {}
    for seeds in ((14,), (45,), (14, 45)):
        replaced = [repeats[(run.seed, run.scene)] if run.seed in seeds else run for run in runs]
        changed = analysis.interior_sample_size(replaced)
        sensitivity["repeat_substitution_seeds_" + "_".join(map(str, seeds))] = changed
    return {
        "schema": "t14-repeatability-audit-v1", "role": "development_only",
        "heldout_inputs_opened": False, "threshold_recalibrated": False,
        "primary_outputs_replaced": False, "independent_additional_events": 0,
        "fastlio_fixed_candidate_threshold": threshold,
        "source_analysis_manifest_sha256": analysis.sha256_file(manifest_path),
        "source_hashes": {path.name: analysis.sha256_file(path) for path in
                          (Path(__file__), Path(analysis.__file__), Path(batch_audit.__file__))},
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "verified_primary_runs": len(runs), "verified_repeat_runs": len(comparisons),
        "comparisons": comparisons, "primary_interior_sample_size": baseline,
        "descriptive_interior_substitution_sensitivity": sensitivity,
        "interpretation": "Four same-input repeat comparisons only; substitution is sensitivity analysis, never threshold training or replacement of primary evidence. R3 must adjudicate seed-14 smoke substitution and variability.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-root", type=Path, default=GENERATED / "runs/T14_FORMAL_BATCH")
    parser.add_argument("--prebatch-root", type=Path, default=GENERATED / "runs/T14_PREBATCH_SMOKE")
    parser.add_argument("--provenance-root", type=Path, default=GENERATED / "t14_formal_input_provenance_v1")
    parser.add_argument("--analysis-manifest", type=Path, default=ROOT / "research_paper/evidence/t16_development_analysis_manifest.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.batch_root, args.prebatch_root, args.provenance_root, args.analysis_manifest,
                   args.output.parent / "reference.txt")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print(json.dumps({"verified_primary_runs": result["verified_primary_runs"],
                      "verified_repeat_runs": result["verified_repeat_runs"]}))


if __name__ == "__main__":
    main()
