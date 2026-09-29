# Antigravity handoff: finish the LiDAR recovery study

Updated 29 September 2026. This is a continuation handoff for the repository's
current research goal, not permission to skip its evidence gates.

## Read these first

1. Root `AGENTS.md` for project boundaries and safety rules.
2. `research_paper/execution/CURRENT_HANDOFF.md` and
   `research_paper/execution/STATUS.md` for the live checkpoint.
3. `research_paper/AGENT_EXECUTION_PLAN.md` and
   `research_paper/execution/PAPER_COMPLETION_PLAN.md` for task order.
4. `research_paper/protocol/POINTLIO_REPLICATION_AMENDMENT_20260929.md` and
   `research_paper/evidence/POINTLIO_IMPLEMENTATION_VERIFICATION_20260929.md`
   for the accepted Point-LIO method and exact attempt evidence.
5. `research_paper/protocol/FREEZE.md` before touching any final/held-out test.

Treat the files above as authoritative over this handoff if they were updated
later. Do not assume a test, run, review, or push completed merely because an
older note planned it.

## Main goal, in ordinary language

The study asks whether existing LiDAR-inertial estimator health signals can
warn us when accurate local movement returns after a drone-like robot exits a
geometrically difficult corridor. This is an evaluation of existing estimators,
not a new estimator or a flight controller. Keep measurement geometry,
short-window motion accuracy and long-term drift separate.

## Verified state at this handoff

- FAST-LIO development analysis and its native lifecycle checks are accepted as
  development evidence. They are not final test results.
- The Point-LIO D050 measurement adaptation has protocol-review PASS. The
  analytic indicator, read-only C++ sidecar, exporter, run manifest, isolated
  ROS-master runner and tests are implemented.
- The exact Point-LIO feasibility workflow/code review returned PASS. The
  full test suite ran 161 tests: 160 passed, one optional SciPy test skipped.
  It included a compiled native-sidecar reset fixture. This PASS does not pass
  overall R3 and does not authorize the 32-pair batch or held-out tests.
- On Acer, one sidecar-off seed-14 run completed: 600 input headers audited,
  597 poses recorded, and required process exit statuses were zero.
- The paired sidecar-on attempt failed before sensor messages reached
  Point-LIO. Its log showed it waiting for bag-topic subscribers after
  Point-LIO exited. The run is preserved as `RUN_FAILED`; its process exit
  codes are unknown because it had to be stopped manually. It contains 600
  audited headers but zero poses, sidecar frames, groups or indicators. This is
  not a completed replay or paired-parity result.
- Attempt folders and manifests are on Acer under
  `runs/POINTLIO_INDICATOR_FEASIBILITY_20260929/`. Do not overwrite or reuse
  either folder. Read the manifest hashes in the implementation evidence.
- Last storage check: Linux had 4.6 GB free, Acer had 102 GB free. Keep at
  least 1 GB free on Linux. Put substantial build/run output on Acer where
  possible. Do not delete caches or user files to make room without asking.
- No Point-LIO threshold has been fitted from seed 14. No held-out input has
  been generated, screened or opened.

## Immediate next work: diagnose the failed sidecar-on startup

Do not immediately replay the bag. First inspect the preserved sidecar-on
manifest and logs, the current Point-LIO source/configuration hashes, ROS
parameter namespace and topic subscriptions, and the runner's process tree.
Find why Point-LIO exited before subscribing when the sidecar was enabled; the
precise cause is not yet known.

The interrupted attempt also exposed a process-management weakness: stopping
the `timeout`/rosbag wrapper did not reliably stop its rosbag child. Fix and
test process-group shutdown so interruption leaves no orphaned bag process,
all children are boundedly stopped, and the attempt is durably marked failed.
Do not hide or replace failed attempts. A retry must use a fresh output folder.

Before retrying, rerun the full suite and focused tests for startup failure,
interruption, child cleanup, manifest failure, and ROS-master isolation. Check
`df -h /` and keep the 1 GB Linux free-space floor. The accepted runner is at
`research_paper/experiments/run_point_lio_indicator_feasibility.sh`.

Once the startup cause and runner are fixed, repeat the exact retained seed-14
sidecar-off/on feasibility pair under D050. This is only an instrumentation
check:

- use the pinned seed-14 corridor bag, config, binary and Point-LIO revision;
- use fresh, unique run directories and preserve all manifests/logs;
- require complete raw-frame coverage, successful estimator/logger/master
  shutdown, on/off byte-identical pose CSVs, valid output hashes, and one
  indicator record per raw input frame (unavailable records remain explicit);
- run `research_paper/experiments/src/verify_pointlio_feasibility_pair.py`;
- do not fit a threshold, count a new event, inspect recovery labels, or access
  held-out data.

Obtain an independent review/readback of the exact completed pair before
starting the development replication.

## Remaining research stages after seed-14 acceptance

1. Run the frozen Point-LIO development replication: 32 corridor seeds
   `14–45` plus their paired controls, using Point-LIO's own poses and the
   existing reference/labels. Follow the accepted D050 threshold rule exactly:
   only corridor-development events select the one global Point-LIO `G_3m`
   threshold; controls and seed-14 feasibility do not. Preserve crashes,
   unavailable frames and no-alarm cases; do not replace attempts.
2. Freeze Point-LIO source, configuration, threshold and output identities
   before final-layout exposure. Keep its threshold independent of FAST-LIO's.
3. Complete overall R3 review and implementation freeze only after all required
   evidence is independently reproducible. R3 is still REVISE now.
4. Only after R3 PASS and the separate Point-LIO replication freeze, run the
   frozen 48-pair unseen final evaluation. Never tune on its outcomes.
5. Analyze uncertainty, failures, missing data and differences across scene
   types/backends. Preserve plot scripts, input data identities and exported
   figures (including vector versions where appropriate).
6. Complete the paper, verify every numerical and visual claim, compile and
   inspect the final PDF, and prepare a simple professor-facing explanation.

## Non-negotiable rules

- Follow the current plan and stop to ask if a new scientific choice is
  required; do not invent methods, results or claims.
- Development evidence is not final evidence. An independent implementation
  review of the runner is not an R3 PASS.
- Do not generate, screen, open, summarize or tune on held-out data until the
  complete R3 gate and required freezes pass.
- Do not fit any threshold on the seed-14 feasibility attempt.
- Report denominators and missing/invalid outputs. Missing data are not zero,
  healthy, recovered, or safe.
- Do not broaden scope to cameras, flight control, a new estimator, hardware
  deployment, or physical drone tests.
- Keep changes local unless the user explicitly asks to push them. Preserve
  unrelated user changes and do not use destructive cleanup.
- Communicate progress in plain language and keep the Linux free-space floor.

## Handoff/report format

When pausing or finishing a stage, state what passed, what failed, what was
not tested, where the evidence is stored, current free space, and the single
next gate. Never call the study publishable until the full manuscript and all
evidence pass the plan's checks. Publication acceptance cannot be promised.
