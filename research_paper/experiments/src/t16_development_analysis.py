"""Apply the R2-frozen recovery analysis to T14 development outputs only.

This module never generates bags and explicitly rejects non-development seeds.
It reuses trajectory_eval's audited SE(3) and reference-association routines.
"""

from __future__ import annotations

import argparse
import bisect
import csv
import hashlib
import json
import math
import platform
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

import trajectory_eval as trajectory


ROOT = Path(__file__).resolve().parents[3]
EPOCH_NS = 1_000_000_000_000
TICK_NS = 100_000_000
MAX_SCORE_AGE_NS = 200_000_000
BOUNDARY_TOLERANCE_NS = 50_000_000
PROFILE_ID = "T14_FORMAL_X_MINUS_6_V1"
SEEDS = tuple(range(14, 46))
SCENES = ("CORRIDOR", "CONTROL")
PRIMARY_LIMITS = (0.20, math.radians(5.0))
SENSITIVITY_LIMITS = {
    "half": (0.10, math.radians(2.5)),
    "double": (0.40, math.radians(10.0)),
}
HEALTHY_EVENT_LIMIT = 0.10


class AnalysisContractError(ValueError):
    """The frozen development inputs do not meet their declared contract."""


@dataclass(frozen=True)
class MotionWindow:
    nominal_start_s: int
    start_ns: int | None
    end_ns: int | None
    translation_error_m: float | None
    rotation_error_rad: float | None
    valid: bool
    reason: str

    def passes(self, limits: tuple[float, float]) -> bool:
        return (self.valid and self.translation_error_m is not None
                and self.rotation_error_rad is not None
                and self.translation_error_m <= limits[0]
                and self.rotation_error_rad <= limits[1])


@dataclass(frozen=True)
class RecoveryLabel:
    status: str
    truth_eligible: bool
    reason: str
    exit_time_s: float
    deadline_s: float
    onset_s: float | None
    confirmation_s: float | None
    relapse_s: float | None
    recovery_end_s: float
    triple_window_starts_s: tuple[int, ...]
    planned_windows: int


@dataclass(frozen=True)
class DiagnosticRecord:
    timestamp_ns: int
    valid: bool
    score: float | None
    fixed_healthy: bool | None
    segment_id: int
    reason: str


@dataclass(frozen=True)
class DecisionTick:
    tick_index: int
    timestamp_ns: int
    available: bool
    score: float | None
    fixed_healthy: bool | None
    source_timestamp_ns: int | None
    segment_id: int | None
    reason: str


@dataclass
class DevelopmentRun:
    run_id: str
    seed: int
    scene: str
    control: bool
    exit_time_s: float
    corridor_length_m: float
    run_dir: Path
    run_manifest: dict[str, Any]
    input_manifest: dict[str, Any]
    poses: list[trajectory.Pose]
    reference: trajectory.ReferenceIndex
    body_transform: np.ndarray
    windows: list[MotionWindow]
    label: RecoveryLabel | None
    diagnostics: dict[str, list[DiagnosticRecord]]
    decisions: dict[str, list[DecisionTick]]
    evaluation_rows: list[dict[str, str]]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def associate_nearest_valid_pose(
    poses: list[trajectory.Pose], nominal_ns: int,
    tolerance_ns: int = BOUNDARY_TOLERANCE_NS,
) -> trajectory.Pose | None:
    """Nearest valid pose; exact ties go to the earlier timestamp."""
    candidates = [pose for pose in poses if pose.valid and pose.event == "POSE"]
    if not candidates:
        return None
    pose = min(candidates, key=lambda value: (abs(value.t_ns - nominal_ns), value.t_ns))
    return pose if abs(pose.t_ns - nominal_ns) <= tolerance_ns else None


def window_at_integer_start(
    poses: list[trajectory.Pose], reference: trajectory.ReferenceIndex,
    body_transform: np.ndarray, start_s: int,
) -> MotionWindow:
    nominal0 = EPOCH_NS + start_s * 1_000_000_000
    nominal1 = nominal0 + 1_000_000_000
    pose0 = associate_nearest_valid_pose(poses, nominal0)
    pose1 = associate_nearest_valid_pose(poses, nominal1)
    if pose0 is None or pose1 is None:
        return MotionWindow(start_s, pose0.t_ns if pose0 else None,
                            pose1.t_ns if pose1 else None, None, None, False,
                            "ESTIMATE_BOUNDARY_UNAVAILABLE")
    duration = (pose1.t_ns - pose0.t_ns) / 1e9
    if pose1.t_ns <= pose0.t_ns:
        reason = "BOUNDARIES_NOT_INCREASING"
    elif pose0.segment != pose1.segment:
        reason = "WINDOW_CROSSES_RESET"
    elif not 0.9 <= duration <= 1.1:
        reason = "WINDOW_DURATION_OUT_OF_RANGE"
    else:
        errors, error_reason = trajectory.local_error(pose0, pose1, reference, body_transform)
        if error_reason or errors is None:
            reason = error_reason or "LOCAL_ERROR_UNAVAILABLE"
        else:
            return MotionWindow(start_s, pose0.t_ns, pose1.t_ns,
                               errors[0], errors[1], True, "")
    return MotionWindow(start_s, pose0.t_ns, pose1.t_ns, None, None, False, reason)


def build_primary_windows(
    poses: list[trajectory.Pose], reference: trajectory.ReferenceIndex,
    body_transform: np.ndarray, exit_time_s: float,
) -> tuple[list[MotionWindow], bool, str]:
    """Build non-overlapping integer-second T11 windows around one exit."""
    deadline_s = exit_time_s + 20.0
    first_s = math.ceil(exit_time_s)
    last_endpoint_s = math.floor(deadline_s)
    if first_s >= last_endpoint_s:
        return [], False, "NO_PLANNED_POST_EXIT_WINDOWS"

    # If the first nearest estimator pose is still at/before the scene exit,
    # skip that boundary and begin at the next integer; never shift the grid.
    while first_s < last_endpoint_s:
        pose = associate_nearest_valid_pose(poses, EPOCH_NS + first_s * 1_000_000_000)
        if pose is None or (pose.t_ns - EPOCH_NS) / 1e9 > exit_time_s:
            break
        first_s += 1
    if first_s >= last_endpoint_s:
        return [], False, "NO_POST_EXIT_ASSOCIATED_BOUNDARY"

    required_boundaries = range(first_s, last_endpoint_s + 1)
    reference_reasons = []
    for second in required_boundaries:
        _, reason = reference.associate(EPOCH_NS + second * 1_000_000_000)
        if reason:
            reference_reasons.append(f"{second}:{reason}")
    truth_ok = not reference_reasons
    truth_reason = "" if truth_ok else "REFERENCE_COVERAGE:" + ";".join(reference_reasons)

    rows: list[MotionWindow] = []
    deadline_ns = EPOCH_NS + round(deadline_s * 1e9)
    for start_s in range(first_s, last_endpoint_s):
        row = window_at_integer_start(poses, reference, body_transform, start_s)
        if row.valid and row.start_ns is not None and row.end_ns is not None:
            if (row.start_ns - EPOCH_NS) / 1e9 <= exit_time_s:
                row = MotionWindow(start_s, row.start_ns, row.end_ns, None, None,
                                   False, "WINDOW_START_NOT_AFTER_EXIT")
            elif row.end_ns > deadline_ns:
                row = MotionWindow(start_s, row.start_ns, row.end_ns, None, None,
                                   False, "WINDOW_END_AFTER_DEADLINE")
        rows.append(row)
    return rows, truth_ok, truth_reason


def find_recovery(
    windows: list[MotionWindow], exit_time_s: float,
    limits: tuple[float, float] = PRIMARY_LIMITS,
    truth_eligible: bool = True, truth_reason: str = "",
) -> RecoveryLabel:
    deadline = exit_time_s + 20.0
    if not truth_eligible:
        return RecoveryLabel("TRUTH_LABEL_UNAVAILABLE", False, truth_reason,
                             exit_time_s, deadline, None, None, None, deadline, (), len(windows))
    first_triple: tuple[int, int, int] | None = None
    for index in range(max(0, len(windows) - 2)):
        triple = windows[index:index + 3]
        if (len(triple) == 3
                and triple[1].nominal_start_s == triple[0].nominal_start_s + 1
                and triple[2].nominal_start_s == triple[1].nominal_start_s + 1
                and all(row.passes(limits) for row in triple)
                and triple[-1].end_ns is not None
                and (triple[-1].end_ns - EPOCH_NS) / 1e9 <= deadline):
            first_triple = (index, index + 1, index + 2)
            break
    if first_triple is None:
        return RecoveryLabel("NO_RECOVERY_WITHIN_HORIZON", True, "", exit_time_s,
                             deadline, None, None, None, deadline, (), len(windows))
    onset_window = windows[first_triple[0]]
    confirmation_window = windows[first_triple[-1]]
    assert onset_window.start_ns is not None and confirmation_window.end_ns is not None
    onset = (onset_window.start_ns - EPOCH_NS) / 1e9
    confirmation = (confirmation_window.end_ns - EPOCH_NS) / 1e9
    relapse = None
    later = windows[first_triple[-1] + 1:]
    for row in later:
        if row.start_ns is None:
            continue
        start_s = (row.start_ns - EPOCH_NS) / 1e9
        if start_s >= deadline:
            break
        if not row.valid or not row.passes(limits):
            relapse = start_s
            break
    end = min(relapse if relapse is not None else deadline, deadline)
    return RecoveryLabel("RECOVERED", True, "", exit_time_s, deadline, onset,
                         confirmation, relapse, end,
                         tuple(windows[index].nominal_start_s for index in first_triple),
                         len(windows))


def _segment_at(poses: list[trajectory.Pose], timestamps: list[int], time_ns: int) -> int:
    index = bisect.bisect_right(timestamps, time_ns) - 1
    if index < 0:
        return 0
    return poses[index].segment


def _read_diagnostics(run_dir: Path, poses: list[trajectory.Pose]) -> dict[str, list[DiagnosticRecord]]:
    stream = run_dir / "stream"
    pose_times = [pose.t_ns for pose in poses]
    health_rows = _read_csv(stream / "health.csv")
    health_rows = [row for row in health_rows if math.isclose(float(row["lever_scale_m"]), 3.0)]
    if len(health_rows) != 600:
        raise AnalysisContractError(f"{run_dir.name}: expected 600 G3 rows, found {len(health_rows)}")
    health: list[DiagnosticRecord] = []
    for row in health_rows:
        valid = row["valid"].lower() == "true"
        raw = row["eigenvalue_0"]
        score = float(raw) if valid and raw else None
        if score is not None and not math.isfinite(score):
            valid, score = False, None
        if valid and score is None:
            raise AnalysisContractError(f"{run_dir.name}: valid G3 row has no finite minimum eigenvalue")
        timestamp = int(row["timestamp_ns"])
        health.append(DiagnosticRecord(timestamp, valid, score, None,
                                       _segment_at(poses, pose_times, timestamp),
                                       row["unavailable_reason"]))

    dcreg_rows = _read_csv(stream / "dcreg.csv")
    if len(dcreg_rows) != 600:
        raise AnalysisContractError(f"{run_dir.name}: expected 600 DCReg rows, found {len(dcreg_rows)}")
    dcreg: list[DiagnosticRecord] = []
    for row in dcreg_rows:
        valid = row["valid"].lower() == "true" and row["state"] != "UNAVAILABLE"
        raw = row["DCREG_HEALTH_SCORE"]
        score = float(raw) if valid and raw else None
        if score is not None and not math.isfinite(score):
            valid, score = False, None
        fixed_healthy = row["state"] == "HEALTHY" if valid else None
        if valid and (score is None or fixed_healthy is None):
            raise AnalysisContractError(f"{run_dir.name}: valid DCReg row has invalid state/score")
        timestamp = int(row["timestamp_ns"])
        dcreg.append(DiagnosticRecord(timestamp, valid, score, fixed_healthy,
                                      _segment_at(poses, pose_times, timestamp),
                                      row["unavailable_reason"]))
    for method, records in (("FASTLIO_MIN_EIG_G3", health), ("DCREG_SCHUR_MASK", dcreg)):
        times = [row.timestamp_ns for row in records]
        if any(b <= a for a, b in zip(times, times[1:])):
            raise AnalysisContractError(f"{run_dir.name}: {method} timestamps are not strictly increasing")
    return {"FASTLIO_MIN_EIG_G3": health, "DCREG_SCHUR_MASK": dcreg}


def associate_decision_ticks(
    records: list[DiagnosticRecord], poses: list[trajectory.Pose],
    count: int = 600,
) -> list[DecisionTick]:
    times = [record.timestamp_ns for record in records]
    pose_times = [pose.t_ns for pose in poses]
    decisions = []
    for tick in range(count):
        timestamp = EPOCH_NS + tick * TICK_NS
        index = bisect.bisect_right(times, timestamp) - 1
        if index < 0:
            decisions.append(DecisionTick(tick, timestamp, False, None, None,
                                          None, None, "NO_PRIOR_DIAGNOSTIC"))
            continue
        record = records[index]
        age = timestamp - record.timestamp_ns
        current_segment = _segment_at(poses, pose_times, timestamp)
        if age > MAX_SCORE_AGE_NS:
            reason = "DIAGNOSTIC_STALE"
        elif not record.valid:
            reason = record.reason or "DIAGNOSTIC_INVALID"
        elif record.segment_id != current_segment:
            reason = "DIAGNOSTIC_CROSSES_RESET"
        else:
            decisions.append(DecisionTick(tick, timestamp, True, record.score,
                                          record.fixed_healthy, record.timestamp_ns,
                                          record.segment_id, ""))
            continue
        decisions.append(DecisionTick(tick, timestamp, False, None, None,
                                      record.timestamp_ns, record.segment_id, reason))
    return decisions


def debounce(
    decisions: list[DecisionTick], method: str,
    threshold: float | None = None,
) -> tuple[np.ndarray, np.ndarray, list[dict[str, Any]]]:
    """Causal three-distinct-record state machine; return state/alarms/audit."""
    active = False
    candidates: list[int] = []
    previous_source: int | None = None
    previous_segment: int | None = None
    states = np.zeros(len(decisions), dtype=bool)
    transitions = np.zeros(len(decisions), dtype=bool)
    alarm_rows = []
    for index, decision in enumerate(decisions):
        if method == "FASTLIO_MIN_EIG_G3":
            healthy = (decision.available and threshold is not None
                       and decision.score is not None and decision.score >= threshold)
        else:
            healthy = decision.available and decision.fixed_healthy is True
        if not healthy or decision.source_timestamp_ns is None:
            active, candidates = False, []
            previous_source = previous_segment = None
        else:
            source = decision.source_timestamp_ns
            if (previous_segment is not None
                    and decision.segment_id != previous_segment):
                active = False
                candidates = []
                previous_source = None
            if active:
                previous_source = source
            elif previous_source is not None and source == previous_source:
                candidates = []  # a reused diagnostic is not a new sample
            else:
                candidates.append(source)
                candidates = candidates[-3:]
                if len(candidates) == 3:
                    active = True
                    transitions[index] = True
                    alarm_rows.append({
                        "decision_tick_ns": decision.timestamp_ns,
                        "source_timestamps_ns": list(candidates),
                        "segment_id": decision.segment_id,
                    })
            previous_source = source
            previous_segment = decision.segment_id
        states[index] = active
    return states, transitions, alarm_rows


def _window_record(window: MotionWindow, label: RecoveryLabel) -> dict[str, Any]:
    result = {
        "nominal_start_s": window.nominal_start_s,
        "start_time_s": ((window.start_ns - EPOCH_NS) / 1e9 if window.start_ns is not None else None),
        "end_time_s": ((window.end_ns - EPOCH_NS) / 1e9 if window.end_ns is not None else None),
        "translation_error_m": window.translation_error_m,
        "rotation_error_rad": window.rotation_error_rad,
        "valid": window.valid,
        "unavailable_reason": window.reason,
    }
    for sensitivity_name, limits in {"primary": PRIMARY_LIMITS, **SENSITIVITY_LIMITS}.items():
        result[f"passes_{sensitivity_name}"] = window.passes(limits)
    result["event_recovery_status"] = label.status
    return result


def _load_run(
    run_dir: Path, provenance_root: Path, reference_path: Path,
    reference: trajectory.ReferenceIndex,
) -> DevelopmentRun:
    manifest_path = run_dir / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    run_id = manifest.get("run_id", "")
    match = re.fullmatch(r"T14_DEV(\d{2})_(CORRIDOR|CONTROL)_XM6_P1", run_id)
    if not match:
        raise AnalysisContractError(f"not a T14 primary run: {run_id}")
    seed, scene = int(match.group(1)), match.group(2)
    if seed not in SEEDS or manifest.get("status") != "COMPLETED":
        raise AnalysisContractError(f"{run_id}: incomplete or outside development seeds")
    if manifest.get("seed") != seed or manifest.get("scene") != scene:
        raise AnalysisContractError(f"{run_id}: run ID and manifest disagree")
    if manifest.get("route_profile") != PROFILE_ID or manifest.get("repeat") is not False:
        raise AnalysisContractError(f"{run_id}: wrong route or repeat status")

    # Verify every output represented in T14's per-run manifest before use.
    outputs = manifest.get("outputs", {})
    if not outputs:
        raise AnalysisContractError(f"{run_id}: no output hashes in manifest")
    for relative, expected in outputs.items():
        path = run_dir / relative
        if not path.is_file() or sha256_file(path) != expected:
            raise AnalysisContractError(f"{run_id}: output hash mismatch: {relative}")

    input_id = f"T14_FORMAL_DEV{seed:02d}_{scene}_INPUT_XM6_V1"
    input_dir = provenance_root / "inputs" / input_id
    input_manifest_path = input_dir / "manifest.json"
    metadata_path = input_dir / "reference_metadata.json"
    fingerprint_hashes = manifest.get("fingerprint", {}).get("input_hashes", {})
    for label, path, key in (
        ("input manifest", input_manifest_path, "input_manifest"),
        ("reference metadata", metadata_path, "reference_metadata"),
        ("reference", reference_path, "reference"),
    ):
        if not path.is_file() or sha256_file(path) != fingerprint_hashes.get(key):
            raise AnalysisContractError(f"{run_id}: {label} does not match run fingerprint")
    input_manifest = json.loads(input_manifest_path.read_text(encoding="utf-8"))
    geometry = input_manifest.get("scene_geometry", {})
    if input_manifest.get("role") != "development" or input_manifest.get("seed") != seed:
        raise AnalysisContractError(f"{run_id}: input provenance is not the declared development seed")
    if input_manifest.get("route_profile", {}).get("profile_id") != PROFILE_ID:
        raise AnalysisContractError(f"{run_id}: input uses a different route profile")
    if input_manifest.get("sensors.bag", {}).get("sha256") != fingerprint_hashes.get("sensor_bag"):
        raise AnalysisContractError(f"{run_id}: sensor bag provenance differs from replay fingerprint")
    if input_manifest.get("reference.txt", {}).get("sha256") != fingerprint_hashes.get("reference"):
        raise AnalysisContractError(f"{run_id}: reference provenance differs from replay fingerprint")
    control = scene == "CONTROL"
    if bool(input_manifest.get("control")) != control:
        raise AnalysisContractError(f"{run_id}: scene/control metadata disagree")
    exit_time_s = float(input_manifest["route_profile"]["exit_time_s"])
    length = float(geometry["corridor_length_m"])

    body_transform = trajectory.load_body_transform(metadata_path, reference_path, True)
    poses = trajectory.load_estimates(run_dir / "stream/poses.csv", "simulation_epoch")
    windows, truth_ok, truth_reason = build_primary_windows(
        poses, reference, body_transform, exit_time_s)
    label = None if control else find_recovery(
        windows, exit_time_s, truth_eligible=truth_ok, truth_reason=truth_reason)
    diagnostics = _read_diagnostics(run_dir, poses)
    decisions = {method: associate_decision_ticks(rows, poses)
                 for method, rows in diagnostics.items()}
    evaluation_rows = _read_csv(run_dir / "stream/evaluation.csv")
    return DevelopmentRun(run_id, seed, scene, control, exit_time_s, length,
                          run_dir, manifest, input_manifest, poses, reference,
                          body_transform, windows, label, diagnostics, decisions,
                          evaluation_rows)


def _tick_bounds(exit_time_s: float, deadline_s: float) -> tuple[int, int]:
    first = math.ceil(exit_time_s * 10.0 - 1e-10)
    stop = math.ceil(deadline_s * 10.0 - 1e-10)
    return first, stop  # stop is exclusive, per frozen tick rule


def _initial_mask(run: DevelopmentRun, count: int = 600) -> np.ndarray:
    assert run.label is not None
    first, stop = _tick_bounds(run.exit_time_s, run.label.deadline_s)
    end_s = run.label.onset_s if run.label.onset_s is not None else run.label.deadline_s
    end = min(stop, math.ceil(end_s * 10.0 - 1e-10))
    result = np.zeros(count, dtype=bool)
    result[first:end] = True
    if not run.label.truth_eligible:
        result[:] = False
    return result


def _recovery_mask(run: DevelopmentRun, count: int = 600) -> np.ndarray:
    assert run.label is not None
    result = np.zeros(count, dtype=bool)
    if not run.label.truth_eligible or run.label.onset_s is None:
        return result
    first = math.ceil(run.label.onset_s * 10.0 - 1e-10)
    stop = math.ceil(run.label.recovery_end_s * 10.0 - 1e-10)
    result[first:stop] = True
    return result


def _post_relapse_mask(run: DevelopmentRun, count: int = 600) -> np.ndarray:
    assert run.label is not None
    result = np.zeros(count, dtype=bool)
    if not run.label.truth_eligible or run.label.relapse_s is None:
        return result
    first = math.ceil(run.label.relapse_s * 10.0 - 1e-10)
    stop = math.ceil(run.label.deadline_s * 10.0 - 1e-10)
    result[first:stop] = True
    return result


def _threshold_arrays(corridors: list[DevelopmentRun], method: str):
    scores = np.full((len(corridors), 600), np.nan, dtype=np.float64)
    available = np.zeros((len(corridors), 600), dtype=bool)
    sources = np.full((len(corridors), 600), -1, dtype=np.int64)
    segments = np.full((len(corridors), 600), -1, dtype=np.int64)
    initial, recovery = [], []
    for event, run in enumerate(corridors):
        for tick, decision in enumerate(run.decisions[method]):
            if decision.available and decision.score is not None:
                scores[event, tick] = decision.score
                available[event, tick] = True
                sources[event, tick] = decision.source_timestamp_ns or -1
                segments[event, tick] = (decision.segment_id
                                         if decision.segment_id is not None else -1)
        initial.append(_initial_mask(run))
        recovery.append(_recovery_mask(run))
    return (scores, available, sources, segments,
            np.asarray(initial, dtype=bool), np.asarray(recovery, dtype=bool))


def select_fastlio_threshold(corridors: list[DevelopmentRun], batch_size: int = 128):
    """Exhaust the frozen unique-score candidates with vectorized debounce."""
    scores, available, sources, segments, initial, recovery = _threshold_arrays(
        corridors, "FASTLIO_MIN_EIG_G3")
    truth_recovered = np.asarray([
        bool(run.label and run.label.truth_eligible and run.label.onset_s is not None)
        for run in corridors
    ], dtype=bool)
    candidates = np.unique(scores[np.isfinite(scores)])
    if len(candidates) == 0:
        return {"status": "NO_FEASIBLE_OPERATING_POINT", "reason": "NO_VALID_G3_SCORES",
                "candidates": [], "threshold": None}, []
    initial_available = (available & initial).any(axis=1)
    false_denominator = int(initial_available.sum())
    recovered_denominator = int(truth_recovered.sum())
    candidate_rows: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None

    all_candidates: list[float | None] = [float(x) for x in candidates]
    all_candidates.append(None)  # explicit final NO_ALARMS candidate
    for start in range(0, len(all_candidates), batch_size):
        batch = all_candidates[start:start + batch_size]
        thresholds = np.asarray([
            np.inf if value is None else value for value in batch
        ], dtype=np.float64)
        batch_size_actual = len(batch)
        counts = np.zeros((batch_size_actual, len(corridors)), dtype=np.int8)
        active = np.zeros((batch_size_actual, len(corridors)), dtype=bool)
        previous_sources = np.full((batch_size_actual, len(corridors)), -1, dtype=np.int64)
        previous_segments = np.full((batch_size_actual, len(corridors)), -1, dtype=np.int64)
        alarm_ticks = np.zeros((batch_size_actual, len(corridors), 600), dtype=bool)
        for tick in range(600):
            raw_healthy = (available[:, tick][None, :]
                           & (scores[:, tick][None, :] >= thresholds[:, None]))
            source = np.broadcast_to(sources[:, tick][None, :],
                                     (batch_size_actual, len(corridors)))
            segment = np.broadcast_to(segments[:, tick][None, :],
                                      (batch_size_actual, len(corridors)))
            unhealthy = ~raw_healthy
            active[unhealthy] = False
            counts[unhealthy] = 0
            previous_sources[unhealthy] = -1
            previous_segments[unhealthy] = -1
            segment_changed = (raw_healthy & (previous_segments >= 0)
                               & (segment != previous_segments))
            active[segment_changed] = False
            counts[segment_changed] = 0
            previous_sources[segment_changed] = -1
            waiting = raw_healthy & ~active
            repeated = waiting & (previous_sources >= 0) & (source == previous_sources)
            counts[repeated] = 0
            previous_sources[repeated] = source[repeated]
            fresh = waiting & ~repeated
            counts[fresh] += 1
            previous_sources[fresh] = source[fresh]
            previous_segments[raw_healthy] = segment[raw_healthy]
            new_alarm = fresh & (counts >= 3)
            active[new_alarm] = True
            alarm_ticks[:, :, tick] = new_alarm

        # Replay each candidate's state timeline from transition timestamps.
        # Three consecutive distinct healthy records confirm; after that the
        # state stays active while healthy, and any invalid/unhealthy tick clears it.
        # A small second pass creates active states from the alarm starts.
        for row_index, value in enumerate(batch):
            candidate = np.inf if value is None else value
            is_healthy = available & (scores >= candidate)
            state = np.zeros((len(corridors), 600), dtype=bool)
            active_event = np.zeros(len(corridors), dtype=bool)
            prior_segment = np.full(len(corridors), -1, dtype=np.int64)
            for tick in range(600):
                healthy_tick = is_healthy[:, tick]
                current_segment = segments[:, tick]
                segment_same = ((prior_segment < 0) | (current_segment == prior_segment))
                active_event &= healthy_tick & segment_same
                active_event |= alarm_ticks[row_index, :, tick]
                state[:, tick] = active_event
                prior_segment = np.where(healthy_tick, current_segment, -1)
            false_events = (state & initial).any(axis=1)
            detections = (alarm_ticks[row_index] & recovery).any(axis=1)
            false_numerator = int(false_events.sum())
            detected_numerator = int((detections & truth_recovered).sum())
            false_rate = (false_numerator / false_denominator
                          if false_denominator else None)
            sensitivity = (detected_numerator / recovered_denominator
                           if recovered_denominator else None)
            label = "NO_ALARMS" if value is None else float(value)
            feasible = false_rate is not None and sensitivity is not None \
                and false_rate <= HEALTHY_EVENT_LIMIT
            row = {"threshold": label, "false_healthy_events": false_numerator,
                   "false_healthy_denominator": false_denominator,
                   "conditional_false_healthy_rate": false_rate,
                   "recovered_events_detected": detected_numerator,
                   "truth_recovered_denominator": recovered_denominator,
                   "recovery_sensitivity": sensitivity,
                   "feasible": feasible}
            candidate_rows.append(row)
            if feasible and sensitivity is not None and sensitivity > 0:
                ordering = (sensitivity, -1.0 if value is None else float(value))
                if best is None or ordering > best["ordering"]:
                    best = {"ordering": ordering, "row": row}
    if false_denominator == 0:
        result = {"status": "NO_FEASIBLE_OPERATING_POINT",
                  "reason": "FALSE_HEALTHY_DENOMINATOR_ZERO", "threshold": None}
    elif recovered_denominator == 0:
        result = {"status": "NO_FEASIBLE_OPERATING_POINT",
                  "reason": "NO_TRUTH_RECOVERED_EVENTS", "threshold": None}
    elif best is None:
        result = {"status": "NO_FEASIBLE_OPERATING_POINT",
                  "reason": "NO_FEASIBLE_THRESHOLD_WITH_NONZERO_SENSITIVITY",
                  "threshold": None}
    else:
        result = {"status": "SELECTED_DEVELOPMENT_THRESHOLD",
                  "reason": "MAXIMUM_SENSITIVITY_WITH_FALSE_HEALTHY_RATE_AT_MOST_10_PERCENT; TIES_USE_HIGHER_THRESHOLD",
                  **best["row"]}
    result["candidate_count_including_no_alarms"] = len(candidate_rows)
    result["unique_finite_g3_scores"] = len(candidates)
    return result, candidate_rows


def _curve(scores: list[float], labels: list[bool], weights: list[float]) -> dict[str, Any]:
    if not scores or not any(labels) or all(labels):
        return {"status": "UNAVAILABLE_ONE_CLASS_OR_NO_TICKS", "roc_auc": None,
                "average_precision": None}
    values = np.asarray(scores, dtype=np.float64)
    truth = np.asarray(labels, dtype=bool)
    weight = np.asarray(weights, dtype=np.float64)
    order = np.argsort(-values, kind="stable")
    values, truth, weight = values[order], truth[order], weight[order]
    positive_total = float(weight[truth].sum())
    negative_total = float(weight[~truth].sum())
    tp = fp = 0.0
    previous_tpr = previous_fpr = 0.0
    auc = average_precision = 0.0
    index = 0
    groups = 0
    while index < len(values):
        stop = index + 1
        while stop < len(values) and values[stop] == values[index]:
            stop += 1
        block_truth, block_weight = truth[index:stop], weight[index:stop]
        tp += float(block_weight[block_truth].sum())
        fp += float(block_weight[~block_truth].sum())
        tpr = tp / positive_total
        fpr = fp / negative_total
        auc += (fpr - previous_fpr) * (tpr + previous_tpr) / 2.0
        precision = tp / (tp + fp) if tp + fp else 0.0
        average_precision += (tpr - previous_tpr) * precision
        previous_tpr, previous_fpr = tpr, fpr
        groups += 1
        index = stop
    return {"status": "AVAILABLE", "roc_auc": auc,
            "average_precision": average_precision,
            "positive_weight": positive_total, "negative_weight": negative_total,
            "tie_groups": groups}


def threshold_free_curves(corridors: list[DevelopmentRun]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for method in ("FASTLIO_MIN_EIG_G3", "DCREG_SCHUR_MASK"):
        scores: list[float] = []
        labels: list[bool] = []
        weights: list[float] = []
        valid_events = 0
        available_count = 0
        planned_count = 0
        for run in corridors:
            assert run.label is not None
            decisions = run.decisions[method]
            first, stop = _tick_bounds(run.exit_time_s, run.label.deadline_s)
            selected = decisions[first:stop]
            planned_count += len(selected)
            valid = [item for item in selected if item.available and item.score is not None]
            available_count += len(valid)
            if not valid:
                continue
            valid_events += 1
            cluster_weight = 1.0 / len(valid)
            for item in valid:
                time_s = item.tick_index / 10.0
                recovered = (run.label.onset_s is not None
                             and time_s >= run.label.onset_s
                             and time_s < run.label.recovery_end_s)
                scores.append(float(item.score))
                labels.append(bool(recovered))
                weights.append(cluster_weight)
        result[method] = {
            **_curve(scores, labels, weights),
            "valid_decision_ticks": available_count,
            "planned_decision_ticks": planned_count,
            "events_with_scores": valid_events,
            "cluster_weighting": "each geometry event has total weight one",
        }
    return result


def wilson_interval(successes: int, trials: int, z: float = 1.96) -> list[float] | None:
    if trials <= 0:
        return None
    proportion = successes / trials
    denominator = 1.0 + z * z / trials
    center = (proportion + z * z / (2.0 * trials)) / denominator
    half = z * math.sqrt(proportion * (1.0 - proportion) / trials
                         + z * z / (4.0 * trials * trials)) / denominator
    return [max(0.0, center - half), min(1.0, center + half)]


def summarize_method(
    runs: list[DevelopmentRun], method: str, threshold: float | None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    corridors = [run for run in runs if run.scene == "CORRIDOR"]
    controls = [run for run in runs if run.scene == "CONTROL"]
    event_rows: list[dict[str, Any]] = []
    counters = {
        "false_healthy_events": 0, "false_healthy_conditional_denominator": 0,
        "truth_eligible_events": 0, "truth_recovered_events": 0,
        "detected_recovery_events": 0, "relapsed_events": 0,
        "post_relapse_false_healthy_events": 0,
        "post_relapse_conditional_denominator": 0,
        "initial_active_ticks": 0, "initial_available_ticks": 0,
        "initial_planned_ticks": 0, "post_relapse_active_ticks": 0,
        "post_relapse_available_ticks": 0, "post_relapse_planned_ticks": 0,
        "available_decision_ticks": 0, "planned_decision_ticks": 0,
    }
    delays: list[float] = []
    sensitivity_denominator = 0

    for run in corridors:
        assert run.label is not None
        states, transitions, alarms = debounce(run.decisions[method], method, threshold)
        label = run.label
        start, stop = _tick_bounds(run.exit_time_s, label.deadline_s)
        planned = np.zeros(600, dtype=bool)
        planned[start:stop] = True
        available = np.asarray([d.available for d in run.decisions[method]], dtype=bool)
        initial = _initial_mask(run)
        post_relapse = _post_relapse_mask(run)
        false_event = bool(np.any(states & initial))
        initial_has_decision = bool(np.any(available & initial))
        if label.truth_eligible:
            counters["truth_eligible_events"] += 1
            counters["false_healthy_events"] += int(false_event)
            counters["false_healthy_conditional_denominator"] += int(initial_has_decision)
            counters["initial_active_ticks"] += int(np.count_nonzero(states & initial))
            counters["initial_available_ticks"] += int(np.count_nonzero(available & initial))
            counters["initial_planned_ticks"] += int(np.count_nonzero(initial))
        recovery_alarm_indices = np.flatnonzero(transitions & _recovery_mask(run))
        if label.truth_eligible and label.onset_s is not None:
            counters["truth_recovered_events"] += 1
            sensitivity_denominator += 1
            if len(recovery_alarm_indices):
                counters["detected_recovery_events"] += 1
                delay = run.decisions[method][int(recovery_alarm_indices[0])].tick_index / 10.0 - label.onset_s
                if delay < -1e-9:
                    raise AnalysisContractError("negative recovery detection delay")
                delays.append(max(0.0, delay))
        if label.truth_eligible and label.relapse_s is not None:
            counters["relapsed_events"] += 1
            any_post_alarm = bool(np.any(states & post_relapse))
            has_post_decision = bool(np.any(available & post_relapse))
            counters["post_relapse_false_healthy_events"] += int(any_post_alarm)
            counters["post_relapse_conditional_denominator"] += int(has_post_decision)
            counters["post_relapse_active_ticks"] += int(np.count_nonzero(states & post_relapse))
            counters["post_relapse_available_ticks"] += int(np.count_nonzero(available & post_relapse))
            counters["post_relapse_planned_ticks"] += int(np.count_nonzero(post_relapse))
        counters["available_decision_ticks"] += int(np.count_nonzero(available & planned))
        counters["planned_decision_ticks"] += int(np.count_nonzero(planned))
        event_rows.append({
            "run_id": run.run_id, "seed": run.seed,
            "truth_status": label.status, "truth_eligible": label.truth_eligible,
            "recovery_onset_s": label.onset_s,
            "recovery_confirmation_s": label.confirmation_s,
            "relapse_s": label.relapse_s,
            "recovery_end_s": label.recovery_end_s,
            "decision_available_ticks_in_primary_horizon": int(np.count_nonzero(available & planned)),
            "planned_decision_ticks_in_primary_horizon": int(np.count_nonzero(planned)),
            "false_healthy_in_initial_unrecovered_interval": false_event,
            "detected_post_onset": bool(len(recovery_alarm_indices)),
            "detection_delay_s": delays[-1] if len(recovery_alarm_indices) else None,
            "confirmed_alarm_count_full_run": len(alarms),
            "confirmed_alarm_timestamps_s": [
                (row["decision_tick_ns"] - EPOCH_NS) / 1e9 for row in alarms
            ],
        })

    def ratio(num: str, den: str) -> float | None:
        denominator = counters[den]
        return counters[num] / denominator if denominator else None

    controls_summary = []
    for run in controls:
        states, _, _ = debounce(run.decisions[method], method, threshold)
        available = np.asarray([d.available for d in run.decisions[method]], dtype=bool)
        raw_healthy = np.asarray([
            (d.available and d.score is not None and threshold is not None
             and d.score >= threshold) if method == "FASTLIO_MIN_EIG_G3"
            else (d.available and d.fixed_healthy is True)
            for d in run.decisions[method]
        ], dtype=bool)
        available_count = int(np.count_nonzero(available))
        controls_summary.append({
            "seed": run.seed, "run_id": run.run_id,
            "available_ticks": available_count,
            "planned_ticks": len(available),
            "available_fraction": float(available_count / len(available)),
            "raw_healthy_fraction_of_available": (
                float(np.count_nonzero(raw_healthy & available) / available_count)
                if available_count else None),
            "debounced_confirmed_healthy_fraction_of_available": (
                float(np.count_nonzero(states & available) / np.count_nonzero(available))
                if available_count else None),
        })
    recovered = counters["truth_recovered_events"]
    eligible = counters["truth_eligible_events"]
    metrics = {
        "method": method,
        "threshold": "NO_ALARMS" if method == "FASTLIO_MIN_EIG_G3" and threshold is None else threshold,
        "truth_label_eligible_corridor_events": eligible,
        "truth_recovered_events": recovered,
        "non_recovery_events": eligible - recovered,
        "truth_recovery_fraction": recovered / eligible if eligible else None,
        "truth_recovery_wilson_95": wilson_interval(recovered, eligible),
        "false_healthy_event_rate_conditional": ratio(
            "false_healthy_events", "false_healthy_conditional_denominator"),
        "false_healthy_event_rate_unconditional": ratio(
            "false_healthy_events", "truth_eligible_events"),
        "false_healthy_events": counters["false_healthy_events"],
        "false_healthy_conditional_denominator": counters["false_healthy_conditional_denominator"],
        "false_healthy_event_wilson_95_conditional": wilson_interval(
            counters["false_healthy_events"], counters["false_healthy_conditional_denominator"]),
        "false_healthy_time_fraction_conditional": ratio(
            "initial_active_ticks", "initial_available_ticks"),
        "false_healthy_time_fraction_unconditional": ratio(
            "initial_active_ticks", "initial_planned_ticks"),
        "recovery_sensitivity": ratio(
            "detected_recovery_events", "truth_recovered_events"),
        "detected_recovery_events": counters["detected_recovery_events"],
        "detection_delay_median_s_detected_only": (
            float(np.median(delays)) if delays else None),
        "relapse_events": counters["relapsed_events"],
        "relapse_fraction_of_truth_recovered": ratio(
            "relapsed_events", "truth_recovered_events"),
        "post_relapse_false_healthy_event_rate_conditional": ratio(
            "post_relapse_false_healthy_events", "post_relapse_conditional_denominator"),
        "post_relapse_false_healthy_event_rate_unconditional": ratio(
            "post_relapse_false_healthy_events", "relapsed_events"),
        "post_relapse_false_healthy_time_fraction_conditional": ratio(
            "post_relapse_active_ticks", "post_relapse_available_ticks"),
        "post_relapse_false_healthy_time_fraction_unconditional": ratio(
            "post_relapse_active_ticks", "post_relapse_planned_ticks"),
        "decision_availability_primary_horizon": ratio(
            "available_decision_ticks", "planned_decision_ticks"),
        "available_decision_ticks": counters["available_decision_ticks"],
        "planned_decision_ticks": counters["planned_decision_ticks"],
        "healthy_scene_controls": controls_summary,
        "interpretation": "development-only; FAST-LIO threshold metrics are evaluated on the data used to select that threshold",
    }
    return metrics, event_rows


def interior_sample_size(runs: list[DevelopmentRun]) -> dict[str, Any]:
    by_seed = {(run.seed, run.scene): run for run in runs}
    differences = []
    details = []
    for seed in SEEDS:
        corridor = by_seed.get((seed, "CORRIDOR"))
        control = by_seed.get((seed, "CONTROL"))
        if corridor is None or control is None:
            raise AnalysisContractError(f"development pair {seed} is incomplete")
        length = corridor.corridor_length_m
        if not math.isclose(length, control.corridor_length_m, abs_tol=1e-12):
            raise AnalysisContractError(f"development pair {seed} uses different geometry")
        begin_s = 3.0 + (6.0 + length / 4.0) / 0.8
        end_s = 3.0 + (6.0 + 3.0 * length / 4.0) / 0.8
        planned_starts = [second for second in range(60)
                          if begin_s <= second < end_s and second + 1 <= 60]
        if len(planned_starts) < 5:
            raise AnalysisContractError(f"seed {seed}: fewer than five frozen interior windows")
        corridor_windows = {second: window_at_integer_start(
            corridor.poses, corridor.reference, corridor.body_transform, second)
            for second in planned_starts}
        control_windows = {second: window_at_integer_start(
            control.poses, control.reference, control.body_transform, second)
            for second in planned_starts}
        missing = [second for second in planned_starts
                   if not corridor_windows[second].valid or not control_windows[second].valid]
        if missing:
            raise AnalysisContractError(
                f"seed {seed}: interior pair coverage failed at seconds {missing}; return to R2")
        corridor_values = [corridor_windows[second].translation_error_m for second in planned_starts]
        control_values = [control_windows[second].translation_error_m for second in planned_starts]
        c_median = float(np.median(corridor_values))
        k_median = float(np.median(control_values))
        difference = c_median - k_median
        differences.append(difference)
        details.append({"seed": seed, "geometry_length_m": length,
                        "interior_time_s": [begin_s, end_s],
                        "planned_window_starts_s": planned_starts,
                        "window_count": len(planned_starts),
                        "corridor_median_translation_error_m": c_median,
                        "control_median_translation_error_m": k_median,
                        "corridor_minus_control_m": difference})
    s_dev = float(np.std(np.asarray(differences, dtype=np.float64), ddof=1))
    n_cont_raw = math.ceil((1.96 * s_dev / 0.10) ** 2)
    n_cont_rounded = int(math.ceil(n_cont_raw / 4.0) * 4)
    n_test = max(48, n_cont_rounded)
    return {
        "pair_count": len(differences), "all_32_pairs_complete": True,
        "standard_deviation_sample_ddof_1_m": s_dev,
        "mean_corridor_minus_control_m": float(np.mean(differences)),
        "median_corridor_minus_control_m": float(np.median(differences)),
        "minimum_corridor_minus_control_m": float(np.min(differences)),
        "maximum_corridor_minus_control_m": float(np.max(differences)),
        "n_cont_ceil_before_rounding": n_cont_raw,
        "n_cont_rounded_multiple_of_four": n_cont_rounded,
        "n_test_geometry_pairs": n_test,
        "within_frozen_48_to_80_budget": n_test <= 80,
        "stop_before_heldout_if_above_80": n_test > 80,
        "paired_seed_differences": details,
    }


def summarize_three_second_sensitivity(runs: list[DevelopmentRun]) -> dict[str, Any]:
    """Descriptive overlapping 3 s rate sensitivity; not a recovery label."""
    by_scene: dict[str, list[dict[str, Any]]] = {"CORRIDOR": [], "CONTROL": []}
    for run in runs:
        deadline_ns = EPOCH_NS + round((run.exit_time_s + 20.0) * 1e9)
        exit_ns = EPOCH_NS + round(run.exit_time_s * 1e9)
        planned = []
        for row in run.evaluation_rows:
            if row.get("window_s") != "3.0":
                continue
            start_ns = int(row["timestamp_ns"])
            end_ns = int(row["window_end_ns"]) if row.get("window_end_ns") else None
            if start_ns < exit_ns:
                continue
            # A missing endpoint is still a planned, unavailable window when
            # its nominal 3 s endpoint fits the frozen horizon.
            if start_ns + 3_000_000_000 > deadline_ns:
                continue
            if end_ns is not None and end_ns > deadline_ns:
                continue
            planned.append(row)
        valid = [row for row in planned
                 if row.get("local_valid", "").lower() == "true"
                 and row.get("window_end_ns")]
        passing = []
        for row in valid:
            translation_rate = float(row["local_translation_error_rate_mps"])
            rotation_rate = float(row["local_rotation_error_rate_radps"])
            passing.append(translation_rate <= 0.20
                           and rotation_rate <= math.radians(5.0))
        by_scene[run.scene].append({
            "run_id": run.run_id, "seed": run.seed,
            "planned_post_exit_3s_windows": len(planned),
            "valid_post_exit_3s_windows": len(valid),
            "unavailable_post_exit_3s_windows": len(planned) - len(valid),
            "unavailable_reasons": {
                reason: sum(row.get("unavailable_reason", "") == reason
                            for row in planned)
                for reason in sorted({row.get("unavailable_reason", "") for row in planned
                                      if row.get("local_valid", "").lower() != "true"})
            },
            "passing_3s_rate_windows": sum(passing),
            "pass_fraction_among_valid": (
                sum(passing) / len(valid) if valid else None),
        })
    result = {}
    for scene, rows in by_scene.items():
        fractions = [row["pass_fraction_among_valid"] for row in rows
                     if row["pass_fraction_among_valid"] is not None]
        result[scene.lower()] = {
            "events": rows,
            "events_with_valid_windows": len(fractions),
            "equal_event_mean_pass_fraction": float(np.mean(fractions)) if fractions else None,
            "valid_window_count_total": sum(row["valid_post_exit_3s_windows"] for row in rows),
            "planned_window_count_total": sum(row["planned_post_exit_3s_windows"] for row in rows),
        }
    result["interpretation"] = (
        "Descriptive 3 s rate sensitivity only; overlapping windows are not independent samples and do not assign recovery labels."
    )
    return result


def _write_csv(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    materialized = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(dict.fromkeys(key for row in materialized for key in row))
    if not fields:
        path.write_text("\n", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in materialized:
            writer.writerow({key: (json.dumps(value, separators=(",", ":"))
                             if isinstance(value, (dict, list, tuple)) else value)
                             for key, value in row.items()})


def analyze(batch_root: Path, provenance_root: Path, audit_path: Path,
            output_dir: Path, repository_root: Path = ROOT) -> dict[str, Any]:
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    if audit.get("heldout_data_opened") is not False:
        raise AnalysisContractError("T14 audit does not certify held-out separation")
    if audit.get("completed_primary_runs") != 64 or audit.get("development_layout_clusters") != 32:
        raise AnalysisContractError("T14 audit does not contain all 32 paired primary events")
    output_dir.mkdir(parents=True, exist_ok=True)
    shared_reference = provenance_root / "shared_reference.txt"
    reference_path = output_dir / "reference.txt"
    if reference_path.exists() or reference_path.is_symlink():
        if not reference_path.is_file() or sha256_file(reference_path) != sha256_file(shared_reference):
            raise AnalysisContractError("existing generated reference alias does not match the T14 shared reference")
    else:
        reference_path.symlink_to(shared_reference.resolve())
    reference = trajectory.load_reference(reference_path)
    runs = []
    run_dirs = sorted(batch_root.glob("T14_DEV*_XM6_P1"))
    if len(run_dirs) != 64:
        raise AnalysisContractError(f"expected 64 completed P1 run folders, found {len(run_dirs)}")
    for run_dir in run_dirs:
        runs.append(_load_run(run_dir, provenance_root, reference_path, reference))
    if len({(run.seed, run.scene) for run in runs}) != 64:
        raise AnalysisContractError("duplicate or missing primary seed/scene pair")
    by_seed = {(run.seed, run.scene): run for run in runs}
    if any((seed, scene) not in by_seed for seed in SEEDS for scene in SCENES):
        raise AnalysisContractError("not all 32 primary corridor/control pairs are present")
    corridors = [by_seed[(seed, "CORRIDOR")] for seed in SEEDS]
    controls = [by_seed[(seed, "CONTROL")] for seed in SEEDS]
    if any(run.label is not None for run in controls):
        raise AnalysisContractError("controls must not receive recovery labels")
    labels = [run.label for run in corridors]
    assert all(label is not None for label in labels)
    if any(not label.truth_eligible for label in labels):
        raise AnalysisContractError("one or more corridor events lack full required reference coverage")

    threshold, threshold_candidates = select_fastlio_threshold(corridors)
    chosen_threshold = (float(threshold["threshold"])
                        if threshold.get("status") == "SELECTED_DEVELOPMENT_THRESHOLD" else None)
    fastlio_summary, fastlio_event_rows = summarize_method(
        runs, "FASTLIO_MIN_EIG_G3", chosen_threshold)
    dcreg_summary, dcreg_event_rows = summarize_method(
        runs, "DCREG_SCHUR_MASK", None)
    sample_size = interior_sample_size(runs)

    truth_counts = {}
    for name, limits in {"primary": PRIMARY_LIMITS, **SENSITIVITY_LIMITS}.items():
        labels_for_limits = [find_recovery(run.windows, run.exit_time_s, limits)
                             for run in corridors]
        recovered = sum(label.onset_s is not None for label in labels_for_limits)
        truth_counts[name] = {
            "recovered": recovered, "non_recovery": len(labels_for_limits) - recovered,
            "eligible": len(labels_for_limits),
            "recovery_fraction": recovered / len(labels_for_limits),
            "recovery_wilson_95": wilson_interval(recovered, len(labels_for_limits)),
        }

    label_rows = []
    for run in corridors:
        assert run.label is not None
        label_rows.append({
            "run_id": run.run_id, "seed": run.seed,
            "exit_time_s": run.label.exit_time_s,
            "deadline_s": run.label.deadline_s,
            "truth_label_status": run.label.status,
            "truth_label_eligible": run.label.truth_eligible,
            "recovery_onset_s": run.label.onset_s,
            "recovery_confirmation_s": run.label.confirmation_s,
            "relapse_s": run.label.relapse_s,
            "recovery_end_s": run.label.recovery_end_s,
            "first_triple_window_starts_s": run.label.triple_window_starts_s,
            "planned_1s_windows": run.label.planned_windows,
            "unavailable_reason": run.label.reason,
        })
    window_rows = []
    for run in corridors:
        assert run.label is not None
        for window in run.windows:
            window_rows.append({"run_id": run.run_id, "seed": run.seed,
                                **_window_record(window, run.label)})

    decision_rows = []
    for run in runs:
        for method, decisions in run.decisions.items():
            for decision in decisions:
                decision_rows.append({
                    "run_id": run.run_id, "seed": run.seed, "scene": run.scene,
                    "method": method,
                    "tick_ns": decision.timestamp_ns,
                    "tick_time_s": decision.tick_index / 10.0,
                    "available": decision.available,
                    "score": decision.score,
                    "fixed_healthy": decision.fixed_healthy,
                    "source_timestamp_ns": decision.source_timestamp_ns,
                    "segment_id": decision.segment_id,
                    "unavailable_reason": decision.reason,
                })

    # The best threshold is chosen on corridor development data only. For the
    # final comparison, the same value is applied once to matched controls.
    # Metric summaries include the selected FAST-LIO threshold and fixed DCReg.
    curves = threshold_free_curves(corridors)
    sample_size_gate = ("READY_FOR_R3_REVIEW" if sample_size["within_frozen_48_to_80_budget"]
                        else "STOP_AND_RETURN_TO_R2_BEFORE_ANY_HELDOUT_ACCESS")

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "t16_truth_labels.csv", label_rows)
    _write_csv(output_dir / "t16_primary_windows.csv", window_rows)
    _write_csv(output_dir / "t16_indicator_ticks.csv", decision_rows)
    _write_csv(output_dir / "t16_threshold_candidates.csv", threshold_candidates)
    _write_csv(output_dir / "t16_fastlio_event_metrics.csv", fastlio_event_rows)
    _write_csv(output_dir / "t16_dcreg_event_metrics.csv", dcreg_event_rows)

    batch_ledger = batch_root / "failure_ledger.csv"
    ledger_counts: dict[str, int] = {}
    if batch_ledger.is_file():
        for row in _read_csv(batch_ledger):
            status = row.get("status", "")
            ledger_counts[status] = ledger_counts.get(status, 0) + 1
    run_provenance = []
    for run in runs:
        input_id = f"T14_FORMAL_DEV{run.seed:02d}_{run.scene}_INPUT_XM6_V1"
        input_dir = provenance_root / "inputs" / input_id
        selected_outputs = {
            name: run.run_manifest["outputs"][f"stream/{name}"]
            for name in ("poses.csv", "health.csv", "dcreg.csv", "evaluation.csv")
        }
        run_provenance.append({
            "run_id": run.run_id,
            "seed": run.seed,
            "scene": run.scene,
            "run_manifest_sha256": sha256_file(run.run_dir / "run_manifest.json"),
            "input_manifest_sha256": sha256_file(input_dir / "manifest.json"),
            "reference_metadata_sha256": sha256_file(input_dir / "reference_metadata.json"),
            "sensor_bag_sha256": run.input_manifest["sensors.bag"]["sha256"],
            "reference_sha256": run.input_manifest["reference.txt"]["sha256"],
            "key_output_sha256": selected_outputs,
        })
    output_hashes = {}
    for path in sorted(output_dir.iterdir()):
        if path.is_file() and path.name not in ("t16_analysis_manifest.json", "reference.txt"):
            output_hashes[path.name] = sha256_file(path)
    result = {
        "schema": "t16-development-analysis-v1",
        "task_id": "T16",
        "status": "DONE" if sample_size["within_frozen_48_to_80_budget"] else "BLOCKED_R2_BUDGET_GATE",
        "role": "development_only",
        "heldout_inputs_opened": False,
        "protocol": {
            "freeze_sha256": sha256_file(repository_root / "research_paper/protocol/FREEZE.md"),
            "metrics_sha256": sha256_file(repository_root / "research_paper/protocol/METRICS.md"),
            "threshold_rule": "R2 frozen unique finite corridor G3 scores plus NO_ALARMS; maximize recovered-event sensitivity subject to conditional false-healthy rate <= 0.10; ties choose higher threshold",
            "recovery_rule": "three consecutive non-overlapping 1 s windows pass 0.20 m and 5 degrees, all endpoints <= exit+20 s",
        },
        "analysis_environment": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "analysis_source_sha256": sha256_file(Path(__file__).resolve()),
            "test_source_sha256": sha256_file(
                repository_root / "research_paper/experiments/tests/test_t16_development_analysis.py"),
            "command": "ROS_ENV/bin/python research_paper/experiments/src/t16_development_analysis.py --output-dir research_paper/experiments/generated/t16_analysis_v1",
        },
        "input_audit": {
            "t14_batch_audit_sha256": sha256_file(audit_path),
            "primary_run_count": len(runs),
            "corridor_event_count": len(corridors),
            "control_event_count": len(controls),
            "run_manifest_output_files_verified": sum(len(run.run_manifest["outputs"]) for run in runs),
            "primary_run_provenance": run_provenance,
            "run_completion_primary": "64/64 completed",
            "t14_formal_slots_including_repeats": audit.get("scheduled_runs"),
            "t14_run_summary_status_counts": audit.get("batch_status_counts"),
            "failure_ledger_attempt_status_counts": ledger_counts,
            "seed14_repeat_reconciliation": audit.get("seed14_smoke_repeat_reconciliation"),
            "seed45_repeat_runs_completed": audit.get("seed45_repeat_runs_completed"),
            "seed45_repeatability_comparison": audit.get("seed45_repeatability_comparison"),
        },
        "truth_labels": {
            "primary_counts": truth_counts["primary"],
            "half_tolerance_counts": truth_counts["half"],
            "double_tolerance_counts": truth_counts["double"],
            "event_rows": label_rows,
            "limitations": "Synthetic analytic truth and a single prescribed trajectory; outcomes are development-only.",
        },
        "fastlio_threshold_selection": threshold,
        "fastlio_threshold_candidates_count": len(threshold_candidates),
        "method_metrics": {
            "FASTLIO_MIN_EIG_G3": fastlio_summary,
            "DCREG_SCHUR_MASK": dcreg_summary,
        },
        "threshold_free_curves": curves,
        "three_second_rate_sensitivity": summarize_three_second_sensitivity(runs),
        "sample_size": sample_size,
        "heldout_gate": sample_size_gate,
        "output_hashes": output_hashes,
        "scientific_conclusion": "development analysis only; no held-out result or publication claim",
    }
    manifest_path = output_dir / "t16_analysis_manifest.json"
    manifest_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch-root", type=Path,
                        default=ROOT / "research_paper/experiments/generated/runs/T14_FORMAL_BATCH")
    parser.add_argument("--provenance-root", type=Path,
                        default=ROOT / "research_paper/experiments/generated/t14_formal_input_provenance_v1")
    parser.add_argument("--audit", type=Path,
                        default=ROOT / "research_paper/evidence/t14_development_batch_manifest.json")
    parser.add_argument("--output-dir", type=Path,
                        default=ROOT / "research_paper/experiments/generated/t16_analysis_v1")
    args = parser.parse_args()
    result = analyze(args.batch_root, args.provenance_root, args.audit, args.output_dir)
    print(json.dumps({"status": result["status"],
                      "primary_events": result["input_audit"]["corridor_event_count"],
                      "truth_labels": result["truth_labels"]["primary_counts"],
                      "fastlio_threshold_selection": result["fastlio_threshold_selection"],
                      "sample_size": {key: value for key, value in result["sample_size"].items()
                                      if key != "paired_seed_differences"},
                      "heldout_gate": result["heldout_gate"]}, indent=2))


if __name__ == "__main__":
    main()
