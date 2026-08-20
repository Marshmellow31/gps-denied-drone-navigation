# Task Backlog

This is the initial execution backlog. Checkboxes represent repository evidence, not verbal progress.

## Milestone 0 — Requirements freeze

- [ ] Record academic deadline, rubric, demonstrations, and mandatory tools.
- [ ] Record target laptop specifications.
- [ ] Confirm coordinate convention and SI-unit policy.
- [ ] Define provisional drone footprint and safety thresholds.
- [ ] Define tuning/evaluation split and minimum terrain families.
- [ ] Assign three-person workstream ownership.

## Milestone 1 — Repository bootstrap

- [ ] Create installable Python package.
- [ ] Add dependency and Python-version constraints.
- [ ] Add command-line entry point and environment doctor command.
- [ ] Add formatter, linter, type checker, and test runner.
- [ ] Add GitHub Actions checks.
- [ ] Test setup from a clean environment.

## Milestone 2 — Terrain and truth

- [ ] Implement height-map container with resolution and origin.
- [ ] Implement plane and slope primitives.
- [ ] Implement obstacle, step, pit, and rough-surface primitives.
- [ ] Add deterministic composition from configuration.
- [ ] Implement footprint-aware noise-free ground truth.
- [ ] Add at least five versioned sample scenario configurations.
- [ ] Add repeatability and known-location tests.

## Milestone 3 — Sensor model

- [ ] Add configurable measurement noise.
- [ ] Add dropout/missing-data masks.
- [ ] Add configurable sample density or grid resolution.
- [ ] Add optional height-map-to-point-cloud conversion.
- [ ] Prove that truth is isolated from observations.

## Milestone 4 — Geometry detector

- [ ] Implement local slope estimation.
- [ ] Implement local roughness estimation.
- [ ] Implement obstacle mask and clearance expansion.
- [ ] Implement confidence/valid-observation mask.
- [ ] Implement footprint erosion and minimum-area filtering.
- [ ] Add synthetic unit fixtures for each operation.

## Milestone 5 — Candidates and output

- [ ] Label connected safe regions.
- [ ] Extract candidate statistics and representative centers.
- [ ] Define and implement ranking policy.
- [ ] Add deterministic tie breaking.
- [ ] Add explicit no-safe-zone behavior.
- [ ] Save diagnostic layers and a composite overlay.

## Milestone 6 — Evaluation

- [ ] Implement all core landing-zone metrics.
- [ ] Freeze tuning and held-out evaluation suites.
- [ ] Add multi-seed clean/noisy benchmark runner.
- [ ] Save per-run manifests and aggregate machine-readable results.
- [ ] Generate tables, plots, and failure-case gallery.
- [ ] Document thresholds, results, and limitations.

## Milestone 7 — Core release

- [ ] Provide one-command demonstration.
- [ ] Verify from a clean checkout.
- [ ] Complete README and setup instructions.
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
