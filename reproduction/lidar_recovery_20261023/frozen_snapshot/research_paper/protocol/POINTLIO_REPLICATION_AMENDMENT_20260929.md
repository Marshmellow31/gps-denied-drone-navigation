# Accepted R2 amendment: Point-LIO replication indicator

**Status:** Accepted on 29 September 2026 for the Point-LIO measurement-
adaptation specification only. An independent review returned **PASS** for
the exact content recorded in this file; the final accepted-file hash and
review record are listed in [`FREEZE.md`](FREEZE.md) and decision D050. The
first draft received **REVISE**. The accepted version incorporates the four
required repairs in
[`POINTLIO_INDICATOR_FEASIBILITY.md`](../reviews/POINTLIO_INDICATOR_FEASIBILITY.md).
No Point-LIO health output, threshold or replication result has been generated.
No held-out data were accessed.

## Purpose and scope

The study already compares a conventional geometry score and the DCReg
directional detector on FAST-LIO. The complete-paper plan requires a second
backend, Point-LIO, to test whether the finding can be reproduced by another
existing LiDAR-inertial estimator. T15 established pose-output compatibility
only. This amendment defines a separate Point-LIO adaptation of the same two
measurement-geometry indicators. It does not introduce a new estimator,
change the recovery labels, change the 48-pair final sample size, or alter the
primary FAST-LIO analysis.

The protocol review is complete, but implementation and replication are not.
After this accepted text and the linked metric/indicator amendments are
hash-recorded, analytic contract fixtures and a development-only health
sidecar may be implemented. The retained seed-14 sidecar-on/off feasibility
check may follow only after those fixtures pass; it must not fit a threshold.
The full 32-pair development replication additionally requires the one-seed
implementation acceptance in the order below. Overall R3 must still pass
before any held-out data are generated, screened or opened.

## Pinned source and formulation boundary

- Official Point-LIO repository: `https://github.com/hku-mars/Point-LIO`.
- Pinned revision: `4b86a469eb5572e70ed575af25b5f15dd06e8e3c`.
- T15 config SHA-256:
  `d23bd8799c3834ac0acc1d23476a0a0c0cd72b09f7b7c542b5bfbe9813a4c98b`.
  It sets `use_imu_as_input: 0`, `extrinsic_est_en: false`, identity simulated
  extrinsics, and a 10 Hz LiDAR profile.
- The existing compatibility patches are build-only: Point-LIO C++17/glog
  export and missing `<deque>` include. Their SHA-256 values are
  `2006e7af098c3fe9b342dd2a52d10d3b69891f4d985332fd64ab48767feb6ddb` and
  `39594d3c07861467151ec7218471513016e286d87a8abfae248a1d37fcf6f4bf`.

At `src/Estimator.cpp:h_model_output` (pinned lines 218–321), Point-LIO
selects its own five-neighbor point-to-plane rows after plane-fit and
residual/range gates. For each accepted row, the first six `h_x` columns are
world translation followed by right/body-tangent rotation:

```text
J_g = [n_W^T, (p_B × R_g^T n_W)^T]
```

With fixed extrinsics, the six remaining columns are zero. An independent
finite-difference review confirmed the first-six-column order, sign and basis
against T08 in this configuration. Point-LIO uses its own map correspondences
and filtering; these are **not** shared rows with FAST-LIO, and the adapter is
not a reproduction of the full DCReg system.

The pinned dynamic update sets `maximum_iter=1`. The estimator processes
point-time groups within a LiDAR frame: the state changes between groups, but
map insertion occurs only after the frame. The native frame-end pose uses
`lidar_end_time` when `publish_odometry_without_downsample=false`. Its configured
`lidar_meas_cov=0.01` is not used as the score normalizer: pinned IKFoM treats
`M_Noise` differently in its small- and large-group branches. The diagnostic
below is raw measurement geometry, not posterior information or a claim that
the EKF uses an inverse-noise weight of `0.01`.

## Point-time grouping and 10 Hz frame output

The amendment defines one diagnostic row per input LiDAR frame so it can be
associated with the frozen 10 Hz decision grid. This is a **frame-pooled
measurement-geometry score**, not the information matrix of one scan-end
state estimate.

1. At receipt of each raw PointCloud2 message, assign a monotonically increasing
   `frame_id` and retain its header timestamp. This callback-side frame ledger
   must run before preprocessing can drop an empty or fully filtered cloud.
   Carry the ID through `Measures` to the frame-end odometry publisher, place it
   in `nav_msgs/Odometry.header.seq`, and have the shared pose logger retain it
   as `source_frame_id`. Use the same ID in the health row and reset-event log.
2. In each point-time group `g`, snapshot the exact pre-update rotation `R_g`
   at the same `h_model_output` evaluation that builds that group's accepted
   `h_x` rows, before the EKF applies `boxplus`. Retain that snapshot through
   aggregation; do not read the post-update rotation. Because the pinned update
   uses `maximum_iter=1`, each scheduled group has one measurement
   linearization; never add a group twice.
3. For each accepted row, transport the rotational columns into a single world
   tangent basis before pooling:

   ```text
   J_translation,world,g = J_translation,g
   J_rotation,world,g   = J_rotation,body,g R_g^T
   J_common,g           = [J_translation,world,g, J_rotation,world,g]
   H_frame              = Σ_g J_common,g^T J_common,g
   N_frame              = total accepted rows in the included groups
   ```

   This prevents a sum from mixing right-tangent rotation coordinates attached
   to different group poses. It does not change the estimator update.
4. For a normal frame, timestamp the one diagnostic record at the actual
   `lidar_end_time`, derived from the maximum usable per-point offset. Keep the
   actual timestamp and `timestamp_source=ACTUAL`; do not snap it to a 10 Hz
   tick. The frozen association rule later chooses the latest record at or
   before a decision tick if no more than 0.2 seconds old and in the same
   segment.
5. If an input frame has no usable points or offsets, use
   `header_stamp + 0.1 s` for this fixed 10 Hz simulator profile and record
   `timestamp_source=NOMINAL`. This fallback is only for an unavailable frame
   record; it must not be used to stamp a normal frame.

The exporter must emit exactly one diagnostic row for every input LiDAR frame,
including startup, map-initialization, empty, fully filtered and skipped frames.
It must compare the emitted `frame_id` set/count with the input bag's
`/sim/points` message audit. A missing input/output diagnostic is
`RUN_INCOMPLETE`, not a reason to synthesize a healthy row. Every diagnostic
row carries `frame_id`, timestamp, `timestamp_source`, `segment_id`, expected,
processed and empty group counts, accepted count, source stage, validity and
unavailable reason. Each emitted frame-end pose row carries the same
`source_frame_id`; sidecar-on/off runs set this header field identically so
their emitted pose values, timestamps and frame IDs remain exactly comparable.

`expected_group_count` is the number of native measurement-group updates
scheduled for that frame's processing stage. Startup, map-initialization and
callback-dropped empty frames schedule no measurement update, so both expected
and processed counts are zero. Do not inherit a nonzero expected count merely
because native code constructed `time_seq` before taking an initialization
`continue`. For a frame that enters the measurement-update stage, every
scheduled group is expected and must be accounted for, including groups with
zero accepted correspondences. A separate raw geometric group count may be
retained for audit, but it does not replace the scheduled-update count.
At shutdown, flush every completed row and compare the pending-frame ledger
with the input audit; any frame left pending or absent makes the run
`RUN_INCOMPLETE` and remains in the attempt ledger.
Treat `processed_group_count != expected_group_count` for a measurement-stage
frame the same way: it is an incomplete frame/run, not an ordinary
empty-correspondence group.

### Frame-level availability

- Startup initialization and map-initialization frames are explicitly
  `UNAVAILABLE` with `STARTUP_INITIALIZATION` or `MAP_INITIALIZATION`.
- An empty or fully filtered input frame is `UNAVAILABLE` with
  `EMPTY_OR_FILTERED_INPUT`.
- A point-time group with zero accepted rows contributes no matrix row and no
  Hessian entry; count it as an empty group. A group with fewer than six
  accepted rows is not individually rejected if the completed frame's
  aggregate has at least six rows.
- A completed frame is `VALID` when `N_frame >= 6` and the common-basis
  aggregate is finite and numerically valid, all expected point-time groups
  completed processing, and no reset/numerical error occurred, even if some
  ordinary groups had no correspondences. Its empty-group and accepted-group
  counts remain visible; missing groups are never filled with zeros.
- A finite positive-semidefinite rank-deficient matrix with `N_frame >= 6`
  remains valid. Its zero minimum eigenvalue is valid, and DCReg reports a
  degenerate subspace with explicitly unbounded ratios. Singularity alone is
  not `UNAVAILABLE`.
- A non-finite row, materially non-PSD result or failed eigensolver makes the
  entire frame `UNAVAILABLE / INDICATOR_NUMERIC_FAILURE`; do not form a partial
  score from corrupted values.
- If `N_frame < 6`, report `UNAVAILABLE / INSUFFICIENT_CORRESPONDENCES`.
- An incomplete/crashed frame remains a run failure in the durable attempt
  ledger. It is not a non-recovery label and is never replaced with a different
  seed.

### Reset and pose-segment contract

The first `ImuProcess::Reset()` during normal startup is
`STARTUP_INITIALIZATION`, not a later estimator reset and not a new segment.
For an explicit later `flg_reset` that clears Point-LIO state/map:

- emit an append-only `reset_events.csv` row with event order, affected
  `frame_id`, sensor timestamp, reset reason, and old/new `segment_id`;
- mark the frame intersecting the reset `UNAVAILABLE / RESET_IN_FRAME` and
  clear its pending frame Hessian accumulator;
- increment `segment_id` before processing the next frame and write that ID on
  subsequent diagnostics;
- run a truth-free pose segment joiner over the original emitted pose CSV,
  diagnostic rows and reset events. For each emitted pose, join to exactly one
  diagnostic/frame-ledger entry by `source_frame_id`, verify its timestamp
  against that frame's actual `lidar_end_time`, then attach the shared segment
  ID. A missing/ambiguous identity, timestamp mismatch or unmatched emitted
  pose makes the run incomplete. Do not require a pose for every unavailable
  startup/empty/reset frame; preserve absent poses as unavailable under the
  frozen outcome rules, and use flushed-count/lifecycle checks to detect logger
  truncation. A reset-intersecting frame has no valid pose/health observation;
  if Point-LIO publishes a pose for it, tag that pose invalid in the adapter;
- never pool Hessians across a reset and never evaluate a motion window across
  segment IDs.

The common pose logger currently sees timestamp regression/frame-ID changes,
not arbitrary internal map resets. Record the reset event directly at
Point-LIO's later reset branch; do not infer it from the startup
`Reset ImuProcess` log line. The pose joiner uses only `source_frame_id`,
timestamps and reset events, never reference or error data. A bounded fixture
must force a later reset and prove that both streams get the same boundary and
no cross-boundary window is evaluated. It must also include a group whose
orientation changes during its update and show that the captured pre-`boxplus`
rotation reconstructs the rows while a post-update rotation does not. These
diagnostics must not change the estimator's state-update equations.

## Indicator outputs

Let `S_L = diag(1,1,1,1/L,1/L,1/L)`. For fixed `L=1, 3, 5 m`, compute:

```text
G_PointLIO,L = S_L H_frame S_L / (N_frame × 0.001)
```

Use `L=3 m` as the primary Point-LIO `lambda_min` score and retain `L=1 m` and
`L=5 m` as the frozen sensitivity outputs. The common `0.001` normalization
preserves the T08 score definition; it does not change Point-LIO's configured
`lidar_meas_cov=0.01` and does not imply equal posterior information. Do not
omit the sensitivity outputs unless a further reviewed amendment justifies
that omission.

For `POINTLIO_DCREG_SCHUR_MASK`, pass the raw common-basis `H_frame` and
`N_frame` into the existing frozen Schur detector. Preserve the rotation/translation
permutation, `rcond=1e-12`, PSD tolerance, minimum six accepted rows, explicit
unbounded-ratio fields and strict `kappa > 10`. Its ratios are invariant to a
uniform positive scale.

The Point-LIO method/stage ID and backend-specific rows remain distinct from
the FAST-LIO exporter. Point-LIO uses its own pose stream for the unchanged R2
recovery labels and local-motion errors; do not copy FAST-LIO event outcomes,
thresholds, caches or poses. Select one global Point-LIO `G_3m` threshold
separately under the exact R2 development-only rule:

- fit only the 32 corridor development seeds `14–45`; controls and seed-14
  feasibility do not fit the threshold;
- candidates are unique finite valid Point-LIO `G_3m` scores plus `NO_ALARMS`;
- healthy is `score >= threshold`; among candidates with conditional event
  false-healthy rate at most 10%, maximize sensitivity across truth-recovered
  corridor events;
- a no-score event or missing qualifying post-onset alarm is a sensitivity
  miss; ties choose the higher numeric threshold and `NO_ALARMS` is the final
  zero-sensitivity candidate;
- if the false-healthy denominator is zero or every feasible candidate has
  zero sensitivity, report `NO_FEASIBLE_OPERATING_POINT`;
- use one selected global Point-LIO threshold on all layouts. Never tune it per
  scene or using held-out output. Keep FAST-LIO's threshold independent, and
  do not change the frozen primary sample size from Point-LIO development
  outcomes.

## Acceptance order

1. **COMPLETE — protocol review PASS.** The independent review covered frame
   emission, timestamps, partial-group validity, reset sharing, `L=1/3/5`,
   and separate Point-LIO threshold selection. Hash-record this accepted
   amendment together with the linked indicator/metric updates before
   implementation; do not treat the review as implementation acceptance.
2. Add analytic tests for known Jacobian rows, tangent transport, frame
   aggregation, 1/3/5 m scaling and Schur parity. A finite PSD rank-deficient
   frame with at least six accepted rows remains valid (`G_3m` can be zero;
   DCReg is valid/degenerate with unbounded ratios). A completed frame with
   ordinary empty groups and at least six total rows remains valid; one group
   may have fewer than six rows. Verify that processed-group count equals the
   frame's expected count. Total count below six, numerical failure, reset in a
   frame, missing input frame or incomplete processing each exercise the
   specified unavailable/run-failure reason. Force a post-start reset and
   verify matching `frame_id`/segment behavior in both diagnostic and pose
   outputs; verify startup reset stays in segment zero.
3. Build a development-only sidecar with no estimator state/covariance writes.
   On retained seed 14, prove sidecar-on/off pose streams are byte-identical,
   match frame identities to the bag, verify startup/unavailable rows, record
   exact hashes and confirm output flush. This feasibility check performs no
   threshold selection and adds no event.
4. Only after steps 1–3 pass, run all 32 Point-LIO development
   corridor/control pairs. Use Point-LIO's own poses/reference and the frozen
   threshold rule. Report every crash, incomplete frame, unavailable outcome
   and no-alarm case; never drop or replace an attempt. Freeze code, source,
   configuration, threshold and output identities before held-out work.

This accepted amendment authorizes only the bounded implementation steps
above after the dated hash read-back. It does not authorize threshold fitting
from the seed-14 feasibility run, the 32-pair batch before one-seed acceptance,
or any held-out screen/final evaluation before overall R3 PASS.
