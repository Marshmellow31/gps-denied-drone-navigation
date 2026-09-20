# Development Setup

This page documents the working standalone baseline. ROS 2, PX4, and physical sensors are intentionally not required.

## Current reality

The repository contains an installable Python package, tests, a command-line runner, a five-family benchmark, and a Colab-oriented notebook. The current Windows development machine passed the commands below on Python 3.13.7. The deployment target remains Raspberry Pi OS/Python 3.11-class and must be tested separately.

## Target prerequisites

- Git.
- Python 3.11 or another version selected and pinned during the machine audit.
- A Python virtual environment.
- Sufficient disk space for generated terrain and experiment outputs.
- Optional later: ROS 2, Gazebo, and PX4 development dependencies.

A GPU is not expected to be required for the geometry-first baseline.

## Quick start

```bash
git clone https://github.com/Marshmellow31/gps-denied-drone-navigation.git
cd gps-denied-drone-navigation
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

On PowerShell, activate with `.\.venv\Scripts\Activate.ps1`. If local policy blocks activation, invoke `.\.venv\Scripts\python.exe` directly.

## Working operating commands

```bash
# Run one deterministic hardware-constrained scenario
python -m gps_denied_landing.cli run \
  --scenario flat_obstacles --seed 2000 \
  --output results/generated/example --plot

# Run the frozen held-out seed range
python -m gps_denied_landing.cli benchmark \
  --seeds 20 --seed-start 2000 \
  --output results/generated/held-out
```

## Checks

Working now:

- four deterministic unit/integration tests;
- one-scenario diagnostic output; and
- multi-seed tuning and held-out benchmarks.

Still to be added: formatting, linting, type checking, clean-checkout CI, and a Pi Zero 2 W benchmark command that records RSS, temperature, and throttling.

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
