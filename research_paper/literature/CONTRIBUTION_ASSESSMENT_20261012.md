# Candidate contribution after the completed evaluation

12 October 2026. Steps 1–3: contribution statement, primary-source comparison and claim classification. This is an author assessment, not independent scientific acceptance or a publication-novelty verdict. It supplements the frozen literature/protocol; no experiment, threshold or numerical result is changed.

## Candidate contribution

> We provide a controlled evaluation of how development-calibrated geometric health decisions transfer to fresh, geometry-screened straight-corridor layouts in FAST-LIO and Point-LIO. At locked operating points, we quantify premature healthy decisions, missed recovery, detection delay, availability and non-recovery against sustained reference-defined local translation/rotation accuracy, with paired controls and uncertainty over geometry clusters.

The resulting empirical finding is that these fixed policies exhibit different failure trade-offs in the evaluated design: few premature healthy decisions can coexist with many missed recoveries, while the fixed directional adaptation can produce substantial premature healthy decisions. Group summaries reveal heterogeneity that aggregate rates conceal. Whether this constitutes a sufficiently new scientific finding remains contingent on the comparison below and scientific review.

Suggested working title: **Fixed geometric health decisions after LiDAR degeneracy: a controlled transfer study in two LIO backends**.

The contribution is an empirical assessment of existing signals. The minimum eigenvalue is a measurement-geometry diagnostic; the Schur detector is an explicitly bounded DCReg adaptation, without its registration mitigation. Neither is a newly proposed algorithm.

## What the completed data support

| Candidate result statement | Evidence | Wording limit |
| --- | --- | --- |
| At its locked scalar operating point, FAST-LIO rarely declares initial health prematurely but misses many recovered events. | Initial false-healthy 1/46 conditional; detection 14/46; median delay among detections 0.850 s. | A sample trade-off, not a population reliability guarantee or better responsiveness. |
| Fixed DCReg adaptation does not provide uniformly reliable recovery decisions in the Point-LIO replication. | Initial false-healthy 16/47; detection 25/32. | Applies to this adaptation, fixed policy, backend and screened design; not full DCReg or every directional method. |
| Planned group summaries show materially different outcomes. | Point recovery counts 12/12, 4/12, 12/12, 4/12; Point scalar false-healthy 0, 0, 4, 0. | The emphasis on width or long/narrow was selected after observing results; mechanism and generalization remain exploratory. |
| Corridors have larger aggregate paired interior translation error than their feature controls. | FAST +0.194 m [0.086, 0.311]; Point +0.149 m [0.068, 0.230], geometry bootstrap 95%. | Conditional on the four screened strata; Point short/narrow mean is negative. Not universal control benefit or estimator superiority. |

Exact counts, intervals and definitions: [accepted results](../evidence/final_geometry_v2_results_20261012/RESULTS_REPORT.md). The [accounting audit](../reviews/FINAL_GEOMETRY_V2_RESULT_AUDIT_20261012.md) accepts reconciliation, not novelty.

## Distinction from reviewed prior work

The [primary-source matrix](CLOSEST_WORK_MATRIX_20261012.md) identifies substantial overlap. OCE is particularly close: short-window ground-truth usability, premature recovery, hysteresis and recovery delay already exist. ICA and ALIVE-LIO also discuss recovery limitations; DCReg already studies temporal detection reliability. These concepts must be described as inherited evaluation concerns.

The candidate distinction is their **joint application to frozen, development-calibrated policies transferred to fresh randomized length/width groups in two independently instrumented LIO measurement stages**, together with an evidence-supported finding about fixed-policy limitations. I did not identify that exact study in the inspected material. This is a bounded inference from the selected sources, not proof of absence across the literature. More runs, two backends, complete logs and a larger metric list alone do not prove novelty.

## Claims to exclude

- No “first,” new detector, guaranteed recovery, flight-safety or real-world reliability claim.
- No superiority over OCE, X-ICP, SuperLoc, ICA, ALIVE-LIO or full DCReg: those systems were not run under a shared evaluation here.
- No formal causal explanation of width effects, diagnostic failure or control benefit. Multiple scene dimensions, visibility and estimator behavior can covary; existing records have not yet established a mechanism.
- No direct backend leaderboard from diagnostic sensitivities: own-backend truth labels yield different denominators.
- No claim of a wholly unadapted original test design. The failed geometry-only screen informed the revised controls/pools; original IDs 100–179 remain excluded. Final policies were not tuned on final outcomes.

## Decision after steps 1–3

**A narrowly framed empirical paper remains plausible; novelty is not established.** The gap to assess is the missing evidence about fixed-policy transfer and its consequences, rather than the invention of recovery metrics. The [claim-to-evidence map](../evidence/CLAIM_EVIDENCE_MAP_20261012.md) separates predeclared estimation from post-result hypotheses.

Before claiming publication novelty, a scientific reviewer should assess whether the observed trade-off adds useful knowledge beyond OCE/DCReg/ICA and whether comparator limitations weaken that conclusion. If a claim depends on the width explanation, validate it in a separately frozen fresh study. Steps 4–8 have not been executed by this assessment. No new ablation, comparator or hypothesis test is authorized by this document.
