# Hilti Exp18 scene-only gate: range change confirmed, recovery event not frozen

**Successor (24 September 2026):** The separate [prespecified structural audit and event record](HILTI_EXP18_EVENT.md) subsequently froze an **exit-only scene interval** for development T07. This earlier range-only gate is retained to show why distance alone was insufficient. Neither document freezes a recovered-odometry label.

24 September 2026. This check uses **LiDAR points only** from the publisher-hash-verified Exp18 bag. It did not read FAST-LIO poses, reference positions, indicators, or pose errors. It is a scene-annotation check, not a localization result.

The [reproducible range audit](../experiments/src/audit_hilti_scene_ranges.py) samples one cloud roughly every 0.5 s. It drops non-finite and <=0.2 m points, then measures the fraction of usable returns under 3 m and the 90th-percentile range. Representative rows from the 29.5–40.5 s audit, relative to the first LiDAR header:

| Relative time | Usable points | Fraction under 3 m | Range p90 |
| ---: | ---: | ---: | ---: |
| 30.099 s | 58,789 | 0.958 | 1.728 m |
| 31.598 s | 56,882 | 0.902 | 2.608 m |
| 32.098 s | 54,120 | 0.844 | 16.528 m |
| 32.599 s | 53,722 | 0.748 | 16.504 m |
| 33.095 s | 60,147 | 0.527 | 18.208 m |
| 35.597 s | 60,385 | 0.566 | 13.886 m |

The [versioned LiDAR before/after image](../figures/exp18_lidar_before_after.png) and a finer ignored local image grid agree that the scanner begins seeing substantially farther structure between about 31.6 and 33.1 s. This is stronger evidence for a **confined/near-to-more-open scene change** than the earlier broad 32–36 s visual guess. It does **not** prove that the earlier geometry was weak for scan registration or that later geometry restores 6-DoF observability: distance alone is not a Hessian/normal-direction analysis. The 34.2–34.4 s reference gap also limits potential truth windows.

**Gate decision:** Do not yet label or freeze this as a weak-to-rich *recovery* event. The scene-change time is a candidate only. Before event-anchored errors or indicator comparisons, inspect LiDAR-only structural diversity on both sides with a predeclared method, then either freeze a scene interval independent of outcomes or reject this candidate. Do not move an interval after seeing error or indicator peaks.

Reproduce the range check from the repository root with the Acer partition mounted read-only:

```bash
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python \
  research_paper/experiments/src/audit_hilti_scene_ranges.py \
  /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag \
  --start-s 29.5 --end-s 40.5 --step-s 0.45
```

The bag and any exploratory outputs stay outside Git. The small script and one synthetic range test are versioned. No final-test data were opened.
