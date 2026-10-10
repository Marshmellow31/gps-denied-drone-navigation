# Independent Point-LIO development workflow review

**Date:** 9 October 2026. **Decision: PASS for the repaired D050 development
workflow and eligibility for a bounded first corridor/control pair, once the
primary native cohort has stopped and the complete research suite passes.**
This is implementation review only. No Point-LIO development replay,
threshold selection or held-out generation/inspection was performed by this
reviewer. The bounded native pair and cache/evaluation readback require
separate acceptance before the remaining Point-LIO cohort runs. Overall R3
remains **REVISE**; no implementation/replication freeze is created here.

## Scope and accepted-method fidelity

The reviewer inspected the accepted amendment, native/source/producer anchor,
the shell runner/helper/recorder changes, development input validator,
attempt verifier, cohort controller, separate offline evaluator, Point-LIO
analysis and the limited generic-method changes to T16.

The seven-argument shell default remains restricted to the retained seed-14
feasibility input and its pinned hash. Development replication requires an
explicit eighth `development_replication` argument and sidecar-on mode.
The formal schedule is exactly 32 corridor/control pairs, seeds 14–45, with
distinct Point-LIO run IDs. No old feasibility attempt or control enters
threshold fitting; formal seed 14 is one of the original 32 events, not an
additional event created by the feasibility/repeated technical runs.
Every input is checked against its historical T16 bag, analytic reference
and reference-metadata identities. Inputs/reference metadata remain
development-only, with truth absent from the sensor bag.

Point-LIO diagnostics retain their own names, frame-pooled measurement rows,
fixed `L=1/3/5 m` scores and frozen Schur/DCReg adaptation. Accepted native
binary `80516da9cafba98262d56c17cc26ec4da76e214049d3af7776248b4c3a342b17`,
configuration, upstream commit/dirty patch, all nine native files and six
Python producer/math modules independently match the preserved acceptance
identities. The anchor SHA-256 is
`13c9aa68e4c55cd3336839548fc48b9be140863908ab1debdc4e5c5236321583`.
The Python producer anchors were independently traced to the original
sidecar-on manifest (DCReg to repository revision `5583b9e...`). The accepted
one-seed review hash also matches. Fresh read-only preflight passed, as did
the **53/53 R2 artifact hash readback** and accepted glog metadata check;
three actual runtime-library identities are recorded for this overlay.

The T16 change adds generic scalar-method/backend-label parameters while
keeping FAST-LIO defaults and mathematical rules intact. Point-LIO uses its
own segmented poses, its own score and DCReg rows, and the shared frozen
local-motion labels, debounce/reset/relapse and event-denominator rules.
Selection is global, over formal corridor scores only, with the unchanged
false-healthy constraint, highest-sensitivity/higher-threshold tie rule and
explicit no-feasible/no-alarm handling. Controls remain descriptive. The
primary final sample size is not recomputed from Point-LIO outcomes.

## Failure, cache and provenance findings repaired during review

The initial implementation required repairs before native eligibility. The
reviewer reported the following concrete gaps; the main agent repaired the
production files, and the reviewer checked the resulting code/tests:

- Missing manifest source entries could pass a subset loop. The attempt
  verifier now requires the **exact repository source-file set**, matching
  current bytes and the cohort identity. Native mathematical producers are
  separately pinned to the accepted one-seed identities; newly reviewed
  workflow code is recorded separately.
- A self-consistent cached run from another slot could be relabelled by the
  outer schedule. Cache/completion now check actual native run/seed/scene/
  control/input identity, launch command/receipt and cohort source/runtime
  bindings before reuse or evaluation.
- Python/NumPy version strings alone did not bind the environment. Runtime
  identity now includes the resolved interpreter binary hash and actual
  conda-history digest. Native, cache, evaluator and analysis identities
  agree; selected glog metadata/library hashes are checked before/after/cache
  and carried into the evaluation identity. The R2 bundle is read back before
  both cohort execution and analysis.
- A dead wrapper could conceal live descendants. Resume checks the recorded
  process identity **and** process-group members; it waits/blocks without
  launching another native attempt. Group cleanup continues until both
  wrapper and owned group are gone, using bounded escalation.
- Failed startup without a native output directory could lose its receipt
  and logs on resume. Existing startup receipts/logs now prevent overwrite.
  Timeout/interruption receipts are retained, and KeyboardInterrupt/SystemExit
  also persist a cohort interruption state. Failed/incomplete verification
  stops the cohort; it is never a non-recovery label or replacement seed.
- Evaluation lacked complete runtime binding/rechecks. It now has a separate
  immutable-identity cache bound to native/segmented poses, reference/metadata,
  evaluator, runtime and overlay. Post-evaluation source/environment checks
  prevent old identity being attached to changed code. Offline evaluation
  lives outside the native attempt, so native output manifests are preserved.

Source and input checks, clean required process statuses, exact raw bag-header
audit, monotonic `1..600` native/export frame identities and truth-free pose
segment join remain mandatory. Measurement-stage frames that the pinned
native code publishes must have emitted poses; this catches pose-logger
truncation even if an output hash record is updated. Unavailable frames and
reset boundaries stay explicit. The unchanged production exporter remains
responsible for Jacobian reconstruction, rotation/count/math fidelity.

## Independent tests

The reviewer added/updated `tests/test_pointlio_development_workflow.py`:
**14 focused tests passed**, using temporary fixtures, synthetic headers and
mocked native/ROS calls only. They check source omissions, measurement-pose
truncation with updated hashes, environment drift, failed process and
feasibility exclusion, exact schedule, Point scalar debounce/reset/candidate
rules, corridor-only selection dispatch, wrong-slot cache rejection, live
descendant handling, cleanup after wrapper death, startup-log preservation
and durable KeyboardInterrupt states. The controls-selection test inspects
the 32 formal Point-LIO corridor arguments; it performs no real-data fit.
The **14 existing T16 tests also passed**, preserving FAST-LIO behavior.

```bash
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python \
  -m unittest discover -s research_paper/experiments/tests \
  -p test_pointlio_development_workflow.py -v
```

`bash -n` passed for the shell runner. The complete-suite run is a main-agent
check and must pass with the stable fixtures before native trial; this review
does not infer its result from the focused tests.

## Reviewed implementation identities

| File under `research_paper/experiments/` | SHA-256 |
| --- | --- |
| `run_point_lio_indicator_feasibility.sh` | `76dcf4e520f6b2e61d66991a8b381123037a11bdc6e605773e287bf0d908f4ea` |
| `src/pointlio_runner_helpers.sh` | `00f88caff3f91efa8cb556ec2f05b46996837b504df0255e44e30a917ce451af` |
| `src/record_pointlio_attempt.py` | `2ae0a813bcf49dbe24bdc8750cac1fc691be4f7bc5b65dd0c84fc5b51a2afe90` |
| `src/validate_pointlio_development_input.py` | `9387dccca0bde4a604e99023c2d887e06d6fafc6c26f049751bddf7f74f976c8` |
| `src/verify_pointlio_development_attempt.py` | `9c971282939c70cbef5427ed3e78f895d5875f85899c92490e8d5c6135c1fe91` |
| `src/run_pointlio_development.py` | `51dd92d3fea17e13b48d460e2c18c7bdba50173194fd34235633c2d904edc448` |
| `src/pointlio_development_analysis.py` | `ff8968a8bf7658ebfe6b35dd9a7ebf268f2c28c817c6d1d261f2890acec21c7b` |
| `src/t16_development_analysis.py` | `db506e8daca813b1f41c0cae4fdeeccdf9c23f3420a6232c453f650467b5900f` |
| `tests/test_pointlio_development_workflow.py` | `3f1f50fbe141c71a3864de5533eca732d3ad1b6f046dffcc7da67baa62b1760e` |

## Next bounded acceptance and limits

After the primary native cohort stops and the complete suite passes, run only
the formal Point-LIO seed-14 corridor/control pair. Independently audit its
native manifests/row reconstruction, coverage/pose flush, runtime/source
identity, separate evaluator/analysis-loader interface and cached resumption.
Compare corridor pose bytes with the accepted one-seed replay where applicable.
Do not fit a threshold from this bounded pair or launch the remaining Point-LIO
cohort before that native readback passes.

This workflow intentionally stops on a failure rather than silently retrying
in place. A later diagnosed retry must preserve and link the failed attempt,
receipt and logs in the final inventory. Analysis cannot treat a blocked or
partial cohort as 32 successful pairs; reference-ineligible corridors stop
selection for explicit review. Full replication, all failures/unavailable/no-
alarm outcomes, separate threshold/freeze and overall R3 remain outstanding.
No publication or final-performance conclusion follows from this code review.

## Actual bounded pair and cache readback

**Decision: PASS for the actual formal seed-14 corridor/control pair and
cached resumption. The remaining prescribed Point-LIO development cohort
may run sequentially under the same reviewed execution identity.** Full
replication, threshold/freeze and overall R3 acceptance remain outstanding.

The complete stable-fixture suite is now retained in
[`development_workflow_full_tests_20261009.log`](../evidence/development_workflow_full_tests_20261009.log):
**191 executed, 190 passed, one skipped**. The reviewer read back that result.
The native trial then completed under the reviewed source; the reviewer
performed only read-only audits and temporary exporter regeneration.

Both native attempts under
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/POINTLIO_DEVELOPMENT_20261009/`
pass the production verifier and independent receipt/cohort/input/source/
runtime/overlay checks. Actual native output file sets/hashes, source-file
set, Python binary/history, accepted producers, clean required process exits,
600 raw frame headers, monotonic native/export IDs and truth-free segment
joins agree. Each has 600 input/indicator frames, 597 emitted poses/valid
diagnostic frames, three explicit startup/map-initialization-unavailable
frames and zero resets. The measurement-stage publication/pose-flush check
passes. Recorded wrapper process groups have no live members.

The reviewer independently regenerated **both entire exports from raw frame,
group and Jacobian CSVs** using the frozen isolated runtime, writing only
temporary files. Group-count, rotation and common-basis row reconstruction
checks passed; regenerated indicator and segmented-pose CSV bytes equal
the preserved native outputs exactly. Formal corridor pose and indicator
bytes also equal the accepted September feasibility replay. This establishes
the bounded producer readback; it does not add an independent event or permit
selection from the feasibility/trial pair.

Each separate offline evaluation is bound to its exact native manifest,
segmented pose/reference/metadata/evaluator/runtime/overlay identities and
output hash. The actual Point-LIO loader accepts 597 own poses and 19 primary
windows per scene; corridor reference eligibility is true, and the control
has no recovery label. Evaluations retain 1,194 rows, 1,154 valid local windows
and zero reference gaps. No threshold was fitted from this pair.

Cached bounded resumption records **2 CACHED and 62 PENDING** with
`BOUNDED_CHECKPOINT`. Only the two original native slot directories exist;
launch receipts remain `PROCESS_EXITED`, return code 0, bound to the same
command/input/cohort identity. Native manifest SHA-256 values are
`7be8d3b180baa2b4e99baf8b0fd30ef6efe805a8f360c3d2b79b4e7f5aaf8d41`
(corridor) and
`3e503a9f9fba2e702273af83ae255e39f51dba1ca34f1905b3705a3b4bdb08d8`
(control), matching the preserved verification records. The reviewed cache
branch verifies these existing runs rather than invoking the native shell
again. The independent readback and exact evaluation/receipt/output identities
are retained in
[`pointlio_development_bounded_review_20261009.json`](../evidence/pointlio_development_bounded_review_20261009.json).
The separate producer snapshot inventory was independently rehashed:
**39/39 source/configuration snapshot files match**.

Resume the formal 64-slot schedule with every failure/receipt retained; do not
replace a seed or suppress a discrepancy. After completion, independently
audit the whole cohort and perform the separately frozen corridor-only
selection under the accepted rule, then review a replication freeze. This
bounded PASS opens no held-out gate and establishes no final recovery finding.
