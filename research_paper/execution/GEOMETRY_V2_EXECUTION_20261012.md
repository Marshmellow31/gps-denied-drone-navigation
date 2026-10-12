# Revised geometry evaluation — 12 October 2026

This dated ledger supersedes the original geometry-screen workflow for the revised cohort. Original R2 frozen files, original generator, failed screen, original final plan and original R3 review/freeze remain historical evidence. The old R3 PASS cannot authorize revised source files.

| Step | Current state | Evidence |
| --- | --- | --- |
| R2 geometry amendment | PASS for bounded protocol | [Independent review](../reviews/R2_GEOMETRY_AMENDMENT_20261012.md) |
| Versioned integration | Implemented; regression checks passed | [Generator](../experiments/src/heldout_simulation_v2.py), [split](../data/SPLITS_GEOMETRY_V2_20261012.csv), [no-data plan](../evidence/FINAL_HELDOUT_PLAN_GEOMETRY_V2_20261012.json) |
| Development native validation | PASS: seven predeclared runs, both input-pair audits, on/off identity | [Native evidence](../evidence/GEOMETRY_V2_NATIVE_VALIDATION_20261012.md) |
| Renewed R3/freeze | PASS: 197 entries; 243 tests passed, one optional skip | [Independent review](../reviews/R3_GEOMETRY_V2_IMPLEMENTATION_20261012.md), [new freeze](../protocol/IMPLEMENTATION_FREEZE_GEOMETRY_V2_20261012.md) |
| Fresh final geometry screen | PASS: 48 selected from 64 checked, 12 per group | [Screen snapshot](../evidence/final_geometry_screen_v2_20261012.json) |
| Final native runs and analysis | Not executed | 48 pairs, two scenes and two backends: 192 formal slots |

The amendment keeps geometry eligibility, outcomes, noise/motion profiles and development-selected backend cutoffs fixed. Baffles have bounded 2 m spacing; larger pools retain rejected candidates instead of relaxing eligibility. Original IDs 100–179 are excluded. The earlier failed screen informed the revised design; fresh instances must not be described as a wholly unadapted test design.

The development native fixtures are explicitly fixed at L=16.5 m, room half-width=6 m, corridor half-width=1.4 or 2.75 m, with sensor seed14. They are separate instrumentation/feasibility evidence, not additions to the historical development cohort or threshold calibration. Their metadata's geometry RNG reservation is unused for these fixed fixtures; `scene_geometry.layout_seed=null` records the absence of a random layout draw. The final generator uses the preserved uniform dimension draws and geometry RNG namespace with fresh test IDs.

Native evidence belongs under the external research workspace's `geometry_v2_native_validation_20261012` folder. All failed attempts remain there. Sidecar on/off pose identity is checked on the changed long/narrow control. Acceptance requires full input/diagnostic/pose coverage and valid own-pose offline evaluation, not favorable accuracy or recovery outcomes.

The historical screening digest discrepancy remains unresolved. The [reconciliation receipt](../evidence/screening_provenance_reconciliation_20261012.json) binds the saved observed version without claiming to authenticate the missing earlier bytes.

The accepted fresh screen contains 12 short/narrow candidates checked, 19 short/wide, 14 long/narrow and 19 long/wide. Its bytes hash to `f088c5cbe539da1624b638148662362ecab6a74a1de861094664df097a99b886`. All 48 selections precede estimator execution. No rejected seed is replaced using accuracy or indicator outcomes.
