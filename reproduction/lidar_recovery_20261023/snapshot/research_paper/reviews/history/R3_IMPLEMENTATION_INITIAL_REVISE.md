**Gate:** REVISE

# R3 independent implementation review — 27 September 2026

The development evidence is reproducible at the level independently checked
below, but the final runner and reset handling are not ready to freeze. No
held-out geometry, sensor input or result was generated, screened, replayed or
opened for this review. No final-run `screen` or `run` CLI was invoked. The
existing rejection tests exercise those interfaces only with a failing gate.
This review does not authorize held-out work. `IMPLEMENTATION_FREEZE.md` is
deliberately not created on this REVISE verdict.

Reviewed HEAD: `f09f62fa805082b8138a44a2f43833f68e0c39d3`, dirty worktree.
The reviewer inspected the current handoff, status, execution plan, R2 freeze,
T13–T16 reports/handoffs, T14/T15/T16 machine manifests, relevant protocols,
implementations, patches and tests. The engineering code-review skill was
used for correctness and error-handling review. Existing source, evidence,
protocol and status files were not changed by this review.

## Required repairs

### T16-R3-01 — Repair the post-gate runner's unconditional crash

`experiments/src/final_evaluation_runner.py:292` refers to `PROFILE_ID`, but
that name is neither defined nor imported in the module. Independently
importing the module confirms `"PROFILE_ID" in vars(module)` is false. Every
first replay, successful or failed, reaches this reference before writing its
run manifest or ledger entry. Thus a PASS would currently expose held-out
data and then fail with `NameError`, leaving an unaccounted run directory.

Use the declared route constant and add a successful-lifecycle test using
mocked processes and development-shaped fixtures. Exercise success, crash,
timeout, retry and cache paths without sampling reserved geometry or running
LIO. Verify manifests and ledger entries, not only return codes.

### T16-R3-02 — Distinguish completed replay from truncated output

At lines 316–343, the final runner checks stream-file existence and subprocess
success, but does not inspect postprocessing counts or temporal coverage.
The frozen shell wrapper launches FAST-LIO in the background and discards
its exit status during cleanup. A nonempty, internally valid prefix of health
groups passes `audit_health_export.audit`; its matching Hessian prefix passes
DCReg parity. A header-only pose CSV is accepted by the trajectory evaluator,
which successfully reports zero rows. Consequently, after T16-R3-01 is fixed,
an empty/truncated pose stream with partial health/Hessian streams can become
`COMPLETED`, and its scratch inputs can be deleted.

Validate delivered scan groups, timestamps/horizon, pose-stream presence and
replay completion independently of scientific accuracy. Missing/invalid
estimates in an otherwise completed run must remain visible; do not demand
597 valid poses or favorable errors from every new scene. Record incomplete
execution separately, retain its inputs, and allow only the documented
technical retry. Test header-only poses, partial groups, early backend exit,
valid unavailable records and a complete run. A wholly header-only health
file is already rejected; that existing guard does not solve truncation.

### T16-R3-03 — Enforce the reviewed implementation and selection lineage

The PASS parser checks text, not a reviewed content bundle. The screen checks
the split file hash, but does not validate the current development-analysis
hash or rederive the supplied plan. The run checks selected older T14 sources
and a supplied binary, but does not enforce R3 hashes for the new held-out
generator, final runner, T16 analysis source/manifest or the screen's saved
generator/review/freeze/plan hashes. Editing the new generator after PASS or
screening can therefore change test inputs without invalidating the gate.
The run accepts repeated seed IDs within a stratum; list length alone is not
an independent-event count. It also checks a caller-provided binary path,
while `rosrun` chooses the executable from the workspace/environment.

Bind screening and execution to a machine-checkable R3 content inventory;
verify it before geometry access. Validate the exact frozen plan, development
manifest, target count, unique ascending seeds, strata, eligibility records,
and screen-to-plan/review/freeze/source linkage. Verify the binary actually
launched. Check and record the frozen Python/NumPy environment. Include these
identities in per-run fingerprints and cache checks. Negative tests must
reject altered hashes, duplicated seeds and stale screens before any input
generation. A retained dirty-tree patch or equivalent immutable source
snapshot with hashes is still required when the eventual freeze is written.

### T16-R3-04 — Make scalar and threshold-sweep debounce agree at resets

`select_fastlio_threshold` (lines 575–605) tracks source timestamps but never
segment IDs. It can count two healthy records before a reset and one after it
as a recovery alarm, or preserve an active state across the reset. Scalar
`debounce` recognizes segment changes, so threshold calibration and reported
metrics need not describe the same classifier.

Independent synthetic counterexample: 600 available ticks, score zero before
tick 5 and ten afterwards, distinct source timestamps, segment 0 through tick
6 and segment 1 from tick 7. With onset 0.5 s and recovery end 0.8 s, the sweep
selects threshold 10 with sensitivity 1.0; scalar summarization at threshold
10 has sensitivity 0.0 and first transition at tick 9. No reserved seed or
input is involved. Separately, an already-active scalar state discards the
first healthy new-segment record (lines 373–375), delaying confirmation by a
tick rather than starting the new three-record sequence there.

Use one state-machine definition or prove parity across both implementations.
Test resets while inactive and active, repeated sources, invalid barriers,
staleness and exact threshold ties. Recompute development analysis after the
fix and preserve the old manifest. The reviewed development runs contain no
reset, so this review establishes an edge-case defect, not a demonstrated
change to their selected threshold.

### T16-R3-05 — Preserve unavailable 3-second windows in coverage

`summarize_three_second_sensitivity` (lines 969–974) skips a row when its
`window_end_ns` is missing. Such a row can be a planned post-exit window with
an unavailable estimate; it must reduce coverage rather than disappear from
the planned denominator. Build planned eligibility from start time and the
declared window/horizon, then retain invalid/missing endpoints with reasons.
Test a completed run containing a missing endpoint and a reset. The current
development set has complete 3-second windows, so its reported 5,440/5,440
counts reproduce; that does not validate missing-data behavior.

### T16-R3-06 — Finish failure accounting and resumability

Input generation and paired-bag audit failures escape the final batch without
a durable failed pair/stage record. `_run_scene` cannot resume an attempt-1
`POSTPROCESSING_FAILED` directory; it raises the overwrite guard. Interrupted
generation similarly leaves an incomplete scratch pair that only produces
another exception on resume. The final ledger records successful runs as
`REPLAYED` but never records their final `COMPLETED` state. Per-run manifests
omit the reviewed implementation/environment identity described above.

Persist stage/attempt identity before work; preserve failure causes and exact
inputs; record terminal states consistently. Define safe resume behavior for
interrupted generation, postprocessing failure and exhausted retries. Do not
replace failed geometry or rerun an estimator merely for an unfavorable
metric. Add mocked failure/resume tests and ensure incomplete batch CLI exits
nonzero. Keep the 900-second replay timeout and process-group cleanup, which
are useful existing guards. Filesystem free-space checks are only a lower
bound: the prior per-user `/tmp` quota failure can recur despite reported
filesystem headroom and must remain diagnosable.

### T14-R3-01 / T16-R3-07 — Quantify the retained repeat evidence

The seed-14 pre-batch pair is an acceptable disclosed exact-input repeat
substitute in principle: independently verified input/backend fingerprints
match, and the only excluded source-fingerprint difference is the documented
provenance runner. The failed scheduled repeats/retries must stay in the
ledger, and the smoke must never become an additional independent event.
However, T16 carries only hash equality flags for variability; T14 explicitly
required numerical quantification. Byte differences do not establish whether
labels, scores, detection decisions or paired variance are stable.

For orientation, independently recomputed full-run 1-second translation-error
medians over 587 valid rows per replay are:

| Pair | Primary median (m) | Repeat median (m) | Largest aligned absolute error change (m) |
| --- | ---: | ---: | ---: |
| Seed 14 corridor | 0.0333379179 | 0.0333379179 | 0 |
| Seed 14 control | 0.0267166003 | 0.0475476582 | 0.1159095239 |
| Seed 45 corridor | 0.0521550899 | 0.0416645768 | 0.1683963712 |
| Seed 45 control | 0.0356815529 | 0.0430280527 | 0.4159563392 |

These illustrative whole-run summaries are not the frozen event/interior
statistics. Add reproducible paired score/error differences, fixed-threshold
decision/label agreement and interior-statistic sensitivity for the four
repeat comparisons. Do not recalibrate on repeats or silently replace the
declared primary outputs. Explain the limits imposed by observed stochastic
backend variation.

## Checks that passed and scientific adjudications

- R2: **51/51 hashes match**. Current `FREEZE.md` SHA-256 is
  `8b6ef5fb83ff459f078bb89c9f0dc7b1708e44d23dfb586598d36ba59198031f`.
  D034 remains intact; the original freeze identity is
  `34e9522beb259fb280ff662f3f4dfab9e3a152cf88ef57f04bd9eb257185af6d`.
  No protocol hash was silently amended by this review.
- Both the system Python 3.14.4/NumPy 2.3.5 and the frozen ROS analysis Python
  3.12.14/NumPy 2.5.3 ran the complete existing suite: **86 tests, 85 passed,
  one optional SciPy test skipped**. The current post-R3 tests only cover
  planning and rejection, explaining why the successful-run defect escaped.
- T13: the Schur complement block permutation, pseudoinverse, spectral
  tolerances, strict `kappa > 10` rule and explicit unavailable/serialization
  behavior match the frozen adaptation. The official pinned
  [DCReg example](https://github.com/JokerJohn/DCReg/tree/8ce8451b15491a4bbe17cf85ab02a8bed6696861)
  was checked live against its published spectra. Fourteen focused tests pass.
  The detector remains an adaptation, without DCReg's physical-axis mapping,
  full registration or PCG mitigation.
- T13 retained on/off poses and health streams independently hash-match.
  Recomputed raw-Hessian/T08 parity gives 600 timestamps, 597 valid groups,
  three unavailable groups and maximum absolute eigenvalue discrepancy
  `3.637978807091713e-11`. No replay was necessary.
- T14: independently verified **768/768 primary output hashes**, all 64
  primary run-manifest identities, and **42/42** retained repeat output hashes
  (18 pre-batch seed-14 files and 24 seed-45 repeat files). The 74-entry failure
  history is preserved: 66 completed, four crashed and four invalid-input
  attempts. Formal route translation and development seed guards match R2.
- T16: all six saved output hashes match. In Python 3.12.14/NumPy 2.5.3,
  independently loaded all 64 primaries with their provenance checks and
  recomputed both method summaries, sample-size statistics, weighted curves
  and 3-second summaries; all match the machine manifest exactly. Separately
  taking the maximum feasible `(sensitivity, threshold)` over its candidate
  CSV gives `166.16366016039856`, 13/32 sensitivity and 1/31 conditional
  false-healthy events. This is development selection, not independent
  performance validation.
- The primary labels use shared nearest boundaries, no per-window alignment,
  the full triple deadline and first-episode relapse. All 32 events recover;
  seed 24 relapses at `30.999722221 s`. Controls receive no recovery label.
  `s_dev=0.2494728850627583 m`, `n_cont=24`, `n_test=48` reproduce.
- Seed 15 has a continuous initial unrecovered interval from
  `23.957044710786963 s` to `23.99972222 s`, but no 0.1-second decision tick
  inside it. Consequently 31 conditional events and 32 unconditional events
  are consistent with the frozen definitions; this is not an off-by-one bug.
- `find_recovery` skips later rows with missing start boundaries. A direct
  artificially inconsistent window list can expose a skipped relapse, but
  shared-boundary production windows first expose a missing boundary as the
  previous window's missing end, whose start exists and triggers relapse.
  No production counterexample was established. Add a coherent
  `build_primary_windows` missing-boundary regression test; do not invent a
  new nominal relapse convention on the evidence of an impossible fixture.
- Weighted ROC/AP correctly group score ties and give each event unit total
  weight; one-class curves are unavailable. The manifest's
  `right_censored_delay_median_s_including_misses` is a median of observed
  detection/censoring durations, not an estimated survival median. Keep that
  distinction explicit if presenting it; the primary detected-only median
  and detection fraction remain the frozen reporting pair.
- T15: independently verified all six final output hashes and identical V2/V3
  pose hashes (`a6373a10895e2449d99d663d59f444247865ea39a8d9768192cca2cdc1760abd`).
  Point-LIO's pose-format smoke is supported. Its missing comparable
  health/Hessian export means second-backend indicator replication remains
  unestablished; the original minimum replication study cannot be declared
  complete. This review requires no new backend work as a hidden condition
  of the bounded FAST-LIO repairs.

## Reviewed content identities

These identify the reviewed pre-repair state; they are not a PASS freeze.

| File | SHA-256 |
| --- | --- |
| `experiments/src/final_evaluation_runner.py` | `3de7593bc74675c9b144b2646271a91806ae7222fb2e81296afadac4c6a4fd29` |
| `experiments/src/heldout_simulation.py` | `81804905abebf0ae4eaed7e16e52ae8cb0f6f72c9b4cfaf3b40dc7e565d6f811` |
| `experiments/src/t16_development_analysis.py` | `5a74d395cb606f6ba46b3789a4612fba1f5a2b7d10504920625ee989c6ed02eb` |
| `experiments/src/dcreg_schur.py` | `516e1da40c9cb8bc58e5a0e4c9c7964392a0877a77ba20e7139eae997783595e` |
| `experiments/run_simulation_smoke.sh` | `a3465d33b85b7f0b0f59e444297c1b71447af1ee7aa3dd2773b33a0172ca3639` |
| `evidence/t14_development_batch_manifest.json` | `66be7cda05e1f97089e523272af5dfd78b70134b12ebd3a9964cf15ad8bc4b87` |
| `evidence/t15_point_lio_smoke_manifest.json` | `e744444d367b1b485020d2800fb92736f3bd07de4b4549a2f9f26fa177a79f6b` |
| `evidence/t16_development_analysis_manifest.json` | `1a716973445616ad0a09b207d50acd49dcfd8e3a87fac09c6d567726acc5b011` |

Reproduction checks used `python -m unittest discover -s
research_paper/experiments/tests -q`, both under system Python and the pinned
ROS environment. Hash/read-only analysis checks called the existing
`_load_run`, `summarize_method`, `interior_sample_size`,
`threshold_free_curves`, `summarize_three_second_sensitivity`,
`verify_g3_parity` and repeat-audit helpers on development paths only. They
did not call `analyze` (which writes outputs) or invoke any LIO backend.

Next: implement the numbered bounded repairs, preserve prior artifacts and
failure history, rerun development-only verification, update handoff/status
consistently, then request focused independent R3 re-review. Simulation
remains axis-aligned geometry with one prescribed motion, ideal timing and
extrinsics, uncalibrated noise, and analytic truth. Neither a later PASS nor
the present development results establish real-world accuracy, flight safety,
publication novelty or completed final evaluation.
