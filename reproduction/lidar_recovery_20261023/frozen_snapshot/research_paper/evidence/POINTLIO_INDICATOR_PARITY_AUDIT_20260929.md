# Point-LIO indicator comparability — source audit and review questions

**Date:** 29 September 2026
**Status:** Candidate adaptation for independent protocol review only. No
indicator was added, no Point-LIO replay was run, no threshold was fitted, and
no held-out data were opened.

## Why this audit is needed

The fifth R3 follow-up accepted the FAST-LIO software repairs and native
seed-14 lifecycle, but kept overall R3 at **REVISE** because Point-LIO has only
a pose-output smoke. The complete-paper plan requires a comparable online
health signal and development replication readiness for Point-LIO before any
final-layout exposure. This note identifies a source-derived candidate; it
does not call the adaptation approved or equivalent without review.

## Pinned source and current configuration

- Official Point-LIO repository: `https://github.com/hku-mars/Point-LIO`.
- Pinned revision: `4b86a469eb5572e70ed575af25b5f15dd06e8e3c`.
- The local source clone is at `research_paper/experiments/generated/upstream/Point-LIO`.
  Its current worktree diff SHA-256 is
  `7fc1a91619a310a1e4b44885e95f415f8af89f3885e54556ad14e2bca7668ce3`; the
  visible changes are compatibility patches only. The checked-in patch hashes
  are `2006e7af098c3fe9b342dd2a52d10d3b69891f4d985332fd64ab48767feb6ddb`
  and `39594d3c07861467151ec7218471513016e286d87a8abfae248a1d37fcf6f4bf`.
- Current T15 development configuration SHA-256:
  `d23bd8799c3834ac0acc1d23476a0a0c0cd72b09f7b7c542b5bfbe9813a4c98b`.
  It sets `use_imu_as_input: 0`, `extrinsic_est_en: false`, collocated
  simulated sensors, `lidar_meas_cov: 0.01`, a 16-line LiDAR input, and
  10 Hz scans. Do not change the frozen smoke configuration in place.

## What the pinned code appears to expose

At `src/Estimator.cpp:h_model_output` (pinned source, approximately lines
218–322), Point-LIO selects map correspondences using its own five-neighbor
plane fit and residual/range gate. It then creates a dynamic `h_x` matrix from
the rows that passed those tests. Under the current collocated, fixed-extrinsic
configuration, its first six columns are constructed as

```text
J_i = [ n_W^T, (p_B × (R_BW n_W))^T ]
```

The source writes the three translation-like normal components first and the
three rotation-like cross-product components next; the remaining six columns
are extrinsic terms and are zero when `extrinsic_est_en=false`. This resembles
T08's translation-first six-column point-to-plane Jacobian, but the bases,
sign convention, sequential update stage, map matches and row-selection rules
must be checked before claiming mathematical parity.

The callback sets `M_Noise = laser_point_cov` (currently `0.01`) and the
iterated EKF combines `h_x` with its state prior in
`include/IKFoM/IKFoM_toolkit/esekfom/esekfom.hpp:update_iterated_dyn_share_modified`
(approximately lines 184–230). The proposed diagnostic must use only the raw
accepted measurement rows, not `P_`, the posterior covariance, the IMU prior,
trajectory errors or reference data.

Unlike FAST-LIO's one scan-level accepted-row linearization, this Point-LIO
configuration performs point-time-group updates inside a LiDAR frame
(`laserMapping.cpp`, approximately lines 595–735; grouping comes from
`include/common_lib.h:time_compressing`). A candidate common-rate output would
sum each successful group's `J_i^T J_i` exactly once, sum its accepted-row
count, and emit one record at the frame's `lidar_end_time`. This is causal at
the end of the current LiDAR frame and aligns the indicator with the existing
10 Hz pose output. It is nevertheless an adaptation: Point-LIO's map and
state change during those sequential groups, unlike FAST-LIO's single scan
linearization. An alternative is a higher-rate per-group stream, but that can
change availability and diagnostic age relative to the frozen 10 Hz
comparison. The reviewer should decide which treatment is defensible.

## Candidate outputs

For each completed LiDAR frame, preserve the raw aggregate translation-first
6×6 Hessian `H = Σ J_i^T J_i`, accepted count, group count, unavailable-group
count, timestamp, validity and reason. From that same `H` and count:

1. Compute a weakest-direction score with the fixed 3 m rotational lever arm
   using the T08 matrix scaling. A valid scan needs at least six accepted rows.
2. Pass the raw `H` to the existing frozen DCReg Schur detector, which uses
   the same block permutation, pseudoinverse tolerance and `κ > 10` directional
   mask. Uniform positive scaling cancels from the Schur condition ratios.
3. Keep a failed/empty update explicitly unavailable; never convert it to zero
   or “healthy”. Keep the backend's own accepted-row source label.

The score's residual-variance denominator needs a decision before coding.
T08's frozen FAST-LIO signal uses `N × 0.001`, while this Point-LIO
configuration sets `lidar_meas_cov=0.01`. Candidate A uses the common T08
`0.001` denominator to preserve a shared score definition. Candidate B uses
the Point-LIO configured `0.01` as a backend-specific normalization and
selects any Point-LIO threshold independently on development data. Both leave
the raw Hessian unchanged; neither may be chosen by looking at held-out
outcomes. The published DCReg condition ratios are invariant to this scalar.

## Checks required before development replication

- Confirm the first six columns' order, basis and sign against T08 using
  source equations and an analytic known-geometry fixture.
- Verify the per-frame Hessian is the sum of final-iteration accepted rows
  exactly once per point-time group; do not count every EKF iteration as new
  evidence.
- With the sidecar disabled/enabled, prove pose streams are byte-identical.
- Verify one scan-end diagnostic timestamp per frame, chronological order,
  reset segmentation, logger flush and explicit missing/invalid rows.
- On the retained seed-14 development corridor/control, compare the export
  against direct source-side reconstruction and evaluate the frozen
  unavailable-data policy. Keep this one seed as feasibility only.
- Before selecting any backend-specific threshold or running the full
  32-pair development replication, obtain an independent decision on whether
  the per-point-group aggregation/variance choice requires a dated R2 amendment.
- Only after that decision, use the frozen development seeds and selection
  rule, report every run/failure, and create a separate Point-LIO development
  freeze. No held-out layout is eligible before both backends are frozen.

## Questions for the independent reviewer

1. Does `h_model_output`'s first-six-column Jacobian, with the current fixed
   extrinsic config, satisfy the same measurement-only geometry contract as
   T08, or is there a basis/sign/formulation mismatch?
2. Is summing final-iteration Hessians across Point-LIO's sequential point-time
   groups and emitting at `lidar_end_time` a valid 10 Hz adaptation, or must
   the study use a per-group stream or amend its time/availability contract?
3. Should the primary normalized Point-LIO score use T08's fixed `0.001` or
   its configured `0.01` measurement-noise value? What comparison claim does
   each permit?
4. Does applying the same DCReg Schur detector to Point-LIO's own native
   accepted rows count as a comparable backend replication, and which
   differences must be reported?
5. Which parts can be resolved by the existing development protocol, and which
   require an independently reviewed dated amendment before the 32-pair
   development replication?

No implementation, replay, threshold selection, Point-LIO result or held-out
data access is authorized by this proposal note.
