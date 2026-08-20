# GPS-Denied Drone Navigation and Safe Landing

A simulation-first design project exploring LiDAR/depth-based autonomous navigation and safe landing-zone detection for a drone operating without reliable GPS.

> **Academic scope:** This is a three-person, third-year, three-credit university design project. The goal is a credible, measurable prototype—not a competition-grade autonomous aircraft.

## Project idea

The system will use synthetic terrain and simulated depth or LiDAR observations to:

1. analyze local terrain geometry;
2. identify and rank safe landing regions;
3. support navigation in a GPS-denied environment; and
4. progressively add localization and mapping capability where time permits.

The first implementation is intentionally geometry-first. It will estimate properties such as slope, roughness, clearance, and usable area directly from terrain or point-cloud data before introducing learned models or a full flight stack.

## Proposed pipeline

```text
Synthetic terrain / depth data
            |
            v
   Pre-processing and filtering
            |
            v
 Geometry-based terrain analysis
 (slope, roughness, clearance, area)
            |
            v
 Candidate landing-zone scoring
            |
            v
 Ranked safe landing locations
            |
            v
 Navigation/localization integration
        (progressive extension)
```

## Scope

### Core deliverable

- Generate or load synthetic terrain/depth data.
- Analyze terrain using explainable geometric criteria.
- Detect, score, and visualize candidate landing zones.
- Evaluate results with repeatable quantitative metrics.
- Demonstrate the pipeline in simulation.

### Progressive extensions

- Local obstacle-aware path planning.
- LiDAR/depth odometry or a lightweight SLAM pipeline.
- Closed-loop navigation to a selected landing zone.
- Integration with ROS 2, PX4, and Gazebo if schedule and compute resources allow.

ROS 2, PX4, and Gazebo are optional later-stage tools, not prerequisites for proving the core terrain-analysis concept.

## Success criteria

The prototype should be evaluated using measurable outcomes rather than only visual demonstrations. Candidate metrics include:

- safe/unsafe landing classification precision, recall, and F1 score;
- landing-zone localization error;
- false-safe rate, treated as a safety-critical metric;
- minimum obstacle clearance and accepted slope/roughness limits;
- processing time per terrain frame or point cloud;
- navigation success rate and collision rate, if navigation is implemented; and
- trajectory or map error, if SLAM is implemented.

See [docs/EVALUATION.md](docs/EVALUATION.md) for the proposed evaluation protocol.

## Planned repository structure

```text
.
├── README.md
├── docs/
│   ├── PROJECT_CONTEXT.md
│   ├── ROADMAP.md
│   └── EVALUATION.md
├── data/              # generated or sample terrain data (later)
├── src/               # implementation (later)
├── tests/             # automated checks (later)
└── results/           # plots, tables, and experiment summaries (later)
```

## Project status

The repository currently contains a complete project definition and execution handbook. Implementation has **not started yet**: there is no terrain generator, detector, simulator integration, or measured result in the repository today.

The immediate next milestone is an executable Python baseline that generates deterministic synthetic terrain, calculates geometric safety layers, selects landing candidates, and exports visual and numerical results. See [docs/CURRENT_STATUS.md](docs/CURRENT_STATUS.md) for the verified status and [docs/EXECUTION_PLAN.md](docs/EXECUTION_PLAN.md) for the build sequence.

## Relationship to VERGE-CUAS

This university design project is **separate from VERGE-CUAS**. Any overlap in general UAV concepts does not imply shared scope, deliverables, ownership, or competition objectives.

## Documentation

- [Project context and boundaries](docs/PROJECT_CONTEXT.md)
- [Current status and definition of done](docs/CURRENT_STATUS.md)
- [System architecture and module contracts](docs/ARCHITECTURE.md)
- [End-to-end execution plan](docs/EXECUTION_PLAN.md)
- [Phased roadmap](docs/ROADMAP.md)
- [Evaluation plan](docs/EVALUATION.md)
- [Development setup and operating commands](docs/SETUP.md)
- [Task backlog and milestones](docs/TASKS.md)
- [Decision log](docs/DECISIONS.md)
