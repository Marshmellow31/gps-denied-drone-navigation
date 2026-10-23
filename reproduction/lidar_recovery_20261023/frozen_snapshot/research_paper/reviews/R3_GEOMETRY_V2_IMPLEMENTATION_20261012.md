**Gate:** PASS

# Independent R3 geometry-v2 implementation review — 12 October 2026

Reviewer: separate sequential review agent, independent of integration and native execution. This is acceptance of the bounded revised implementation under the [R2 amendment](R2_GEOMETRY_AMENDMENT_20261012.md), not a scientific result, novelty verdict or flight-safety claim. Original R2/R3 files and failed screening evidence remain preserved. The new freeze is required for revised execution.

## Independent verification

Read AGENTS.md, the R3 execution-plan requirements, amendment, spacing implementation, revised generator/split, source changes since `87aab06466fe5492cc78d711e822bc1a95753082`, both final runners, input validators, both final analyses, no-data plan, inventory, native report and actual external evidence. Reviewed the unchanged mathematical/recovery contracts through the preserved R2 inventory and regression suite.

Independently reran all 244 tests in Python 3.12.14 / NumPy 2.5.3: **243 passed, one optional SciPy scene-structure test skipped** (9.372 s). The compiled C++ sidecar reset fixture ran using the actual patched Point-LIO source and environment Eigen headers. Independent test output was retained at `/tmp/r3_geometry_independent_tests_20261012.log`; the separately retained [readiness log](../evidence/geometry_v2_readiness_tests_20261012.log) gives the same test count and skip. `git diff --check` passed.

Independently recomputed the complete 197-entry review inventory and all **53 original R2 frozen file hashes**. Verified the actual FAST-LIO binary/configuration/environment/source-patch identity with `_check_backend`, Point-LIO binary/configuration/patched native source with `validate_native`, and actual glog/gflags runtime library hashes. No source/binary/threshold change was needed for native validation.

One bounded defect was found: the saved revised no-data plan had stale workflow and Point-LIO analysis hashes after integration. Regenerated that plan and review-input inventory without calling any seed-specific geometry function. Verified exact equality with `workflow.build_plan(FAST_ANALYSIS, SPLITS_PATH)` afterward. This was an identity refresh, not a protocol or geometry change.

## Actual native evidence

Audited `/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/geometry_v2_native_validation_20261012`, not only the [compact summary](../evidence/geometry_v2_native_validation_20261012.json). The checked-in summary equals the external summary. Rehashed all four input manifests, all bag/reference/metadata bytes and generator/route/simulator identities; verified explicit development dimensions, seed14 and truth isolation. Independently reran both paired bag audits: only sensor topics, 600 scans and 12,021 IMU messages per bag, byte-identical serialized IMU within each pair. Paired reference files also have identical hashes.

| Prespecified native check | Independent evidence |
| --- | --- |
| FAST-LIO long/narrow corridor and control; long/wide control | Three completed slots; every recorded output hash matches. Recomputed full-stream completion: each has 600 health groups, 600 DCReg rows, 597 valid poses and 1,194 own-pose evaluation rows; no reference gaps, invalid poses or reset records. Final pose time is 1059999722221 ns. |
| Point-LIO same three inputs with sidecar on | Three completed slots; every recorded output hash matches. Each has 600 input-header records, 600 covered sidecar frames, 600 indicator rows, 597 poses and 1,194 own-pose evaluation rows. Actual evaluation hashes match the compact summary. Final source frame is600 at1059999722221 ns. |
| Point-LIO long/narrow control with sidecar off | Completed fourth Point slot; native/output identities verified. The597-pose file is byte-identical to its on counterpart, SHA-256 `16197c207327bd44b178b093b2651baab934feb058c08c03c28a1623f47a6d0e`. |

The exporter enforces common-basis row reconstruction, frame coverage and reset association. Startup unavailable states remain explicit. Native reset behavior is supported by the compiled fixture; these new replay poses contain no reset event and are not evidence of an actual replay reset. On/off equality establishes non-perturbation on this one fixture. Native output/evaluation completion is feasibility evidence regardless of error magnitude or recovery success. No threshold fitting occurred.

## Revised final contracts and leakage boundary

Verified the actual final generator calls the accepted `build_candidate`: `max(4, ceil(length/2)-1)` baffles and longitudinal spacing no greater than2m. Corridors and room surfaces use the preserved original implementation; short-stratum controls are structurally identical. Uniform dimensions, geometry RNG namespace, sensor/noise model, route and60s duration remain unchanged. The unused legacy `build_straight_surfaces` helper inside the new module is not its generation path; acceptance concerns the tested `build_candidate` path.

The exact split reserves four disjoint80-ID pools:10000–10079,10100–10179,10200–10279,10300–10379. Original100–179 exposure is excluded and adaptation to the failed screen is disclosed. The no-data plan binds12 pairs per stratum, ascending first-eligible selection, unchanged geometry-only criteria and stop/return-to-R2 on any quota failure. Screening stops when each quota is met and retains all attempted decisions.

Both final runners and both analyses use `SPLITS_GEOMETRY_V2_20261012.csv`. Point's standalone input validator delegates to the primary revised generator/source identity verifier after validating the new gate. Both backends consume the same retained inputs; source hashes, split/plan, screen/review/freeze identities, actual bag hashes and execution identities bind inputs and cached attempts. Old freezes cannot authorize revised screening; the regression verifies rejection before touching fresh geometry. Old inputs/caches cannot satisfy the new source/gate identities.

Locked operating points remain FAST-LIO **166.16366016039856**, Point-LIO **123.80876977779258**, and unchanged DCReg policy. Own-backend trajectory labels, joint translation/rotation recovery, three non-overlapping1s windows,20s deadline, causal confirmation, unavailable/reset handling, failure retention, conditional denominators, relapse/non-recovery and stratified geometry-cluster uncertainty remain unchanged. Revised control geometry shifts the evaluation distribution; historical development performance must not be presented as calibration on this new design.

No fresh reserved ID was sampled by this reviewer. Tests use mocked sampling, range checks and explicit development dimensions. Reviewed no-data plan/native manifests assert no fresh final screen/input/replay; observed new evidence is development-only. This is a bounded evidence audit, not an exhaustive search of every disk for undisclosed data.

## Acceptance and limitations

**PASS:** proceed under the exact new freeze to one revised geometry screen, then192 formal native slots only if48 eligible pairs are obtained. Preserve every screen decision, technical attempt and output identity; no outcome tuning, pool borrowing or discretionary rescreening. Material source/method changes require renewed review/freeze.

The earlier screening digest discrepancy remains unresolved; the saved observed version is preserved and does not authenticate missing earlier bytes. Geometry coverage is an eligibility proxy, synthetic clocks/extrinsics and prescribed motion limit external validity, native raw evidence is external to Git, and the optional SciPy check was skipped. Final experimental conclusions and publication novelty remain unproven, particularly given documented OCE overlap.
