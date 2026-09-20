# Current Status

**Status date:** 21 August 2026

**Project stage:** Hardware-constrained simulation baseline implemented; physical validation not started

This page is the source of truth for what exists today. It should be updated whenever a milestone is completed or the scope changes.

## Completed

- The academic scope is defined: a three-person, third-year, three-credit design project.
- The project is explicitly independent of VERGE-CUAS.
- The core problem is defined as simulation-first safe landing-zone detection from LiDAR/depth-style terrain observations in GPS-denied environments.
- The initial technical strategy is fixed: synthetic terrain first and explainable geometry before SLAM or flight-stack integration.
- Core features and evaluation metrics are identified.
- The staged roadmap, proposed architecture, execution workflow, and initial backlog are documented.
- The public GitHub repository has been created.
- An installable NumPy-only package and command-line runner have been added.
- Five deterministic terrain families and independent ground-truth safety masks are implemented.
- A conservative 8×8 multizone ToF observation model includes quantization, noise, dropout, outliers, pose error and random-walk drift, altitude error, attitude/yaw error, and a ten-second survey path.
- Slope, roughness, step, confidence, footprint erosion, connected candidates, scoring, and explicit no-target behavior are implemented.
- Four automated baseline tests pass.
- Tuning seeds 0–49 and untouched held-out seeds 2000–2019 are saved under `results/reference/`.

## Baseline evidence

The held-out v0.1 suite contains 100 synthetic runs: five scenario families times 20 unseen seeds.

| Measure | Held-out result |
| --- | ---: |
| Aggregate predicted-safe-cell precision | 100% |
| Aggregate false-safe-cell rate | 0% |
| Mean recall on scenes containing safe terrain | 6.677% |
| Target availability on safe scenes | 56.25% |
| Target validity when produced | 100% |
| Correct rejection of no-safe scenes | 100% |
| Desktop detector p95 | 2.86 ms |
| Peak traced detector allocation | 341 KiB |

The low recall and 56.25% target availability are intentional conservative trade-offs after pose-drift testing exposed unsafe selections at looser thresholds. The next algorithmic goal is an adaptive second survey that improves availability without relaxing the safety gate. Desktop timing excludes sensor-acquisition time and does not prove Pi performance. Synthetic truth does not model material strength, water, grass, dust, rain, direct sunlight, vibration, or propeller airflow.

## Not yet implemented

- Continuous integration, formatter, linter, and type-check configuration.
- A second LD19 scanning-LiDAR sensor adapter/profile.
- Real sensor logs and calibration.
- Raspberry Pi Zero 2 W timing, RSS, temperature, and throttling measurements.
- Outdoor-light, reflectivity, vibration, motion-distortion, and pose-drift stress suites.
- Navigation, odometry, or SLAM.
- ROS 2, Gazebo, or PX4 integration.
- Hardware flight testing.

No performance claim should be made until an experiment produces saved, reproducible evidence.

## Current readiness

| Area | State | Evidence needed to advance |
| --- | --- | --- |
| Problem definition | Complete | Approved project statement |
| Architecture | Drafted | First implementation validates interfaces |
| Development environment | Specified | Clean setup succeeds on the target laptop |
| Synthetic terrain | Baseline complete | More varied and physically measured terrain models |
| Landing detector | Baseline complete | Improve availability while preserving target validity |
| Navigation | Deferred | Core detector meets its acceptance gates |
| SLAM | Deferred | Navigation baseline and schedule capacity |
| ROS 2/PX4/Gazebo | Optional | Clear benefit after standalone baseline |
| Physical flight | Out of core scope | Separate safety plan and authorization |

## Immediate next actions

1. Confirm indoor/outdoor use, drone size, hardware budget, deadline, and rubric.
2. Add an adaptive second-survey strategy, then ambient-light, reflectivity, vibration, and motion-distortion stress profiles.
3. Run the same benchmark on a Pi Zero 2 W and enforce the 200 ms p95 / 256 MB gates.
4. Buy or borrow the selected multizone ToF breakout and bench-test ramps, blocks, gravel, grass, dark fabric, reflective material, and sunlight.
5. Implement a recorded-log adapter using the same observation contract.
6. Add PX4 SITL only after the perception and stale-data gates pass.

## Definition of done

### Core project

The core project is complete only when all of the following are true:

- A new user can set up and run the project by following `SETUP.md`.
- At least five terrain families are generated reproducibly from recorded seeds.
- Ground-truth safe regions are created independently of simulated observation noise.
- The detector uses slope, roughness, clearance, and minimum support area.
- The system outputs a safety map, candidate regions, a ranked target, and diagnostic visualizations.
- Automated tests cover geometry calculations and known edge cases.
- Clean and noisy experiments report precision, recall, F1, false-safe rate, valid-footprint rate, target error, and runtime.
- Configurations and raw metric files are saved with the results.
- Failure cases and limitations are documented honestly.
- The final demonstration runs from a single documented command.

### Extension project

Navigation, SLAM, and flight-stack integration are complete only if they have their own tests and metrics. A visual simulator demo alone is not sufficient.

## Status update template

When updating this file, record:

- date and milestone;
- what is now demonstrably working;
- command used to reproduce it;
- test and experiment results;
- known failures;
- next acceptance gate; and
- links to the relevant commit and result artifacts.
