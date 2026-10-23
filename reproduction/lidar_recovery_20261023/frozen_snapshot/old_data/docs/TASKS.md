# Task Backlog

This is the initial execution backlog. Checkboxes represent repository evidence, not verbal progress.

## Milestone 0 — Requirements freeze

- [ ] Record academic deadline, rubric, demonstrations, and mandatory tools.
- [ ] Record target laptop specifications.
- [ ] Confirm flight-controller, optical-flow, and range hardware.
- [x] Confirm coordinate convention and SI-unit policy.
- [x] Define provisional drone footprint and safety thresholds.
- [x] Define tuning/evaluation split and minimum terrain families.
- [ ] Assign three-person workstream ownership.

## Milestone 1 — Repository bootstrap

- [x] Create installable Python package.
- [x] Add dependency and Python-version constraints.
- [ ] Add command-line entry point and environment doctor command.
- [ ] Add formatter, linter, type checker, and test runner.
- [ ] Add GitHub Actions checks.
- [ ] Test setup from a clean environment.

## Milestone 2 — Terrain and truth

- [x] Implement height-map container with resolution and origin.
- [x] Implement plane and slope primitives.
- [x] Implement obstacle, step, pit, and rough-surface primitives.
- [ ] Add deterministic composition from configuration.
- [x] Implement footprint-aware noise-free ground truth.
- [ ] Add at least five versioned sample scenario configurations.
- [x] Add repeatability and known-outcome tests.

## Milestone 3 — Sensor model

- [x] Add configurable measurement noise and quantization.
- [x] Add dropout/missing-data masks and outliers.
- [x] Add configurable sample density and grid resolution.
- [ ] Add optional height-map-to-point-cloud conversion.
- [x] Keep truth isolated from observations.

## Milestone 4 — Geometry detector

- [x] Implement local slope estimation.
- [x] Implement local roughness estimation.
- [x] Implement obstacle mask and clearance expansion.
- [x] Implement confidence/valid-observation mask.
- [x] Implement footprint erosion and minimum-area filtering.
- [ ] Add synthetic unit fixtures for each operation.

## Milestone 5 — Candidates and output

- [x] Label connected safe regions.
- [x] Extract candidate statistics and representative centers.
- [x] Define and implement ranking policy.
- [x] Add deterministic tie breaking.
- [x] Add explicit no-safe-zone behavior.
- [x] Save diagnostic layers and a composite overlay.

## Milestone 6 — Evaluation

- [ ] Implement all core landing-zone metrics.
- [x] Freeze tuning seeds 0–49 and held-out seeds 2000–2019.
- [x] Add multi-seed noisy benchmark runner.
- [x] Save per-run and aggregate machine-readable results.
- [x] Generate result tables and a diagnostic plot.
- [x] Document thresholds, results, and limitations.

## Milestone 7 — Core release

- [x] Provide one-command demonstration.
- [ ] Verify from a clean checkout.
- [x] Complete baseline README and setup instructions.
- [ ] Prepare report-ready architecture and result figures.
- [ ] Tag the stable core release.

## Optional Milestone 8 — Navigation

- [ ] Define cost-map interface.
- [ ] Add baseline planner and approach simulation.
- [ ] Evaluate success, collision, clearance, path length, and runtime.

## Optional Milestone 9 — SLAM

- [ ] Define sequential sensor and pose interfaces.
- [ ] Integrate selected odometry/SLAM baseline.
- [ ] Evaluate trajectory, drift, map consistency, and runtime.
- [ ] Measure impact on end-to-end landing performance.

## Optional Milestone 10 — ROS 2 / Gazebo / PX4

- [ ] Select mutually compatible pinned versions.
- [ ] Add ROS 2 adapters without coupling core algorithms.
- [ ] Validate Gazebo sensor and coordinate conventions.
- [ ] Integrate PX4 Software-in-the-Loop.
- [ ] Run and record an end-to-end simulated mission.

## Task completion evidence

A task is complete only when applicable evidence exists:

- implementation committed;
- automated tests passing;
- reproduction command documented;
- relevant result or screenshot saved;
- known limitations recorded; and
- current status updated.
