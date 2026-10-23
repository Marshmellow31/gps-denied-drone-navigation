"""Verify the retained Point-LIO seed-14 sidecar-on/off feasibility pair."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit

from pointlio_information import join_emitted_pose_segments
from pointlio_indicator_export import verify_input_frame_coverage


EXPECTED_SEED14_BAG_SHA256 = "89f4ac21b24a2b9dfc86b74cd3d082e48365ac1ed63207b08969e7aca25d4627"
EXPECTED_POINTLIO_CONFIG_SHA256 = "d23bd8799c3834ac0acc1d23476a0a0c0cd72b09f7b7c542b5bfbe9813a4c98b"
PINNED_POINTLIO_COMMIT = "4b86a469eb5572e70ed575af25b5f15dd06e8e3c"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def verify_manifest_outputs(run_dir: Path, manifest: Mapping[str, object]) -> None:
    expected = manifest.get("output_sha256")
    require(isinstance(expected, dict), f"{run_dir.name} manifest lacks output hashes")
    actual = {
        str(path.relative_to(run_dir)): sha256(path)
        for path in sorted(run_dir.rglob("*"))
        if path.is_file() and path.name != "run_manifest.json"
    }
    require(actual == expected,
            f"{run_dir.name} files changed or are missing since the run manifest")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def verify_pair(sidecar_on: Path, sidecar_off: Path) -> dict[str, object]:
    on_manifest_path = sidecar_on / "run_manifest.json"
    off_manifest_path = sidecar_off / "run_manifest.json"
    on_manifest = json.loads(on_manifest_path.read_text(encoding="utf-8"))
    off_manifest = json.loads(off_manifest_path.read_text(encoding="utf-8"))
    verify_manifest_outputs(sidecar_on, on_manifest)
    verify_manifest_outputs(sidecar_off, off_manifest)
    require(on_manifest["status"] == "COMPLETED", "sidecar-on run is not complete")
    require(off_manifest["status"] == "COMPLETED", "sidecar-off run is not complete")
    require(on_manifest["mode"] == "on" and off_manifest["mode"] == "off",
            "run modes are not one on and one off")
    for manifest in (on_manifest, off_manifest):
        require(manifest["study_split"] == "development_seed14_feasibility_only",
                "run is not explicitly marked seed-14 feasibility-only")
        require(manifest["threshold_fit_performed"] is False,
                "a feasibility attempt must not fit a threshold")
        require(manifest["heldout_inputs_opened"] is False,
                "held-out access is forbidden in this feasibility check")
        statuses = manifest["process_exit_codes"]
        require(statuses["rosbag"] == 0 and statuses["pointlio"] == 0
                and statuses["pose_logger"] == 0,
                "a required process did not exit successfully")
        require(statuses["roscore"] in (0, 130),
                "isolated ROS master did not shut down cleanly")
        ros_master = urlsplit(str(manifest["ros_master_uri"]))
        require(ros_master.scheme == "http" and ros_master.hostname == "127.0.0.1"
                and ros_master.port is not None,
                "run did not use its recorded isolated loopback ROS master")
        bag_path_parts = Path(manifest["input_bag"]["path"]).parts
        require(manifest["input_bag"]["sha256"] == EXPECTED_SEED14_BAG_SHA256,
                "input is not the pinned seed-14 development bag")
        require(bag_path_parts[-3:] == (
            "t14_retained_inputs",
            "T14_FORMAL_DEV14_CORRIDOR_INPUT_XM6_V1",
            "sensors.bag",
        ), "input path is not the retained seed-14 corridor input")
        require(manifest["configuration"]["sha256"] == EXPECTED_POINTLIO_CONFIG_SHA256,
                "Point-LIO configuration hash is not the reviewed development profile")
        require(manifest["native_source"]["commit"] == PINNED_POINTLIO_COMMIT,
                "Point-LIO upstream commit is not the pinned T15 revision")
    for key in ("input_bag", "configuration", "native_binary", "native_source",
                "build_overlay", "repository_sources"):
        require(on_manifest[key] == off_manifest[key],
                f"on/off {key} identities differ")
    require(on_manifest["process_exit_codes"]["exporter"] == 0,
            "sidecar-on postprocessor did not pass")
    require(off_manifest["process_exit_codes"]["exporter"] == -2,
            "sidecar-off manifest must state that export was not run")

    on_pose = sidecar_on / "poses.csv"
    off_pose = sidecar_off / "poses.csv"
    on_pose_hash = sha256(on_pose)
    off_pose_hash = sha256(off_pose)
    require(on_pose_hash == off_pose_hash,
            "sidecar-on/off pose CSVs are not byte-identical")
    on_input_audit = sidecar_on / "input_header_stamps.csv"
    off_input_audit = sidecar_off / "input_header_stamps.csv"
    require(sha256(on_input_audit) == sha256(off_input_audit),
            "on/off raw input audits differ")

    expected_rows = read_rows(on_input_audit)
    frame_rows = read_rows(sidecar_on / "sidecar" / "frame_ledger.csv")
    indicator_rows = read_rows(sidecar_on / "pointlio_indicators.csv")
    verify_input_frame_coverage(frame_rows,
                                [int(row["header_stamp_ns"]) for row in expected_rows])
    expected_ids = list(range(1, len(expected_rows) + 1))
    frame_ids = [int(row["frame_id"]) for row in frame_rows]
    indicator_ids = [int(row["frame_id"]) for row in indicator_rows]
    require(sorted(frame_ids) == expected_ids,
            "frame ledger IDs are missing, duplicated, or non-monotonic")
    require(sorted(indicator_ids) == expected_ids,
            "indicator output does not contain one row per input frame")
    require(all(row["run_state"] == "COMPLETE" for row in frame_rows),
            "one or more native frames are incomplete")
    require(all(row["run_state"] == "COMPLETE" for row in indicator_rows),
            "one or more exported indicator frames are incomplete")

    poses = read_rows(on_pose)
    reset_events = read_rows(sidecar_on / "sidecar" / "reset_events.csv")
    joined = join_emitted_pose_segments(poses, indicator_rows, reset_events)
    require(len(joined) > 0, "no Point-LIO poses were emitted")
    pose_ids = [int(row["source_frame_id"]) for row in joined]
    require(len(set(pose_ids)) == len(pose_ids), "duplicate pose frame identity")
    require(all(frame_id in set(frame_ids) for frame_id in pose_ids),
            "an emitted pose has no raw input frame")

    return {
        "schema_version": 1,
        "status": "PASS",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "development_only": True,
        "seed": 14,
        "threshold_fit_performed": False,
        "heldout_inputs_opened": False,
        "rosbag_sha256": on_manifest["input_bag"]["sha256"],
        "configuration_sha256": on_manifest["configuration"]["sha256"],
        "binary_sha256": on_manifest["native_binary"]["sha256"],
        "native_source_commit": on_manifest["native_source"]["commit"],
        "input_frame_count": len(expected_rows),
        "frame_ledger_count": len(frame_rows),
        "indicator_row_count": len(indicator_rows),
        "pose_row_count": len(joined),
        "poses_sha256": on_pose_hash,
        "sidecar_on_manifest_sha256": sha256(on_manifest_path),
        "sidecar_off_manifest_sha256": sha256(off_manifest_path),
        "reset_event_count": len(reset_events),
        "notes": [
            "This is a one-seed feasibility check, not a new independent event.",
            "It does not select or fit a Point-LIO operating threshold.",
            "The native sidecar outputs are separate from held-out evaluation data.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sidecar-on", type=Path, required=True)
    parser.add_argument("--sidecar-off", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = verify_pair(args.sidecar_on, args.sidecar_off)
    except Exception as exc:
        result = {
            "schema_version": 1,
            "status": "REVISE",
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "development_only": True,
            "seed": 14,
            "threshold_fit_performed": False,
            "heldout_inputs_opened": False,
            "failure": f"{type(exc).__name__}: {exc}",
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"feasibility_pair={result['status']} output={args.output}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
