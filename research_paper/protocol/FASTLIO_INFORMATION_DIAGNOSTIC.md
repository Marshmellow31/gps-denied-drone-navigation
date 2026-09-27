# T08 source audit: FAST-LIO measurement-only registration information

26 September 2026. **T08 software acceptance complete.** See the [latest audit](../evidence/T08_FINAL_PATCH_AUDIT.md): after shutdown clock draining, 547 byte-identical on/off poses, 550 groups, and one final input scan excluded for incomplete IMU coverage. The earlier interrupted-run notes below are historical. This is a conventional point-to-plane scan-to-map diagnostic, not X-ICP, SuperLoc, FAST-LIO's posterior uncertainty, or a validated recovery indicator. It can use only backend information available when the current scan is processed. No reference trajectory, event annotation or evaluated error enters the computation.

## Pinned source-to-output derivation

Source: official FAST-LIO revision `7cc4175de6f8ba2edf34bab02a42195b141027e9`, `src/laserMapping.cpp`, function `h_share_model` (approximately lines 638–752), and `include/IKFoM_toolkit/esekfom/esekfom.hpp`, `update_iterated_dyn_share_modified` (approximately lines 1619–1835). The local build differs only by the [C++17 compatibility patch](../experiments/patches/fast_lio_pcl17.patch).

The backend downsamples an undistorted LiDAR scan, finds five nearest map points for each candidate, fits a plane, and accepts a correspondence only after its distance/planarity/residual tests. For each **accepted** point it stores the LiDAR-frame point `p_L`, world-frame plane normal `n_W`, and signed point-to-plane residual. With the estimated IMU rotation `R_WI` and fixed extrinsics `R_IL,t_IL`, the first six measurement Jacobian columns are, in the source's order:

```text
p_I = R_IL p_L + t_IL
n_I = R_WI^T n_W
h_i = [n_W^T, (p_I × n_I)^T]
```

The source also has six extrinsic-state columns if extrinsic estimation is enabled; they are **excluded** here so the diagnostic explicitly asks about current translation/rotation measurement constraints. The EKF additionally uses the IMU prediction/prior and a point covariance constant `LASER_POINT_COV = 0.001`; neither the posterior precision nor an independent truth estimate is being exported. The geometric diagnostic uses the same accepted correspondences and an unweighted residual variance equal to that source constant. Do not substitute all points in the raw scan or a fitted reference alignment.

Translation perturbation is measured in metres and rotation perturbation in radians, so a 6×6 eigenvalue has no unique meaning without a rotation lever scale. For a declared `L` metres, define `h_i(L) = [n_W^T, ((p_I × n_I)/L)^T]` and `G_L = (sum_i h_i(L)^T h_i(L))/(N × 0.001)`. This defines both perturbation blocks in metre-equivalent coordinates. Retain raw accepted count `N`, all six eigenvalues, and at least `L=1,3,5 m` as *sensitivity outputs*, not three optimized thresholds. Scaling by `N` avoids making a dense scan appear healthier solely because it contains more accepted points; accepted-point availability remains a separate output. Report the unnormalized count and optionally the unnormalized information as an audit. No scalar threshold or recovered label is chosen here.

The smallest eigenvalue is a measurement-only weakest-direction score: larger means the accepted scan-to-map residuals constrain every scaled direction more strongly. It does **not** say the EKF estimate is accurate, prior drift is corrected, or all six directions are physically observable under a persistent sequence. In particular, world translation and IMU-tangent rotation coordinates are different bases; their 6×6 score is invariant to a common orthonormal frame re-expression but its eigenvector must be interpreted with the recorded basis and `L`.

## Verified and still required

- The [independent Python mirror](../experiments/src/fastlio_information.py) follows the pinned backend's first six Jacobian columns; its four analytic fixtures remain passed. The complete experiment suite currently reports 40 passed and one SciPy-dependent skip (41 executed). These fixtures validate math and schema, not the scientific utility of the indicator.
- The [versioned backend patch](../experiments/patches/fast_lio_health_diagnostic.patch) and the final [T08 audit](../evidence/T08_FINAL_PATCH_AUDIT.md) document the compiled pinned implementation, shutdown clock drain, all delivered scans, unavailable reasons, on/off pose parity and hashes. The 55 s corrected on/off runs yielded 547 byte-identical poses, 550 audited groups (547 valid and three startup-unavailable), and one final delivered scan excluded for incomplete IMU coverage.
- T08 is DONE as a software/instrumentation task. Runtime and RSS observations are from one pair and are not a total-process resource benchmark. The exported minimum eigenvalue has no calibrated recovery threshold and is not evidence that an estimate is accurate. T09/R1 must relate it to valid reference-based local motion without assigning a label from this diagnostic.
- If a standalone scan-normal score is used instead, it must be named separately: the [Hilti scene proxy](HILTI_SCENE_STRUCTURE.md) has no map correspondences or EKF residual selection, and must not be represented as this backend signal.

The motivation for a point-to-plane information/eigenstructure baseline comes from [X-ICP, Sections III and V-A](https://arxiv.org/html/2211.16335v3); this document's specific `G_L` is a declared FAST-LIO diagnostic, **not** a reproduction of X-ICP's published method.
