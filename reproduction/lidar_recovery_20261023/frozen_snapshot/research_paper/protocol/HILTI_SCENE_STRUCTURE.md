# Prespecified LiDAR-only structure check for Hilti Exp18

Frozen before running the structural calculation on 24 September 2026. This is a **scene-selection diagnostic**, not a FAST-LIO health indicator, a reference-based accuracy metric, or a proof of 6-DoF observability. It may use only raw `/hesai/pandar` point clouds and their header times. It must not load poses, reference, IMU, estimator logs, or eventual indicator/error streams.

## Question and fixed windows

The range-only audit found a near-to-far scene change around 31.6–33.1 s. Does the direction of visible local surface normals also become more diverse? Inspect clouds nearest relative times `26, 27, 28, 29, 30` s (before) and `35, 36, 37, 38, 39` s (after), each within 0.06 s of target. Keep all ten results, including failures. These windows were selected outside the observed range-change interval, before viewing trajectory errors or structural scores.

For each cloud, use finite XYZ points with range 0.3–20 m. Keep a deterministic maximum of 8,000 points by index-even subsampling. For each sampled point, find its 20 nearest sampled neighbors in the same scan with a Euclidean KD-tree. A local neighborhood is usable only if its farthest neighbor is at most 1.5 m and its covariance eigenvalues obey `lambda_min / trace <= 0.02` (locally planar) and `lambda_mid / trace >= 0.03` (not line-like). The eigenvector for `lambda_min` is its unit surface normal; its sign is irrelevant.

Compute the normalized translation-normal matrix `G = (1/N) sum(n n^T)` from usable normals. Report `N`, usable-normal fraction, the three eigenvalues in ascending order, and `lambda_min(G)` for every cloud. The smallest eigenvalue is a scale-free proxy for the weakest translation direction of point-to-plane registration. Also report cloud range p50/p90 to expose range-dependent sampling. Repeat at maximum ranges 10 m and 20 m as a sensitivity check; a positive change that exists only because the far-range cutoff changes cannot establish robust structural improvement.

This proxy is motivated by the point-to-plane registration information analysis in [X-ICP, Sections III and V-A](https://arxiv.org/html/2211.16335v3). It is **not** X-ICP's full scan-to-map Hessian: it has no correspondences, map, residual weights, IMU prior, rotational block, or backend point selection. It cannot by itself label a full 6-DoF weak-to-rich recovery event.

## Decision rule

Report the per-cloud values and before/after medians without treating ten nearby scans as independent trials. If the after-window minimum eigenvalue is not consistently higher across both range caps, reject the weak-to-rich interpretation. If it is consistently higher, retain only a **candidate** scene event and audit the rotational/correspondence geometry separately before freezing a recovery event. No threshold is to be tuned against FAST-LIO errors. A visually striking range change alone is insufficient.

## Prespecified second stage (before its calculation)

The first-stage translation-normal medians increased under both range caps but individual scans overlapped. Before computing any rotational result, extend the *same ten selected clouds and normals* with a dimensionless six-column point-to-plane Jacobian `J = [(p cross n)/L, n]`. Evaluate `L = 1, 3, 5 m` (fixed sensitivity scales, not fitted) and report the smallest eigenvalue of `J^T J / N` for every scan under both 10 m and 20 m range caps. This includes rotational and translation directions but still lacks scan-to-map correspondences, robust weights and priors; it is a structural proxy, not the actual backend Hessian.

Retain the scene as a candidate only if the after-window median smallest eigenvalue exceeds the before-window median for **all six** cap/scale combinations. Do not characterize the scene as a fully validated 6-DoF recovery event from this proxy alone. If the result passes, a separate, outcome-blind geometric annotation can freeze the event interval as a *scene-defined candidate* for development T07; if it fails, reject Exp18 for the transition pilot rather than move the boundary.
