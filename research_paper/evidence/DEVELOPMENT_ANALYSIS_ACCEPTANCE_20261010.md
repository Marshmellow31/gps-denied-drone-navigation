# Corrected development analyses — 10 October 2026

This note records the completed FAST-LIO and Point-LIO development analyses
after review of the frozen threshold-candidate rule. **The selected cutoffs and
event metrics did not change.** The candidate inventories and analysis source
identity did change. All data remain development-only; no held-out geometry,
input, screen or result was opened.

## Candidate rule correction

The frozen protocol requires every unique finite valid corridor score plus the
explicit `NO_ALARMS` candidate. The earlier shared selector used only scores
associated to the 10 Hz decision grid. It therefore omitted the final valid
diagnostic row from each corridor. Each omission was frame 600 at
`1059999722221` ns. The decision grid still controls when the detector can
raise an alarm; it does not limit which raw scores are threshold candidates.

The selector now takes candidates from all finite valid raw diagnostic records
and evaluates every candidate under the unchanged 10 Hz association, debounce,
false-healthy ceiling and tie rule. Each backend now has **19,104 unique raw
scores plus `NO_ALARMS` (19,105 candidates)**. The omitted terminal values do
not change either selected threshold or any resulting event metric. The old
Point-LIO analysis at the Acer `analysis_20261010/` path is retained as
superseded evidence; the corrected results below use the separate
`analysis_20261010_v2/` output. FAST-LIO v2 is similarly stored in
`t16_analysis_20261010_v2/`.

## Development results

| Backend and signal | Threshold | False-healthy events | Recovery detections | Median delay among detected events |
| --- | ---: | ---: | ---: | ---: |
| FAST-LIO minimum eigenvalue, `G_3m` | 166.16366016039856 | 1/31 | 13/32 | 0.9003 s |
| FAST-LIO fixed DCReg adaptation | fixed `kappa_th=10` | 0/31 | 30/32 | 4.0503 s |
| Point-LIO minimum eigenvalue, `G_3m` | 123.80876977779258 | 3/32 | 21/27 | 3.2003 s |
| Point-LIO fixed DCReg adaptation | fixed `kappa_th=10` | 11/32 | 20/27 | 1.7503 s |

Both scalar thresholds were fitted independently on their own 32 corridor
events, choosing maximum recovery sensitivity subject to the frozen
conditional false-healthy event ceiling of 10%; controls were excluded.
FAST-LIO's own poses yielded 32/32 recovered corridor labels and one relapse.
Point-LIO's own poses yielded 27 recovered, five no-recovery labels and one
relapse. These backend-specific truth labels give different sensitivity
denominators, so these development counts are not a common-denominator claim
that one backend is better. The fixed DCReg rows are descriptive and were not
tuned.

The primary paired interior-motion standard deviation remains 0.2503454775 m
over 32 independent geometry pairs. The frozen sample-size calculation still
sets 48 final primary geometry pairs, 12 per stratum. This is a development
planning value; the final-data gate remains closed.

## Cohort and runtime accounting

The recovered primary FAST-LIO cohort has 64 completed scene runs plus four
declared repeats. Its 69 native attempts include one preserved interrupted
seed-37 attempt and its technical retry. The Point-LIO cohort has exactly 64
formal slots: 62 new completions and the two reviewed seed-14 corridor/control
slots reused from cache. All 64 verifications and offline evaluations pass.
Across Point-LIO there are 38,400 input/indicator frames, 38,208 emitted poses
and valid indicator frames, 192 explicit initialization-unavailable frames,
zero resets and no failed formal attempt. Its corridor labels are all truth
eligible. Full raw streams, receipts, native directories and input bags remain
on Acer; manifests bind their hashes.

The corrected analyses used the frozen Python 3.12.14 / NumPy 2.5.3 runtime.
The complete research suite ran **210 tests: 209 passed, one optional scene
audit skipped**. The test log is
[`development_workflow_full_tests_20261010.log`](development_workflow_full_tests_20261010.log).
Independent Point-LIO acceptance is in
[`POINTLIO_DEVELOPMENT_ACCEPTANCE_20261010.md`](../reviews/POINTLIO_DEVELOPMENT_ACCEPTANCE_20261010.md).

## Exact analysis artifacts

The corrected manifest and exhaustive candidate tables are retained with this
repository under [`development_analysis_20261010/`](development_analysis_20261010/).
Their manifest hashes are:

- FAST-LIO corrected manifest:
  `1678e1c8b62b3ceeabf4e9f4e63593832cf8c94f7793e7b933647e8569c082f7`.
- Point-LIO corrected manifest:
  `e3a03d83f5854c5705177bc7610cb6ff18d9f0d331f50783c23dcd036b6ce254`.
- Shared corrected analysis source `t16_development_analysis.py`:
  `f34fa9479e95bfa78823e3be8f70d63445631d09f3d46fe59a75331ae2975077`.
- Point-LIO analysis source:
  `ff8968a8bf7658ebfe6b35dd9a7ebf268f2c28c817c6d1d261f2890acec21c7b`.

The development comparison figure, source and hash manifest are under
[`figures/development_signal_comparison_20261010/`](../figures/development_signal_comparison_20261010/).
Its error bars are 95% Wilson intervals over geometry events. It is explicitly
labelled as development evidence.

The separate Point-LIO replication freeze passed independent review; see
[`POINTLIO_REPLICATION_FREEZE_REVIEW_20261010.md`](../reviews/POINTLIO_REPLICATION_FREEZE_REVIEW_20261010.md).
Overall R3 still requires final execution/analysis interfaces and the exact
implementation inventory. No final geometry has been generated or screened,
and neither acceptance opens the held-out gate or establishes the paper's
final scientific conclusion.
