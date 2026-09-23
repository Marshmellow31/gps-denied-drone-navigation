# AGENTS.md

## Current repository scope (23 September 2026)

The active goal is now the LiDAR recovery-reliability study in `research_paper/RESEARCH_GOAL.md`. `research_paper/SCOPE_DECISION.md` supersedes the camera proposal and earlier broad recovery-policy recommendation. Prioritize the research contribution; use public LiDAR/IMU recordings and simulation, without requiring physical hardware. Cameras, navigation controllers and new full estimators are outside the current scope. The older guide below remains applicable to the archived prototype.

For the present checkpoint and exact next steps, read `research_paper/execution/CURRENT_HANDOFF.md`, then `research_paper/execution/STATUS.md` and `research_paper/AGENT_EXECUTION_PLAN.md`. The Hilti-Oxford Exp18 download, inspection and 55-second FAST-LIO replay are **development-only** evidence; no formal recovery result or final-test evaluation exists. The earlier GEODE runs remain documented failures. The manuscript still contains only a proposal abstract, not new experimental conclusions.

The original simulation-first safe-landing prototype was archived under `old_data/`. The guide **below this current-scope section** describes that archive: interpret its `src/`, `tests/`, `docs/`, `results/`, and package setup paths relative to `old_data/`, and run its commands from that directory. Its historical milestones and metrics do not establish results for the new research. Preserve its safety invariants and held-out seed restrictions when reusing it. `research_paper/PLAN_REVIEW.md` records earlier planning review, not the current task ledger.

This file is the working guide for coding agents in this repository. Read it before making changes. The repository is a university research prototype for GPS-denied drone safe-landing perception; it is not flight-ready software.

## Project at a glance

- **Repository:** `https://github.com/Marshmellow31/gps-denied-drone-navigation`
- **Package:** `gps-denied-landing` / Python module `gps_denied_landing`
- **Current version:** `0.1.0`
- **Language/runtime:** Python 3.10+; NumPy-only core; no GPU required
- **Entry point:** `gps-landing = gps_denied_landing.cli:main`
- **Stage:** hardware-constrained simulation baseline implemented; physical validation has not started
- **Project context:** three-person, third-year, three-credit university design project, independent of VERGE-CUAS

The central research question is whether inexpensive onboard distance sensing can find a safe landing location when GPS is unavailable. The implemented baseline generates synthetic terrain, simulates a low-cost multizone time-of-flight sensor and imperfect local pose, builds a local elevation map, computes explainable geometric safety layers, and returns either a footprint-safe target or an explicit no-target result.

Safe landing-zone detection is the core deliverable. Navigation, odometry/SLAM, ROS 2, Gazebo, PX4/ArduPilot integration, and physical flight are later, separately gated extensions.

## Non-negotiable boundaries

1. **Safety is asymmetric.** A false-safe location is worse than rejecting usable terrain. Preserve explicit `NO_SAFE_TARGET` behavior when evidence is missing, stale, or uncertain.
2. **Truth and observation stay separate.** Ground truth is derived from pristine synthetic terrain before sensor corruption. Never expose truth data to detector logic.
3. **Validate the full vehicle footprint.** A safe center alone is insufficient; slope, roughness, steps, clearance, localization margin, support area, and observation confidence all matter.
4. **Do not tune on held-out seeds `2000-2019`.** Seeds `0-49` are the v0.1 tuning partition. The held-out range is frozen evaluation evidence.
5. **Core algorithms remain simulator/autopilot independent.** Keep NumPy-domain logic free of ROS 2, Gazebo, PX4, vendor SDK, network, cloud, and GPU dependencies. Add integrations as boundary adapters.
6. **Use SI units internally.** Use metres, seconds, and radians unless a name explicitly says otherwise (for example, `max_slope_deg`). Preserve the documented local map origin and resolution.
7. **Missing data is not zero and is not safe.** Represent unavailable height with `NaN` and insufficient confidence explicitly.
8. **Do not claim deployment or flight safety from synthetic results.** Physical sensing, Raspberry Pi performance, positioning, failsafes, and controlled-flight validation are still outstanding.
9. **Do not command a physical aircraft from this prototype.** Future flight work requires a separate hazard analysis, geofenced site, human override, regulatory review, staged tests, and explicit authorization.
10. **Keep this project separate from VERGE-CUAS** in code, documentation, presentations, ownership, and claims.

## Architecture and data flow

```text
Scenario + seed
    -> pristine synthetic terrain
       -> independently computed truth-safe mask
    -> simulated 8x8 ToF observations + corrupted local pose
    -> bounded robot-centric elevation grid
       (height, confidence, sample count, resolution, origin)
    -> slope / roughness / local step layers
    -> thresholding + hazard dilation + confidence rejection
    -> full-footprint erosion + localization margin
    -> 4-connected safe regions
    -> deterministic candidate scoring
    -> selected target or no target
    -> arrays, manifest, plot, and evaluation metrics
```

The flight controller is intended to retain stabilization, arming, manual override, link-loss behavior, and final failsafes. A future companion-computer adapter may hand over only a validated, timestamped, short-lived target.

### Coordinate and map conventions

- Terrain is a 2.5D height grid (`GridMap`) with `height_m`, `resolution_m`, and `origin_xy_m`.
- Arrays use `[row, col]`; `x` derives from column and `y` from row.
- Cell centers are `origin + (index + 0.5) * resolution`.
- The repository documents a right-handed Cartesian frame requirement; preserve and record explicit frame metadata when adding adapters.
- All safety layers must share the source observation's shape and coordinate transform.
- Preserve continuous feature arrays separately from thresholded masks for diagnosis.

## Current hardware-constrained baseline

### Sensor and compute assumptions

- Downward-facing VL53L5CX-class direct-ToF sensor: 8x8 zones, 45-degree horizontal/vertical field of view, simulated at 15 Hz, maximum range 4 m.
- Ten-second raster survey at 1.5 m altitude accumulates 150 frames over a 1.6 m span.
- Simulated corruption includes range noise and quantization, dropout, outliers, XY pose error, pose random-walk drift, altitude error, attitude error, and yaw drift.
- Deployment floor: Raspberry Pi Zero 2 W-class computer (1 GHz quad-core Arm, 512 MB); no GPU.
- GPS-denied map accumulation assumes an external local pose estimate, ultimately from flight-controller IMU/barometer plus PMW3901-class optical flow and valid downward range.
- An LD19-class scanning-LiDAR adapter is the planned denser second profile. A TF-Luna-class single-point sensor may aid altitude/clearance but cannot be the sole terrain-safety sensor.

### Default model thresholds

Defaults live in `src/gps_denied_landing/models.py`; change them there and document/re-evaluate the consequences.

| Profile | Default |
| --- | ---: |
| Map resolution | 0.15 m |
| Vehicle footprint radius | 0.22 m |
| Clearance margin | 0.12 m |
| Localization margin | 0.10 m |
| Maximum physical slope | 8 degrees |
| Maximum physical roughness | 0.035 m |
| Maximum physical step | 0.080 m |
| Detector threshold safety factor | 0.60 |
| Minimum confidence | 0.18 |
| Minimum connected-region area | 0.01 m2 |
| Hole-filling passes | 3 |

The detector applies the safety factor to geometric thresholds, dilates hazards by the clearance margin, then erodes valid terrain by footprint radius plus localization margin. Candidate score weights are 0.45 clearance, 0.30 area, 0.20 confidence, and -0.05 normalized distance. Candidates sort by descending score, then row and column for deterministic ties.

### Terrain families

`src/gps_denied_landing/terrain.py` defines exactly these CLI choices:

- `flat_obstacles`: mostly level terrain with raised hazards;
- `mixed_slope`: a safe region beside a 14-degree slope;
- `rough_patch`: smooth and rough terrain in one scene;
- `step_and_pit`: step, depression, and raised obstacle;
- `no_safe_zone`: intentionally impossible landing scene.

Terrain generation and sensor simulation are deterministic for a fixed scenario and seed.

## Repository map and ownership

```text
README.md                              User-facing overview and quick start
pyproject.toml                         Package metadata, dependencies, CLI, pytest config
src/gps_denied_landing/
  models.py                            Dataclasses and all default profiles/configuration
  terrain.py                           Deterministic terrain families
  sensor.py                            Multizone ToF + pose-error simulation and interpolation
  geometry.py                          Feature layers, masks, connected regions, ranking
  evaluation.py                        Cell-classification and selected-target metrics
  pipeline.py                          End-to-end orchestration, timing, allocation tracking
  cli.py                               `run`/`benchmark`, persistence, optional plotting
tests/test_baseline.py                 Determinism and baseline safety regression tests
notebooks/01_hardware_constrained_baseline.ipynb
                                       Local/Colab interactive walkthrough
results/reference/                     Reviewed, versioned v0.1 evidence
results/generated/                     Ignored local experiment output
docs/                                  Architecture, status, setup, plans, decisions, backlog
```

Maintain separation of responsibilities. In particular, terrain owns pristine terrain, sensor owns corruption, geometry owns calculations and candidate policy, evaluation compares against truth, pipeline composes, and CLI handles user interaction/files. Do not move algorithmic decisions into CLI or visualization code.

Some files proposed in `docs/ARCHITECTURE.md` (`config.py`, `candidates.py`, `scoring.py`, `visualization.py`, `io.py`, config folders, and split test folders) do not exist yet. Treat that layout as a direction, not current reality.

## Setup and commands

Create an isolated environment before installing dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,plot]"
```

PowerShell activation is `\.venv\Scripts\Activate.ps1`; direct `\.venv\Scripts\python.exe` invocation is acceptable when activation is blocked.

Run the checks:

```bash
python -m pytest -q
python -m gps_denied_landing.cli --help
```

Run and plot one deterministic scenario:

```bash
python -m gps_denied_landing.cli run \
  --scenario flat_obstacles \
  --seed 2000 \
  --output results/generated/example \
  --plot
```

Reproduce the frozen five-family held-out benchmark:

```bash
python -m gps_denied_landing.cli benchmark \
  --seeds 20 \
  --seed-start 2000 \
  --output results/generated/held-out
```

The installed console script supports the same subcommands (`gps-landing run` and `gps-landing benchmark`). Plotting requires the `plot` extra; tests require the `dev` extra.

## Outputs and reproducibility

A single `run` writes:

- `manifest.json`: scenario, seed, complete sensor/vehicle/detector configuration, metrics, and selected candidate;
- `layers.npz`: terrain, observation, confidence, truth-safe mask, predicted-safe mask, slope, roughness, and step arrays;
- `diagnostic.png`: optional six-panel plot when `--plot` is passed.

A `benchmark` writes `runs.csv` and `summary.json`. Generated bulk output belongs under ignored `results/generated/`; commit only small, deliberately reviewed evidence under `results/reference/`.

For every meaningful experiment, retain the code revision, configuration, random seed, dependency/environment information, timestamp/runtime, scenario identity, predictions/metrics, and warnings/failures. Current manifests do not yet store all of these fields; improving provenance is valid work.

## Tests and change validation

The current suite has four tests covering terrain determinism, sensor determinism, rejection of the no-safe scene, and truth-safety of a baseline target. For changes:

1. Add focused tests for new or changed behavior.
2. Run the closest targeted test first, then `python -m pytest -q`.
3. For geometry or threshold changes, run tuning experiments on seeds `0-49`; never tune against `2000-2019`.
4. After freezing choices, run the full held-out benchmark and compare safety-critical metrics plus availability/recall.
5. Inspect diagnostic arrays/plots for representative failures; do not rely only on aggregate accuracy.
6. Update `docs/CURRENT_STATUS.md`, relevant decision/evaluation docs, and reference artifacts when a milestone or evidenced result changes.

Formatting, linting, static type checks, CI, and a clean-checkout verification workflow are not configured yet. Do not claim they exist. If introduced, document exact commands here and in `docs/SETUP.md`.

## Evaluation contract and accepted v0.1 evidence

Report at minimum precision, recall, F1, false-safe rate, valid selected-target rate, target availability, no-safe-scene rejection, runtime, and memory. Failed scenes and limitations must remain visible.

The checked-in held-out v0.1 suite is 100 runs: five scenarios x 20 unseen seeds (`2000-2019`). Its recorded results are:

| Metric | v0.1 held-out result |
| --- | ---: |
| Aggregate predicted-safe-cell precision | 100% |
| Aggregate false-safe-cell rate | 0% |
| Mean recall on safe scenes | 6.677% |
| Target availability on safe scenes | 56.25% |
| Target validity when produced | 100% |
| No-safe-scene rejection | 100% |
| Desktop detector p95 | 2.86 ms |
| Peak traced detector allocation | about 341 KiB |

Interpret these correctly: the baseline is conservative and rejects most usable cells. The results are synthetic; desktop detector timing excludes acquisition and is not Raspberry Pi evidence; traced detector allocation is not total process RSS.

The next algorithmic goal is an adaptive second survey that improves availability without weakening safety thresholds.

## Engineering gates and known gaps

Provisional airborne gates from ADR-001 are a map no larger than 64x64 cells, at least 5 Hz perception updates, detector p95 at most 200 ms on an actual Pi Zero 2 W, total process memory below 256 MB, no GPU/cloud/internet/ROS dependency in the core, and fail-safe rejection for stale data or excessive pose uncertainty.

Not yet implemented or validated:

- adaptive second-survey behavior;
- bright ambient light, low reflectivity, vibration, motion distortion, and stronger drift stress profiles;
- physical sensor calibration/log replay and LD19 adapter;
- Raspberry Pi latency, RSS, temperature, and throttling benchmark;
- formatting, linting, typing, CI, and fuller per-layer test coverage;
- navigation, odometry/SLAM, ROS 2, Gazebo, PX4, or physical-flight integration;
- material/semantic safety (water, grass, snow, weak roofing, and visually flat but unsupported surfaces).

Do not silently broaden scope into these extensions. Land the smallest measurable change that preserves the standalone core and its safety invariants.

## Documentation sources of truth

- `README.md`: public overview, quick start, baseline results, and repository map.
- `docs/CURRENT_STATUS.md`: what is demonstrably implemented and what remains.
- `docs/ADR-001-HARDWARE-CONSTRAINED-PIPELINE.md`: hardware assumptions, resource gates, and sensor alternatives.
- `docs/ARCHITECTURE.md`: data flow, module contracts, conventions, and extension boundaries.
- `docs/EVALUATION.md`: metrics and experiment protocol.
- `docs/DECISIONS.md`: accepted and open decisions.
- `docs/EXECUTION_PLAN.md`: gated implementation sequence and quality loop.
- `docs/ROADMAP.md`: phased scope from core through optional integrations.
- `docs/SETUP.md`: development environment and working commands.
- `docs/TASKS.md`: evidence-based backlog; note that its entry-point checkbox is stale because `cli.py` and the console script already exist, while an environment-doctor command does not.
- `docs/PROJECT_CONTEXT.md`: academic scope and project boundaries.

When documentation conflicts with executable code, inspect the code and checked-in artifacts, call out the mismatch, and update the relevant source rather than guessing. A task is complete only when implementation, tests, reproduction instructions, evidence, limitations, and status documentation agree.
