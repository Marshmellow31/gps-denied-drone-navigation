from __future__ import annotations

import math

import numpy as np

from .models import Candidate


def classification_metrics(predicted: np.ndarray, truth: np.ndarray) -> dict[str, float]:
    tp = int(np.count_nonzero(predicted & truth))
    fp = int(np.count_nonzero(predicted & ~truth))
    fn = int(np.count_nonzero(~predicted & truth))
    tn = int(np.count_nonzero(~predicted & ~truth))
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 1.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_positive_cells": tp,
        "false_positive_cells": fp,
        "false_negative_cells": fn,
        "true_negative_cells": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_safe_rate": fp / (tp + fp) if tp + fp else 0.0,
    }


def target_metrics(selected: Candidate | None, truth: np.ndarray, resolution_m: float) -> dict[str, float | bool | None]:
    if selected is None:
        return {"target_produced": False, "target_is_truly_safe": None, "target_error_m": None}
    is_safe = bool(truth[selected.row, selected.col])
    truth_points = np.argwhere(truth)
    if len(truth_points):
        error = float(
            np.sqrt(((truth_points - np.array([selected.row, selected.col])) ** 2).sum(axis=1)).min()
            * resolution_m
        )
    else:
        error = math.inf
    return {"target_produced": True, "target_is_truly_safe": is_safe, "target_error_m": error}

