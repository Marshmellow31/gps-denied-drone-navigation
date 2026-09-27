"""DCReg Schur-condition detector on a timestamped FAST-LIO Hessian sidecar.

The mathematical detector follows Hu et al., DCReg v3, Sections 4.2--4.4,
Equations 18--21 (https://arxiv.org/html/2509.06285v3). The input is the raw
6x6 point-to-plane Hessian captured at FAST-LIO's accepted-correspondence
linearization. FAST-LIO's translation-first columns are permuted to DCReg's
rotation-first convention. This is a detector adaptation, not a full DCReg
registration or PCG reproduction.

This module consumes only timestamped Hessian rows and optional T08 health rows;
it has no interface for reference poses, event labels, or trajectory errors.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


CORRESPONDENCE_MINIMUM = 6
PSEUDOINVERSE_RCOND = 1e-12
SCHUR_NEGATIVE_REL_TOL = 1e-10
SINGULAR_EIGENVALUE_REL_TOL = 1e-12
KAPPA_THRESHOLD = 10.0
ROTATION_FIRST_PERMUTATION = np.array([3, 4, 5, 0, 1, 2], dtype=np.intp)

HESSIAN_COLUMNS = tuple(f"h{row}{col}" for row in range(6) for col in range(6))


@dataclass(frozen=True)
class DcregResult:
    accepted_count: int
    valid: bool
    unavailable_reason: str
    detail: str
    state: str
    health_score: float | None
    rotation_eigenvalues: tuple[float, ...] = ()
    translation_eigenvalues: tuple[float, ...] = ()
    rotation_kappas: tuple[float, ...] = ()
    translation_kappas: tuple[float, ...] = ()
    rotation_flags: tuple[bool, ...] = ()
    translation_flags: tuple[bool, ...] = ()


def _unavailable(count: int, reason: str, detail: str) -> DcregResult:
    return DcregResult(
        accepted_count=count,
        valid=False,
        unavailable_reason=reason,
        detail=detail,
        state="UNAVAILABLE",
        health_score=None,
    )


def _psd_eigh(matrix: np.ndarray, label: str):
    """Symmetrize a 3x3 Schur/block matrix and apply the frozen PSD tolerance."""
    symmetric = (matrix + matrix.T) * 0.5
    try:
        eigenvalues, eigenvectors = np.linalg.eigh(symmetric)
    except np.linalg.LinAlgError:
        return None, None, f"EIGENSOLVER_FAILURE_{label}"
    if not np.isfinite(eigenvalues).all() or not np.isfinite(eigenvectors).all():
        return None, None, f"NONFINITE_EIGEN_SOLUTION_{label}"

    scale = float(np.max(np.abs(eigenvalues)))
    tolerance = SCHUR_NEGATIVE_REL_TOL * scale
    if np.any(eigenvalues < -tolerance):
        return None, None, f"MATERIALLY_NEGATIVE_SPECTRUM_{label}"
    eigenvalues = np.where(eigenvalues < 0.0, 0.0, eigenvalues)
    return eigenvalues, eigenvectors, ""


def _psd_pseudoinverse(eigenvalues: np.ndarray, eigenvectors: np.ndarray) -> np.ndarray:
    """Moore-Penrose inverse of a PSD block with the frozen relative cutoff."""
    maximum = float(eigenvalues[-1])
    if maximum <= 0.0:
        return np.zeros((3, 3), dtype=np.float64)
    keep = eigenvalues > PSEUDOINVERSE_RCOND * maximum
    inverse_values = np.zeros(3, dtype=np.float64)
    inverse_values[keep] = 1.0 / eigenvalues[keep]
    return (eigenvectors * inverse_values) @ eigenvectors.T


def _kappas(eigenvalues: np.ndarray) -> tuple[float, float, float]:
    maximum = float(eigenvalues[-1])
    if maximum <= 0.0:
        return (math.inf, math.inf, math.inf)
    return tuple(
        math.inf if value <= SINGULAR_EIGENVALUE_REL_TOL * maximum
        else maximum / float(value)
        for value in eigenvalues
    )


def compute_dcreg(hessian_translation_first: np.ndarray,
                  accepted_count: int) -> DcregResult:
    """Compute DCReg directional Schur ratios from FAST-LIO's raw ``J.T @ J``.

    The accepted-correspondence count and the first-six-column Hessian must
    come from the same scan-to-map linearization. Missing/invalid upstream
    records should be passed through as unavailable by the CSV adapter.
    """
    try:
        count = int(accepted_count)
    except (TypeError, ValueError, OverflowError):
        return _unavailable(-1, "INDICATOR_INPUT_INVALID", "invalid accepted_count")
    if count != accepted_count or count < 0:
        return _unavailable(count, "INDICATOR_INPUT_INVALID", "invalid accepted_count")
    if count < CORRESPONDENCE_MINIMUM:
        return _unavailable(
            count,
            "INSUFFICIENT_CORRESPONDENCES",
            f"accepted_count={count}; minimum={CORRESPONDENCE_MINIMUM}",
        )

    hessian = np.asarray(hessian_translation_first, dtype=np.float64)
    if hessian.shape != (6, 6):
        return _unavailable(count, "INDICATOR_INPUT_INVALID", "Hessian must be 6x6")
    if not np.isfinite(hessian).all():
        return _unavailable(count, "INDICATOR_NUMERIC_FAILURE", "NONFINITE_HESSIAN")

    # DCReg uses [rotation, translation]; FAST-LIO T08 exports [translation, rotation].
    hessian_symmetric = (hessian + hessian.T) * 0.5
    hessian_dcreg = hessian_symmetric[np.ix_(
        ROTATION_FIRST_PERMUTATION, ROTATION_FIRST_PERMUTATION)]
    h_rr = hessian_dcreg[:3, :3]
    h_rt = hessian_dcreg[:3, 3:]
    h_tr = hessian_dcreg[3:, :3]
    h_tt = hessian_dcreg[3:, 3:]

    eig_rr, vec_rr, reason = _psd_eigh(h_rr, "H_RR")
    if reason:
        return _unavailable(count, "INDICATOR_NUMERIC_FAILURE", reason)
    eig_tt, vec_tt, reason = _psd_eigh(h_tt, "H_tt")
    if reason:
        return _unavailable(count, "INDICATOR_NUMERIC_FAILURE", reason)

    schur_rotation = h_rr - h_rt @ _psd_pseudoinverse(eig_tt, vec_tt) @ h_tr
    schur_translation = h_tt - h_tr @ _psd_pseudoinverse(eig_rr, vec_rr) @ h_rt
    rotation_eigenvalues, _, reason = _psd_eigh(schur_rotation, "S_R")
    if reason:
        return _unavailable(count, "INDICATOR_NUMERIC_FAILURE", reason)
    translation_eigenvalues, _, reason = _psd_eigh(schur_translation, "S_t")
    if reason:
        return _unavailable(count, "INDICATOR_NUMERIC_FAILURE", reason)

    rotation_kappas = _kappas(rotation_eigenvalues)
    translation_kappas = _kappas(translation_eigenvalues)
    all_kappas = (*rotation_kappas, *translation_kappas)
    flags = tuple(value > KAPPA_THRESHOLD for value in all_kappas)
    maximum_kappa = max(all_kappas)
    score = 0.0 if math.isinf(maximum_kappa) else 1.0 / maximum_kappa
    state = "DEGENERATE" if any(flags) else "HEALTHY"

    return DcregResult(
        accepted_count=count,
        valid=True,
        unavailable_reason="",
        detail="",
        state=state,
        health_score=float(score),
        rotation_eigenvalues=tuple(float(x) for x in rotation_eigenvalues),
        translation_eigenvalues=tuple(float(x) for x in translation_eigenvalues),
        rotation_kappas=rotation_kappas,
        translation_kappas=translation_kappas,
        rotation_flags=flags[:3],
        translation_flags=flags[3:],
    )


def _result_row(timestamp_ns: int, source_stage: str,
                result: DcregResult) -> dict[str, object]:
    row: dict[str, object] = {
        "timestamp_ns": timestamp_ns,
        "accepted_count": result.accepted_count,
        "valid": "true" if result.valid else "false",
        "unavailable_reason": result.unavailable_reason,
        "detail": result.detail,
        "state": result.state,
        "DCREG_HEALTH_SCORE": "" if result.health_score is None else result.health_score,
        "source_stage": source_stage,
    }
    for prefix, values in (("lambda_R", result.rotation_eigenvalues),
                           ("lambda_t", result.translation_eigenvalues)):
        for index in range(3):
            row[f"{prefix}_{index}"] = values[index] if values else ""
    for prefix, values, flags in (
        ("kappa_R", result.rotation_kappas, result.rotation_flags),
        ("kappa_t", result.translation_kappas, result.translation_flags),
    ):
        for index in range(3):
            value = values[index] if values else math.nan
            unbounded = math.isinf(value)
            row[f"{prefix}_{index}"] = "" if unbounded or not values else value
            row[f"{prefix}_{index}_unbounded"] = "true" if unbounded else "false"
            row[f"{prefix}_{index}_flagged"] = (
                "true" if flags and flags[index] else "false"
            )
    return row


OUTPUT_FIELDS = (
    "timestamp_ns", "accepted_count", "valid", "unavailable_reason", "detail",
    "lambda_R_0", "lambda_R_1", "lambda_R_2",
    "lambda_t_0", "lambda_t_1", "lambda_t_2",
    "kappa_R_0", "kappa_R_0_unbounded", "kappa_R_0_flagged",
    "kappa_R_1", "kappa_R_1_unbounded", "kappa_R_1_flagged",
    "kappa_R_2", "kappa_R_2_unbounded", "kappa_R_2_flagged",
    "kappa_t_0", "kappa_t_0_unbounded", "kappa_t_0_flagged",
    "kappa_t_1", "kappa_t_1_unbounded", "kappa_t_1_flagged",
    "kappa_t_2", "kappa_t_2_unbounded", "kappa_t_2_flagged",
    "DCREG_HEALTH_SCORE", "state", "source_stage",
)


def hessian_column_names() -> tuple[str, ...]:
    return tuple(f"h{row}{col}" for row in range(6) for col in range(6))


def _read_hessian_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        required = {"timestamp_ns", "accepted_count", "valid", "unavailable_reason",
                    "source_stage", *hessian_column_names()}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"Hessian sidecar schema missing columns: {sorted(required-set(reader.fieldnames or []))}")
        return list(reader)


def _read_health_g3(path: Path) -> dict[int, dict[str, str]]:
    by_timestamp: dict[int, dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        required = {"timestamp_ns", "lever_scale_m", "accepted_count", "valid",
                    "unavailable_reason", *(f"eigenvalue_{i}" for i in range(6))}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("T08 health CSV schema is incomplete")
        for row in reader:
            if float(row["lever_scale_m"]) != 3.0:
                continue
            timestamp = int(row["timestamp_ns"])
            if timestamp in by_timestamp:
                raise ValueError(f"duplicate T08 scale-3 row at {timestamp}")
            by_timestamp[timestamp] = row
    return by_timestamp


def verify_g3_parity(hessian_rows: Iterable[dict[str, str]], health_path: Path,
                     *, rtol: float = 1e-8, atol: float = 1e-8) -> dict[str, object]:
    """Check raw sidecar Hessians against T08's scale-3 eigenvalue export."""
    g3_rows = _read_health_g3(health_path)
    row_list = list(hessian_rows)
    h_rows = {int(row["timestamp_ns"]): row for row in row_list}
    if len(h_rows) != len(row_list):
        raise ValueError("duplicate raw-Hessian timestamp")
    if set(h_rows) != set(g3_rows):
        raise ValueError("raw-Hessian/T08 timestamp sets differ")

    maximum_absolute_error = 0.0
    valid_groups = 0
    unavailable_groups = 0
    for timestamp, raw_row in h_rows.items():
        g3_row = g3_rows[timestamp]
        count = int(raw_row["accepted_count"])
        if count != int(g3_row["accepted_count"]):
            raise ValueError(f"accepted correspondence count differs at {timestamp}")
        raw_valid = raw_row["valid"].strip().lower() == "true" and count >= CORRESPONDENCE_MINIMUM
        g3_valid = g3_row["valid"].strip().lower() == "true"
        if raw_valid != g3_valid:
            raise ValueError(f"T08/raw Hessian validity differs at {timestamp}")
        if not raw_valid:
            unavailable_groups += 1
            continue

        hessian = np.array([float(raw_row[name]) for name in hessian_column_names()],
                           dtype=np.float64).reshape(6, 6)
        if not np.isfinite(hessian).all():
            raise ValueError(f"non-finite valid raw Hessian at {timestamp}")
        scale = np.diag([1.0, 1.0, 1.0, 1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0])
        information = scale @ ((hessian + hessian.T) * 0.5) @ scale
        information /= count * 0.001
        expected = np.maximum(0.0, np.linalg.eigvalsh(information))
        observed = np.array([float(g3_row[f"eigenvalue_{i}"]) for i in range(6)])
        if not np.allclose(expected, observed, rtol=rtol, atol=atol):
            difference = float(np.max(np.abs(expected - observed)))
            raise ValueError(f"T08 scale-3 eigenvalue parity failed at {timestamp}: {difference}")
        maximum_absolute_error = max(
            maximum_absolute_error, float(np.max(np.abs(expected - observed)))
        )
        valid_groups += 1
    return {
        "timestamps": len(h_rows),
        "valid_groups": valid_groups,
        "unavailable_groups": unavailable_groups,
        "max_abs_eigenvalue_error": maximum_absolute_error,
        "rtol": rtol,
        "atol": atol,
    }


def process_hessian_csv(input_path: Path, output_path: Path,
                        health_path: Path | None = None) -> dict[str, object]:
    """Compute one DCREG row per accepted-correspondence timestamp."""
    rows = _read_hessian_rows(input_path)
    if health_path is not None:
        parity = verify_g3_parity(rows, health_path)
    else:
        parity = None

    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        valid_count = 0
        unavailable_count = 0
        for row in rows:
            timestamp = int(row["timestamp_ns"])
            count = int(row["accepted_count"])
            source_stage = row.get("source_stage", "")
            upstream_valid = row["valid"].strip().lower() == "true"
            if not upstream_valid:
                result = _unavailable(
                    count,
                    row.get("unavailable_reason", "") or "INDICATOR_INPUT_INVALID",
                    "upstream Hessian sidecar marked invalid",
                )
            else:
                hessian = np.array(
                    [float(row[name]) for name in hessian_column_names()],
                    dtype=np.float64,
                ).reshape(6, 6)
                result = compute_dcreg(hessian, count)
            valid_count += int(result.valid)
            unavailable_count += int(not result.valid)
            writer.writerow(_result_row(timestamp, source_stage, result))

    return {
        "rows": len(rows),
        "valid": valid_count,
        "unavailable": unavailable_count,
        "g3_parity": parity,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hessian-csv", required=True, type=Path)
    parser.add_argument("--output-csv", required=True, type=Path)
    parser.add_argument("--health-csv", type=Path,
                        help="optional T08 health.csv for exact scale-3 parity audit")
    args = parser.parse_args()
    summary = process_hessian_csv(args.hessian_csv, args.output_csv, args.health_csv)
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
