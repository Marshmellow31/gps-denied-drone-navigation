# Approved amendment: simulation-primary recovery study

26 September 2026. User explicitly approved the proposed simulation-primary
direction with “yes proceed”. This changes the evidence hierarchy, not the
scientific question or sensor scope.

**Question unchanged:** after weak geometric constraints end, how reliably do
existing LiDAR health signals indicate reliable short-term local motion?
Keep local observability, local motion error and accumulated drift separate.
No cameras, controllers, hardware purchase, new full estimator or flight claim.

Primary quantitative evidence will be controlled end-to-end LiDAR/IMU
simulation with exact independently generated trajectory truth, occlusion,
point acquisition timing, matched motion controls and unseen-layout evaluation.
Truth must never enter estimator or online-indicator processes. Real Hilti
recordings remain supporting software/observational examples, not independent
recovery truth. No claim that all public real datasets are unusable.

## Gate amendment, not automatic approval

The original real-reference T09/R1 requirement cannot be met by Hilti. It
remains a documented failure of the original plan. Amended T09 requires a
measurable end-to-end simulated transition pilot and an honest real-data
illustration. Amended R1 must audit simulator validity, actual weak/rich
transition evidence, truth isolation and literature distinction before PASS.
Public data transfer and physical realism remain limitations, not validated
generalization claims.

To remove the R1/T12 circular dependency, authorize **T12 feasibility bootstrap
only** before R1: one development scene/control, sensor tests and one LIO smoke
run. This does not authorize protocol freeze, parameter sweeps, threshold
selection or final-test exposure. After amended R1 PASS, normal T10–T12/R2
protocol work resumes; R2/R3 gates remain mandatory. Failure to produce a
usable simulation pilot returns REVISE, not a fabricated PASS.

Publishability is an aim, not guaranteed by a working simulator. Simulated
results alone must support a useful, defensible finding with faithful
comparators and unseen-scene evidence. Do not claim generic eigenvalues,
corridor experiments, or local-versus-global drift distinction are novel.
