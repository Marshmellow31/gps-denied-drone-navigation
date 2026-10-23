# End-to-end simulation feasibility pilot

26 September 2026. **Development-only, no recovery claim.** User-approved
simulation-primary scope is recorded in [the amendment](../SCOPE_AMENDMENT_SIMULATION.md).
Sensing assumptions and deliberately simplified motion are in
[SIMULATION.md](../protocol/SIMULATION.md).

![Matched development simulation timelines](../figures/simulation_bootstrap_timeline.png)

## What actually ran

Two 32 s sensor bags, each 320 timed rotating scans and 6,421 IMU messages,
were generated from one prescribed trajectory. Corridor and added-feature
control have identical noisy IMU messages, verified by reading both bags.
Only `/sim/points` and `/sim/imu` occur in either bag. Reference is a separate
file; FAST-LIO/diagnostic processes never read it.

Both pinned FAST-LIO runs completed, producing 317 poses and 320 diagnostic
groups each: 317 valid, one first-scan, one empty-undistorted and one map-init.
The exporter schema/numeric audit passed for both. Both offline evaluations
contain 634 rows; 594 local-valid and 40 cutoff-incomplete windows, zero
reference gaps. No run disappeared and no unavailable value became zero.
Exact truth is independent of estimator computation, **not physical evidence**.

| Descriptive bin | Corridor 1 s translation median | Control 1 s translation median | Valid starts in each |
| --- | ---: | ---: | ---: |
| 5–8 s, pre-corridor | 0.02980 m | 0.01144 m | 30/30 |
| 14–20 s, interior | 0.11359 m | 0.02371 m | 60/60 |
| 25–28 s, post-corridor | 0.10245 m | 0.01163 m | 30/30 |

All these bins also have complete 3 s-window reference. They were defined
from layout/motion before summary inspection. No recovery tolerance, healthy
threshold, reassurance rate or delay has been chosen from these values.
Adjacent frames are not independent replicates; one seed gives no
generalization uncertainty or publishable effect estimate.

A separate scene-only ray audit, with no backend/error input, finds at 17 s
5.625% x-normal hits in the corridor versus 16.094% in the control. It supports
reduced axial geometric clues, not complete rank deficiency or a health label.
The body crosses layout boundaries at 9.25/24.25 s; distant features may be
visible beforehand. Top-panel smallest eigenvalues do not simply rise when
the body leaves the corridor; do not assume they encode local accuracy.

## Reproduction, provenance and cost

Use commands in SIMULATION.md for both `--seed 10` inputs, with `--control`
for the second; `run_simulation_smoke.sh` replays them sequentially. Evaluate
each with `trajectory_eval.py`, `--body-transform-json
research_paper/data/simulation_bootstrap_reference_metadata.json`,
`--development-only`, and `--alignment-target-ns 1005000000000`.
Then run `summarize_simulation_bootstrap.py RUN_DIR` and:

```bash
python3 research_paper/experiments/src/audit_simulation_scene.py
python3 research_paper/experiments/src/plot_simulation_bootstrap.py \
  --corridor CORRIDOR_RUN_DIR --control CONTROL_RUN_DIR \
  --output research_paper/figures/simulation_bootstrap_timeline.png
```

Retained inputs/logs/manifests are in ignored
`experiments/generated/simulation_bootstrap/sim-recovery-{dev10,control10}-v2/`.
Each bag is 40,657,955 bytes and generation took about 0.8–0.9 s.
Replay wall times: 43.64/43.60 s including startup/shutdown; observed largest
child-process RSS 188,532/188,280 KiB, not combined process-tree memory.
Python 3.12.14, NumPy 2.5.3 in the existing isolated ROS environment.
Backend revision and patches are unchanged from the T08 audit.
The generator manifests retain bag/reference/source hashes and dirty state;
reviewed output hashes are in [the pilot manifest](simulation_bootstrap_manifest.json).

Tests: 36 passed, one SciPy-dependent older scene test skipped (37 executed);
six new independent simulator fixtures passed. Script syntax and repository
whitespace checks passed. Figure inspected visually.

## Attempts retained, limits and next work

`sim-recovery-dev10` v1 successfully replayed but used a shared noise generator;
the v1 control was generated, not replayed. These are superseded for paired
comparison, not failed/crashed runs. v2 separated noise streams and draws
range noise per emitted ray before visibility masking; actual IMU parity passed.

This bootstrap has axis-aligned surfaces, ideal clocks, zero biases, collocated
sensors and yaw-only motion. Room/corridor shoulder gaps are currently open
surfaces, not a fully closed architectural model. Do not infer real-building
realism or tune geometry to produce a preferred failure. Before protocol freeze,
review closure/visibility, richer motion, bias/range models, enough post-exit
horizon, unseen layouts, faithful published comparator and repeatability.
No held-out data were generated or evaluated.
