# Agent execution plan: LiDAR recovery-reliability study

Created: 22 September 2026. This is the original task specification, not a live completion record. Work and blockers through 23 September are in the [current handoff](execution/CURRENT_HANDOFF.md) and [status ledger](execution/STATUS.md). Resume from those files; do not restart T01 or treat the historical GEODE choice as the current dataset plan.

## 1. Objective and scope

Complete the first three milestones shown in the project schedule:

| Deadline | Required outcome |
| --- | --- |
| September 27 | Closest-work comparison, defensible candidate gap, eligible reference data, one transition pilot |
| October 4 | Frozen question, indicators, datasets/simulation assumptions, metrics and split policy |
| October 11 | Reproduced indicators, completed development experiments, frozen implementation |

The user gives instructions; agents perform research, implementation, experiments, checks and documentation. This plan packages that work into bounded tasks suitable for less capable models. It does not require the user to code, install software manually, or interpret raw logs.

The active scientific scope comes from [RESEARCH_GOAL.md](RESEARCH_GOAL.md) and [SCOPE_DECISION.md](SCOPE_DECISION.md). The root [AGENTS.md](../AGENTS.md) applies. The historical broad proposal in PLAN_REVIEW.md and the archived landing prototype are not the current implementation plan.

Question: after weak geometric constraints end, how reliably do existing LiDAR health indicators identify recovery of accurate local motion? Keep localizability, local-motion error and accumulated drift distinct. Use LiDAR/IMU recordings and controlled simulation. Do not build a navigation controller, purchase hardware, add camera inputs, or invent a new full estimator.

This file specifies the original sequence and acceptance checks. Some proposed artifacts below now exist; inspect the live ledger and files before deciding what remains. Backend commands, dataset identifiers, numerical thresholds and published-method equations must be verified during their assigned tasks; do not invent them from this plan.

## 2. How the user dispatches work

Use one task per model session. Paste the following prompt, replacing the task ID:

```text
Read AGENTS.md, research_paper/RESEARCH_GOAL.md,
research_paper/SCOPE_DECISION.md and research_paper/AGENT_EXECUTION_PLAN.md.
Execute task T01 only. Inspect its dependency artifacts before starting.
Implement and verify all work in that task; do not stop at advice or a plan.
Use the task's allowed scope and acceptance checks. Preserve unrelated work.
Do not invent facts, results, citations, commands or missing scientific decisions.
Do not inspect or tune against final-test outcomes. Do not expand the study.
Record outputs and exact verification results in execution/STATUS.md and
execution/handoffs/T01.md under research_paper. If genuinely blocked, record
the evidence and smallest decision needed. End with links to deliverables,
checks run, remaining limitations and the next eligible task ID.
```

For scientific review, use this prompt with a stronger model:

```text
Read the active research scope and AGENT_EXECUTION_PLAN.md. Execute review
task R1 only. Audit the actual linked evidence, code and checks rather than
trusting task completion summaries. Correct bounded problems directly.
Record PASS, REVISE or BLOCKED with evidence and exact repair task IDs.
Do not manufacture novelty or pass incomplete work. Do not run final tests.
```

Replace R1 with R2 or R3 at the later gates. Reviews are scientific quality checks, not routine user permission requests. A capable reviewer can resolve supported methodological choices within scope. Ask the user only for unavailable access, a material scope change, or constraints that cannot be inferred.

### Shared execution rules

- Read existing files before creating replacements. Work inside `research_paper/` except minimal root README links/status updates and necessary ignore rules.
- Leave `old_data/` untouched. Its results and held-out seeds do not supply evidence for this study.
- Each task finishes with evidence, not just a checked box. Status values: TODO, RUNNING, BLOCKED, DONE. DONE requires its acceptance checks.
- Keep an append-only decision/change record. Preserve failed attempts and failed runs.
- Published claims require primary-source links plus page/section/equation or code revision references. Record inaccessible material as unverified.
- Keep reference trajectories confined to offline evaluation. Indicators use only information available at their timestamp.
- Use isolated dependencies. Record exact successful commands and upstream revisions. Do not change the system Python or assume archived setup commands apply.
- Keep raw recordings, upstream builds and large generated outputs out of Git. Check available storage and published sizes before downloads; start with one eligible development sequence.
- Stop and diagnose a failed run before launching a batch. After two failed attempts with the same cause, record a concise blocker and work on independent tasks; do not spend repeated sessions guessing installation flags.
- Do not add frameworks, dashboards, extra backends or extra datasets simply to fill the layout. Add directories only when needed.

### Handoff format

Every `execution/handoffs/<ID>.md` must contain: task ID/status; dependencies inspected; files changed; sources/revisions; exact commands and outcomes; acceptance checklist; unresolved limitations; next eligible task. For blocked work, include the smallest reproducible error and next proposed action. Never include credentials.

## 3. Proposed artifact layout and interfaces

```text
research_paper/
  execution/STATUS.md              Task ledger: ID, status, dependency, evidence
  execution/DECISIONS.md           Dated choices, rationale and amendments
  execution/handoffs/              One short handoff per task
  literature/                     Source notes, comparison matrix, gap decision
  data/                           Eligibility inventory and split manifest only
  protocol/                       Contracts, metrics, preregistered development rules
  configs/                        Versioned backend and experiment configurations
  experiments/README.md           Verified setup and reproduction commands
  experiments/src/                Adapters, indicators, evaluation and plotting
  experiments/tests/              Small, independent verification fixtures
  experiments/generated/          Ignored logs, trajectories and bulk outputs
  evidence/                       Small reviewed manifests, tables and figures
  reviews/                        R1, R2 and R3 gate reports
```

Choose a minimal package/build arrangement during T06; do not pre-build empty modules. Upstream LIO dependencies may require ROS or native libraries in adapters; the offline evaluation layer should remain independently testable without a running backend.

T05 will finalize these interface requirements before implementation:

| Artifact | Required information |
| --- | --- |
| Run manifest | Run/sequence ID, development/test role, input hash, code revision and dirty state, upstream revision, full configuration, seed if applicable, environment, invocation, timestamps, runtime, status, warnings and output paths |
| Pose stream | Timestamp, declared clock, position in metres, explicit quaternion order and transform direction, frame IDs, validity, reset/segment ID |
| Indicator stream | Timestamp, method/version, raw value(s), validity and unavailable reason; decisions and thresholds recorded separately |
| Transition annotations | Event ID, entry/exit times, annotation method/evidence, reference coverage; independent of tested indicator and estimator-error peaks |
| Reference metadata | Source, coverage, accuracy/limitations, frames, calibration, synchronization and independence from estimator inputs |
| Evaluation output | Local translation/rotation error, fixed-alignment accumulated drift, reference validity, recovery label, indicator decision, unavailable/failure reason |

Missing values must remain explicitly unavailable, never converted to zero error or a healthy decision. Never interpolate across resets, long gaps or uncovered reference intervals. Exact time association and maximum gaps are decisions for T05/T11.

## 4. Fast execution order

Default to sequential task sessions; this avoids conflicting edits and works with any model. If the user explicitly starts separate workers, literature T02 and dataset T03 can run independently after T01, with disjoint output folders. Integration and reviews remain sequential. On a 16 GB laptop, do not assume multiple native builds or LIO replays can run concurrently.

| Work block | Tasks | Target |
| --- | --- | --- |
| A | T01, T02, T03 | September 22–23 |
| B | T04, T05, T06 | September 23–25 |
| C | T07, T08, T09, R1 | September 25–27 |
| D | T10, T11, T12, R2 | September 28–October 4 |
| E | T13, T14, T15, T16, R3 | October 5–11 |

Dates are targets, not evidence that a task is feasible or complete. Compress idle time and duplicated work; do not skip scientific gates. If a gate slips, record a revised schedule instead of marking it passed.

## 5. Milestone one: prove a measurable and useful question

### T01 — Initialize execution tracking

**Depends on:** none. **Worker:** less capable model.

Read active scope and inspect Git status, existing files, OS, CPU/RAM, disk space and available build/container tools. Create the task ledger, decision log and environment inventory at `execution/ENVIRONMENT.md`. Add ignore rules only when needed for actual generated directories. Record all tasks below as TODO; do not claim technical readiness from tool presence alone.

**Acceptance:** current environment facts include commands used; ledger includes dependencies and evidence columns; no archived code or user changes overwritten. No dependency installation yet.

### T02 — Extract closest-work evidence

**Depends on:** T01. **Worker:** less capable model for extraction; R1 reviews interpretation.

Read X-ICP, SuperLoc, AdaLIO and GEODE full papers and available supplements/official code. Start from links in SCOPE_DECISION.md. Search primary sources for directly relevant recovery/transition evaluations and followups; log queries and access dates. Do not treat a missing keyword as proof of novelty.

Create one note per paper and `literature/COMPARISON.md`. Matrix columns: claimed target; estimator/indicator; formulation reference; online inputs; degeneracy mechanism; transitions tested; reference truth; recovery definition; false reassurance/delay analysis; scene transfer; relevant results; limitations; exact evidence locations. Distinguish “not found in inspected material” from “not studied.”

**Acceptance:** all four papers have traceable entries; inaccessible sections are explicit; candidate overlap and unresolved questions are listed. No unsupported “first” or “novel” claim.

### T03 — Audit dataset eligibility

**Depends on:** T01. **Worker:** less capable model.

Inspect official NTNU degeneracy and GEODE metadata. Create `data/ELIGIBILITY.md` and a machine-readable inventory. Record sequence IDs, platform, download/license conditions, size, LiDAR type, point timing, IMU units/rates, extrinsics, clocks, reference type/accuracy/coverage, and possible transition intervals. Label each property verified, unknown or unsuitable with source evidence.

Rank candidates by whether they support the exact local-motion recovery evaluation. Position-only reference cannot validate full rotational recovery. A sequence is not eligible merely because it contains a tunnel. Identify one development candidate and at least one alternative if available. Do not download whole datasets.

**Acceptance:** candidate eligibility is auditable per sequence; missing full-pose truth is explicit; aerial versus ground-platform claims are accurate; download prerequisites are known.

### T04 — Select and inspect one development recording

**Depends on:** T03.

Retrieve the smallest suitable sequence/subset through official access. Record checksum, provenance and storage path. Inspect actual streams, timestamps, reference coverage and calibration. Preserve a sufficient pre-event initialization segment; do not crop to the transition and assume LIO can initialize there. Annotate tentative geometry entry/exit using scene evidence, independent of indicator output or error peaks. Save `data/DEVELOPMENT_SEQUENCE.md` and transition annotations.

**Acceptance:** actual data, not only README claims, confirm input/reference fields; annotations have evidence; incompatible or unavailable reference produces a blocker rather than fabricated truth.

### T05 — Specify data and evaluation contracts

**Depends on:** T04. **Worker:** stronger-model review needed if frame/time definitions are uncertain.

Write `protocol/DATA_CONTRACT.md` and a provisional `protocol/METRICS.md`. Specify all interfaces from section 3, transforms, quaternion ordering, time origin, synchronization, association/interpolation policy, invalid intervals and reset handling. Specify local relative-motion translation/rotation errors over fixed physical time windows and accumulated pose error using one fixed pre-event alignment. LIO uses metric scale; do not silently fit scale.

State the relative-transform error equation and frame convention explicitly. Make numerical windows provisional development settings with rationale. Do not confuse global alignment with a new alignment at every window.

**Acceptance:** a later agent can implement without guessing units, frame direction or denominator; unresolved numerical choices are labeled provisional; truth inputs are isolated from indicator APIs.

### T06 — Reproduce the primary backend

**Depends on:** T01, T04, T05.

Verify FAST-LIO2 upstream requirements and sequence compatibility. Use a pinned revision and isolated environment/container as supported by this machine. Build, run a short initialization-plus-transition development replay and save trajectory/status/reset logs through a minimal adapter. Record exact setup and replay commands in `experiments/README.md`; preserve effective calibration/configuration.

**Acceptance:** actual successful replay with a manifest and parsed pose stream; crashes/missing poses logged; runtime and memory observed. If incompatible, document the concrete reason and propose a supported candidate change for review—do not quietly replace the estimator.

### T07 — Implement offline trajectory evaluation

**Depends on:** T05, T06.

Implement reference association, relative errors and fixed-pre-event-alignment drift. Add independent fixtures: identical trajectories give zero; a known increment error gives the analytic local error; a constant rigid frame change is handled as specified; a reset remains visible; reference gaps are excluded with reasons. Include rotation and quaternion sign-equivalence checks. Do not test only code against itself.

**Acceptance:** targeted tests and full new evaluation suite pass; development replay produces error streams with valid/invalid counts; metrics do not bridge resets or hide drift through post-event alignment.

### T08 — Export one conventional health indicator

**Depends on:** T02, T05, T06.

Select a documented Hessian/eigenvalue baseline. Locate the actual relevant backend computation or instrument a minimal diagnostic path. Record point selection, residuals, weights, Jacobians, coordinate frame, rotational/translational scaling and whether the matrix includes priors. Export raw values with availability reasons. Test informative and underconstrained synthetic registration geometries with known expected directions.

If only a standalone scan-registration implementation is feasible, label that narrower diagnostic honestly. Do not call it the backend's internal health signal or a reproduction of X-ICP/SuperLoc.

**Acceptance:** source-to-output derivation is documented; diagnostic export does not intentionally alter estimation; geometry checks pass; provisional operating settings are identified as development-only.

### T09 — Produce the first transition pilot

**Depends on:** T04, T07, T08.

Generate one aligned timeline of transition annotations, indicator values, local translation/rotation error and accumulated drift. Show unavailable intervals/resets visibly. Save a small reviewed figure, manifest and `evidence/PILOT_REPORT.md` containing reproduction commands, observations, limitations and unresolved questions. Keep exploratory thresholds visibly provisional.

**Acceptance:** plot is derived from retained outputs, axes/units/windows are explicit, reference covers the claimed recovery interval, and no finding is asserted from invented or substituted data.

### R1 — Week-one scientific gate

**Depends on:** T02–T09. **Worker:** stronger model.

Write `reviews/R1_FEASIBILITY.md` and `literature/GAP_DECISION.md`. Audit literature overlap, actual reference validity, time/frame handling and whether the pilot can answer the question. PASS requires a defensible candidate distinction and at least one measurable transition; it does not establish publication novelty or generalization. Otherwise specify exact repair tasks or a scope revision. Update root README status only to the extent supported by evidence.

If real data are unsuitable, a controlled registration pilot can support a narrowed feasibility question, but it cannot silently satisfy the full LIO/reference-data gate.

## 6. Milestone two: freeze the protocol

### T10 — Specify the published comparator faithfully

**Depends on:** R1 PASS, T02, T08.

Write `protocol/INDICATORS.md` selecting the relevant X-ICP/SuperLoc formulation after evidence review. Specify equations/code revision, required inputs, operating meaning, computational stage, scaling, priors and any adaptation to the primary backend. Define comparison conditions and expected validation fixtures. If equal point selection/residuals cannot preserve the published method, document the mismatch and design a separate controlled comparison or ablation; do not force false equivalence.

**Acceptance:** implementation instructions contain no missing mathematical steps; naming distinguishes original method from adaptation; reviewer can assess fairness before coding.

### T11 — Define outcomes and freeze leakage controls

**Depends on:** R1 PASS, T05, T09, T10.

Complete `protocol/METRICS.md` and `data/SPLITS.csv`. Define sustained local recovery, window lengths, tolerances, required duration, pre/post-event horizons and transition annotation rules. Use development evidence and reference uncertainty to justify values. A hindsight recovery label may use later reference samples; an online indicator must not.

Define false-reassurance numerator/denominator, event-versus-time weighting, decision availability, missed recovery, premature declarations, recovery-detection delay and right-censored/non-recovery outcomes. Report conditional error among available decisions alongside availability; a silent indicator must not appear superior. Specify whether delay uses the onset or confirmation time of sustained recovery and apply it consistently.

Split by independent trajectories/scenes, not frames or cropped intervals from the same recording. All data already used in pilots are development data. Record planned held-out IDs without inspecting their performance. Define the uncertainty unit and bootstrap/interval method using independent trajectory/event clusters, with events nested within recordings where needed. Set final sample requirements from precision needs and pilot variability; repeated backend runs are not new independent scenes.

**Acceptance:** every outcome has a computable definition, failure policy and denominator; no threshold is selected using test results; inadequate independent data are reported as a limitation.

### T12 — Specify and smoke-test controlled simulation

**Depends on:** R1 PASS, T05, T11.

Write `protocol/SIMULATION.md`. Choose the smallest viable implementation for corridor-to-feature-rich geometry with matched nondegenerate motion controls. Define geometry, trajectories, severity/duration factors, scan pattern/rate, per-point timestamps, ray visibility/occlusion, noise, IMU specific-force/gravity convention, biases, frames and extrinsics. Use development seeds and reserved unseen layouts; keep these separate from archived seed partitions.

Implement only enough to verify one development scan/trajectory segment, timing and IMU outputs before protocol freeze. Test ray intersections against simple known surfaces, occlusion, sensor-frame transforms and stationary IMU behavior. Estimate generation/runtime/storage costs. Ideal point pairs are permitted for indicator unit tests, not claimed as end-to-end LIO simulation.

**Acceptance:** sensing assumptions are explicit, feasibility has executable evidence, and remaining full-generation work is bounded for T14. If this cannot be achieved in scope, escalate the reduced evidence plan at R2.

### R2 — Protocol freeze gate

**Depends on:** T10–T12. **Worker:** stronger model.

Audit all numerical definitions, method fidelity, reference uncertainty, event independence, split separation, simulator feasibility and run budget. Save `reviews/R2_PROTOCOL.md` and `protocol/FREEZE.md` with dated file hashes/revision, selected sequences/methods, frozen development-selection rules and planned test analysis. Define which implementation settings may still be tuned on development data before R3 and how they will be selected.

**Acceptance:** another agent can compute the same outcomes without choosing new conventions; no critical TBD remains. Later changes require dated amendments and an explicit account of affected evidence. Test-data exposure may require replacement untouched test data. Do not run final evaluation yet.

## 7. Milestone three: reproduce and freeze implementation

### T13 — Implement and validate the published indicator

**Depends on:** R2 PASS, T10.

Implement the specified comparator with citations beside non-obvious equations. Verify against official examples/code outputs when available and independent analytic fixtures. Record tolerances, deviations and any inability to reproduce expected behavior in `evidence/INDICATOR_REPRODUCTION.md`.

**Acceptance:** both indicators satisfy the contract; parity or adaptation limits are evidenced; failed reproduction cannot be relabeled as a completed faithful implementation.

### T14 — Complete simulation and the development runner

**Depends on:** R2 PASS, T12, T13.

Complete the frozen simulation model and a resumable development runner using explicit configuration/run IDs. Keep simulation truth outside backend/indicator inputs. Validate one simulated LIO run before the batch. Run paired geometry/motion controls, permitted threshold sensitivity and repeated backend executions. Retain all attempts in a failure ledger; distinguish successful, crashed, invalid-input, missing-reference and non-recovery cases.

Cache unchanged upstream outputs only when input/configuration/code hashes match. Do not rerun LIO for plotting-only changes. Produce per-run manifests and aggregate summaries with the frozen uncertainty unit.

**Acceptance:** every scheduled development run is accounted for; restart/resume avoids silent duplicates; test split is untouched; runtime/storage estimates are updated from measurements.

### T15 — Verify replication-backend feasibility

**Depends on:** R2 PASS, T13; use the same development data only.

Build the selected Point-LIO candidate at a pinned revision with its validated sensor configuration. Run one development replay through the common output contract. Check reset handling, timing and whether indicator instrumentation remains comparable. Record any backend-specific adaptation. Do not launch full replication experiments before implementation freeze.

**Acceptance:** a reproducible development smoke run and compatibility report exist, or a concrete blocker is raised for R3. One smoke run is not replication evidence.

### T16 — Summarize development and prepare the freeze bundle

**Depends on:** T14, T15.

Create `evidence/DEVELOPMENT_REPORT.md`: paired results, uncertainty where sample size supports it, sensitivity, repeatability, failures and limitations. Select operating settings using only the rule frozen at R2; record the decision and all alternatives tested. Update commands/configurations and run the relevant complete research test suite. Reproduce one small development example from a clean isolated environment where practical; record precisely what was verified and what was not.

Prepare `execution/FINAL_EVALUATION_HANDOFF.md` containing exact proposed evaluation commands, immutable config hashes, untouched split IDs, resource estimates and stop conditions. These commands must refer to implemented, verified interfaces; mark the final batch as not executed.

**Acceptance:** report tables trace back to manifests, no failed runs disappear, selected settings are justified, and no test outcomes entered selection.

### R3 — Implementation freeze gate

**Depends on:** T13–T16. **Worker:** stronger model.

Audit mathematical fidelity, tests, data leakage, simulation realism, failure accounting, backend comparability and interpretation of local recovery versus global drift. Save `reviews/R3_IMPLEMENTATION.md` and `protocol/IMPLEMENTATION_FREEZE.md` with exact revisions/hashes, dependency versions, configurations and known limitations. A dirty tree requires a retained patch/hash, not merely a commit ID.

**Acceptance:** code and configurations reproduce the development evidence; the held-out batch is ready without additional tuning; root status documentation agrees. If replication or simulation remains blocked, record REVISE and the effect on study claims rather than declaring the original minimum study complete.

Work covered by this plan ends here. The October 12–18 final evaluation and full replication are the next phase, followed by analysis and manuscript completion. They are not implied by the freezes.

## 8. Recovery rules when work gets stuck

| Problem | Required next action |
| --- | --- |
| Literature already answers the question | R1 records overlap and proposes a precise evidence-backed revision; do not disguise it as a new algorithm |
| Dataset lacks adequate reference | Reject unsupported metrics; inspect the listed alternative; narrow claims only through a documented scope decision |
| Download needs login or unavailable access | Record official link and exact access requirement; continue literature/contracts; ask only for the missing access |
| Backend fails to build or cannot read sensor data | Capture minimal failure, verify official compatibility, isolate dependency issue; propose backend change if necessary |
| Published indicator cannot be reproduced | Preserve failure, verify formulation and scaling; request methodological review before renaming an approximation |
| Indicators perform well | Report that outcome; do not manufacture failure using historical global drift |
| Pilot gives no suitable transition | Record it; select another development event by the annotation policy, not by favorable indicator/error disagreement |
| Compute/storage budget is too large | Cache, shorten development smoke tests and reduce nonessential factors with a protocol amendment; preserve independent final evidence |
| A test sequence is used during development | Mark it development, record the exposure and arrange untouched replacement before final claims |

## 9. Minimal user involvement and completion tracking

The user normally only needs to dispatch the next task ID and select a stronger model for R1–R3. Agents should resolve routine implementation choices from evidence and the active scope. Professor-review packages should summarize decisions and linked artifacts; agents must not message the professor unless explicitly instructed.

Start with **T01**, then **T02** and **T03**. Use the dependency table and handoffs to continue. Avoid asking a less capable model to “complete the whole research project” in one session: it should have a narrow task, explicit evidence requirements and a clear stopping point.

Final checklist for this plan:

- [ ] R1 passes: useful candidate gap, eligible reference and real transition pilot.
- [ ] R2 passes: protocol and split policy frozen with no critical ambiguity.
- [ ] R3 passes: validated indicators, development evidence and immutable implementation.
- [ ] Failed runs, reference limitations and unverified claims remain visible.
- [ ] Final-test outcomes have not been used for development.
- [ ] Reproduction handoff is ready for the October 12–18 evaluation phase.
