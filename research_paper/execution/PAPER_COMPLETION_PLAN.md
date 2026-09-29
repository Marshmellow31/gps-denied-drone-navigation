# Completion plan for the research paper

User objective, 27 September 2026: finish the LiDAR recovery-reliability paper,
produce defensible publishable results, and preserve every visualization.
This extends execution beyond the original T01–R3 implementation plan.
The full objective remains open until experiments, interpretation and the
manuscript are complete and verified together.

## Requirements and evidence

| Requirement | Evidence needed for completion | Current state |
| --- | --- | --- |
| A defensible contribution relative to closest work | Updated primary-source comparison, precise supported claim, explicit overlaps and independent claim review | A 28 Sep audit found exit/recovery detectors and a 2026 health-versus-error study; only a sustained, exit-conditioned accuracy/timing comparison across unseen scenes remains a candidate, still unproven |
| Trustworthy primary implementation | All R3 repair checks, quantitative repeats, complete-stream/failure/resume tests, reviewed source and runtime identities | FAST-LIO software and lifecycle are independently accepted. Point-LIO implementation passes the 161-test suite (160 pass, one optional skip) and its bounded workflow review passed. Sidecar-off completed, but sidecar-on failed before bag delivery; seed-14 acceptance and 32-pair development replication remain outstanding. R3 remains REVISE and no implementation freeze exists |
| Untouched final evaluation | R3 PASS, geometry-only selection ledger, 48 paired layouts, all attempts and compact outputs, locked threshold, no final-data tuning | No held-out geometry or result has been opened |
| Faithful signal comparison | FAST-LIO information signal and documented DCReg detector adaptation with numerical fidelity and parity evidence | T13 FAST-LIO implementation exists. Point-LIO adaptation is implemented, but native one-seed parity and development-replication evidence remain incomplete |
| Second-backend replication | Comparable instrumented Point-LIO signal definitions, development validation and separate freeze before replication results | Pose-format smoke, accepted protocol and implementation fixtures exist; exact implementation review, seed-14 feasibility acceptance, 32-pair replication and separate freeze remain incomplete |
| Honest statistical analysis | Frozen event/availability denominators, relapse and delay results, uncertainty by geometry cluster, paired control analysis and failures | Development analysis exists; final analysis absent |
| Saved figures at every analysis stage | Exported data plots, source scripts and input hashes; PNG plus vector/PDF exports where appropriate; descriptive versus final labels | Existing figures retained; repeat figures added in PNG/PDF/SVG |
| Complete manuscript | Introduction, related work, formulation, methods, experimental protocol, results, failure analysis, limitations, conclusion, references and reproducibility statement | Main LaTeX file still contains a proposal abstract |
| Verified professor/submission package | Compiled PDF, visual inspection, citation/claim audit, reusable commands, figure/evidence inventory and plain-English explanation | Awaiting final evidence and manuscript |

## Order of work

1. Point-LIO is the remaining readiness gate. Its source-derived adaptation
   is independently accepted as an R2 protocol amendment (D050), and analytic/
   contract fixtures plus a read-only sidecar are now implemented. The complete
   experiment suite passes with the native reset fixture enabled and the
   bounded workflow review passed. The first sidecar-on run failed before bag
   delivery, so diagnose that startup failure and process-group cleanup before
   retrying the retained seed-14 on/off feasibility pair in a fresh output
   directory. Do not fit a threshold. Only after one-seed acceptance may the
   32-pair development replication run, using Point-LIO's own poses and its
   separately selected development threshold. A pose-only replay does not
   satisfy replication.
2. After Point-LIO indicator development and the separate replication freeze,
   submit the accepted FAST-LIO native evidence and complete implementation
   package for final R3 acceptance. The exact T14 binary hash matched, and the
   supervised lifecycle verified playback, shutdown, output flush,
   post-processing and cached resumption. Preserve all run files and source
   identities. Held-out work remains gated until the implementation freeze.
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
