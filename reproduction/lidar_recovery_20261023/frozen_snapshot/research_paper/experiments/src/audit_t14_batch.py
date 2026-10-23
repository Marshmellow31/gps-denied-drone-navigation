"""Audit T14 development-run completeness, hashes, pairing and repeats."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


PROFILE_ID = "T14_FORMAL_X_MINUS_6_V1"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare_output_hashes(first: dict[str, str], second: dict[str, str]) -> dict[str, Any]:
    shared = sorted(set(first) & set(second))
    changed = [name for name in shared if first[name] != second[name]]
    return {
        "common_artifacts": len(shared),
        "identical_artifacts": len(shared) - len(changed),
        "changed_artifacts": changed,
        "missing_from_first": sorted(set(second) - set(first)),
        "missing_from_second": sorted(set(first) - set(second)),
    }


def _run_manifest(run_root: Path, run_id: str) -> dict[str, Any]:
    path = run_root / run_id / "run_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if manifest.get("run_id") != run_id:
        raise ValueError(f"run ID mismatch in {path}")
    return manifest


def _verify_run_outputs(run_root: Path, manifest: dict[str, Any]) -> int:
    for relative, expected in manifest.get("outputs", {}).items():
        path = run_root / manifest["run_id"] / relative
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"output hash mismatch: {path}")
    return len(manifest.get("outputs", {}))


def _audit_input(input_root: Path, seed: int, scene: str) -> dict[str, Any]:
    control = scene == "CONTROL"
    input_id = f"T14_FORMAL_DEV{seed:02d}_{scene}_INPUT_XM6_V1"
    input_dir = input_root / input_id
    manifest = json.loads((input_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("role") != "development" or manifest.get("truth_in_sensor_bag") is not False:
        raise ValueError(f"invalid role/truth separation in {input_id}")
    if manifest.get("seed") != seed or manifest.get("layout_seed") != seed:
        raise ValueError(f"layout/sensor seed mismatch in {input_id}")
    if manifest.get("control") is not control:
        raise ValueError(f"corridor/control mismatch in {input_id}")
    route = manifest.get("route_profile", {})
    if (route.get("profile_id") != PROFILE_ID or route.get("vehicle_start_x_m") != -6.0
            or route.get("entry_time_s") != 10.5 or route.get("duration_s") != 60.0):
        raise ValueError(f"formal route mismatch in {input_id}")
    for filename in ("sensors.bag", "reference.txt", "reference_metadata.json"):
        recorded = manifest.get(filename, {}).get("sha256")
        path = input_dir / filename
        if not recorded or not path.is_file() or sha256(path) != recorded:
            raise ValueError(f"input hash mismatch: {path}")
    reference_metadata = json.loads((input_dir / "reference_metadata.json").read_text())
    if reference_metadata.get("source", {}).get("sha256") != sha256(input_dir / "reference.txt"):
        raise ValueError(f"reference body metadata does not match: {input_id}")
    return manifest


def _audit_resource_log(path: Path) -> int | None:
    if not path.is_file():
        return None
    match = re.search(r"Maximum resident set size \(kbytes\): (\d+)",
                      path.read_text(encoding="utf-8", errors="replace"))
    return int(match.group(1)) if match else None


def _compare_replays(first: dict[str, Any], second: dict[str, Any]) -> dict[str, Any]:
    first_sources = {k: v for k, v in first["fingerprint"]["sources"].items() if k != "runner"}
    second_sources = {k: v for k, v in second["fingerprint"]["sources"].items() if k != "runner"}
    artifacts = ("stream/poses.csv", "stream/health.csv", "stream/health.csv.hessian.csv",
                 "stream/dcreg.csv", "stream/evaluation.csv")
    return {
        "same_full_input_fingerprint": first["fingerprint"]["input_hashes"]
        == second["fingerprint"]["input_hashes"],
        "same_backend_fingerprint": first["fingerprint"]["backend"]
        == second["fingerprint"]["backend"],
        "same_analysis_and_replay_sources_except_runner": first_sources == second_sources,
        "runner_source_hash_equal": first["fingerprint"]["sources"]["runner"]
        == second["fingerprint"]["sources"]["runner"],
        "measurement_stream_hashes_equal": {
            artifact: first.get("outputs", {}).get(artifact)
            == second.get("outputs", {}).get(artifact)
            for artifact in artifacts
        },
        "output_hash_comparison": compare_output_hashes(first.get("outputs", {}),
                                                         second.get("outputs", {})),
    }


def audit_batch(run_root: Path, input_root: Path, prebatch_root: Path,
                screen_path: Path) -> dict[str, Any]:
    run_root, input_root = run_root.resolve(), input_root.resolve()
    batch = json.loads((run_root / "batch_summary.json").read_text(encoding="utf-8"))
    screen = json.loads(screen_path.read_text(encoding="utf-8"))
    if screen.get("profile_id") != PROFILE_ID or screen.get("eligible_count") != 32:
        raise ValueError("formal screen profile or eligible count mismatch")
    if screen.get("ineligible_seeds"):
        raise ValueError("formal screen has ineligible development seeds")

    primary_manifests = []
    verified_outputs = 0
    input_hashes: dict[int, dict[str, str]] = {}
    for seed in range(14, 46):
        scene_input_hashes = {}
        for scene in ("CORRIDOR", "CONTROL"):
            input_manifest = _audit_input(input_root, seed, scene)
            scene_input_hashes[scene] = input_manifest["sensors.bag"]["sha256"]
            run_id = f"T14_DEV{seed:02d}_{scene}_XM6_P1"
            manifest = _run_manifest(run_root, run_id)
            if manifest.get("status") != "COMPLETED":
                raise ValueError(f"primary replay did not complete: {run_id}")
            if manifest.get("sensor_bag_sha256") != scene_input_hashes[scene]:
                raise ValueError(f"run/input bag hash mismatch: {run_id}")
            if manifest.get("dcreg_summary", {}).get("valid") != 597:
                raise ValueError(f"unexpected DCReg availability: {run_id}")
            if manifest.get("evaluation_local_valid_rows") != 1154:
                raise ValueError(f"unexpected local-window availability: {run_id}")
            verified_outputs += _verify_run_outputs(run_root, manifest)
            primary_manifests.append(manifest)
        if scene_input_hashes["CORRIDOR"] == scene_input_hashes["CONTROL"]:
            raise ValueError(f"corridor/control LiDAR bags unexpectedly identical at seed {seed}")
        input_hashes[seed] = scene_input_hashes
        pair_path = input_root / "pair_audits" / f"T14_FORMAL_DEV{seed:02d}_PAIR.json"
        pair = json.loads(pair_path.read_text(encoding="utf-8"))
        if pair.get("paired_imu_identical") is not True:
            raise ValueError(f"matched IMU audit failed for seed {seed}")

    seed45_repeats = []
    verified_seed45_repeat_outputs = 0
    seed45_repeat_comparison = {}
    for scene in ("CORRIDOR", "CONTROL"):
        run_id = f"T14_DEV45_{scene}_XM6_REPEAT1"
        manifest = _run_manifest(run_root, run_id)
        primary = _run_manifest(run_root, f"T14_DEV45_{scene}_XM6_P1")
        if manifest.get("status") != "COMPLETED":
            raise ValueError(f"seed-45 repeat did not complete: {run_id}")
        if manifest.get("sensor_bag_sha256") != input_hashes[45][scene]:
            raise ValueError(f"seed-45 repeat input mismatch: {run_id}")
        verified_seed45_repeat_outputs += _verify_run_outputs(run_root, manifest)
        seed45_repeats.append(manifest)
        seed45_repeat_comparison[scene.lower()] = _compare_replays(primary, manifest)

    smoke_reconciliation = {}
    verified_smoke_outputs = 0
    for scene in ("CORRIDOR", "CONTROL"):
        smoke_id = f"T14_DEV14_{scene}_XM6_P1"
        smoke = _run_manifest(prebatch_root, smoke_id)
        primary = _run_manifest(run_root, smoke_id)
        if smoke.get("status") != "COMPLETED":
            raise ValueError(f"seed-14 smoke replay incomplete: {smoke_id}")
        verified_smoke_outputs += _verify_run_outputs(prebatch_root, smoke)
        if smoke.get("sensor_bag_sha256") != primary.get("sensor_bag_sha256"):
            raise ValueError(f"seed-14 smoke and primary input mismatch: {scene}")
        if smoke["fingerprint"]["input_hashes"] != primary["fingerprint"]["input_hashes"]:
            raise ValueError(f"seed-14 smoke and primary input fingerprints differ: {scene}")
        smoke_reconciliation[scene.lower()] = {
            "smoke_run_id": smoke_id,
            "primary_run_id": smoke_id,
            "same_sensor_bag_sha256": True,
            "same_full_input_fingerprint": True,
            "same_reference_sha256": smoke["reference_sha256"] == primary["reference_sha256"],
            **_compare_replays(smoke, primary),
        }

    ledger_path = run_root / "failure_ledger.csv"
    ledger = list(csv.DictReader(ledger_path.open(newline="", encoding="utf-8")))
    ledger_status_counts = dict(Counter(row["status"] for row in ledger))
    elapsed = [float(manifest["elapsed_s"]) for manifest in primary_manifests]
    rss = []
    for manifest in primary_manifests + seed45_repeats:
        rss_kib = _audit_resource_log(run_root / manifest["run_id"] / "resources.time.txt")
        if rss_kib is not None:
            rss.append(rss_kib)

    return {
        "schema": "t14-audit-summary-v1",
        "role": "development_only",
        "profile_id": PROFILE_ID,
        "screen_sha256": sha256(screen_path),
        "batch_summary_sha256": sha256(run_root / "batch_summary.json"),
        "batch_status_counts": batch.get("counts", {}),
        "scheduled_runs": batch.get("scheduled_primary_runs", 0)
        + batch.get("scheduled_repeat_runs", 0),
        "completed_primary_runs": len(primary_manifests),
        "verified_primary_output_files": verified_outputs,
        "verified_seed45_repeat_output_files": verified_seed45_repeat_outputs,
        "verified_prebatch_repeat_output_files": verified_smoke_outputs,
        "development_layout_clusters": 32,
        "scene_only_eligible_layouts": screen["eligible_count"],
        "paired_imu_audits_passed": 32,
        "mean_primary_replay_elapsed_s": statistics.mean(elapsed),
        "median_primary_replay_elapsed_s": statistics.median(elapsed),
        "mean_primary_dcreg_valid_rows": statistics.mean(
            m["dcreg_summary"]["valid"] for m in primary_manifests),
        "mean_primary_local_valid_rows": statistics.mean(
            m["evaluation_local_valid_rows"] for m in primary_manifests),
        "maximum_measured_run_rss_kib": max(rss) if rss else None,
        "seed45_repeat_runs_completed": len(seed45_repeats),
        "seed45_repeatability_comparison": seed45_repeat_comparison,
        "seed14_smoke_repeat_reconciliation": smoke_reconciliation,
        "failure_ledger_rows": len(ledger),
        "failure_ledger_status_counts": ledger_status_counts,
        "heldout_data_opened": False,
        "scientific_conclusion": "NOT_EVALUATED; T16 analysis and R3 remain",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--input-root", type=Path, required=True)
    parser.add_argument("--prebatch-root", type=Path, required=True)
    parser.add_argument("--screen-json", type=Path, required=True)
    parser.add_argument("--output-json", type=Path)
    args = parser.parse_args()
    result = audit_batch(args.run_root, args.input_root, args.prebatch_root, args.screen_json)
    serialized = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
