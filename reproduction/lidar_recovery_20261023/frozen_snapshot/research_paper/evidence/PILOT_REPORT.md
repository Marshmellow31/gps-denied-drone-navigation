# Development transition pilot — not a recovery finding

26 September 2026. The aligned timeline uses the final T08 drained replay,
its actual online diagnostic, and an offline evaluation of that same pose
stream. See [T08 provenance](T08_FINAL_PATCH_AUDIT.md) and the frozen
[LiDAR-only event](../data/HILTI_EXP18_EVENT.md).

![Development timeline with unavailable reference clearly shown](../figures/exp18_health_error_pilot.png)

The top panel is measurement-only smallest information eigenvalue at 3 m
lever scale, shown logarithmically, not a health threshold. The next panels
are 1 s local translation and rotation errors. The final panel uses one
fixed pre-exit alignment at 25 s, not repeated alignment or pre-entry drift.
Gold marks the independently annotated 31.6–33.6 s scene exit. Grey marks
unavailable data; line segments never bridge those rows.

There are 547 pose starts, 423/547 valid 1 s windows and 345/547 valid 3 s
windows. The prespecified matched post-exit bin remains only **13/56**
valid 1 s windows and **0/56** valid 3 s windows. No sustained recovery
label, false-reassurance score, or detection delay can be inferred.
The reference partly comes from LiDAR-to-map registration and is not
independent truth. One handheld recording cannot validate drones or scene
transfer. This is a failed feasibility/availability pilot, not a passed
original recovery pilot gate.

Reproduce after the replay in the T08 audit, from repository root:

```bash
python3 research_paper/experiments/src/trajectory_eval.py \
  --poses RUN_DIR/poses.csv \
  --reference /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2_imu.txt \
  --body-transform-json research_paper/data/hilti_exp18_reference_metadata.json \
  --development-only --event-id HILTI_EXP18_EXIT_NEAR_TO_OPEN \
  --alignment-target-ns 1649856252623466000 --run-id T08_drained_on55 \
  --output RUN_DIR/evaluation.csv
python3 research_paper/experiments/src/plot_transition_pilot.py \
  --health RUN_DIR/health.csv --evaluation RUN_DIR/evaluation.csv \
  --output research_paper/figures/exp18_health_error_pilot.png
```

`RUN_DIR` is the retained ignored `experiments/generated/runs/T08_20260926/drained_on55`.
Plot dependency: Pillow 12.1.1. Figure inspected visually; axis labels were
corrected to avoid overlap. Data credit: Hilti-Oxford 2022, CC BY-NC-SA 3.0.
