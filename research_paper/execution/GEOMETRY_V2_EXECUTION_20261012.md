# Revised geometry evaluation — 12 October 2026

This dated ledger supersedes the original geometry-screen workflow for the revised cohort. Original R2 frozen files, original generator, failed screen, original final plan and original R3 review/freeze remain historical evidence. The old R3 PASS cannot authorize revised source files.

| Step | Current state | Evidence |
| --- | --- | --- |
| R2 geometry amendment | PASS for bounded protocol | [Independent review](../reviews/R2_GEOMETRY_AMENDMENT_20261012.md) |
| Versioned integration | Implemented; regression checks passed | [Generator](../experiments/src/heldout_simulation_v2.py), [split](../data/SPLITS_GEOMETRY_V2_20261012.csv), [no-data plan](../evidence/FINAL_HELDOUT_PLAN_GEOMETRY_V2_20261012.json) |
| Development native validation | PASS: seven predeclared runs, both input-pair audits, on/off identity | [Native evidence](../evidence/GEOMETRY_V2_NATIVE_VALIDATION_20261012.md) |
| Renewed R3/freeze | PASS: 197 entries; 243 tests passed, one optional skip | [Independent review](../reviews/R3_GEOMETRY_V2_IMPLEMENTATION_20261012.md), [new freeze](../protocol/IMPLEMENTATION_FREEZE_GEOMETRY_V2_20261012.md) |
| Fresh final geometry screen | PASS: 48 selected from 64 checked, 12 per group | [Screen snapshot](../evidence/final_geometry_screen_v2_20261012.json) |
| Final FAST-LIO native cohort | COMPLETED: 48 pairs, 96 formal runs | [Batch export](../evidence/final_geometry_v2_results_20261012/fastlio_batch.json) |
| Final Point-LIO native cohort | COMPLETED: 48 pairs, 96 formal runs; zero native replay failures | [Batch export](../evidence/final_geometry_v2_results_20261012/pointlio_batch.json) |
| Final analysis compatibility | Supplemental independent PASS; original 197-entry freeze unchanged | [Review](../reviews/R3_GEOMETRY_V2_ANALYSIS_COMPATIBILITY_20261012.md), [adapter](../experiments/src/final_dataset_analysis_geometry_v2_compat.py) |
| Final analyses | CONFIRMATORY_COMPLETE for both backends; all 48 pairs usable | [Full results](../evidence/final_geometry_v2_results_20261012/RESULTS_REPORT.md), [export audit](../evidence/final_geometry_v2_results_20261012/export_audit.json) |
| Independent final result-accounting audit | Scoped PASS: dataset and reported accounting reconcile; novelty not established | [Final audit](../reviews/FINAL_GEOMETRY_V2_RESULT_AUDIT_20261012.md) |

The amendment keeps geometry eligibility, outcomes, noise/motion profiles and development-selected backend cutoffs fixed. Baffles have bounded 2 m spacing; larger pools retain rejected candidates instead of relaxing eligibility. Original IDs 100–179 are excluded. The earlier failed screen informed the revised design; fresh instances must not be described as a wholly unadapted test design.

The development native fixtures are explicitly fixed at L=16.5 m, room half-width=6 m, corridor half-width=1.4 or 2.75 m, with sensor seed14. They are separate instrumentation/feasibility evidence, not additions to the historical development cohort or threshold calibration. Their metadata's geometry RNG reservation is unused for these fixed fixtures; `scene_geometry.layout_seed=null` records the absence of a random layout draw. The final generator uses the preserved uniform dimension draws and geometry RNG namespace with fresh test IDs.

Native evidence belongs under the external research workspace's `geometry_v2_native_validation_20261012` folder. All failed attempts remain there. Sidecar on/off pose identity is checked on the changed long/narrow control. Acceptance requires full input/diagnostic/pose coverage and valid own-pose offline evaluation, not favorable accuracy or recovery outcomes.

The historical screening digest discrepancy remains unresolved. The [reconciliation receipt](../evidence/screening_provenance_reconciliation_20261012.json) binds the saved observed version without claiming to authenticate the missing earlier bytes.

The accepted fresh screen contains 12 short/narrow candidates checked, 19 short/wide, 14 long/narrow and 19 long/wide. Its bytes hash to `f088c5cbe539da1624b638148662362ecab6a74a1de861094664df097a99b886`. All 48 selections precede estimator execution. No rejected seed is replaced using accuracy or indicator outcomes.

The native batch completed in `final_heldout_geometry_v2_20261012` under the external research workspace. FAST-LIO retained its pair ledger and every attempt manifest before Point-LIO reused the identical sensor-bag hashes. A sequential driver records its own source hash, commands, child process identity and exit codes in `pipeline_state.json`; it stops for attention on a failed stage. The frozen analyses and independent result-accounting audit subsequently passed.

FAST-LIO completed all 96 native runs without a native failure. The initial Point-LIO preflight stopped before replay because its scratch-root directory was absent; the entire initial output directory and logs are retained in `pointlio_preflight_failure_20261012`. Creating the directory and starting a fresh output root required no source or scientific-policy change. The original analysis then stopped before reading final poses/reference/labels because its expected FAST execution identity included additional shared Point threshold metadata absent from the primary recorder. The independently accepted adapter changes only this expected metadata dictionary; all original numerical and provenance checks remain. Its review checked all 96 identities without opening outcomes. The original failed driver state remains intact; `analysis_resume_state.json` records the subsequent sequential analysis commands and their exit codes.

Supplemental checks: five focused adapter tests passed. The full current suite ran 249 tests: 248 passed, one optional SciPy skip, with the compiled native reset fixture enabled. [Regression log](../evidence/geometry_v2_analysis_compat_regression_20261012.log).

Final observation: all 192 native runs completed on matching sensor inputs. FAST-LIO recovered in 46/48 corridors; Point-LIO in 32/48. Initial conditional false-healthy/detection counts are FAST scalar 1/46 and 14/46, FAST fixed DCReg 4/46 and 38/46, Point scalar 4/47 and 27/32, Point fixed DCReg 16/47 and 25/32. All methods have 9600/9600 primary horizon ticks available. These denominators are explained in the result report; native completion alone does not establish reliability. Both backends have one relapse. The frozen paired geometry bootstrap intervals for corridor-minus-control interior translation error are FAST +0.194 m [0.086, 0.311] and Point +0.149 m [0.068, 0.230].

The result report and research README now separate completed evaluation from unfinished publication novelty/manuscript work. Four final figures show operating points, group-specific events, every corridor event and paired geometry uncertainty; existing historical illustrations remain clearly labelled. Original frozen status files retain their dated checkpoint text and are supplemented by this ledger.
