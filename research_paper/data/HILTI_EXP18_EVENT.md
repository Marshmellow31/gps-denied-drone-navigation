# Hilti Exp18 exit-only scene event for development evaluation

Frozen 24 September 2026 **before viewing any FAST-LIO/reference error or health-indicator curve**. This is a scene-defined candidate transition, not a recovered/not-recovered truth label. It is handheld data, not a drone flight.

## Decision

The raw LiDAR range shift and [predeclared structural proxy](../protocol/HILTI_SCENE_STRUCTURE.md) both support a move from near/confined geometry to more varied visible surfaces. For **development T07 only**, freeze:

| Boundary | Seconds after first LiDAR header | Unix nanoseconds |
| --- | ---: | ---: |
| exit start | 31.6 | 1649856259223466000 |
| exit nominal | 32.6 | 1649856260223466000 |
| exit end | 33.6 | 1649856261223466000 |

The first LiDAR header is `1649856227623466000` ns. These boundaries bracket the observed range-p90 jump by 32.1 s, the strong fall in the fraction of returns under 3 m by 33.1 s, and the changing top-down structures through about 33.6 s. They were not shifted to fit backend performance. No pre-degeneracy *entry* is established: the recording appears already confined at its start. The event is therefore **exit-only**, and it cannot support a claim about accumulated drift from a pre-entry anchor.

## Structural evidence and limitations

The [scene-only range audit](HILTI_EXP18_SCENE_GATE.md) found the under-3 m fraction dropping from 0.958 at 30.099 s to 0.527 at 33.095 s. The structure script sampled the ten prespecified clouds at 26–30 and 35–39 s, with both 10 m and 20 m caps. Its complete per-cloud output is [versioned here](hilti_exp18_scene_structure.csv). Medians are descriptive, not ten independent trials:

| Proxy weakest eigenvalue | 10 m cap: before → after | 20 m cap: before → after |
| --- | ---: | ---: |
| translation-normal matrix | 0.0454 → 0.1206 | 0.0300 → 0.1372 |
| six-direction Jacobian, 1 m scale | 0.0318 → 0.0920 | 0.0271 → 0.0565 |
| six-direction Jacobian, 3 m scale | 0.00379 → 0.0347 | 0.00482 → 0.0531 |
| six-direction Jacobian, 5 m scale | 0.00136 → 0.0135 | 0.00174 → 0.0406 |

All six predeclared six-direction cap/scale comparisons increased after the transition. The synthetic plane test confirms the proxy gives a weak minimum direction for one plane and stronger diversity for three orthogonal planes. This supports a **candidate scene-geometry improvement**, not verified scan matching: there are no temporal correspondences, map residuals, backend weights or IMU priors in this proxy. Nearby scans are correlated. We do not claim the exact weak direction, a causal explanation of FAST-LIO accuracy, or that the scene supplies fully independent 6-DoF constraints.

## Evaluation boundary

Reference has a gap near 34.2–34.4 s; windows across it must remain unavailable. Use only the first 55-second development replay, the qualified IMU-body [reference metadata](hilti_exp18_reference_metadata.json), and the repaired T07 evaluator. The 1 s/3 s local errors are provisional. No recovery threshold or indicator comparison is frozen here. An optional fixed alignment at 25.0 s is a **pre-exit** anchor, not the study's canonical pre-entry drift anchor; label its accumulated error separately and do not merge it with GEODE or future pre-entry results.

Reproduce the structural check using Python 3.12, NumPy 2.2.6 and SciPy 1.15.3 in an isolated environment, with the Acer partition mounted read-only:

```bash
OPENBLAS_NUM_THREADS=1 PYTHONPATH=/tmp/hilti_structure_compatible \
  /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python \
  research_paper/experiments/src/audit_hilti_scene_structure.py \
  /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag
```

`/tmp/hilti_structure_compatible` is an ephemeral isolated install of those exact numerical packages; it must be recreated after reboot. The bag and backend outputs remain outside Git. The [X-ICP paper](https://arxiv.org/html/2211.16335v3) motivates the point-to-plane information proxy but does not validate this dataset-specific event.
