# Post-R2 novelty audit: recovery signals after geometric degeneracy

Updated 28 September 2026. This is a focused update to the older R1/R2
literature snapshot, not a systematic review and not proof that the proposed
study is novel. It records several close primary sources found while checking
whether the candidate paper can support a publishable contribution.

## The overlap that changes the claim

The paper must not claim that it is the first to detect when a robot leaves a
degenerate corridor, restore LiDAR odometry, or plot a health/weight signal
through a corridor transition. Earlier work already covers those ideas.

| Primary work | What it already does | What remains different from our candidate study |
| --- | --- | --- |
| Zhang et al., [LOFF, *Drones* (2024)](https://doi.org/10.3390/drones8080411) | A UAV system has a LiDAR failure detector, a separate detector for leaving tunnel degeneracy, and switches between LiDAR and optical-flow odometry. It reports detector behavior and real tunnel flights. In the return flight, the paper describes Faster-LIO and DLIO estimates returning after wall returns become available. | It does not report a prespecified event-level analysis of whether the recovery trigger agrees with sustained, reference-defined one-second translation and rotation accuracy, including false-healthy decisions and delay. Its tunnel reference uses landmarks marked at one-metre spacing rather than motion capture or RTK; the paper reports trajectory/position outcomes, not a full event-by-event short-window recovery label. This is a close overlap, not an empty literature gap. |
| García Daza et al., [Fail-Aware LiDAR Odometry (2020)](https://arxiv.org/html/2103.03626) | A LiDAR odometry system uses heading covariance and its second derivative to estimate time until a failure threshold; it plots that warning with XY error against KITTI reference and reports time-to-threshold on failure/nominal sequences. | Predicting future localization failure from a health signal and comparing it with trajectory error are prior work. The audited paper targets impending malfunction on road sequences, not recovery after a geometry exit; its indicator cutoff was chosen using KITTI sequences 00 and 03, and it reports neither a prespecified exit event nor a sustained local-motion recovery label. |
| Nubert et al., [Learning-based Localizability Estimation (IROS 2022)](https://arxiv.org/html/2203.05698v2) | A network predicts per-scan 6-DoF localizability. Training labels come from Monte-Carlo scan-to-scan ICP errors, with 0.10 m / 2 degree convergence thresholds; field runs include a tunnel traversal and an indoor path with geometry changes. | Per-scan prediction of registration success from pose-error labels, temporal tunnel localizability plots, and sensor-transfer tests are established. The target is local scan-to-scan registration adequacy and map quality; the inspected study does not score a causal health alarm against sustained one-second full-estimator relative motion after an exit. |
| Lanegger et al., [When Your State Estimator Has Lost The Plot (2026)](https://arxiv.org/html/2608.10623v1) | A recent aerial study detects estimator failures from spectral power in estimated velocities for visual-, LiDAR- and radar-inertial systems. It uses 0.1 s windows and reports precision/recall. In a separate RoVIO dataset, it compares high-frequency power with 0.1 s relative pose error and reports 85% health classification. | This is the closest general health-versus-error study. Its failure labels are primarily estimator-consensus/manual, and the authors explicitly say the signal detects degradation rather than measuring accuracy. It does not annotate geometry exits or define a sustained post-exit recovery episode. The spectral method also depends on output rate and is not directly reproducible from our 10 Hz pose stream, whose Nyquist frequency is 5 Hz. |
| Wu et al., [Kinematic-Aware Robust LIO-W, *IEEE Access* (2026)](https://doi.org/10.1109/ACCESS.2026.3680604) | A wheel/IMU consistency score changes LiDAR confidence through a corridor sequence. The paper plots the score and weight at corridor entry and exit; it describes the LiDAR weight returning toward its nominal value after exit. | This is a new fusion method, not a standalone test of existing LiDAR health indicators against independent short-window motion truth. The M3DGR corridor section says full-trajectory ground truth is unavailable and emphasizes endpoint drift and map/trajectory consistency. The shown weight recovery is therefore not itself proof that local motion accuracy recovered at that time. |
| Wang et al., [AGI-LO, *ISPRS Journal of Photogrammetry and Remote Sensing* (2026)](https://doi.org/10.1016/j.isprsjprs.2026.04.007) | An adaptive LiDAR method assesses localizability and changes frame length and use of intensity information as geometric constraints degrade and return. The publisher abstract and accessible article text describe transition-aware updates and pose-accuracy goals in tunnel-like scenes. | This is an estimator/method contribution. The accessible primary text did not establish the same event-level reliability outcome for fixed existing health indicators. The full experimental section and supplement still need a complete manual audit before this comparison can be treated as final. |
| Tagliabue et al., [LION/HeRO (2021)](https://arxiv.org/html/2102.03443v1) | An observability score is used to assess degraded geometry; a supervisor uses odometry confidence to switch sources and restart/reinitialize as needed. | It makes generic observability monitoring, estimator health supervision and odometry-source switching established ideas. It does not, in the inspected paper, define the candidate study's sustained reference-based local-motion recovery outcome after an exit. |
| Turcan Tuna et al., [ICA (2024)](https://arxiv.org/html/2408.11809v3) | Dynamic scenes enter and leave degenerate geometry; the paper plots local and accumulated errors through transitions and discusses recovery feasibility. | Its recovery-feasibility wording is environmental, not the same as a frozen sustained local-error label paired with a causal health alarm and false-reassurance/delay analysis. |
| DCReg, [v3 paper and supplement](https://arxiv.org/html/2509.06285v3) | Directional degeneracy flags, changing masks, detection ratios, registration recall and trajectory errors are evaluated. | Generic detector comparison and accuracy checks are occupied. The remaining candidate difference is the exact event-level timing/outcome protocol, not “indicators sometimes fail.” |

## Narrow candidate question

The only candidate claim worth testing is:

> For fixed LiDAR-inertial estimators and fixed causal health signals, how well
> do health decisions track the return of sustained, reference-defined
> short-window translation and rotation accuracy after an independently
> annotated geometry exit? Measure false-healthy decisions, missed recovery,
> decision availability and delay, and keep accumulated drift separate.

The distinction is an outcome-and-timing evaluation. It is not a new recovery
detector, the first tunnel-exit signal, a new corridor scenario, a new
degeneracy index, or the observation that local accuracy can return while
global drift remains. Those broader claims are contradicted by the work above.

The 2026 spectral paper means we also cannot claim to be the first to compare
an online estimator-health signal with relative pose error. The possible
difference is narrower still: condition that analysis on independently
annotated geometry exits; evaluate geometric information/Schur indicators of
the running LIO itself; require a prespecified triple of consecutive
one-second reference-defined motion windows; measure false-healthy decisions
and confirmation delay; and repeat on unseen scene layouts and a second
estimator. The output-rate mismatch prevents treating its high-frequency
spectral feature as a faithful baseline on our current 10 Hz pose channel.
This difference is a candidate protocol distinction, not a publishable result
or evidence of priority.

## Publication-risk assessment

**Risk remains high.** LOFF is especially close because it explicitly has a
recovery detector for switching back to LiDAR after tunnel exit. The narrower
study could still be useful if it establishes a clear, reproducible fact that
the earlier systems did not measure: whether those online indicators provide
timely and truthful evidence of local motion accuracy, with independent labels
and uncertainty across unseen layouts and a second comparable estimator.
That is a hypothesis to test, not a verified novelty claim.

The current development batch cannot establish that contribution. Its FAST-LIO
threshold was selected on the same 32 scenes that produced the development
scores; Point-LIO currently provides a pose-only smoke run without a comparable
health stream; and the held-out layouts have not been generated or screened.
The manuscript must remain a proposal until independent implementation review,
Point-LIO indicator parity, untouched evaluation, uncertainty analysis and a
fresh claim review are complete.

## Source and access record

- LOFF: the publisher's full article was inspected for its method, detector
  descriptions and tunnel experiments. Its source code link is in the paper.
- Kinematic-Aware Robust LIO-W: the IEEE publisher record and indexed article
  text were inspected. The article explicitly states the M3DGR full-trajectory
  ground-truth limitation and shows a score/weight transition plot.
- AGI-LO: the publisher abstract and accessible article text were inspected;
  the complete experimental section still needs retrieval and manual review.
- Fail-Aware LiDAR Odometry: the complete arXiv HTML source was inspected,
  including the covariance-derivative time-to-failure signal, KITTI results,
  ground-truth error plot, and threshold-selection sequences.
- Learning-based Localizability: the complete arXiv v2 article was inspected,
  including Monte-Carlo ICP error labels, field transitions, sensor transfer,
  and limitations.
- Spectral estimator-health study: the complete arXiv v1 article was inspected,
  including its consensus label rule, direct RoVIO/RPE comparison, performance,
  and limitations about slow drift and transition ambiguity.
- LION/HeRO, ICA and DCReg: compare the already linked full-text notes in
  [RECOVERY_OVERLAP_UPDATE.md](RECOVERY_OVERLAP_UPDATE.md) and
  [INFORMED_CONSTRAINED_ALIGNED.md](INFORMED_CONSTRAINED_ALIGNED.md).

No absence claim here means “no paper exists.” The source search was focused,
not exhaustive. Refresh it again immediately before manuscript submission.
