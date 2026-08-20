# System Architecture

## Design goal

Keep the core terrain-analysis pipeline independent of any simulator or autopilot. This allows fast development on ordinary arrays and point clouds, deterministic testing, and later adapters for ROS 2, Gazebo, or PX4 without rewriting the algorithms.

## Core data flow

```text
Scenario configuration
        |
        v
Synthetic terrain generator ------> noise-free ground truth
        |
        v
Sensor model (noise, dropout, range, density)
        |
        v
Terrain observation (height map / point cloud)
        |
        v
Pre-processing and local geometry
        |
        +--> slope layer
        +--> roughness layer
        +--> obstacle/clearance layer
        +--> observation-confidence layer
        |
        v
Safety fusion and footprint validation
        |
        v
Connected candidate regions and ranking
        |
        +--> selected landing target
        +--> safety/cost map
        +--> visual diagnostics
        +--> metrics and run manifest
```

## Proposed repository layout

```text
.
├── configs/
│   ├── scenarios/
│   └── detector/
├── data/
│   ├── samples/
│   └── generated/          # ignored; regenerated from configs and seeds
├── docs/
├── results/
│   ├── reference/          # small reviewed outputs safe to version
│   └── generated/          # ignored bulk runs
├── src/gps_denied_landing/
│   ├── cli.py
│   ├── config.py
│   ├── terrain.py
│   ├── sensor.py
│   ├── geometry.py
│   ├── candidates.py
│   ├── scoring.py
│   ├── evaluation.py
│   ├── visualization.py
│   └── io.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── pyproject.toml
└── README.md
```

The exact names can change during implementation, but responsibilities should remain separate.

## Module responsibilities

| Module | Responsibility | Must not own |
| --- | --- | --- |
| `config` | Validate scenario and detector parameters | Numerical algorithms |
| `terrain` | Generate terrain and noise-free truth | Sensor corruption |
| `sensor` | Simulate noise, dropout, sampling, and range | Safety labels |
| `geometry` | Compute normals, slope, roughness, and clearance | Final ranking policy |
| `candidates` | Apply footprint constraints and find connected regions | Simulator control |
| `scoring` | Rank valid regions using recorded weights | Ground-truth creation |
| `evaluation` | Compare predictions with truth and aggregate metrics | Parameter tuning during test evaluation |
| `visualization` | Produce overlays and plots from saved data | Recompute hidden results |
| `io` | Save/load arrays, configs, manifests, and metrics | Domain decisions |
| `cli` | Compose workflows into stable commands | Algorithm implementation |

## Canonical data conventions

- Use SI units: metres, seconds, radians internally, and degrees only for human-readable thresholds where clearly named.
- Use a right-handed Cartesian frame and document the chosen axis convention in code and saved metadata.
- Represent unavailable measurements explicitly, not as a valid zero height.
- Store the map resolution and origin with every grid.
- Store the random seed, source configuration, code version, and timestamp with every experiment.
- Give every safety layer the same shape and coordinate transform as its source observation.
- Separate continuous feature values from thresholded safe/unsafe masks.

## Initial algorithm baseline

1. Generate a 2.5D height map with flat, sloped, rough, stepped, and obstacle features.
2. Derive a noise-free ground-truth safe mask using the full landing footprint.
3. Simulate an observation by adding configurable noise, dropout, and sampling effects.
4. Estimate local surface normals or height gradients to obtain slope.
5. Estimate roughness from plane-fit residuals or local height variance.
6. Detect obstacles and expand them by the required drone clearance.
7. Erode the safe mask by the landing-footprint radius so that every accepted center supports the entire vehicle.
8. Label connected safe regions and remove regions below the required area.
9. Score remaining regions using safety margin, area, confidence, and optional distance cost.
10. Return the best target and save all intermediate layers for diagnosis.

## Extension boundaries

### Navigation

Navigation consumes the selected target and safety/cost map. It should not alter the detector's ground truth or silently relax safety constraints.

### SLAM

SLAM supplies estimated pose and map observations through an adapter. Evaluation should preserve simulator ground truth separately so localization error can be measured.

### ROS 2, Gazebo, and PX4

Adapters translate messages and coordinate frames at the repository boundary. Core geometry and scoring remain callable without ROS.

## Safety boundary

The initial system is a research prototype and must not command a physical aircraft. Any future physical-flight phase requires a separate hazard analysis, flight-test checklist, geofenced test site, human override, regulatory review, and explicit approval.
