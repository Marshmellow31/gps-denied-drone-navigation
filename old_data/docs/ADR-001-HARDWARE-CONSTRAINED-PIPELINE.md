# ADR-001: Hardware-Constrained Perception Pipeline

**Status:** Accepted for the first baseline  
**Date:** 21 August 2026  
**Deciders:** Project team; thresholds and final purchase still require faculty/team review

## Context

The project must produce an algorithm that can later run on an inexpensive drone with an inexpensive LiDAR-class sensor. A desktop simulation that starts from a dense, perfect height map would not demonstrate that. The first baseline therefore needs a real sensor and compute contract, incomplete-data behavior, resource measurements, and a clean boundary to a flight controller.

## Decision

Use a **sensor-to-local-elevation-grid-to-safe-target** architecture:

```text
Budget ToF/LiDAR + flight-controller local pose
                    |
                    v
          timestamped sensor adapter
                    |
                    v
     bounded robot-centric elevation grid
       (height, variance, count, age)
                    |
                    v
   slope / roughness / step / confidence
                    |
                    v
 footprint-safe regions + ranked target
                    |
                    v
      validated target adapter only
                    |
                    v
       PX4/ArduPilot flight controller
        (stabilization and failsafes)
```

The baseline sensor profile is a downward-facing **VL53L5CX-class 8×8 multizone direct-ToF module**, conservatively simulated at 15 Hz rather than its maximum advertised rate. The deployment floor is a **Raspberry Pi Zero 2 W-class** companion computer: 1 GHz quad-core Arm CPU, 512 MB RAM, no GPU requirement. The core stays NumPy-only and uses a bounded 2.5D grid.

The richer second profile is an **LDROBOT LD19-class 2D scanning LiDAR**. It can feed the same elevation-grid contract by accumulating pose-corrected, downward/oblique scan slices. A single-point TF-Luna-class rangefinder is useful for altitude and redundancy but is not accepted as the only terrain-safety sensor because one ray cannot prove full-footprint slope, roughness, or obstacle clearance.

### GPS-denied pose prerequisite

Frame accumulation requires a local pose estimate; the landing detector cannot infer reliable horizontal motion from the downward 8×8 sensor alone. The low-cost integration path is a flight controller with IMU/barometer plus a PMW3901-class downward optical-flow sensor and valid downward range, fused by the flight-controller estimator. PX4 explicitly requires valid range data before using optical flow and documents optical-flow setups for non-GPS position control. The simulator therefore includes pose noise and accumulated random-walk drift, and later versions must consume pose covariance/quality and reject stale or uncertain maps.

The multizone ToF's central robust range can be evaluated as the height input. If flight-controller compatibility or surface performance is inadequate, add a separate TF-Luna-class downward rangefinder; this does not change the terrain-grid or detector interface.

## Hardware facts behind the profiles

| Component | Published capability used by the simulation | Design consequence |
| --- | --- | --- |
| ST VL53L5CX | 8×8 zones, 45°×45° detection volume (65° diagonal), up to 4 m, up to 60 Hz, I²C | First low-mass/low-cost indoor and low-altitude profile; explicitly simulate sparse spatial samples and ambient/dropout degradation |
| LDROBOT LD19 | 47 g, 0.02–12 m, 4,500 ranges/s, 5–13 Hz, UART at 230400 | Second profile for denser scan accumulation; vehicle pose/motion is required to turn 2D slices into terrain coverage |
| Benewake TF-Luna | under 5 g, 0.2–8 m, 1–250 Hz, UART/I²C | Altitude/clearance aid only, not sole landing-zone detector |
| Raspberry Pi Zero 2 W | 1 GHz quad-core Cortex-A53, 512 MB, 65×30 mm, 12 g, advertised at $15 | Minimum compute target; no neural network or GPU dependency in the core baseline |

Sources: [ST VL53L5CX datasheet](https://www.st.com/resource/en/datasheet/vl53l5cx.pdf), [LDROBOT LD19 datasheet](https://www.ldrobot.com/images/2023/05/23/LDROBOT_LD19_Datasheet_EN_v2.6_Q1JXIRVq.pdf), [Benewake TF-Luna](https://en.benewake.com/TFLuna/index.html?proid=328), [Raspberry Pi Zero 2 W](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/).

## Resource and timing gates

These are engineering gates, not current performance claims:

- local map no larger than 64×64 cells in the first airborne prototype;
- perception update target of at least 5 Hz;
- detector p95 target of at most 200 ms on an actual Pi Zero 2 W;
- resident process-memory target below 256 MB on that device;
- no GPU, cloud, internet, ROS, or desktop-only dependency in the detector;
- stale observations and insufficient coverage must produce `NO_SAFE_TARGET`;
- excessive pose covariance or optical-flow/range quality loss must also produce `NO_SAFE_TARGET`;
- a target must contain timestamp, local frame, confidence, footprint clearance, score, and validity duration;
- a companion-computer timeout must cause the flight controller to enter its configured safe action, never continue using a stale target.

Desktop timings are recorded for regression only. Deployment readiness cannot be claimed until the benchmark runs on the target Arm board.

## Options considered

### A. Dense 3D LiDAR from the start

| Dimension | Assessment |
| --- | --- |
| Data quality | High |
| Cost/weight/power | High |
| Academic feasibility | Low |

**Rejected for the baseline:** it would hide whether the method can work under the stated low-cost constraint.

### B. Single-point rangefinder only

| Dimension | Assessment |
| --- | --- |
| Cost/weight | Very low |
| Terrain observability | Insufficient without risky motion or a scan mechanism |
| Integration | Easy |

**Rejected as the only detector input:** keep it as a vertical range/altitude check.

### C. Multizone ToF first, scanning LiDAR adapter second

| Dimension | Assessment |
| --- | --- |
| Cost/weight | Low |
| Terrain observability | Coarse but directly testable |
| Compute | Low |
| Upgrade path | Strong through the common grid contract |

**Accepted.**

## Consequences

- The algorithm will be evaluated under missing, noisy, quantized, pose-corrupted data from the first run.
- High recall is secondary to preventing false-safe targets.
- The first prototype is most credible indoors or under controlled lighting; outdoor sunlight, reflective/absorptive surfaces, dust, rain, and propeller vibration need physical tests.
- LiDAR geometry alone cannot determine whether grass, water, snow, or a weak surface can support the aircraft. Semantic sensing is a future safety layer, not an implied capability.
- PX4/ROS 2 integration remains an adapter. PX4 documents a serial or UDP uXRCE-DDS bridge between the flight controller and companion computer; the core algorithm will not import it.

## Action items

1. [x] Add the conservative multizone-ToF simulation and bounded-grid detector.
2. [x] Record safety, target-validity, coverage, runtime, and peak detector allocation.
3. [ ] Add bright-ambient, low-reflectivity, vibration, motion-distortion, and stronger pose-drift sweeps.
4. [ ] Run the benchmark on a Pi Zero 2 W and record p50/p95 timing, RSS, temperature, and throttling.
5. [ ] Bench-test the selected breakout against ramps, blocks, gravel, grass, dark cloth, reflective material, and sunlight.
6. [ ] Implement a hardware adapter that emits the exact simulated observation contract.
7. [ ] Add PX4 SITL with a target-only interface and explicit stale-data failsafe before any propeller-on test.
8. [ ] Validate PMW3901 optical flow plus range in GPS-disabled SITL/bench tests before using accumulated terrain maps.

## Research basis

The geometry-first choice aligns with published LiDAR landing systems that derive slope, roughness, safe-area size, and confidence from elevation or depth maps. Resource-efficient work also supports bounded or multi-resolution elevation mapping. Relevant starting points include [Chen et al.](https://arxiv.org/abs/2011.13761), [Schoppmann et al.](https://arxiv.org/abs/2111.06271), and the [real-time airborne LiDAR landing-zone study](https://www.mdpi.com/1424-8220/23/7/3491). The flight-controller boundary follows [PX4's documented companion-computer bridge](https://docs.px4.io/main/en/middleware/uxrce_dds), [PX4 optical-flow estimator requirements](https://docs.px4.io/main/en/advanced_config/tuning_the_ecl_ekf.html#optical-flow), and [PX4 failsafe configuration](https://docs.px4.io/main/en/config/safety).
