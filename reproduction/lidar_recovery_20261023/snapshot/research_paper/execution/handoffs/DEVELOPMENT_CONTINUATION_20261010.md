# Development continuation — 10 October 2026

The complete-paper goal remains open. This checkpoint records a finished and
independently reviewed Point-LIO development cohort, a corrected all-score
threshold sweep for both backends, and the next remaining implementation gate.
Held-out geometry and results remain sealed.

## Completed in this checkpoint

Primary FAST-LIO recovery is complete: 64 primary scene slots plus four
declared repeats, with 69 attempts including one preserved interruption and
its technical retry. The new primary evidence and event tables are described
in [`PRIMARY_DEVELOPMENT_RECOVERY_20261009.md`](../../evidence/PRIMARY_DEVELOPMENT_RECOVERY_20261009.md).

Point-LIO completed all 64 formal development slots for seeds 14–45: 62 fresh
native completions and two previously reviewed seed-14 slots reused from
cache. All 64 verifications and offline evaluations pass. Its own pose stream
labels 27/32 corridor events as recovered and five as no-recovery within the
horizon; one event relapses. Full native receipts, logs, bags, sidecar data and
evaluation streams remain on Acer at
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/POINTLIO_DEVELOPMENT_20261009/`.
Independent acceptance is
[`POINTLIO_DEVELOPMENT_ACCEPTANCE_20261010.md`](../../reviews/POINTLIO_DEVELOPMENT_ACCEPTANCE_20261010.md).

Review found and repaired one threshold-selection defect. The frozen rule
requires every unique finite valid raw corridor score plus `NO_ALARMS`; the
first analysis used only values associated with the 10 Hz decision grid and
missed the last valid frame in each corridor. The shared selector now uses all
valid raw diagnostic scores, while still evaluating alarms on the frozen
decision grid. The repaired full sweeps have 19,104 unique scores plus
`NO_ALARMS` for each backend. The cutoffs and event outcomes did not change.
Both old analyses remain preserved; corrected manifests and complete
candidate tables are in
[`development_analysis_20261010/`](../../evidence/development_analysis_20261010/).
The correction and current counts are summarized in
[`DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md`](../../evidence/DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md).

The separate Point-LIO freeze passed independent review in
[`POINTLIO_REPLICATION_FREEZE_20261010.json`](../../protocol/POINTLIO_REPLICATION_FREEZE_20261010.json)
with exact SHA-256 `87f31c5febff860fe774eb4533a1be584f68b663f0125ea40dc18e85cc587621`.
See the [freeze review](../../reviews/POINTLIO_REPLICATION_FREEZE_REVIEW_20261010.md).
It does not open the held-out gate.
Overall R3 remains REVISE pending a complete current final runner/analysis
interface and implementation freeze that binds the corrected evidence.

The corrected development comparison figure, plotting source and hash manifest
are in
[`development_signal_comparison_20261010/`](../../figures/development_signal_comparison_20261010/).
PNG and PDF were visually inspected. The frozen environment suite ran
**210 tests: 209 passed, one optional scene audit skipped**; see
[`development_workflow_full_tests_20261010.log`](../../evidence/development_workflow_full_tests_20261010.log).

## Current development-only operating points

FAST-LIO's candidate threshold is `G_3m >= 166.16366016039856`: 13/32
truth-recovered events detected and 1/31 conditional initial false-healthy
events. Its fresh primary cohort labels 32/32 corridor events recovered, with
one relapse. Fixed DCReg detects 30/32 and has no initial false-healthy event;
it produces a false-healthy event after the one relapse.

Point-LIO's separately fitted threshold is `G_3m >= 123.80876977779258`: 21/27
truth-recovered events detected and 3/32 conditional initial false-healthy
events. Its fixed DCReg comparator detects 20/27 and produces 11/32 initial
false-healthy events, including a false-healthy event after its one relapse.
These development denominators come from each backend's own poses, so they do
not establish which estimator is better.

The FAST-LIO paired interior sample standard deviation remains 0.2503454775 m;
the frozen development size calculation still plans 48 final geometry pairs,
12 per stratum. This is not permission to generate or screen them.

## Next work

1. Integrate the corrected development manifests into the final evaluation
   plan and current analysis interfaces. Preserve the accepted Point-LIO native
   producer snapshot so later R3 code changes cannot rewrite native history.
2. Complete the full R3 audit and implementation freeze. Keep all final inputs
   sealed until R3 passes.
3. After R3 passes, screen the frozen lowest-eligible 48 layouts, run the
   primary and Point-LIO replication with all attempts retained, and apply the
   frozen event-level uncertainty analysis.
4. Refresh primary-source novelty claims against actual results, complete the
   full manuscript and figures, compile and inspect the final PDF, and prepare
   the professor review package. Do not contact the professor or submit the
   paper without explicit instruction.

No final geometry, screen or final result has been generated or opened. This
checkpoint makes no physical-flight, deployment or publication claim.
