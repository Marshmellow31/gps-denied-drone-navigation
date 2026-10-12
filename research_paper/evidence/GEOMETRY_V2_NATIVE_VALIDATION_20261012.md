# Geometry-v2 native development validation

**Status: PASS for the predeclared bounded development checks.** Final geometry/results remain ungenerated. This report is implementation evidence for independent R3 review, not a scientific recovery result or a self-issued gate.

The [R2 review](../reviews/R2_GEOMETRY_AMENDMENT_20261012.md) required a long/narrow pair on both backends, a long/wide changed control on both, paired sensor audits and at least one Point-LIO changed-control sidecar-on/off replay. All seven predeclared native runs completed in fresh directories under `/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/geometry_v2_native_validation_20261012`.

Fixed dimensions were L=16.5 m, room half-width=6 m, corridor half-width=1.4 or 2.75 m. These separate development fixtures use sensor seed14, the original formal route, 60 s horizon, original noise/bias model, and bounded-spacing controls. They are excluded from historical threshold selection and final counts. Both analytic references and serialized IMU streams match within each corridor/control pair; each bag contains 600 scans and 12,021 IMU messages, only on the two sensor topics.

FAST-LIO completed the long/narrow corridor/control and long/wide control with full input/pose completion checks and own-pose offline evaluation. Its accepted binary remains `4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792`; the operating point is unchanged. Receipts, process logs, run manifests, output hashes and any retry accounting are retained by the existing supervised lifecycle.

Point-LIO completed the corresponding three sidecar-on slots plus the long/narrow control sidecar-off slot. Each on slot has 600 input-header records, 600 sidecar frames, 600 indicator records and 597 poses. The exporter validates common-basis row reconstruction, frame coverage and reset/unavailable association. Own-pose offline evaluations completed for the three on slots. Native binary/config/source/glog and Python producer identities match the accepted anchor. No cutoff was fitted or changed.

The changed long/narrow control has byte-identical on/off `poses.csv`, SHA-256 `16197c207327bd44b178b093b2651baab934feb058c08c03c28a1623f47a6d0e`. This demonstrates non-perturbation on that fixture, not all future native executions. Startup-unavailable diagnostics remain explicit; no unavailable rows are converted to zero information or healthy state.

The [compact summary](geometry_v2_native_validation_20261012.json) retains native manifest/evaluation hashes, pair audits, runtime identities and generator/runner identities. Detailed native ledgers remain external; a Git clone alone cannot reproduce their verification. Development bags were generated while the working tree was uncommitted; their recorded Git revision identifies the prior checkpoint, and explicit generator/simulator/route/producer hashes identify the actual code. Fixed-fixture geometry does not draw from the manifest's reserved geometry RNG namespace; its nested `layout_seed=null` records this.

The [244-test readiness log](geometry_v2_readiness_tests_20261012.log) records 243 passes and one optional SciPy skip. The compiled native sidecar reset fixture ran with `POINTLIO_SOURCE_ROOT` and the research environment's Eigen headers. Geometry profile, fresh seed reservations, structural equivalence for short controls, old-freeze rejection, cache/receipt and analysis regression checks passed.

Required next gate: independent R3 review of actual native evidence, source contracts, no-data plan and complete current inventory. Neither the original R3 freeze nor this development report authorizes revised final runs.
