# End-to-End Execution Plan

## Execution strategy

Build the smallest measurable system first, preserve reproducibility at every step, and add simulator complexity only after the standalone algorithm passes its acceptance gates.

The implementation agent can perform repository work, environment setup, coding, tests, experiment runs, plots, and documentation on the authorized laptop. The human project team remains responsible for academic decisions, access credentials, final scope approval, hardware safety, and submission.

## Working agreement for laptop access

When implementation begins, the agent will:

- inspect the available OS, hardware, installed tools, and repository state before changing anything;
- work inside the project directory and a project-specific virtual environment;
- preserve unrelated files and existing changes;
- use version control for every meaningful increment;
- record commands, dependencies, configurations, seeds, and results;
- run relevant tests after each change;
- report blockers and evidence, not hide failed experiments; and
- request explicit permission before destructive actions, external account changes, physical-device control, or scope expansion.

Full laptop access does not itself authorize deleting unrelated data, exposing credentials, spending money, publishing private information, or operating flight hardware.

## Stage 1 — Machine audit and project bootstrap

### Work

- Record OS, CPU, RAM, GPU, Python version, and disk availability.
- Confirm Git/GitHub access and clone or update the repository.
- Create a pinned Python environment and package skeleton.
- Add formatting, linting, type checking, unit testing, and GitHub Actions.
- Add a single `doctor` or equivalent command that validates the environment.

### Deliverables

- `pyproject.toml` and lock/pin strategy.
- Importable package and command-line entry point.
- Automated checks running locally and on GitHub.
- Updated setup instructions.

### Acceptance gate

A clean environment can install the project, run the command-line help, and pass all initial checks.

## Stage 2 — Deterministic terrain and ground truth

### Work

- Implement terrain primitives: plane, slope, mound/rock, step, pit, wall, and mixed scenes.
- Compose primitives from configuration files.
- Generate height maps with stored resolution, origin, parameters, and seed.
- Produce noise-free safe-region truth from explicit vehicle-footprint rules.
- Save compact sample scenes and render diagnostic images.

### Deliverables

- Terrain generator and configuration schema.
- At least five terrain families.
- Unit tests for dimensions, bounds, repeatability, and known safe/unsafe locations.

### Acceptance gate

Repeated runs with the same configuration and seed produce identical arrays and truth masks.

## Stage 3 — Sensor observation model

### Work

- Add Gaussian/range-dependent noise, missing pixels/points, and configurable resolution.
- Keep ground truth isolated from the corrupted observation.
- Add optional conversion between height-map and point-cloud representations.
- Test extreme cases: all missing, single obstacle, boundary obstacles, and sparse observations.

### Acceptance gate

Noise conditions are reproducible and do not leak ground truth into detector inputs.

## Stage 4 — Geometry-first detector

### Work

- Implement and test slope estimation.
- Implement and test roughness estimation.
- Implement obstacle detection and clearance expansion.
- Enforce full-footprint support and minimum connected area.
- Preserve every intermediate feature and rejection reason.

### Acceptance gate

Hand-constructed fixtures yield the expected slope, roughness, clearance, and safety masks within specified tolerances.

## Stage 5 — Candidate selection and scoring

### Work

- Label connected safe regions.
- Extract candidate centers and region statistics.
- Rank candidates with a documented weighted score and deterministic tie breaking.
- Reject the scene explicitly when no safe zone exists.
- Produce an overlay showing truth, predicted safety, candidates, and the selected target.

### Acceptance gate

Every chosen target has a fully valid footprint, and no-safe scenes return a safe failure instead of a fabricated target.

## Stage 6 — Reproducible benchmark

### Work

- Freeze tuning and evaluation scenario sets.
- Sweep thresholds only on the tuning set.
- Run multiple fixed seeds for every noise condition.
- Save per-run manifests and aggregate metrics.
- Generate final tables, plots, and a failure-case gallery.

### Acceptance gate

One command reproduces the reference benchmark and its summary files. False-safe performance is reported prominently.

## Stage 7 — Demonstration package

### Work

- Build a concise interactive or scripted demonstration.
- Add architecture, algorithm, result, and limitation explanations for the report/presentation.
- Test from a clean checkout.
- Tag a stable core release.

### Acceptance gate

Another team member can reproduce the demonstration using only the repository documentation.

## Stage 8 — Navigation extension

Begin only after the core release gate passes.

- Convert terrain safety into a traversability/cost representation.
- Implement or integrate a baseline planner.
- Simulate approach from multiple start states.
- Measure success, collision, clearance, path length, planning time, and landing error.

## Stage 9 — SLAM extension

Begin only if navigation is stable and the schedule remains healthy.

- Generate sequential observations and ground-truth trajectory.
- Integrate a suitable odometry or SLAM baseline.
- Measure trajectory and map error.
- Test how localization uncertainty changes landing performance.

## Stage 10 — Optional ROS 2 / Gazebo / PX4 integration

Use these tools only when they add demonstrable value:

1. wrap stable core modules as ROS 2 nodes;
2. validate transforms, timestamps, and message rates;
3. move the scenario into Gazebo;
4. add PX4 Software-in-the-Loop after sensing and planning work independently; and
5. retain a standalone mode for fast tests.

## Quality loop for every task

```text
Define expected behavior
        -> implement smallest change
        -> add/adjust tests
        -> run targeted checks
        -> run full relevant suite
        -> inspect visual/numerical output
        -> update status and documentation
        -> commit with reproducible evidence
```

## Stop/go rules

- Do not start SLAM while landing detection has unresolved false-safe failures.
- Do not add ROS 2 merely to make the architecture look sophisticated.
- Do not tune on the held-out evaluation scenarios.
- Do not report only aggregate accuracy; preserve safety-critical metrics.
- Do not start physical flight from this repository's simulation result alone.
- Prefer a complete, tested core result over several incomplete integrations.

## What the team must provide before implementation

- Academic deadline and review dates.
- Faculty requirements, mandatory tools, and grading rubric.
- Target laptop availability and any compute/storage limits.
- Agreed drone footprint, clearance, slope, and roughness assumptions—or approval to begin with documented provisional values.
- Preferred division of work and member names if ownership is to be recorded.
- Any required report, presentation, or demonstration format.

Missing values can begin as clearly marked assumptions, but they must be reviewed before the final benchmark.
