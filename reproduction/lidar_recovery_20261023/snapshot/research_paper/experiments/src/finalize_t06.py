"""Summarize a completed FAST-LIO development replay without reading reference truth."""

import argparse
import ast
import csv
import hashlib
import json
import os
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml
import rosbag
import rospy


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> bytes:
    return subprocess.check_output(("git", *args))


def resource(path: Path) -> dict:
    values = {}
    for line in path.read_text().splitlines():
        if ":" in line:
            key, value = line.strip().split(":", 1)
            values[key] = value.strip()
    elapsed = next((line.strip().split(": ", 1)[-1] for line in path.read_text().splitlines()
                    if line.strip().startswith("Elapsed (wall clock) time")), None)
    return {
        "elapsed_wall_text": elapsed,
        "max_rss_bytes": int(values["Maximum resident set size (kbytes)"]) * 1024,
        "exit_status": int(values["Exit status"]),
        "measurement": "GNU /usr/bin/time -v",
    }


def artifact(path: Path, rows: int | None = None) -> dict:
    if not path.exists():
        return {"path": str(path), "available": False, "reason": "not produced"}
    result = {"path": str(path), "available": True, "size_bytes": path.stat().st_size, "sha256": sha256(path)}
    if rows is not None:
        result["rows"] = rows
    return result


def file_birth_utc(path: Path) -> datetime:
    seconds = int(subprocess.check_output(("/usr/bin/stat", "-c", "%W", str(path))).decode().strip())
    if seconds <= 0:
        raise RuntimeError(f"filesystem creation time unavailable for {path}")
    return datetime.fromtimestamp(seconds, timezone.utc)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--start-seconds", type=float, default=0.0)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    project = Path(__file__).resolve().parents[2]
    root = project.parent
    config = project / "configs/fastlio_geode_alpha_exploratory.yaml"
    bag = project / "experiments/generated/raw/geode/Urban_Tunnel01/bag/Urban_Tunnel01_lidar_imu.bag"
    with (run_dir / "poses.csv").open(newline="", encoding="utf-8") as stream:
        poses = list(csv.DictReader(stream))
    valid = [row for row in poses if row["event"] == "POSE" and row["valid"] == "true"]
    resets = sum(row["event"] == "RESET" for row in poses)
    if valid:
        times = [int(row["timestamp_ns"]) for row in valid]
        assert times == sorted(times), "pose timestamps regressed"
    backend_log = (run_dir / "backend.log").read_text(errors="replace")
    adapter_log = (run_dir / "adapter.log").read_text(errors="replace")
    adapter_counts = re.findall(r"GEODE adapter counts: (\{[^\n]+\})", adapter_log)
    parsed_adapter_counts = ast.literal_eval(adapter_counts[-1]) if adapter_counts else None
    player_usage = resource(run_dir / "player_resource.txt")
    backend_usage = resource(run_dir / "backend_resource.txt")
    expected_bag_hash = "4d479cefb4e5dd1a5b14de95b0dc50377b2ab431135b9c5a766112869597cc17"
    assert sha256(bag) == expected_bag_hash
    tracked_diff = git("diff", "--binary", "HEAD")
    untracked = git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
    dirty_digest = hashlib.sha256(tracked_diff)
    for raw_name in sorted(filter(None, untracked)):
        name = raw_name.decode()
        if name == "research_paper/AGENT_EXECUTION_PLAN.md":
            continue  # supplied plan is recorded as an input, not adapter code
        path = root / name
        dirty_digest.update(raw_name)
        dirty_digest.update(sha256(path).encode())
    start = file_birth_utc(run_dir / "player.log")
    end = datetime.fromtimestamp((run_dir / "backend_resource.txt").stat().st_mtime, timezone.utc)
    outputs = {name: artifact(run_dir / name, len(poses) if name == "poses.csv" else None)
               for name in ("poses.csv", "backend.log", "adapter.log", "pose_logger.log",
                            "player.log", "backend_resource.txt", "player_resource.txt")}
    with rosbag.Bag(str(bag)) as source_bag:
        start_time = rospy.Time.from_sec(source_bag.get_start_time() + args.start_seconds)
        scan_count = sum(1 for _ in source_bag.read_messages(
            topics=["/velodyne_points"], start_time=start_time))
    completed = (player_usage["exit_status"] == 0 and backend_usage["exit_status"] == 0
                 and len(valid) > 0 and times[-1] >= 1693022293_000_000_000
                 and parsed_adapter_counts == {"seen": scan_count, "published": scan_count, "failed": 0})
    manifest = {
        "schema_version": "lidar-recovery/0.1",
        "run_id": run_dir.name,
        "sequence_id": "GEODE_Urban_Tunnel01",
        "role": "development",
        "input": {"path": str(bag), "size_bytes": bag.stat().st_size, "sha256": expected_bag_hash,
                  "topics": ["/imu/data", "/velodyne_points"],
                  "source": "https://github.com/PengYu-Team/GEODE_dataset",
                  "license_status": "dataset reuse terms not stated in inspected release"},
        "code": {"repository_commit": git("rev-parse", "HEAD").decode().strip(),
                 "dirty": bool(tracked_diff or any(untracked)), "dirty_diff_sha256": dirty_digest.hexdigest(),
                 "backend": "FAST-LIO2", "backend_revision": "7cc4175de6f8ba2edf34bab02a42195b141027e9",
                 "ikd_tree_revision": "e2e3f4e9d3b95a9e66b1ba83dc98d4a05ed8a3c4",
                 "backend_patch_sha256": sha256(project / "experiments/patches/fast_lio_pcl17.patch"),
                 "adapter_sha256": sha256(project / "experiments/src/velodyne_time_adapter.py"),
                 "pose_logger_sha256": sha256(project / "experiments/src/pose_logger.py")},
        "configuration": {"path": str(config), "sha256": sha256(config), "effective": yaml.safe_load(config.read_text()),
                          "extrinsic_interpretation": "provisional T_IMU_LiDAR: LiDAR coordinates into IMU coordinates",
                          "extrinsic_source": "GEODE alpha_config.yaml revision c6e930623d4fed450d7fc50e16e3ffe0288b692b",
                          "extrinsic_verified": False,
                          "backend_pose": "T_camera_init_body, inferred IMU-state body from FAST-LIO source; reference-body match unverified",
                          "clock_id": "geode_ros_header_unix"},
        "seed": None, "deterministic": True,
        "environment": {"os": platform.platform(), "architecture": platform.machine(),
                        "cpu": platform.processor(),
                        "ram_bytes": os.sysconf("SC_PHYS_PAGES") * os.sysconf("SC_PAGE_SIZE"),
                        "ros": "Noetic 1.17.4 via RoboStack", "python": platform.python_version(),
                        "compiler": "GCC 15.3.0 in isolated Conda; C++17", "host_pseudonym": "local-laptop-1"},
        "invocation": {"player_argv": ["rosbag", "play", "-q", "--clock", "-r", "1", str(bag),
                                       "/velodyne_points:=/velodyne_points_raw"]
                                       if args.start_seconds == 0 else
                                       ["rosbag", "play", "-q", "--clock", "-r", "1", "-s",
                                        str(args.start_seconds), str(bag),
                                        "/velodyne_points:=/velodyne_points_raw"],
                       "backend_argv": ["rosrun", "fast_lio", "fastlio_mapping"],
                       "adapter_argv": ["python", "research_paper/experiments/src/velodyne_time_adapter.py"],
                       "logger_argv": ["python", "research_paper/experiments/src/pose_logger.py", "--output", str(run_dir / "poses.csv")],
                       "cwd": str(root), "start_utc": start.isoformat(), "end_utc": end.isoformat(),
                       "time_origin_ns": 1693022008716670513,
                       "player_runtime": player_usage, "backend_runtime": backend_usage},
        "status": {"state": "completed" if completed else "partial", "player_exit_code": player_usage["exit_status"],
                   "backend_exit_code": backend_usage["exit_status"],
                   "state_meaning": "execution and stream completeness only; not trajectory accuracy",
                   "trajectory_quality": "not assessed by this online-only manifest",
                   "expected_lidar_scans": scan_count, "output_pose_count": len(valid),
                   "replay_start_offset_s": args.start_seconds,
                   "expected_pose_count_upper_bound": scan_count,
                   "invalid_pose_count": len(poses) - len(valid) - resets, "reset_count": resets,
                   "first_pose_ns": times[0] if valid else None, "last_pose_ns": times[-1] if valid else None,
                   "warning_count": backend_log.count("[WARN]"),
                   "no_effective_points_warning_count": backend_log.count("No Effective Points"),
                   "warnings_first_100": [line for line in backend_log.splitlines() if "[WARN]" in line][:100],
                   "adapter_shutdown_counts": parsed_adapter_counts},
        "outputs": outputs,
        "limitations": ["published extrinsic direction unverified", "reference body convention unverified",
                        "no reference used by backend or online adapter", "development sequence only"],
    }
    path = run_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"state": manifest["status"]["state"], "poses": len(valid),
                      "last_pose_ns": manifest["status"]["last_pose_ns"],
                      "backend_max_rss_bytes": backend_usage["max_rss_bytes"]}))


if __name__ == "__main__":
    main()
