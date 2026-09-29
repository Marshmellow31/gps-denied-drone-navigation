"""Write a hash-first manifest for one Point-LIO development attempt."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import tempfile
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
    parser.add_argument("--rosbag-status", type=int, default=-1)
    parser.add_argument("--node-status", type=int, default=-1)
    parser.add_argument("--pose-logger-status", type=int, default=-1)
    parser.add_argument("--roscore-status", type=int, default=-1)
    parser.add_argument("--exporter-status", type=int, default=-1)
    args = parser.parse_args()

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
        "study_split": "development_seed14_feasibility_only",
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
    meta_path = args.glog_prefix / "conda-meta"
    glog_records = sorted(meta_path.glob("glog-*.json"))
    run_manifest["build_overlay"]["glog_metadata"] = (
        {"path": str(glog_records[0]), "sha256": sha256(glog_records[0])}
        if glog_records else None
    )

    path = write_manifest_atomically(run_dir, run_manifest)
    print(f"manifest_status={args.state} manifest={path} sha256={sha256(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
