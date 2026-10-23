# Informed, Constrained, Aligned — full experiments audit

Reviewed 26 September 2026 against the complete arXiv v3 article and the
authors' public project/code pages. This is a scoped overlap review, not a
systematic review or proof of novelty.

## Sources inspected

- Turcan Tuna et al., [arXiv v3 full text](https://arxiv.org/html/2408.11809), dated 14 July 2025: Abstract; Sections I–VI; all of Section V experiments; Table 2 and its recovery-feasibility footnote; Tables 3 and 5; Figure 14; Section VI-D and conclusion.
- Authors' [project page](https://sites.google.com/leggedrobotics.com/perfectlyconstrained): paper, datasets, code and supplementary-video links.
- Authors' [official implementation repository](https://github.com/leggedrobotics/perfectlyconstrained): repository README, build instructions, experiment replay instructions and listed root files. It includes a preprint and the implementations/configurations; no separate written experiment-supplement PDF was listed there.

The project page labels a supplementary section and links a Google Drive video
folder. Its public viewer exposed no video file listing/content in this audit,
so the videos are **not inspected**. No numerical method claim below depends
on those videos. The accessible full-text article and repository README are
the inspected methodological sources.

## What the study actually evaluates

The paper's target is improving LiDAR point-cloud registration under
ill-conditioning. It compares active and passive mitigation methods in one
unified Open3D-SLAM/point-to-plane registration setup; it is not a standalone
study of health-indicator decisions.

The experiments cover more than static registration:

- **Section V-A-1:** static symmetric-cylinder ICP, per-iteration solution
  behavior and error along a deliberately unobservable rotational direction.
- **Section V-A-3:** simulated ANYmal with severe multi-axis degeneracy,
  noised motion prior, APE/RPE and map-to-truth results. The robot starts and
  ends in a degenerate region; the text describes multiple degenerate snippets.
- **Section V-B:** ANYmal moves from a forest into an open field and returns.
  GNSS provides position-only global trajectory truth; a handheld Leica scan
  provides map truth near the revisited region.
- **Section V-C:** handheld Ulmberg tunnel, one-directional degeneracy for
  more than 80% of the dataset. Figure 14 plots RTE and ATE over time with the
  degenerate interval highlighted; RTE is explicitly called local consistency
  and stability, while ATE represents longer-horizon absolute consistency.
- **Section V-D:** HEAP excavator, 170 m traverse with only the between-building
  passage marked degenerate. The authors evaluate mapping and report that
  mitigation methods work comparably with a good COIN-LIO prior.

Table 2's “Is recovery feasible?” column does **not** label when estimated
motion becomes accurate. Its footnote defines feasibility as whether the
environment contains sufficient geometric information. Separately, the paper
does examine trajectory/local and global quality: its metrics include RTE,
ATE, drift and map error. Therefore neither “recovery after degeneracy is
hard” nor “local and accumulated error differ” can be our contribution.

The compared methods include X-ICP/equality constraints, TSVD, regularization,
robust norms, sampling and prior-only variants. Degeneracy detection is used
to drive mitigation; the paper reports method/map/trajectory outcomes and
time-varying error curves, not a sustained post-exit local-motion recovery
label with a causal warning decision.

## Error definitions and overlap boundary

The paper evaluates pose and map outcomes after degeneracy. In the tunnel
study, it uses distance-based RTE and ATE over the sequence and highlights the
degenerate interval. In the excavator/ANYmal studies, it compares map quality
and prior-only performance. These results make a generic time-series of
Hessian values beside trajectory error too weak as a distinction.

In the inspected main text, I found no prespecified sustained local-motion
recovery label, false-healthy denominator, causal alarm delay, right-censored
non-recovery outcome, or threshold transfer of an alarm rule to held-out
transition scenes. This is a bounded “not found in inspected material,” not a
claim that no such measurement exists elsewhere.

The author's repository shows the experiment framework, launch files, method
configurations and field replay recipes. It supports reproducing registration
mitigation comparisons, but it does not identify a frozen health-alarm versus
post-exit local-accuracy protocol in its README.

## Relevance to our candidate

The potentially distinct question must stay narrow: for an already-running
LIO backend, does an online geometry-health value agree with independently
measured **sustained short-window translation and rotation accuracy after
geometry changes**, and how often is it falsely healthy, unavailable, or late
when tested on layouts not used to select its operating point? That is an
evaluation question about a signal's relation to system-level local accuracy;
it is not a new degeneracy detector or a new explanation of ATE versus RTE.

This difference is plausible enough for a feasibility gate, not established
novelty. It must also withstand [DCReg's temporal detection/reliability
analysis](RECOVERY_OVERLAP_UPDATE.md), [ALIVE-LIO's reported slow recovery](RECOVERY_OVERLAP_UPDATE.md),
and the X-ICP/SuperLoc findings in the [comparison matrix](COMPARISON.md).

## Exact paper locations

- Degeneracy definition and scope: Sections I-2, I-4 and I-5.
- Simulated transitions and per-pose errors: Section V-A-3, Table 3.
- Entry/exit/open-field path and truth limits: Section V-B.
- Local RTE, global ATE, temporal error trace and highlighted degeneracy:
  Section V-C-1 and V-C-3, Figure 14, Table 5.
- Short-burst narrow-passage experiment: Section V-D, Table 2.
- Meaning of “recovery feasible”: Table 2 footnote.
- Motion-prior dependence: Section VI-D.

