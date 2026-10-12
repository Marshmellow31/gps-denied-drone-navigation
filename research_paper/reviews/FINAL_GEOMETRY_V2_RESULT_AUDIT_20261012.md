**Gate:** PASS

# Independent final geometry-v2 result-accounting audit — 12 October 2026

**Scoped PASS: the complete planned controlled dataset and its reported accounting reconcile. Publication novelty is NOT established.** This review accepts evidence completeness, provenance reconciliation and bounded interpretation. It is not a new detector, estimator-superiority, real-world recovery or flight-safety acceptance. No source, threshold, geometry or native output was changed by this reviewer.

## Scope and independently verified provenance

Read the [final results report](../evidence/final_geometry_v2_results_20261012/RESULTS_REPORT.md), both exported analyses/batches, all192 compact native receipts, original failed driver state, resumed state, retained Point preflight batch and all CSV summaries. Compared every exported source copy with its actual external source bytes. Recomputed export/report/receipt/source-script hashes. Read every actual external native manifest and verified its recorded receipt hash, output-hash dictionary, scientific slot and accepted execution identity. The raw streams remain external; this audit did not repeat their full byte rehash or rerun either complete analysis, because the unchanged frozen analyses already perform output/source/input/stream checks and no accounting discrepancy warranted repetition.

The live original197-entry R3 freeze and supplemental compatibility inventory both pass. Every analysis/batch cites that exact gate and matching bound scientific source hashes. The FAST analysis compatibility receipt matches its separate accepted review/wrapper/original-analyzer hashes. FAST native identities match the primary gate exactly after the one separately accepted metadata adjustment; Point native identities match its accepted replication identity. Locked scalar cutoffs remain166.16366016039856 and123.80876977779258. Both analyses declare no final threshold fitting.

The scene screen contains64 attempted geometry candidates and selects48 distinct paired geometries,12 per fixed stratum, in the first-eligible order. The primary and replication batches contain the same48 keys and identical corridor/control bag hashes for every pair. Exactly192 unique native slots exist:48 geometries ×2 scenes ×2 backends. Every actual manifest is COMPLETED; no alternate native attempt/repeat was substituted. Both analyses are `CONFIRMATORY_COMPLETE`, with48/48 completed pairs,96 loaded scenes and no failed/unusable pair.

Two retained workflow failures are not hidden native samples. The original FAST analyzer's recorded traceback rejects identity before final pose/reference/label loading; its repair is the independently accepted metadata-only compatibility adapter. The Point preflight failed batch contains all48 scheduled pairs but zero scene attempts and zero completed pairs; its retained failure tree contains no native run manifest. The resumed driver finishes both analyses. These records remain in the compact export and external directories.

## Independent numerical reconciliation

Recounted all48 own-backend truth labels and all48 per-method event rows, checked unique selected seeds, and matched every diagnostic row's truth status/onset/relapse to the corresponding label. All48 corridors are truth-eligible. FAST has46 recoveries,2 non-recoveries and1 relapse; Point has32 recoveries,16 non-recoveries and1 relapse. Each backend's two diagnostics share its own labels, rather than transferring FAST labels to Point.

| Backend / fixed diagnostic | Initial false-healthy | Recovery detections | Detected-only median delay |
| --- | --- | --- | --- |
| FAST scalar | 1/46 conditional;1/48 unconditional | 14/46 | 0.8502777795s |
| FAST DCReg adaptation | 4/46 conditional;4/48 unconditional | 38/46 | 6.8002777795s |
| Point scalar | 4/47 conditional;4/48 unconditional | 27/32 | 3.40027778s |
| Point DCReg adaptation | 16/47 conditional;16/48 unconditional | 25/32 | 3.000277779s |

Independently recomputed event numerators and median delays from event rows. Missed detection rows have null delay; no synthetic zero/infinite value was inserted. Every method has9600/9600 available/planned20s horizon ticks. Independently reconstructed initial interval tick occupancy from label exit/onset times and the frozen10Hz half-open tick rule:46 FAST and47 Point intervals contain a decision tick. Thus full horizon availability and smaller conditional initial denominators are consistent; the unconditional denominator remains48 continuous initial intervals. The report correctly distinguishes these quantities and detection sensitivity conditional on truth recovery.

Verified every scalar cell in the4-row method CSV, all16 group summary rows and all192 diagnostic event CSV rows against the JSON exports. Those192 rows represent four diagnostic analyses of48 shared geometries, not192 independent experimental units. Independently recalculated Wilson intervals using the specified z=1.96 formula; they agree with the exports. In particular the scalar false-healthy upper bounds exceed10%, so neither scalar point estimate establishes a population reliability guarantee below10%. Relapse endpoints have only one event per backend and cannot support robust reliability conclusions.

## Geometry dependence and uncertainty interpretation

Independently counted recovery by stratum: FAST12/12 short-narrow,10/12 short-wide,12/12 long-narrow and12/12 long-wide; Point12/12,4/12,12/12 and4/12 respectively. The report's Point width dependence (24/24 narrow versus8/24 wide) follows these labels. The Point scalar's four initial false-healthy events occur in long-narrow; FAST scalar detects just1/12 long-wide recoveries. These are descriptive interactions with12 sampled eligible geometries per group; they are not a formal universal width law or causal interaction test.

The paired interior estimates equal the arithmetic mean of the four fixed-stratum means: FAST0.1938590334m and Point0.1485828066m, corridor minus control. Their frozen geometry-cluster intervals are respectively[0.0862811847,0.3114604534]m and[0.0682528873,0.2296533300]m. Inspected the unchanged bootstrap implementation and output metadata:10,000 draws, PCG64 seed20260926, paired geometry resampling within fixed strata and equal stratum weights. The report correctly limits positive aggregate intervals to this screened simulation design, notes Point's negative short-narrow group mean, and does not use overlapping/separate backend intervals as a between-estimator superiority test. This accounting audit did not independently regenerate paired-error/ROC bootstrap samples from raw poses.

The report also correctly treats ROC/AP as threshold-free discrimination, retains sensitivity analyses separately, and explains detection-only delays, misses, non-recovery censoring, unavailable/reset semantics and own-backend denominators. Faster conditional delay alone is not overall better responsiveness. Changes informed by the earlier failed screen are disclosed; original100–179 reservations remain excluded. The fresh geometry cohort must not be described as a wholly unadapted original test design.

## Completion and limits

**The planned revised controlled two-backend evaluation is complete and its reported accounting is accepted.** The evidence supports bounded geometry-dependent fixed-policy trade-offs and a positive aggregate paired interior translation-error effect. It does not establish publication novelty. The final manuscript remains incomplete; a precise comparison against the documented OCE overlap and a reviewed scientific manuscript are still required. Hilti remains development-only with inadequate sustained independent reference, GEODE failures remain preserved, and the earlier screening digest discrepancy remains unresolved.

Acceptance covers the exact export/report hashes below. Subsequent numerical/source/report changes require rechecking the affected identities and conclusions. Documentation and visualization updates may cite this scoped result; no tuning, resampling, native-output selection or relaxation of original gates is authorized by this audit.

```json
{
  "schema": "final-geometry-v2-result-audit-v1",
  "scope": "complete dataset and accounting; publication novelty NOT established",
  "artifacts": {
    "fastlio_analysis.json": "0760db8485d1bb4e18aa227503c46591316dad21a88ce697543bd1e0152f182b",
    "pointlio_analysis.json": "7e33f976236cc9b6d3545a8a65c29dbe88bfccbb3d467946a0f48bda58e5d475",
    "fastlio_batch.json": "b6f862ad9bdf745d04b14452e6a9c8a9bc1b25230f06e830b1f4ce423652e7a4",
    "pointlio_batch.json": "7e2890279fd057b02cfc74f63e1a49a2eb5132370b6779ac0fc843da604f3426",
    "native_attempt_receipts.json": "3bcab0472bb8de760a9817da5dfa40c3671f088f2661793a3a7c0a65f177b87e",
    "export_audit.json": "78d70cba688cc04936e4f88018f9a7a3247e50e47a23f402d8d6945ea0962a6e",
    "RESULTS_REPORT.md": "b7498a2c10e62c2daa99c588d1715c204ff8678a3676cae08293329707d16fe8",
    "report_manifest.json": "249e74c4cf42a07e94cd8ac40a7bd7ed5a8f5ce74bb7cc4340240910f8267b8a",
    "method_summary.csv": "405f6ebadef9b63602a32dcab52f680dba799c57427fb6a1b2c20216495a67b5",
    "stratum_summary.csv": "80e63158dd66a9adad94a2b723f231e552bbced64ac45cc93c3f1a584292b3b2",
    "corridor_event_ledger.csv": "3b0ce8f26fcd3bb4524b1f7cad47bf14c14cdf42c8621d5832a71c97776161d9",
    "pipeline_state.json": "76f308c2b232c299bce2428da6f2f43b62724796f4999a28fd559c718130fbcc",
    "analysis_resume_state.json": "2b1b91f998cbcf4f75761af793d13b6ccc71888290151a95f56b42c91ebc35b1",
    "pointlio_preflight_failed_batch.json": "98b75854de6b9522730b76500dd7302f1efe5a0a90bf9222c4a037b7e9efb5bf"
  }
}
```
