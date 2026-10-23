# Completion plan for the research paper

User objective, 27 September 2026: finish the LiDAR recovery-reliability paper,
produce defensible publishable results, and preserve every visualization.
This extends execution beyond the original T01–R3 implementation plan.
The full objective remains open until experiments, interpretation and the
manuscript are complete and verified together.

## Requirements and evidence

| Requirement | Evidence needed for completion | Current state |
| --- | --- | --- |
| A defensible contribution relative to closest work | Updated primary-source comparison, precise supported claim, explicit overlaps and independent claim review | The 9 Oct OCE paper already evaluates ground-truth local-motion usability and recovery delay. An independent review passed feasibility only for the narrower transfer across untouched corridor length/width strata and two-backend replication question; publication novelty remains unproven. See the 10 Oct addendum/review. |
| Trustworthy primary implementation | All R3 repair checks, quantitative repeats, complete-stream/failure/resume tests, reviewed source and runtime identities | Corrected FAST-LIO and Point-LIO final runners/analyses now target the same screened 48 pairs. The full 143-entry candidate inventory is awaiting fresh independent R3 review; no final exposure is authorized. |
| Untouched final evaluation | R3 PASS, geometry-only selection ledger, 48 paired layouts, all attempts and compact outputs, locked threshold, no final-data tuning | No held-out geometry or result has been opened |
| Faithful signal comparison | FAST-LIO information signal and documented DCReg detector adaptation with numerical fidelity and parity evidence | FAST-LIO and Point-LIO development analyses use their own poses/signals and the frozen outcome rule. Corrected full-score candidate inventories are independently accepted; development thresholds remain separate |
| Second-backend replication | Comparable instrumented Point-LIO signal definitions, development validation and separate freeze before replication results | Point-LIO one-seed review, 32-pair development cohort, corrected own-pose analysis and separate freeze passed independent review. A same-pair final replication runner is implemented, not yet independently accepted or run. |
| Honest statistical analysis | Frozen event/availability denominators, relapse and delay results, uncertainty by geometry cluster, paired control analysis and failures | Development metrics, labels, repeatability and sample-size planning are recorded with full denominators. Final analysis and uncertainty package remain unrun and gated |
| Saved figures at every analysis stage | Exported data plots, source scripts and input hashes; PNG plus vector/PDF exports where appropriate; descriptive versus final labels | Primary repeatability and corrected development-signal figures are saved with scripts and hashes in PNG/PDF/SVG; all remain development-only |
| Complete manuscript | Introduction, related work, formulation, methods, experimental protocol, results, failure analysis, limitations, conclusion, references and reproducibility statement | Main LaTeX file still contains a proposal abstract |
| Verified professor/submission package | Compiled PDF, visual inspection, citation/claim audit, reusable commands, figure/evidence inventory and plain-English explanation | Awaiting final evidence and manuscript |

## Order of work

1. Complete the primary final runner/analysis review and update the exact R3
   inventory to use the corrected development manifests, and submit the full
   FAST-LIO plus Point-LIO implementation package for R3 acceptance. The final
   geometry/input/result gate stays closed until R3 PASS and both backend
   freezes are recorded. Preserve the accepted native producer snapshot when
   preparing final-interface code.
3. After primary R3 PASS and the replication development freeze, screen
   reserved layouts using the frozen geometry rules. Execute the 48 paired
   primary tests and reviewed replication. Preserve incomplete samples and
   technical attempts; never replace an unfavorable result or recalibrate
   on final outcomes. Freezing both backend adaptations before final-layout
   exposure avoids selecting a replication method after seeing primary test
   outcomes.
4. Apply the frozen primary analysis, report interval estimates and failures,
   and save plots and the data behind them. Assess what changes across scene
   strata and backends without turning final outcomes into tuning inputs.
5. Refresh the closest-work search and audit the actual contribution against
   primary papers. Derive the manuscript's claim from the evidence. If an
   additional study is necessary for that claim, design and freeze it with
   fresh untouched data before execution; do not retrofit the existing test.
6. Complete the manuscript, compile and inspect the PDF, check citations and
   every numerical/visual claim, and produce the professor review package.

## Completion rules

The paper is complete only when the requirements above have direct current
evidence. A green test suite, R3 PASS, a proposal PDF or 32 development
recoveries alone cannot close the goal. Publication acceptance cannot be
guaranteed; the deliverable is a complete, reproducible manuscript with a
precise evidence-supported contribution suitable for external review.

Keep the active scope: LiDAR/IMU recovery indicators, existing estimators,
public recordings and controlled simulation. Preserve the archived landing
prototype separately. No aircraft operation, cameras or navigation controller
is required for this paper. Do not submit the paper or contact reviewers on
the user's behalf without an explicit request.

Every figure used or inspected during analysis should be retained with its
script and data identity. Preserve intermediate drafts under ignored
`experiments/generated/figure_drafts/`; keep deliberate public exports under
`figures/` with a provenance manifest. Final figures must identify units,
denominators, independent sample units and missing-data behavior.
