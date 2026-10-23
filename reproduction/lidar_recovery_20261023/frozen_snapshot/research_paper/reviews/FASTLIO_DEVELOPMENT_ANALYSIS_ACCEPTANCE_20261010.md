# Independent FAST-LIO corrected development analysis acceptance

Date: 10 October 2026. **Decision: PASS for the corrected T16 development analysis v2.** This accepts the raw-score candidate correction and its actual regenerated outputs. It does not pass overall R3, create an implementation freeze or authorize held-out access.

The accepted folder is
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/PRIMARY_DEVELOPMENT_RECOVERY_20261009/t16_analysis_20261010_v2/`.
The reviewer performed read-only native/input/adapter audits and temporary offline calculations in the frozen Python 3.12.14 / NumPy 2.5.3 environment. No native estimator or held-out geometry, input, screen or result was used.

## Verification and findings

The reviewer freshly reran the complete primary lineage auditor. Its result equals the previously accepted complete-audit JSON exactly: 64 completed primary slots and four declared repeats, with 69 native attempts including the preserved seed-37 interrupted attempt. All native/adapter/input hashes and lineage checks pass. The corrected analysis binds exactly the 32 corridor and 32 control primary runs for seeds 14–45; all 64 analysis provenance records, actual manifest hashes and key stream hashes were checked. Each actual run was reloaded through the validated own-pose/reference contract. Repeats, controls and failed technical attempts add no threshold-fitting event.

The candidate defect and bounded source repair are described in the [Point-LIO review](POINTLIO_DEVELOPMENT_ACCEPTANCE_20261010.md). FAST-LIO had the same omission of 32 valid terminal diagnostic scores from its original decision-associated candidate population. The corrected table contains **19,104 unique finite valid raw corridor scores plus `NO_ALARMS`**, as METRICS requires. Alarm evaluation still uses the frozen decision grid.

An independent candidate-by-event state calculation compared **every one of the 19,105 official candidate rows**, checking sorted score identity, false-healthy and detection numerators/denominators, rates and feasibility flags. All agree. The optimum remains **166.16366016039856**, with **1/31** conditional initial false-healthy events and **13/32** post-onset recovery detections. The independent raw-score calculation and higher-threshold tie rule select the same optimum.

Both full method-summary objects agree with fresh calculations over the actual 64 runs. All six corrected CSV hashes read back. Compared with the earlier accepted recovery analysis, only candidate population/count metadata, the candidate CSV and analysis/test source identities change. The other five CSVs, all labels, method metrics, three-second sensitivity, threshold-free curves, input/failure provenance and sample-size calculations remain identical. All 32 corridor labels remain recovered, with one relapse; fixed DCReg retains 30/32 detections, 0/31 initial false-healthy events and 1/1 post-relapse false-healthy events. The paired interior sample SD remains **0.2503454775041967 m**, and the frozen-rule final requirement remains **48 geometry pairs**.

The manifest declares `role=development_only` and `heldout_inputs_opened=false`; actual reviewed inputs are the declared development seeds. These are development-fitting descriptions, not independent final performance estimates. The earlier fresh-versus-historical differences and interrupted-run runtime limitation remain as disclosed in the [primary recovery review](PRIMARY_RECOVERY_ACCEPTANCE_20261009.md).

## Accepted identities

| Artifact | SHA-256 |
| --- | --- |
| Corrected `t16_analysis_manifest.json` | `1678e1c8b62b3ceeabf4e9f4e63593832cf8c94f7793e7b933647e8569c082f7` |
| Corrected `t16_threshold_candidates.csv` | `7ebbe1e5858ad49c4b175bd406dfa25921a0b3a957ef3a6d9aa8510e9d2d89c2` |
| Shared analysis source | `f34fa9479e95bfa78823e3be8f70d63445631d09f3d46fe59a75331ae2975077` |
| Analysis test source | `b084cd32cc9a4d1592ea26e94584ffcce305090350ec0030cfce9f475cde42ca` |
| Preserved earlier recovery analysis manifest | `6efd16c0bb2eeacd4c9f61d2e6c3f32e4227ba7ff80debd6416d45b30677f1f3` |

The corrected artifacts supersede the earlier candidate enumeration; the earlier files remain preserved. The manifest's generic command remains a historical default-path example, not the exact invocation for this restoration folder. Freeze/reproduction instructions must use the actual recovery adapter/input/audit paths documented in the primary recovery review and the v2 output folder above. Complete final interfaces and overall R3 remain outstanding.
