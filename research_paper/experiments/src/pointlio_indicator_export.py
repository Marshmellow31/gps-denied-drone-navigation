"""Validate and turn the native Point-LIO sidecar into frame indicators.

This postprocessor consumes Point-LIO's retained measurement rows only. It
does not read trajectory truth, event labels, or choose any operating cutoff.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping

import numpy as np

from pointlio_information import (
    PointLioGroupRows,
    compute_pointlio_frame,
    is_valid_rotation,
    join_emitted_pose_segments,
    transport_group_rows_to_world,
)


FRAME_FIELDS = (
    "frame_id", "input_header_stamp_ns", "timestamp_ns", "timestamp_source",
    "segment_id", "source_stage", "frame_state", "run_state",
    "unavailable_reason", "expected_group_count", "processed_group_count",
    "empty_group_count", "accepted_count",
)
GROUP_FIELDS = (
    "frame_id", "group_index", "group_timestamp_ns", "callback_count",
    "accepted_count", "rotation_snapshot_present",
)
ROW_FIELDS = (
    "frame_id", "group_index", "group_timestamp_ns", "row_index",
    *(f"R{row}{col}" for row in range(3) for col in range(3)),
    *(f"J_body{col}" for col in range(6)),
    *(f"J_common{col}" for col in range(6)),
)
BASE_OUTPUT_FIELDS = (
    "frame_id", "input_header_stamp_ns", "timestamp_ns", "timestamp_source",
    "segment_id", "source_stage", "run_state", "valid",
    "unavailable_reason", "expected_group_count", "processed_group_count",
    "empty_group_count", "accepted_count",
    "lambda_min_1m", "lambda_min_3m", "lambda_min_5m",
    "DCREG_state", "DCREG_HEALTH_SCORE",
)
DCREG_OUTPUT_FIELDS = (
    *(f"lambda_R_{i}" for i in range(3)),
    *(f"lambda_t_{i}" for i in range(3)),
    *(name for i in range(3) for name in
      (f"kappa_R_{i}", f"kappa_R_{i}_unbounded", f"kappa_R_{i}_flagged")),
    *(name for i in range(3) for name in
      (f"kappa_t_{i}", f"kappa_t_{i}_unbounded", f"kappa_t_{i}_flagged")),
)
OUTPUT_FIELDS = BASE_OUTPUT_FIELDS + DCREG_OUTPUT_FIELDS


def _read_csv(path: Path, required: Iterable[str]) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        missing = set(required) - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path} is missing columns: {sorted(missing)}")
        return list(reader)


def _integer(row: Mapping[str, str], key: str) -> int:
    try:
        return int(row[key])
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"invalid integer field {key!r}: {row.get(key)!r}") from exc


def _matrix_from_fields(row: Mapping[str, str], prefix: str) -> np.ndarray:
    return np.asarray([
        [float(row[f"{prefix}{r}{c}"]) for c in range(3)]
        for r in range(3)
    ], dtype=np.float64)


def verify_input_frame_coverage(
    frame_rows: Iterable[Mapping[str, str]],
    expected_header_stamps_ns: Iterable[int],
) -> None:
    """Require one native ledger row for every raw input cloud by header time."""
    frames = list(frame_rows)
    expected = [int(value) for value in expected_header_stamps_ns]
    actual = [_integer(frame, "input_header_stamp_ns") for frame in frames]
    if len(actual) != len(expected):
        raise ValueError(
            f"raw input/ledger frame count mismatch: {len(expected)} != {len(actual)}"
        )
    if len(set(actual)) != len(actual):
        raise ValueError("native frame ledger contains duplicate input timestamps")
    missing = Counter(expected) - Counter(actual)
    extra = Counter(actual) - Counter(expected)
    if missing or extra:
        raise ValueError(
            f"raw input/ledger timestamps differ; missing={list(missing.elements())[:5]}, "
            f"extra={list(extra.elements())[:5]}"
        )


def _numeric_failure_frame(frame: Mapping[str, str], reason: str,
                           accepted_count: int | None,
                           empty_group_count: int | None) -> dict[str, object]:
    return {
        "frame_id": _integer(frame, "frame_id"),
        "input_header_stamp_ns": _integer(frame, "input_header_stamp_ns"),
        "timestamp_ns": _integer(frame, "timestamp_ns"),
        "timestamp_source": frame["timestamp_source"],
        "segment_id": _integer(frame, "segment_id"),
        "source_stage": frame["source_stage"],
        "run_state": "COMPLETE",
        "valid": False,
        "unavailable_reason": reason,
        "expected_group_count": _integer(frame, "expected_group_count"),
        "processed_group_count": _integer(frame, "processed_group_count"),
        "empty_group_count": empty_group_count,
        "accepted_count": accepted_count,
    }


def _contract_failure_frame(frame: Mapping[str, str], reason: str,
                            accepted_count: int | None,
                            empty_group_count: int | None) -> dict[str, object]:
    row = _numeric_failure_frame(frame, reason, accepted_count, empty_group_count)
    row["run_state"] = "RUN_INCOMPLETE"
    return row


def _unavailable_frame(frame: Mapping[str, str]) -> dict[str, object]:
    run_state = frame["run_state"]
    reason = frame["unavailable_reason"]
    result: dict[str, object] = {
        "frame_id": _integer(frame, "frame_id"),
        "input_header_stamp_ns": _integer(frame, "input_header_stamp_ns"),
        "timestamp_ns": _integer(frame, "timestamp_ns"),
        "timestamp_source": frame["timestamp_source"],
        "segment_id": _integer(frame, "segment_id"),
        "source_stage": frame["source_stage"],
        "run_state": run_state,
        "valid": False,
        "unavailable_reason": reason,
        "expected_group_count": _integer(frame, "expected_group_count"),
        "processed_group_count": _integer(frame, "processed_group_count"),
        "empty_group_count": _integer(frame, "empty_group_count"),
        "accepted_count": _integer(frame, "accepted_count"),
    }
    return result


def _build_frame_groups(
    frame_id: int,
    group_rows: Iterable[Mapping[str, str]],
    jacobian_rows: Iterable[Mapping[str, str]],
) -> tuple[list[PointLioGroupRows], bool]:
    by_group: dict[int, dict[str, object]] = {}
    numeric_capture_failure = False
    for group in group_rows:
        group_id = _integer(group, "group_index")
        if group_id in by_group:
            raise ValueError(f"duplicate group {group_id} in frame {frame_id}")
        if _integer(group, "callback_count") != 1:
            raise ValueError(
                f"measurement callback count is not one for frame {frame_id}, group {group_id}"
            )
        if group["rotation_snapshot_present"].lower() != "true":
            raise ValueError(
                f"pre-update rotation snapshot missing for frame {frame_id}, group {group_id}"
            )
        by_group[group_id] = {
            "timestamp_ns": _integer(group, "group_timestamp_ns"),
            "accepted_count": _integer(group, "accepted_count"),
            "rotation": _matrix_from_fields(group, "R"),
            "rows": [],
        }
        if not is_valid_rotation(by_group[group_id]["rotation"]):
            numeric_capture_failure = True

    for row in jacobian_rows:
        group_id = _integer(row, "group_index")
        if group_id not in by_group:
            raise ValueError(f"Jacobian row has no group ledger: {frame_id}/{group_id}")
        group = by_group[group_id]
        if _integer(row, "group_timestamp_ns") != group["timestamp_ns"]:
            raise ValueError(f"group timestamp mismatch for frame {frame_id}, group {group_id}")
        row_index = _integer(row, "row_index")
        body = np.asarray([float(row[f"J_body{i}"]) for i in range(6)], dtype=np.float64)
        common = np.asarray([float(row[f"J_common{i}"]) for i in range(6)], dtype=np.float64)
        row_rotation = _matrix_from_fields(row, "R")
        if not np.array_equal(row_rotation, group["rotation"]):
            if not np.allclose(row_rotation, group["rotation"], rtol=0.0, atol=1e-14,
                               equal_nan=True):
                raise ValueError(f"rotation snapshot mismatch for frame {frame_id}, group {group_id}")
        row_is_finite = (np.isfinite(body).all() and np.isfinite(common).all()
                         and is_valid_rotation(group["rotation"])
                         and is_valid_rotation(row_rotation))
        if not row_is_finite:
            numeric_capture_failure = True
        else:
            expected = transport_group_rows_to_world(body.reshape(1, 6), group["rotation"])[0]
            if not np.allclose(common, expected, rtol=1e-12, atol=1e-12):
                raise ValueError(
                    f"source-row reconstruction mismatch for frame {frame_id}, group {group_id}, row {row_index}"
                )
        group["rows"].append((row_index, body))

    result = []
    for group_id in sorted(by_group):
        group = by_group[group_id]
        rows = sorted(group["rows"], key=lambda item: item[0])
        if [index for index, _ in rows] != list(range(len(rows))):
            raise ValueError(f"non-unique/non-contiguous row indices for frame {frame_id}, group {group_id}")
        if len(rows) != group["accepted_count"]:
            raise ValueError(f"accepted-row count mismatch for frame {frame_id}, group {group_id}")
        matrix = (np.vstack([row for _, row in rows]) if rows
                  else np.empty((0, 6), dtype=np.float64))
        result.append(PointLioGroupRows(
            group_index=group_id,
            jacobian_body=matrix,
            rotation_world_body_preupdate=group["rotation"],
        ))
    return result, numeric_capture_failure


def _populate_scores(frame: Mapping[str, str],
                     result: Mapping[str, object]) -> dict[str, object]:
    row = _unavailable_frame(frame)
    row.update({
        "run_state": result["run_state"],
        "valid": result["valid"],
        "unavailable_reason": result["unavailable_reason"],
        "expected_group_count": result["expected_group_count"],
        "processed_group_count": result["processed_group_count"],
        "empty_group_count": result["empty_group_count"],
        "accepted_count": result["accepted_count"],
    })
    if not result["valid"]:
        return row
    for scale in (1, 3, 5):
        row[f"lambda_min_{scale}m"] = result[f"lambda_min_{scale}m"]
    dcreg = result["dcreg"]
    row["DCREG_state"] = dcreg.state
    row["DCREG_HEALTH_SCORE"] = dcreg.health_score
    for prefix, eigenvalues in (("lambda_R", dcreg.rotation_eigenvalues),
                                ("lambda_t", dcreg.translation_eigenvalues)):
        for index, value in enumerate(eigenvalues):
            row[f"{prefix}_{index}"] = value
    for prefix, kappas, flags in (
        ("kappa_R", dcreg.rotation_kappas, dcreg.rotation_flags),
        ("kappa_t", dcreg.translation_kappas, dcreg.translation_flags),
    ):
        for index, value in enumerate(kappas):
            unbounded = math.isinf(value)
            row[f"{prefix}_{index}"] = "" if unbounded else value
            row[f"{prefix}_{index}_unbounded"] = str(unbounded).lower()
            row[f"{prefix}_{index}_flagged"] = str(flags[index]).lower()
    return row


def export_sidecar(
    frame_ledger_path: Path,
    group_ledger_path: Path,
    jacobian_rows_path: Path,
    output_path: Path,
    *,
    expected_header_stamps_ns: Iterable[int] | None = None,
    pose_path: Path | None = None,
    reset_events_path: Path | None = None,
    segmented_poses_path: Path | None = None,
) -> list[dict[str, object]]:
    frames = _read_csv(frame_ledger_path, FRAME_FIELDS)
    group_rows = _read_csv(group_ledger_path, GROUP_FIELDS)
    jacobian_rows = _read_csv(jacobian_rows_path, ROW_FIELDS)
    if expected_header_stamps_ns is not None:
        verify_input_frame_coverage(frames, expected_header_stamps_ns)

    frames_by_id: dict[int, dict[str, str]] = {}
    for frame in frames:
        frame_id = _integer(frame, "frame_id")
        if frame_id in frames_by_id:
            raise ValueError(f"duplicate frame ledger row {frame_id}")
        frames_by_id[frame_id] = frame

    groups_by_frame: dict[int, list[dict[str, str]]] = defaultdict(list)
    for group in group_rows:
        frame_id = _integer(group, "frame_id")
        if frame_id not in frames_by_id:
            raise ValueError(f"group ledger references missing frame {frame_id}")
        groups_by_frame[frame_id].append(group)

    rows_by_frame_group: dict[tuple[int, int], list[dict[str, str]]] = defaultdict(list)
    for jacobian in jacobian_rows:
        frame_id = _integer(jacobian, "frame_id")
        group_id = _integer(jacobian, "group_index")
        if frame_id not in frames_by_id:
            raise ValueError(f"Jacobian row references missing frame {frame_id}")
        rows_by_frame_group[(frame_id, group_id)].append(jacobian)

    output_rows: list[dict[str, object]] = []
    for frame_id in sorted(frames_by_id):
        frame = frames_by_id[frame_id]
        state = frame["frame_state"]
        if frame["run_state"] == "RUN_INCOMPLETE" or state == "RUN_INCOMPLETE":
            output_rows.append(_unavailable_frame(frame))
            continue
        if state not in {"READY", "UNAVAILABLE"}:
            row = _unavailable_frame(frame)
            row["run_state"] = "RUN_INCOMPLETE"
            row["unavailable_reason"] = "UNKNOWN_FRAME_LEDGER_STATE"
            output_rows.append(row)
            continue

        groups_meta = groups_by_frame.get(frame_id, [])
        expected_count = _integer(frame, "expected_group_count")
        processed_count = _integer(frame, "processed_group_count")
        if frame["source_stage"] != "MEASUREMENT":
            has_rows = any(key[0] == frame_id for key in rows_by_frame_group)
            if expected_count != 0 or processed_count != 0 or groups_meta or has_rows:
                output_rows.append(_contract_failure_frame(
                    frame, "UNAVAILABLE_FRAME_HAS_MEASUREMENT_GROUPS",
                    _integer(frame, "accepted_count"),
                    _integer(frame, "empty_group_count"),
                ))
            else:
                output_rows.append(_unavailable_frame(frame))
            continue

        declared_group_ids = {_integer(group, "group_index") for group in groups_meta}
        stray_group_rows = [key for key in rows_by_frame_group
                            if key[0] == frame_id and key[1] not in declared_group_ids]
        if stray_group_rows:
            output_rows.append(_contract_failure_frame(
                frame, "JACOBIAN_ROW_WITHOUT_GROUP_LEDGER",
                _integer(frame, "accepted_count"),
                _integer(frame, "empty_group_count"),
            ))
            continue
        groups: list[PointLioGroupRows] = []
        try:
            groups, numeric_capture_failure = _build_frame_groups(
                frame_id,
                groups_meta,
                [row for group_id in sorted(
                    _integer(group, "group_index") for group in groups_meta
                ) for row in rows_by_frame_group.get((frame_id, group_id), [])],
            )
        except ValueError as exc:
            output_rows.append(_contract_failure_frame(
                frame, f"SIDECAR_CONTRACT_FAILURE:{exc}",
                _integer(frame, "accepted_count"),
                _integer(frame, "empty_group_count"),
            ))
            continue

        group_accepted_count = sum(len(group.jacobian_body) for group in groups)
        group_empty_count = sum(len(group.jacobian_body) == 0 for group in groups)
        if (len(groups) != expected_count
                or len(groups) != processed_count
                or group_accepted_count != _integer(frame, "accepted_count")
                or group_empty_count != _integer(frame, "empty_group_count")):
            output_rows.append(_contract_failure_frame(
                frame, "SIDE_CAR_GROUP_COUNT_MISMATCH",
                group_accepted_count, group_empty_count,
            ))
            continue
        if numeric_capture_failure:
            output_rows.append(_numeric_failure_frame(
                frame, "INDICATOR_NUMERIC_FAILURE",
                group_accepted_count, group_empty_count,
            ))
            continue

        result = compute_pointlio_frame(
            groups,
            frame_id=frame_id,
            expected_group_count=_integer(frame, "expected_group_count"),
            processed_group_count=_integer(frame, "processed_group_count"),
            source_stage="MEASUREMENT",
            unavailable_reason=frame["unavailable_reason"],
        )
        count_mismatch = (
            result.get("accepted_count") is not None
            and int(result["accepted_count"]) != _integer(frame, "accepted_count")
        )
        empty_mismatch = (
            result.get("empty_group_count") is not None
            and int(result["empty_group_count"]) != _integer(frame, "empty_group_count")
        )
        if count_mismatch or empty_mismatch:
            output_rows.append(_contract_failure_frame(
                frame, "SIDECAR_ACCEPTED_COUNT_MISMATCH",
                int(result["accepted_count"]), result.get("empty_group_count"),
            ))
            continue
        if state == "UNAVAILABLE":
            if result["run_state"] != "COMPLETE":
                output_rows.append(_contract_failure_frame(
                    frame, str(result["unavailable_reason"]),
                    result.get("accepted_count"),
                    result.get("empty_group_count"),
                ))
                continue
            if result["valid"] or result["unavailable_reason"] != frame["unavailable_reason"]:
                output_rows.append(_contract_failure_frame(
                    frame, "FRAME_UNAVAILABLE_REASON_MISMATCH",
                    result.get("accepted_count"),
                    result.get("empty_group_count"),
                ))
                continue
        output_rows.append(_populate_scores(frame, result))

    segmented_pose_rows = None
    pose_fields = None
    if (pose_path is None) != (reset_events_path is None):
        raise ValueError("pose input and reset event paths must be supplied together")
    if pose_path is not None:
        poses = _read_csv(pose_path, {"timestamp_ns", "source_frame_id", "valid", "event"})
        reset_events = _read_csv(reset_events_path, {
            "affected_frame_id", "old_segment_id", "new_segment_id",
        })
        joined = join_emitted_pose_segments(poses, output_rows, reset_events)
        with pose_path.open(newline="", encoding="utf-8") as stream:
            pose_fields = list(csv.DictReader(stream).fieldnames or ())
        if "segment_id" not in pose_fields:
            pose_fields.append("segment_id")
        segmented_pose_rows = joined

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if segmented_pose_rows is not None:
        target = segmented_poses_path or output_path.with_name("poses_segmented.csv")
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=pose_fields, extrasaction="ignore")
            writer.writeheader()
            for row in segmented_pose_rows:
                writer.writerow({key: (str(value).lower() if isinstance(value, bool) else value)
                                 for key, value in row.items()})
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for row in output_rows:
            normalized = {field: row.get(field, "") for field in OUTPUT_FIELDS}
            if isinstance(normalized["valid"], bool):
                normalized["valid"] = str(normalized["valid"]).lower()
            writer.writerow(normalized)
    return output_rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frame-ledger", type=Path, required=True)
    parser.add_argument("--group-ledger", type=Path, required=True)
    parser.add_argument("--jacobian-rows", type=Path, required=True)
    parser.add_argument("--expected-header-stamps", type=Path,
                        help="CSV exported from the input bag; must contain header_stamp_ns")
    parser.add_argument("--poses", type=Path,
                        help="Point-LIO pose CSV with source_frame_id from the optional logger flag")
    parser.add_argument("--reset-events", type=Path,
                        help="Native frame reset_events.csv")
    parser.add_argument("--segmented-poses", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    expected = None
    if args.expected_header_stamps is not None:
        expected_rows = _read_csv(args.expected_header_stamps, {"header_stamp_ns"})
        expected = [_integer(row, "header_stamp_ns") for row in expected_rows]
    rows = export_sidecar(
        args.frame_ledger, args.group_ledger, args.jacobian_rows, args.output,
        expected_header_stamps_ns=expected,
        pose_path=args.poses,
        reset_events_path=args.reset_events,
        segmented_poses_path=args.segmented_poses,
    )
    failures = sum(row["run_state"] == "RUN_INCOMPLETE" for row in rows)
    invalid = sum(not row["valid"] for row in rows)
    print(f"frames={len(rows)} incomplete={failures} unavailable={invalid}")
    return 2 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
