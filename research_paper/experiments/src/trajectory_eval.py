"""Offline SE(3) trajectory evaluation under the T05 development contract.

This module has no ROS/backend imports. Reference truth enters only here.
Unknown reference-body conventions produce unavailable results.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import json
import math
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

import numpy as np


NSEC = 1_000_000_000
MAX_BRACKET_NS = 200_000_000
END_TOLERANCE_NS = 50_000_000
COLUMNS = (
    "event_id", "run_id", "timestamp_ns", "window_s", "window_end_ns", "segment_id",
    "reference_valid", "pose_valid", "local_valid", "local_translation_error_m",
    "local_rotation_error_rad", "local_translation_error_rate_mps",
    "local_rotation_error_rate_radps", "alignment_valid",
    "accumulated_translation_error_m", "accumulated_rotation_error_rad",
    "recovery_label", "indicator_method_id", "indicator_output_name",
    "indicator_value", "indicator_decision", "evaluation_valid", "unavailable_reason",
)


def timestamp_ns(decimal_text: str) -> int:
    return int((Decimal(decimal_text) * NSEC).to_integral_value(rounding=ROUND_HALF_EVEN))


def unit_quaternion(q: np.ndarray) -> np.ndarray:
    q = np.asarray(q, dtype=np.float64)
    norm = float(np.linalg.norm(q))
    if not np.isfinite(q).all() or abs(norm - 1.0) > 1e-5:
        raise ValueError("POSE_INVALID: quaternion norm")
    return q / norm


def normalize_interpolated(q: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(q))
    if not np.isfinite(q).all() or norm == 0:
        raise ValueError("POSE_INVALID: interpolated quaternion")
    return q / norm


def quaternion_rotation(q: np.ndarray) -> np.ndarray:
    x, y, z, w = unit_quaternion(q)
    return np.array([
        [1 - 2 * (y*y + z*z), 2 * (x*y - z*w), 2 * (x*z + y*w)],
        [2 * (x*y + z*w), 1 - 2 * (x*x + z*z), 2 * (y*z - x*w)],
        [2 * (x*z - y*w), 2 * (y*z + x*w), 1 - 2 * (x*x + y*y)],
    ], dtype=np.float64)


def slerp(q0: np.ndarray, q1: np.ndarray, fraction: float) -> np.ndarray:
    q0, q1 = unit_quaternion(q0), unit_quaternion(q1)
    dot = float(np.dot(q0, q1))
    if dot < 0:
        q1, dot = -q1, -dot
    dot = min(1.0, max(-1.0, dot))
    if dot > 0.9995:
        return normalize_interpolated((1 - fraction) * q0 + fraction * q1)
    angle = math.acos(dot)
    scale = math.sin(angle)
    return normalize_interpolated((math.sin((1-fraction)*angle)*q0 + math.sin(fraction*angle)*q1) / scale)


def transform(position: np.ndarray, quaternion: np.ndarray) -> np.ndarray:
    matrix = np.eye(4, dtype=np.float64)
    matrix[:3, :3] = quaternion_rotation(quaternion)
    matrix[:3, 3] = np.asarray(position, dtype=np.float64)
    if not np.isfinite(matrix).all():
        raise ValueError("POSE_INVALID: nonfinite transform")
    return matrix


def inverse(matrix: np.ndarray) -> np.ndarray:
    result = np.eye(4, dtype=np.float64)
    result[:3, :3] = matrix[:3, :3].T
    result[:3, 3] = -result[:3, :3] @ matrix[:3, 3]
    return result


def errors(matrix: np.ndarray) -> tuple[float, float]:
    rotation = matrix[:3, :3]
    if np.linalg.det(rotation) <= 0 or not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-6):
        raise ValueError("POSE_INVALID: non-SO3 rotation")
    cosine = min(1.0, max(-1.0, (float(np.trace(rotation)) - 1.0) / 2.0))
    return float(np.linalg.norm(matrix[:3, 3])), math.acos(cosine)


@dataclass(frozen=True)
class Pose:
    t_ns: int
    position: np.ndarray
    quaternion: np.ndarray
    segment: int = 0

    def matrix(self) -> np.ndarray:
        return transform(self.position, self.quaternion)


class ReferenceIndex:
    def __init__(self, source_rows: list[Pose], max_bracket_ns: int = MAX_BRACKET_NS):
        self.max_bracket_ns = max_bracket_ns
        self.source_order_decreases = sum(b.t_ns < a.t_ns for a, b in zip(source_rows, source_rows[1:]))
        # Coverage is inferred solely from reference timestamps. It does not
        # depend on estimator trajectories, diagnostics, or error peaks.
        ordered = sorted(source_rows, key=lambda pose: pose.t_ns)
        self.ambiguous: set[int] = set()
        unique: list[Pose] = []
        for pose in ordered:
            if unique and pose.t_ns == unique[-1].t_ns:
                previous = unique[-1]
                qa, qb = unit_quaternion(previous.quaternion), unit_quaternion(pose.quaternion)
                qdistance = min(np.linalg.norm(qa-qb), np.linalg.norm(qa+qb))
                qangle = 4 * math.asin(min(1.0, float(qdistance)/2))
                if np.linalg.norm(pose.position - previous.position) > 1e-9 or qangle > 1e-9:
                    self.ambiguous.add(pose.t_ns)
                continue
            unique.append(pose)
        segment = 0
        self.gaps: list[tuple[int, int]] = []
        segmented = []
        for index, pose in enumerate(unique):
            if index and pose.t_ns - unique[index-1].t_ns > max_bracket_ns:
                self.gaps.append((unique[index-1].t_ns, pose.t_ns))
                segment += 1
            segmented.append(Pose(pose.t_ns, pose.position, pose.quaternion, segment))
        self.poses = segmented
        self.times = [pose.t_ns for pose in segmented]

    def associate(self, t_ns: int) -> tuple[Pose | None, str | None]:
        if not self.poses or t_ns < self.times[0] or t_ns > self.times[-1]:
            return None, "REFERENCE_UNCOVERED"
        index = bisect.bisect_left(self.times, t_ns)
        if t_ns in self.ambiguous:
            return None, "REFERENCE_AMBIGUOUS"
        if index < len(self.times) and self.times[index] == t_ns:
            return self.poses[index], None
        if index == 0 or index == len(self.times):
            return None, "REFERENCE_UNCOVERED"
        left, right = self.poses[index-1], self.poses[index]
        if left.segment != right.segment or right.t_ns - left.t_ns > self.max_bracket_ns:
            return None, "REFERENCE_GAP"
        fraction = (t_ns - left.t_ns) / (right.t_ns - left.t_ns)
        return Pose(t_ns, left.position + fraction*(right.position-left.position),
                    slerp(left.quaternion, right.quaternion, fraction), left.segment), None


def load_reference(path: Path) -> ReferenceIndex:
    rows = []
    for line_number, line in enumerate(path.read_text().splitlines(), 1):
        fields = line.split()
        if len(fields) != 8:
            raise ValueError(f"reference line {line_number}: expected 8 fields")
        rows.append(Pose(timestamp_ns(fields[0]), np.array([float(value) for value in fields[1:4]]),
                         unit_quaternion(np.array([float(value) for value in fields[4:8]]))))
    return ReferenceIndex(rows)


def load_estimates(path: Path) -> list[Pose]:
    result = []
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["event"] != "POSE" or row["valid"] != "true":
                continue
            result.append(Pose(int(row["timestamp_ns"]),
                               np.array([float(row[key]) for key in ("x_m", "y_m", "z_m")]),
                               unit_quaternion(np.array([float(row[key]) for key in ("qx", "qy", "qz", "qw")])),
                               int(row["segment_id"])))
    if any(right.t_ns <= left.t_ns for left, right in zip(result, result[1:])):
        raise ValueError("POSE_RESET_BOUNDARY: non-increasing pose timestamps")
    return result


def local_error(estimate0: Pose, estimate1: Pose, reference: ReferenceIndex,
                body_transform: np.ndarray | None) -> tuple[tuple[float, float] | None, str | None]:
    if estimate0.segment != estimate1.segment:
        return None, "WINDOW_CROSSES_RESET"
    reference0, reason0 = reference.associate(estimate0.t_ns)
    reference1, reason1 = reference.associate(estimate1.t_ns)
    if reason0 or reason1:
        return None, reason0 or reason1
    if reference0.segment != reference1.segment:
        return None, "REFERENCE_GAP"
    if body_transform is None:
        return None, "REFERENCE_BODY_UNKNOWN"
    delta_ref = inverse(reference0.matrix()) @ reference1.matrix()
    delta_est = inverse(estimate0.matrix() @ body_transform) @ (estimate1.matrix() @ body_transform)
    return errors(inverse(delta_ref) @ delta_est), None


def alignment(estimate_anchor: Pose, reference: ReferenceIndex,
              body_transform: np.ndarray | None) -> tuple[np.ndarray | None, str | None]:
    if body_transform is None:
        return None, "REFERENCE_BODY_UNKNOWN"
    reference_anchor, reason = reference.associate(estimate_anchor.t_ns)
    if reason:
        return None, reason
    return reference_anchor.matrix() @ inverse(estimate_anchor.matrix() @ body_transform), None


def accumulated_error(estimate: Pose, reference: ReferenceIndex, body_transform: np.ndarray | None,
                      fixed_alignment: np.ndarray | None) -> tuple[tuple[float, float] | None, str | None]:
    reference_pose, reason = reference.associate(estimate.t_ns)
    if reason:
        return None, reason
    if body_transform is None:
        return None, "REFERENCE_BODY_UNKNOWN"
    if fixed_alignment is None:
        return None, "ALIGNMENT_UNAVAILABLE"
    return errors(inverse(reference_pose.matrix()) @ fixed_alignment @ estimate.matrix() @ body_transform), None


def evaluate(estimates: list[Pose], reference: ReferenceIndex, body_transform: np.ndarray | None,
             entry_start_ns: int, event_id: str, run_id: str,
             windows_s: tuple[float, ...] = (1.0, 3.0)) -> list[dict]:
    if not estimates:
        return []
    times = [pose.t_ns for pose in estimates]
    target = entry_start_ns - 5*NSEC
    anchor_index = min(range(len(times)), key=lambda index: (abs(times[index] - target), times[index]))
    if abs(times[anchor_index] - target) <= END_TOLERANCE_NS:
        fixed_alignment, alignment_reason = alignment(estimates[anchor_index], reference, body_transform)
    else:
        fixed_alignment, alignment_reason = None, "ALIGNMENT_UNAVAILABLE"
    rows = []
    for index, estimate in enumerate(estimates):
        associated, reference_reason = reference.associate(estimate.t_ns)
        accumulation, accumulation_reason = accumulated_error(estimate, reference, body_transform, fixed_alignment)
        for window_s in windows_s:
            target_end = estimate.t_ns + round(window_s*NSEC)
            candidate = bisect.bisect_left(times, target_end - END_TOLERANCE_NS)
            upper = bisect.bisect_right(times, target_end + END_TOLERANCE_NS)
            matches = [j for j in range(candidate, upper) if abs(times[j]-target_end) <= END_TOLERANCE_NS]
            end_index = min(matches, key=lambda j: (abs(times[j]-target_end), times[j])) if matches else None
            if end_index is None:
                local, local_reason = None, "WINDOW_INCOMPLETE"
            else:
                local, local_reason = local_error(estimate, estimates[end_index], reference, body_transform)
            actual_duration = (times[end_index]-estimate.t_ns)/NSEC if end_index is not None else None
            reason = local_reason or accumulation_reason
            rows.append({
                "event_id": event_id, "run_id": run_id, "timestamp_ns": estimate.t_ns,
                "window_s": window_s, "window_end_ns": times[end_index] if end_index is not None else None,
                "segment_id": estimate.segment,
                "reference_valid": associated is not None, "pose_valid": True, "local_valid": local is not None,
                "local_translation_error_m": local[0] if local else None,
                "local_rotation_error_rad": local[1] if local else None,
                "local_translation_error_rate_mps": local[0]/actual_duration if local else None,
                "local_rotation_error_rate_radps": local[1]/actual_duration if local else None,
                "alignment_valid": accumulation is not None,
                "accumulated_translation_error_m": accumulation[0] if accumulation else None,
                "accumulated_rotation_error_rad": accumulation[1] if accumulation else None,
                "recovery_label": None, "indicator_method_id": None,
                "indicator_output_name": None, "indicator_value": None, "indicator_decision": None,
                "evaluation_valid": local is not None,
                "unavailable_reason": reason,
            })
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if value is None else str(value).lower() if isinstance(value, bool) else value
                             for key, value in row.items()})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--poses", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--body-transform-json", type=Path)
    args = parser.parse_args()
    body_transform = None
    if args.body_transform_json:
        metadata = json.loads(args.body_transform_json.read_text())
        if metadata.get("verified") is not True:
            raise ValueError("body transform must be verified for canonical evaluation")
        body_transform = np.array(metadata["T_est_body_to_ref_body"], dtype=np.float64).reshape(4, 4)
    estimates = load_estimates(args.poses)
    reference = load_reference(args.reference)
    entry_start_ns = timestamp_ns("1693022176.719765425")
    rows = evaluate(estimates, reference, body_transform, entry_start_ns, "UT01_TUNNEL2", args.run_id)
    write_csv(args.output, rows)
    print(json.dumps({"rows": len(rows), "local_valid": sum(row["local_valid"] for row in rows),
                      "reference_gaps": len(reference.gaps), "out_of_order_source_rows": reference.source_order_decreases,
                      "body_transform_verified": body_transform is not None}))


if __name__ == "__main__":
    main()
