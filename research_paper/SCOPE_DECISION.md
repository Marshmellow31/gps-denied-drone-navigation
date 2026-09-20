# LiDAR scope decision and existing-work check

20 September 2026. User correction: prioritize the research contribution; use LiDAR rather than cameras when a sensor modality is needed. No physical hardware is available or required. The camera-outage study is superseded.

## Recommendation

Investigate the reliability of existing LiDAR localization-health indicators during the transition out of geometric degeneracy. Separate recovery of accurate local motion from accumulated drift. This is a candidate empirical gap; it is not a verified novel algorithm.

## Closest work

| Primary source | What exists | Consequence |
| --- | --- | --- |
| [X-ICP](https://arxiv.org/html/2211.16335v3) | Fine-grained localizability detection and constrained ICP registration. | Generic eigenvalue-based degeneracy detection is not novel. Compare the actual published formulation. |
| [AdaLIO](https://arxiv.org/abs/2304.12577) | Adaptive LIO for degenerate indoor environments. | Merely adapting parameters in corridors is already covered. |
| [SuperLoc](https://arxiv.org/html/2412.02901v1), [author explanation](https://superodometry.com/superloc.html) | Predictive alignment risk, localizability and prior integration in degraded geometry. Explains limits of Hessian thresholds across environments/sensors. | Generic LiDAR failure prediction, confidence and sensor-switching proposals have close overlap. |
| [GEODE](https://arxiv.org/abs/2409.04961), [official data documentation](https://github.com/PengYu-Team/GEODE_dataset) | Broad dataset and benchmark for geometric degeneracy. | Another general corridor/tunnel benchmark is insufficient differentiation. Data contain reference-quality caveats. |
| [Degradation Resilient LiDAR-Radar-Inertial Odometry](https://arxiv.org/abs/2403.05332) | Uses radar to mitigate LiDAR degeneracy. | Adding another sensor is established and expands scope; we will evaluate LiDAR/IMU inputs only. |
| [Unveiling Non-Reproducibility in LIO](https://ieeexplore.ieee.org/document/11266943/) | Empirical work on LIO repeatability. | Reproducibility alone is not novel; include backend repeatability as a control. |

Inspection: author abstracts, project explanations and dataset READMEs were reviewed; X-ICP and SuperLoc full-text pages were retrieved, but complete experimental/supplement/code audits remain pending. This is a targeted scoping review, not an exhaustive systematic review or proof of novelty.

## What might be distinct

A prespecified comparison of false reassurance and detection delay specifically after degeneracy ends, with independent local-motion recovery labels, fixed-frame drift reporting, and unseen-scene transfer. The checked overview material did not establish that exact study; absence from an overview does not show absence from the literature.

The gap must survive a detailed comparison of X-ICP, SuperLoc, their references and GEODE evaluation protocols before implementation expands. Do not claim the distinction between local observability and global drift is new: it is an expected property of odometry. A publishable contribution must show a useful, previously unestablished limitation, tradeoff or transferable empirical finding about the indicators.

If health indicators correctly track local recovery, report that result with uncertainty. Do not manufacture a failure claim by testing them against accumulated drift they were never designed to estimate.

## Options and publication potential

| Scope | Novelty risk | Judgment |
| --- | --- | --- |
| Generic LiDAR/IMU fusion or degeneracy detector | High overlap with mature literature | Reject as the paper's contribution |
| Broad robustness comparison across many sensors/environments | High overlap with GEODE and other benchmarks | Too broad and weakly differentiated |
| Transition-focused health-indicator reliability study | Unresolved; narrower comparison to verify | Preferred research candidate |
| New recovery-aware indicator | Requires separate mathematical/methodological distinction | Possible extension only if the empirical study establishes a gap |

The preferred option is manageable as an empirical paper with public data and simulation. Its publication potential depends on findings, not hardware ownership. One backend on one illustrative scene would be preliminary evidence. A relevant workshop can provide feedback but may be non-archival. A specialist archival paper needs clear differentiation, reproducible comparisons and convincing controls. RA-L/ICRA/IROS main-track remains a stretch unless results provide broader insight and independent validation. [RA-L's official scope](https://www.ieee-ras.org/publications/ieee-robotics-and-automation-letters/) emphasizes innovative research and significant findings/application studies.

No venue or acceptance probability is selected. First-week-of-November delivery is a manuscript objective, not a promise of a publication decision by then.

## Candidate evidence and software

- [NTNU LiDAR degeneracy recordings](https://github.com/ntnu-arl/lidar_degeneracy_datasets) are recorded on a manually flown aerial robot and include LiDAR/IMU/radar. Confirm suitable independent reference and entry/exit intervals before choosing sequences. Ignore radar input.
- [GEODE documentation](https://github.com/PengYu-Team/GEODE_dataset) describes sensor-frame transformations, position-only reference in some tunnels and missing pose truth for a staircase device. Do not assume every recording supports full pose-recovery metrics or is airborne.
- [FAST-LIO2 code](https://github.com/hku-mars/FAST_LIO) is a candidate primary LIO backend; [Point-LIO](https://github.com/hku-mars/Point-LIO) is a replication candidate. Confirm point timestamps, IMU units, calibration and sensor-format compatibility. These are literature/tool candidates, not locally reproduced systems.
- Controlled synthetic geometry can isolate transition duration and geometry under matched motion. Simulated point clouds need an explicit sensing model; full LIO needs timed scans and inertial data. Ideal registration pairs support narrower registration claims only.

## Search record and next decision

Queries covered LiDAR-inertial degeneracy detection/recovery, localizability and false confidence, recovery after restored observability, scan loss, corruption benchmarks, and named followups for X-ICP, SuperLoc, GEODE and AdaLIO. Sources were accessed on 20 September 2026. Narrow searches with no match were not treated as novelty evidence.

Week one: write an exact claim-versus-prior-work matrix and demonstrate one valid transition with reference data. The six weekly professor-review milestones are in [the goal](RESEARCH_GOAL.md). Topic validity is the first gate; equipment procurement and embedded performance are outside scope.
