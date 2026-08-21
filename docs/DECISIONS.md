# Decision Log

This lightweight log prevents important scope and architecture choices from being lost. Add a dated entry whenever a decision changes implementation direction, dependencies, evaluation, or project boundaries.

## D-001 — Simulation-first development

**Status:** Accepted

**Decision:** Prove the system on deterministic synthetic terrain before physical flight or high-fidelity simulator integration.

**Reason:** Simulation provides ground truth, repeatability, faster iteration, and lower safety risk.

**Consequence:** Physical-flight claims are outside the core result.

## D-002 — Geometry-first safe landing detection

**Status:** Accepted

**Decision:** Begin with slope, roughness, obstacle clearance, observation confidence, and support area rather than an end-to-end learned model.

**Reason:** These features are explainable, testable, and appropriate for the course scope.

**Consequence:** Machine learning is an optional response to a measured limitation, not a default requirement.

## D-003 — Safe landing is the core; SLAM is an extension

**Status:** Accepted

**Decision:** Complete and evaluate landing-zone detection before investing in SLAM.

**Reason:** SLAM can consume the whole schedule and obscure the primary measurable contribution.

**Consequence:** A strong core submission remains possible without a complete SLAM stack.

## D-004 — Keep core algorithms independent of ROS 2/PX4/Gazebo

**Status:** Accepted

**Decision:** Implement the core as ordinary Python modules with adapters added later.

**Reason:** Standalone algorithms are easier to test, profile, reproduce, and reuse.

**Consequence:** Simulator messages and coordinate transforms remain boundary concerns.

## D-005 — Treat false-safe predictions as safety critical

**Status:** Accepted

**Decision:** Report false-safe rate and valid-footprint rate prominently in addition to precision, recall, and F1.

**Reason:** Incorrectly accepting unsafe ground is more serious than rejecting a usable region.

**Consequence:** Threshold selection should favor safety and expose the cost in rejected sites.

## D-006 — Separate project from VERGE-CUAS

**Status:** Accepted

**Decision:** Maintain separate identity, scope, ownership, deliverables, and claims.

**Reason:** General UAV-domain overlap does not make these the same project.

**Consequence:** Documentation and presentations must not imply organizational continuity.

## D-007 — Design to a low-cost hardware floor

**Status:** Accepted provisionally

**Decision:** Use a conservative VL53L5CX-class 8×8 multizone ToF profile and a Raspberry Pi Zero 2 W-class companion-compute floor for the first baseline. Keep the core input as a sensor-neutral local elevation grid so an LD19-class scanning LiDAR can be added later.

**Reason:** A perfect dense height map would not demonstrate deployability. The selected floor forces sparse-data, latency, memory, and failure behavior to be addressed now while avoiding a costly 3D LiDAR or GPU.

**Alternatives considered:** Dense 3D LiDAR first; single-point rangefinder only; desktop-only simulation.

**Consequence:** The baseline must simulate sensor and pose limitations, run without a GPU or ROS, produce no target under insufficient evidence, and pass a real Pi/sensor bench gate before integration claims.

See [ADR-001](ADR-001-HARDWARE-CONSTRAINED-PIPELINE.md).

## Open decisions

| ID | Decision needed | Required input |
| --- | --- | --- |
| O-001 | Final Python version and environment tooling | Target laptop audit |
| O-002 | Initial landing footprint and safety thresholds | Vehicle assumption or faculty guidance |
| O-003 | Final physical sensor breakout and supplier | Indoor/outdoor requirement, local availability, and budget |
| O-004 | Academic schedule and milestone dates | Course deadline and reviews |
| O-005 | Navigation and SLAM extension go/no-go | Core benchmark result and remaining time |
| O-006 | ROS 2/Gazebo/PX4 versions | Laptop OS and extension approval |

## Entry template

```text
## D-XXX — Short title

Status: Proposed / Accepted / Superseded
Date:
Decision:
Reason:
Alternatives considered:
Consequences:
Supersedes / superseded by:
```
