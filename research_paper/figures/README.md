# README figure provenance

These two small figures are derived from the official [Hilti-Oxford 2022 Exp18 Corridor Lower Gallery 2 recording](https://hilti-challenge.com/dataset-2022), credited to its authors under [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/). They are illustrations of **development data**, not evaluated recovery results. The full 8.66 GB source bag and reference text are not committed; their checksums and retained local paths are in [the actual-file inspection](../data/HILTI_EXP18_INSPECTION.md).

- `exp18_lidar_before_after.png` shows the actual LiDAR scans nearest +25 and +40 seconds after the first LiDAR header. Both top-down panels cover the same 30 m by 30 m square centred on the sensor. The displayed points require `-3 < z < 3 m` and `|x|,|y| < 15 m`; darkness is based on binned return count. The labelled 90th-percentile range uses all finite ranges in each selected scan, not just the displayed height slice. The two snapshots show different visible geometry but cannot establish odometry recovery or a precise event boundary.
- `exp18_data_timeline.png` uses the observed LiDAR span, the 789-row dense reference time span, its **five gaps longer than 0.5 s**, and the first 55 seconds of the retained FAST-LIO trial. White cuts depict only those larger gaps; smaller gaps may also invalidate an error window under the provisional 0.20 s rule. The 32–36 s gold interval comes from LiDAR-only scene inspection before any error/health analysis and remains tentative.

The deterministic generator is [`make_exp18_readme_figures.py`](../experiments/src/make_exp18_readme_figures.py), run with `rosbags==0.11.5`, NumPy and Pillow:

```bash
PYTHONPATH=/tmp/hilti_python python3 research_paper/experiments/src/make_exp18_readme_figures.py \
  PATH_TO_VERIFIED_EXP18_BAG PATH_TO_EXP18_IMU_REFERENCE research_paper/figures
```

The source data's [publisher page](https://hilti-challenge.com/dataset-2022) identifies the recording as handheld and provides the sensor and reference data. The [replay report](../data/HILTI_EXP18_REPLAY.md) explains why the 55-second run is a technical smoke test, not a scientific accuracy result.
