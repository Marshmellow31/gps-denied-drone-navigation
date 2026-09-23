# AdaLIO evidence note

## Source and target

Primary source: Hyungtae Lim et al., [“AdaLIO: Robust Adaptive LiDAR-Inertial Odometry in Degenerate Indoor Environments,” arXiv:2304.12577v1](https://arxiv.org/html/2304.12577), accessed 22 September 2026.

AdaLIO targets divergence in narrow/cramped scenes by changing Faster-LIO preprocessing/correspondence parameters when the observed surroundings appear corridor-like. It is an adaptive LIO method, not a general health-indicator benchmark.

## Method and online inputs

- Section 3.1 attributes the observed failure to too few voxelized points/correspondences and imbalanced normals under settings chosen for open space.
- Section 3.2 states the Faster-LIO iterated error-state Kalman filter base.
- Section 3.3 detects likely narrow/degenerate surroundings from voxel-sampled point count and concentration near the sensor, then changes voxel size, normal-search radius, and plane residual margin.
- Table 1 gives two fixed parameter sets: general versus degeneracy cases.
- Online inputs are LiDAR/IMU and scan/submap geometry. Independent reference is evaluation-only.

## Experiments and reference

- Section 4 uses HILTI-Oxford. Exp01-Exp06 provide marker-based validation, while Exp11 is qualitative because it contains narrow spiral stairs.
- Section 4.1 explicitly says the millimetre-level marker poses are not full trajectories. Scores count proximity to markers at 1 cm, 10 cm, and 100 cm thresholds.
- Section 4.2 provides qualitative mapping/divergence comparison; Section 4.3 reports challenge scores and divergence. Exp03 contains a transition from a narrow staircase toward an underground parking lot, so scene transition is present in the trajectory.

## Recovery, reassurance, delay, and transfer

- Searches found neither `recovery` nor `transition` in the paper text; the Exp03 scene change is described narratively.
- **Not found in inspected material:** full time-series truth through the transition, a sustained local-motion recovery definition, false reassurance, detection delay, indicator availability, or fixed-frame accumulated drift separated from local error.
- The method's binary parameter adaptation overlaps a broad “respond to corridor degeneracy” idea, which this study must not claim as novel.
- Evaluation spans multiple HILTI-Oxford validation sequences but uses one dataset and sparse marker scoring; frozen unseen-scene recovery transfer is not established in the inspected material.

## Availability and limitations

No official implementation was linked in the paper and no author/project repository was found by the targeted GitHub search. This is recorded as **not found**, not as proof that code does not exist. The paper's sparse marker reference cannot support the planned continuous translation-and-rotation recovery label.

## Exact evidence locations

- Contributions: Section 1.
- Failure mechanism and base estimator: Sections 3.1-3.2.
- Adaptation: Section 3.3 and Table 1.
- Dataset/reference limitations: Section 4.1.
- Qualitative/quantitative results: Sections 4.2-4.3, Figures 3-5, Table 2.
