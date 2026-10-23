"""Point-LIO frame-pooled measurement-geometry indicators.

This implements the accepted D050 adaptation, not Point-LIO's posterior
covariance and not the complete DCReg optimizer. It consumes already accepted
native Point-LIO Jacobian rows and never selects correspondences or reads
trajectory/reference data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np

from dcreg_schur import compute_dcreg


MINIMUM_ACCEPTED_ROWS = 6
POINTLIO_LEVER_SCALES_M = (1.0, 3.0, 5.0)
GEOMETRY_NORMALIZATION = 0.001
ROTATION_ORTHOGONALITY_TOL = 1e-8
PSD_RELATIVE_TOL = 1e-10


@dataclass(frozen=True)
class PointLioGroupRows:
    """Rows from one native point-time group and its pre-update rotation.

    ``jacobian_body`` has Point-LIO's first-six-column order:
    world translation followed by right/body-tangent rotation. Empty groups
    use a shape ``(0, 6)`` matrix but still count as processed groups.
    """

    group_index: int
    jacobian_body: np.ndarray
    rotation_world_body_preupdate: np.ndarray


def is_valid_rotation(rotation: np.ndarray) -> bool:
    if rotation.shape != (3, 3) or not np.isfinite(rotation).all():
        return False
    identity = np.eye(3, dtype=np.float64)
    return (np.allclose(rotation.T @ rotation, identity,
                        rtol=0.0, atol=ROTATION_ORTHOGONALITY_TOL)
            and np.linalg.det(rotation) > 0.0
            and abs(float(np.linalg.det(rotation)) - 1.0)
            <= ROTATION_ORTHOGONALITY_TOL)


def transport_group_rows_to_world(
    jacobian_body: np.ndarray,
    rotation_world_body_preupdate: np.ndarray,
) -> np.ndarray:
    """Express one group's rotational columns in the common world tangent.

    The rotation must be the exact state snapshot used by the same
    ``h_model_output`` callback, before the EKF ``boxplus`` update.
    """
    rows = np.asarray(jacobian_body, dtype=np.float64)
    rotation = np.asarray(rotation_world_body_preupdate, dtype=np.float64)
    if rows.ndim != 2 or rows.shape[1] != 6:
        raise ValueError("Point-LIO Jacobian rows must have shape N x 6")
    if not is_valid_rotation(rotation):
        raise ValueError("pre-update rotation must be a finite proper 3 x 3 rotation")
    if not np.isfinite(rows).all():
        raise ValueError("Point-LIO Jacobian rows contain non-finite values")
    common = rows.copy()
    common[:, 3:6] = rows[:, 3:6] @ rotation.T
    return common


def _unavailable(
    *, frame_id: int | None, source_stage: str, reason: str,
    expected: int, processed: int, empty: int | None = 0,
    accepted: int | None = 0,
    run_state: str = "COMPLETE",
) -> dict[str, object]:
    return {
        "frame_id": frame_id,
        "source_stage": source_stage,
        "run_state": run_state,
        "valid": False,
        "unavailable_reason": reason,
        "expected_group_count": expected,
        "processed_group_count": processed,
        "empty_group_count": empty,
        "accepted_count": accepted,
    }


def _observed_group_counts(
    groups: Sequence[PointLioGroupRows],
) -> tuple[int | None, int | None]:
    """Count native rows independently of whether numeric transport succeeds."""
    accepted = 0
    empty = 0
    known = True
    for group in groups:
        try:
            rows = np.asarray(group.jacobian_body)
        except (TypeError, ValueError):
            known = False
            continue
        if rows.ndim != 2 or rows.shape[1] != 6:
            known = False
            continue
        accepted += len(rows)
        empty += int(len(rows) == 0)
    return (accepted, empty) if known else (None, None)


def _recorded_bool(value: object) -> bool:
    """Interpret booleans read from CSV without treating 'false' as true."""
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"false", "0", "no", ""}:
            return False
        if lowered in {"true", "1", "yes"}:
            return True
    return bool(value)


def compute_pointlio_frame(
    groups: Sequence[PointLioGroupRows],
    *,
    frame_id: int | None,
    expected_group_count: int,
    processed_group_count: int,
    source_stage: str = "MEASUREMENT",
    unavailable_reason: str = "",
) -> dict[str, object]:
    """Pool a complete frame and compute the fixed-scale score and DCReg.

    Startup, map-initialization and empty-input records pass their frozen
    unavailable reason with zero expected/processed measurement updates.
    Missing scheduled groups are a run failure, never a partial health score.
    """
    try:
        expected = int(expected_group_count)
        processed = int(processed_group_count)
    except (TypeError, ValueError, OverflowError):
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="INDICATOR_INPUT_INVALID", expected=-1, processed=-1,
        )
    if expected != expected_group_count or processed != processed_group_count:
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="INDICATOR_INPUT_INVALID", expected=expected,
            processed=processed,
        )
    if expected < 0 or processed < 0:
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="INDICATOR_INPUT_INVALID", expected=expected,
            processed=processed,
        )

    if source_stage != "MEASUREMENT":
        if expected != 0 or processed != 0 or groups:
            observed_accepted, observed_empty = _observed_group_counts(groups)
            return _unavailable(
                frame_id=frame_id, source_stage=source_stage,
                reason="RUN_INCOMPLETE", expected=expected,
                processed=processed, empty=observed_empty,
                accepted=observed_accepted, run_state="RUN_INCOMPLETE",
            )
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason=unavailable_reason or "FRAME_UNAVAILABLE",
            expected=0, processed=0, empty=0, accepted=0,
        )

    observed_accepted, observed_empty = _observed_group_counts(groups)
    if expected != processed or len(groups) != expected:
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="INCOMPLETE_GROUP_PROCESSING", expected=expected,
            processed=processed, empty=observed_empty,
            accepted=observed_accepted, run_state="RUN_INCOMPLETE",
        )

    if unavailable_reason == "RESET_IN_FRAME":
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="RESET_IN_FRAME", expected=expected,
            processed=processed,
        )

    group_indices = [group.group_index for group in groups]
    if group_indices != list(range(expected)):
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="GROUP_IDENTITY_MISMATCH", expected=expected,
            processed=processed, empty=observed_empty,
            accepted=observed_accepted, run_state="RUN_INCOMPLETE",
        )

    common_rows: list[np.ndarray] = []
    empty_groups = observed_empty
    for group in groups:
        try:
            common = transport_group_rows_to_world(
                group.jacobian_body,
                group.rotation_world_body_preupdate,
            )
        except ValueError:
            return _unavailable(
                frame_id=frame_id, source_stage=source_stage,
                reason="INDICATOR_NUMERIC_FAILURE", expected=expected,
                processed=processed, empty=empty_groups,
                accepted=observed_accepted,
                run_state="COMPLETE",
            )
        if len(common) > 0:
            common_rows.append(common)

    accepted_count = observed_accepted
    if accepted_count is None:
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="INDICATOR_NUMERIC_FAILURE", expected=expected,
            processed=processed, empty=empty_groups,
        )
    if accepted_count < MINIMUM_ACCEPTED_ROWS:
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="INSUFFICIENT_CORRESPONDENCES", expected=expected,
            processed=processed, empty=empty_groups,
            accepted=accepted_count,
        )

    rows = np.concatenate(common_rows, axis=0)
    hessian = rows.T @ rows
    hessian = (hessian + hessian.T) * 0.5
    if not np.isfinite(hessian).all():
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="INDICATOR_NUMERIC_FAILURE", expected=expected,
            processed=processed, empty=empty_groups,
            accepted=accepted_count,
        )

    scale = float(np.max(np.abs(hessian)))
    try:
        h_eigenvalues = np.linalg.eigvalsh(hessian)
    except np.linalg.LinAlgError:
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="INDICATOR_NUMERIC_FAILURE", expected=expected,
            processed=processed, empty=empty_groups,
            accepted=accepted_count,
        )
    if (not np.isfinite(h_eigenvalues).all()
            or np.any(h_eigenvalues < -PSD_RELATIVE_TOL * scale)):
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="INDICATOR_NUMERIC_FAILURE", expected=expected,
            processed=processed, empty=empty_groups,
            accepted=accepted_count,
        )

    dcreg = compute_dcreg(hessian, accepted_count)
    if not dcreg.valid:
        return _unavailable(
            frame_id=frame_id, source_stage=source_stage,
            reason="INDICATOR_NUMERIC_FAILURE", expected=expected,
            processed=processed, empty=empty_groups,
            accepted=accepted_count,
        )

    output: dict[str, object] = {
        "frame_id": frame_id,
        "source_stage": source_stage,
        "run_state": "COMPLETE",
        "valid": True,
        "unavailable_reason": "",
        "expected_group_count": expected,
        "processed_group_count": processed,
        "empty_group_count": empty_groups,
        "accepted_count": accepted_count,
        "hessian_common": hessian,
    }
    for lever_scale in POINTLIO_LEVER_SCALES_M:
        scaling = np.diag([1.0, 1.0, 1.0,
                           1.0 / lever_scale,
                           1.0 / lever_scale,
                           1.0 / lever_scale])
        information = (scaling @ hessian @ scaling) / (
            accepted_count * GEOMETRY_NORMALIZATION
        )
        information = (information + information.T) * 0.5
        try:
            eigenvalues = np.linalg.eigvalsh(information)
        except np.linalg.LinAlgError:
            return _unavailable(
                frame_id=frame_id, source_stage=source_stage,
                reason="INDICATOR_NUMERIC_FAILURE", expected=expected,
                processed=processed, empty=empty_groups,
                accepted=accepted_count,
            )
        information_scale = float(np.max(np.abs(eigenvalues)))
        if (not np.isfinite(eigenvalues).all()
                or np.any(eigenvalues < -PSD_RELATIVE_TOL * information_scale)):
            return _unavailable(
                frame_id=frame_id, source_stage=source_stage,
                reason="INDICATOR_NUMERIC_FAILURE", expected=expected,
                processed=processed, empty=empty_groups,
                accepted=accepted_count,
            )
        output[f"G_{int(lever_scale)}m"] = information
        output[f"eigenvalues_{int(lever_scale)}m"] = eigenvalues
        output[f"lambda_min_{int(lever_scale)}m"] = float(
            max(0.0, float(eigenvalues[0]))
        )

    output["dcreg"] = dcreg
    return output


def join_emitted_pose_segments(
    pose_rows: Iterable[Mapping[str, object]],
    frame_rows: Iterable[Mapping[str, object]],
    reset_events: Iterable[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Attach frame-ledger segments to emitted poses by exact frame identity.

    Unavailable frames need not emit poses. Every emitted pose must match one
    unique frame row and the diagnostic's actual scan-end timestamp.
    """
    frames: dict[int, Mapping[str, object]] = {}
    for frame in frame_rows:
        frame_id = int(frame["frame_id"])
        if frame_id in frames:
            raise ValueError(f"duplicate diagnostic frame_id {frame_id}")
        frames[frame_id] = frame

    resets: dict[int, Mapping[str, object]] = {}
    for event in reset_events:
        frame_id = int(event["affected_frame_id"])
        if frame_id in resets:
            raise ValueError(f"duplicate reset event for frame_id {frame_id}")
        resets[frame_id] = event

    joined: list[dict[str, object]] = []
    seen_pose_ids: set[int] = set()
    for pose in pose_rows:
        # The shared pose logger can emit a synthetic barrier record when its
        # timestamp/frame convention regresses. It is not an estimated pose;
        # the pinned Point-LIO reset_events.csv is the authoritative boundary.
        if str(pose.get("event", "POSE")) == "RESET":
            continue
        frame_id = int(pose["source_frame_id"])
        if frame_id in seen_pose_ids:
            raise ValueError(f"duplicate emitted pose source_frame_id {frame_id}")
        seen_pose_ids.add(frame_id)
        if frame_id not in frames:
            raise ValueError(f"pose frame_id {frame_id} has no diagnostic row")
        frame = frames[frame_id]
        if str(frame.get("timestamp_source", "ACTUAL")) != "ACTUAL":
            raise ValueError(f"pose frame_id {frame_id} lacks an actual scan-end time")
        if int(pose["timestamp_ns"]) != int(frame["timestamp_ns"]):
            raise ValueError(f"pose/frame timestamp mismatch for frame_id {frame_id}")

        result = dict(pose)
        result["segment_id"] = int(frame["segment_id"])
        reset = resets.get(frame_id)
        if reset is not None:
            result["valid"] = False
            result["unavailable_reason"] = "RESET_IN_FRAME"
        joined.append(result)

    # Reconcile reset events against every diagnostic row, even when the
    # affected frame emitted no pose. A reset advances exactly one shared
    # segment; unlogged jumps and reset flags without events are failures.
    expected_segment = 0
    for frame_id in sorted(frames):
        frame = frames[frame_id]
        frame_segment = int(frame["segment_id"])
        event = resets.get(frame_id)
        reason = str(frame.get("unavailable_reason", ""))
        if reason == "RESET_IN_FRAME" and event is None:
            raise ValueError(f"reset frame {frame_id} has no reset event")
        if event is not None:
            old_segment = int(event["old_segment_id"])
            new_segment = int(event["new_segment_id"])
            if old_segment != expected_segment or frame_segment != old_segment:
                raise ValueError(f"reset segment mismatch for frame_id {frame_id}")
            if new_segment != old_segment + 1:
                raise ValueError(f"reset after frame {frame_id} skips a segment")
            frame_valid = frame.get("valid")
            if frame_valid is None:
                frame_valid = str(frame.get("frame_state", "READY")) == "READY"
            if _recorded_bool(frame_valid) or reason != "RESET_IN_FRAME":
                raise ValueError(f"reset frame {frame_id} is not explicitly invalid")
            expected_segment = new_segment
        elif frame_segment != expected_segment:
            raise ValueError(f"unexplained segment change at frame_id {frame_id}")

    for frame_id in resets:
        if frame_id not in frames:
            raise ValueError(f"reset event references missing frame_id {frame_id}")
    return joined
