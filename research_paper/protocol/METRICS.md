# Provisional evaluation metrics

Version: development `0.1`, 22 September 2026. These definitions make T06–T09 implementable; numerical outcome thresholds and final aggregation are not frozen until T11/R2. Any development result must say **provisional**.

**Dataset update (24 September 2026):** The GEODE event and **pre-entry** anchor example below is not a Hilti protocol. Hilti's [exit-only scene interval](../data/HILTI_EXP18_EVENT.md) was fixed independently of estimator errors and indicators. The [T07 development pilot](../evidence/HILTI_EXP18_T07_PILOT.md) uses a separately named **pre-exit** anchor at 25 s; its accumulated error is not canonical pre-entry drift. Only 13/56 matched post-exit 1 s windows and 0/56 3 s windows have valid reference, so no sustained-recovery label exists. Keep invalid windows unavailable and do not infer a result from the surviving rows. See the [current handoff](../execution/CURRENT_HANDOFF.md).

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

### Provisional windows

- Primary development window: `tau = 1.0 s`.
- Secondary sensitivity window: `tau = 3.0 s`.
- End-pose selection tolerance: `±0.05 s` in the same pose segment.

At the roughly 10 Hz LiDAR/output cadence, one second spans about ten scans and tests useful short-horizon motion without reducing the 38.4 s post-nominal-exit reference horizon to only a few observations. Three seconds tests whether apparent recovery persists over a longer local interval. These are development settings, not evidence-derived final choices. T11 must assess motion magnitude, reference uncertainty, autocorrelation, and pilot variability before freezing them.

The denominator for each window is the number of candidate start timestamps for which a same-segment end timestamp should exist in the declared evaluation horizon. Report valid-window count and coverage fraction separately. Invalid windows never enter mean/median error as zeros.

## Fixed-alignment accumulated pose error

For development, choose an alignment anchor at the valid associated estimator pose nearest `entry_start - 5.0 s`, requiring an absolute time difference no larger than `0.05 s`. This places the anchor before the annotated geometry boundary and within independently covered reference for `UT01_TUNNEL2`. Define exactly once:

```text
T_G_W = T_G_B^r(t_anchor) * inverse(T_W_B^e(t_anchor))
T_G_B^aligned(t) = T_G_W * T_W_B^e(t)
E_acc(t) = inverse(T_G_B^r(t)) * T_G_B^aligned(t)
```

Translation and rotation error use the same norm and `SO(3)` angle definitions as above. This is an `SE(3)` alignment with scale fixed to 1.0. It is not recomputed at entry, exit, after a reset, or for each window. A reset/discontinuity remains visible under the original alignment or becomes explicitly unavailable if frame semantics are lost.

The single-anchor rule is transparent and avoids an underdetermined trajectory fit, but it is sensitive to one reference/estimate sample. T11 must compare a preregistered multi-pose rigid alternative on development data if needed; it may not choose the alternative from final-test outcomes.

## Provisional event horizons

For each transition, retain its annotated interval and nominal boundary. T09's development timeline should display at least:

- pre-exit context from 10 s before `exit_start` where sensor/pose data exist;
- the full exit interval `[exit_start, exit_end]`;
- post-exit evaluation through 30 s after `exit_nominal`, or to the last available stream/reference sample if earlier.

For `UT01_TUNNEL2`, quantitative truth-based output begins only when valid reference resumes at relative `243.870 s`; the earlier portion of the exit interval is visibly `REFERENCE_UNCOVERED`. No error is inferred through the 70.816 s tunnel gap.

## Recovery labels

A hindsight local-recovery label will mean that both local translation and rotation errors satisfy frozen tolerances for every valid evaluation window over a frozen sustained duration. It may look forward over that duration. The online indicator decision at time `t` may use only information available at or before `t`.

T05 intentionally does **not** assign translation/rotation tolerances, sustained duration, or minimum valid-window fraction. Those choices require T09 development error distributions, stated reference uncertainty, and T10 indicator semantics, and are assigned to T11. Until then:

- `recovery_label` is `null`;
- no false-reassurance rate or recovery-delay number is reported;
- plots may show raw indicator and raw errors but cannot label recovered/not-recovered regions.

Failure to produce enough truth-valid windows yields unavailable recovery, not recovered or unrecovered by assumption.

## Indicator decisions and association

Raw indicator values retain their native timestamp and semantics. A causal decision at evaluation time uses the most recent valid indicator sample at or before that time, subject to a method-specific maximum age declared before evaluation. No future sample may be used. T08/T10 must document whether a value describes a scan start, scan end, registration linearization, or state update.

Thresholds are development-only until frozen. A method that emits no decision is unavailable, not automatically unhealthy. Decision availability must accompany all reliability metrics so an always-silent indicator cannot appear safe.

## Metrics to freeze in T11

Subject to exact T11 definitions, the final protocol must include:

| Metric | Required interpretation / denominator |
| --- | --- |
| Local translation/rotation error | Raw per-window values plus event-cluster summaries; never pooled adjacent frames as independent replicates. |
| Accumulated translation/rotation error | Raw fixed-alignment values; descriptive outcome separate from local recovery. |
| Decision availability | Eligible online decision timestamps with a valid causal indicator decision divided by all eligible timestamps. |
| Truth-label availability | Timestamps/events with sufficient independent reference windows divided by all planned timestamps/events. |
| False reassurance | Healthy/recovered indicator decisions when the frozen truth label says local motion is not recovered; denominator and unavailable handling must be reported explicitly. |
| Recovery-detection delay | First sustained causal healthy decision relative to the independently annotated exit anchor or truth-recovery time, with the chosen definition stated. Non-detections are right-censored, not discarded. |
| Failure to recover | Explicit event outcome when truth never meets sustained recovery within the horizon. |
| Crash/reset/missing-output rate | Planned runs/events affected, reported separately and included in availability accounting. |

Operating points must be chosen on development data or by a preregistered false-alarm budget. Final-test thresholds cannot be tuned. Uncertainty is clustered by independent trajectory/event (and simulation seed/scene where applicable), never by treating nearby frames as independent samples.

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
