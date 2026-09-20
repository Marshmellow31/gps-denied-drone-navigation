# Research Goal: Resilient GPS-Denied Drone Navigation

**Status:** Initial direction, to be refined after a structured literature review

**Created:** 20 September 2026

## Goal

Develop and rigorously evaluate a simulation-first, uncertainty-aware navigation approach that allows an unmanned aerial vehicle (UAV) to respond safely when GNSS/GPS becomes unavailable and its remaining localization sensors begin to degrade.

The work will investigate whether detecting localization degradation and adapting the vehicle's behaviour can improve mission success and safety compared with navigation systems that continue using a fixed estimator or fixed sensor-fusion strategy.

This is a new research direction. The existing repository is sample material and a possible source of reusable ideas; it is not assumed to define the final problem, method, simulator, evidence, or paper claims.

## 4W + 1H

### What

Resilient autonomous navigation following GNSS loss, with an emphasis on:

- detecting when localization is becoming unreliable;
- estimating and calibrating uncertainty;
- selecting a safe recovery behaviour; and
- explicitly refusing unsafe continued navigation when evidence is insufficient.

### Why

GPS-denied navigation methods can degrade under conditions such as poor visual texture, motion blur, darkness, sensor dropout, accumulated inertial drift, and incorrect sensor measurements. A system may continue navigating even when its pose estimate is no longer trustworthy. The research will address this gap by connecting localization confidence to safety-aware navigation decisions.

### Who

The intended audience and beneficiaries are:

- researchers working on autonomous micro aerial vehicles;
- developers of safety-conscious GPS-denied navigation systems; and
- researchers who need reproducible simulation scenarios and evaluation procedures.

### Where

Evaluation should cover controlled simulated environments representative of:

- indoor buildings and corridors;
- urban canyons;
- tunnels or other confined spaces; and
- degraded-visibility or perceptually difficult environments.

The exact environment set will be chosen after reviewing available simulators, datasets, comparable papers, and feasible research scope.

### How

The proposed direction is a combined methodological and evaluation contribution:

1. Create controlled GNSS-loss and sensor-degradation scenarios.
2. Implement or integrate suitable localization and navigation baselines.
3. Develop a confidence-calibrated degradation detector.
4. Develop a risk-aware policy that can continue, slow down, relocalize, hover, return, or initiate a simulated safe landing.
5. Evaluate the approach through repeated simulation experiments and, where appropriate, public real-world datasets.
6. Compare it with fixed-estimator, fixed-fusion, and non-adaptive baselines.

## Central Research Question

> Can an uncertainty-aware adaptive navigation system improve mission success and safety after GNSS loss by detecting localization degradation and dynamically selecting an appropriate recovery action?

## Proposed Core Contribution

A **confidence-calibrated localization-degradation detector and risk-aware recovery policy for GPS-denied UAV navigation**, supported by a reproducible evaluation framework containing controlled sensor failures and environmental degradations.

The intended novelty is not merely another generic sensor-fusion pipeline. It is the connection between:

- localization uncertainty;
- actual localization error;
- degradation and failure detection;
- adaptive recovery decisions; and
- end-to-end navigation safety.

## Preliminary Evaluation Principles

The study should measure more than localization accuracy. Candidate evaluation dimensions include:

- trajectory and pose error;
- mission completion rate;
- collision and unsafe-state rate;
- degradation-detection precision, recall, and detection delay;
- uncertainty calibration and false-confidence rate;
- recovery success and time to recovery;
- unnecessary-abort rate;
- runtime, memory, and computational cost; and
- performance across repeated random seeds and degradation severity levels.

Metrics, thresholds, baselines, simulators, datasets, and statistical tests are not yet frozen. They will be selected from the literature before experiments begin.

## Research Boundaries

- The project is simulation-first because physical UAV hardware is unavailable.
- Public real-world datasets may be used to strengthen estimator-level evidence, but dataset replay must not be misrepresented as closed-loop flight validation.
- Synthetic results will not be presented as proof of real-world flight safety or deployment readiness.
- The paper will use the broader term **GNSS-denied** where technically appropriate; GPS is one GNSS.
- The scope should remain narrow enough to support rigorous baselines, ablations, repeated trials, and reproducibility.
- Safe landing may be one recovery action, but it does not automatically remain the paper's central problem.
- The work remains separate from VERGE-CUAS.

## Working Paper Positioning

The paper should be positioned around **failure-aware and uncertainty-aware resilience**, rather than claiming to solve all GPS-denied drone navigation. A suitable working formulation is:

> Failure-Aware Adaptive Navigation for UAVs Under GNSS and Perception Degradation: A Reproducible Simulation Study

This is a working direction, not a final title.

## Initial Literature Anchors

These sources motivated the direction and are starting points, not a complete literature review:

- [State-of-the-Art and Future Directions in Autonomous Navigation for UAVs in GNSS-Denied Environments](https://www.sciencedirect.com/science/article/abs/pii/S1566253526005907)
- [MUN-FRL: A Visual-Inertial-LiDAR Dataset for Aerial Autonomous Navigation and Mapping](https://journals.sagepub.com/doi/10.1177/02783649241238358)
- [GNSS-Denied Semi-Direct Visual Navigation for Autonomous UAVs Aided by PI-Inspired Inertial Priors](https://www.mdpi.com/2226-4310/10/3/220)

## Next Decision Gate

The [20 September plan review](PLAN_REVIEW.md) recommends a smaller first study and documents unresolved novelty, calibration, action-feasibility, and evaluation issues. Its recommendations are provisional until the literature and platform pilot support them. The [LaTeX manuscript](paper/main.tex) contains a proposal abstract only.

Before committing to implementation, conduct a structured literature and feasibility review to decide:

1. the exact research gap and novelty claim;
2. the sensor configuration and failure model;
3. the simulator, public datasets, and baseline algorithms;
4. the recovery actions that are feasible to evaluate;
5. the experimental matrix and statistical methodology; and
6. the diagrams, paper outline, reproduction instructions, and evidence package.

No implementation or experimental result should be treated as paper evidence until these choices are documented and the evaluation protocol is frozen.
