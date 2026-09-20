# Research plan review

**Historical:** The recovery-policy recommendation below was superseded by [the reduced scope decision](SCOPE_DECISION.md) after closer prior work was found. Use [the current goal](RESEARCH_GOAL.md) for active planning.

Reviewed: 20 September 2026. This is a targeted feasibility and novelty-risk review, not a systematic literature review.

## Verdict

The roadmap has sound evidence and reproducibility principles, but it is not yet an executable or optimal experiment plan. Its breadth is the largest delivery risk. The proposed connection between uncertainty and recovery is a research direction, not an established novelty claim.

## Issues and recommended decisions

| Priority | Issue | Recommended correction before protocol freeze |
| --- | --- | --- |
| High | Novelty overlaps existing introspective perception and competence-aware planning. | Compare the exact risk target, calibration method, temporal prediction, action selection, and evaluation with the closest primary papers. Stop or refine the contribution if it is only integration. |
| High | Multiple environments, sensor suites, estimators, and five recovery families are too broad. | Start with one camera/IMU estimator, one simulator, one mission family, two visual degradations, and a small executable action set. Additional domains are extensions. |
| High | GNSS loss and visual localization failure are conflated. Indoor missions may never have GNSS. | Define initialization, coordinate frame, map access, and whether GNSS is absent throughout or removed after initialization. Evaluate the transition separately if retained. |
| High | Hover, return, and landing are assumed available when localization has failed. | Specify sensor and controller requirements for every action. Log simulated abort as a mission outcome; it is not proof of a successful landing. Model braking and stabilization rather than teleporting or freezing the vehicle. |
| High | "Calibrated confidence" has no event, horizon, or label definition. | Define a candidate target such as probability of exceeding a pose-error threshold within a fixed horizon. Distinguish this from collision risk, which also depends on obstacles and actions. Freeze thresholds, horizon, and coordinate alignment. |
| High | Proposed baseline list includes easy comparisons but no mandatory strong recovery baseline. | Compare with a relevant published uncertainty/perception-aware method and a tuned native-confidence threshold. Hold estimator, controller, observations, mission, and tuning budget constant. Report task-relevant adaptations. |
| High | Train/calibration/test separation is unspecified. | Split by scene and trajectory, not adjacent frames. Reserve separate training, calibration, development, and final test data. Fit calibration without final-test access. Ground truth may label offline training/evaluation but must not enter online method inputs. |
| Medium | Huge experiment matrix and no compute/sample budget. | Run a feasibility pilot first; estimate time per run and total storage. Choose repetitions from desired confidence-interval precision and pilot variability. Use paired scenarios/seeds and trajectory-level analysis, not frames as independent trials. |
| Medium | Safety/usefulness tradeoff and many metrics invite selective reporting. | Preregister primary mission-completion and collision outcomes, report their tradeoff over fixed operating points, and separate secondary calibration/detection metrics. Define timeout, abort, tracking loss, and failed-run accounting. |
| Medium | Roadmap freezes protocol before platform feasibility, while phase descriptions imply earlier selection. | Use literature plus a minimal platform pilot, then select baselines and freeze the confirmatory protocol. Any later change requires a dated amendment and untouched replacement test data when needed. |
| Medium | Ground-truth isolation statement could inadvertently prohibit valid offline supervision. | Keep independent evaluator truth and offline training labels; forbid online truth features, future observations, and oracle hazard maps unless explicitly part of a separately labeled bound. |
| Medium | Venue and resources are deferred too far. | Record available compute, team effort, deadline, and two possible venue scopes during feasibility; select submission formatting later. Acceptance cannot be inferred from simulation alone. |
| Low | Root agent instructions and archived commands describe the old layout. | Read old prototype paths relative to old_data; run its commands there. Keep current research status in the root README. |

## Recommended minimum study (provisional)

Investigate whether calibrated short-horizon localization-failure prediction improves the mission-completion/collision tradeoff over tuned native estimator confidence under unseen visual degradation. Use a fixed camera/IMU estimator and controller. Begin with continue, slow/reobserve, and terminate-mission outcomes, subject to controller feasibility. Do not claim terminate-mission is a safe flight manoeuvre.

Use texture loss and image dropout as initial candidate degradations; the literature and simulator pilot may change these. Hold out scene layouts and degradation severities. Compare calibration and temporal-history ablations using identical inputs and budgets. Add public flight-data replay only for the detector/estimator claims that replay can test. This recommendation is a scope proposal, not a frozen method or novelty finding.

```mermaid
flowchart LR
    A[Closest literature + compute budget] --> B[One estimator and simulator pilot]
    B --> C[Narrow gap + viable actions]
    C --> D[Strong baselines + data splits]
    D --> E[Freeze hypotheses and protocol]
    E --> F[Development + calibration]
    F --> G[Freeze method]
    G --> H[Untouched evaluation + paper]
```

## Primary sources checked

- Rabiee et al., [Competence-Aware Path Planning via Introspective Perception](https://arxiv.org/abs/2109.13974), revised 2022, accepted by IEEE Robotics and Automation Letters. Connects perception failures to task-level competence and planning. This directly challenges a broad claim that connecting confidence to navigation decisions is new.
- Rabiee and Biswas, [Introspective Perception for Mobile Robots](https://arxiv.org/abs/2306.16698), 2023. Predicts perception-error uncertainty and evaluates visual SLAM and stereo depth. Uncertainty estimation alone is insufficient differentiation.
- [UAV Active Perception and Motion Control for Improving Navigation Using Low-Cost Sensors](https://arxiv.org/abs/2407.15122), 2024. Relevant aerial perception-aware motion-control work to examine in full before claiming novelty for reobservation actions.

These checks establish overlap risk. They do not establish that the narrower proposed study is novel; full-text comparison and a broader search remain required.
