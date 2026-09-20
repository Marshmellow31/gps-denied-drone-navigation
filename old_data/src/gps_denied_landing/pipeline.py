from __future__ import annotations

import time
import tracemalloc
from dataclasses import asdict
from typing import Any

import numpy as np

from .evaluation import classification_metrics, target_metrics
from .geometry import compute_safety_layers, detect_landing_zones
from .models import DetectorConfig, SensorProfile, VehicleProfile
from .sensor import simulate_multizone_scan
from .terrain import generate_terrain


def run_simulation(
    scenario: str,
    seed: int,
    sensor: SensorProfile | None = None,
    vehicle: VehicleProfile | None = None,
    detector_config: DetectorConfig | None = None,
) -> dict[str, Any]:
    sensor = sensor or SensorProfile()
    vehicle = vehicle or VehicleProfile()
    detector_config = detector_config or DetectorConfig()
    terrain = generate_terrain(scenario, seed, resolution_m=detector_config.map_resolution_m)

    truth_confidence = np.ones_like(terrain.height_m, dtype=np.float32)
    truth_safe, _, _, _ = compute_safety_layers(
        terrain.height_m,
        truth_confidence,
        terrain.resolution_m,
        vehicle,
        min_confidence=0.0,
    )

    observation = simulate_multizone_scan(
        terrain,
        sensor,
        seed=seed + 10_000,
        interpolation_passes=detector_config.max_interpolation_passes,
    )
    tracemalloc.start()
    start = time.perf_counter()
    detection = detect_landing_zones(observation, vehicle, detector_config)
    runtime_ms = (time.perf_counter() - start) * 1000
    _, peak_memory = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    metrics: dict[str, Any] = classification_metrics(detection.safe_mask, truth_safe)
    metrics.update(target_metrics(detection.selected, truth_safe, terrain.resolution_m))
    metrics.update(
        {
            "runtime_ms": runtime_ms,
            "peak_detector_memory_kib": peak_memory / 1024,
            "coverage": float(np.isfinite(observation.height_m).mean()),
            "direct_measurement_coverage": float((observation.sample_count > 0).mean()),
            "raw_samples": observation.raw_sample_count,
            "frames": observation.frame_count,
            "acquisition_duration_s": observation.frame_count / sensor.frame_rate_hz,
            "candidate_count": len(detection.candidates),
            "truth_safe_cells": int(truth_safe.sum()),
            "predicted_safe_cells": int(detection.safe_mask.sum()),
        }
    )
    return {
        "scenario": scenario,
        "seed": seed,
        "sensor": asdict(sensor),
        "vehicle": asdict(vehicle),
        "detector": asdict(detector_config),
        "metrics": metrics,
        "selected": asdict(detection.selected) if detection.selected else None,
        "arrays": {
            "terrain": terrain.height_m,
            "observation": observation.height_m,
            "confidence": observation.confidence,
            "truth_safe": truth_safe,
            "predicted_safe": detection.safe_mask,
            "slope_deg": detection.slope_deg,
            "roughness_m": detection.roughness_m,
            "step_m": detection.step_m,
        },
    }
