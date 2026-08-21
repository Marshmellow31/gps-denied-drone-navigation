from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class SensorProfile:
    name: str = "vl53l5cx_conservative"
    zones_x: int = 8
    zones_y: int = 8
    horizontal_fov_deg: float = 45.0
    vertical_fov_deg: float = 45.0
    max_range_m: float = 4.0
    frame_rate_hz: float = 15.0
    range_noise_std_m: float = 0.020
    range_quantization_m: float = 0.005
    dropout_probability: float = 0.08
    outlier_probability: float = 0.01
    pose_xy_std_m: float = 0.015
    pose_random_walk_m_sqrt_s: float = 0.008
    altitude_std_m: float = 0.010
    attitude_std_deg: float = 0.40
    yaw_random_walk_deg_sqrt_s: float = 0.15


@dataclass(frozen=True)
class VehicleProfile:
    footprint_radius_m: float = 0.22
    clearance_margin_m: float = 0.12
    max_slope_deg: float = 8.0
    max_roughness_m: float = 0.035
    max_step_m: float = 0.080


@dataclass(frozen=True)
class DetectorConfig:
    map_resolution_m: float = 0.15
    min_confidence: float = 0.18
    min_region_area_m2: float = 0.01
    max_interpolation_passes: int = 3
    threshold_safety_factor: float = 0.60
    localization_margin_m: float = 0.10


@dataclass
class GridMap:
    height_m: np.ndarray
    resolution_m: float
    origin_xy_m: tuple[float, float]


@dataclass
class Observation:
    height_m: np.ndarray
    confidence: np.ndarray
    sample_count: np.ndarray
    resolution_m: float
    origin_xy_m: tuple[float, float]
    raw_sample_count: int
    frame_count: int


@dataclass
class Candidate:
    row: int
    col: int
    x_m: float
    y_m: float
    area_m2: float
    clearance_m: float
    confidence: float
    score: float


@dataclass
class Detection:
    safe_mask: np.ndarray
    slope_deg: np.ndarray
    roughness_m: np.ndarray
    step_m: np.ndarray
    candidates: list[Candidate]
    selected: Candidate | None


def dataclass_dict(value: Any) -> dict[str, Any]:
    return asdict(value)
