# Candidate gap decision

26 September 2026. **R1 PASS for protocol design only.** This is not a
novelty finding, publication claim or authorization to inspect test outcomes.
The updated [R1 review](../reviews/R1_FEASIBILITY.md) and
[overlap audit](RECOVERY_OVERLAP_UPDATE.md) identify a narrow candidate that
is testable with the amended simulation evidence.

## Candidate question

For a fixed LiDAR-inertial estimator, does an online geometric health value
predict when **reference-defined short-window translation and rotation
accuracy is sustained again after an independently annotated geometry exit**?
Measure false-healthy decisions, availability, non-recovery and time to a
causal healthy decision; keep accumulated drift separate. Test the operating
rule on scene clusters not used to choose it.

This is an empirical evaluation question, not a new detector. ICA already
compares methods across several geometry transitions and plots local RTE and
longer-horizon ATE through degeneracy intervals. DCReg explicitly evaluates
time-varying direction masks, over/under-detection and degeneracy ratios, and
its supplement reports registration recall at pose-error cutoffs. ALIVE-LIO
reports slow recovery and missed corrective updates. Therefore generic
degeneracy detection, local/global error separation, recovery difficulty,
time-series plots and false-detection language are not contributions by
themselves.

The potential distinction is the sustained relationship between an online
health decision and actual **post-exit local motion accuracy** at the system
level, with event-based denominators and a frozen decision rule transferred
to untouched scene templates. The review judged this sufficiently distinct
to test at protocol stage. Broader literature may still reveal closer work;
no “first” claim is permitted.

## Limits and next gates

The only end-to-end evidence is a single synthetic scene pair and seed. The
bias settings are not hardware-calibrated, the geometry is rectangular, and
the real Hilti reference is incomplete and partly map-derived. These limits
prevent a publication conclusion or generalization claim today.

Next: T10 must select and specify the published detector comparator(s),
including exact equations, input stage, scaling, code revision and any
FAST-LIO adaptation. T11 must define the sustained label, false-reassurance
denominators, delay/censoring, availability and scene-level split. T12 must
implement and smoke-test the protocol's distinct development/held-out layout
families. R2 must review all three before a batch or final evaluation.

See the [matrix](COMPARISON.md), the [full ICA audit](INFORMED_CONSTRAINED_ALIGNED.md),
the [overlap refresh](RECOVERY_OVERLAP_UPDATE.md) and
[execution status](../execution/STATUS.md).
