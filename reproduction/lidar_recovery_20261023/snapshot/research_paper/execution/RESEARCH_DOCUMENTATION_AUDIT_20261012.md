# Research implementation and visual-documentation audit

Audited 12 October 2026. This is a documentation and bounded verification audit, not a new independent R3 review or a scientific novelty acceptance. The [current research README](../README.md) is the reader entry point.

## Verified findings

- The current R3 report begins with PASS dated 12 October. A read-only call to `r3_evaluation_workflow.require_r3_pass` returned PASS with **179 entries** against `IMPLEMENTATION_FREEZE.md`; this includes validation of the original 53-file R2 bundle. Both locked thresholds match.
- A fresh run in the recorded external Python environment discovered **233 tests: 231 passed, 2 skipped**, in 8.019 seconds. Log: [documentation audit test run](../evidence/documentation_audit_tests_20261012.log). This new log is not the accepted freeze's test log; the retained [readiness log](../evidence/r3_readiness_tests_20261010.log) independently reports the same test/skip counts.
- Skips: SciPy scene-structure fixture, and the native sidecar C++ fixture needing `POINTLIO_SOURCE_ROOT`. Native reset checks and sidecar on/off identity are separately documented in the [Point-LIO verification report](../evidence/POINTLIO_IMPLEMENTATION_VERIFICATION_20260929.md) and [one-seed acceptance](../reviews/POINTLIO_ONE_SEED_ACCEPTANCE_20261009.md). They were not rerun here.
- Both development cohorts and their corrected analyses are documented and accepted. Current counts are in [the corrected report](../evidence/DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md), superseding historical counts such as FAST-LIO DCReg 29/32.
- The saved final plan states no geometry screen, generated inputs or executed final batch. No final geometry, sensor input or output was opened during this audit.
- OCE's publisher article was checked live. Section 4.2 and its recovery/hysteresis results substantiate the overlap described in the [dated addendum](../literature/RECOVERY_OVERLAP_ADDENDUM_20261010.md). This was a focused source check, not a fresh systematic literature search.
- The development comparison and fresh repeat-motion PNGs were visually inspected. All three comparison exports and all six fresh repeat exports were checked against their manifests. This does not revalidate every native bag or bulk output on Acer.

## Documentation conflicts

| File | Stale statement | Current evidence/action |
| --- | --- | --- |
| Root `README.md` | 29 September checkpoint, Point-LIO implementation pending, old tests/results | Superseded for readers by [research README](../README.md); preserve root bytes because its hash is in R3. |
| `execution/STATUS.md` and `CURRENT_HANDOFF.md` | Latest headline still says R3 REVISE, no freeze, older inventory/test counts | Read the 12 October R3 PASS and live freeze verification. These summaries are also frozen inventory members; use this addendum rather than changing their bytes. |
| `experiments/README.md` | Historical 86-test status and incomplete Point-LIO headline | Historical GEODE reproduction context. Use the research README's verified test command/current evidence. |
| `paper/README.md` | September manuscript checkpoint; methods draft omitted | Main article is still a proposal; separate methods draft exists and contains stale pending-stage prose. Neither is a completed paper. |
| `figures/README.md` | Fresh repeat and two-backend comparison not indexed | Added a dated current-figure index without changing frozen plots/manifests. |

No accepted inventory member was edited by this documentation work. To replace frozen summaries later, retain the accepted snapshot, update the intended files, rebuild the exact inventory and obtain acceptance for that revised bundle. Do not silently relabel an old hash bundle as current.

## Coverage by research step

“Present” means an actual figure exists, not just a suggested plot. Tables and manifests remain valid documentation even when no figure is needed.

| Step | Existing visual/documentation | Assessment |
| --- | --- | --- |
| T01 environment | Environment table and logs | Adequate as text; a screenshot adds little reproducibility value. |
| T02 literature / novelty | Comparison matrix and source notes | Written evidence exists; add a compact feature matrix with OCE and clearly provisional distinction. |
| T03–T04 data eligibility and inspection | Hilti scan snapshots and reference timeline | Useful qualified visuals. Dataset failures/reference independence still need explicit prose. |
| T05 metrics and interfaces | Written contracts | A recovery timing diagram is missing. |
| T06–T08 replay / evaluator / diagnostic export | Hilti health-error pilot plot, source derivation and manifests | Good pilot illustration; lacks a complete end-to-end measurement/export schematic. README now adds a pipeline diagram. |
| T09 / T12 simulation | Bootstrap and motion-v3 timeline | Early development examples exist; formal x=-6 m route and corridor/control dimensions lack a dedicated schematic. |
| T10 / T13 signal definitions and math | Formula/specification, analytic tests and reproduction report | Adequate technical text; add a common-basis measurement schematic if needed for presentation. |
| T11 development/test split | `SPLITS.csv` and frozen rules | Split visual missing; can draw it from metadata without generating test scenes. |
| T14–T16 current development | Two-backend comparison, fresh repeat plots, accepted tables/CSVs | Strongest quantitative visuals; event timeline, full outcome ledger and selection trade-off plot still missing. |
| R1–R3 checks | Independent reviews, exact hash inventories, test logs | Evidence is present; dated milestone graphic useful, test-output screenshots unnecessary. |
| Final evaluation / uncertainty / results | Tested callers and plan only | Scientific outputs absent. Plotting fixture results as final findings would be misleading. |
| Manuscript | Proposal abstract and separate methods draft | Results, final claim, discussion and submission review remain unfinished. |

Existing figure caveats: the signal-comparison PNG's long footer approaches/overruns the right edge; wrap it into explicit shorter lines in a future version. The Hilti figure guide retains a coarse 32–36 s band, while the later event audit fixed 31.6–33.6 s. Explain that chronology rather than presenting the historical band as the exact frozen boundary. Bootstrap figures should remain labelled historical.

## What to add, where, and how

These are proposed artifacts, not already implemented scripts. Add explanatory diagrams now using frozen rules and development data. Add final-result figures only after the accepted final workflow produces verified outputs.

| Priority / proposed artifact | Data source and contents | Implementation and placement |
| --- | --- | --- |
| 1. `recovery_timing.svg` | Frozen `METRICS.md`: exit, one-second truth windows, 0.20 m / 5° tests, three-window confirmation, 10 Hz causal ticks, three-tick debounce, alarm delay and relapse | Use Mermaid or a small Matplotlib schematic. Label illustrative values as illustrative; do not imply measured timing. Embed beside the recovery definition in README and Methods. |
| 1. `formal_scene_pair.svg` | Frozen simulator and formal route: corridor/control geometry, start x=-6 m, entry/exit, coordinate axes, units, LiDAR/IMU and identical motion | Draw a dimensioned plan view from an already permitted development seed. A conceptual schematic needs no sensor replay. Embed in README and experimental setup. |
| 1. `development_event_outcomes.png` | Corrected FAST-LIO/Point-LIO truth-label and event-metric CSVs, seed-aligned | Plot one row per geometry seed with recovered, non-recovered, relapsed and unavailable states; add detections and false-healthy markers in separate columns. Keep each backend's own truth labels. Embed after the development table. |
| 2. `development_recovery_timeline.png` | Verified development health/pose/error streams and frozen labels | Stack geometry score, causal state, truth-window translation/rotation, availability and accumulated drift. Mark fixed exit, truth confirmation and first alarm. Select examples by a stated rule (e.g. first seed in each outcome class), not attractive plots. Put in failure analysis. |
| 2. `development_threshold_tradeoff.png` | Both corrected threshold-candidate CSVs | Plot recovery sensitivity versus conditional initial false-healthy rate; identify chosen threshold and `NO_ALARMS`. Show development selection clearly; no final-data optimization. Put detailed plot in supplement and selected values in README. |
| 2. `split_and_gate.svg` | `SPLITS.csv`, accepted reviews and saved plan metadata | Draw development seeds 14–45 separately from four reserved final strata, with 12 eligible pairs per stratum and separate protocol/implementation gates. Do not generate held-out layouts to illustrate the split. |
| 2. `execution_accounting.png` | Native attempt receipts and accepted cohort audits | Distinguish planned slots, completed slots, cached reuse, interrupted attempts, retries, resets and missing outputs. Attempts are not independent events. Keep backend-specific accounting. |
| 3. Final per-stratum, delay, availability and paired-effect plots | Verified final analysis manifests/CSVs after execution | Use frozen event/geometry denominators and 10,000-draw stratified geometry bootstrap where specified. Show missing/non-recovered outcomes and interval availability. Avoid frame-level sample inflation and delay plots containing only successful cases without counts. |
| 3. Literature distinction matrix | Primary sources, sections/equations and actual final findings | Columns: local-motion truth, sustained translation+rotation, false healthy, delay, held-out strata, backend replication. Mark unverified cells; do not use checkmarks as proof of novelty. Put in Related Work. |

### Reproducible figure recipe

1. Work from a reviewed development manifest or verified final analysis output. Bind source hashes, role, backend, event IDs and exact definitions. Never read reference inside an online indicator.
2. Write a dedicated plotting script under `research_paper/experiments/src/`; proposed names above describe exports, not existing CLI commands. Plot computed metrics; avoid duplicating selection or recovery logic inside plotting code.
3. Export PNG for README and SVG/PDF for manuscript. Use consistent backend colors, SI units, visible unavailable regions, legible fonts, exact counts and an explicit development/final label.
4. Store a sidecar manifest containing input/script/output hashes, runtime/library versions, selection rule and uncertainty unit. Include a source table where useful. Follow the existing development comparison manifest as a model.
5. Render and inspect every export for clipped footnotes, legends, axes and grayscale readability. Validate plotted counts against the source CSV/manifests.
6. Add the exact successful reproduction command and caption to `figures/README.md`; embed only the useful overview figures in the research README. Keep bulk outputs ignored. Any edits to frozen scripts or evidence require a reviewed successor bundle.

For an unchanged existing comparison script, reproduce into a **new directory** rather than overwriting the accepted exports. With the current research Python and Matplotlib installed:

```bash
RESEARCH_PY='/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python'
"$RESEARCH_PY" research_paper/experiments/src/plot_development_signal_comparison.py \
  --output-dir research_paper/experiments/generated/figure_drafts/comparison_review
"$RESEARCH_PY" research_paper/experiments/src/plot_repeatability.py \
  --audit research_paper/evidence/primary_recovery_repeatability_20261009.json \
  --output-dir research_paper/experiments/generated/figure_drafts/repeats_review
```

These are supported reproduction commands; this audit did not rerender the accepted figures. The existing scripts and manifests were preserved.

## Completion and novelty judgment

The engineering implementation milestone has passed. The research is **not complete**: held-out measurements, frozen analysis, result-dependent novelty review and manuscript completion are pending. A passed test suite, hash inventory or review gate cannot establish a research contribution by itself.

[OCE's publisher paper](https://link.springer.com/article/10.1007/s43684-026-00144-1) already includes local-motion usability, detection errors, hysteresis and recovery delay. The supported candidate is a controlled external transfer/replication evaluation across untouched corridor dimensions, with sustained joint motion outcomes. This may yield a useful empirical finding, including a documented failure to transfer; it is not an achieved novelty claim. No OCE implementation/comparison exists here. A full literature refresh and assessment of actual final findings are still required.
