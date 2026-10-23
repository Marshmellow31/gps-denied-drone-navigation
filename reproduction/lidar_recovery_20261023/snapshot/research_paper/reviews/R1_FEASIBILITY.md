# R1 — PASS for protocol design only; not a novelty or publication verdict

Second-model re-review: 26 September 2026, GPT-6. This fresh review re-opened
the primary paper text, the available official implementation/supplement,
current manifests and retained v3 outputs. It supersedes the first R1
REVISE-only outcome for the **feasibility gate**. It is not an external human
peer review or a finding that the proposed result is novel or publishable.

## Evidence audited

- Approved [simulation-primary amendment](../SCOPE_AMENDMENT_SIMULATION.md).
- The v3 [simulation model/protocol](../protocol/SIMULATION.md),
  [pilot/report](../evidence/SIMULATION_MOTION_V3.md),
  [manifest](../evidence/simulation_motion_v3_manifest.json),
  [reference metadata](../data/simulation_motion_v3_reference_metadata.json),
  and source/test hashes.
- Retained FAST-LIO v3 corridor/control inputs and outputs under ignored
  `experiments/generated/`, with the logged input/reference/output SHA-256s.
- Current T07/T08 metric and diagnostic derivations, availability rules,
  and the Hilti reference audit. Hilti remains supporting evidence only.
- Full available closest-work sources and exact locations in
  [the comparison matrix](../literature/COMPARISON.md), [ICA note](../literature/INFORMED_CONSTRAINED_ALIGNED.md)
  and [overlap refresh](../literature/RECOVERY_OVERLAP_UPDATE.md).

## Feasibility findings

**Measurable transition: PASS, development only.** The 40 s matched runs have
400 scans each, 397 valid health groups/poses, 754/794 valid local-motion
windows, and zero reference gaps. The input bags contain only LiDAR and IMU;
the analytic reference is separate. The paired 8,021-message IMU streams are
byte-identical. The geometry-only audit at 17 s finds x-facing returns for
342/5,760 rays (5.94%) in the corridor and 1,043/5,760 (18.11%) in the feature
control. In the corridor run's prespecified bins, 1 s local translation-error
medians are 0.093 m before, 1.218 m inside, and 0.0207 m in the extended
post-corridor interval; the smallest online information-value medians at the
3 m scale are 107.5, 15.25 and 141.8. This is one synthetic scene pair/seed,
not a statistical effect or a sustained-recovery label.

**Simulator checks: PASS for feasibility.** Wall shoulders and jambs are
tested, analytic translation/rotation derivatives match independently
computed finite differences, bias streams are seeded/repeatable, and the
40 s run supplies 15.75 s after the second layout crossing. The full suite
reports 40 passed and one SciPy-dependent test skipped (41 executed). The
model still has ideal sensor clocks/extrinsics, rectangular walls and
uncalibrated stress biases.

**Truth, time and frames: PASS for this pilot.** FAST-LIO receives no reference
topic/file; estimator truth remains in offline evaluation. Reference hashes
and time/frame metadata match both runs. Cutoff/startup windows remain named
unavailable values. No final-test layout or threshold was inspected.

## Closest-work decision

The [full ICA audit](../literature/INFORMED_CONSTRAINED_ALIGNED.md) materially
narrows our claim. ICA already studies dynamic transitions, defines “recovery
feasible” from environmental information, plots RTE/ATE over a marked tunnel
degeneracy interval, and analyzes a short-burst building passage. Therefore
generic transition plots, local/global error separation, and recovery from
degeneracy are not distinctions.

DCReg is an additional close overlap. Its main paper reports time-varying
directional detection, over/under-detection and detection ratios. Its
supplement reports registration recall for pose pairs at fixed translation
and rotation error limits alongside degeneracy ratio, ATE/RTE and map scores.
ALIVE-LIO also explicitly reports slow recovery and missed corrective updates.
These works cover generic detection reliability and recovery limitations.

**Candidate distinction judged sufficient to proceed to protocol design:**
test whether an online health value from an already-running LIO system
predicts **sustained reference-defined short-window translation and rotation
accuracy after an independently annotated geometry exit**, with causal
availability, false-healthy declarations, non-recovery/censoring and detection
delay measured on scene clusters held out from operating-point selection.
The contribution would be the event-level relation between indicator and
actual local motion, not a new detector, generic false-alarm metric, corridor
benchmark or explanation of ATE versus RTE. The paper claim remains
unproven; the accessible ICA supplementary videos could not be inspected.

## R1 decision

**PASS for feasibility and protocol design.** The approved simulation supplies
one valid end-to-end transition, isolates truth, and enables the narrowed
outcome comparison. This passes the R1 entry criterion; it does not establish
novelty, generalization, statistical power or publication readiness. The
review does not approve a threshold or test run.

Proceed to T10 comparator specification, T11 outcome/split design, complete
T12 simulation specification, and then R2 review. If T10/T11 cannot define a
fair detector comparison and a usable sustained-local-motion denominator,
return to REVISE before generating a batch. All previously used v2/v3 runs
remain development data. No held-out evaluation is authorized before R2 PASS.

## Post-R1 development update — 26 September 2026

T10 specified DCReg's directional detector as an explicit shared-correspondence
adaptation; T11 defined the proposed sustained label, denominators and split
rule. T12 then generated one 60 s randomized development layout/control pair.
The scene-only screen passed for all 32 reserved development geometry seeds
14–45, but only seed 14 has sensor bags and FAST-LIO outputs. The new pair has
600 scans, 597 valid health groups/poses, 1,154/1,194 valid local windows and
zero reference gaps. These results improve feasibility and variability
evidence; they do not validate the detector adaptation or the held-out plan.
R2 remains the next decision gate.
