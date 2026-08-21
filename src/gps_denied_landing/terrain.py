from __future__ import annotations

import numpy as np

from .models import GridMap


SCENARIOS = (
    "flat_obstacles",
    "mixed_slope",
    "rough_patch",
    "step_and_pit",
    "no_safe_zone",
)


def generate_terrain(
    scenario: str,
    seed: int,
    size_m: float = 3.2,
    resolution_m: float = 0.10,
) -> GridMap:
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario {scenario!r}; choose from {SCENARIOS}")

    cells = int(round(size_m / resolution_m))
    axis = (np.arange(cells) + 0.5) * resolution_m - size_m / 2
    x, y = np.meshgrid(axis, axis)
    rng = np.random.default_rng(seed)
    z = np.zeros_like(x, dtype=np.float32)

    if scenario == "flat_obstacles":
        z += 0.006 * np.sin(2.2 * x) * np.cos(1.7 * y)
        z[(x - 0.72) ** 2 + (y - 0.40) ** 2 < 0.15**2] += 0.24
        z[(x + 0.82) ** 2 + (y + 0.55) ** 2 < 0.12**2] += 0.18
    elif scenario == "mixed_slope":
        right = x > 0.25
        z[right] += (x[right] - 0.25) * np.tan(np.deg2rad(14.0))
        z[(x + 0.72) ** 2 + (y - 0.48) ** 2 < 0.13**2] += 0.20
    elif scenario == "rough_patch":
        patch = (x > -0.15) & (y > -0.75)
        rough = 0.045 * np.sin(24 * x) * np.cos(21 * y)
        rough += rng.normal(0.0, 0.018, size=z.shape)
        z[patch] += rough[patch]
        z[(x + 0.82) ** 2 + (y - 0.62) ** 2 < 0.14**2] += 0.22
    elif scenario == "step_and_pit":
        z[(x > 0.40) & (y > -0.65)] += 0.16
        z[(x + 0.58) ** 2 + (y + 0.42) ** 2 < 0.23**2] -= 0.20
        z[(x - 0.62) ** 2 + (y - 0.72) ** 2 < 0.12**2] += 0.25
    elif scenario == "no_safe_zone":
        z += x * np.tan(np.deg2rad(13.0))
        z += 0.045 * np.sin(18 * x) * np.cos(19 * y)
        for cx, cy in ((-0.8, -0.5), (0.0, 0.4), (0.75, -0.1)):
            z[(x - cx) ** 2 + (y - cy) ** 2 < 0.16**2] += 0.22

    return GridMap(
        height_m=z,
        resolution_m=resolution_m,
        origin_xy_m=(-size_m / 2, -size_m / 2),
    )

