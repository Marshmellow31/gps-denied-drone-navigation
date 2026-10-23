import numpy as np

from gps_denied_landing.models import SensorProfile
from gps_denied_landing.pipeline import run_simulation
from gps_denied_landing.sensor import simulate_multizone_scan
from gps_denied_landing.terrain import generate_terrain


def test_terrain_is_deterministic() -> None:
    first = generate_terrain("rough_patch", seed=7)
    second = generate_terrain("rough_patch", seed=7)
    np.testing.assert_array_equal(first.height_m, second.height_m)


def test_sensor_model_is_deterministic() -> None:
    terrain = generate_terrain("flat_obstacles", seed=2)
    first = simulate_multizone_scan(terrain, SensorProfile(), seed=99)
    second = simulate_multizone_scan(terrain, SensorProfile(), seed=99)
    np.testing.assert_array_equal(first.height_m, second.height_m)
    np.testing.assert_array_equal(first.sample_count, second.sample_count)


def test_no_safe_scene_never_returns_false_target() -> None:
    result = run_simulation("no_safe_zone", seed=0)
    assert result["selected"] is None
    assert result["metrics"]["false_positive_cells"] == 0


def test_baseline_target_is_truth_safe() -> None:
    result = run_simulation("flat_obstacles", seed=1)
    assert result["selected"] is not None
    assert result["metrics"]["target_is_truly_safe"] is True
