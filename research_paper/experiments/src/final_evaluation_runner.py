"""R3-gated held-out screening and final FAST-LIO replay.

`plan` only reads the development sample-size result and frozen split table.
`screen` and `run` refuse to touch reserved held-out layouts until both the R3
review and implementation-freeze documents explicitly say PASS.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import heldout_simulation as heldout


ROOT = Path(__file__).resolve().parents[3]
T14_AUDIT = ROOT / "research_paper/evidence/t14_development_batch_manifest.json"
T14_REFERENCE_RUN = ROOT / "research_paper/experiments/generated/runs/T14_FORMAL_BATCH/T14_DEV14_CORRIDOR_XM6_P1/run_manifest.json"
CONFIG = ROOT / "research_paper/configs/fastlio_simulation_bootstrap.yaml"
RUN_SCRIPT = ROOT / "research_paper/experiments/run_simulation_smoke.sh"
POSE_LOGGER = ROOT / "research_paper/experiments/src/pose_logger.py"
HEALTH_AUDIT = ROOT / "research_paper/experiments/src/audit_health_export.py"
DCREG = ROOT / "research_paper/experiments/src/dcreg_schur.py"
EVALUATOR = ROOT / "research_paper/experiments/src/trajectory_eval.py"
PAIR_AUDIT = ROOT / "research_paper/experiments/src/audit_paired_simulation_bags.py"
P1_ID = "T14_DEV14_CORRIDOR_XM6_P1"
PROFILE_ID = heldout.PROFILE_ID
EXPECTED_BINARY_SHA256 = "4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792"
EXPECTED_UPSTREAM_COMMIT = "7cc4175de6f8ba2edf34bab02a42195b141027e9"
LOCKED_DEVELOPMENT_THRESHOLD = 166.16366016039856
T16_ANALYSIS_MANIFEST = ROOT / "research_paper/evidence/t16_development_analysis_manifest.json"
FINAL_PLAN = ROOT / "research_paper/evidence/FINAL_HELDOUT_PLAN.json"


class FinalEvaluationError(RuntimeError):
    pass


class RunIncompleteError(FinalEvaluationError):
    """The replay did not deliver the complete planned sensor/pose horizon."""


class RunInProgressError(FinalEvaluationError):
    """An authoritative live process prevents a concurrent replay."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def _read_tsv_or_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _require_r3_pass(review_path: Path, freeze_path: Path) -> dict[str, str]:
    if not review_path.is_file() or not freeze_path.is_file():
        raise FinalEvaluationError("R3 review and implementation freeze must both exist")
    review = review_path.read_text(encoding="utf-8")
    freeze = freeze_path.read_text(encoding="utf-8")
    pass_pattern = r"(?im)^\*\*Gate:\*\*\s*PASS\s*$"
    if not __import__("re").search(pass_pattern, review[:6000]):
        raise FinalEvaluationError("R3 report does not declare Gate: PASS near its start")
    if not __import__("re").search(pass_pattern, freeze[:6000]):
        raise FinalEvaluationError("implementation freeze does not declare Gate: PASS near its start")
    required = _r3_required_hashes(review_path)
    blocks = __import__("re").findall(r"```json\s*(.*?)```", freeze, __import__("re").DOTALL)
    try:
        bundles = [json.loads(block) for block in blocks]
    except ValueError as exc:
        raise FinalEvaluationError("implementation freeze inventory JSON is malformed") from exc
    matching = [bundle for bundle in bundles if isinstance(bundle, dict)
                and bundle.get("schema") == "r3-implementation-freeze-v1"]
    if len(matching) != 1 or matching[0].get("artifacts") != required:
        raise FinalEvaluationError("implementation freeze does not contain the exact current R3 artifact inventory")
    if matching[0].get("FASTLIO_MIN_EIG_G3_threshold") != LOCKED_DEVELOPMENT_THRESHOLD:
        raise FinalEvaluationError("implementation freeze does not lock the exact T16 threshold")
    return {"r3_review_sha256": sha256_file(review_path),
            "implementation_freeze_sha256": sha256_file(freeze_path),
            "reviewed_artifact_hashes": required}


def _r3_required_hashes(review_path: Path) -> dict[str, str]:
    artifacts = {
        "R3 review": review_path,
        "R2 freeze": ROOT / "research_paper/protocol/FREEZE.md",
        "R2 metrics": ROOT / "research_paper/protocol/METRICS.md",
        "split table": ROOT / "research_paper/data/SPLITS.csv",
        "FAST-LIO config": CONFIG,
        "T14 batch audit": ROOT / "research_paper/evidence/t14_development_batch_manifest.json",
        "T14 development report": ROOT / "research_paper/evidence/T14_DEVELOPMENT_BATCH.md",
        "T14 repeatability audit": ROOT / "research_paper/evidence/t14_repeatability_audit.json",
        "T14 repeatability report": ROOT / "research_paper/evidence/T14_REPEATABILITY_AUDIT.md",
        "T14 repeatability implementation": ROOT / "research_paper/experiments/src/audit_t14_repeatability.py",
        "T14 repeatability tests": ROOT / "research_paper/experiments/tests/test_audit_t14_repeatability.py",
        "T14 repeat figure manifest": ROOT / "research_paper/figures/t14_repeat_figure_manifest.json",
        "T15 smoke manifest": ROOT / "research_paper/evidence/t15_point_lio_smoke_manifest.json",
        "T16 report": ROOT / "research_paper/evidence/DEVELOPMENT_REPORT.md",
        "T16 analysis manifest": T16_ANALYSIS_MANIFEST,
        "final evaluation plan": FINAL_PLAN,
        "execution decisions": ROOT / "research_paper/execution/DECISIONS.md",
        "T16 analyzer": ROOT / "research_paper/experiments/src/t16_development_analysis.py",
        "T16 analyzer tests": ROOT / "research_paper/experiments/tests/test_t16_development_analysis.py",
        "held-out generator": Path(heldout.__file__).resolve(),
        "held-out generator tests": ROOT / "research_paper/experiments/tests/test_heldout_simulation.py",
        "final runner": Path(__file__).resolve(),
        "final runner tests": ROOT / "research_paper/experiments/tests/test_final_evaluation_runner.py",
        "final lifecycle tests": ROOT / "research_paper/experiments/tests/test_final_run_lifecycle.py",
        "final input preparation tests": ROOT / "research_paper/experiments/tests/test_final_input_preparation.py",
        "backend rebuild script": ROOT / "research_paper/experiments/restore_fastlio_workspace.sh",
        "backend CMake newline restoration": ROOT / "research_paper/experiments/patches/fast_lio_cmake_final_newline.patch",
        "development lifecycle validation script": ROOT / "research_paper/experiments/src/run_r3_development_validation.py",
        "development lifecycle validation report": ROOT / "research_paper/evidence/r3_development_validation.json",
        "T14 route adapter": ROOT / "research_paper/experiments/src/t14_formal_route.py",
        "simulator": ROOT / "research_paper/experiments/src/simulate_lidar.py",
        "trajectory evaluator": EVALUATOR,
        "health audit": HEALTH_AUDIT,
        "DCReg adapter": DCREG,
        "pair audit": PAIR_AUDIT,
        "pose logger": POSE_LOGGER,
        "FAST-LIO replay script": RUN_SCRIPT,
        "PCL17 backend patch": ROOT / "research_paper/experiments/patches/fast_lio_pcl17.patch",
        "T08 backend patch": ROOT / "research_paper/experiments/patches/fast_lio_health_diagnostic.patch",
        "T13 backend patch": ROOT / "research_paper/experiments/patches/fast_lio_hessian_sidecar.patch",
    }
    missing_paths = [name for name, path in artifacts.items() if not path.is_file()]
    if missing_paths:
        raise FinalEvaluationError("required implementation-freeze artifacts missing: "
                                   + ", ".join(missing_paths))
    result = {name: sha256_file(path) for name, path in artifacts.items()}
    result["FASTLIO_BINARY_SHA256"] = EXPECTED_BINARY_SHA256
    result["FASTLIO_UPSTREAM_COMMIT"] = EXPECTED_UPSTREAM_COMMIT
    return result


def _check_analysis_runtime() -> dict[str, str]:
    version = ".".join(map(str, sys.version_info[:3]))
    numpy_version = heldout.np.__version__
    if version != "3.12.14" or numpy_version != "2.5.3":
        raise FinalEvaluationError("final screen/run requires frozen Python 3.12.14 and NumPy 2.5.3")
    return {"python": version, "numpy": numpy_version, "python_executable": sys.executable}


def build_plan(analysis_path: Path, splits_path: Path) -> dict[str, Any]:
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    if (analysis.get("status") != "DONE"
            or analysis.get("role") != "development_only"
            or analysis.get("heldout_inputs_opened") is not False):
        raise FinalEvaluationError("T16 analysis is not a completed development-only manifest")
    n_test = int(analysis["sample_size"]["n_test_geometry_pairs"])
    if n_test < 48 or n_test > 80 or n_test % 4:
        raise FinalEvaluationError("frozen sample-size rule requires 48–80 pairs, divisible by four")
    per_stratum = n_test // 4
    rows = _read_tsv_or_csv(splits_path)
    test_rows = [row for row in rows if row.get("role") == "held_out"]
    by_name = {row["split_id"]: row for row in test_rows}
    plan_strata = []
    for stratum in heldout.STRATA:
        row = by_name.get(stratum)
        if row is None:
            raise FinalEvaluationError(f"frozen split table lacks {stratum}")
        low, high = int(row["seed_start"]), int(row["seed_end"])
        frozen = heldout.STRATA[stratum]
        if (low, high) != (frozen["seed_min"], frozen["seed_max"]):
            raise FinalEvaluationError(f"split table and held-out stratum bounds differ for {stratum}")
        plan_strata.append({
            "stratum": stratum, "seed_min": low, "seed_max": high,
            "target_eligible_geometry_pairs": per_stratum,
            "candidate_seeds_to_scene_screen_in_ascending_order": list(range(low, high + 1)),
            "length_m": list(frozen["length_m"]),
            "corridor_half_width_m": list(frozen["half_width_m"]),
        })
    return {
        "schema": "final-evaluation-plan-v1", "status": "PENDING_R3_SCENE_SCREEN",
        "role": "heldout", "heldout_inputs_generated": False,
        "heldout_geometry_screened": False, "final_batch_executed": False,
        "n_test_geometry_pairs": n_test, "stratum_count": 4,
        "geometry_pairs_per_stratum": per_stratum,
        "development_analysis_sha256": sha256_file(analysis_path),
        "splits_sha256": sha256_file(splits_path),
        "strata": plan_strata,
        "selection_rule": "After R3 PASS only: scene-screen candidates in ascending reserved-seed order; keep the lowest eligible IDs until each stratum reaches its target; if any stratum cannot reach target, stop and return to R2.",
    }


def screen_reserved_layouts(
    plan_path: Path, review_path: Path, freeze_path: Path,
) -> dict[str, Any]:
    gate_hashes = _require_r3_pass(review_path, freeze_path)
    runtime = _check_analysis_runtime()
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("status") != "PENDING_R3_SCENE_SCREEN":
        raise FinalEvaluationError("screening plan is not pending or has an unexpected role")
    if (sha256_file(plan_path) != sha256_file(FINAL_PLAN)
            or plan.get("development_analysis_sha256") != sha256_file(T16_ANALYSIS_MANIFEST)):
        raise FinalEvaluationError("plan is not the exact R3-reviewed T16 sample-size lineage")
    splits_path = ROOT / "research_paper/data/SPLITS.csv"
    if sha256_file(splits_path) != plan.get("splits_sha256"):
        raise FinalEvaluationError("the frozen split table changed after the no-data plan was made")
    if plan != build_plan(T16_ANALYSIS_MANIFEST, splits_path):
        raise FinalEvaluationError("screen plan differs from the frozen development-derived plan")
    results, selected_by_stratum = [], {}
    all_eligible = True
    for stratum_plan in plan["strata"]:
        name = stratum_plan["stratum"]
        target = int(stratum_plan["target_eligible_geometry_pairs"])
        bounds = heldout.STRATA[name]
        if (int(stratum_plan["seed_min"]) != bounds["seed_min"]
                or int(stratum_plan["seed_max"]) != bounds["seed_max"]
                or stratum_plan["candidate_seeds_to_scene_screen_in_ascending_order"]
                != list(range(bounds["seed_min"], bounds["seed_max"] + 1))):
            raise FinalEvaluationError(f"plan seed range/order changed for {name}")
        selected = []
        for seed in stratum_plan["candidate_seeds_to_scene_screen_in_ascending_order"]:
            audit = heldout.screen_layout(int(seed), name)
            results.append(audit)
            if audit["eligible"]:
                selected.append(int(seed))
            if len(selected) == target:
                break
        selected_by_stratum[name] = selected
        all_eligible &= len(selected) == target
    result = {
        "schema": "final-heldout-scene-screen-v1",
        "status": "SCENE_SCREEN_PASS" if all_eligible else "STOP_RETURN_TO_R2_INSUFFICIENT_ELIGIBLE_LAYOUTS",
        "role": "heldout", "plan_sha256": sha256_file(plan_path),
        "development_analysis_sha256": plan["development_analysis_sha256"],
        **gate_hashes,
        "analysis_runtime": runtime,
        "target_per_stratum": plan["geometry_pairs_per_stratum"],
        "selected_seeds_by_stratum": selected_by_stratum,
        "screened_layouts": results,
        "screen_runner_sha256": sha256_file(Path(__file__).resolve()),
        "heldout_generator_sha256": sha256_file(Path(heldout.__file__).resolve()),
        "sensor_bags_generated": False, "lio_runs_executed": False,
    }
    return result


def _check_backend(ros_env: Path, workspace: Path, binary_path: Path) -> dict[str, Any]:
    reference = json.loads(T14_REFERENCE_RUN.read_text(encoding="utf-8"))
    backend = reference["fingerprint"]["backend"]
    if backend.get("upstream_commit") != EXPECTED_UPSTREAM_COMMIT:
        raise FinalEvaluationError("T14 reference manifest has an unexpected FAST-LIO revision")
    binary_hash = sha256_file(binary_path)
    if binary_hash != backend.get("binary_sha256") or binary_hash != EXPECTED_BINARY_SHA256:
        raise FinalEvaluationError("final workspace FAST-LIO binary differs from R3-reviewed T14 binary")
    environment = subprocess.run(
        ["bash", "-c", 'export CONDA_PREFIX="$1"; export PATH="$1/bin:$PATH"; '
         'source "$1/etc/conda/activate.d/ros-noetic-catkin_activate.sh"; '
         'source "$2/devel/setup.bash"; rosrun --prefix /usr/bin/realpath fast_lio fastlio_mapping',
         "resolve-fastlio", str(ros_env), str(workspace)],
        capture_output=True, text=True, check=True, timeout=30)
    launched = Path(environment.stdout.strip()).resolve()
    if launched != binary_path.resolve() or sha256_file(launched) != binary_hash:
        raise FinalEvaluationError("rosrun would launch a different FAST-LIO executable")
    source = workspace / "src/fast_lio"
    revision = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    diff = subprocess.check_output(["git", "-C", str(source), "diff", "HEAD", "--binary"])
    if revision != EXPECTED_UPSTREAM_COMMIT or hashlib.sha256(diff).hexdigest() != backend["worktree_diff_sha256"]:
        raise FinalEvaluationError("restored FAST-LIO source differs from the T14 backend")
    history = ros_env / "conda-meta/history"
    if sha256_file(history) != reference["fingerprint"]["runtime"]["conda_history_sha256"]:
        raise FinalEvaluationError("ROS environment dependency history differs from the T14 environment")
    expected = reference["fingerprint"]["sources"]
    sources = {
        "config": CONFIG,
        "dcreg": DCREG,
        "health_audit": HEALTH_AUDIT,
        "pair_audit": PAIR_AUDIT,
        "pose_logger": POSE_LOGGER,
        "replay_script": RUN_SCRIPT,
        "route_adapter": ROOT / "research_paper/experiments/src/t14_formal_route.py",
        "simulator": ROOT / "research_paper/experiments/src/simulate_lidar.py",
        "trajectory_evaluator": EVALUATOR,
    }
    for key, path in sources.items():
        if sha256_file(path) != expected.get(key):
            raise FinalEvaluationError(f"frozen T14 source changed before final run: {key}")
    patch_files = {
        "pcl17_patch_sha256": ROOT / "research_paper/experiments/patches/fast_lio_pcl17.patch",
        "t08_patch_sha256": ROOT / "research_paper/experiments/patches/fast_lio_health_diagnostic.patch",
        "t13_patch_sha256": ROOT / "research_paper/experiments/patches/fast_lio_hessian_sidecar.patch",
    }
    for key, path in patch_files.items():
        if sha256_file(path) != backend.get(key):
            raise FinalEvaluationError(f"frozen FAST-LIO build patch changed before final run: {key}")
    return {
        "upstream_commit": backend["upstream_commit"],
        "binary_sha256": binary_hash,
        "launched_binary_path": str(launched),
        "worktree_diff_sha256": hashlib.sha256(diff).hexdigest(),
        "conda_history_sha256": sha256_file(history),
        "pcl17_patch_sha256": backend["pcl17_patch_sha256"],
        "t08_patch_sha256": backend["t08_patch_sha256"],
        "t13_patch_sha256": backend["t13_patch_sha256"],
        "configuration_sha256": sha256_file(CONFIG),
        "source_hashes": {key: sha256_file(path) for key, path in sources.items()},
        "ros_env": str(ros_env.resolve()), "workspace": str(workspace.resolve()),
    }


def _append_ledger(path: Path, row: dict[str, Any]) -> None:
    fields = ("run_id", "scheduled_run_id", "stratum", "seed", "scene", "attempt",
              "stage", "status", "reason", "bag_sha256", "started_utc_ns", "elapsed_s")
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in fields})


def _record_run_state(run_root: Path, run_dir: Path, base: dict[str, Any]) -> None:
    """Persist identity before work and append every stage/terminal transition."""
    _write_json(run_dir / "run_manifest.json", base)
    _append_ledger(run_root / "failure_ledger.csv", {
        key: base.get(key, "") for key in
        ("run_id", "scheduled_run_id", "stratum", "seed", "scene", "attempt",
         "stage", "status", "reason", "started_utc_ns", "elapsed_s")
    } | {"bag_sha256": base["fingerprint"]["sensor_bag_sha256"]})


def _process_identity(pid: int | None) -> str | None:
    if pid is None:
        return None
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        return fields[19] if fields[0] != "Z" else None
    except (OSError, IndexError):
        return None


def _postprocess_attempt(run_root: Path, run_dir: Path, base: dict[str, Any],
                         ros_env: Path, input_dir: Path) -> dict[str, Any]:
    stream_dir = run_dir / "stream"
    maximum = 2 if base["attempt"] == 1 else 1
    first = int(base.get("postprocess_attempt", 0)) + 1
    for post_attempt in range(first, maximum + 1):
        base.update(status="RUNNING", stage="POSTPROCESSING", reason="",
                    postprocess_attempt=post_attempt, postprocess_owner_pid=os.getpid(),
                    postprocess_owner_identity=_process_identity(os.getpid()))
        _record_run_state(run_root, run_dir, base)
        try:
            required = ("poses.csv", "health.csv", "health.csv.hessian.csv")
            if not all((stream_dir / name).is_file() for name in required):
                raise RunIncompleteError("successful wrapper is missing a required raw stream")
            commands = [
                [str(ros_env / "bin/python"), str(HEALTH_AUDIT), str(stream_dir / "health.csv")],
                [str(ros_env / "bin/python"), str(DCREG), "--hessian-csv",
                 str(stream_dir / "health.csv.hessian.csv"), "--health-csv",
                 str(stream_dir / "health.csv"), "--output-csv", str(stream_dir / "dcreg.csv")],
                [str(ros_env / "bin/python"), str(EVALUATOR), "--poses",
                 str(stream_dir / "poses.csv"), "--reference", str(input_dir / "reference.txt"),
                 "--output", str(stream_dir / "evaluation.csv"), "--run-id", base["scheduled_run_id"],
                 "--event-id", f"FINAL_GEOMETRY_EXIT_TEST_{base['seed']}",
                 "--body-transform-json", str(input_dir / "reference_metadata.json"),
                 "--entry-start-ns", str(1_010_500_000_000)],
            ]
            if base["role"] == "development":
                commands[-1].append("--development-only")
                event_index = commands[-1].index("--event-id") + 1
                commands[-1][event_index] = f"R3_DEVELOPMENT_SMOKE_EXIT_{base['seed']}"
            summaries = []
            for index, command in enumerate(commands):
                result = subprocess.run(command, cwd=ROOT, capture_output=True,
                                        text=True, timeout=180, check=False)
                log = run_dir / f"postprocess_{post_attempt}_{index}"
                log.with_suffix(".stdout.log").write_text(result.stdout)
                log.with_suffix(".stderr.log").write_text(result.stderr)
                result.check_returncode()
                summaries.append(json.loads(result.stdout))
            completion = validate_completed_streams(stream_dir, base["input_manifest"], *summaries)
            outputs = {str(path.relative_to(run_dir)): sha256_file(path)
                       for path in sorted(run_dir.rglob("*"))
                       if path.is_file() and path.name != "run_manifest.json"}
            base.update(status="COMPLETED", stage="FINISHED", reason="",
                        postprocess_summaries=summaries, completion_validation=completion,
                        outputs=outputs)
            _record_run_state(run_root, run_dir, base)
            return {"status": "COMPLETED", "run_id": base["run_id"],
                    "scheduled_run_id": base["scheduled_run_id"]}
        except RunIncompleteError as exc:
            base.update(status="INCOMPLETE_EXECUTION", stage="VALIDATION", reason=str(exc))
            _record_run_state(run_root, run_dir, base)
            return {"status": base["status"], "run_id": base["run_id"], "reason": str(exc)}
        except (OSError, ValueError, AssertionError, subprocess.SubprocessError) as exc:
            base.update(status="POSTPROCESSING_FAILED", stage="POSTPROCESSING", reason=str(exc)[:2000])
            _record_run_state(run_root, run_dir, base)
    if base["status"] == "RUNNING":
        base.update(status="POSTPROCESSING_FAILED", reason="postprocessing interrupted with its retry budget exhausted")
        _record_run_state(run_root, run_dir, base)
    return {"status": base["status"], "run_id": base["run_id"],
            "reason": base.get("reason", "postprocessing retry exhausted")}


def _live_postprocess_pid(stream_dir: Path) -> int | None:
    """Check actual processes before resuming an interrupted derived-output stage."""
    scripts = {str(path) for path in (HEALTH_AUDIT, DCREG, EVALUATOR)}
    targets = {str(stream_dir / name) for name in
               ("health.csv", "health.csv.hessian.csv", "poses.csv", "evaluation.csv", "dcreg.csv")}
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            args = set((entry / "cmdline").read_bytes().decode(errors="replace").split("\0"))
            if args & scripts and args & targets and _process_identity(int(entry.name)) is not None:
                return int(entry.name)
        except OSError:
            continue
    return None


def validate_completed_streams(
    stream_dir: Path, input_manifest: dict[str, Any],
    health_summary: dict[str, Any], dcreg_summary: dict[str, Any],
    evaluation_summary: dict[str, Any],
) -> dict[str, Any]:
    """Check replay completeness separately from estimator accuracy.

    Missing/invalid individual pose rows remain valid unavailable evidence.
    A partial sensor replay, truncated logger, or absent pose stream is an
    incomplete execution and must not be labeled non-recovery.
    """
    expected_scans = int(input_manifest.get("scans", 0))
    if expected_scans != 600:
        raise RunIncompleteError(f"expected 600 input scans, manifest has {expected_scans}")
    rosbag_log = stream_dir / "rosbag.log"
    if not rosbag_log.is_file() or "Done." not in rosbag_log.read_text(encoding="utf-8", errors="replace"):
        raise RunIncompleteError("rosbag playback did not record its normal completion marker")

    if int(health_summary.get("timestamp_groups", -1)) != expected_scans:
        raise RunIncompleteError(
            f"health stream covers {health_summary.get('timestamp_groups')} of {expected_scans} scans")
    row_counts = health_summary.get("row_counts", {})
    if sum(int(value) for value in row_counts.values()) != expected_scans * 3:
        raise RunIncompleteError("health stream does not account for all three lever-scale rows per scan")
    health_rows = _read_tsv_or_csv(stream_dir / "health.csv")
    scale3_rows = [row for row in health_rows if float(row["lever_scale_m"]) == 3.0]
    health_times = [int(row["timestamp_ns"]) for row in scale3_rows]
    if (len(scale3_rows) != expected_scans or len(set(health_times)) != expected_scans
            or min(health_times) > 1_000_200_000_000
            or max(health_times) < 1_059_800_000_000):
        raise RunIncompleteError("health timestamps do not cover all 600 scans across the 60-second horizon")
    if (int(dcreg_summary.get("rows", -1)) != expected_scans
            or int(dcreg_summary.get("valid", 0)) + int(dcreg_summary.get("unavailable", 0)) != expected_scans):
        raise RunIncompleteError("DCReg stream does not account for all 600 diagnostic updates")
    dcreg_rows = _read_tsv_or_csv(stream_dir / "dcreg.csv")
    dcreg_times = [int(row["timestamp_ns"]) for row in dcreg_rows]
    if (len(dcreg_rows) != expected_scans or len(set(dcreg_times)) != expected_scans
            or min(dcreg_times) > 1_000_200_000_000
            or max(dcreg_times) < 1_059_800_000_000):
        raise RunIncompleteError("DCReg timestamps do not cover the 60-second replay horizon")
    if dcreg_times != health_times:
        raise RunIncompleteError("DCReg timestamps do not match the delivered health groups")

    poses_path = stream_dir / "poses.csv"
    if not poses_path.is_file():
        raise RunIncompleteError("pose stream is missing")
    pose_rows = _read_tsv_or_csv(poses_path)
    if not pose_rows:
        raise RunIncompleteError("pose logger wrote only a header; no pose/reset records exist")
    if any(row.get("event") not in ("POSE", "RESET") for row in pose_rows):
        raise RunIncompleteError("pose stream has an unexpected event type")
    pose_times = [int(row["timestamp_ns"]) for row in pose_rows]
    for first, second in zip(pose_rows, pose_rows[1:]):
        if (first.get("segment_id") == second.get("segment_id")
                and int(second["timestamp_ns"]) < int(first["timestamp_ns"])):
            raise RunIncompleteError("pose timestamps decrease inside one estimator segment")
    pose_events = [row for row in pose_rows if row.get("event") == "POSE"]
    if not pose_events:
        raise RunIncompleteError("no pose message was recorded")
    first_ns = int(pose_events[0]["timestamp_ns"])
    last_ns = int(pose_events[-1]["timestamp_ns"])
    if first_ns > 1_001_000_000_000 or last_ns < 1_059_800_000_000:
        raise RunIncompleteError("pose stream does not span the required 60-second run horizon")

    pose_logger_log = stream_dir / "pose_logger.log"
    if not pose_logger_log.is_file():
        raise RunIncompleteError("pose logger shutdown/count record is missing")
    counter_line = next((line for line in pose_logger_log.read_text(
        encoding="utf-8", errors="replace").splitlines() if "pose logger counts:" in line), None)
    if counter_line is None:
        raise RunIncompleteError("pose logger did not record shutdown counts")
    try:
        counts = ast.literal_eval(counter_line.split("counts:", 1)[1].strip())
    except (ValueError, SyntaxError, IndexError) as exc:
        raise RunIncompleteError("pose logger shutdown counts are malformed") from exc
    if int(counts.get("valid", -1)) + int(counts.get("invalid", -1)) != len(pose_events):
        raise RunIncompleteError("pose logger counts disagree with the flushed pose CSV")
    if int(counts.get("resets", -1)) != sum(row["event"] == "RESET" for row in pose_rows):
        raise RunIncompleteError("pose logger reset count disagrees with the pose CSV")

    expected_evaluation_rows = len(pose_rows) * 2  # the evaluator emits 1 s and 3 s rows per record
    if (int(evaluation_summary.get("rows", -1)) != expected_evaluation_rows
            or int(evaluation_summary.get("reference_gaps", -1)) != 0
            or int(evaluation_summary.get("out_of_order_source_rows", -1)) != 0
            or evaluation_summary.get("body_transform_verified") is not True):
        raise RunIncompleteError("trajectory evaluation did not cover the flushed pose stream/reference")
    evaluation_rows = _read_tsv_or_csv(stream_dir / "evaluation.csv")
    if len(evaluation_rows) != expected_evaluation_rows:
        raise RunIncompleteError("evaluation CSV row count disagrees with its summary")
    return {
        "expected_lidar_scans": expected_scans,
        "health_groups": int(health_summary["timestamp_groups"]),
        "dcreg_rows": int(dcreg_summary["rows"]),
        "pose_records": len(pose_events),
        "valid_pose_records": int(counts["valid"]),
        "invalid_pose_records": int(counts["invalid"]),
        "reset_records": int(counts["resets"]),
        "first_pose_timestamp_ns": first_ns,
        "last_pose_timestamp_ns": last_ns,
        "evaluation_rows": len(evaluation_rows),
        "reference_gaps": int(evaluation_summary["reference_gaps"]),
        "completion_status": "FULL_INPUT_AND_POSE_LOGGER_HORIZON",
    }


def _run_scene(
    run_id: str, seed: int, stratum: str, scene: str, input_dir: Path,
    run_root: Path, ros_env: Path, workspace: Path, binary_hash: str,
    threshold: float, execution_identity: dict[str, Any],
) -> dict[str, Any]:
    bag_path = input_dir / "sensors.bag"
    input_manifest_path = input_dir / "manifest.json"
    metadata_path = input_dir / "reference_metadata.json"
    reference_path = input_dir / "reference.txt"
    input_manifest = json.loads(input_manifest_path.read_text(encoding="utf-8"))
    role = input_manifest.get("role")
    if role not in ("development", "heldout"):
        raise FinalEvaluationError("run input must explicitly declare development or heldout role")
    if role == "heldout" and not execution_identity.get("reviewed_artifact_hashes"):
        raise FinalEvaluationError("held-out replay requires the reviewed execution inventory")
    fingerprint = {
        "sensor_bag_sha256": sha256_file(bag_path),
        "input_manifest_sha256": sha256_file(input_manifest_path),
        "reference_metadata_sha256": sha256_file(metadata_path),
        "reference_sha256": sha256_file(reference_path),
        "configuration_sha256": sha256_file(CONFIG),
        "backend_binary_sha256": binary_hash,
        "threshold_from_development_manifest": threshold,
        "execution_identity": execution_identity,
    }
    last_result = None
    for attempt in (1, 2):
        attempt_id = run_id if attempt == 1 else f"{run_id}_TECHNICAL_RETRY1"
        run_dir = run_root / attempt_id
        if run_dir.exists():
            manifest_path = run_dir / "run_manifest.json"
            if manifest_path.is_file():
                cached = json.loads(manifest_path.read_text(encoding="utf-8"))
                identity_match = cached.get("fingerprint") == fingerprint
                all_match = identity_match and bool(cached.get("outputs"))
                all_match &= bool(cached.get("completion_validation"))
                for relative, expected in cached.get("outputs", {}).items():
                    path = run_dir / relative
                    all_match &= path.is_file() and sha256_file(path) == expected
                if all_match and cached.get("status") == "COMPLETED":
                    return {"status": "CACHED", "run_id": attempt_id,
                            "scheduled_run_id": run_id}
                if identity_match and (cached.get("status") in ("REPLAYED", "POSTPROCESSING_FAILED")
                                       or (cached.get("status") == "RUNNING" and cached.get("stage") == "POSTPROCESSING")):
                    if cached.get("status") == "RUNNING":
                        owner = cached.get("postprocess_owner_pid")
                        current_owner = _process_identity(owner)
                        live_owner = (owner != os.getpid() and current_owner is not None
                                      and current_owner == cached.get("postprocess_owner_identity"))
                        child = _live_postprocess_pid(run_dir / "stream")
                        if live_owner or child is not None:
                            return {"status": "IN_PROGRESS", "run_id": attempt_id,
                                    "reason": "recorded postprocessing owner or matching subprocess is confirmed live"}
                    last_result = _postprocess_attempt(run_root, run_dir, cached, ros_env, input_dir)
                    if last_result["status"] == "INCOMPLETE_EXECUTION" and attempt == 1:
                        continue
                    return last_result
                if identity_match and cached.get("status") == "RUNNING":
                    actual = _process_identity(cached.get("process_pid"))
                    if actual is not None and actual == cached.get("process_start_identity"):
                        return {"status": "IN_PROGRESS", "run_id": attempt_id,
                                "reason": "recorded replay process is still live"}
                    cached.update(status="INTERRUPTED_REPLAY", reason="recorded replay process is absent")
                    _record_run_state(run_root, run_dir, cached)
                if identity_match and cached.get("status") in (
                        "CRASHED", "INCOMPLETE_EXECUTION", "INTERRUPTED_REPLAY"):
                    last_result = {"status": cached["status"], "run_id": attempt_id,
                                   "reason": cached.get("reason", "")}
                    if attempt == 1:
                        continue
                    return last_result
            raise FinalEvaluationError(f"refusing to overwrite existing output: {run_dir}")
        run_dir.mkdir(parents=True)
        stream_dir = run_dir / "stream"
        started_ns = time.time_ns()
        started = time.monotonic()
        command = ["/usr/bin/time", "-v", "-o", str(run_dir / "resources.time.txt"),
                   "bash", str(RUN_SCRIPT), str(ros_env), str(workspace),
                   str(bag_path), str(stream_dir)]
        base = {
            "schema": "lio-run-lifecycle-v2", "run_id": attempt_id,
            "scheduled_run_id": run_id, "attempt": attempt,
            "role": role, "stratum": stratum, "seed": seed,
            "scene": scene, "control": scene == "CONTROL", "route_profile": PROFILE_ID,
            "scientific_outcome": "DEVELOPMENT_SMOKE_ONLY" if role == "development" else "PENDING_FINAL_ANALYSIS",
            "input_manifest": input_manifest,
            "fingerprint": fingerprint, "command": command, "started_utc_ns": started_ns,
            "elapsed_s": 0.0, "status": "RUNNING", "stage": "REPLAY", "reason": "",
        }
        _record_run_state(run_root, run_dir, base)
        try:
            process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, text=True,
                                       start_new_session=True)
            base.update(process_pid=process.pid, process_start_identity=_process_identity(process.pid))
            _write_json(run_dir / "run_manifest.json", base)
            try:
                stdout, stderr = process.communicate(timeout=900)
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    stdout, stderr = process.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    stdout, stderr = process.communicate()
                return_code = 124
                stderr += "\nFinal replay exceeded the frozen 900-second technical timeout."
        except OSError as exc:
            stdout, stderr, return_code = "", str(exc), 127
        elapsed = time.monotonic() - started
        (run_dir / "runner.stdout.log").write_text(stdout, encoding="utf-8")
        (run_dir / "runner.stderr.log").write_text(stderr, encoding="utf-8")
        base.update({
            "schema": "lio-run-lifecycle-v2", "run_id": attempt_id,
            "scheduled_run_id": run_id, "attempt": attempt,
            "role": role, "stratum": stratum, "seed": seed,
            "scene": scene, "control": scene == "CONTROL",
            "route_profile": PROFILE_ID,
            "scientific_outcome": "DEVELOPMENT_SMOKE_ONLY" if role == "development" else "PENDING_FINAL_ANALYSIS",
            "input_manifest": input_manifest,
            "fingerprint": fingerprint, "command": command,
            "started_utc_ns": started_ns, "elapsed_s": elapsed,
            "return_code": return_code,
        })
        base.update(status="CRASHED" if return_code else "REPLAYED",
                    stage="REPLAY", reason=stderr[-2000:] if return_code else "")
        _record_run_state(run_root, run_dir, base)
        if return_code != 0:
            base.update({"status": "CRASHED", "reason": stderr[-2000:]})
            _write_json(run_dir / "run_manifest.json", base)
            last_result = {"status": "CRASHED", "run_id": attempt_id,
                           "reason": base["reason"]}
            if attempt == 1:
                continue
            return last_result

        last_result = _postprocess_attempt(run_root, run_dir, base, ros_env, input_dir)
        if last_result["status"] == "INCOMPLETE_EXECUTION" and attempt == 1:
            continue
        return last_result
    return last_result or {"status": "FAILED", "run_id": run_id}


def _verify_retained_input(path: Path, seed: int, stratum: str, control: bool) -> dict[str, Any]:
    manifest = json.loads((path / "manifest.json").read_text())
    if (manifest.get("role") != "heldout" or manifest.get("seed") != seed
            or manifest.get("stratum") != stratum or manifest.get("control") is not control
            or manifest.get("truth_in_sensor_bag") is not False
            or manifest.get("scans") != 600 or manifest.get("imu_messages") != 12021
            or manifest.get("route_profile", {}).get("profile_id") != PROFILE_ID):
        raise FinalEvaluationError("retained pair does not match the scheduled input contract")
    for field, source in (("generator_sha256", Path(heldout.__file__)),
                          ("simulator_sha256", ROOT / "research_paper/experiments/src/simulate_lidar.py"),
                          ("formal_route_sha256", ROOT / "research_paper/experiments/src/t14_formal_route.py")):
        if manifest.get(field) != sha256_file(source):
            raise FinalEvaluationError(f"retained input source identity changed: {field}")
    for name in ("sensors.bag", "reference.txt", "reference_metadata.json"):
        if not (path / name).is_file() or sha256_file(path / name) != manifest.get(name, {}).get("sha256"):
            raise FinalEvaluationError(f"retained input hash mismatch: {path / name}")
    return manifest


def _prepare_pair(first_dir: Path, results_root: Path, run_root: Path,
                  seed: int, stratum: str, ros_env: Path,
                  identity: dict[str, Any], minimum_free_mb: int):
    """Resume verified input pairs or retain interrupted attempts and retry once."""
    reason = "input attempts exhausted"
    for attempt in (1, 2):
        folder = first_dir if attempt == 1 else first_dir.with_name(first_dir.name + "_TECHNICAL_RETRY1")
        record_path = results_root / "input_attempts" / f"{stratum}_{seed}_A{attempt}.json"
        previous = json.loads(record_path.read_text()) if record_path.is_file() else None
        if previous and previous.get("execution_identity") != identity:
            raise FinalEvaluationError("input attempt belongs to a different reviewed execution")
        archive_resume = False
        if previous and previous.get("status") == "FAILED_INPUT":
            reason = previous.get("reason", reason)
            if int(previous.get("archive_resume_count", 0)) >= 1:
                raise FinalEvaluationError(reason)
            archive_resume = previous.get("stage") == "INPUT_ARCHIVE" and attempt == 1
            if not archive_resume:
                continue
        if previous and previous.get("status") == "RUNNING":
            current = _process_identity(previous.get("owner_pid"))
            if current is not None and current == previous.get("owner_process_identity"):
                raise RunInProgressError("input generation is confirmed live in another process")
        record = {"schema": "final-input-attempt-v1", "run_id": f"INPUT_{stratum}_{seed}_A{attempt}",
                  "scheduled_run_id": f"INPUT_{stratum}_{seed}", "stratum": stratum,
                  "seed": seed, "scene": "PAIR", "attempt": attempt, "stage": "INPUT_GENERATION",
                  "status": "RUNNING", "reason": "", "started_utc_ns": time.time_ns(),
                  "scratch_path": str(folder), "execution_identity": identity,
                  "owner_pid": os.getpid(), "owner_process_identity": _process_identity(os.getpid())}
        if archive_resume:
            record.update(archive_resume_count=1, prior_failed_archive_record=previous)
        _write_json(record_path, record)
        _append_ledger(run_root / "failure_ledger.csv", record)
        try:
            for path in (first_dir.parent, results_root):
                if shutil.disk_usage(path).free < minimum_free_mb * 1024 * 1024:
                    raise FinalEvaluationError(f"insufficient free space for pair {stratum}/{seed}: {path}")
            corridor, control = folder / "corridor", folder / "control"
            if not folder.exists():
                folder.mkdir(parents=True)
                heldout.write_sensor_input(corridor, seed, stratum, False)
                heldout.write_sensor_input(control, seed, stratum, True)
            left = _verify_retained_input(corridor, seed, stratum, False)
            right = _verify_retained_input(control, seed, stratum, True)
            if left["reference.txt"]["sha256"] != right["reference.txt"]["sha256"]:
                raise FinalEvaluationError("paired analytic references differ")
            record.update(stage="PAIRED_BAG_AUDIT")
            _write_json(record_path, record)
            command = [str(ros_env / "bin/python"), str(PAIR_AUDIT),
                       "--corridor", str(corridor / "sensors.bag"),
                       "--control", str(control / "sensors.bag"),
                       "--expected-scans", "600", "--expected-imu", "12021"]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=180, check=False)
            record.update(audit_stdout=result.stdout, audit_stderr=result.stderr,
                          audit_return_code=result.returncode)
            _write_json(record_path, record)
            result.check_returncode()
            paired = json.loads(result.stdout)
            if paired.get("paired_imu_identical") is not True:
                raise FinalEvaluationError("paired IMU audit did not certify identical inputs")
            record.update(stage="INPUT_ARCHIVE")
            _write_json(record_path, record)
            reference = results_root / "shared_reference.txt"
            if reference.exists():
                if sha256_file(reference) != left["reference.txt"]["sha256"]:
                    raise FinalEvaluationError("common analytic reference changed between events")
            else:
                shutil.copy2(corridor / "reference.txt", reference)
            for scene, path in (("CORRIDOR", corridor), ("CONTROL", control)):
                archive = results_root / "inputs" / f"{stratum}_{seed}" / scene
                archive.mkdir(parents=True, exist_ok=True)
                for name in ("manifest.json", "reference_metadata.json"):
                    target = archive / name
                    if target.exists() and sha256_file(target) != sha256_file(path / name):
                        raise FinalEvaluationError(f"archived provenance mismatch: {target}")
                    if not target.exists():
                        shutil.copy2(path / name, target)
            record.update(status="INPUTS_VERIFIED", stage="INPUTS_VERIFIED",
                          paired_bag_audit=paired)
            _write_json(record_path, record)
            _append_ledger(run_root / "failure_ledger.csv", record)
            return folder, corridor, control, left, right, paired
        except (OSError, ValueError, FinalEvaluationError, subprocess.SubprocessError) as exc:
            reason = str(exc)[:2000]
            record.update(status="FAILED_INPUT", reason=reason)
            _write_json(record_path, record)
            _append_ledger(run_root / "failure_ledger.csv", record)
            if record.get("archive_resume_count") == 1:
                raise FinalEvaluationError(reason) from exc
            if record["stage"] == "INPUT_ARCHIVE" and attempt == 1:
                return _prepare_pair(first_dir, results_root, run_root, seed, stratum,
                                     ros_env, identity, minimum_free_mb)
    raise FinalEvaluationError(reason)


def execute_final_batch(
    screen_path: Path, plan_path: Path, analysis_path: Path,
    review_path: Path, freeze_path: Path,
    ros_env: Path, workspace: Path, binary_path: Path,
    scratch_root: Path, results_root: Path, minimum_free_mb: int = 1024,
) -> dict[str, Any]:
    gate_hashes = _require_r3_pass(review_path, freeze_path)
    runtime = _check_analysis_runtime()
    screen = json.loads(screen_path.read_text(encoding="utf-8"))
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    if screen.get("status") != "SCENE_SCREEN_PASS" or screen.get("role") != "heldout":
        raise FinalEvaluationError("final runs require a passed held-out geometry-only screen")
    if analysis.get("heldout_inputs_opened") is not False:
        raise FinalEvaluationError("T16 development manifest indicates held-out exposure")
    if (analysis_path.resolve() != T16_ANALYSIS_MANIFEST.resolve()
            or plan_path.resolve() != FINAL_PLAN.resolve()
            or screen.get("plan_sha256") != sha256_file(plan_path)
            or screen.get("development_analysis_sha256") != sha256_file(analysis_path)):
        raise FinalEvaluationError("screen is not descended from the exact T16 analysis and no-data plan")
    if screen.get("reviewed_artifact_hashes") != gate_hashes["reviewed_artifact_hashes"]:
        raise FinalEvaluationError("R3 content inventory changed after the geometry screen")
    if any(screen.get(key) != gate_hashes[key] for key in ("r3_review_sha256", "implementation_freeze_sha256")):
        raise FinalEvaluationError("screen review/freeze identity changed")
    if (plan != build_plan(analysis_path, ROOT / "research_paper/data/SPLITS.csv")
            or plan.get("development_analysis_sha256") != sha256_file(analysis_path)):
        raise FinalEvaluationError("screen plan no longer matches the frozen development analysis")
    if (screen.get("screen_runner_sha256") != sha256_file(Path(__file__).resolve())
            or screen.get("heldout_generator_sha256") != sha256_file(Path(heldout.__file__).resolve())):
        raise FinalEvaluationError("held-out screen source changed after R3 review")
    threshold_info = analysis["fastlio_threshold_selection"]
    if threshold_info.get("status") != "SELECTED_DEVELOPMENT_THRESHOLD":
        raise FinalEvaluationError("T16 has no feasible FAST-LIO threshold to lock")
    threshold = float(threshold_info["threshold"])
    freeze_text = freeze_path.read_text(encoding="utf-8")
    if "FASTLIO_MIN_EIG_G3" not in freeze_text or format(threshold, ".17g") not in freeze_text:
        raise FinalEvaluationError("R3 freeze does not lock the exact T16 development threshold")
    target = int(analysis["sample_size"]["n_test_geometry_pairs"])
    selected = screen["selected_seeds_by_stratum"]
    if set(selected) != set(heldout.STRATA):
        raise FinalEvaluationError("screen lacks one of the four frozen strata")
    if any(len(selected.get(name, [])) != target // 4 for name in heldout.STRATA):
        raise FinalEvaluationError("screen does not provide the frozen equal-per-stratum event count")
    if any(row.get("stratum") not in heldout.STRATA for row in screen.get("screened_layouts", [])):
        raise FinalEvaluationError("screen contains an unknown stratum")
    for stratum, seeds in selected.items():
        if seeds != sorted(set(seeds)):
            raise FinalEvaluationError(f"selected seed list is duplicated or unordered: {stratum}")
        if any(heldout.stratum_for_seed(int(seed)) != stratum for seed in seeds):
            raise FinalEvaluationError(f"screen selection contains a seed from the wrong stratum: {stratum}")
        stratum_rows = [row for row in screen.get("screened_layouts", [])
                        if row.get("stratum") == stratum]
        eligible_order = [int(row["seed"]) for row in stratum_rows if row.get("eligible")]
        if list(map(int, seeds)) != eligible_order[:target // 4]:
            raise FinalEvaluationError(f"selected seeds are not the lowest eligible IDs for {stratum}")
        if (not seeds or [row["seed"] for row in stratum_rows]
                != list(range(heldout.STRATA[stratum]["seed_min"], seeds[-1] + 1))):
            raise FinalEvaluationError(f"screen does not preserve the complete ascending candidate prefix for {stratum}")
    backend = _check_backend(ros_env, workspace, binary_path)
    execution_identity = {**gate_hashes, "runtime": runtime, "backend": backend,
                          "plan_sha256": sha256_file(plan_path),
                          "screen_sha256": sha256_file(screen_path),
                          "analysis_sha256": sha256_file(analysis_path)}
    for stratum, seeds in selected.items():
        stratum_rows = [row for row in screen["screened_layouts"] if row["stratum"] == stratum]
        for recorded in stratum_rows:
            seed = int(recorded["seed"])
            if heldout.screen_layout(seed, stratum) != recorded:
                raise FinalEvaluationError(f"scene-screen read-back differs for {stratum}/{seed}")
    scratch_root.mkdir(parents=True, exist_ok=True)
    results_root.mkdir(parents=True, exist_ok=True)
    pair_rows = []
    run_root = results_root / "runs"
    run_root.mkdir(parents=True, exist_ok=True)
    shared_reference = results_root / "shared_reference.txt"
    for stratum, seeds in selected.items():
        for seed in seeds:
            pair_scratch = scratch_root / f"heldout_{stratum}_{seed}"
            pair_key = f"{stratum}_{seed}"
            pair_record_path = results_root / "pairs" / f"{pair_key}.json"
            if pair_record_path.is_file():
                cached_pair = json.loads(pair_record_path.read_text(encoding="utf-8"))
                if (cached_pair.get("status") == "COMPLETED"
                        and cached_pair.get("scene_screen_sha256") == sha256_file(screen_path)
                        and cached_pair.get("development_analysis_sha256") == sha256_file(analysis_path)
                        and cached_pair.get("execution_identity") == execution_identity):
                    runs_ok = len(cached_pair.get("scene_runs", [])) == 2
                    seen_scenes = set()
                    for scene_result in cached_pair["scene_runs"]:
                        manifest_path = run_root / scene_result["run_id"] / "run_manifest.json"
                        if not manifest_path.is_file():
                            runs_ok = False
                            break
                        run_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                        runs_ok &= run_manifest.get("status") == "COMPLETED"
                        seen_scenes.add(run_manifest.get("scene"))
                        runs_ok &= run_manifest.get("seed") == int(seed) and run_manifest.get("stratum") == stratum
                        runs_ok &= bool(run_manifest.get("outputs")) and bool(run_manifest.get("completion_validation"))
                        runs_ok &= run_manifest.get("fingerprint", {}).get("execution_identity") == execution_identity
                        for relative, expected in run_manifest.get("outputs", {}).items():
                            artifact = manifest_path.parent / relative
                            runs_ok &= artifact.is_file() and sha256_file(artifact) == expected
                    runs_ok &= seen_scenes == {"CORRIDOR", "CONTROL"}
                    if runs_ok:
                        pair_rows.append(cached_pair)
                        continue
            try:
                (pair_scratch, corridor_input, control_input, corridor_manifest,
                 control_manifest, pair_audit) = _prepare_pair(
                    pair_scratch, results_root, run_root, int(seed), stratum, ros_env,
                    execution_identity, minimum_free_mb)
            except (OSError, ValueError, FinalEvaluationError, subprocess.SubprocessError) as exc:
                failed = {"schema": "final-heldout-pair-v2", "status": "FAILED_KEEP_INPUTS",
                          "stratum": stratum, "seed": int(seed), "stage": "INPUT_PREPARATION",
                          "reason": str(exc)[:2000], "scene_runs": [],
                          "execution_identity": execution_identity}
                _write_json(pair_record_path, failed)
                pair_rows.append(failed)
                if isinstance(exc, RunInProgressError):
                    raise
                continue
            scene_results = []
            for scene, input_dir, input_manifest in (
                ("CORRIDOR", corridor_input, corridor_manifest),
                ("CONTROL", control_input, control_manifest),
            ):
                run_id = f"FINAL_TEST_{stratum.removeprefix('TEST_')}_{seed}_{scene}_P1"
                try:
                    scene_results.append(_run_scene(
                        run_id, int(seed), stratum, scene, input_dir, run_root,
                        ros_env, workspace, backend["binary_sha256"], threshold, execution_identity))
                except (OSError, ValueError, FinalEvaluationError) as exc:
                    scene_results.append({"status": "FAILED_VALIDATION", "run_id": run_id,
                                          "reason": str(exc)[:2000]})
                if scene_results[-1]["status"] == "IN_PROGRESS":
                    break
            completed = all(row["status"] in ("COMPLETED", "CACHED") for row in scene_results)
            pair_rows.append({
                "stratum": stratum, "seed": int(seed),
                "corridor_bag_sha256": corridor_manifest["sensors.bag"]["sha256"],
                "control_bag_sha256": control_manifest["sensors.bag"]["sha256"],
                "reference_sha256": corridor_manifest["reference.txt"]["sha256"],
                "paired_bag_audit": pair_audit,
                "scene_runs": scene_results,
                "status": "COMPLETED" if completed else "FAILED_KEEP_INPUTS",
            })
            archive_pair = {
                "schema": "final-heldout-pair-v2",
                "execution_identity": execution_identity,
                "status": "COMPLETED" if completed else "FAILED_KEEP_INPUTS",
                "stratum": stratum, "seed": int(seed),
                "scene_screen_sha256": sha256_file(screen_path),
                "development_analysis_sha256": sha256_file(analysis_path),
                "corridor_manifest_sha256": sha256_file(corridor_input / "manifest.json"),
                "control_manifest_sha256": sha256_file(control_input / "manifest.json"),
                "corridor_bag_sha256": corridor_manifest["sensors.bag"]["sha256"],
                "control_bag_sha256": control_manifest["sensors.bag"]["sha256"],
                "reference_sha256": corridor_manifest["reference.txt"]["sha256"],
                "scene_runs": scene_results,
                "paired_bag_audit": pair_audit,
            }
            _write_json(pair_record_path, archive_pair)
            _write_json(results_root / "final_batch_progress.json", {
                "schema": "final-heldout-batch-progress-v1", "role": "heldout",
                "status": "RUNNING", **gate_hashes,
                "development_analysis_sha256": sha256_file(analysis_path),
                "scene_screen_sha256": sha256_file(screen_path),
                "backend": backend, "threshold_locked_from_development": threshold,
                "pairs_completed_or_failed_so_far": pair_rows,
            })
            if any(row["status"] == "IN_PROGRESS" for row in scene_results):
                raise RunInProgressError("retained replay process is confirmed live; progress saved")
            if completed:
                # Hash-verified manifests and streams remain; raw scratch bags
                # are reproducible and are discarded only after both scenes pass.
                shutil.rmtree(pair_scratch)
            else:
                # A failed pair is kept with both exact raw sensor inputs for diagnosis.
                continue
    completed_pairs = sum(row["status"] == "COMPLETED" for row in pair_rows)
    result = {
        "schema": "final-heldout-batch-v1", "role": "heldout",
        "status": "COMPLETED" if completed_pairs == target else "INCOMPLETE_KEEP_FAILURES",
        **gate_hashes,
        "target_geometry_pairs": target,
        "completed_geometry_pairs": completed_pairs,
        "scheduled_scene_runs": target * 2,
        "scene_runs": sum(len(row.get("scene_runs", [])) for row in pair_rows),
        "development_analysis_sha256": sha256_file(analysis_path),
        "scene_screen_sha256": sha256_file(screen_path),
        "backend": backend,
        "runner_sha256": sha256_file(Path(__file__).resolve()),
        "heldout_generator_sha256": sha256_file(Path(heldout.__file__).resolve()),
        "threshold_locked_from_development": threshold,
        "minimum_free_space_mib": minimum_free_mb,
        "pair_results": pair_rows,
        "heldout_inputs_or_results_used_for_tuning": False,
    }
    _write_json(results_root / "final_batch_summary.json", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="make a reserved-seed screen schedule; creates no data")
    plan.add_argument("--analysis", type=Path, required=True)
    plan.add_argument("--splits", type=Path, default=ROOT / "research_paper/data/SPLITS.csv")
    plan.add_argument("--output", type=Path, required=True)
    screen = commands.add_parser("screen", help="scene-only screen; gated on R3 PASS")
    screen.add_argument("--plan", type=Path, required=True)
    screen.add_argument("--r3-review", type=Path, required=True)
    screen.add_argument("--implementation-freeze", type=Path, required=True)
    screen.add_argument("--output", type=Path, required=True)
    run = commands.add_parser("run", help="run the final paired batch; gated on R3 PASS")
    run.add_argument("--screen", type=Path, required=True)
    run.add_argument("--plan", type=Path, required=True)
    run.add_argument("--analysis", type=Path, required=True)
    run.add_argument("--r3-review", type=Path, required=True)
    run.add_argument("--implementation-freeze", type=Path, required=True)
    run.add_argument("--ros-env", type=Path, required=True)
    run.add_argument("--workspace", type=Path, required=True)
    run.add_argument("--fastlio-binary", type=Path, required=True)
    run.add_argument("--scratch-root", type=Path, required=True)
    run.add_argument("--results-root", type=Path, required=True)
    run.add_argument("--minimum-free-mb", type=int, default=1024)
    args = parser.parse_args()
    if args.command == "plan":
        result = build_plan(args.analysis, args.splits)
        _write_json(args.output, result)
        print(json.dumps({"status": result["status"],
                          "n_test_geometry_pairs": result["n_test_geometry_pairs"],
                          "pairs_per_stratum": result["geometry_pairs_per_stratum"],
                          "heldout_inputs_generated": False,
                          "heldout_geometry_screened": False}, indent=2))
    elif args.command == "screen":
        result = screen_reserved_layouts(args.plan, args.r3_review,
                                         args.implementation_freeze)
        _write_json(args.output, result)
        print(json.dumps({"status": result["status"],
                          "selected_seeds_by_stratum": result["selected_seeds_by_stratum"]}, indent=2))
        if result["status"] != "SCENE_SCREEN_PASS":
            raise SystemExit(2)
    else:
        # Check resource headroom before generating any test input.
        for path in (args.scratch_root, args.results_root):
            probe = path if path.exists() else path.parent
            if shutil.disk_usage(probe).free < args.minimum_free_mb * 1024 * 1024:
                raise SystemExit(f"insufficient free space on filesystem containing {path}")
        result = execute_final_batch(
            args.screen, args.plan, args.analysis, args.r3_review, args.implementation_freeze,
            args.ros_env, args.workspace, args.fastlio_binary,
            args.scratch_root, args.results_root, args.minimum_free_mb)
        print(json.dumps({"status": result["status"],
                          "target_geometry_pairs": result["target_geometry_pairs"],
                          "completed_geometry_pairs": result["completed_geometry_pairs"]}, indent=2))
        if result["status"] != "COMPLETED":
            raise SystemExit(2)


if __name__ == "__main__":
    main()
