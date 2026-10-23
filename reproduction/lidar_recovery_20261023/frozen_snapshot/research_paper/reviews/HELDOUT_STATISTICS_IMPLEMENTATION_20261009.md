# Independent frozen statistics implementation review

**Date:** 9 October 2026. **Decision: PASS for the repaired numerical module
on analytic fixtures only.** No held-out geometry, recording, native replay or
final outcome was generated, opened or analyzed. This review does not grant
R3/implementation-freeze acceptance or a confirmatory claim.

The reviewer compared `heldout_statistics.py` with the frozen bootstrap,
paired-outcome and ROC/AP definitions in `protocol/METRICS.md`, inspected its
existing tests and added meaningful synthetic counterexamples. The module
imports NumPy and has no file reader or geometry/backend generator.

## Method fidelity

- Random draws use `Generator(PCG64(20260926))`, with replicate outermost and
  the fixed short-narrow, short-wide, long-narrow, long-wide stratum order.
  Each draw has the stratum's original geometry count and replacement is
  enabled. All **10,000** draws matched an independent literal RNG stream.
- Seed lists must be ascending, unique, disjoint and balanced across all four
  required strata. Already computed corridor-minus-control per-seed outcomes
  are resampled as a single geometry unit, preserving pairing. Estimates and
  resamples are equal-weight means of the four stratum-specific means.
- Confidence bounds use 2.5/97.5 percentiles with NumPy `method='linear'`.
  A nonconstant analytic fixture independently reproduced the paired point
  estimate, literal bootstrap aggregation and both bounds. Missing paired
  keys reject; nonfinite outcomes produce an unavailable interval rather
  than being zero-filled or excluded.
- Curve weighting gives each scored geometry total weight one. Bootstrap
  multiplicity scales that geometry's whole contribution, not its individual
  frames independently. Duplicating one event's frames 19 times does not alter
  its curve point estimate or interval. No-score events remain in the required
  planned inventory and availability counts; the all-empty case is unavailable.
- Tied scores are grouped before trapezoidal weighted ROC-AUC and step-sum
  average precision. These match the existing frozen `_curve` definition.
  A missing truth class makes the statistic undefined. **Any** undefined
  bootstrap replicate makes the curve interval unavailable; the count is
  reported rather than dropping failed replicates and computing a selected CI.

## Contract repairs checked

Initial input handling silently converted unavailable truth such as `None`
to a negative class and did not support NumPy event arrays. The main agent
repaired these before this PASS. Labels now require explicit Boolean or
integer 0/1 classes; unavailable/NaN/string labels reject. Sequence emptiness
uses length rather than array truth conversion. Replicate count must be a
positive integer, and integer seed identities cannot be Boolean or silently
truncated floats. Counterexample tests verify these protections. The changes
guard the existing statistical definition; they introduce no new estimator,
metric, threshold or sampling method.

## Independent verification

**13 focused tests passed** under the frozen Python 3.12.14/NumPy 2.5.3 runtime.
The fixtures are artificial numerical vectors/seed identifiers, not actual
held-out geometry or data. They include full draw-stream parity, linear
percentiles, event weighting/duplication, no-score/undefined-class handling,
missing/nonfinite pairs, invalid identity/count inputs and array support.

```bash
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python \
  -m unittest discover -s research_paper/experiments/tests \
  -p test_heldout_statistics.py -v
```

Reviewed module SHA-256:
`09a6471003e692d2fafc9058fbe62662935bc46fa8f9feb7cbaa23b39a055a50`.
Reviewed test SHA-256:
`7e0569e97766c4e2faf89e8aede0ce0097a91eac0e69310b6e7f3ec855e43e09`.
The reviewer edited only the test file; the main agent repaired production.

## Mandatory final caller and publication boundaries

The module cannot infer the real planned sample size, selected geometry
ledger, run completeness, interior-window eligibility, locked thresholds or
R3 status. `confirmatory_replicate_count` certifies **only** that the numerical
call used 10,000 replicates. `AVAILABLE` is numerical availability, not
confirmatory-dataset authorization.

A final caller must separately verify the R3/replication/implementation freeze,
exact reviewed source inventory and frozen runtime; bind ascending selected
seeds to the planned equal-stratum cohort; retain every failed pair/attempt;
check both complete native runs and usable primary interior windows for
**every planned pair**; and supply only explicitly valid truth/score samples
to curves while preserving no-score events in the full inventory. If any
planned pair fails after the allowed retry, successful-run results must stay
descriptive, without a confirmatory interval at the planned sample size.
An unavailable curve interval cannot be repaired by dropping bootstrap
replicates, events or strata. These conditions require caller integration
review before R3, not an assumption from this module's PASS.

The optional read-only check of `paper/methods_protocol_draft.tex` found its
bootstrap/paired aggregation, undefined-interval and incomplete-cohort prose
consistent with the frozen metrics. Its 48-pair statement is the current plan,
not an executed result. The draft retains simulation/handheld-reference limits
and makes no final recovery finding. Final claim, citation and full manuscript
review remain separate gates. Overall R3 and held-out work stay sealed.
