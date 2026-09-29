# Online indicator comparison specification

Version 0.1, 26 September 2026, with the accepted Point-LIO R2 amendment D050
(29 September 2026). The base T10 specification passed R2 and its original
hash read-back; T13 implementation is complete. The FAST-LIO cutoff selected
on T14 development runs remains a candidate until R3. No Point-LIO cutoff has
been selected. The question is whether online registration geometry predicts
later reference-defined local motion accuracy. It is not an estimator bake-off.
No indicator may access the reference, geometry-event labels or trajectory
errors.

## Selected methods

| ID | Method | Output and role |
| --- | --- | --- |
| `FASTLIO_MIN_EIG_G3` | T08's measurement-only accepted-correspondence information matrix, normalized with the fixed 3 m rotation lever scale | Continuous weakest-direction eigenvalue; larger means stronger measurement geometry. Primary conventional baseline. |
| `DCREG_SCHUR_MASK` | DCReg's published directional condition detector applied to the same accepted FAST-LIO point-to-plane correspondences | Raw rotational/translational subspace condition ratios plus six directional flags; no mitigation/preconditioner is run. Primary published comparator. |
| `POINTLIO_MIN_EIG_G3` | Accepted Point-LIO amendment: frame-pooled measurement geometry from Point-LIO's own native measurement rows, with the fixed 3 m rotation lever scale | Separate-backend replication score; not the FAST-LIO score or Point-LIO's posterior covariance. |
| `POINTLIO_DCREG_SCHUR_MASK` | DCReg Schur detector applied to the raw common-basis Point-LIO frame matrix | Separate Point-LIO adaptation; retain frozen `kappa > 10` and explicit unbounded-ratio flags. |

The choice of DCReg over the older X-ICP/SuperLoc candidates follows the
updated R1 audit: DCReg is the closest recent published detector with explicit
time-varying direction flags and a public implementation. X-ICP's categories
and SuperLoc's feature-confidence/fusion pipeline remain in the literature
matrix; they are not silently called equivalent to these two streams. The
SuperLoc code revision inspected earlier has unresolved paper-parity and
availability semantics. If a later review requires X-ICP as an additional
comparator, add a dated amendment before implementation.

## FAST-LIO conventional baseline

Use the [T08 source derivation](FASTLIO_INFORMATION_DIAGNOSTIC.md) exactly.
At each scan, take only the first six columns from the last accepted
`h_share_model` linearization, after FAST-LIO's point selection, plane fit,
residual filters and accepted-correspondence tests. Let `h_i(L)` be the
declared six-vector with translation in metres and rotation divided by lever
scale `L`. Compute:

```text
G_L = sum_i h_i(L)^T h_i(L) / (N * 0.001)
```

Report the raw accepted count, validity/reason, all six ascending eigenvalues,
and the fixed-scale smallest eigenvalue `lambda_min(G_3m)` as the primary
continuous score. Preserve `L=1m` and `L=5m` as scale-sensitivity outputs;
do not select the best scale per sequence. The current export has no calibrated
decision threshold. It is a measurement-only geometric score, not FAST-LIO's
posterior covariance or a guarantee that its pose is accurate.

## DCReg detector comparator

Primary paper: Hu et al., [DCReg arXiv v3](https://arxiv.org/html/2509.06285v3),
10 September 2026; accepted IJRR 2026 version. Official implementation:
[JokerJohn/DCReg](https://github.com/JokerJohn/DCReg), `main` revision
`8ce8451b15491a4bbe17cf85ab02a8bed6696861`. The inspected official
[supplement](https://github.com/JokerJohn/DCReg/blob/8ce8451b15491a4bbe17cf85ab02a8bed6696861/paper/supp.pdf)
reports DR/RR and registration/map metrics. Equations and source locations
are in the [overlap audit](../literature/RECOVERY_OVERLAP_UPDATE.md).

At the same timestamp and from the same accepted point-plane Jacobian used by
FAST-LIO, construct the unweighted measurement Hessian `H = J^T J` from the
first six columns only. T08 stores FAST-LIO order
`x_F=[t_x,t_y,t_z,r_x,r_y,r_z]`; DCReg uses
`x_D=[r_x,r_y,r_z,t_x,t_y,t_z]`. Apply the explicit permutation
`P=[[0,I_3],[I_3,0]]` and set `H_D=P H_F P^T`. Keep the recorded basis: FAST-LIO
translation columns are world-frame and rotation columns are IMU-tangent.
The scalar subspace spectra are invariant to an orthonormal re-expression
within either 3D block; do not attach physical-axis labels to eigenvalue index
`i`. The T08 `N*0.001` normalization is a common positive scalar and does not
change these condition ratios; compute the comparator from raw `H_F` to avoid
mixing its units with the scaled minimum-eigenvalue baseline. Split:

```text
H = [ H_RR  H_Rt ]
    [ H_tR  H_tt ]

S_R = H_RR - H_Rt * pinv(H_tt, rcond=1e-12) * H_tR
S_t = H_tt - H_tR * pinv(H_RR, rcond=1e-12) * H_Rt
```

The DCReg main paper gives the Schur-complement equations in Section 4.2 and
notes Moore-Penrose generalizations in Section 4.4. This implementation uses
that pseudoinverse extension for rank-deficient blocks; the relative rank
tolerance `1e-12` is our explicit adaptation setting, not a value reported by
the paper or its supplement.
The comparator requires at least six accepted correspondences, matching T08's
existing exporter; `N<6` is `UNAVAILABLE` with reason
`INSUFFICIENT_CORRESPONDENCES`, not a healthy/degenerate score.
Build and evaluate the Hessian/subspaces in float64. Symmetrize each Schur
result as `(S+S^T)/2` before `eigh`. For each subspace, let
`scale=max(abs(eigenvalues))` and `tol=1e-10*scale`; if any eigenvalue is
less than `-tol`, mark the scan `UNAVAILABLE`. Clamp only remaining negative
eigenvalues in `[-tol,0)` to zero. If the largest eigenvalue is zero, all
three direction ratios in that subspace are infinite. Otherwise compute the
three ratios `kappa_i=lambda_max/lambda_i` in ascending-eigenvalue order;
treat `lambda_i <= 1e-12*lambda_max` as infinite. Flag direction `i` when
`kappa_i > 10`, the strict comparison in DCReg Equation 21. Thus equality at
10 is not flagged.

Export both subspace spectra, all six ratios/flags, accepted count and the
scan-level state. `HEALTHY` means no direction is flagged; otherwise the state
is `DEGENERATE`. Define the scalar health score for threshold-free analysis as
`DCREG_HEALTH_SCORE = 1 / max(all six kappa_i)`; higher is healthier, and it
is zero if any ratio is infinite. The categorical state is computed from the
direction flags, not a rounded comparison of the scalar score. A non-finite
Hessian or materially negative subspace spectrum is `UNAVAILABLE` with
`INDICATOR_NUMERIC_FAILURE` and a detail field, never healthy.

Never serialize mathematical infinity as the text `inf`/`Infinity` or a JSON
non-finite number. Store a blank CSV / `null` JSON ratio and a matching
`ratio_unbounded=true` flag; the scan remains `DEGENERATE` and its health score
is `0`. A numerically invalid scan uses the contract's unavailable reason and
blank score/ratios instead.

### Point-LIO replication extension (accepted R2 amendment D050)

The complete method and data contract is the accepted
[Point-LIO amendment](POINTLIO_REPLICATION_AMENDMENT_20260929.md), independently
reviewed PASS on 29 September 2026. Point-LIO uses its own accepted map
correspondences and point-time updates; its rows are not shared with FAST-LIO.
The adapter captures the first six native measurement-Jacobian columns,
transports each group's rotation columns using its exact pre-update pose,
and pools those rows in one common frame basis. For `L=1,3,5 m`, use the
amendment's fixed `N_frame × 0.001` normalization; `lambda_min(G_3m)` is the
primary Point-LIO score. This is a measurement-geometry adaptation, not
Point-LIO's posterior information and not a reproduction of the full DCReg
system. Point-LIO's own pose stream receives the unchanged R2 recovery labels;
its global `G_3m` threshold is selected separately under the development rule
in [METRICS.md](METRICS.md). The FAST-LIO threshold and primary sample-size
plan do not change.

Protocol acceptance is not implementation acceptance. Analytic contract
fixtures and the read-only sidecar must pass before the retained seed-14
on/off feasibility replay; that replay does not fit a threshold. The complete
32-pair Point-LIO development batch follows only after seed-14 acceptance.
No held-out work is allowed until overall R3 and the separate replication
freeze pass.

### Adaptation boundary

This FAST-LIO stream is the **DCReg detector module adapted to FAST-LIO's
accepted correspondences**, not the complete DCReg registration solver, not
its PCG preconditioner, and not a reproduction of its whole SLAM experiment.
The shared correspondences control for front-end differences; the Hessian is
exported from a read-only side path and must not alter FAST-LIO pose updates.
The separate Point-LIO adaptation is governed by D050 and does not claim
shared correspondences between backends.
The DCReg paper's rotation/translation subspace formulation is retained; do
not compute condition numbers of the coupled six-dimensional matrix as a
substitute. Record the exact row/column permutation and verify basis handling
with analytic fixtures.

If FAST-LIO's backend cannot expose the accepted rows/Hessian at the same
registration stage without changing outputs, do not approximate DCReg using
raw scan normals. Either document a separate standalone registration ablation
or return to R2 with the failed parity evidence.

## Common time and truth boundary

The two FAST-LIO indicators are timestamped at that backend's scan-to-map
measurement update after accepted correspondences are known. Point-LIO uses
one separately named frame-pooled row at its actual `lidar_end_time`, with an
explicit nominal timestamp only for unavailable frames, as defined in D050.
Each backend may use only its LiDAR/IMU state and current correspondence data.
Neither may read the reference,
scene-layout annotations, future scans, evaluation CSV, or recovery labels.
For each method, preserve raw continuous output, categorical decision,
validity and unavailable reason. At an evaluation decision tick, use the latest
record (valid or invalid) at or before that tick, only if it is no more than
0.2 s old and belongs to the same estimator segment. If that latest record is
invalid, the decision is `UNAVAILABLE`; do not skip it to reuse an older valid
record. Debounced confirmation is timestamped at the third decision tick, and
the three source diagnostic timestamps are retained separately. This agrees
with the event-level association and barrier rule in [METRICS.md](METRICS.md).

## Expected validation before T13 completion

- Analytic Hessians: isotropic full-rank geometry, one weak translation axis,
  one weak rotation axis, and coupled rotation/translation where Schur
  conditioning detects a weakness hidden by the diagonal block.
- DCReg fixtures: condition threshold equality (`kappa == 10` is not flagged),
  above-threshold mask, first-six-column block permutation, invariance of the
  scalar score to orthonormal basis changes, and singular/non-PSD handling.
- FAST-LIO integration: exact accepted-correspondence count/timestamp parity;
  exported matrix reproduces the current T08 eigenvalues; exporter on/off
  pose streams remain byte-identical.
- Truth isolation: the estimator/indicator process opens no reference or
  evaluation path; changing a reference file alone cannot change either
  indicator output.
- Availability: fewer than six accepted correspondences, non-finite Hessians
  and materially non-PSD Schur spectra remain unavailable, never replaced by
  zero or a healthy state; rank-deficient PSD subspaces instead produce
  explicitly unbounded ratios and a degenerate decision.

No threshold was selected from the v3 pilot. The FAST-LIO numeric threshold
selected on the T14 development set is not yet frozen by R3; no Point-LIO
threshold or health output exists. All current simulation results remain
development evidence.
