# Development Setup

This is the intended setup contract. Commands will be finalized and tested when the Python package is added. Until then, this page distinguishes planned commands from commands that already work.

## Current reality

There is no executable application or dependency file in the repository yet. The commands below define the target developer experience; they must not be represented as working until Stage 1 is complete.

## Target prerequisites

- Git.
- Python 3.11 or another version selected and pinned during the machine audit.
- A Python virtual environment.
- Sufficient disk space for generated terrain and experiment outputs.
- Optional later: ROS 2, Gazebo, and PX4 development dependencies.

A GPU is not expected to be required for the geometry-first baseline.

## Planned quick start

The bootstrap stage will make an equivalent flow work:

```bash
git clone https://github.com/Marshmellow31/gps-denied-drone-navigation.git
cd gps-denied-drone-navigation
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

Windows activation instructions will be added if the target machine uses Windows.

## Planned operating commands

Exact flags may change during implementation, but the final interface should cover:

```bash
# Validate the local environment
gps-denied-landing doctor

# Generate a deterministic scenario
gps-denied-landing generate --config configs/scenarios/mixed.yaml --seed 42

# Run landing-zone detection and save diagnostics
gps-denied-landing detect --config configs/detector/baseline.yaml --scenario mixed --seed 42

# Run the reference evaluation suite
gps-denied-landing benchmark --suite configs/benchmark/core.yaml
```

## Expected checks

Stage 1 will define stable commands for:

- formatting;
- linting;
- type checking;
- unit and integration tests;
- a small smoke benchmark; and
- a full reproducible benchmark.

## Reproducibility requirements

Every experiment must save:

- code commit identifier;
- configuration snapshot;
- random seed;
- dependency/environment information;
- start time and runtime;
- input scenario identity;
- predicted outputs and metrics; and
- failure or warning messages.

Large generated datasets and bulk results should remain outside Git history unless a small artifact is deliberately selected as a reference result.

## Optional simulator setup

ROS 2, Gazebo, and PX4 instructions will live in a separate document after the standalone baseline works. Their versions must be pinned together because simulator, middleware, and autopilot compatibility changes over time.
