# Research Goal: Reliability after LiDAR Degeneracy

Updated: 20 September 2026. Status: LiDAR-focused candidate scope; exact novelty pending. Supersedes the camera-outage proposal and broad adaptive-navigation proposal.

## Goal

Produce a focused research paper on whether LiDAR localization-health indicators correctly identify the return of reliable local motion estimation after geometric degeneracy in GNSS-denied navigation.

The research question and contribution determine the study. Hardware ownership, sensor purchase and embedded deployment are not deliverables. Use public LiDAR/IMU recordings and controlled simulation as evidence. Cameras are excluded from estimator inputs.

## Aim and question

> After an interval of weak geometric constraints, how reliably do existing LiDAR health indicators distinguish recovered local odometry from continuing estimation error?

A corridor can poorly constrain motion along its length. On leaving it, new geometry may improve current scan matching without correcting previously accumulated position drift. That distinction is expected from estimation theory; merely demonstrating it is not sufficient novelty.

The candidate empirical contribution is a transition-focused comparison of health indicators against local-motion recovery, including false reassurances, detection delays, and transfer to unseen scenes. Original-frame drift is a separate outcome, not an automatic failure of local recovery.

## 4W + 1H

| Question | Answer |
| --- | --- |
| What? | Reliability of health indicators during recovery from geometric degeneracy in LiDAR-inertial odometry. |
| Why? | A useful recovery indicator must agree with actual local estimation quality, not merely resumed output or improved scene geometry. |
| Who? | Researchers studying dependable localization for GNSS-denied UAV navigation. |
| Where? | Controlled LiDAR geometry simulations and public recorded sequences containing entry to and exit from weakly constrained regions. |
| How? | Compare established indicators on existing LIO backends against independent reference trajectories; report errors, delays and unavailable outcomes. |

## Minimum study

- Sensors available to estimation: LiDAR and IMU only. Other channels in a public dataset may provide evaluation reference but never online estimator input.
- One phenomenon: geometric degeneracy and recovery. Do not combine camera degradation, weather, sensor blackout, timing faults and navigation control.
- Candidate primary backend: FAST-LIO2. Candidate replication backend: Point-LIO. Confirm suitable timestamped datasets and configurations before final selection.
- Indicators: a conventional Hessian/eigenvalue baseline and a relevant published localizability/risk measure selected after full-text review of X-ICP and SuperLoc. They are not interchangeable full LIO backends. Portability and implementation equivalence must be checked and documented.
- Start with one controlled corridor-to-feature-rich geometry family and one real recorded dataset. Vary degeneracy duration/severity and balance motion, with matched nondegenerate controls.
- Simulated scans must follow ray visibility and occlusion, preserve per-point timing, and include a defined IMU model if used for end-to-end LIO. Ideal point-cloud pairs can validate registration indicators only, not full odometry.
- A lightweight simulation or public replay is enough to test the question; do not construct a full flight simulator unless the protocol requires it.
- No physical data collection, hardware benchmark, camera input, new sensor-fusion stack, flight controller or safe-landing system.

## Data direction

The NTNU aerial LiDAR-degeneracy recordings are a candidate because they were collected on a manually flown aerial robot. Reference accuracy/coverage and suitable recovery transitions still require verification. Ignore radar in estimator inputs.

GEODE is a candidate supplementary degeneracy dataset, but some sequences have only position reference or lack suitable pose ground truth. Verify per-sequence metadata, frames and independence before use. Ground-platform results must not be called drone validation. If no suitable aerial reference exists, narrow the paper's claims rather than invent evidence.

## Evaluation requirements

1. Keep three quantities separate: geometric localizability, short-window relative motion error, and accumulated original-frame pose error.
2. Define recovery by sustained relative-error validity over a frozen window, using independent truth; choose thresholds/windows on development data. A hindsight label may use a subsequent window, but the online indicator may use only data available at its timestamp.
3. Define transition boundaries independently of the indicator under test. In simulation use known scene design; for real data use a prespecified annotation protocol, not detector outputs or selected error peaks.
4. Compare false-reassurance rate with recovery-detection delay and decision availability. An always-unreliable indicator cannot win by silence. Fix operating points or false-alarm budgets using development data.
5. Preserve resets, missing output, crashes and failure to recover. Use censored recovery times or explicit non-recovery outcomes.
6. Report local motion in comparable frames and fixed windows. Use a fixed pre-event alignment for accumulated drift; do not realign after resets to hide discontinuity. Do not label localizability indicators defective merely because they do not estimate accumulated global drift.
7. Standardize point selection, residual definitions, rotational/translational scaling and evaluation timestamps for indicator comparisons. Do not pretend a naive eigenvalue threshold is equivalent to published X-ICP or SuperLoc.
8. Use separate development/test trajectories and unseen scene geometry. Quantify uncertainty by independent trajectory/event clusters, not individual points or adjacent frames.
9. Include matched nondegenerate motion controls, threshold sensitivity and repeated backend execution; publish code revisions, configuration, masks/scenes, timing, references and all failed runs.
10. Derive final repetitions from pilot variability and required precision. No final-test tuning. No numerical novelty or performance claim before experiments.

## Candidate paper outputs

A literature distinction table; a transition-based protocol; two-indicator comparison with one backend and replication on a second; interpretable failure cases and reproducible artifacts. No new algorithm is required for an empirical contribution. If a method is later proposed, its novelty and fair baselines require their own decision.

Figures: corridor-to-rich-scene schematic; localizability/relative-error/drift timeline; false-reassurance versus delay tradeoff; held-out-scene paired results with uncertainty.

## Weekly professor-review milestones

User deadline: first week of November 2026; weekly professor meetings. Laptop: 16 GB RAM and RTX 4060. These are supporting resources, not the basis for the topic. Weekly hours and exact deadline day remain unspecified.

| Week | Reviewable deliverable |
| --- | --- |
| Sep 21-27 | Full closest-work comparison; confirm useful gap, eligible reference data and one transition pilot |
| Sep 28-Oct 4 | Freeze question, indicators, datasets/simulator assumptions, metrics and split policy |
| Oct 5-11 | Reproduce indicators and development experiments; freeze implementation |
| Oct 12-18 | Execute prespecified evaluation and replication; complete failure ledger |
| Oct 19-25 | Analyze uncertainty, alternative explanations and failure cases; finalize supported contribution |
| Oct 26-Nov 1 | Complete manuscript and reproducibility audit; professor review |
| Nov 2-7 | Revision buffer, subject to the actual agreed deadline |

Week-one go/no-go: the exact transition-focused comparison must remain distinct from existing evidence and measurable with valid reference data. Otherwise refine the question before expanding implementation.

## Publication and boundaries

Aim for a focused empirical paper. A simple expected drift demonstration is insufficient. Strong venue suitability requires a useful new finding, rigorous comparison and generalization evidence; acceptance is not guaranteed. See [scope decision](SCOPE_DECISION.md).

No deployment or flight-safety claims from simulation/replay. The archived safe-landing results and held-out seeds remain separate. This project remains independent of VERGE-CUAS.
