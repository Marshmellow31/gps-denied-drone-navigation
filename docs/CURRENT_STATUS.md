# Current Status

**Status date:** 21 August 2026

**Project stage:** Definition complete; implementation not started

This page is the source of truth for what exists today. It should be updated whenever a milestone is completed or the scope changes.

## Completed

- The academic scope is defined: a three-person, third-year, three-credit design project.
- The project is explicitly independent of VERGE-CUAS.
- The core problem is defined as simulation-first safe landing-zone detection from LiDAR/depth-style terrain observations in GPS-denied environments.
- The initial technical strategy is fixed: synthetic terrain first and explainable geometry before SLAM or flight-stack integration.
- Core features and evaluation metrics are identified.
- The staged roadmap, proposed architecture, execution workflow, and initial backlog are documented.
- The public GitHub repository has been created.

## Not yet implemented

- Python package and command-line interface.
- Synthetic terrain generator.
- Height-map, depth-image, or point-cloud data pipeline.
- Slope, roughness, clearance, and support-area calculations.
- Landing candidate segmentation, ranking, and visualization.
- Automated tests and continuous integration.
- Benchmark datasets, experiment results, plots, or report tables.
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
| Synthetic terrain | Not started | Generated scenes and deterministic tests |
| Landing detector | Not started | Metric output and diagnostic overlays |
| Navigation | Deferred | Core detector meets its acceptance gates |
| SLAM | Deferred | Navigation baseline and schedule capacity |
| ROS 2/PX4/Gazebo | Optional | Clear benefit after standalone baseline |
| Physical flight | Out of core scope | Separate safety plan and authorization |

## Immediate next actions

1. Record the target laptop's OS, CPU, RAM, GPU, and available disk space.
2. Create the Python package, pinned environment, test runner, formatter, and continuous-integration check.
3. Implement deterministic height-map generation and ground-truth masks.
4. Implement the geometry layers independently, with unit tests.
5. Combine the layers into candidate regions and a ranked target.
6. Run the first clean/noisy benchmark and publish the results.

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
