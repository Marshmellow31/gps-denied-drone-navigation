# SuperLoc evidence note

## Source and target

Primary sources: Shibo Zhao et al., [“SuperLoc: The Key to Robust LiDAR-Inertial Localization Lies in Predicting Alignment Risks,” arXiv:2412.02901v1](https://arxiv.org/html/2412.02901v1), the authors' [method/dataset page](https://superodometry.com/superloc.html), and the linked [SuperOdom repository](https://github.com/superxslam/SuperOdom), all accessed 22 September 2026.

The claimed target is predictive alignment-risk/observability assessment before optimization, followed by active fusion of a pose prior in a LiDAR-inertial localization system. It explicitly challenges the generalizability of raw ICP-Hessian thresholds across sensors/environments.

## Formulation and online inputs

- Section III-B derives a point-to-plane constraint matrix from correspondence points/normals (equation (4)).
- Section III-C, equation (5), computes six per-correspondence observability contributions, scaled by squared planarity `a_2D^2`, in world-frame axes. The initial scan-registration guess appears in the rotational cross-product term.
- Section III-D turns confidence into a prior covariance and combines multi-metric ICP, IMU preintegration, and a relative pose prior in a factor graph (equation (9)).
- Online inputs include LiDAR/IMU, extracted points/planes/lines, correspondences, an initial guess, and an alternative odometry pose prior for active fusion. This is broader than an indicator-only API and must be separated when adapting it to FAST-LIO2.

## Experiments relevant to the candidate question

- Section IV-A visualizes confidence/observability in cave, multi-floor, and corridor environments using approximately 10 seconds of aggregated point clouds.
- Section IV-B evaluates localization map outlier rates against FARO ground-truth maps across four cave, one floor, and two corridor sequences and demonstrates active fusion.
- Sections IV-C-D report ATE and a robustness metric on SubT-MRS sequences; the robustness metric combines accuracy and trajectory completeness across an error-threshold range.
- The official page describes eight released datasets and TUM-format ground-truth trajectories, plus ground-truth maps for selected sites.

## Recovery, reassurance, delay, and transfer

- Searches of the full paper found neither `recovery` nor `transition`.
- **Not found in inspected material:** an independent post-degeneracy transition annotation; sustained local-motion recovery label; false-reassurance denominator; recovery-detection delay; censored recovery outcome; or a time-aligned comparison of confidence against short-window translation/rotation error after an exit.
- Figure/sequence-level robustness evidence is close overlap, but it does not by itself answer whether an online health indicator declares recovery correctly and promptly.
- The evaluation spans several scenes/platforms and compares confidence patterns across sensors/environments on the official page. A frozen recovery rule evaluated on unseen transition scenes was not found in the inspected material.

## Official-code inspection

The linked repository was inspected at `ros2` revision `f10e65cd50007767b22e4c401689665e20d827d6` (commit date 23 July 2026). Relevant code exists in:

- `super_odometry/src/LidarProcess/LidarSlam.cpp`: PCA-derived planarity, rotational cross products, translation-normal dot products, histogram aggregation, and six published uncertainty/confidence topics.
- `super_odometry/include/super_odometry/LidarProcess/LidarSlam.h`: observability enums, per-feature structures, uncertainty outputs, and degeneracy fields.
- `super_odometry/src/LaserMapping/laserMapping.cpp`: prediction-source selection and a degeneracy flag in output covariance.

Material cautions at this revision:

- assignments that set `isDegenerate` from uncertainty/histogram tests are commented out in `EstimateLidarUncertainty()`;
- empty translation or rotation histograms are converted to six zero values, so zero is ambiguous without a separate availability flag;
- the repository is newer than arXiv v1 and cannot be assumed to reproduce the paper results without a pinned parity test;
- source naming calls the published 0-to-1 quantities “uncertainty,” while the paper/project explanation often describes confidence/observability. Direction and semantics need verification before T10.

These are code-audit observations, not performance findings. They make official-source parity testable but not automatic.

## Exact evidence locations

- Claimed target and contributions: Abstract and Section I.
- Pipeline: Section III-A and Figure 2.
- Alignment risk and observability: Sections III-B-C, equations (4)-(5).
- Prior fusion: Section III-D, equations (6)-(9).
- Experiments: Sections IV-A-D, Tables I-III.
- Code: revision above, `LidarSlam.cpp` functions `FeatureObservabilityAnalysis`, `computeEigenProperties`, `computeTranslationObservability`, `analyzeFeatureObservability`, and `EstimateLidarUncertainty`.
