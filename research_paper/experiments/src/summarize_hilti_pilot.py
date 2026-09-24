"""Descriptive, no-threshold T07 summary under HILTI_PILOT_ANALYSIS.md."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np


ORIGIN_NS = 1649856227623466000
BINS = (("pre_scene", 26.0, 31.6), ("transition", 31.6, 33.6),
        ("matched_post_scene", 35.0, 40.6))


def group_name(timestamp_ns: int) -> str:
    t = (timestamp_ns - ORIGIN_NS) / 1e9
    return next((name for name, start, end in BINS if start <= t < end), "other")


def summarize(rows: list[dict]) -> dict:
    result = {}
    for window_s in (1.0, 3.0):
        selected_window = [row for row in rows if float(row["window_s"]) == window_s]
        result[str(window_s)] = {}
        for group in ("pre_scene", "transition", "matched_post_scene", "other", "all"):
            selected = [row for row in selected_window
                        if group == "all" or group_name(int(row["timestamp_ns"])) == group]
            valid = [row for row in selected if row["local_valid"] == "true"]
            aligned = [row for row in selected if row["alignment_valid"] == "true"]
            def distribution(key: str, items: list[dict]) -> dict | None:
                values = np.asarray([float(row[key]) for row in items], dtype=np.float64)
                if not len(values):
                    return None
                return {"median": float(np.median(values)), "p90": float(np.percentile(values, 90))}
            result[str(window_s)][group] = {
                "planned": len(selected), "local_valid": len(valid),
                "alignment_valid": len(aligned),
                "invalid_reasons": dict(sorted(Counter(row["unavailable_reason"] or "UNSPECIFIED"
                                                       for row in selected if row["local_valid"] != "true").items())),
                "translation_error_m": distribution("local_translation_error_m", valid),
                "rotation_error_rad": distribution("local_rotation_error_rad", valid),
                "translation_error_rate_mps": distribution("local_translation_error_rate_mps", valid),
                "rotation_error_rate_radps": distribution("local_rotation_error_rate_radps", valid),
                "accumulated_translation_error_m": distribution("accumulated_translation_error_m", aligned),
                "accumulated_rotation_error_rad": distribution("accumulated_rotation_error_rad", aligned),
            }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("evaluation", type=Path)
    args = parser.parse_args()
    with args.evaluation.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    print(json.dumps(summarize(rows), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
