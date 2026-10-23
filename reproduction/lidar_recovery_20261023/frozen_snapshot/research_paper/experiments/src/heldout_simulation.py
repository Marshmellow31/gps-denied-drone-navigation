"""Frozen held-out geometry and sensor-input generator.

Do not call its seed-specific layout/screen/write functions until R3 PASS.
This module is intentionally separate from the development-only T14 generator.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

from simulate_lidar import Surface, scan, simulate_imu_biases
import simulate_lidar as simulator
import t14_formal_route as formal_route


ROOT = Path(__file__).resolve().parents[3]
PROFILE_ID = "T14_FORMAL_X_MINUS_6_V1"
DURATION_S = 60.0
STRATA = {
    "TEST_SHORT_NARROW": {
        "seed_min": 100, "seed_max": 119,
        "length_m": (8.0, 9.0), "half_width_m": (1.3, 1.5),
    },
    "TEST_SHORT_WIDE": {
        "seed_min": 120, "seed_max": 139,
        "length_m": (8.0, 9.0), "half_width_m": (2.5, 3.0),
    },
    "TEST_LONG_NARROW": {
        "seed_min": 140, "seed_max": 159,
        "length_m": (15.0, 18.0), "half_width_m": (1.3, 1.5),
    },
    "TEST_LONG_WIDE": {
        "seed_min": 160, "seed_max": 179,
        "length_m": (15.0, 18.0), "half_width_m": (2.5, 3.0),
    },
}


class HeldoutContractError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stratum_for_seed(seed: int) -> str:
    for name, ranges in STRATA.items():
        if ranges["seed_min"] <= seed <= ranges["seed_max"]:
            return name
    raise HeldoutContractError(f"seed {seed} is not in a reserved held-out stratum")


def build_straight_surfaces(
    length_m: float, corridor_half_width_m: float, room_half_width_m: float,
    control: bool = False,
) -> list[Surface]:
    """Build the frozen box/baffle topology for one parameterized layout."""
    length = float(length_m)
    half_width = float(corridor_half_width_m)
    room = float(room_half_width_m)
    if not 0 < half_width < room or length <= 0:
        raise HeldoutContractError("invalid corridor/room dimensions")
    surfaces: list[Surface] = []
    regions = [(-12.0, 0.0, room), (0.0, length, half_width),
               (length, 50.0, room)]
    for xmin, xmax, width in regions:
        surfaces += [Surface(1, side * width, ((xmin, xmax), (-1.0, 2.0)))
                     for side in (-1, 1)]
        surfaces += [Surface(2, height, ((xmin, xmax), (-width, width)))
                     for height in (-1.0, 2.0)]
    surfaces += [Surface(0, -12.0, ((-room, room), (-1.0, 2.0))),
                 Surface(0, 50.0, ((-room, room), (-1.0, 2.0)))]
    for x in (0.0, length):
        surfaces += [Surface(0, x, (interval, (-1.0, 2.0)))
                     for interval in ((-room, -half_width), (half_width, room))]
    for x, side in ((-8.0, -1), (-2.0, 1), (length + 3.0, -1),
                    (length + 7.0, 1), (length + 12.0, -1)):
        low, high = 0.42 * room, 0.83 * room
        y_bounds = (-high, -low) if side < 0 else (low, high)
        surfaces.append(Surface(0, x, (y_bounds, (-1.0, 1.5))))
    if control:
        for index in range(1, 5):
            x = length * index / 5.0
            surfaces.append(Surface(
                0, x, ((0.65 * half_width, half_width), (-1.0, 1.5))))
    return surfaces


def sample_layout(seed: int, stratum: str, control: bool = False):
    """Sample one frozen held-out layout; call only after the R3 gate."""
    if stratum not in STRATA:
        raise HeldoutContractError(f"unknown held-out stratum: {stratum}")
    bounds = STRATA[stratum]
    if not bounds["seed_min"] <= seed <= bounds["seed_max"]:
        raise HeldoutContractError(f"seed {seed} is outside {stratum}")
    rng = np.random.default_rng(np.random.SeedSequence([int(seed), 0x4C494441]))
    length = float(rng.uniform(*bounds["length_m"]))
    half_width = float(rng.uniform(*bounds["half_width_m"]))
    room = float(rng.uniform(4.5, 7.5))
    surfaces = build_straight_surfaces(length, half_width, room, control)
    entry_s = formal_route.formal_crossing_time_x(0.0)
    exit_s = formal_route.formal_crossing_time_x(length)
    metadata = {
        "layout_family": stratum.lower(), "role": "heldout",
        "layout_seed": seed, "corridor_length_m": length,
        "corridor_half_width_m": half_width, "room_half_width_m": room,
        "entry_plane_x_m": 0.0, "exit_plane_x_m": length,
        "entry_time_s": entry_s, "exit_time_s": exit_s,
        "control_baffles": bool(control),
        "corridor_baffle_x_m": [length * i / 5.0 for i in range(1, 5)] if control else [],
        "vehicle_start_x_m": -6.0, "route_profile": PROFILE_ID,
    }
    return surfaces, metadata


def _scene_coverage(time_s: float, control: bool, surfaces: list[Surface]) -> dict[str, Any]:
    import audit_simulation_scene as scene_audit

    old_trajectory = scene_audit.trajectory
    scene_audit.trajectory = formal_route.formal_trajectory
    try:
        return scene_audit.coverage(time_s, control, surfaces)
    finally:
        scene_audit.trajectory = old_trajectory


def screen_layout(seed: int, stratum: str) -> dict[str, Any]:
    """Scene-only test geometry screen; never reads estimator outputs."""
    corridor, geometry = sample_layout(seed, stratum, control=False)
    control, _ = sample_layout(seed, stratum, control=True)
    midpoint = (geometry["entry_time_s"] + geometry["exit_time_s"]) / 2.0
    post_exit = geometry["exit_time_s"] + 5.0
    degraded = _scene_coverage(midpoint, False, corridor)
    rich_control = _scene_coverage(midpoint, True, control)
    post = _scene_coverage(post_exit, False, corridor)
    eligible = (degraded["axial_normal_fraction"] <= 0.10
                and rich_control["axial_normal_fraction"] >= 0.15
                and post["axial_normal_fraction"] >= 0.20)
    return {
        "seed": seed, "stratum": stratum,
        "geometry": geometry,
        "midpoint_time_s": midpoint,
        "corridor_midpoint": degraded,
        "control_midpoint": rich_control,
        "post_exit_plus5_s": post,
        "eligible": eligible,
        "rule": {"corridor_x_normal_max": 0.10,
                 "control_x_normal_min": 0.15,
                 "post_exit_x_normal_min": 0.20},
    }


def write_sensor_input(
    output_dir: Path, seed: int, stratum: str, control: bool,
    duration_s: float = DURATION_S,
) -> dict[str, Any]:
    """Write one 60 s sensor-only bag and its separately stored analytic truth."""
    if duration_s != DURATION_S:
        raise HeldoutContractError("frozen held-out duration is exactly 60 seconds")
    surfaces, geometry = sample_layout(seed, stratum, control)
    exit_time = geometry["exit_time_s"]
    if duration_s < exit_time + 20.0:
        raise HeldoutContractError("trajectory does not cover the frozen 20 s post-exit horizon")
    output_dir.mkdir(parents=True, exist_ok=False)
    # ROS imports are delayed so geometry fixtures remain independently testable.
    import rosbag
    import rospy
    from sensor_msgs.msg import PointCloud2, PointField, Imu

    imu_noise_seed, lidar_seed, bias_seed = np.random.SeedSequence(seed).spawn(3)
    imu_noise_rng = np.random.default_rng(imu_noise_seed)
    lidar_rng = np.random.default_rng(lidar_seed)
    bias_rng = np.random.default_rng(bias_seed)
    imu_times = np.arange(round(duration_s * 200) + 21) / 200.0
    gyro_bias, accel_bias = simulate_imu_biases(imu_times, bias_rng)
    epoch = 1000.0
    fields = [PointField(name=name, offset=offset, datatype=dtype, count=1)
              for name, offset, dtype in (
                  ("x", 0, 7), ("y", 4, 7), ("z", 8, 7),
                  ("intensity", 12, 7), ("ring", 16, 4), ("time", 18, 7))]
    dtype = np.dtype({"names": ["x", "y", "z", "intensity", "ring", "time"],
                      "formats": ["<f4", "<f4", "<f4", "<f4", "<u2", "<f4"],
                      "offsets": [0, 4, 8, 12, 16, 18], "itemsize": 22})
    scan_count = points_total = 0
    old_trajectory = simulator.trajectory
    simulator.trajectory = formal_route.formal_trajectory
    try:
        with rosbag.Bag(str(output_dir / "sensors.bag"), "w") as bag:
            for imu_index, sample_time in enumerate(imu_times):
                _, _, _, force, gyro = formal_route.formal_trajectory(np.array([sample_time]))
                stamp = rospy.Time.from_sec(epoch + sample_time)
                imu = Imu()
                imu.header.stamp = stamp
                imu.header.frame_id = "sim_body"
                imu.orientation_covariance[0] = -1
                gyro_sample = gyro[0] + gyro_bias[imu_index] + imu_noise_rng.normal(0.0, .002, 3)
                accel_sample = force[0] + accel_bias[imu_index] + imu_noise_rng.normal(0.0, .02, 3)
                imu.angular_velocity.x, imu.angular_velocity.y, imu.angular_velocity.z = gyro_sample
                imu.linear_acceleration.x, imu.linear_acceleration.y, imu.linear_acceleration.z = accel_sample
                bag.write("/sim/imu", imu, stamp)
                if imu_index % 20 == 0 and sample_time < duration_s:
                    points, offsets, rings = scan(sample_time, surfaces, lidar_rng)
                    payload = np.empty(len(points), dtype=dtype)
                    for axis, name in enumerate(("x", "y", "z")):
                        payload[name] = points[:, axis]
                    payload["intensity"] = 1.0
                    payload["ring"], payload["time"] = rings, offsets
                    cloud = PointCloud2()
                    cloud.header.stamp = rospy.Time.from_sec(epoch + sample_time)
                    cloud.header.frame_id = "sim_body"
                    cloud.height, cloud.width = 1, len(points)
                    cloud.fields = fields
                    cloud.point_step, cloud.row_step = 22, len(points) * 22
                    cloud.is_dense = True
                    cloud.data = payload.tobytes()
                    bag.write("/sim/points", cloud,
                              rospy.Time.from_sec(epoch + sample_time + .1))
                    scan_count += 1
                    points_total += len(points)
    finally:
        simulator.trajectory = old_trajectory

    reference_path = output_dir / "reference.txt"
    reference_times = np.arange(0.0, duration_s + .11, .005)
    positions, _, quaternions, _, _ = formal_route.formal_trajectory(reference_times)
    with reference_path.open("w", encoding="utf-8") as stream:
        for sample_time, position, quaternion in zip(reference_times, positions, quaternions):
            stream.write(f"{epoch + sample_time:.9f} "
                         + " ".join(f"{value:.17g}" for value in [*position, *quaternion])
                         + "\n")

    reference_meta = json.loads((ROOT / "research_paper/data/simulation_random_layout_reference_metadata.json")
                                .read_text(encoding="utf-8"))
    reference_meta["evaluation_scope"] = "heldout"
    reference_meta["source"]["sha256"] = sha256_file(reference_path)
    reference_meta["route_profile"] = {
        "profile_id": PROFILE_ID, "vehicle_start_x_m": -6.0,
        "entry_time_s": 10.5, "exit_time_s": exit_time,
        "duration_s": duration_s,
    }
    reference_meta["limitations"].append("held-out geometry stratum; synthetic evidence only")
    metadata_path = output_dir / "reference_metadata.json"
    metadata_path.write_text(json.dumps(reference_meta, indent=2) + "\n", encoding="utf-8")

    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    manifest = {
        "schema": "heldout-simulation-input-v1", "role": "heldout",
        "seed": seed, "layout_seed": seed, "sensor_seed": seed,
        "layout_family": stratum.lower(),
        "stratum": stratum, "control": control, "scene_geometry": geometry,
        "route_profile": {"profile_id": PROFILE_ID, "vehicle_start_x_m": -6.0,
                          "corridor_entry_x_m": 0.0, "entry_time_s": 10.5,
                          "exit_time_s": exit_time,
                          "exit_time_formula": "3 + (6 + corridor_length_m) / 0.8",
                          "duration_s": duration_s},
        "scans": scan_count, "points": points_total, "imu_messages": len(imu_times),
        "epoch_s": epoch, "clock_id": "simulation_epoch",
        "rng": {"geometry": [seed, 0x4C494441],
                "sensor_seed_spawn_order": ["imu_white_noise", "lidar_noise", "imu_bias_random_walk"]},
        "imu_model": {
            "rate_hz": 200, "gyro_white_noise_sd_rad_s": .002,
            "accel_white_noise_sd_m_s2": .02,
            "gyro_initial_bias_sd_rad_s": .003,
            "accel_initial_bias_sd_m_s2": .03,
            "gyro_bias_random_walk_sd_rad_s_per_sqrt_s": .0001,
            "accel_bias_random_walk_sd_m_s2_per_sqrt_s": .001,
            "gyro_bias_initial_rad_s": gyro_bias[0].tolist(),
            "accel_bias_initial_m_s2": accel_bias[0].tolist(),
            "gyro_bias_final_rad_s": gyro_bias[-1].tolist(),
            "accel_bias_final_m_s2": accel_bias[-1].tolist(),
        },
        "truth_in_sensor_bag": False, "generator_sha256": sha256_file(Path(__file__).resolve()),
        "simulator_sha256": sha256_file(Path(simulator.__file__).resolve()),
        "formal_route_sha256": sha256_file(Path(formal_route.__file__).resolve()),
        "code_revision": revision,
        "limitations": ["synthetic analytic truth", "single prescribed motion",
                        "ideal clocks/extrinsics", "uncalibrated sensor stress values"],
    }
    for name in ("sensors.bag", "reference.txt", "reference_metadata.json"):
        path = output_dir / name
        manifest[name] = {"size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                               encoding="utf-8")
    return manifest
