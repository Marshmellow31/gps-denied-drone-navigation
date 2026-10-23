# Project Context

## Summary

This is a three-person, third-year, three-credit university design project focused on autonomous drone operation in GPS-denied environments. Its practical center is safe landing-zone detection from LiDAR/depth-style terrain observations, with navigation and SLAM introduced progressively.

The design deliberately favors a small, defensible system that can be measured and demonstrated within an academic term.

## Problem statement

When GPS is unavailable or unreliable, a drone cannot depend on global position updates for navigation. It must instead interpret onboard observations to understand nearby terrain, avoid hazards, and select a safe place to land.

The project asks:

> Can simulated LiDAR/depth observations and explainable geometric terrain features be used to reliably identify safe landing regions, while providing a foundation for GPS-denied navigation?

## Design principles

### Simulation first

Development starts with reproducible synthetic terrain rather than physical flight hardware. Simulation reduces safety risk, makes ground truth available, and enables controlled testing across many terrain conditions.

### Geometry first

Initial landing-zone decisions will use interpretable features such as:

- local surface slope;
- surface roughness or height variance;
- obstacle presence and clearance;
- connected usable area;
- distance or reachability; and
- confidence or data density.

This baseline is easier to debug and evaluate than an end-to-end learned approach. Machine learning may be considered later only if it addresses a demonstrated limitation.

### Progressive autonomy

Safe landing-zone analysis is the core. Additional autonomy is layered in stages:

1. terrain generation and geometric analysis;
2. candidate detection and ranking;
3. obstacle-aware local navigation;
4. pose estimation or SLAM; and
5. optional flight-stack integration.

## System boundaries

### In scope

- Synthetic height maps, point clouds, or simulated depth/LiDAR data.
- Geometric terrain analysis.
- Safe landing-zone detection and scoring.
- Visualization and quantitative evaluation.
- A simulation-based demonstration.
- A progressive SLAM/navigation extension if the core system is stable.

### Not required for the core deliverable

- A competition-grade autonomous drone.
- Custom airframe or flight-controller hardware.
- Outdoor autonomous flight.
- Full production robustness across every sensor and environment.
- Deep learning as a prerequisite.
- Immediate ROS 2, PX4, or Gazebo integration.

## Candidate inputs and outputs

### Inputs

- Synthetic height map or 3D terrain mesh.
- Point cloud or depth image derived from the terrain.
- Optional simulated vehicle pose and sensor noise.

### Outputs

- Terrain safety/cost map.
- Candidate landing regions.
- Ranked landing target with component scores.
- Visual diagnostic overlays.
- Experiment metrics and logs.
- Optional planned path and pose/map estimates.

## SLAM's role

SLAM combines localization and mapping: consecutive observations are compared to estimate vehicle motion while updating a representation of the environment. It is relevant to GPS-denied flight, but it is a progressive extension rather than the first dependency.

The project can establish value by detecting safe landing zones from known or locally observed terrain first. A later phase can add odometry or SLAM, then evaluate how pose uncertainty affects landing-site selection and navigation.

## Optional technology stack

- Python and common numerical/point-cloud libraries for the initial prototype.
- ROS 2 for modular message-based integration.
- Gazebo for richer robotics simulation.
- PX4 Software-in-the-Loop for autopilot integration.

The final selection should follow the needs of the baseline rather than drive them.

## Separation from VERGE-CUAS

This project is independent of VERGE-CUAS. It has its own academic scope, team, deliverables, and evaluation criteria. References to UAV autonomy are domain overlap only and should not be presented as organizational or project continuity.
