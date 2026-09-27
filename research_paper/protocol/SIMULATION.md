# Simulation-primary feasibility model

Updated 26 September 2026. The user approved simulation as the primary evidence
route; the [scope amendment](../SCOPE_AMENDMENT_SIMULATION.md) allowed one T12
feasibility bootstrap before R1. R1 passed for protocol design only, and the
independent R2 review now passes for protocol content. The dated content/hash
bundle is [protocol/FREEZE.md](FREEZE.md). This does not implement the formal
x=-6 m route or authorize a final test; T14 still must implement/revalidate the
development generator and R3 must pass before any held-out generation/run.

The latest paired pilot is documented in
[SIMULATION_MOTION_V3.md](../evidence/SIMULATION_MOTION_V3.md), with its
machine-readable [manifest](../evidence/simulation_motion_v3_manifest.json)
and [timeline figure](../figures/simulation_motion_v3_timeline.png). Three
additional sensor seeds on the same fixed geometry are in the
[sensitivity follow-up](../evidence/SIMULATION_SEED_SENSITIVITY.md) and its
[manifest](../evidence/simulation_seed_sensitivity_manifest.json). Earlier
v1/v2 runs and their records remain preserved; v3 uses new run IDs.

## Scene and sensor model

Coordinates use a right-handed z-up world. The body points forward along x,
left along y, and up along z. Rooms cover x=-12..0 and x=12..30 m with
half-width 6 m; the corridor covers x=0..12 m with half-width 2 m. The floor
is z=-1 m and ceiling z=2 m. At both joins, opaque shoulder walls occupy
y=[-6,-2] and [2,6] m, leaving a 4 m opening y=[-2,2] m. The control scene
adds four partial-width baffles at x=2, 5, 8 and 11 m. Surface intersection
tests cover both shoulders and both doorway jambs. A ray audit shows fewer
x-normal returns in the corridor than in the control; this establishes a
scene contrast, not backend observability or a recovery label.

LiDAR and IMU are collocated with identity extrinsics. The generic LiDAR has
16 elevations from -15 to +15 degrees, 360 azimuth columns, a 10 Hz scan rate
and 0.1 s point-acquisition span. Each ray uses the pose at its acquisition
time. The nearest opaque rectangle wins; no-return rays are omitted. Gaussian
range noise has 0.01 m standard deviation. There is no reflectivity,
material, weather or intensity model.

IMU samples at 200 Hz. Ideal body specific force follows
`f_body = R_world_body.T @ (a_world - g_world)`, with
`g_world=(0,0,-9.80665) m/s^2`; body angular velocity comes from the analytic
ZYX attitude rates. The ROS orientation field is marked unavailable, so the
estimator does not receive truth attitude. Independent white-noise standard
deviations are 0.002 rad/s for gyro and 0.02 m/s^2 for acceleration. A
seeded per-axis initial bias uses standard deviations 0.003 rad/s and
0.03 m/s^2, followed by random-walk increments of 0.0001 rad/s/sqrt(s) and
0.001 m/s^2/sqrt(s). These are explicit development stress settings, not
measurements or calibration for a particular IMU. The realized bias path is
recorded in each input manifest. Paired scenes receive byte-identical IMU
messages, including bias and white noise.

## Prescribed motion

The body starts at x=-5 m, rests for 2 s, then follows a quintic smoothstep
speed ramp over 2 s to 0.8 m/s. It continues along a gently curved x/y/z path
with smooth roll, pitch and yaw. The path and attitude are analytic; the
specific-force and body-gyro streams are derived from their derivatives.
Sensors have ideal clocks and extrinsics. This improves on the earlier
yaw-only, piecewise-acceleration v2 model, but it remains one prescribed path,
not a model of pilot-driven or uncontrolled flight.

The body crosses x=0 at 9.25 s and x=12 at 24.25 s. Those are layout crossing
times, not instantaneous observability boundaries: rays can see through a
doorway before the body crosses it. The run lasts 40 s, giving 15.75 s after
the second crossing. Predeclared descriptive bins are 5–8 s (before), 14–20 s
(inside), and 28–36 s (extended after). Bins follow the scene and motion, not
the observed errors. They do not assign recovery.

## Inputs, truth separation and development split

`write_simulation_bag.py` writes `/sim/points` and `/sim/imu` to
`sensors.bag`; it writes a separate `reference.txt` containing the analytic
world-from-body pose in `xyzw` quaternion order. No reference topic or truth
file is opened by FAST-LIO or the online diagnostic. Seeds 10–13 are 40 s
realizations of the fixed v3 geometry; they are one geometry cluster, not four
independent scenes. Seed 14 adds one 60 s randomized straight-corridor layout
with a matched control. See the [seed sensitivity report](../evidence/SIMULATION_SEED_SENSITIVITY.md),
[random-layout smoke](../evidence/SIMULATION_RANDOM_LAYOUT_SMOKE.md) and
[split manifest](../data/SPLITS.csv). No held-out layout/seed has been
generated or inspected. Synthetic truth is independent of estimator
computation, but it is not a physical measurement.

Each 40 s fixed-layout seed processed 400 scans and 8,021 IMU messages per
scene. The 60 s randomized-layout smoke processed 600 scans and 12,021 IMU
messages per scene. All groups are accounted for; startup and cutoff windows
remain explicitly unavailable, with no reference gaps in either evaluation.
The [v3 report](../evidence/SIMULATION_MOTION_V3.md) and
[random-layout report](../evidence/SIMULATION_RANDOM_LAYOUT_SMOKE.md) contain
counts, scene-only audits, hashes and limits. Earlier v1/v2 attempts remain
preserved under the ignored generated-data area.

## R2-frozen T12 layout plan; T14 implementation pending

The held-out claim is limited to **unseen straight-corridor geometry
parameterizations**. This protocol does not claim transfer to a new topology,
natural environment or physical building. All layouts remain axis-aligned
boxes with the same 16-beam scan pattern and 3 m room height.

Each event uses its split seed as both `layout_seed` and `sensor_seed`; its
corridor and control share both. Geometry uses the deterministic layout stream
`default_rng(SeedSequence([layout_seed, 0x4C494441]))`. The sensor seed spawns
three separate NumPy streams in this fixed order: IMU white noise, LiDAR range
noise, and IMU bias/random walk. T14's input manifest must record the NumPy
version and seed/spawn-key mapping for all streams. Corridor length `L`,
half-width `w`, and room half-width are drawn
independently from the ranges below (room half-width 4.5–7.5 m). Geometry is
deterministic for a layout seed.
The corridor entry/exit planes are x=0 and x=L. Its side walls are y=±w;
room side walls are y=±room-half-width. Each doorway plane has shoulders over
`[-room_half_width,-w]` and `[w,room_half_width]`, leaving the doorway open.
The floor and ceiling remain z=-1 and z=2 m. The left room covers x=-12..0
and the right room x=L..50 m. A fixed five-baffle asymmetric pattern occupies
the rich rooms at x=-8,-2,L+3,L+7,L+12 m, alternating sides; each baffle spans
the outer 42–83% of the room half-width and z=-1..1.5 m. The matched feature
control adds four partial baffles at x=L/5, 2L/5, 3L/5, 4L/5, along the
positive corridor wall band y=0.65w..w, z=-1..1.5 m. Both runs use the same
layout, route, sensor timing and byte-identical IMU stream.

The current feasibility-smoke route starts at x=-5 m, so it crosses the entry
plane at 9.25 s and exits at `3 + (5 + L)/0.8` seconds. It is not long enough
to meet the final protocol's 10 s pre-entry context. T14 must add a named
formal route profile starting at x=-6 m, keeping the same rest, speed ramp and
smooth 3D motion shape. That profile crosses entry at 10.5 s and exits at
`t_exit = 3 + (6 + L)/0.8` seconds; the longest layout exits at 33 s. A 60 s
run then provides at least 27 s after exit. T14 must use this same formal
profile for every development and held-out layout, regenerate the development
split under new run IDs, and rerun the scene-only screen at the profile's
derived sample times. The earlier seed-14 smoke remains feasibility-only.

| Split | Corridor length L | Corridor half-width w | Geometry draws |
| --- | ---: | ---: | ---: |
| Development randomized straight | Uniform 9–13 m | Uniform 1.6–2.4 m | Seeds 14–45 |
| Held-out short/narrow | Uniform 8–9 m | Uniform 1.3–1.5 m | Seeds 100–119, minimum 12 |
| Held-out short/wide | Uniform 8–9 m | Uniform 2.5–3.0 m | Seeds 120–139, minimum 12 |
| Held-out long/narrow | Uniform 15–18 m | Uniform 1.3–1.5 m | Seeds 140–159, minimum 12 |
| Held-out long/wide | Uniform 15–18 m | Uniform 2.5–3.0 m | Seeds 160–179, minimum 12 |

Seed 10 and repeats 11–13 remain one fixed-layout development cluster. Each
geometry draw and its control share the same smooth 3D trajectory and the
same serialized IMU noise/bias stream. The generator records exact geometry
parameters and all RNG seeds. A final run lasts 60 s, providing at least 20 s
after the maximum planned exit time.

Before running FAST-LIO on a generated event, a **scene-only** ray audit will
count nearest-surface normal axes at the corridor midpoint and 5 s after exit:
the degraded scene must have at most 10% x-facing returns at its midpoint,
its feature-control pair at least 15%, and the post-exit room at least 20%.
The v3 scene met these limits at its audited points (5.94%, 18.11%, and at
least 25%). This is a geometry eligibility screen, not an estimator outcome.
Every rejected layout and reason remains in the ledger; thresholds are not
changed after looking at LIO scores or errors. If a split cannot supply the
planned number of eligible scenes, return to R2 rather than silently swapping
in favorable layouts.

The source currently implements the fixed v3 scene and the
`randomized_straight_dev` feasibility layout, plus the scene-only eligibility
audit. Seeds 14–45 all passed the screen for that feasibility profile; seed
14 alone has a 60 s sensor bag pair and FAST-LIO replay. T14 must repeat the
screen for the formal x=-6 m profile before replay. See
[the 32-seed geometry screen](../evidence/randomized_layout_geometry_screen_dev14_45.json)
and [the randomized-layout smoke](../evidence/SIMULATION_RANDOM_LAYOUT_SMOKE.md).
The four held-out width/length strata in [SPLITS.csv](../data/SPLITS.csv) are
reserved but not supported by the generator, generated or inspected. Their
implementation and all held-out work remain behind R2.

## Checks and reproduction

Twelve simulator fixtures cover known plane distance, parallel missing rays,
nearest-surface occlusion, finite bounds, closed portal shoulders and open
doorways, stationary specific force, smooth-ramp acceleration, full 3D pose
derivatives, seeded bias repeatability, scan timing and deterministic output.
The complete experiment suite reports 42 passed and one SciPy-dependent
scene test skipped (43 executed). The v3 and randomized-layout manifests record
the FAST-LIO runs, health exports,
reference hashes, topic isolation and paired IMU equality are checked in the
v3 evidence manifest. `audit_paired_simulation_bags.py` rechecks that each
bag contains only the two sensor topics and that serialized IMU messages match.

## Preliminary run budget

The planned study contains 32 paired randomized development geometry seeds and
48–80 paired held-out geometry seeds: 80–112 primary geometry pairs, or
160–224 primary FAST-LIO runs across both phases. **T14 runs only the 32
development seeds** under the formal x=-6 m route. After the scene-only screen,
repeat the first and last eligible development geometry seeds once with
identical sensor bags, configuration and backend build (four additional
FAST-LIO runs); use repeats only for backend-repeatability checks, never as
independent events or threshold-training records. The 48–80 held-out pairs are
for the final evaluation only after R3 PASS; do not generate or geometry-screen
those inputs during T14. Preserve both repeat outputs and compare
pose/health/evaluation hashes. The old fixed-v3 seeds and T12 seed-14 smoke are
not part of the formal development batch; all seeds 14–45 are regenerated
under the formal x=-6 m route. A 40 s bag is 53.8 MB per scene;
scaling the measured size by duration gives about 80.7 MB per 60 s bag. If all
inputs were kept, 80–112 paired events would use about 13–18 GB. A 40 s pair
was previously estimated at 1–2 min including startup/shutdown; scaling to 60 s
gives a planning estimate of 1.5–3 min per pair, or about 2–5.6 h sequentially
before audits/rebuilds. T14 must time the first formal pair and revise this
estimate before launching the batch.

Instead of retaining all raw bags, process one paired event at a time: the two
60 s input bags need about 162 MB of scratch, and each prior smoke output was
about 704 KB per run. On 26 September `/tmp` had 7.0 GB free, the workspace
filesystem 1.8 GB free, and the 104 GB-free Acer partition was read-only.
Regeneration with current code exactly matched the recorded seed-10 fixed-v3
and seed-14 randomized corridor/control bag and reference hashes. This supports
a one-pair scratch plan: keep a pair until input audit, replay, output audit and
manifest hashes pass; then discard only regenerable raw bags, retaining compact
outputs and manifests. Preserve failed inputs until diagnosed. T14 must check
free space before every pair and stop if projected output storage is
insufficient; it must not depend on the read-only Acer partition. Raw bags
stay outside Git.

Generate fresh development inputs using new empty output directories:

```bash
ROS_ENV/bin/python research_paper/experiments/src/write_simulation_bag.py \
  --output NEW_CORRIDOR_INPUT --duration 40 --seed 10
ROS_ENV/bin/python research_paper/experiments/src/write_simulation_bag.py \
  --output NEW_CONTROL_INPUT --duration 40 --seed 10 --control
bash research_paper/experiments/run_simulation_smoke.sh \
  ROS_ENV PATCHED_WORKSPACE NEW_CORRIDOR_INPUT/sensors.bag NEW_CORRIDOR_RUN
bash research_paper/experiments/run_simulation_smoke.sh \
  ROS_ENV PATCHED_WORKSPACE NEW_CONTROL_INPUT/sensors.bag NEW_CONTROL_RUN
ROS_ENV/bin/python research_paper/experiments/src/audit_paired_simulation_bags.py \
  --corridor NEW_CORRIDOR_INPUT/sensors.bag \
  --control NEW_CONTROL_INPUT/sensors.bag --expected-scans 400 --expected-imu 8021
```

Generate and audit one randomized development layout/control pair with new
empty output directories:

```bash
ROS_ENV/bin/python research_paper/experiments/src/write_simulation_bag.py \
  --output NEW_RANDOM_INPUT --duration 60 --seed 14 \
  --layout-family randomized_straight_dev --layout-seed 14
ROS_ENV/bin/python research_paper/experiments/src/write_simulation_bag.py \
  --output NEW_RANDOM_CONTROL --duration 60 --seed 14 \
  --layout-family randomized_straight_dev --layout-seed 14 --control
python3 research_paper/experiments/src/audit_simulation_scene.py \
  --layout-family randomized_straight_dev --layout-seed 14 --require-eligible
bash research_paper/experiments/run_simulation_smoke.sh \
  ROS_ENV PATCHED_WORKSPACE NEW_RANDOM_INPUT/sensors.bag NEW_RANDOM_RUN
bash research_paper/experiments/run_simulation_smoke.sh \
  ROS_ENV PATCHED_WORKSPACE NEW_RANDOM_CONTROL/sensors.bag NEW_RANDOM_CONTROL_RUN
ROS_ENV/bin/python research_paper/experiments/src/audit_paired_simulation_bags.py \
  --corridor NEW_RANDOM_INPUT/sensors.bag --control NEW_RANDOM_CONTROL/sensors.bag \
  --expected-scans 600 --expected-imu 12021
```

Run the offline evaluator once per run with its corresponding reference file:

```bash
python3 research_paper/experiments/src/trajectory_eval.py \
  --poses RUN_DIR/poses.csv --reference INPUT_DIR/reference.txt \
  --output RUN_DIR/evaluation.csv --run-id RUN_ID \
  --event-id SIMULATION_LAYOUT \
  --body-transform-json research_paper/data/simulation_motion_v3_reference_metadata.json \
  --development-only --alignment-target-ns 1005000000000
python3 research_paper/experiments/src/audit_health_export.py RUN_DIR/health.csv
python3 research_paper/experiments/src/summarize_simulation_bootstrap.py RUN_DIR
```

For the 60 s randomized input, use
`research_paper/data/simulation_random_layout_reference_metadata.json` with
the same evaluator arguments; its hash is tied to that 60 s reference file.

R2 protocol content and the hash bundle are complete. T13 implementation and
validation is next; T14 then implements the formal development generator and
runs only seeds 14–45 plus the two repeat pairs. The held-out parameter strata
are not implemented in the generator and must not be generated or screened
until R3 PASS and the final-evaluation handoff. No current development seed is
a final evaluation.
