# Four-seed fixed-layout sensitivity check

26 September 2026. **Development-only; one geometry layout.** This follows
the seed-10 v3 pilot with three more paired FAST-LIO runs using the same
straight corridor/control geometry and different LiDAR noise, IMU noise and
bias realizations. It estimates run-to-run variation within this model; the
four seeds are not four independent scene layouts.

The per-run inputs, outputs, source hashes and summaries are in the
[machine-readable manifest](simulation_seed_sensitivity_manifest.json).
Raw sensor bags and replay outputs remain under ignored
`experiments/generated/`.

## Checks and descriptive results

All four corridor/control pairs contain 400 LiDAR scans and 8,021 IMU
messages each; serialized IMU streams match exactly within each pair. Every
FAST-LIO run has 400 accounted diagnostic groups (397 valid, three startup
unavailable), 397 poses and 794 local-motion rows (754 valid, 40 incomplete,
zero reference gaps). Both health exports passed the schema/numeric audit and
each trajectory evaluation passed reference hash and time/frame checks.

The table summarizes medians **within each seed**, then reports the mean and
spread across four seeds. The screening cutoffs `0.20 m` and `5 degrees` are
borrowed from DCReg's pairwise registration success definition and are used
here only as a proposed local-window screen; they are not a calibrated
recovery rule.

| Layout period | Corridor 1 s translation median (mean ± SD across seeds) | Control 1 s translation median (mean ± SD) | Seeds with any 1 s windows passing both cutoffs, corridor/control |
| --- | ---: | ---: | ---: |
| Before, 5–8 s | 0.123 ± 0.068 m | 0.097 ± 0.073 m | corridor: 53–100%; control: 50–100% |
| Inside, 14–20 s | 0.943 ± 0.187 m | 0.882 ± 0.030 m | 0/4; 0/4 |
| Extended after, 28–36 s | 0.031 ± 0.013 m | 0.022 ± 0.013 m | corridor: 85–100%; control: 100% |

Inside the corridor, the paired corridor-minus-control median-error difference
averages `0.061 m` but ranges from `-0.036` to `0.302 m` across seeds. The
feature control therefore does not produce a consistent reduction in motion
error for this layout. The scene-only ray audit still finds fewer x-facing
returns in the corridor, so the geometric contrast is present while its
translation-error effect varies with the sensor/bias draw. The online
information score also varies substantially across seeds. These are reasons
to test indicator reliability and availability, not evidence of a stable
causal advantage.

All four seeds pass the joint local-error screen in most extended post-exit
windows; that does not establish that an online indicator identifies the
right onset. The indicators have not yet been scored against the final
hindsight label or decision-delay metrics.

## Reproduction

The exact retained v3 runs are `SIM40_v3_{corridor,control}` and
`SIM40_v3_seed{11,12,13}_{corridor,control}`. Each input directory is
`sim-recovery-{dev,control}{seed}-v3`. Recreate them using:

```bash
for seed in 11 12 13; do
  ROS_ENV/bin/python research_paper/experiments/src/write_simulation_bag.py \
    --output research_paper/experiments/generated/simulation_bootstrap/sim-recovery-dev${seed}-v3 \
    --duration 40 --seed "$seed"
  ROS_ENV/bin/python research_paper/experiments/src/write_simulation_bag.py \
    --output research_paper/experiments/generated/simulation_bootstrap/sim-recovery-control${seed}-v3 \
    --duration 40 --seed "$seed" --control
done
```

Replay, input audit and trajectory evaluation run sequentially per seed pair:

```bash
for seed in 11 12 13; do
  bash research_paper/experiments/run_simulation_smoke.sh \
    ROS_ENV PATCHED_WORKSPACE \
    research_paper/experiments/generated/simulation_bootstrap/sim-recovery-dev${seed}-v3/sensors.bag \
    research_paper/experiments/generated/runs/SIM40_v3_seed${seed}_corridor
  bash research_paper/experiments/run_simulation_smoke.sh \
    ROS_ENV PATCHED_WORKSPACE \
    research_paper/experiments/generated/simulation_bootstrap/sim-recovery-control${seed}-v3/sensors.bag \
    research_paper/experiments/generated/runs/SIM40_v3_seed${seed}_control
  ROS_ENV/bin/python research_paper/experiments/src/audit_paired_simulation_bags.py \
    --corridor research_paper/experiments/generated/simulation_bootstrap/sim-recovery-dev${seed}-v3/sensors.bag \
    --control research_paper/experiments/generated/simulation_bootstrap/sim-recovery-control${seed}-v3/sensors.bag \
    --expected-scans 400 --expected-imu 8021
done
```

For each run, `trajectory_eval.py` used its corresponding `reference.txt`,
`simulation_motion_v3_reference_metadata.json`, and
`--alignment-target-ns 1005000000000`; `audit_health_export.py` was run on
each health CSV. The manifest records each input and output hash.

The summary is reproduced by:

```bash
python3 research_paper/experiments/src/summarize_simulation_seed_sensitivity.py \
  --seeds 10,11,12,13 \
  --output-json NEW_SUMMARY.json
```

`NEW_SUMMARY.json` must not already exist; the summarizer refuses to overwrite
previous output.

After the randomized-layout code was added, the current `fixed_v3` generator
was rerun for the seed-10 corridor and matched-control inputs. Both generated
sensor-bag hashes and both reference hashes exactly match the retained input
manifests. The original source hashes in the manifest are preserved as the
versions recorded when the four-seed artifacts were generated; the manifest
also records the current generator hashes and the limited seed-10 reproduction
check. This confirms the legacy fixed-scene path for seed 10, not a fresh
replay of seeds 11–13 or a new FAST-LIO result.

This pilot cannot estimate between-layout variation or publishable
uncertainty. T11 uses it only as an initial variability check. One randomized
development layout (seed 14) has since been smoke-tested in
[SIMULATION_RANDOM_LAYOUT_SMOKE.md](SIMULATION_RANDOM_LAYOUT_SMOKE.md); the
remaining development geometry draws and all held-out strata in
[`SPLITS.csv`](../data/SPLITS.csv) remain ungenerated. R2 must approve the
protocol before a batch.
