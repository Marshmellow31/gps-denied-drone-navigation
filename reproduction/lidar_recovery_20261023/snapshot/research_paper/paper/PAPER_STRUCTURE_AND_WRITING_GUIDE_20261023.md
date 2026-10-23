# Paper structure and first-author writing guide

Prepared 23 October 2026 for Harshil Patel, Daksha Lingampeta and Nisarg Vyas.

This is a proposed writing blueprint based on the existing project. It is not a manuscript, an independent novelty verdict, a new experimental protocol, or a submission. No scientific result or frozen artifact was changed to prepare it.

## 1. What we are writing

We are preparing an **empirical evaluation paper**: a paper that carefully measures the behavior and limitations of existing methods. Its value must come from what the measurements teach a reader.

The subject is the reliability of existing LiDAR health decisions after a difficult corridor. The existing LiDAR–IMU estimators are FAST-LIO and Point-LIO. We instrumented them, applied two diagnostic families, and evaluated their decisions against separately generated simulated reference motion.

The archived safe-landing prototype is a different study. Its landing accuracy, terrain experiments, low-cost ToF sensor and Raspberry Pi goals do not belong in this paper's experimental results. Physical drone operation, cameras and navigation controllers are outside this paper's scope.

### One-sentence research question

> When a LiDAR–IMU system leaves a corridor with weak geometric constraints, how reliably do fixed geometric health policies identify sustained accurate local motion on fresh corridor layouts?

### Proposed working title

**Fixed Geometric Health Decisions after LiDAR Degeneracy: A Controlled Transfer Study in Two LIO Backends**

Plain-English meaning: we tested whether existing warning rules still work when the corridor dimensions change, using two existing motion-estimation systems. The title is provisional; it makes no claim of being the first study or proposing a new detector.

### Candidate contribution, subject to scientific review

> We evaluate development-calibrated geometric health policies on fresh, geometry-screened corridor/control pairs in two LiDAR–IMU estimators. We quantify premature healthy decisions, missed recovery declarations, detection delay and availability against sustained reference-defined local-motion accuracy, and examine the observed policy failure patterns.

The experiments are new evidence from this project. Whether the findings add enough beyond previous literature for publication remains unresolved. Adding two systems or many metrics is not, by itself, a scientific contribution.

## 2. What is already available

| Project material | Verified documented state | Role in the paper |
| --- | --- | --- |
| Research question and scope | LiDAR recovery-reliability study; simulation is primary quantitative evidence | Introduction and scope |
| Development experiments | 32 paired corridor/control development geometries; separate backend calibration and accepted development analyses | Methods and threshold-selection description |
| Revised final evaluation | 48 geometry pairs, four fixed groups, 12 pairs per group; 64 candidates screened | Experimental design |
| Native final runs | 48 geometries × two scenes × two estimators = 192 completed native runs | Completion and provenance |
| Final analysis | Both backends report `CONFIRMATORY_COMPLETE`; result-accounting audit passed | Results and uncertainty |
| Failure investigation | All 96 corridor events examined; 192 diagnostic event rows reproduced | Exploratory failure analysis |
| Figures | Operating points, group results, event ledger, paired error effects, failure overview and 15 illustrative timelines | Main figures and supplement |
| Main manuscript | Proposal abstract only | Must be written |
| Separate methods draft | Useful equations and definitions; stale pending-work statements and incomplete related work | Source material to revise, not submission-ready text |
| Professor briefing | Illustrated eight-page PDF from 19 October | Teaching/background material, not the manuscript |
| Novelty assessment | Candidate contribution, closest-work matrix and claim map exist | Basis for an argument; no independent novelty acceptance |

**192 runs are not 192 independent geometries.** There are 48 shared final geometry clusters. The two scenes are paired, and the two estimators receive matching input bags. The 192 diagnostic event rows are repeated analyses of those shared geometries, not another 192 experiments.

Older root README, STATUS and CURRENT_HANDOFF statements are historical and partly frozen. The dated final evidence and current research README supersede their pending-stage descriptions. Do not rewrite frozen files just to make their prose current.

## 3. The argument the reader should follow

1. A robot needs to know whether its current movement estimates are trustworthy.
2. Corridors can weaken geometric constraints; leaving a corridor does not automatically certify accurate motion.
3. Existing research already studies degeneracy, local-motion usability and recovery. Our introduction must acknowledge that.
4. We test fixed policies calibrated on development layouts, then apply them unchanged to fresh layouts under the revised screened design.
5. The policies exhibit different premature-health and missed-declaration trade-offs. Aggregate numbers can hide group differences.
6. A missed new declaration sometimes occurs even while health is already active. Decision semantics matter.
7. These findings apply to the recorded simulation design. They do not establish universal reliability, a new detector, real-world recovery or flight safety.

This is the scientific argument. The installation history, successive debugging sessions and every review gate do not need to become the main narrative. Relevant design changes, exposure and failure disclosures still belong in the protocol/reproducibility sections.

## 4. Proposed paper structure

Use this logical structure before choosing a venue template. Section names and lengths can change later. Each section below states its purpose, our content and the existing evidence to use.

### Title, author details and keywords

The title should tell the reader what was tested and the scope. Confirm author order, affiliations, corresponding author and contributions with all coauthors; current file order is not evidence of a final authorship agreement. Do not invent affiliations or funding.

Possible keywords: LiDAR-inertial odometry; geometric degeneracy; recovery assessment; diagnostic reliability; threshold transfer; controlled simulation.

### Abstract — the whole study in one short paragraph

**Reader's question:** What problem did you study, how did you test it, what did you find, and why does it matter?

Write the abstract last. For an initial draft, aim for roughly 180–250 words, then follow the selected venue's limit. This is a drafting suggestion, not a publisher requirement.

Use five parts:

1. Problem: geometric health does not automatically establish sustained accurate local motion.
2. Question: how fixed policies transfer to fresh corridor layouts.
3. Design: two existing estimators, 48 matched geometry pairs, locked policies and offline reference-based recovery.
4. Main result: one or two decisive numerical trade-offs with clear denominators.
5. Meaning and scope: limitations of these fixed decisions in the evaluated simulated design.

Do not paste the proposal abstract: it describes planned work. Avoid a list of every result, a claim of universal safety, or a promise that the study is novel before the comparison is settled.

### 1. Introduction — why this question deserves attention

**Reader's question:** Why should I care, and what do I learn from this paper?

Draft about five connected paragraphs:

1. Explain LiDAR–IMU motion estimation in environments where satellite positioning is unavailable.
2. Explain weak geometric constraints using the corridor example. Distinguish geometric information, accurate new motion, and accumulated position drift.
3. Describe the known work and the remaining question about fixed-policy transfer. OCE must appear here or in closely connected related-work prose.
4. Describe our controlled study and its scope: existing estimators, separate calibration, revised fresh geometry groups and matching controls.
5. State the candidate contributions and the practical lesson supported by the results.

Provisional contribution bullets for the draft:

- A controlled transfer evaluation of two existing diagnostic families in independently instrumented FAST-LIO and Point-LIO, using matched corridor/control sensor inputs.
- Event-level estimates of premature health, recovery declaration, delay, non-recovery and availability under locked definitions and operating points.
- An exploratory diagnosis of missed declarations that distinguishes threshold rejection, failed confirmation and already-active health.

These describe the work. The related-work argument must still establish why the resulting knowledge is distinct and useful.

Sources: [research goal](../RESEARCH_GOAL.md), [candidate contribution](../literature/CONTRIBUTION_ASSESSMENT_20261012.md), [claim map](../evidence/CLAIM_EVIDENCE_MAP_20261012.md).

### 2. Related work — what others already established

**Reader's question:** How does this differ from existing research?

Organize by ideas rather than one disconnected paragraph per paper:

| Theme | Papers to cover | Purpose |
| --- | --- | --- |
| Existing motion estimators | FAST-LIO2 and Point-LIO | Identify the systems used, with official publication and implementation citations |
| Geometric localizability and directional diagnostics | X-ICP, SuperLoc and DCReg | Explain inherited concepts and the specific diagnostic adaptation |
| Recovery, usable motion and estimator failure | OCE, ICA, LOFF and ALIVE-LIO | Acknowledge overlap in transitions, recovery and failure assessment |
| Geometry-dependent adaptation and benchmarking | AdaLIO and GEODE | Explain environmental dependence and the difference from broad dataset evaluation |

The project identifies OCE as the closest overlap. Its published paper evaluates ground-truth motion usability, recovery behavior and diagnostic performance. We cannot present those general concerns as our invention. See [OCE](https://link.springer.com/article/10.1007/s43684-026-00144-1).

End with a short, precise distinction: the candidate value lies in the observed fixed-policy transfer findings and decision failure patterns under our particular two-backend design. Do not argue that different window lengths or a larger metric list alone establish novelty.

Build a compact comparison table from the [closest-work matrix](../literature/CLOSEST_WORK_MATRIX_20261012.md). Recheck original sources, versions, bibliographic details and important claims before submission. This writing guide is not a new exhaustive literature search.

### 3. Problem formulation and outcome definitions — what counts as recovery

**Reader's question:** Exactly what are you measuring?

Explain the concepts in words before introducing notation:

- **Geometric health:** what accepted measurements tell the diagnostic about constraints.
- **Local-motion accuracy:** agreement between estimated and reference motion over a short interval.
- **Accumulated drift:** position/orientation error after one fixed pre-entry alignment.

Then define the relative pose error and its translation norm/rotation angle. Reference truth is used offline only. Local error does not require a fitted global alignment.

State the primary recovery rule explicitly: three consecutive non-overlapping one-second windows each within 0.20 m translation error and 5° rotation error, with the full triple confirmed within 20 seconds after the independently defined exit. These are operational research tolerances, not flight-safety requirements. Their adaptation from a registration-pair success criterion needs explanation.

Define exit, retrospective onset, truth confirmation, relapse, non-recovery and failed/incomplete execution. The operational label does not prove every event previously lost accuracy before the corridor exit.

**Put the endpoint distinction here, before results:**

| Outcome | Meaning |
| --- | --- |
| Active healthy state | The causal policy currently says healthy |
| New recovery declaration | A new transition into confirmed health after retrospective recovery onset |
| Missed recovery declaration | No qualifying new transition during the first recovery episode, even if health was already active |
| Initial false-healthy event | Health active during the protocol-defined interval before sustained recovery onset |

An initial false-healthy tick is not necessarily proof of a large instantaneous pose error. Sustained recovery is known retrospectively; some individual windows can already be accurate before the first qualifying triple. Avoid equating the frozen label with a physical safety verdict.

Include a simple timing diagram showing exit, three passing reference windows, onset, truth confirmation, causal decisions and a possible relapse. This would be a new explanatory figure, derived from the frozen rules, not new evidence.

Sources: [metrics](../protocol/METRICS.md), [data contract](../protocol/DATA_CONTRACT.md), [failure analysis](../evidence/final_failure_analysis_20261012/FAILURE_ANALYSIS_REPORT.md).

### 4. Diagnostic extraction and fixed decision policies — what we actually evaluated

**Reader's question:** How were health signals obtained without changing the estimators?

Describe four components:

1. Read-only native measurement exports, accepted point-to-plane rows, source timestamps and availability.
2. The normalized minimum-eigenvalue diagnostic, including accepted-count normalization and the fixed 3 m rotation lever scale.
3. The DCReg Schur detector adaptation, including the fixed directional ratio rule. It does not run full DCReg registration or mitigation.
4. The causal decision state machine: 10 Hz ticks, latest record no more than 0.2 s old, three distinct consecutive healthy records, and reset/unavailable handling.

Explain why Point-LIO needs a distinct adaptation: its measurement state changes within a frame, so rows are transported to a common basis before frame pooling. Its score is not a scan-end posterior covariance and is not numerically interchangeable with FAST-LIO's score.

Explain separate development-only threshold selection: maximize recovery-declaration sensitivity subject to the 10% conditional initial false-healthy ceiling; higher threshold resolves ties. The full candidate rule and no-feasible-point behavior go in the supplement if space is tight. The fixed DCReg rule is not tuned.

Record the locked scalar thresholds precisely in the reproducibility material: FAST-LIO 166.16366016039856 and Point-LIO 123.80876977779258. No final threshold was fitted. The 10% development constraint does not become a population reliability guarantee.

Sources: [indicator specification](../protocol/INDICATORS.md), [Point-LIO amendment](../protocol/POINTLIO_REPLICATION_AMENDMENT_20260929.md), [accepted development analysis](../evidence/DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md), [existing methods draft](methods_protocol_draft.tex). Check equations against the implementation rather than copying stale draft prose.

### 5. Experimental design and statistics — how the test was made fair

**Reader's question:** What was controlled, what changed, and what is the unit of evidence?

Suggested subsections:

**5.1 Simulator and motion.** Rectangular corridor/room geometry, formal x = −6 m start, 60-second runs, 0.8 m/s cruise with prescribed smooth 3D motion, 10 Hz LiDAR and 200 Hz IMU. Record ray timing, noise/bias assumptions and separately generated reference. The simulated sensor model is not a calibrated physical device.

**5.2 Development and final groups.** The 32 development geometries use central dimensions; final groups use short/long × narrow/wide parameter ranges. There are 12 eligible pairs per group. Existing source uses half-width: label it explicitly. If displaying full width, multiply the bounds by two and identify that conversion.

| Final group | Corridor length | Corridor half-width | Full width, if displayed | Selected pairs |
| --- | --- | --- | --- | ---: |
| Short/narrow | 8–9 m | 1.3–1.5 m | 2.6–3.0 m | 12 |
| Short/wide | 8–9 m | 2.5–3.0 m | 5.0–6.0 m | 12 |
| Long/narrow | 15–18 m | 1.3–1.5 m | 2.6–3.0 m | 12 |
| Long/wide | 15–18 m | 2.5–3.0 m | 5.0–6.0 m | 12 |

**5.3 Controls and eligibility.** Each geometry has a matched feature-added control with the same motion and byte-identical IMU. Both estimators receive matching bag identities. Geometry-only screening selected 48 pairs from 64 candidates before estimator outcomes. The axial-normal coverage criteria are eligibility proxies, not proof of observability or recovery.

**5.4 Design amendment and exposure.** The original screen failed; revised control spacing and fresh candidate pools were accepted before the fresh final estimator outcomes. Exclude original IDs 100–179, disclose the earlier-screen digest discrepancy, and retain the complete chronology in the supplement. Fresh instances do not make the design wholly untouched: the revision was informed by the earlier geometry screen. Final pose errors and health outcomes did not select scenes or change cutoffs.

**5.5 Outcome denominators and uncertainty.** Show planned/completed runs, eligible events, recoveries, false-healthy event denominators, diagnostic availability, and detected-only delay. Event proportions use Wilson 95% intervals. Continuous paired effects use per-geometry summaries and 10,000 bootstrap resamples of paired geometry seeds within fixed groups, with equal group weights. Do not count ticks or diagnostic rows as independent geometries or invent a significance test after seeing the data.

Sources: [simulation protocol](../protocol/SIMULATION.md), [accepted geometry amendment](../reviews/R2_GEOMETRY_AMENDMENT_20261012.md), [revised generator](../experiments/src/heldout_simulation_v2.py), [final execution ledger](../execution/GEOMETRY_V2_EXECUTION_20261012.md), [statistics implementation](../experiments/src/heldout_statistics.py).

### 6. Results — what happened

**Reader's question:** What are the actual observations, including failures and uncertainty?

Use this order:

1. Cohort completeness: 48 paired geometries, 192 completed native runs; distinguish retained preflight/analysis workflow failures from native scientific slots.
2. Reference-defined recovery: FAST-LIO 46/48 and Point-LIO 32/48; two and sixteen non-recoveries respectively; one relapse each.
3. Locked diagnostic performance, including counts, intervals, misses, delay and availability.
4. Four-group summaries and paired corridor-minus-control interior error.
5. Secondary sensitivity/threshold-free analyses, briefly in the main text and fully in the supplement.

Core draft table, to be typeset from the accepted exports:

| Estimator / diagnostic | Initial false-healthy, conditional | New recovery declarations / recovered | Missed declarations | Median delay among detections |
| --- | ---: | ---: | ---: | ---: |
| FAST-LIO / minimum eigenvalue | 1/46 | 14/46 | 32/46 | 0.850 s |
| FAST-LIO / fixed DCReg adaptation | 4/46 | 38/46 | 8/46 | 6.800 s |
| Point-LIO / minimum eigenvalue | 4/47 | 27/32 | 5/32 | 3.400 s |
| Point-LIO / fixed DCReg adaptation | 16/47 | 25/32 | 7/32 | 3.000 s |

Report unconditional initial false-healthy counts out of 48 alongside the conditional values. Existing operating-point figures use the unconditional denominator: captions and tables must make the distinction visible. Each diagnostic has 9,600/9,600 available primary horizon ticks; availability does not mean correctness.

A useful opening result sentence is:

> At its locked operating point, the FAST-LIO scalar policy produced one conditional initial false-healthy event among 46 eligible intervals, but declared recovery in only 14 of 46 recovered corridor events.

This connects the trade-off. Saying only “2.2% false alarms” or “0.85 s response” hides essential information.

The paired interior translation effects are +0.194 m [0.086, 0.311] for FAST-LIO and +0.149 m [0.068, 0.230] for Point-LIO, corridor minus control, with geometry-bootstrap 95% intervals. These are conditional design estimates, not a test of superiority between estimators.

Sources: [accepted results](../evidence/final_geometry_v2_results_20261012/RESULTS_REPORT.md), [method CSV](../evidence/final_geometry_v2_results_20261012/method_summary.csv), [group CSV](../evidence/final_geometry_v2_results_20261012/stratum_summary.csv), [accounting audit](../reviews/FINAL_GEOMETRY_V2_RESULT_AUDIT_20261012.md).

### 7. Exploratory failure analysis and discussion — what the observations mean

**Reader's question:** What should I learn, and what remains unexplained?

Make the separation explicit: primary endpoints/calculations were fixed before final outcomes; the failure categorization, selected illustrations and emphasized explanations were developed afterward.

Use all-event miss partitions:

| Policy | No raw healthy tick | Raw health without confirmation | Active state without new declaration | Total misses |
| --- | ---: | ---: | ---: | ---: |
| FAST scalar | 30 | 2 | 0 | 32 |
| FAST fixed Schur | 5 | 2 | 1 | 8 |
| Point scalar | 3 | 0 | 2 | 5 |
| Point fixed Schur | 2 | 0 | 5 | 7 |

Explain that “no new recovery declaration” does not always mean “the policy remained unhealthy.” Show an example with an already-active signal and a separate example with persistent threshold rejection. If the application needs continuous permission rather than a new transition, that motivates a different endpoint for future work; it does not justify replacing the frozen headline after seeing outcomes.

Discuss group heterogeneity with caution. Point-LIO's narrow/wide recovery contrast is descriptive, and emphasizing width is exploratory. Do not claim width is the established cause. Accepted measurement counts alone did not explain misses in the displayed group summaries; this does not rule out correspondence quality, geometry directions, map history or bias effects.

Compare the findings back to OCE/DCReg/ICA without claiming to beat systems that were not run. Give the practical interpretation: geometric constraint information and a policy declaration must be evaluated against the accuracy claim the application actually needs.

Source: [all-event failure report](../evidence/final_failure_analysis_20261012/FAILURE_ANALYSIS_REPORT.md). The deterministic lowest-seed illustration rule was selected after results; describe it as transparent example selection, not prespecified confirmatory evidence.

### 8. Limitations and validity — where the evidence stops

**Reader's question:** When might these findings fail to apply?

Include these concrete limits:

- Controlled rectangular straight corridors, one prescribed motion family and a specific sensor/noise profile; no claim of arbitrary environment transfer.
- Ideal clocks/extrinsics and simplified surfaces; no reflectivity, material or weather model, and no physical sensor validation.
- Geometry-conditioned selection and an explicitly revised control design informed by a failed earlier screen.
- Only 48 final geometries, 12 per group; group estimates are uncertain. One relapse per backend cannot establish relapse reliability.
- Own-backend recovery labels and separately adapted measurement stages; no universal estimator leaderboard.
- DCReg detector adaptation only; no shared benchmark against full DCReg, OCE, X-ICP or SuperLoc.
- Recovery-declaration endpoint differs from active-state usability. Operational post-exit accuracy is not proof every event previously lost accuracy.
- Detection delay conditions on successful declarations. Misses must remain visible.
- Scalar false-healthy 95% upper bounds exceed 10%; the development ceiling does not establish a final population guarantee.
- Hilti's usable sustained reference is inadequate for primary independent real-world recovery evidence. GEODE failures remain historical failures.
- Existing AI-assisted/internal acceptance reports are scoped implementation/accounting checks, not journal peer review or publication-novelty approval.
- A Git clone contains compact evidence, not all native environments, raw bags and external streams.

These limits should also shape the abstract and conclusion; placing them only at the end cannot repair an overstated headline.

### 9. Conclusion — the answer we can defend

**Reader's question:** What was learned from this specific study?

Use one short paragraph answering the research question: fixed geometric policies had distinct premature-health/missed-declaration behavior in the evaluated design; behavior varied across groups/backends; declaration timing and active-state semantics require care. Name the simulation scope and the most justified next validation step.

Do not introduce a new result or claim a physical mechanism, new detector, guaranteed reliability or flight readiness.

### Reproducibility, declarations, references and supplementary material

**Reproducibility:** identify the exact code revision, accepted protocol versions, configurations, thresholds, source/binary identities, RNG/split rules, environment and commands. Explain what is public and what remains external. Preserve failure receipts. A planned artifact release is not an available public dataset until released and checked.

**Declarations:** confirm real human contributions, affiliations, funding/conflicts and acknowledgments. Document AI assistance accurately according to the selected venue. COPE states that AI tools cannot be authors and that humans remain responsible for the content; do not present generated text, citations or automated reviews as independently validated science. [COPE guidance](https://doi.org/10.24318/cCVRZBms).

**References:** build a verified bibliography from original papers and official records. Check titles, authors, years, publication versions and DOI/arXiv links. The methods draft's five entries are insufficient for the planned related-work section.

**Supplement:** detailed derivations, full configurations/noise settings, exact splits, screening history, all event rows, all 15 timelines, repeatability, sensitivity/ROC/AP results, reset/unavailable rules, workflow failures, unresolved historical digest disclosure and detailed reproduction instructions. Hilti and GEODE development history can be summarized here. Dataset images require appropriate credit and license checks before reuse.

## 5. Figure and table plan

Start with a small set that tells the argument. The repository retains more illustrations than the main article needs.

| Item | Reader purpose | Existing source or required work |
| --- | --- | --- |
| Figure 1: dimensioned corridor/control and evaluation flow | Understand scene, motion, geometry change and offline truth separation | New explanatory schematic using accepted revised geometry; do not imply physical flight |
| Figure 2: recovery and declaration timing | Understand onset, confirmation and active state versus new declaration | New conceptual diagram from frozen metrics |
| Figure 3: locked operating points | See premature health, missed recovery, delay and availability together | `figures/final_geometry_v2_results_20261012/final_operating_points.png` |
| Figure 4: group behavior | See differences hidden in pooled numbers | `figures/final_geometry_v2_results_20261012/final_stratum_events.png` |
| Figure 5: failure explanation | See the all-event miss partition and a small number of aligned native examples | `figures/final_failure_analysis_20261012/failure_patterns.png` and selected existing timelines; simplify for print with provenance preserved |
| Figure 6, if space permits: paired error | See the paired corridor/control effect and geometry uncertainty | `figures/final_geometry_v2_results_20261012/final_paired_geometry_effect.png` |
| Table 1: closest work | Assess candidate distinction | Compact version of closest-work matrix |
| Table 2: design/settings | Know the sample, factors and locked policies | Frozen protocol plus revised generator/configurations |
| Table 3: primary results | Read exact counts, intervals, misses and conditional delay | Accepted JSON/CSV exports |
| Supplement: complete event ledger | Inspect every geometry and secondary endpoint | Existing final event ledger figure and exported event rows |

Check figures at the actual printed size. Existing native timelines have five panels and need larger space or careful simplification. Use explicit units, denominator labels and uncertainty definitions. Do not redraw a plot from manually copied approximate values when its source export exists. Keep original figures and manifests; save manuscript adaptations separately.

## 6. How to write the paragraphs

A research paragraph normally has a point, supporting evidence or citation, and an interpretation limited to that evidence. Prefer concrete verbs and exact objects.

| Weak or misleading sentence | Better sentence |
| --- | --- |
| Our system is highly reliable. | In the evaluated final geometries, the FAST-LIO scalar policy detected 14 of 46 reference-defined recoveries. |
| Our method recovers in 0.85 seconds. | Among the 14 detected FAST-LIO scalar events, median declaration delay was 0.850 s; 32 recovered events had no qualifying declaration. |
| DCReg fails in corridors. | The fixed Point-LIO DCReg detector adaptation produced 16 conditional initial false-healthy events among 47 eligible intervals in this screened simulation design. |
| Width causes Point-LIO failure. | Point-LIO recovered in 24/24 narrow and 8/24 wide layouts; this post-result contrast motivates a hypothesis rather than establishing a cause. |
| We propose a novel recovery detector. | We evaluate existing geometric diagnostics and their fixed decision policies against sustained local-motion accuracy. |

Use present tense for definitions and interpretation, past tense for what was executed, and future tense only for genuinely proposed work. Explain symbols before using them. Cite inherited ideas, equations and methods; link our empirical claims to the accepted evidence during drafting. Keep debugging chronology in the artifact history unless it affects validity.

## 7. Writing order and concrete deliverables

The reader's section order is different from the easiest writing order.

| Step | Work | Completion condition |
| --- | --- | --- |
| 1 | Agree on question, candidate contribution and section outline | The paper has one clear argument and no unsupported headline |
| 2 | Draft the core result table and captions | Every number matches accepted exports; all denominators are explained |
| 3 | Draft definitions, diagnostics and experimental design | Another researcher can understand what was measured and how |
| 4 | Draft results | Counts, intervals, misses, non-recoveries and availability are reported together |
| 5 | Draft failure analysis, discussion and limitations | Prespecified estimates and post-result interpretations are clearly separated |
| 6 | Refresh related work and draft introduction | The precise distinction is defensible against the closest sources |
| 7 | Draft conclusion, then abstract/title | Both match the actual evidence and scope |
| 8 | Complete bibliography, declarations and artifact inventory | Citations, human details and availability claims are checked |
| 9 | Obtain coauthor/professor scientific criticism | Specific objections are recorded and addressed; publication novelty is assessed rather than assumed |
| 10 | Select target format, compile and inspect the full paper | Readable PDF, consistent figures, complete source and compliant submission materials |

We can write the existing-evidence draft now. It need not wait for another batch of experiments. A new comparator, a causal width claim, or real-world generalization would require additional justification and potentially new evidence. Any fresh confirmatory study must be designed and frozen before generating new evaluation outcomes; current final data are already exposed.

## 8. How publication works, in simple English

A **manuscript** is the paper we write. A **venue** is the journal or conference to which we submit it. **Peer review** means subject experts evaluate the research for that venue. An internal PASS or a compiled PDF is not a publication acceptance.

### Step A: create a complete scientific draft

Write the evidence-supported paper and resolve the main contribution argument with coauthors/professor feedback. A useful complete draft makes the remaining weaknesses visible.

### Step B: choose a suitable venue

Shortlist outlets that actually publish empirical robotics/localization evaluations and consider simulation-only evidence. Compare recent accepted papers, scope, article type, page limits, anonymity, artifact policies, fees and deadlines. A journal is a continuing publication; a conference is associated with an event and usually a submission cycle. Exact review and presentation requirements depend on the venue.

No venue is selected or recommended by this guide. Choose the target before polishing the final layout. Assess the finished contribution rather than choosing solely by a prestige label, an indexing claim, speed or a promised acceptance.

### Step C: prepare the submission package

Follow the selected venue's current instructions: manuscript/template, bibliography, figures, supplement, author metadata, required declarations, any cover letter and any anonymized artifact links. Obtain all coauthors' approval. Check funding before committing to a publishing option. Fees depend on the outlet and publishing model; IEEE's open-access information is an example, not a fee quote for our future paper. [Official APC information](https://open.ieee.org/for-authors/article-processing-charges/).

### Step D: submit and undergo review

The editor first assesses suitability; expert review, if invited, examines contribution, validity, data and clarity. IEEE describes these criteria in its [peer-review explanation](https://journals.ieeeauthorcenter.ieee.org/submit-your-article-for-peer-review/about-the-peer-review-process/). Other venues have their own processes.

Submit to one venue at a time unless an explicitly applicable policy permits otherwise. Check disclosure requirements for related versions and prior public material. [IEEE submission policies](https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/).

### Step E: respond to the decision

Possible outcomes include rejection, requests for revision, and acceptance. For a revision, answer every reviewer point, state what changed and where, and explain disagreements with evidence. A rejection can reveal either fixable weaknesses or a fundamental contribution/scope problem. [IEEE's decision guide](https://journals.ieeeauthorcenter.ieee.org/submit-your-article-for-peer-review/understanding-the-decision-process/) explains these outcomes.

### Step F: complete production after acceptance

Supply requested final files, check proofs, resolve the publishing agreement and applicable charges, and retain the accepted source/artifact version. Acceptance is a venue decision; writing quality, payment or internal checks cannot guarantee it.

### A preprint is a separate choice

A preprint is a publicly shared manuscript; it is not journal/conference acceptance. arXiv explicitly distinguishes moderation from peer review. Check the target venue's preprint/anonymity policy and coauthor approval before posting. [arXiv moderation](https://info.arxiv.org/help/moderation/index.html). No posting, submission, payment or external contact is performed by preparing this guide.

## 9. Remaining questions that matter scientifically

These are draft/review questions, not assumptions that automatically require new experiments:

1. Is the observed fixed-policy transfer limitation sufficiently distinct and useful beyond OCE, DCReg and ICA?
2. Is a new recovery declaration the right primary endpoint for the intended use, and does the paper explain active-state behavior fairly?
3. Is the current DCReg adaptation an adequate comparison for the narrow empirical claim, or does the claim require a closer faithful comparator?
4. Can the contribution stand without a causal explanation of the width pattern? The existing evidence supports descriptive findings; a mechanism claim requires more.
5. Does a prospective outlet accept the limited simulation scope, and what artifact availability would it require?

The next concrete deliverable is a complete evidence-backed first draft, with unresolved scientific questions clearly marked. Additional experiments should answer a specific objection rather than simply increase the run count.

## 10. Review scope and source map

This guide draws on the repository instructions and execution plan; scope/goals and simulation amendment; current and historical handoffs; research README; frozen metrics/data/indicator protocols; revised geometry amendment and implementation freeze; development acceptance; final results, CSV exports and result-accounting review; all-event failure report; closest-work/contribution/claim assessments; figure inventory; existing main/methods drafts; and professor-briefing documentation. Representative generator, diagnostic and statistical source paths were inspected to anchor terminology and the half-width distinction. The operating-point figure and Point-LIO 10002 timeline were visually inspected.

It is a document/evidence synthesis, not a new full source-code audit, an exhaustive reading of every historical log, an independent reanalysis of raw external streams, a fresh regression-test run or a systematic novelty search. The recorded completion counts are checked against the current compact reports; the native experiments were not rerun.

Primary local entry points:

- [Current research overview](../README.md)
- [Final accepted result report](../evidence/final_geometry_v2_results_20261012/RESULTS_REPORT.md)
- [Independent result-accounting audit](../reviews/FINAL_GEOMETRY_V2_RESULT_AUDIT_20261012.md)
- [Exploratory failure analysis](../evidence/final_failure_analysis_20261012/FAILURE_ANALYSIS_REPORT.md)
- [Claim-to-evidence map](../evidence/CLAIM_EVIDENCE_MAP_20261012.md)
- [Candidate contribution](../literature/CONTRIBUTION_ASSESSMENT_20261012.md)
- [Closest-work comparison](../literature/CLOSEST_WORK_MATRIX_20261012.md)
- [Figure inventory](../figures/README.md)
- [Main proposal manuscript](main.tex)
- [Preliminary methods draft](methods_protocol_draft.tex)
- [Professor briefing documentation](../briefings/README.md)

Official publishing guidance linked above was accessed on 23 October 2026. The section structure and drafting suggestions are project-specific recommendations; the eventual venue's instructions govern submission.
