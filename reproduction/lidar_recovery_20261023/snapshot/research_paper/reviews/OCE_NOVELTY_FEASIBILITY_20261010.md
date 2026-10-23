# OCE overlap and novelty feasibility review — 10 October 2026

**Decision: PASS for feasibility of the narrowed external evaluation question.**
This is not a publication-novelty verdict, nor an authorization to access
held-out data by itself.

## Primary-source audit

The reviewer read Zhang et al., [OCE: an optimization convergence metric for
LiDAR SLAM degeneracy detection](https://doi.org/10.1007/s43684-026-00144-1),
and the frozen metrics, sample design, and Point-LIO replication freeze.
OCE already evaluates detector agreement with ground-truth local-motion
usability: Section 4.2, Eq. 12 defines 0.5-second axial relative-displacement
error; Eq. 13 sets a nominal-calibrated usability cutoff. Section 4.2 and
Table 1 report frame-level detection errors and onset delay. Section 3.3 and
Algorithm 1 use consecutive healthy frames; Section 4.2 and Table 3 report
premature recovery, switching, and recovery delay. Section 4.2 also reports
coverage and threshold-transfer effects. Local accuracy, hysteresis,
availability, false alarms, and timing individually cannot establish the
gap.

OCE's quantitative comparison is one GICP/LM sequence with perturbations;
Sections 4.3–4.4 give behavioral field evidence. The frozen project instead
asks whether independently calibrated geometric decisions remain reliable
after a predefined exit across untouched straight-corridor length/width
strata, using sustained joint translation/rotation outcomes, event-level
denominators, relapse/non-recovery handling, and independent FAST-LIO and
Point-LIO measurement-stage replication. That supports a useful external
transfer-and-replication question, without establishing that its answer is
new.

## Claim limits and gate consequence

- Describe the held-out design as transfer across untouched corridor
  length/width strata; do not imply new topologies or broad scene-family
  generalization.
- Present the work as an external evaluation of the frozen geometric
  indicators. Do not claim superiority to OCE without implementing and
  comparing OCE.
- Backend replication and sample size support transfer evidence but do not,
  by themselves, prove novelty.
- Keep broader publication positioning contingent on final outcomes and the
  completed literature refresh.

No protocol redesign is required by this source. Bind this review and the
dated overlap addendum into R3 acceptance while preserving every frozen
artifact hash. This review itself does not open the held-out gate.
