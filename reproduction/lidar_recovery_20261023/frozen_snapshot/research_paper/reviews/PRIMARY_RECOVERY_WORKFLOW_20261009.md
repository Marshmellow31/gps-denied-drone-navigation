# Independent primary development recovery workflow review

**Date:** 9 October 2026. **Initial decision: REVISE before native trial or
large recovery batch.** Scope is only
`experiments/src/recover_primary_development.py`, its native-lifecycle wrapper,
failure/cache behavior and analysis adapters. No native replay, threshold fit
or held-out generation/inspection was performed by this reviewer. Repairs
and any later bounded acceptance are recorded below rather than erasing this
initial decision.

## Contract and positive checks

The helper delegates replay, shutdown, postprocessing, complete-stream
validation, technical retry and cached resumption to the previously reviewed
`final_evaluation_runner._run_scene`. It restricts expected inputs to exactly
64 slots: seeds 14–45 crossed with corridor/control, each matched to historical
T16 bag/reference/metadata hashes. The imported development scheduler emits
64 primary runs plus four prescribed seed-14/45 corridor/control repeats;
repeat IDs are separate and cannot enter T16's primary-run regex/denominator.
The underlying lifecycle accepts development-role input and explicitly
requires reviewed identities for any held-out input. This helper produces no
held-out geometry and performs no threshold selection; passing `None` stores
an absent threshold in provenance rather than calibrating one.

New native attempt directories/manifests remain under `native/`; adapters
under `analysis_contract/` reference actual output files, record source-native
manifest hashes and explicitly state that they are new supervised evidence.
They do not recreate missing historical manifests. Completed output hashes
are checked before adaptation. Technical retry IDs remain native attempts,
while adapters preserve scheduled scientific slot IDs for the unchanged T16
interface. The reviewed scheduler and lifecycle preserve the original cohort
and retry policy. A completed native cohort is reported as pending analysis,
not a scientific result or R3 acceptance.

During review, source tracking was repaired to include the actual supervised
replay wrapper and imported development runner; the latter owns scheduling,
input validation and adapter persistence. The current identity records and
checks these alongside lifecycle/recovery sources. A failure-ledger symlink
was also added from the analysis root to the native ledger so the unchanged
T16 reader can see its status rows. These address the initial source-coverage
and missing-ledger-visibility findings, subject to the remaining checks below.

## Required repairs

- **PRR-01: Bind adapters to native input/execution provenance.** Initially
  `analysis_adapter` rehashed the current input directory and attached supplied
  backend/source/runtime values without comparing them to the completed
  native manifest fingerprint. A standalone temporary fixture with a
  `COMPLETED` native manifest and altered post-run reference was accepted;
  the adapter's new reference hash disagreed with the native fingerprint.
  This can relabel unchanged outputs against changed evidence. Before
  publication, require bag/reference/metadata/raw-manifest identities and
  execution identity to match the native fingerprint, and require scheduled
  run ID, seed, scene, role/control and route metadata to agree. Reject the
  mismatch rather than publishing fresh metadata for old output bytes.
- **PRR-02: Recheck identities after native work.** Per-slot source/backend
  checks originally happened only before `_run_scene`. A wrapper or
  postprocessor change during replay could therefore be missed at a bounded
  checkpoint or final slot and receive the old source identity. Recheck all
  inventoried source files, actual backend/configuration/runtime anchors and
  scientific input identities after native return and before exposing its
  adapter/declaring cohort completion.
- **PRR-03: Validate the ledger bridge.** Reject an existing analysis ledger
  regular file or symlink targeting a different native ledger. Do not silently
  leave a stale unrelated file in place, because T16 would report its statuses.
  The native ledger is append-only stage/state-transition evidence, so report
  its counts as transition/status-row counts, not unique attempt counts.
  Unique technical attempts require separate manifest/attempt-ID accounting.
- **PRR-04: Persist failures outside the native lifecycle.** Source/input/
  backend/storage preflight exceptions and adapter failures originally left
  `recovery_schedule.json` marked `RUNNING`. Durably record `BLOCKED`, the
  affected scheduled slot, stage and reason. Retain existing native attempt
  manifests/ledger. Never mark an adapter failure as a completed analysis slot.

Verify repairs with independent failure fixtures: post-native input mutation,
wrong native slot/execution identity, source changes during mocked native
work, wrong ledger link/file, preflight rejection and adapter failure. Also
verify the bounded completed/checkpoint path and cached resumption without
launching a backend. Use a fresh native trial only after these repairs pass.

Overall R3 remains REVISE regardless of this workflow review. Full restored
primary outputs, reanalysis, repeatability and Point-LIO replication/freeze
remain separate acceptance gates; held-out work stays sealed.

## Repaired workflow acceptance

**Decision: PASS for the repaired development recovery workflow and a bounded
first native trial.** The initial findings are closed for the reviewed helper
SHA-256 `1c00980bf1a6e7121d10f36a2b817b21fabf17a22e1db64c858e28944ce2ea51`.
The reviewer made no production-source changes; the main agent repaired it.

- PRR-01: adapters now compare actual input bytes with the native fingerprint
  and copy those original identities only after agreement. Native scheduled
  slot, seed, scene, role/control, route, backend, source/runtime identities
  and output hashes are checked. Changed references cannot be relabelled.
- PRR-02: actual wrapper and development runner are inventoried; all source
  files and backend identities are checked both before and after native work,
  including the bounded/final slot before adapter publication.
- PRR-03: existing unrelated analysis-ledger files/links are rejected. The
  valid symlink exposes the complete native lifecycle ledger without rewriting
  its schema. T16's existing `failure_ledger_attempt_status_counts` name is
  imprecise for these stage/status-transition rows: label this limitation
  explicitly in the restoration analysis and count unique attempts from
  native manifests separately.
- PRR-04: per-slot preflight/post-native/adapter exceptions persist a BLOCKED
  cohort summary with reason and current slot. Native evidence remains intact.
  A native slot marked COMPLETED in a blocked summary is a native status;
  absence of the adapter hash means analysis exposure did not complete.

An additional default-ROS-port issue was fixed: checking only fresh first
slots could skip collision prevention when a crashed first attempt triggers
a technical retry. The helper now refuses occupied port 11311 before every
lifecycle call, including retries/cached calls. This conservative check can
block cache-only access during an unrelated live ROS session, but cannot
alter that session. It does not replace the reviewed lifecycle's bounded
process cleanup/retry accounting.

The reviewer added
`experiments/tests/test_primary_recovery.py`, SHA-256
`288aa1ab5816b807e7e5e29e80952794a233fca69a057d785c76bf35d0bc068c`.
**10 focused tests passed** under the frozen isolated Python. Tests cover the
exact 64+4 schedule, retry-to-scientific-slot identity, all four input artifact
mutations, source/backend/runtime/slot/role/control/route mutation, corrupted
completed output, source change during mocked native work, occupied master
with a prior crashed manifest, durable blocked reporting with preserved
ledger and rejection of wrong ledger files/links. They use temporary
fixtures/mocked native calls and launch no estimator or real ROS master.

```bash
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python \
  -m unittest discover -s research_paper/experiments/tests \
  -p test_primary_recovery.py -v
```

Cached/resumable native output validation and two-attempt/postprocess retry
budgets remain owned by the previously accepted lifecycle, rather than being
reimplemented here. Each resume checks cohort execution identity; current
successful slots are re-established from hash-checked native caches. The
schedule summary is rebuilt, while original attempt manifests/append-only
native ledger retain failures. `--stop-after` counts visited slots including
caches; resume without that option to traverse the complete frozen schedule.

Next run only the planned bounded development pair, audit actual native and
adapter manifests/streams and verify the unchanged T16 loader accepts them
before executing the remaining schedule. This PASS is implementation review,
not acceptance of native trial results or all 68 completed runs. No threshold,
split, metric, sample size or scientific-method amendment is introduced.

## Actual bounded trial and cache acceptance

**Decision: PASS for the completed development seed-14 corridor/control
trial, adapter readback and cached resumption. The full prescribed 68-run
native recovery schedule may now resume under the same reviewed identity.**
This authorizes recovery execution, not threshold fitting, completed-cohort
acceptance or held-out work.

The reviewer independently inspected the two actual native manifests,
18 hash-bound outputs per native run, adapters, restored input bytes, cohort
summary and native ledger under
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/PRIMARY_DEVELOPMENT_RECOVERY_20261009/`.
Every native output hash matches its adapter-linked file; every link resolves
to the corresponding actual native file. Both source-native manifest hashes
and native execution fingerprints match the recorded adapter/cohort identity.
Current source hashes and direct backend preflight also match that identity.
Bag/reference/metadata hashes match both the original native fingerprint and
historical T16 anchors.

Both are first-attempt COMPLETED native runs with 600 complete health groups,
597 poses/valid diagnostic frames and 1,194 evaluation rows, including 1,154
valid local windows and no reference gaps. The reviewer freshly reran the
production completion validator; its output equals each native manifest's
completion record. Read-only bag audits confirm 600 raw LiDAR messages each.
Every health timestamp group has all three lever-scale rows, and pose
timestamps equal the last 597 diagnostic frame timestamps, with only the
three declared startup-unavailable frames absent. No dropped source frame,
invalid pose or reset was found in these two runs.

The unchanged T16 `_load_run` independently accepts both adapters: each has
597 poses, 600 diagnostic ticks and 19 primary windows. Corridor reference
eligibility is true; the control has no recovery label. This tests the actual
analysis interface without running a threshold search. The small trial
readback is retained in
[`primary_recovery_bounded_trial_20261009.json`](../evidence/primary_recovery_bounded_trial_20261009.json).

After same-command bounded resumption, the cohort summary is
`BOUNDED_CHECKPOINT`, with **2 CACHED and 66 PENDING**. Both adapter hashes are
unchanged from the original bounded-trial record:
`5eb4c455f6d3b5bbd13a71b93c976744e698c29d314e483538282ddeed9b293c`
(corridor) and
`61319962aa5c3e600a0bb1e0bd3bae083a4c2d7c663986bedc49ee3c4618aec6`
(control). Because these bind the source-native manifests, their equality
also establishes unchanged native-manifest lineage. Only the two original
native run directories exist; no technical retry was created. The native
ledger retains four RUNNING stage transitions, two REPLAYED and two COMPLETED
rows, describing **two unique attempts**, not eight attempts. Its analysis
symlink resolves to that exact native ledger. Recorded native replay process
groups have no remaining live members. These observations and the reviewed
cache branch support resumption without a new native replay.

The initial pair's historical primary pose, health and DCReg hashes also
match, but this does not predict reproduction for the remaining scenes.
Continue sequentially, preserve every attempted slot and discrepancy, stop
on the helper's failure/identity/resource guards and retain the source-native
manifests beside the adapters. After all slots finish, complete independent
cohort/hash/failure/repeatability review and the unchanged T16 analysis before
using results in a primary freeze. Overall R3 remains REVISE; no final-data
gate is opened by this bounded-trial PASS.
