# README figure provenance

## Current figure index — 12 October 2026

The [current research README](../README.md) embeds the corrected two-backend
development comparison, fresh primary-repeat exports, accepted final geometry screen and four complete final result plots. The sections below
preserve provenance for earlier figures.

| Figure | Source / provenance | Evidence boundary |
| --- | --- | --- |
| [Final operating points](final_geometry_v2_results_20261012/final_operating_points.png) | [Figure manifest](final_geometry_v2_results_20261012/manifest.json), [results](../evidence/final_geometry_v2_results_20261012/RESULTS_REPORT.md), [plotter](../experiments/src/plot_final_recovery_results.py) | Locked diagnostics: unconditional initial false-healthy, conditional recovery detection, detection-only median delay and horizon availability. Event Wilson 95% intervals; backend labels differ. |
| [Final group estimates](final_geometry_v2_results_20261012/final_stratum_events.png) | Same source exports and plotter as final operating points | 12 geometries per group. Scalar/fixed diagnostic event rates and Wilson intervals; recovery denominators vary by backend/group. |
| [Every final corridor event](final_geometry_v2_results_20261012/final_event_ledger.png) | [Event CSV](../evidence/final_geometry_v2_results_20261012/corridor_event_ledger.csv), same final analysis exports | All 48 geometries in both backends: recovery, relapse, initial false-healthy and detection. Grey endpoints are inapplicable, not successful detections. |
| [Final paired geometry effect](final_geometry_v2_results_20261012/final_paired_geometry_effect.png) | Frozen paired-difference analysis exports, same final plotter | Per-pair median interior translation error difference, then equal-group mean and 10,000 geometry-cluster bootstrap 95% interval. Group means shown without group intervals; no between-estimator superiority test. |
| [Accepted final geometry screen](final_geometry_screen_v2_20261012/final_geometry_screen.png) | [Manifest](final_geometry_screen_v2_20261012/manifest.json), [screen snapshot](../evidence/final_geometry_screen_v2_20261012.json), [plotter](../experiments/src/plot_final_geometry_screen.py) | 48 selected from 64 geometry checks; fixed criteria. No estimator results. |
| [Geometry repair candidate](geometry_revision_development_20261012/geometry_revision_development.png) | [Manifest](geometry_revision_development_20261012/manifest.json), [audit](../evidence/geometry_revision_development_20261012.json), [plotter](../experiments/src/plot_geometry_revision_dev.py) | Development ray geometry only; 32 fixtures per dimension group. This illustrated proposal subsequently passed R2/R3/native checks; it is not estimator evidence. PNG/SVG exports. |
| [Development signal comparison](development_signal_comparison_20261010/development_signal_comparison.png) | [Manifest](development_signal_comparison_20261010/figure_manifest.json), [corrected analysis](../evidence/DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md), [plotter](../experiments/src/plot_development_signal_comparison.py) | 32 corridor events per backend; backend-specific recovery labels, conditional false-healthy denominators and 95% Wilson intervals. Thresholds fitted on development data. |
| [Fresh repeat motion errors](primary_recovery_20261009/t14_repeat_motion_errors.png) and [warning disagreements](primary_recovery_20261009/t14_repeat_warning_disagreement.png) | [Manifest](primary_recovery_20261009/t14_repeat_figure_manifest.json), [fresh audit](../evidence/primary_recovery_repeatability_20261009.json), [plotter](../experiments/src/plot_repeatability.py) | Four repeats from two development layouts, not new independent events. |

The comparison and repeat sets include PNG/PDF/SVG. The earlier 12 October audit verified all nine export
hashes. Preserve these accepted exports. Reproduction into fresh directories
and the prioritized plan for missing figures are in the
[visual-documentation audit](../execution/RESEARCH_DOCUMENTATION_AUDIT_20261012.md).
The comparison's long footer needs better wrapping in a future reviewed
version. Older repeat exports below remain historical evidence.

## Historical Hilti illustrations

These two small figures are derived from the official [Hilti-Oxford 2022 Exp18 Corridor Lower Gallery 2 recording](https://hilti-challenge.com/dataset-2022), credited to its authors under [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/). They are illustrations of **development data**, not evaluated recovery results. The full 8.66 GB source bag and reference text are not committed; their checksums and retained local paths are in [the actual-file inspection](../data/HILTI_EXP18_INSPECTION.md).

- `exp18_lidar_before_after.png` shows the actual LiDAR scans nearest +25 and +40 seconds after the first LiDAR header. Both top-down panels cover the same 30 m by 30 m square centred on the sensor. The displayed points require `-3 < z < 3 m` and `|x|,|y| < 15 m`; darkness is based on binned return count. The labelled 90th-percentile range uses all finite ranges in each selected scan, not just the displayed height slice. The two snapshots show different visible geometry but cannot establish odometry recovery or a precise event boundary.
- `exp18_data_timeline.png` uses the observed LiDAR span, the 789-row dense reference time span, its **five gaps longer than 0.5 s**, and the first 55 seconds of the retained FAST-LIO trial. White cuts depict only those larger gaps; smaller gaps may also invalidate an error window under the provisional 0.20 s rule. The 32–36 s gold interval comes from LiDAR-only scene inspection before any error/health analysis and remains tentative.

The deterministic generator is [`make_exp18_readme_figures.py`](../experiments/src/make_exp18_readme_figures.py), run with `rosbags==0.11.5`, NumPy and Pillow:

```bash
PYTHONPATH=/tmp/hilti_python python3 research_paper/experiments/src/make_exp18_readme_figures.py \
  PATH_TO_VERIFIED_EXP18_BAG PATH_TO_EXP18_IMU_REFERENCE research_paper/figures
```

The source data's [publisher page](https://hilti-challenge.com/dataset-2022) identifies the recording as handheld and provides the sensor and reference data. The [replay report](../data/HILTI_EXP18_REPLAY.md) explains why the 55-second run is a technical smoke test, not a scientific accuracy result.

# 26 September simulation addition

`simulation_motion_v3_timeline.png` is generated by
`experiments/src/plot_simulation_bootstrap.py` from the paired 40-second
simulation runs. Teal and purple are the corridor and feature control; the
gold band marks when the simulated body is between x=0 and x=12 m. Panels show
the FAST-LIO information value, local 1-second movement and turn errors, and
position error after one fixed 5-second alignment. It is a single development
seed with synthetic truth, so it is not a recovery claim. Reproduction, units,
source hashes and limits are in [the v3 report](../evidence/SIMULATION_MOTION_V3.md)
and [manifest](../evidence/simulation_motion_v3_manifest.json).
# 26 September addition

`exp18_health_error_pilot.png` is generated by
`experiments/src/plot_transition_pilot.py` from actual final-patch diagnostic
and offline evaluator outputs. See `evidence/PILOT_REPORT.md` and
`evidence/exp18_pilot_manifest.json` for attribution, units, reproduction,
hashes and limitations. It is not a recovery result. Grey means unavailable,
gold marks the LiDAR-only scene exit; no error-derived transition is used.

# 27 September retained-repeat figures

`t14_repeat_motion_errors` and `t14_repeat_warning_disagreement` are saved as
PNG, PDF and SVG. They visualize only the four retained repeat comparisons
from two development layouts. Motion medians use 587 jointly valid 1-second
rows per comparison; warning disagreement fractions use 596 jointly available
decision ticks per comparison. Those correlated rows/ticks are not additional
independent events. Thresholds are fixed to the development candidate and the
published DCReg detector adaptation rule.

The source is [`t14_repeatability_audit.json`](../evidence/t14_repeatability_audit.json),
with definitions, reproduction and interpretation in the
[audit report](../evidence/T14_REPEATABILITY_AUDIT.md). The plotting script is
[`plot_repeatability.py`](../experiments/src/plot_repeatability.py).
[`t14_repeat_figure_manifest.json`](t14_repeat_figure_manifest.json) records
the input, script and all export hashes plus plotting-library versions.
Initial layout drafts are preserved under ignored
`experiments/generated/figure_drafts/t14_repeat_v1/`.
