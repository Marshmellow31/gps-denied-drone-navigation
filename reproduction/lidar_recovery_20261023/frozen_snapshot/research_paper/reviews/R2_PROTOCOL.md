# R2 — PASS for protocol content only

**Review date:** 26 September 2026  
**Reviewer:** GPT-6 Astra, independent read-only review task  
**Reviewed repository HEAD:** `f09f62fa805082b8138a44a2f43833f68e0c39d3`  
**Worktree:** dirty; governing-file content is identified by the hashes in
[`protocol/FREEZE.md`](../protocol/FREEZE.md).

## Verdict

**PASS for protocol design and freeze content.** The latest review re-read the
amended T10–T12 documents and found no remaining critical ambiguity that would
force a new methodological choice. The two earlier R2 reviews returned
**REVISE**; their findings and resolutions are summarized below. This PASS is
not a novelty, publication, implementation, held-out-data, or result verdict.

R2 does not authorize final testing. It permits T13–T14 implementation and
development work only after the content and hash freeze are read back. Held-out
layouts must not be generated or screened before R3 passes.

## Evidence audited

- [T10 indicator specification](../protocol/INDICATORS.md), including DCReg
  source equations, FAST-LIO adaptation boundary, rank/count policy, score and
  serialization rules.
- [T11 metrics proposal v0.4](../protocol/METRICS.md), including time/pose
  association, recovery/re-lapse state, causal alarm machine, denominators,
  threshold calibration, sample size and uncertainty procedures.
- [T12 simulation protocol](../protocol/SIMULATION.md), [split manifest](../data/SPLITS.csv),
  current feasibility reports/manifests and sequential scratch budget.
- [Data contract T11 amendment](../protocol/DATA_CONTRACT.md), T10–T12 handoffs,
  R1 review, scope amendment, decision log, current status, and repository
  source/configuration files.
- DCReg v3 primary-paper equations and the recorded official implementation
  revision; this is an indicator-module adaptation, not a full DCReg
  reproduction.

## Prior REVISE findings and resolution

1. **First REVISE:** the previous protocol did not settle premature alarms,
   window/score association, failures and availability, threshold/curve
   construction, sample-size/bootstrap details, or DCReg numeric boundaries.
   Proposal v0.3 addressed those items but still required a second review.
2. **Second REVISE:** the exact integer-second pose requirement was incompatible
   with FAST-LIO's scan-end timestamps (597 seed-14 poses, zero exactly on
   integer seconds). Alarm confirmation time/state re-arming, indicator invalid
   record barriers, relapse denominators and bootstrap details also needed
   refinement.
3. **Final review:** the shared nearest-pose association at each nominal
   integer boundary resolves the timing mismatch; the state machine uses one
   third-decision-tick transition per continuous healthy run; invalid records
   are barriers; relapse and failures have explicit handling; statistical
   resampling is deterministic and failure-visible. DCReg's equations are
   faithful to Sections 4.2–4.4, with all deviations named as adaptations.

The user explicitly approved the two protocol choices that required user
direction: all three local-motion windows must finish within `t_exit+20 s`, and
formal T14 routes start at x=-6 m (entry at 10.5 s). The earlier seed-14 smoke
remains feasibility-only.

## R2 acceptance audit

| Area | R2 disposition |
| --- | --- |
| Numerical definitions and outcome denominators | PASS — local errors, grid-boundary pose association, 20 s triple completion, debounce, false-healthy measures, recovery sensitivity/delay, relapse, missing data and run failure are specified. |
| Method fidelity | PASS — FAST-LIO `G_3m` and DCReg Schur direction mask use the same accepted correspondences; source equations, strict threshold, correspondence minimum, eigentolerance, pseudoinverse setting and non-finite serialization are explicit. |
| Reference uncertainty | PASS for the bounded simulation study — analytic truth is independent of FAST-LIO but is synthetic, idealized and not a physical reference; Hilti remains supporting only. |
| Event independence and split separation | PASS — geometry seed is the unit; fixed v3 repeats are one cluster; 32 development layouts and reserved held-out strata are disjoint. No held-out inputs/results have been generated or inspected. |
| Simulator feasibility | PASS for protocol — fixed and randomized feasibility smokes exist. T14 still must implement the formal x=-6 m route and repeat its geometry-only screen before development LIO runs. |
| Sample size and uncertainty | PASS — 32-pair development variance rule, 48–80 held-out events, fixed-stratum bootstrap, seed order, interval method and stop conditions are specified. |
| Resource and execution plan | PASS for protocol — process one paired input at a time in checked scratch, retain hashes/manifests and compact outputs, preserve failures, and stop on insufficient space; 60 s runtime remains a planning estimate for T14 to measure. |
| Permitted tuning and gates | PASS — only one global FAST-LIO threshold is calibrated under the frozen development rule and locked at R3. T13/T14/T15/T16 obligations remain explicit; R2 is not R3. |

## Remaining boundaries

- No recovery result, fitted FAST-LIO operating threshold, or final-test result
  exists.
- The 32 formal development layouts have not been re-generated/replayed under
  the x=-6 m route; only the prior x=-5 m seed-14 feasibility smoke exists.
- Held-out generator code is not implemented. Held-out seeds remain untouched
  until R3 and the final-evaluation handoff.
- Simulation parameters are uncalibrated stress settings. The claim is limited
  to parameterized straight-corridor layouts and cannot establish flight
  safety, real-world accuracy or publication novelty.
- Before any experiment batch, re-read the content hashes and status in
  [`protocol/FREEZE.md`](../protocol/FREEZE.md). Any governing-file change
  requires a dated amendment and an account of affected evidence.
