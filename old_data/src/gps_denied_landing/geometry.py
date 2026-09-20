from __future__ import annotations

import math
import warnings

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

from .models import Candidate, Detection, DetectorConfig, Observation, VehicleProfile


def _window_view(array: np.ndarray, radius: int, fill: float) -> np.ndarray:
    width = radius * 2 + 1
    return sliding_window_view(np.pad(array, radius, constant_values=fill), (width, width))


def _nan_local_mean(array: np.ndarray, radius: int = 1) -> np.ndarray:
    windows = _window_view(array, radius, np.nan)
    with warnings.catch_warnings(), np.errstate(invalid="ignore"):
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return np.nanmean(windows, axis=(-2, -1)).astype(np.float32)


def _nan_local_std(array: np.ndarray, radius: int = 1) -> np.ndarray:
    windows = _window_view(array, radius, np.nan)
    with warnings.catch_warnings(), np.errstate(invalid="ignore"):
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return np.nanstd(windows, axis=(-2, -1)).astype(np.float32)


def _local_range(array: np.ndarray, radius: int = 1) -> np.ndarray:
    windows = _window_view(array, radius, np.nan)
    with warnings.catch_warnings(), np.errstate(invalid="ignore"):
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return (np.nanmax(windows, axis=(-2, -1)) - np.nanmin(windows, axis=(-2, -1))).astype(np.float32)


def _binary_erode(mask: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return mask.copy()
    windows = _window_view(mask, radius, False)
    return windows.all(axis=(-2, -1))


def _binary_dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    if radius <= 0:
        return mask.copy()
    windows = _window_view(mask, radius, False)
    return windows.any(axis=(-2, -1))


def compute_safety_layers(
    height_m: np.ndarray,
    confidence: np.ndarray,
    resolution_m: float,
    vehicle: VehicleProfile,
    min_confidence: float,
    threshold_factor: float = 1.0,
    extra_footprint_margin_m: float = 0.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    smoothed = _nan_local_mean(height_m, radius=1)
    filled = np.where(np.isfinite(smoothed), smoothed, 0.0)
    dz_dy, dz_dx = np.gradient(filled, resolution_m)
    slope_deg = np.degrees(np.arctan(np.hypot(dz_dx, dz_dy))).astype(np.float32)
    roughness_m = _nan_local_std(height_m - smoothed, radius=1)
    step_m = _local_range(height_m, radius=1)

    observed = np.isfinite(height_m) & (confidence >= min_confidence)
    base_safe = (
        observed
        & (slope_deg <= vehicle.max_slope_deg * threshold_factor)
        & (roughness_m <= vehicle.max_roughness_m * threshold_factor)
        & (step_m <= vehicle.max_step_m * threshold_factor)
    )
    hazard = observed & (
        (step_m > vehicle.max_step_m * threshold_factor)
        | (slope_deg > vehicle.max_slope_deg * threshold_factor)
    )
    clearance_cells = math.ceil(vehicle.clearance_margin_m / resolution_m)
    base_safe &= ~_binary_dilate(hazard, clearance_cells)
    footprint_cells = math.ceil((vehicle.footprint_radius_m + extra_footprint_margin_m) / resolution_m)
    safe_centers = _binary_erode(base_safe, footprint_cells)
    return safe_centers, slope_deg, roughness_m, step_m


def _components(mask: np.ndarray) -> list[list[tuple[int, int]]]:
    seen = np.zeros_like(mask, dtype=bool)
    components: list[list[tuple[int, int]]] = []
    rows, cols = mask.shape
    for row, col in zip(*np.nonzero(mask), strict=True):
        if seen[row, col]:
            continue
        stack = [(int(row), int(col))]
        seen[row, col] = True
        component: list[tuple[int, int]] = []
        while stack:
            current_row, current_col = stack.pop()
            component.append((current_row, current_col))
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                nr, nc = current_row + dr, current_col + dc
                if 0 <= nr < rows and 0 <= nc < cols and mask[nr, nc] and not seen[nr, nc]:
                    seen[nr, nc] = True
                    stack.append((nr, nc))
        components.append(component)
    return components


def detect_landing_zones(
    observation: Observation,
    vehicle: VehicleProfile,
    config: DetectorConfig,
) -> Detection:
    safe, slope, roughness, step = compute_safety_layers(
        observation.height_m,
        observation.confidence,
        observation.resolution_m,
        vehicle,
        config.min_confidence,
        threshold_factor=config.threshold_safety_factor,
        extra_footprint_margin_m=config.localization_margin_m,
    )
    min_cells = math.ceil(config.min_region_area_m2 / observation.resolution_m**2)
    unsafe_points = np.argwhere(~safe)
    map_diagonal = math.hypot(*safe.shape) * observation.resolution_m
    candidates: list[Candidate] = []

    for component in _components(safe):
        if len(component) < min_cells:
            continue
        points = np.asarray(component, dtype=np.int32)
        if len(unsafe_points):
            distances_sq = ((points[:, None, :] - unsafe_points[None, :, :]) ** 2).sum(axis=2)
            min_dist = np.sqrt(distances_sq.min(axis=1)) * observation.resolution_m
            center_index = int(np.argmax(min_dist))
            clearance = float(min_dist[center_index])
        else:
            center_index = len(points) // 2
            clearance = map_diagonal
        row, col = (int(value) for value in points[center_index])
        area = len(component) * observation.resolution_m**2
        confidence = float(np.mean([observation.confidence[r, c] for r, c in component]))
        x_m = observation.origin_xy_m[0] + (col + 0.5) * observation.resolution_m
        y_m = observation.origin_xy_m[1] + (row + 0.5) * observation.resolution_m
        distance_cost = math.hypot(x_m, y_m) / max(map_diagonal, 1e-6)
        score = 0.45 * min(clearance / 0.8, 1.0) + 0.30 * min(area / 1.0, 1.0) + 0.20 * confidence - 0.05 * distance_cost
        candidates.append(Candidate(row, col, x_m, y_m, area, clearance, confidence, score))

    candidates.sort(key=lambda item: (-item.score, item.row, item.col))
    return Detection(safe, slope, roughness, step, candidates, candidates[0] if candidates else None)
