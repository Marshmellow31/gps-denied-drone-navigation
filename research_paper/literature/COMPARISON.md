# Closest-work comparison for recovery-reliability study

Status: T02 evidence extraction, 22 September 2026. This matrix supports a **candidate gap**, not a novelty claim. “Not found” means not found in the cited inspected material; it does not mean no study exists.

| Work | Claimed target | Estimator / indicator | Formulation reference | Online inputs | Degeneracy mechanism | Transitions tested | Reference truth | Recovery definition | False reassurance / delay | Scene transfer | Relevant results | Limitations and exact evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| X-ICP | Detect and mitigate weakly constrained registration directions | Three-category, per-eigendirection localizability plus constrained scan-to-map ICP | Sections III, V-VI; equations (2), (4)-(6), (23) | Scan, map, point-normal correspondences, pose prior | Insufficient/self-similar geometry makes point-to-plane ICP ill-conditioned | Mixed-geometry paths and smooth partial/non-localizable changes are shown; no prespecified exit-recovery event found | Simulated truth; Leica-based map/trajectory for real sites | **Not found** as sustained post-exit local error | **Not found** | Multiple simulations/sites and VLP-16/OS0-128; not a frozen unseen recovery rule | Better map/APE/RPE than baselines; Seemühle includes 10 m RPE | Paper [Sections VII-C-F](https://arxiv.org/html/2211.16335v3); official code not found; metrics aggregate trajectory/map quality rather than recovery reliability |
| SuperLoc | Predict alignment risk before optimization and actively fuse priors | Per-feature six-direction observability/confidence plus factor-graph LIO/localization | Sections III-B-D; equations (4), (5), (9) | LiDAR/IMU, features/correspondences, initial guess, alternative odometry prior | Raw geometry lacks directional constraint; Hessian eigenvalues vary by sensor/environment | Cave/floor/corridor sequences; no independently annotated post-exit recovery interval found | FARO maps and released TUM trajectories, depending on sequence | **Not found** | **Not found** | Several environments/platforms and sensor comparisons; no frozen recovery transfer rule found | Lower map outlier rates; reported ATE and completeness-aware robustness metric | Paper [Sections IV-A-D](https://arxiv.org/html/2412.02901v1); official code revision `f10e65c...` is later than preprint and requires parity/availability repair |
| AdaLIO | Avoid Faster-LIO divergence in narrow indoor scenes by adapting correspondence parameters | Binary environment-conditioned voxel/search/residual settings in Faster-LIO | Sections 3.1-3.3; Table 1 | LiDAR/IMU, voxelized scan/submap geometry | Narrow volume reduces points/correspondences and skews normals under open-space settings | Exp03 moves from narrow staircase toward parking; no transition metric found | Sparse HILTI-Oxford marker poses, not full trajectories; Exp11 qualitative | **Not found** | **Not found** | Multiple sequences in one dataset; no unseen recovery decision rule | Avoids reported Exp03 divergence and improves challenge score | Paper [Sections 4.1-4.3](https://arxiv.org/html/2304.12577); sparse markers cannot label continuous 6-DoF recovery; official code not found |
| GEODE | Provide heterogeneous degenerate data and benchmark SLAM robustness | Dataset/system benchmark; no proposed health indicator | Sections 3-5; Tables 2-6 | Depends on benchmarked system; dataset includes LiDAR/IMU/camera, though this study would use LiDAR/IMU only | Repetitive/weak geometry, motion, dynamics, FoV, and sensor failures | Whole sequences include tunnels/entries/exits; no transition annotations found | RTK-INS or Vicon 6-DoF for some scenes; metro position-only; stairs PALoc/map-derived, missing for `gamma` | “Recovery” is a system-capability discussion, not a computable sustained local-error label | **Not found** | Broad scenes, LiDARs, and ground/handheld/sailboat platforms | Sequence ATE table exposes many breakdowns; Section 5.2.3 calls out missing failure detection/recovery | Paper [Sections 4.4-6](https://arxiv.org/html/2409.04961); truth quality/DoF varies per sequence, and the dataset is not aerial |

## Candidate overlap

The following territory is already occupied and must not be presented as the new contribution:

- eigenvalue/Hessian-based degeneracy detection and solution projection;
- fine-grained/direction-wise localizability classification;
- predictive observability/confidence from raw correspondence geometry;
- adaptive LIO parameters for narrow/corridor environments;
- broad benchmarking of SLAM in tunnels, corridors, stairs, and other degenerate scenes;
- the theoretical distinction between current local observability and previously accumulated global drift;
- repeated-run reproducibility as a concern in LIO.

## Defensible candidate distinction, pending R1

The inspected anchors do not directly provide a prespecified, transition-centered evaluation in which:

1. geometry exit is annotated independently of the indicator and estimator error;
2. short-window translation and rotation recovery is defined from independent reference as a sustained hindsight outcome;
3. the online indicator is evaluated for false reassurance, missed recovery, availability, and recovery-detection delay;
4. original-frame accumulated drift remains a separate reported outcome; and
5. operating rules are frozen on development trajectories and transferred to unseen scenes.

This is a **candidate empirical distinction** only. X-ICP already analyzes smooth localizability changes, SuperLoc already predicts risk before optimization, and recent 2025-2026 work may narrow the space. A valid contribution therefore depends on R1's fuller overlap audit and an actual measurable transition with adequate reference.

## Unresolved questions for later tasks/review

- Does the final published SuperLoc formulation or supplementary material specify normalization/aggregation details omitted or ambiguous in arXiv v1, and which official code revision corresponds to the paper?
- Can X-ICP be reproduced faithfully without official source, especially its filtering/categorization and translation/rotation scaling?
- Do LA-LIO, ALIVE-LIO, DCReg/direction-level methods, or other 2025-2026 follow-ups report time-to-recovery or false healthy declarations in full text?
- Which method is a fair comparator on FAST-LIO2 when correspondence selection, residuals, priors, and optimizer stage differ?
- Which real sequences contain both a defensible geometry exit and continuous independent 6-DoF truth? T03 must answer eligibility; T04 must verify actual files.

See individual notes and [the query/access record](SEARCH_LOG.md) for traceability.
