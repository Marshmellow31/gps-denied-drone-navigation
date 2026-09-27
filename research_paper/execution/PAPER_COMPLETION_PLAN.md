# Completion plan for the research paper

User objective, 27 September 2026: finish the LiDAR recovery-reliability paper,
produce defensible publishable results, and preserve every visualization.
This extends execution beyond the original T01–R3 implementation plan.
The full objective remains open until experiments, interpretation and the
manuscript are complete and verified together.

## Requirements and evidence

| Requirement | Evidence needed for completion | Current state |
| --- | --- | --- |
| A defensible contribution relative to closest work | Updated primary-source comparison, precise supported claim, explicit overlaps and independent claim review | R1 supports feasibility only; final novelty claim remains unproven |
| Trustworthy primary implementation | All R3 repair checks, quantitative repeats, complete-stream/failure/resume tests, reviewed source and runtime identities | Repairs underway; initial R3 review is REVISE |
| Untouched final evaluation | R3 PASS, geometry-only selection ledger, 48 paired layouts, all attempts and compact outputs, locked threshold, no final-data tuning | No held-out geometry or result has been opened |
| Faithful signal comparison | FAST-LIO information signal and documented DCReg detector adaptation with numerical fidelity and parity evidence | T13 development implementation exists |
| Second-backend replication | Comparable instrumented Point-LIO signal definitions, development validation and separate freeze before replication results | Only pose-format smoke exists; indicator parity and replication remain incomplete |
| Honest statistical analysis | Frozen event/availability denominators, relapse and delay results, uncertainty by geometry cluster, paired control analysis and failures | Development analysis exists; final analysis absent |
| Saved figures at every analysis stage | Exported data plots, source scripts and input hashes; PNG plus vector/PDF exports where appropriate; descriptive versus final labels | Existing figures retained; repeat figures added in PNG/PDF/SVG |
| Complete manuscript | Introduction, related work, formulation, methods, experimental protocol, results, failure analysis, limitations, conclusion, references and reproducibility statement | Main LaTeX file still contains a proposal abstract |
| Verified professor/submission package | Compiled PDF, visual inspection, citation/claim audit, reusable commands, figure/evidence inventory and plain-English explanation | Awaiting final evidence and manuscript |

## Order of work

1. Finish and test the R3 repairs, reproduce development analysis, quantify
   the retained repeats, restore the exact primary backend, and test one
   development replay through the final runner's lifecycle. Retain every
   failure and source identity. Request the required independent R3 re-review.
2. Complete Point-LIO indicator feasibility using development data and the
   same scientific question. Document any formulation differences. Require
   an independent protocol/implementation amendment before replication
   testing if a comparable adapter changes the agreed measurement contract.
   A pose-only replay does not satisfy replication.
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
