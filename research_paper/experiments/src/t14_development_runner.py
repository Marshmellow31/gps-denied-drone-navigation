"""Resumable, development-only T14 FAST-LIO runner.

Every input, configuration, build and analysis source is hashed. A completed
run is reused only when its full fingerprint and all output hashes match.
One technical retry is allowed after a backend crash; each attempt is retained.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENTS = ROOT / "research_paper/experiments"
RUNNER_PATH = Path(__file__).resolve()
ROUTE_PATH = EXPERIMENTS / "src/t14_formal_route.py"
GENERATOR_PATH = EXPERIMENTS / "src/write_simulation_bag.py"
SIMULATOR_PATH = EXPERIMENTS / "src/simulate_lidar.py"
SCENE_AUDIT_PATH = EXPERIMENTS / "src/audit_simulation_scene.py"
PAIR_AUDIT_PATH = EXPERIMENTS / "src/audit_paired_simulation_bags.py"
HEALTH_AUDIT_PATH = EXPERIMENTS / "src/audit_health_export.py"
DCREG_PATH = EXPERIMENTS / "src/dcreg_schur.py"
EVALUATOR_PATH = EXPERIMENTS / "src/trajectory_eval.py"
POSE_LOGGER_PATH = EXPERIMENTS / "src/pose_logger.py"
REPLAY_SCRIPT = EXPERIMENTS / "run_simulation_smoke.sh"
CONFIG_PATH = ROOT / "research_paper/configs/fastlio_simulation_bootstrap.yaml"
PROFILE_ID = "T14_FORMAL_X_MINUS_6_V1"
DEVELOPMENT_SEEDS = range(14, 46)
EXPECTED_DURATION_S = 60.0
EXPECTED_SCANS = 600
EXPECTED_IMU_MESSAGES = 12021
ENTRY_TIME_S = 10.5
SIMULATION_EPOCH_S = 1000.0
RUN_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{2,79}\Z")


class InputContractError(ValueError):
    pass


class MissingReferenceError(InputContractError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def evaluation_entry_start_ns(manifest: dict[str, Any]) -> int:
    timestamp_s = SIMULATION_EPOCH_S + float(manifest["route_profile"]["entry_time_s"])
    return round(timestamp_s * 1_000_000_000)


def _seed_range(text: str) -> list[int]:
    try:
        low, high = (int(value) for value in text.split("-", 1))
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("use an inclusive development range, e.g. 14-45") from exc
    if low > high or low not in DEVELOPMENT_SEEDS or high not in DEVELOPMENT_SEEDS:
        raise argparse.ArgumentTypeError("T14 may use only development seeds 14-45")
    return list(range(low, high + 1))


def build_schedule(seeds: Sequence[int]) -> list[dict[str, Any]]:
    """Primary corridor/control pairs plus the preregistered first/last repeats."""
    if not seeds or any(seed not in DEVELOPMENT_SEEDS for seed in seeds):
        raise ValueError("schedule must contain development seeds 14-45 only")
    if list(seeds) != sorted(set(seeds)):
        raise ValueError("schedule seeds must be unique and ascending")
    runs: list[dict[str, Any]] = []
    for seed in seeds:
        for scene_name, control in (("CORRIDOR", False), ("CONTROL", True)):
            runs.append({"seed": seed, "scene": scene_name, "control": control,
                         "repeat": False, "run_id": f"T14_DEV{seed:02d}_{scene_name}_XM6_P1"})
    if len(seeds) > 1:
        for seed in (seeds[0], seeds[-1]):
            for scene_name, control in (("CORRIDOR", False), ("CONTROL", True)):
                runs.append({"seed": seed, "scene": scene_name, "control": control,
                             "repeat": True,
                             "run_id": f"T14_DEV{seed:02d}_{scene_name}_XM6_REPEAT1"})
    if len({row["run_id"] for row in runs}) != len(runs):
        raise ValueError("generated T14 run IDs are not unique")
    return runs


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def _record_ledger(ledger_path: Path, row: dict[str, Any]) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    fields = ("run_id", "seed", "scene", "repeat", "stage", "status", "reason",
              "input_bag_sha256", "fingerprint_sha256", "started_utc_ns",
              "elapsed_s", "return_code", "scientific_outcome")
    exists = ledger_path.exists()
    with ledger_path.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        if not exists:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in fields})


def _validate_screen(path: Path, seeds: Sequence[int]) -> dict[str, Any]:
    if not path.is_file():
        raise InputContractError(f"formal scene-only screen missing: {path}")
    screen = json.loads(path.read_text(encoding="utf-8"))
    expected = list(seeds)
    result_seeds = [int(row["layout_seed"]) for row in screen.get("results", [])]
    if screen.get("profile_id") != PROFILE_ID or screen.get("role") != "development_only":
        raise InputContractError("screen is not for the formal development-only route")
    if result_seeds != expected:
        raise InputContractError("screen seed IDs do not match the scheduled development set")
    if screen.get("eligible_count") != len(expected) or screen.get("ineligible_seeds"):
        raise InputContractError("formal scene-only screen did not pass every scheduled seed")
    if screen.get("route_adapter_sha256") != sha256_file(ROUTE_PATH):
        raise InputContractError("route adapter changed after the formal geometry screen")
    if screen.get("frozen_simulator_sha256") != sha256_file(SIMULATOR_PATH):
        raise InputContractError("frozen simulator changed after the formal geometry screen")
    return screen


def _validate_input(input_dir: Path, seed: int, control: bool) -> dict[str, Any]:
    bag_path = input_dir / "sensors.bag"
    reference_path = input_dir / "reference.txt"
    reference_metadata_path = input_dir / "reference_metadata.json"
    manifest_path = input_dir / "manifest.json"
    if not bag_path.is_file():
        raise InputContractError(f"sensor bag missing: {bag_path}")
    if not reference_path.is_file() or not reference_metadata_path.is_file():
        raise MissingReferenceError("separate analytic reference or its metadata is missing")
    if not manifest_path.is_file():
        raise InputContractError("input manifest is missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("role") != "development" or manifest.get("truth_in_sensor_bag") is not False:
        raise InputContractError("input role/truth isolation contract is invalid")
    if manifest.get("seed") != seed or manifest.get("layout_seed") != seed:
        raise InputContractError("layout and sensor seeds must match the scheduled seed")
    if manifest.get("control") is not control:
        raise InputContractError("input corridor/control role does not match the schedule")
    if manifest.get("duration_s") != EXPECTED_DURATION_S:
        raise InputContractError("formal development inputs must run for 60 seconds")
    route = manifest.get("route_profile", {})
    if route.get("profile_id") != PROFILE_ID or route.get("vehicle_start_x_m") != -6.0:
        raise InputContractError("input does not use the approved x=-6 m profile")
    if route.get("entry_time_s") != ENTRY_TIME_S:
        raise InputContractError("formal route entry must be at 10.5 seconds")
    if manifest.get("layout_seed_equals_sensor_seed") != seed:
        raise InputContractError("manifest does not certify the frozen seed mapping")
    for artifact_name, artifact_path in (("sensors.bag", bag_path),
                                         ("reference.txt", reference_path),
                                         ("reference_metadata.json", reference_metadata_path)):
        recorded = manifest.get(artifact_name, {})
        if recorded.get("sha256") != sha256_file(artifact_path):
            raise InputContractError(f"input hash mismatch for {artifact_name}")
    reference_metadata = json.loads(reference_metadata_path.read_text(encoding="utf-8"))
    if reference_metadata.get("verified") is not True:
        raise MissingReferenceError("reference body metadata is not verified")
    if reference_metadata.get("evaluation_scope") != "development_only":
        raise InputContractError("reference is outside the development-only scope")
    if reference_metadata.get("source", {}).get("sha256") != sha256_file(reference_path):
        raise MissingReferenceError("reference hash does not match its body metadata")
    if reference_metadata.get("route_profile", {}).get("profile_id") != PROFILE_ID:
        raise InputContractError("reference metadata uses a different route profile")
    if manifest.get("status") != "completed":
        raise InputContractError("input generator did not mark the bag complete")
    return manifest


def _backend_identity(workspace: Path) -> dict[str, Any]:
    source = workspace / "src/fast_lio"
    binary_candidates = (workspace / "devel/lib/fast_lio/fastlio_mapping",
                         workspace / "devel/.private/fast_lio/lib/fast_lio/fastlio_mapping")
    binary = next((path.resolve() for path in binary_candidates if path.exists()), None)
    if binary is None or not source.is_dir():
        raise InputContractError("FAST-LIO source or built binary is missing from workspace")
    commit = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    diff = subprocess.check_output(["git", "-C", str(source), "diff", "HEAD", "--binary"])
    status = subprocess.check_output(["git", "-C", str(source), "status", "--short"], text=True)
    return {
        "upstream_commit": commit,
        "worktree_diff_sha256": sha256_bytes(diff),
        "worktree_status": status.splitlines(),
        "binary_sha256": sha256_file(binary),
        "binary_path": str(binary),
        "pcl17_patch_sha256": sha256_file(EXPERIMENTS / "patches/fast_lio_pcl17.patch"),
        "t08_patch_sha256": sha256_file(EXPERIMENTS / "patches/fast_lio_health_diagnostic.patch"),
        "t13_patch_sha256": sha256_file(EXPERIMENTS / "patches/fast_lio_hessian_sidecar.patch"),
    }


def _runtime_identity(ros_env: Path, python_path: Path) -> dict[str, Any]:
    probe = subprocess.check_output(
        [str(python_path), "-c",
         "import json, numpy, sys; print(json.dumps({'python': sys.version, 'numpy': numpy.__version__}))"],
        text=True)
    history = ros_env / "conda-meta/history"
    return {
        "host_platform": platform.platform(),
        "python_executable": str(python_path.resolve()),
        "python_packages": json.loads(probe),
        "ros_environment": str(ros_env.resolve()),
        "ros_distro": "noetic",
        "conda_history_sha256": sha256_file(history) if history.is_file() else None,
    }


def _fingerprint(input_dir: Path, input_manifest: dict[str, Any],
                 workspace: Path, ros_env: Path,
                 python_path: Path) -> dict[str, Any]:
    paths = {
        "input_manifest": input_dir / "manifest.json",
        "sensor_bag": input_dir / "sensors.bag",
        "reference": input_dir / "reference.txt",
        "reference_metadata": input_dir / "reference_metadata.json",
    }
    sources = {
        "runner": RUNNER_PATH,
        "route_adapter": ROUTE_PATH,
        "input_generator": GENERATOR_PATH,
        "simulator": SIMULATOR_PATH,
        "scene_screen": SCENE_AUDIT_PATH,
        "pair_audit": PAIR_AUDIT_PATH,
        "health_audit": HEALTH_AUDIT_PATH,
        "dcreg": DCREG_PATH,
        "trajectory_evaluator": EVALUATOR_PATH,
        "pose_logger": POSE_LOGGER_PATH,
        "replay_script": REPLAY_SCRIPT,
        "config": CONFIG_PATH,
    }
    return {
        "input_hashes": {name: sha256_file(path) for name, path in paths.items()},
        "route_profile": input_manifest["route_profile"],
        "sources": {name: sha256_file(path) for name, path in sources.items()},
        "backend": _backend_identity(workspace),
        "runtime": _runtime_identity(ros_env, python_path),
    }


def _verify_cached(run_dir: Path, fingerprint: dict[str, Any]) -> bool:
    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.is_file():
        return False
    run_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if run_manifest.get("status") != "COMPLETED" or run_manifest.get("fingerprint") != fingerprint:
        return False
    for relative_path, expected_hash in run_manifest.get("outputs", {}).items():
        output = run_dir / relative_path
        if not output.is_file() or sha256_file(output) != expected_hash:
            return False
    return bool(run_manifest.get("outputs"))


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def _run_one(run: dict[str, Any], input_root: Path, output_root: Path,
             ros_env: Path, workspace: Path, python_path: Path,
             ledger_path: Path) -> dict[str, Any]:
    seed, control, base_run_id = run["seed"], run["control"], run["run_id"]
    scene_name, repeat = run["scene"], run["repeat"]
    input_id = f"T14_FORMAL_DEV{seed:02d}_{scene_name}_INPUT_XM6_V1"
    input_dir = input_root / input_id
    input_manifest: dict[str, Any] | None = None
    bag_hash = ""
    fingerprint: dict[str, Any] = {}
    try:
        input_manifest = _validate_input(input_dir, seed, control)
        bag_hash = input_manifest["sensors.bag"]["sha256"]
        fingerprint = _fingerprint(input_dir, input_manifest, workspace, ros_env, python_path)
    except MissingReferenceError as exc:
        return _preflight_failure(run, output_root, ledger_path, "MISSING_REFERENCE", str(exc))
    except (InputContractError, OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        return _preflight_failure(run, output_root, ledger_path, "INVALID_INPUT", str(exc))

    run_id = base_run_id
    if not RUN_ID_PATTERN.fullmatch(run_id):
        return _preflight_failure(run, output_root, ledger_path, "INVALID_INPUT",
                                  f"unsafe run ID: {run_id}")
    run_dir = output_root / run_id
    if run_dir.exists():
        if _verify_cached(run_dir, fingerprint):
            cached = json.loads((run_dir / "run_manifest.json").read_text(encoding="utf-8"))
            return {"status": "CACHED", "run_id": run_id,
                    "scientific_outcome": cached.get("scientific_outcome", "PENDING_T16"),
                    "run_manifest": str(run_dir / "run_manifest.json")}
        existing_path = run_dir / "run_manifest.json"
        if existing_path.is_file():
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            if existing.get("fingerprint") != fingerprint:
                return _preflight_failure(run, output_root, ledger_path, "INVALID_INPUT",
                                          "existing run ID has a different input/config/code fingerprint")
            return {"status": existing.get("status", "CRASHED"), "run_id": run_id,
                    "reason": existing.get("reason", "incomplete prior attempt"),
                    "run_manifest": str(existing_path)}
        return {"status": "CRASHED", "run_id": run_id,
                "reason": "orphaned output directory without a completion manifest"}

    run_dir.mkdir(parents=True)
    stream_dir = run_dir / "stream"
    resource_file = run_dir / "resources.time.txt"
    command = ["/usr/bin/time", "-v", "-o", str(resource_file), "bash",
               str(REPLAY_SCRIPT), str(ros_env), str(workspace),
               str(input_dir / "sensors.bag"), str(stream_dir)]
    started_ns = time.time_ns()
    started = time.monotonic()
    try:
        process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                 timeout=900, check=False)
        return_code = process.returncode
        stdout, stderr = process.stdout, process.stderr
    except subprocess.TimeoutExpired as exc:
        return_code = 124
        stdout = exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode(errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        stderr += "\nT14 replay exceeded its 900 second technical timeout."
    elapsed = time.monotonic() - started
    (run_dir / "runner.stdout.log").write_text(stdout, encoding="utf-8")
    (run_dir / "runner.stderr.log").write_text(stderr, encoding="utf-8")

    attempt_number = 2 if run_id.endswith("_TECHNICAL_RETRY1") else 1
    scheduled_run_id = run.get("scheduled_run_id", base_run_id)
    base_manifest: dict[str, Any] = {
            "schema": "t14-run-manifest-v1",
            "run_id": run_id,
            "scheduled_run_id": scheduled_run_id,
            "attempt": attempt_number,
            "role": "development",
            "scientific_outcome": "PENDING_T16",
            "seed": seed,
            "scene": scene_name,
            "control": control,
            "repeat": repeat,
            "route_profile": PROFILE_ID,
            "entry_start_ns": evaluation_entry_start_ns(input_manifest),
            "exit_time_s": input_manifest["route_profile"]["exit_time_s"],
            "input_manifest_sha256": fingerprint["input_hashes"]["input_manifest"],
            "sensor_bag_sha256": bag_hash,
            "reference_sha256": fingerprint["input_hashes"]["reference"],
            "reference_metadata_sha256": fingerprint["input_hashes"]["reference_metadata"],
            "fingerprint": fingerprint,
        "command": command,
        "runtime": fingerprint["runtime"],
            "started_utc_ns": started_ns,
            "elapsed_s": elapsed,
            "return_code": return_code,
        }
    if return_code != 0:
        base_manifest.update({"status": "CRASHED", "reason": stderr[-2000:]})
        _write_json(run_dir / "run_manifest.json", base_manifest)
        _record_ledger(ledger_path, {
            **run, "run_id": run_id, "stage": "REPLAY", "status": "CRASHED",
            "reason": base_manifest["reason"], "input_bag_sha256": bag_hash,
            "fingerprint_sha256": sha256_bytes(json.dumps(fingerprint, sort_keys=True).encode()),
            "started_utc_ns": started_ns, "elapsed_s": round(elapsed, 3),
            "return_code": return_code, "scientific_outcome": "PENDING_T16",
        })
        return {"status": "CRASHED", "run_id": run_id,
                "run_manifest": str(run_dir / "run_manifest.json"),
                "reason": base_manifest["reason"]}

    try:
        required_outputs = (stream_dir / "poses.csv", stream_dir / "health.csv",
                           stream_dir / "health.csv.hessian.csv")
        if not all(path.is_file() for path in required_outputs):
            raise RuntimeError("replay exited zero but one or more required streams are missing")
        health_audit = subprocess.run(
            [str(python_path), str(HEALTH_AUDIT_PATH), str(stream_dir / "health.csv")],
            cwd=ROOT, capture_output=True, text=True, check=True)
        dcreg_process = subprocess.run(
            [str(python_path), str(DCREG_PATH), "--hessian-csv",
             str(stream_dir / "health.csv.hessian.csv"), "--health-csv",
             str(stream_dir / "health.csv"), "--output-csv", str(stream_dir / "dcreg.csv")],
            cwd=ROOT, capture_output=True, text=True, check=True)
        eval_process = subprocess.run(
            [str(python_path), str(EVALUATOR_PATH), "--poses", str(stream_dir / "poses.csv"),
             "--reference", str(input_dir / "reference.txt"), "--output",
             str(stream_dir / "evaluation.csv"), "--run-id", run_id,
             "--event-id", f"T14_GEOMETRY_EXIT_DEV{seed:02d}",
             "--body-transform-json", str(input_dir / "reference_metadata.json"),
             "--development-only", "--entry-start-ns",
             str(evaluation_entry_start_ns(input_manifest))],
            cwd=ROOT, capture_output=True, text=True, check=True)
        health_summary = json.loads(health_audit.stdout)
        dcreg_summary = json.loads(dcreg_process.stdout)
        eval_summary = json.loads(eval_process.stdout)
        evaluation_rows = _read_rows(stream_dir / "evaluation.csv")
        output_files = [path for path in sorted(stream_dir.iterdir())
                        if path.is_file() and path.name != "diagnostic.png"]
        output_files.extend(path for path in (
            run_dir / "resources.time.txt", run_dir / "runner.stdout.log",
            run_dir / "runner.stderr.log") if path.is_file())
        base_manifest.update({
            "status": "COMPLETED", "reason": "",
            "health_audit": health_summary,
            "dcreg_summary": dcreg_summary,
            "evaluation_summary": eval_summary,
            "evaluation_local_valid_rows": sum(
                row.get("local_valid", "").lower() == "true" for row in evaluation_rows),
            "outputs": {str(path.relative_to(run_dir)): sha256_file(path)
                        for path in output_files},
        })
        _write_json(run_dir / "run_manifest.json", base_manifest)
        _record_ledger(ledger_path, {
            **run, "run_id": run_id, "stage": "POSTPROCESSING", "status": "COMPLETED",
            "input_bag_sha256": bag_hash,
            "fingerprint_sha256": sha256_bytes(json.dumps(fingerprint, sort_keys=True).encode()),
            "started_utc_ns": started_ns, "elapsed_s": round(elapsed, 3),
            "return_code": return_code, "scientific_outcome": "PENDING_T16",
        })
        return {"status": "COMPLETED", "run_id": run_id,
                "run_manifest": str(run_dir / "run_manifest.json"),
                "elapsed_s": round(elapsed, 3), "dcreg_valid": dcreg_summary["valid"],
                "evaluation_local_valid": base_manifest["evaluation_local_valid_rows"]}
    except FileNotFoundError as exc:
        status = "MISSING_REFERENCE" if "reference" in str(exc).lower() else "POSTPROCESSING_FAILED"
        reason = str(exc)
    except subprocess.CalledProcessError as exc:
        status = "MISSING_REFERENCE" if "reference" in (exc.stderr or "").lower() else "POSTPROCESSING_FAILED"
        reason = (exc.stderr or exc.stdout or str(exc))[-2000:]
    except (RuntimeError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        status, reason = "POSTPROCESSING_FAILED", str(exc)

    base_manifest.update({"status": status, "reason": reason})
    _write_json(run_dir / "run_manifest.json", base_manifest)
    _record_ledger(ledger_path, {
        **run, "run_id": run_id, "stage": "POSTPROCESSING", "status": status,
        "reason": reason, "input_bag_sha256": bag_hash,
        "fingerprint_sha256": sha256_bytes(json.dumps(fingerprint, sort_keys=True).encode()),
        "started_utc_ns": started_ns, "elapsed_s": round(elapsed, 3),
        "return_code": return_code, "scientific_outcome": "PENDING_T16",
    })
    return {"status": status, "run_id": run_id,
            "run_manifest": str(run_dir / "run_manifest.json"), "reason": reason}


def _preflight_failure(run: dict[str, Any], output_root: Path, ledger_path: Path,
                       status: str, reason: str) -> dict[str, Any]:
    run_dir = output_root / run["run_id"]
    if not run_dir.exists():
        run_dir.mkdir(parents=True)
        _write_json(run_dir / "run_manifest.json", {
            "schema": "t14-run-manifest-v1", "run_id": run["run_id"],
            "status": status, "reason": reason, "role": "development",
            "scientific_outcome": "PENDING_T16", **run,
        })
    _record_ledger(ledger_path, {
        **run, "stage": "PREFLIGHT", "status": status, "reason": reason,
        "scientific_outcome": "PENDING_T16",
    })
    return {"status": status, "run_id": run["run_id"], "reason": reason}


def _ensure_input(run: dict[str, Any], input_root: Path, ros_env: Path,
                  python_path: Path) -> Path:
    seed, control, scene_name = run["seed"], run["control"], run["scene"]
    input_id = f"T14_FORMAL_DEV{seed:02d}_{scene_name}_INPUT_XM6_V1"
    input_dir = input_root / input_id
    if input_dir.exists():
        manifest = _validate_input(input_dir, seed, control)
        if manifest.get("route_adapter_sha256") != sha256_file(ROUTE_PATH):
            raise InputContractError("saved input was generated by another route adapter version")
        return input_dir
    command = [str(python_path), str(ROUTE_PATH), "generate", "--run-id", input_id,
               "--output-root", str(input_root), "--seed", str(seed),
               "--duration", str(EXPECTED_DURATION_S)]
    if control:
        command.append("--control")
    process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    generation_log = input_root / "generation_logs" / f"{input_id}.log"
    generation_log.parent.mkdir(parents=True, exist_ok=True)
    generation_log.write_text(process.stdout + "\n" + process.stderr, encoding="utf-8")
    if process.returncode:
        raise InputContractError(f"input generation failed for {input_id}: {process.stderr[-1000:]}")
    manifest = _validate_input(input_dir, seed, control)
    if manifest.get("route_adapter_sha256") != sha256_file(ROUTE_PATH):
        raise InputContractError("generated input route-adapter hash differs from current source")
    return input_dir


def _audit_pair(corridor_dir: Path, control_dir: Path, input_root: Path,
                python_path: Path, seed: int) -> dict[str, Any]:
    command = [str(python_path), str(PAIR_AUDIT_PATH), "--corridor",
               str(corridor_dir / "sensors.bag"), "--control",
               str(control_dir / "sensors.bag"), "--expected-scans", str(EXPECTED_SCANS),
               "--expected-imu", str(EXPECTED_IMU_MESSAGES)]
    process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    result = json.loads(process.stdout)
    if result.get("paired_imu_identical") is not True:
        raise InputContractError(f"seed {seed}: paired corridor/control IMU differ")
    path = input_root / "pair_audits" / f"T14_FORMAL_DEV{seed:02d}_PAIR.json"
    _write_json(path, result)
    return result


def _run_with_retry(run: dict[str, Any], input_root: Path, output_root: Path,
                    ros_env: Path, workspace: Path, python_path: Path,
                    ledger_path: Path) -> dict[str, Any]:
    result = _run_one(run, input_root, output_root, ros_env, workspace, python_path,
                      ledger_path)
    if result["status"] == "CRASHED":
        retry = dict(run)
        retry["run_id"] = run["run_id"] + "_TECHNICAL_RETRY1"
        retry["scheduled_run_id"] = run["run_id"]
        retry_result = _run_one(retry, input_root, output_root, ros_env, workspace,
                                python_path, ledger_path)
        retry_result["technical_retry_used"] = True
        retry_result["first_attempt"] = result
        return retry_result
    return result


def _batch(args) -> int:
    seeds = args.seeds
    screen = _validate_screen(args.screen_json, seeds)
    if not args.ros_env.is_dir() or not args.workspace.is_dir():
        raise InputContractError("ROS environment and catkin workspace must exist")
    python_path = args.python.resolve() if args.python else (args.ros_env / "bin/python").resolve()
    if not python_path.is_file():
        raise InputContractError(f"Python interpreter does not exist: {python_path}")
    input_root, output_root = args.input_root.resolve(), args.output_root.resolve()
    input_root.mkdir(parents=True, exist_ok=True)
    output_root.mkdir(parents=True, exist_ok=True)
    ledger_path = output_root / "failure_ledger.csv"
    schedule = build_schedule(seeds)
    summary: dict[str, Any] = {
        "schema": "t14-batch-summary-v1", "role": "development_only",
        "profile_id": PROFILE_ID, "screen_sha256": sha256_file(args.screen_json),
        "screen_source_hash": screen["route_adapter_sha256"],
        "scheduled_primary_runs": 2 * len(seeds),
        "scheduled_repeat_runs": 4 if len(seeds) > 1 else 0,
        "eligible_seeds": list(seeds), "runs": [],
    }
    _write_json(output_root / "batch_summary.json", summary)

    pair_cache: dict[int, tuple[Path, Path]] = {}
    any_failed = False
    for row in schedule:
        seed = row["seed"]
        input_dir: Path | None = None
        try:
            if seed not in pair_cache:
                corridor_run = {"seed": seed, "scene": "CORRIDOR", "control": False,
                                "repeat": False, "run_id": f"INPUT_SEED{seed:02d}"}
                control_run = {"seed": seed, "scene": "CONTROL", "control": True,
                               "repeat": False, "run_id": f"INPUT_CONTROL{seed:02d}"}
                corridor_dir = _ensure_input(corridor_run, input_root, args.ros_env, python_path)
                control_dir = _ensure_input(control_run, input_root, args.ros_env, python_path)
                _audit_pair(corridor_dir, control_dir, input_root, python_path, seed)
                pair_cache[seed] = (corridor_dir, control_dir)
            input_dir = pair_cache[seed][1 if row["control"] else 0]
            result = _run_with_retry(row, input_root, output_root, args.ros_env,
                                     args.workspace, python_path, ledger_path)
        except (InputContractError, FileNotFoundError, subprocess.CalledProcessError,
                OSError, json.JSONDecodeError, KeyError, ValueError) as exc:
            result = _preflight_failure(row, output_root, ledger_path, "INVALID_INPUT", str(exc))
        summary["runs"].append({**row, **result,
                                "input_dir": str(input_dir) if input_dir else ""})
        any_failed |= result["status"] not in ("COMPLETED", "CACHED")
        _write_json(output_root / "batch_summary.json", summary)
        print(json.dumps(summary["runs"][-1], sort_keys=True))
    summary["counts"] = {}
    for run_result in summary["runs"]:
        status = run_result["status"]
        summary["counts"][status] = summary["counts"].get(status, 0) + 1
    summary["completed_at_utc_ns"] = time.time_ns()
    _write_json(output_root / "batch_summary.json", summary)
    return 1 if any_failed else 0


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    batch = commands.add_parser("batch", help="run the frozen development pairs and repeats")
    batch.add_argument("--screen-json", required=True, type=Path)
    batch.add_argument("--seeds", type=_seed_range, default=_seed_range("14-45"))
    batch.add_argument("--input-root", required=True, type=Path,
                       help="scratch directory for generated ROS bags and separate reference data")
    batch.add_argument("--output-root", required=True, type=Path,
                       help="ignored generated directory for per-run output/manifests")
    batch.add_argument("--ros-env", required=True, type=Path)
    batch.add_argument("--workspace", required=True, type=Path)
    batch.add_argument("--python", type=Path,
                       help="defaults to ROS_ENV/bin/python for rosbag + NumPy")
    args = parser.parse_args(argv)
    if args.command == "batch":
        raise SystemExit(_batch(args))


if __name__ == "__main__":
    main()
