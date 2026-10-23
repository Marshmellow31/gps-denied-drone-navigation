# Recovery-reliability literature overlap audit

Updated 26 September 2026. This is a focused primary-source audit for the
candidate R1 gate, not a systematic review and not proof of novelty. The full
ICA experiment note is [here](INFORMED_CONSTRAINED_ALIGNED.md).

## Informed, Constrained, Aligned

The complete arXiv v3 article, authors' project page and public code README
were reviewed. The main experiments already contain several kinds of
degeneracy transitions and both local and longer-horizon accuracy:

- Dynamic ANYmal simulation starts and ends in a three-axis degenerate region
  (Section V-A-3); the authors add noise to a motion prior and compare APE/RPE
  and map error.
- The ANYmal forest path enters an open field and returns to the forest
  (Section V-B). GNSS supplies position-only global truth, and a handheld
  Leica scan supplies a ground-truth map around the revisited area.
- The Ulmberg tunnel is described as degenerate for over 80% of the sequence.
  Figure 14 plots RTE and ATE over time with the degenerate interval marked;
  Section V-C-1 explicitly interprets RTE as local consistency/stability and
  ATE as longer-horizon absolute consistency.
- The HEAP experiment is a 170 m traverse with only the short passage between
  buildings marked degenerate (Section V-D). It compares mitigation methods
  and a good COIN-LIO prior.

Table 2's “Is recovery feasible?” is defined in its footnote as sufficient
geometric information being available in the environment. That is an
environmental feasibility judgment, not a sustained label that estimator
local motion has returned within an error tolerance. The article reports
registration/mapping performance, but the inspected text does not define
false-healthy decisions, causal alarm delay, censored non-recovery, or an
error-based post-exit recovery time.

The authors' official project page lists supplementary videos in a public
Drive folder. Its public viewer exposed no video contents here. The official
code repository lists the preprint and implementations/configurations but no
separate written experiment supplement. The relevant method/results claims in
this audit are grounded in the full article, not the inaccessible videos.

## DCReg v3, including its supplement

Reviewed the 10 September 2026 arXiv v3 main article, Sections 7.1 and 7.4,
plus the four-page official [`paper/supp.pdf`](https://github.com/JokerJohn/DCReg/blob/8ce8451b15491a4bbe17cf85ab02a8bed6696861/paper/supp.pdf)
at repository commit `8ce8451b15491a4bbe17cf85ab02a8bed6696861` (SHA-256
`b1b9a862ebaee36f3f3390ddd91e2bda53f9ff54d2267f35723e2d9f7394dc16`).

This is a close overlap for generic detection reliability: Section 7.4.1
shows per-direction degeneracy masks over time, compares thresholds/condition
numbers, and reports detection ratios across datasets. The text explicitly
describes competing methods' over-detection and insufficient detection.
Section 7.4.2 tracks changing conditioning during a staircase traversal.
Section 7.1 defines degeneracy ratio as the percentage of frames marked
degenerate and says it is a detection-sensitivity measure, separate from
ATE/map errors.

For comparator implementation, the main paper—not the four-page supplement—
defines the rotational/translational Schur complements in Section 4.2,
direction-specific ratios in Equation 20 and the `>` threshold rule in
Equation 21. Section 4.4 states the usual positive-definite block assumptions
and notes Moore-Penrose generalizations. The study's relative pseudoinverse
cutoff `1e-12` is therefore an explicitly declared adaptation setting, not a
published DCReg default.

The supplement also reports frame-pair Registration Recall: a pair succeeds
when relative rotation error is below 5 degrees and relative translation
error below 0.2 m; RR is the fraction of successful pairs. Tables combine
degeneracy ratio (DR), RR, ATE, relative translation/rotation error, and map
quality per sequence. Thus a general claim that “degeneracy flags can be
wrong” or that indicators should be compared with registration quality is
not distinct by itself.

In the inspected main text and supplement, I found no event-centered
geometry-exit annotation, sustained full-LIO local-motion label, causal
recovery-detection delay, right-censored non-recovery outcome, or transfer of
a frozen post-exit health decision to untouched scene clusters. Their RR is
per registration pair and their DR is an aggregate fraction; the documents
do not report a joint false-healthy/time-to-recovery analysis against sustained
trajectory-window accuracy. This is the narrow potential difference, not
proof that no such study exists elsewhere.

## ALIVE-LIO

Reviewed [arXiv v1](https://arxiv.org/html/2604.02706v1), including the
limitations/conclusion. The authors report slow recovery after degeneracy
and failures to trigger corrective updates when degeneracy is not detected.
This makes recovery difficulty and missed correction an existing observation.
The inspected article does not define an event-level post-exit local-motion
label or report an alarm-delay/false-healthy evaluation for existing health
signals.

## Candidate distinction and limits

The defensible candidate is now narrower:

> For a fixed LiDAR-inertial estimator and fixed online health signal, how
> well does a causal signal decision predict **sustained, reference-defined
> short-window translation and rotation accuracy after a geometry exit**?
> Measure false-healthy declarations, detection delay, non-recovery/censoring,
> decision availability and transfer to untouched scene templates. Report
> accumulated drift separately without treating local/global disagreement as
> a novelty claim.

The distinction is the **outcome and timing evaluation**, not a new detector,
generic degeneracy classification, corridor scenario, error trace, or ATE/RTE
comparison. Existing work already covers each of those pieces separately and
some together. A publishable contribution remains uncertain until a fair
comparator and computable outcome rule are specified in T10/T11 and the
full multi-scene study supports a useful result.

## Source locations and access record

- ICA: [arXiv v3](https://arxiv.org/html/2408.11809), Sections I-2, I-4–I-5,
  V-A-3, V-B, V-C-1/V-C-3, V-D, Table 2 footnote, Figure 14, Table 5,
  Section VI-D; [project page](https://sites.google.com/leggedrobotics.com/perfectlyconstrained);
  [official repository](https://github.com/leggedrobotics/perfectlyconstrained).
- DCReg: [arXiv v3](https://arxiv.org/html/2509.06285v3), Sections 7.1.1–7.1.3,
  7.3–7.4.2 and Table 2; [supplement PDF](https://github.com/JokerJohn/DCReg/blob/8ce8451b15491a4bbe17cf85ab02a8bed6696861/paper/supp.pdf),
  pp. 1–4.
- ALIVE-LIO: [arXiv v1](https://arxiv.org/html/2604.02706v1), limitations
  and conclusion, final section before References.

Targeted exact-title and “LiDAR degeneracy detection reliability / recovery /
delay” searches were used to locate the primary sources. Aggregator summaries
were not used for the evidence claims above. Supplementary videos for ICA were
not readable in the public Drive viewer and remain an explicit access limit.
