# Provisional evaluation metrics

Version: T11 protocol `0.4`, frozen 26 September 2026 after R2 PASS and a 51/51 base-file hash read-back, with accepted Point-LIO amendment D050 (29 September 2026); see [`FREEZE.md`](FREEZE.md) and the [Point-LIO amendment](POINTLIO_REPLICATION_AMENDMENT_20260929.md). The user approved the full-triple-within-20-seconds recovery deadline and formal x=-6 m route. This freezes the analysis plan, not implementation, publication novelty or a recovery result. No held-out work is permitted before R3.

**Data update (26 September 2026):** Hilti remains a supporting illustration; only 13/56 matched post-exit 1 s windows and 0/56 3 s windows have usable reference. The primary pilot is the truth-isolated v3 simulation in [SIMULATION_MOTION_V3.md](../evidence/SIMULATION_MOTION_V3.md), with the four-seed fixed-layout follow-up in [SIMULATION_SEED_SENSITIVITY.md](../evidence/SIMULATION_SEED_SENSITIVITY.md). All v1/v2/v3 runs remain development data, and seeds 10–13 share one geometry cluster. No threshold or recovery label has been selected from final-test data. See the [current handoff](../execution/CURRENT_HANDOFF.md).

## Quantities kept separate

The study reports three different objects and does not substitute one for another:

1. **Geometric/localization health indicator:** an online diagnostic computed without reference truth.
2. **Local relative-motion error:** agreement of estimated and reference motion over a fixed physical time window.
3. **Accumulated original-frame pose error:** pose disagreement after one pre-event rigid alignment, without later re-alignment.

An indicator may correctly report restored local constraints while accumulated drift remains large. That is not automatically false reassurance unless the indicator's documented claim includes accumulated/global accuracy.

## Pose notation

The [data contract](DATA_CONTRACT.md) defines `T_A_B` as mapping frame `B` coordinates into frame `A`. After conversion to common comparison body `B`, let:

- `T_G_B^r(t)` be the reference body pose in reference world `G`;
- `T_W_B^e(t)` be the estimated body pose in estimator world `W`.

Quaternions are `qx,qy,qz,qw`; distances are metres, times seconds, and stored angles radians. Tables/figures may display degrees if labeled.

## Local relative-motion error

For two associated estimator timestamps `t0` and `t1`, where `t1` is selected near `t0 + tau`, define:

```text
Delta_r(t0,t1) = inverse(T_G_B^r(t0)) * T_G_B^r(t1)
Delta_e(t0,t1) = inverse(T_W_B^e(t0)) * T_W_B^e(t1)
E_rel(t0,t1)   = inverse(Delta_r(t0,t1)) * Delta_e(t0,t1)
```

Both deltas map the comparison body at `t1` into the comparison body at `t0`; therefore `E_rel` is meaningful without global-frame alignment. If `E_rel = [R_rel, p_rel; 0, 1]`, report:

```text
local_translation_error_m = norm(p_rel, 2)
local_rotation_error_rad  = acos(clamp((trace(R_rel) - 1) / 2, -1, 1))
```

Rates divide these errors by the actual `t1 - t0`, not by nominal `tau`. Endpoint reference poses use the interpolation policy in the data contract. There is no new global alignment at either endpoint.

### Frozen T11 local windows

- Primary: non-overlapping `tau = 1.0 s` windows on an integer-second
  simulation-clock grid. Associate each nominal integer boundary once to the
  nearest valid estimator pose within `±0.05 s`, ties to the earlier pose;
  reuse that same associated pose as the previous window's end and the next
  window's start. If no pose matches, the boundary is unavailable. This T11
  label rule is more specific than the generic evaluator row policy in
  [DATA_CONTRACT.md](DATA_CONTRACT.md). Use actual associated timestamps for
  window durations and the event deadline.
- Secondary: `tau = 3.0 s`, reported as translation/rotation error rates per
  actual window duration. It is a sensitivity outcome, not a second label.
- Causal indicator sample: latest diagnostic record (valid or invalid) at or
  before a planned decision tick, maximum age `0.2 s` and same estimator
  segment. If that latest record is invalid, do not skip it to reuse an older
  healthy value. No future values/interpolation.

One second spans about ten scans at the current 10 Hz stream. The 3 s outcome
checks whether local error persists over a longer interval. All current pilots
are development data. R2 froze the numerical tolerances and study budget below.

The denominator for each window is the number of planned integer-grid windows
for which both nominal boundaries should exist in the evaluation horizon.
Report valid-window count and coverage separately. Each nominal boundary may
map to only one unique pose; actual boundary times must increase strictly and
both endpoints must lie in the same segment. A window with actual duration
outside `[0.9,1.1] s`, a reset barrier, or a missing endpoint is invalid. Invalid
windows never enter mean/median error as zeros.

## Fixed-alignment accumulated pose error

For each planned scene, set one alignment anchor at the valid associated
estimator pose nearest `entry_start - 5.0 s`, with an absolute tolerance of
`0.05 s`. For v3, the predeclared simulation anchor is `t=5 s` (epoch
1005 s); the body first crosses x=0 at 9.25 s. Future route templates must
record their entry time and anchor before replay. Real Hilti's old pre-exit
anchor is historical supporting evidence and is not mixed into the simulation
summary. Define the transform exactly once:

```text
T_G_W = T_G_B^r(t_anchor) * inverse(T_W_B^e(t_anchor))
T_G_B^aligned(t) = T_G_W * T_W_B^e(t)
E_acc(t) = inverse(T_G_B^r(t)) * T_G_B^aligned(t)
```

Translation and rotation error use the same norm and `SO(3)` angle definitions as above. This is an `SE(3)` alignment with scale fixed to 1.0. It is not recomputed at entry, exit, after a reset, or for each window. A reset/discontinuity remains visible under the original alignment or becomes explicitly unavailable if frame semantics are lost.

The primary protocol uses this single alignment anchor only. It is transparent
and avoids an underdetermined trajectory fit, but is sensitive to one
reference/estimate sample. No multi-pose alternative is authorized in the
current protocol; if a test fixture shows the anchor rule is not computable,
return to R2 with the failure evidence before batches rather than selecting a
new alignment from favorable results.

## Frozen event anchor and horizon

Each simulation event records its CAD doorway plane, body-path crossing time,
and a separate scene-only ray/normal audit. The crossing is a layout anchor,
not a claim that the estimator becomes observable at that instant. It is
independent of online indicators and estimation error. In v3, body exit at
x=12 m is 24.25 s; v3 only covers 15.75 s afterward, sufficient for the
feasibility pilot but shorter than the final planned horizon.

The final study will run each prescribed route for 60 s, with at least 20 s
after the last weak-geometry exit. T14's formal randomized profile must start
at `x=-6 m` (rather than the feasibility-smoke profile's `x=-5 m`) while
keeping the same rest, speed ramp and smooth 3D motion shape. This gives
10.5 s before the body crosses the entry plane at `x=0`; its exit time is
`t_exit = 3 + (6 + L)/0.8 s`, at most 33 s for `L=18 m`, leaving 27 s after
exit in a 60 s run. The T12 seed-14 smoke used the legacy start and remains
feasibility-only; T14 must regenerate the full development split using the
formal profile and record a new run ID. Show at least 10 s of pre-entry
context, the complete annotated weak interval, and the full post-exit horizon.
If a scene's planned trajectory fails to provide that coverage, the event is
invalid for the primary recovery analysis and remains in the failure ledger.
No event boundary may be moved after viewing an indicator/error curve.

Hilti's 31.6–33.6 s interval remains an exit-only supporting illustration.
Its matched post-exit reference gaps and partly LiDAR-map-derived truth make
it ineligible for the primary quantitative recovery outcomes.

## Recovery labels

A **1 s local-motion window passes** when both its relative translation
error is at most `0.20 m` and its relative rotation error is at most
`5 degrees`. These cutoffs are borrowed as operational reference points from
DCReg's published registration-pair success definition (RRE <5 degrees,
RTE <0.2 m; see the audited supplement). Applying them to a 1 s LIO motion
window is an explicit adaptation, not the same registration metric. Sensitivity
labels use half and double tolerances: `0.10 m/2.5 degrees` and
`0.40 m/10 degrees`.

For every randomized layout, candidate 1 s windows use nominal integer
simulation-clock boundaries. Associate each boundary once to the nearest
valid estimator pose within `±0.05 s`, ties to the earlier pose, and reuse the
same pose for adjacent windows. The first candidate nominal boundary is
`ceil(t_exit)`; if its actual associated pose is at/before `t_exit`, skip that
boundary and continue to the next integer. Window `k` runs from the associated
pose at boundary `k` to the associated pose at `k+1`. `recovery_onset` is the
actual associated start time of the earliest triple of consecutive valid
windows that each passes both limits. All three actual window endpoints must
be no later than `t_exit+20 s`. `recovery_confirmation` is the actual
associated endpoint of the third window; it can never occur outside that 20 s
horizon. A missing/invalid boundary/window breaks the triple; do not slide or
re-anchor the grid. This resolves the boundary case where a triple could
otherwise begin before, but finish after, the deadline.
A 3 s relative-motion window is reported separately as translation and
rotation error rates; the corresponding rate limits are `0.20 m/s` and
`5 degrees/s`, and it is a sensitivity outcome, not the label.

For a truth-label-eligible event, reference poses must cover every required
1 s window endpoint from the first post-exit candidate through `t_exit+20 s`;
no gaps are bridged or replaced with zero. Missing reference coverage makes
the event's primary recovery label unavailable and it remains in the
availability/failure ledger. A missing or invalid **estimated** pose window
does not make truth unavailable and cannot pass the recovery rule. If the run
completed and no passing triple is confirmed by the deadline, report
`NO_RECOVERY_WITHIN_HORIZON`; a crashed, timed-out or incomplete run remains
`RUN_FAILED`/`RUN_INCOMPLETE` per the data contract and is not recoded as
non-recovery. Recovery labels may use future reference windows. Indicators
and their decisions at time `t` may use only data timestamped at or before `t`.

The first qualifying triple defines the primary recovery episode. For
event-level primary sensitivity, a confirmation before `recovery_onset` is a
premature false-healthy declaration, never a successful recovery alarm. A
qualifying recovery alarm must be confirmed at or after the onset and before
the first subsequent 1 s window that either fails a cutoff or has an invalid
estimated pose/segment in a completed run. The associated actual start boundary
of that window is `relapse_time`; set `recovery_end=min(relapse_time,t_exit+20 s)`, or the event
deadline if no relapse occurs. A whole-run crash/timeout is `RUN_FAILED`/
`RUN_INCOMPLETE`, not a relapse or a non-recovery. Such an attempt is excluded
from completed-event primary denominators, retained in the failure ledger, and
reported in the scheduled-run completion rate. One technical retry is allowed
only for a documented execution/environment failure with identical input,
configuration and code; the first successful attempt is primary, and all
failed attempts remain visible. Never retry because a metric/error is
unfavorable or replace a failed seed with another layout. The primary onset
remains the first recovery episode; later recoveries are descriptive only.
Report false-healthy time/declarations during any relapse interval separately
rather than silently changing the first onset. Negative detection delays are
not possible by definition.

These are development-proposed tolerances, not flight-safety tolerances or
evidence of a real drone requirement. R2 freezes the label cutoffs and their
half/double sensitivity values before batches.

## Indicator decisions and reliability metrics

FAST-LIO scores are timestamped at that backend's scan-to-map update. The
Point-LIO adaptation emits one frame-pooled score at its actual `lidar_end_time`;
only unavailable rows without usable point offsets use the amendment's marked
nominal timestamp. Both streams are evaluated under the same frozen time
association and decision rules. Evaluate the state
machine at every 0.1 s tick from simulation time zero. For primary event
metrics, use the ticks from the first grid tick at or after `t_exit` through
ticks strictly before `t_exit+20 s`. At each tick, associate the latest
**record** (valid or invalid) at or before that time, no more than `0.2 s` old
and from the same estimator segment. If no such record exists, the latest
record is invalid, or a reset/segment boundary intervenes, the decision is
`UNAVAILABLE`; never skip a newer invalid row to reuse an older healthy value.
No future sample, geometry label or reference value enters the score or
decision.

- `FASTLIO_MIN_EIG_G3` emits healthy when its development-selected threshold
  is met. Fit that threshold using development layouts only: choose the
  threshold with the greatest post-onset recovery sensitivity while keeping
  the conditional event false-healthy rate at or below `10%`. Ties choose the
  more conservative (higher) threshold. If no threshold satisfies the limit,
  report `NO_FEASIBLE_OPERATING_POINT`; do not relax the limit on held-out data.
- `DCREG_SCHUR_MASK` emits healthy only when no rotational or translational
  direction is flagged using the paper's fixed `kappa_th=10`. Do not tune this
  comparator threshold on the study data.
- `POINTLIO_MIN_EIG_G3` uses Point-LIO's own poses and its separate global
  `G_3m` threshold. Apply the same deterministic development-only objective
  below, independently from the FAST-LIO threshold. The fixed-rule
  `POINTLIO_DCREG_SCHUR_MASK` comparator retains `kappa_th=10`; do not tune it.
- For either method, debounce is a two-state machine (`INACTIVE`,
  `CONFIRMED_HEALTHY`). In `INACTIVE`, three distinct healthy diagnostic
  records on three consecutive planned ticks cause one transition to
  `CONFIRMED_HEALTHY`, timestamped at the third **decision tick**; retain the
  three diagnostic source timestamps separately. While active, further
  healthy ticks do not emit new alarm events. Any unhealthy, unavailable or
  cross-segment tick resets the count and returns to `INACTIVE`; reusing the
  same source-record timestamp on adjacent ticks also resets an inactive
  candidate count and cannot count as a new sample. After a reset, a new run
  of three distinct records can create a new alarm. The state machine runs
  before the event as well, so a persistent pre-onset alarm remains visible at
  exit but cannot be counted as a new post-onset recovery alarm.

For FAST-LIO threshold selection, use only the 32 randomized development
geometry seeds `14–45`; fixed-layout seeds `10–13` remain feasibility and
implementation evidence, not operating-point training events. No score model
is fitted, so this is development threshold calibration, not cross-validation.
Only corridor runs enter the threshold objective; controls remain paired by
geometry seed for separate healthy-scene analysis. Candidate thresholds are
every unique finite valid `G_3m` score in those development runs plus an
explicit `NO_ALARMS` candidate. Healthy means `score >= threshold`. Among
thresholds with a conditional event false-healthy rate at most `10%`, maximize
recovery sensitivity across all truth-recovered corridor events. A no-score
event or no qualifying post-onset alarm is a sensitivity miss. Ties choose
the higher numeric threshold; `NO_ALARMS` is the final, zero-sensitivity
candidate. If the false-healthy denominator is zero or every feasible
threshold has zero sensitivity, report `NO_FEASIBLE_OPERATING_POINT`. Apply
one selected global threshold to every layout; never tune per-scene values.
R2 freezes this selection procedure and all recovery thresholds. The realized
FAST-LIO numeric threshold is computed only from development outputs and
locked at R3 before held-out outputs are opened.

For Point-LIO, use the same candidate rule and objective independently on its
own `lambda_min(G_3m)` values and its own pose-derived recovery labels. Use only
the 32 corridor development seeds `14–45`; controls and the separate seed-14
feasibility attempt are excluded from threshold fitting. Candidate cutoffs are
the unique finite valid Point-LIO scores plus `NO_ALARMS`; healthy means
`score >= threshold`. Keep the conditional false-healthy event rate at or
below `10%`, maximize sensitivity among feasible thresholds, choose the higher
numeric threshold on ties, and report `NO_FEASIBLE_OPERATING_POINT` if the
false-healthy denominator is zero or no feasible threshold has positive
sensitivity. A missing score or no qualifying post-onset alarm is a miss.
This creates a separate Point-LIO cutoff only; it does not change the FAST-LIO
cutoff, recovery labels, primary sample-size plan or held-out budget. The
exact measurement-row, timestamp, reset and unavailable rules are in the
accepted amendment.

Matched feature-rich controls do not receive a post-degeneracy recovery onset
or enter primary recovery-delay/sensitivity denominators, because they have no
prespecified weak-geometry interval. Report them separately as healthy-scene
controls: local-motion accuracy, indicator availability and the fraction of
available decisions marked healthy/degenerate, paired by geometry seed.

Report these event-level outcomes with eligible denominators:

| Outcome | Numerator / denominator |
| --- | --- |
| False-healthy event rate (primary, conditional) | Truth-label-eligible corridor clusters whose debounced `CONFIRMED_HEALTHY` state is active during the initial unrecovered interval `[t_exit,recovery_onset)` (or through the deadline for a non-recovery) / truth-label-eligible corridor clusters with at least one available decision in that interval. A zero denominator is undefined, not 0%. |
| False-healthy event incidence (unconditional) | Same false-healthy numerator / all truth-label-eligible corridor clusters with a non-empty initial unrecovered interval, including events with no available decisions. |
| False-healthy time fraction (conditional) | Decision ticks at which `CONFIRMED_HEALTHY` is active during initial unrecovered time / all available decision ticks during that time. |
| False-healthy time fraction (unconditional) | Same numerator / all planned decision ticks during initial unrecovered time. |
| Recovery sensitivity | Recovered corridor clusters with an `INACTIVE -> CONFIRMED_HEALTHY` transition at or after `recovery_onset` and before `recovery_end` / all truth-recovered, truth-label-eligible corridor clusters. A premature alarm, no available decision or no qualifying post-onset transition is a miss. |
| Detection delay | `confirmation_time - recovery_onset` for qualifying post-onset alarms; otherwise right-censor at `recovery_end = min(first relapse time, t_exit+20 s)`. Delay is never negative. Report detection fraction with median delay among detections. |
| Decision availability | Decision times with valid score / all eligible planned decision times, by method and event. |
| Run completion | Fully completed scene replays / all scheduled corridor and control scene replays; list every failed attempt and final run state separately. |
| Truth-label availability | Corridor events with reference coverage at every required primary window endpoint through `t_exit+20 s` / all planned corridor events. Report reasons for each unavailable event. |
| Non-recovery | Completed, truth-label-eligible corridor events with no qualifying triple confirmed by `t_exit+20 s`; report separately, never discard. Crashes/timeouts are `RUN_FAILED`/`RUN_INCOMPLETE`, not non-recovery. |
| Relapse | Truth-recovered corridor events with a later planned 1 s window that either has valid estimates but fails a cutoff, or has an invalid estimated pose/segment in a completed run, before the deadline / truth-recovered corridor events with complete post-onset truth coverage. Report first relapse time; do not move the primary first-onset label. |
| Post-relapse false-healthy event rate (secondary, conditional) | Relapsed corridor events with `CONFIRMED_HEALTHY` active at any decision tick from `relapse_time` through the deadline / relapsed events with at least one available decision in that interval. Report the unconditional numerator / all truth-eligible relapsed events alongside it. |
| Post-relapse false-healthy time fraction (secondary) | Active `CONFIRMED_HEALTHY` ticks after relapse / available ticks after relapse (conditional) and / all planned ticks after relapse (unconditional). |

Except for run-completion and truth-label-availability rows, primary outcome
denominators require both complete reference coverage and a successfully
completed corridor replay. Incomplete attempts remain visible in the run
completion/failure ledger and are not silently replaced by a different seed.

For threshold-free curves, each available 0.1 s decision tick is labeled
`UNRECOVERED` before onset and after the first relapse, and `RECOVERED` from
onset until relapse or the deadline. Use FAST-LIO `G_3m` as its higher-is-
healthier score and `1/max(kappa)` over DCReg's six direction ratios as the
DCReg higher-is-healthier score (`0` when any ratio is infinite). Exclude
unavailable ticks from curves and report their count/availability separately.
Give each geometry cluster total weight one by assigning each of its valid
ticks weight `1 / number_of_valid_ticks_in_that_cluster`. Compute weighted
ROC-AUC by trapezoidal interpolation after grouping tied scores; compute
precision-recall average precision as the step sum
`sum((recall_i-recall_(i-1))*precision_i)` after grouping tied scores. A curve
is unavailable if the pooled labels lack either class. Paired corridor/control
differences use the geometry seed as the pairing unit. Nearby frames are never
independent replicates.

## Allowed development tuning before R3

R2 freezes the simulation geometry/noise/bias profile, event/label thresholds,
screen limits, detector formulas, DCReg `kappa_th=10`, score definitions,
denominators, statistical intervals and run schedule. No LIO configuration,
simulator factor, outcome cutoff, DCReg threshold or per-scene setting may be
selected from development or held-out results. The two permitted post-R2
operating cutoffs are the separate global FAST-LIO and Point-LIO `G_3m`
thresholds, each selected only from its backend's development poses/scores
with the deterministic rule above. Lock the FAST-LIO cutoff at primary R3;
lock the separate Point-LIO cutoff with its replication development freeze.
Both locks must precede any held-out output exposure. The Point-LIO addition
is governed by D050 and does not revise the primary FAST-LIO sample size. The
half/double label tolerances are fixed sensitivity analyses, not candidates
for choosing a preferred headline.
T13 may make source-parity/correctness fixes only; any change affecting score
values requires a dated amendment and regeneration of all affected development
evidence before R3. T14 may implement the already frozen route/layout generator
and its tests but may not adjust factors after seeing LIO outcomes. Technical
retries follow the single-retry rule above and never create new independent
events.

## Uncertainty and planned splits

The proposed [split manifest](../data/SPLITS.csv) places v1/v2/v3 seed-10
attempts and v3 seeds 11–13 in one fixed-layout development cluster. It
reserves 32 randomized straight-corridor development layouts in a central
range (length 9–13 m, half-width 1.6–2.4 m). It reserves at least 12 held-out
layouts in each of four non-overlapping length/width strata (short/long ×
narrow/wide), with up to 20 per stratum if the development-only precision
rule requires expansion. Every event has a paired feature-rich control. No
held-out layout or output has been generated or inspected. Geometry
randomization and split enforcement remain T12/T14 implementation work.

The four-seed fixed-layout pilot gives an initial paired corridor-minus-control
1 s translation-median standard deviation of `0.162 m`; its seeds share one
geometry and do not determine the final count. For the 32 formal randomized
development seeds, define the interior as body positions with
`x in [L/4,3L/4)`, corresponding on the formal route to
`t in [3+(6+L/4)/0.8, 3+(6+3L/4)/0.8)`. Use integer-second candidate starts
inside that time interval and the primary non-overlapping 1 s windows. Each
of the 32 seed pairs must have at least five planned interior windows and all
of those windows valid in both corridor and control; if any pair fails this
coverage rule, do not substitute another seed or compute a favorable partial
variance—return to R2 with the failure evidence. For each scene, calculate the
median local translation error over those exact windows; for each geometry
seed calculate corridor median minus its paired control median. Compute
`s_dev` as the sample standard deviation with denominator `n-1` across the 32
independent geometry-seed differences. For target 95% confidence half-width
`h=0.10 m`, calculate `n_cont=ceil((1.96*s_dev/h)^2)`, round `n_cont` up to a
multiple of four, and set `n_test=max(48,n_cont)`.

Start with 12 eligible held-out geometry seeds per stratum; if `n_test` is
larger, add one seed per stratum per round in **ascending reserved seed order**
until the target count is reached. Apply the geometry-only screen before any
LIO replay; if a candidate fails, record it and try the next reserved seed in
that same stratum. If any stratum cannot supply its target by seed 119/139/159/
179, stop and return to R2; do not substitute from another stratum.
If `n_test > 80`, stop and return to R2 with a revised budget; do not inspect
held-out outputs to decide whether to expand.
For event-rate outcomes, 48 held-out events give a worst-case binomial 95%
half-width of about 14 percentage points. If the continuous-metric calculation
requires more than 48 held-out events, expand only before opening any held-out
outputs, up to the reserved maximum of 80. If it exceeds 80, return to R2 with
an amended budget rather than inspect outcomes.

For event proportions, report 95% Wilson score intervals on geometry-event
counts, pooled and separately by stratum. For continuous paired outcomes,
first compute each geometry seed's paired difference of the corridor and
control per-seed medians over the predeclared interior windows. The overall
point estimate is the unweighted mean of the four stratum-specific means;
report each stratum mean too. Other continuous per-seed summaries use the same
two-stage aggregation: median over that seed's planned valid windows, then
mean across seeds within each stratum, then equal-weight mean of the four
stratum means. Use 10,000 stratified geometry-seed bootstrap
replicates with `numpy.random.Generator(numpy.random.PCG64(20260926))`, under
Python 3.12.14 and NumPy 2.5.3. In fixed order
`short_narrow`, `short_wide`, `long_narrow`, `long_wide`, draw exactly `n_h`
geometry seeds with replacement from each stratum's ascending selected-seed
list (`n_h` is the selected geometry count for that stratum, equal across
strata), preserving each seed's corridor/control pair. Recompute the same
equal-stratum mean and event-weighted ROC/AP statistics in every replicate.
Report 2.5th/97.5th percentiles using NumPy `method="linear"`. This estimates
uncertainty conditional on these four
fixed design strata, not a population of arbitrary corridor types.

The final confirmatory analysis requires all planned `n_test` geometry pairs
to have complete corridor/control runs and usable primary interior windows.
After the single technical retry, any failed pair remains in the ledger and is
not replaced; report completion and successful-run summaries as descriptive
only, with no confirmatory interval/claim under the planned sample size. If a
ROC/AP bootstrap replicate contains only one truth class, its curve statistic
is undefined; if any of the 10,000 replicates is undefined, mark that curve's
confidence interval `UNAVAILABLE` and report the undefined-replicate count
rather than silently dropping it. The four strata remain within
straight-corridor topology; no transfer claim to different topologies, stairs,
natural scenes or real buildings is permitted. Repeated noise/bias runs on the
fixed v3 layout do not count as new geometry events.

R2 freezes the recovery-label thresholds, DCReg `kappa_th=10`, healthy-state
debounce rule, timestamp/age rules, threshold-candidate set, selection
objective and test analysis before held-out IDs are generated. The
FAST-LIO threshold value itself is learned from randomized development outputs
by that frozen rule and locked at R3 before the held-out outputs are opened.
If development variance or the resource audit shows the planned sample cannot
estimate the stated outcomes, return to R2 with an amendment rather than
examining test scores to tune the protocol.

## Numerical safeguards

- Clamp only the `acos` argument to `[-1,1]`; do not clamp errors or replace non-finite values.
- Use `float64` for transform evaluation and retain integer nanosecond time.
- Normalize quaternions only after enforcing the data-contract norm tolerance; use quaternion sign equivalence in tests.
- Reject reflections (`det(R) <= 0`) and rotations outside a documented orthonormality tolerance.
- Store radians in artifacts even when a plot displays degrees.
- Report counts before summaries: planned, emitted, reference-associated, locally valid, alignment-valid, indicator-valid, reset-crossing, and unavailable by reason.

## Required implementation checks for T07

Independent fixtures must demonstrate:

1. identical trajectories give zero local and accumulated error;
2. a known translational and rotational increment produces the analytic relative error;
3. a constant rigid change of estimator world frame does not affect relative error and is removed by the one fixed accumulated alignment;
4. quaternion sign flips do not change rotation error;
5. a reset/segment change invalidates crossing windows and is never re-aligned away;
6. reference gaps, long brackets, extrapolation, and ambiguous duplicate timestamps produce named unavailable reasons;
7. metric scale error remains visible because no scale fit occurs.
