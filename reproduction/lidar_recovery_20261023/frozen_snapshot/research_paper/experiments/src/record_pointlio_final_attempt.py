"""Write a hash-first manifest for a gated Point-LIO final replication attempt."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import subprocess
import tempfile
import sys
from datetime import datetime, timezone
from pathlib import Path


NATIVE_SOURCE_FILES = (
    "CMakeLists.txt",
    "include/common_lib.h",
    "src/Estimator.cpp",
    "src/Estimator.h",
    "src/laserMapping.cpp",
    "src/li_initialization.cpp",
    "src/preprocess.h",
    "src/IndicatorSidecar.cpp",
    "src/IndicatorSidecar.h",
)
REPO_SOURCE_FILES = (
    "research_paper/experiments/src/audit_pointlio_input_frames.py",
    "research_paper/experiments/src/drain_sim_clock.py",
    "research_paper/experiments/src/pointlio_information.py",
    "research_paper/experiments/src/pointlio_indicator_export.py",
    "research_paper/experiments/src/pointlio_pose_logger.py",
    "research_paper/experiments/src/pointlio_runner_helpers.sh",
    "research_paper/experiments/src/record_pointlio_attempt.py",
    "research_paper/experiments/src/verify_pointlio_feasibility_pair.py",
    "research_paper/experiments/src/validate_pointlio_development_input.py",
    "research_paper/experiments/src/verify_pointlio_development_attempt.py",
    "research_paper/experiments/src/run_pointlio_development.py",
    "research_paper/experiments/src/dcreg_schur.py",
    "research_paper/experiments/src/final_evaluation_runner.py",
    "research_paper/evidence/pointlio_native_identity_20261009.json",
    "research_paper/experiments/src/t14_development_runner.py",
    "research_paper/evidence/t16_development_analysis_manifest.json",
    "research_paper/protocol/POINTLIO_REPLICATION_AMENDMENT_20260929.md",
    "research_paper/experiments/run_point_lio_indicator_feasibility.sh",
    "research_paper/experiments/patches/point_lio_build_compat.patch",
    "research_paper/experiments/patches/point_lio_deque_header.patch",
    "research_paper/experiments/patches/point_lio_indicator_sidecar.patch",
    "research_paper/experiments/compat/pointlio_livox_ros_driver_msgs/CMakeLists.txt",
    "research_paper/experiments/compat/pointlio_livox_ros_driver_msgs/package.xml",
    "research_paper/experiments/compat/pointlio_livox_ros_driver_msgs/msg/CustomMsg.msg",
    "research_paper/experiments/compat/pointlio_livox_ros_driver_msgs/msg/CustomPoint.msg",
    "research_paper/experiments/compat/pointlio_livox_ros_driver_msgs/LICENSE.txt",
    "research_paper/experiments/compat/pointlio_livox_ros_driver_msgs/README.md",
    "research_paper/experiments/tests/test_pointlio_information.py",
    "research_paper/experiments/tests/test_pointlio_indicator_export.py",
    "research_paper/experiments/tests/test_pointlio_feasibility_pair.py",
    "research_paper/experiments/tests/test_pointlio_attempt_recorder.py",
    "research_paper/experiments/tests/test_pointlio_pose_logger.py",
    "research_paper/experiments/tests/test_pointlio_runner_helpers.py",
    "research_paper/experiments/tests/test_pointlio_native_sidecar.py",
    "research_paper/experiments/tests/native/pointlio_sidecar_reset.cpp",
    "research_paper/experiments/src/validate_pointlio_final_input.py",
    "research_paper/experiments/src/record_pointlio_final_attempt.py",
    "research_paper/experiments/src/verify_pointlio_final_attempt.py",
    "research_paper/experiments/src/run_pointlio_final_replication.py",
    "research_paper/experiments/src/pointlio_final_analysis.py",
    "research_paper/experiments/src/r3_evaluation_workflow.py",
    "research_paper/experiments/run_point_lio_final_replication.sh",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def count_csv_rows(path: Path) -> int | None:
    if not path.is_file():
        return None
    with path.open(newline="", encoding="utf-8") as stream:
        return sum(1 for _ in csv.DictReader(stream))


def git_value(source_root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(source_root), *args],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def write_manifest_atomically(run_dir: Path, manifest: dict[str, object]) -> Path:
    """Replace the attempt manifest atomically and preserve its run identity."""
    path = run_dir / "run_manifest.json"
    immutable_keys = (
        "run_id", "mode", "study_split", "input_bag", "configuration",
        "native_binary", "native_source", "build_overlay", "repository_sources",
        "ros_master_uri",
        "seed", "scene", "control", "input_manifest", "reference_sha256",
        "reference_metadata_sha256", "stratum", "role", "execution_identity",
        "runtime",
    )
    if path.exists():
        previous = json.loads(path.read_text(encoding="utf-8"))
        for key in immutable_keys:
            if previous.get(key) != manifest.get(key):
                raise ValueError(f"attempt identity changed while recording: {key}")

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=run_dir,
            prefix=".run_manifest.", suffix=".tmp", delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(manifest, temporary, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, path)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=("on", "off"), required=True)
    parser.add_argument("--state", choices=("RUNNING", "COMPLETED", "RUN_FAILED"), required=True)
    parser.add_argument("--input-bag", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--glog-prefix", type=Path, required=True)
    parser.add_argument("--ros-master-uri", required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--study-split", choices=("development_seed14_feasibility_only", "development_replication", "final_test_replication"),
                        default="development_seed14_feasibility_only")
    parser.add_argument('--seed', type=int)
    parser.add_argument('--stratum')
    parser.add_argument('--scene', choices=('CORRIDOR', 'CONTROL'))
    parser.add_argument('--input-dir', type=Path)
    parser.add_argument('--execution-identity-json', type=Path)
    parser.add_argument("--rosbag-status", type=int, default=-1)
    parser.add_argument("--node-status", type=int, default=-1)
    parser.add_argument("--pose-logger-status", type=int, default=-1)
    parser.add_argument("--roscore-status", type=int, default=-1)
    parser.add_argument("--exporter-status", type=int, default=-1)
    args = parser.parse_args()

    if args.study_split == 'final_test_replication':
        if args.execution_identity_json is None:
            raise ValueError('final replication requires its reviewed execution identity')
        execution_identity = json.loads(args.execution_identity_json.read_text())
        from r3_evaluation_workflow import require_r3_pass
        require_r3_pass(Path(execution_identity['r3_review_path']),
                        Path(execution_identity['implementation_freeze_path']))

    run_dir = args.run_dir.resolve()
    if not run_dir.is_dir():
        raise SystemExit(f"run directory does not exist: {run_dir}")
    native_hashes = {
        name: sha256(args.source_root / name) for name in NATIVE_SOURCE_FILES
    }
    repo_hashes = {
        name: sha256(args.repo_root / name) for name in REPO_SOURCE_FILES
    }
    sidecar_dir = run_dir / "sidecar"
    outputs = {
        str(path.relative_to(run_dir)): sha256(path)
        for path in sorted(run_dir.rglob("*"))
        if path.is_file() and path.name != "run_manifest.json"
    }
    run_manifest = {
        "schema_version": 1,
        "run_id": run_dir.name,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": args.state,
        "mode": args.mode,
        "study_split": args.study_split,
        "threshold_fit_performed": False,
        "heldout_inputs_opened": False,
        "input_bag": {
            "path": str(args.input_bag.resolve()),
            "bytes": args.input_bag.stat().st_size,
            "sha256": sha256(args.input_bag),
        },
        "configuration": {
            "path": str(args.config.resolve()),
            "sha256": sha256(args.config),
        },
        "native_binary": {
            "path": str(args.binary.resolve()),
            "sha256": sha256(args.binary),
        },
        "native_source": {
            "root": str(args.source_root.resolve()),
            "commit": git_value(args.source_root, "rev-parse", "HEAD"),
            "dirty_patch_sha256": hashlib.sha256(
                subprocess.run(
                    ["git", "-C", str(args.source_root), "diff", "--binary", "HEAD"],
                    check=True, capture_output=True,
                ).stdout
            ).hexdigest(),
            "files": native_hashes,
        },
        "build_overlay": {
            "glog_prefix": str(args.glog_prefix.resolve()),
            "glog_metadata": {
                "glog": next(iter((args.glog_prefix / "conda-meta").glob("glog-*.json")), Path("")),
            },
        },
        "ros_master_uri": args.ros_master_uri,
        "repository_sources": repo_hashes,
        "process_exit_codes": {
            "rosbag": args.rosbag_status,
            "pointlio": args.node_status,
            "pose_logger": args.pose_logger_status,
            "roscore": args.roscore_status,
            "exporter": args.exporter_status,
        },
        "counts": {
            "input_frames": count_csv_rows(run_dir / "input_header_stamps.csv"),
            "emitted_pose_rows": count_csv_rows(run_dir / "poses.csv"),
            "sidecar_frames": count_csv_rows(sidecar_dir / "frame_ledger.csv"),
            "sidecar_groups": count_csv_rows(sidecar_dir / "measurement_groups.csv"),
            "sidecar_jacobian_rows": count_csv_rows(sidecar_dir / "jacobian_rows.csv"),
            "indicator_rows": count_csv_rows(run_dir / "pointlio_indicators.csv"),
        },
        "output_sha256": outputs,
    }
    import numpy as np
    history = Path(sys.prefix) / 'conda-meta/history'
    run_manifest['runtime'] = {
        'python': platform.python_version(), 'numpy': np.__version__,
        'python_executable': str(Path(sys.executable).resolve()),
        'python_binary_sha256': sha256(Path(sys.executable).resolve()),
        'conda_history_sha256': sha256(history) if history.is_file() else None,
    }
    meta_path = args.glog_prefix / "conda-meta"
    glog_records = sorted(meta_path.glob("glog-*.json"))
    run_manifest["build_overlay"]["glog_metadata"] = (
        {"path": str(glog_records[0]), "sha256": sha256(glog_records[0])}
        if glog_records else None
    )

    if args.study_split == 'development_replication':
        from validate_pointlio_development_input import validate_input, validate_native, glog_identity
        slot = validate_input(args.input_bag)
        validate_native(args.binary, args.source_root, args.config)
        if args.mode != 'on':
            raise ValueError('development replication requires the measurement sidecar')
        run_manifest.update(slot)
        run_manifest['build_overlay'] = glog_identity(args.glog_prefix)
    elif args.study_split == 'final_test_replication':
        from validate_pointlio_final_input import validate
        from validate_pointlio_development_input import validate_native, glog_identity
        if args.mode != 'on' or args.seed is None or not args.stratum or not args.scene or args.input_dir is None:
            raise ValueError('final replication requires sidecar-on and an exact scheduled input slot')
        if args.execution_identity_json is None:
            raise ValueError('final replication requires its reviewed execution identity')
        execution_identity = json.loads(args.execution_identity_json.read_text())
        from r3_evaluation_workflow import require_r3_pass
        gate = require_r3_pass(Path(execution_identity['r3_review_path']),
                               Path(execution_identity['implementation_freeze_path']))
        if any(execution_identity.get(key) != gate.get(key) for key in
               ('r3_review_sha256', 'implementation_freeze_sha256', 'reviewed_artifact_hashes')):
            raise ValueError('current R3 review/freeze differs from the Point-LIO launch identity')
        slot = validate(args.input_dir, args.seed, args.stratum, args.scene,
                        args.execution_identity_json)
        if slot['sensor_bag_sha256'] != sha256(args.input_bag):
            raise ValueError('final input bag differs from the validated slot')
        validate_native(args.binary, args.source_root, args.config)
        run_manifest.update({key: slot[key] for key in
                             ('seed', 'stratum', 'scene', 'control', 'input_manifest',
                              'reference_sha256', 'reference_metadata_sha256')})
        run_manifest['role'] = 'heldout'
        run_manifest['heldout_inputs_opened'] = True
        run_manifest['execution_identity'] = execution_identity
        run_manifest['build_overlay'] = glog_identity(args.glog_prefix)

    path = write_manifest_atomically(run_dir, run_manifest)
    print(f"manifest_status={args.state} manifest={path} sha256={sha256(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
