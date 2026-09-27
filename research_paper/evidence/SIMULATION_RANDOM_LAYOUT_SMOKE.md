# Randomized straight-corridor T12 smoke (development seed 14)

26 September 2026. **One randomized layout feasibility run; no paper finding.**
This run exercises T12's new layout-seeded geometry branch with the same
analytic motion and sensor model as v3. It uses one layout and one noise/bias
seed only. The full inputs, outputs, source hashes and audit counts are in the
[manifest](simulation_random_layout_manifest.json).

## Geometry and independent eligibility check

Seed 14 generated a 12.762 m corridor with half-width 2.335 m and room
half-width 5.213 m. The body crosses into the corridor at 9.25 s and exits at
25.202 s. The 60 s run gives 34.8 s after exit. Both doorways have closed
shoulders and a clear opening; the control adds four evenly spaced corridor
baffles while keeping the same layout and trajectory.

Before FAST-LIO ran, the scene-only ray audit checked the corridor midpoint
and the room five seconds after exit. Its predeclared limits were: at most 10%
x-facing returns in the degraded corridor, at least 15% in the paired feature
control at the same time, and at least 20% in the post-exit room. The measured
fractions were 5.97%, 19.97% and 21.74%, respectively. This verifies a
directional geometry contrast in this layout, not complete observability.

## Replay and truth checks

Each sensor bag contains 600 LiDAR scans, 12,021 IMU messages and only the two
sensor topics. The reference is separate. The serialized paired IMU streams
are identical. Each FAST-LIO run accounts for all 600 diagnostic groups: 597
valid and three startup-unavailable; each emits 597 valid poses. The offline
evaluator produces 1,194 rows per run, 1,154 valid, 40 incomplete and zero
reference gaps. Health schema and reference-hash audits pass.

As a **draft-rule check only**, using 0.20 m/5 degree per 1 s window (borrowed
from a registration-pair cutoff and not yet frozen by R2), 197/200 corridor
post-exit windows and 199/200 control windows pass both limits. All 200 3 s
windows per run pass the draft rate check. Three consecutive non-overlapping
1 s windows first pass at 26 s in both runs. These descriptive values do not
establish indicator reliability: the operating point is not fitted, the
outcome rule is still under review, and this is one layout/seed.

## Reproduction and limits

The source is the pinned FAST-LIO revision `7cc4175de6f8ba2edf34bab02a42195b141027e9`
with its existing health patch and simulation configuration. Python 3.12.14,
NumPy 2.5.3. Exact SHA-256 values, geometry settings and successful command
arguments are in the manifest. Raw bags and outputs remain under ignored
`experiments/generated/`; no held-out seed or layout was created.

The layout branch and its geometry-only screen passed analytic tests and this
one backend smoke. A scene-only audit screened all 32 development geometry
seeds 14–45 before estimator runs; all met the three eligibility limits.
The complete counts/ranges are in
[randomized_layout_geometry_screen_dev14_45.json](randomized_layout_geometry_screen_dev14_45.json).
Only seed 14 was turned into sensor bags and replayed; seeds 15–45 and all
reserved held-out ranges in [`SPLITS.csv`](../data/SPLITS.csv) remain
unreplayed.
The IMU model is not calibrated to physical hardware. R2 must review the full
layout generator, event qualification, outcome rule and storage/runtime plan
before a batch or held-out evaluation.
