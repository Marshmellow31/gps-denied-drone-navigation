# Phased Roadmap

The roadmap protects a complete minimum viable demonstration while leaving room for ambitious extensions.

## Phase 0 — Define the experiment

- Fix initial assumptions about drone footprint and required clearance.
- Define safe slope, roughness, obstacle, and area thresholds.
- Select synthetic terrain families and noise levels.
- Define ground-truth labels and baseline metrics.

**Exit condition:** A written evaluation protocol and a small set of deterministic test scenes.

## Phase 1 — Synthetic terrain baseline

- Generate flat, sloped, stepped, rough, and obstacle-populated terrains.
- Export a height map and/or point-cloud representation.
- Visualize terrain and known-safe regions.

**Exit condition:** Reproducible terrain datasets with ground truth.

## Phase 2 — Geometry-first landing analysis

- Estimate local surface normals and slope.
- Calculate roughness or residual height variance.
- Reject obstacles and enforce clearance.
- Find connected regions large enough for the vehicle.
- Score and rank candidate zones.

**Exit condition:** The system returns explainable landing candidates for every baseline scene.

## Phase 3 — Evaluation and robustness

- Measure detection quality and false-safe decisions.
- Sweep geometric thresholds.
- Add sensor noise, missing data, and terrain variation.
- Record processing time and failure cases.

**Exit condition:** A repeatable results table, plots, and documented limitations.

## Phase 4 — Navigation extension

- Convert unsafe terrain and obstacles into a local cost map.
- Plan a path from a simulated start pose to the selected landing zone.
- Evaluate reachability, path length, clearance, success, and collisions.

**Exit condition:** A simulated agent reaches and lands within an accepted candidate region.

## Phase 5 — Localization/SLAM extension

- Add simulated sequential LiDAR/depth observations.
- Integrate odometry, scan matching, or a suitable SLAM method.
- Quantify pose drift and map error.
- Test the impact of localization uncertainty on candidate selection.

**Exit condition:** GPS-denied motion is demonstrated with quantified localization performance.

## Phase 6 — Optional robotics stack integration

- Package components as ROS 2 nodes.
- Move the scenario to Gazebo if its added fidelity is useful.
- Connect to PX4 Software-in-the-Loop for higher-fidelity control.

**Exit condition:** Integrated simulation without compromising the documented core result.

## Suggested team split

Ownership can rotate, but three parallel workstreams are natural:

1. terrain/data generation and simulation;
2. geometry, candidate scoring, and navigation algorithms; and
3. evaluation, visualization, integration, and documentation.

All members should agree on shared interfaces and participate in final integration and testing.

## Risk controls

| Risk | Control |
| --- | --- |
| Full simulator setup consumes the schedule | Prove algorithms on arrays/point clouds first |
| SLAM becomes the entire project | Treat it as an extension after landing detection |
| Visual demo works but cannot be defended | Define ground truth and metrics before tuning |
| Thresholds overfit one terrain | Sweep varied terrains and noise levels |
| Unsafe false positives are hidden by accuracy | Report the false-safe rate separately |
| Team work does not integrate | Fix data formats and module interfaces early |
