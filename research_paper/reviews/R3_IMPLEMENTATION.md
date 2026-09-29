**Gate:** REVISE

# R3 independent fifth follow-up — 29 September 2026

**T16-R3-10 is closed: the current native seed-14 lifecycle and cached
resumption are accepted. T16-R3-09 remains closed, and the earlier wrapper,
cache, failure-accounting and cleanup defects remain closed.** No new
FAST-LIO software defect was found in this review.

The overall R3 gate remains **REVISE for study readiness**. Point-LIO still
has only a pose-output smoke; comparable online health instrumentation and
replication development readiness are not established. The execution plan
explicitly requires REVISE while replication is blocked. No implementation
freeze is created, no threshold is locked, and held-out work remains gated.

## Exact reviewed input

The reviewed inventory has **108 entries**, `heldout_inputs_opened=false`,
and SHA-256
`4a6c054d7ed77e0512970cda266dd8855709075b9c06a8468ad6cb9afe3cfbd8`.
All 108 named entries matched before this report was edited, including the
native report, Acer completed summary, Acer cached-resume summary and actual
native run manifest. Independently parsing and hashing the R2 table matched
**51/51 files**; checking the retained T14 fingerprint matched **9/9 sources**.
The current R2 freeze-file hash is
`d1a351e51a8706a13e76759cb851a804c40adf7f5c6805993cf9d5c34c127f83`.
The inventory remains unchanged and identifies the preceding report as its
review input. This dated entry is the review output; earlier entries below
remain historical evidence.

## T16-R3-10 — Native lifecycle and cache accepted

The reviewer read the actual Acer files under
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/R3_NATIVE_SEED14_20260929/`.
The completed summary declares `COMPLETED`; the later summary declares
`CACHED`. Both point to the same run manifest, SHA-256
`4de6b50d6f4fc492dab6db2bb741c05894d2370f7ac695fd256764c7b3d99e31`,
with identical execution identity, completion validation, postprocessing
summaries and retained output hashes. All **18 output hashes** independently
matched their actual files. The run is explicitly development-only, seed 14;
its exact input bag, reference, metadata, raw manifest and canonical manifest
identity were rechecked. It adds no calibration or independent geometry event.

The live `_check_backend` was executed as a read-only diagnostic and exactly
matched the saved backend identity, including executable resolution:

- Upstream revision `7cc4175de6f8ba2edf34bab02a42195b141027e9`.
- Source-diff hash
  `1397219a8765c2bc8c49adaf7e94dcc1e6006788acac06467e28e660876e51a0`.
- Executed binary hash
  `4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792`,
  exactly the T14 binary identity.
- Frozen Python 3.12.14 / NumPy 2.5.3 and Conda history hash
  `90c14f8caa0cbc8a1a769f012c5bbcd9c1fbe7ba96d4626f22bbc077917b757f`.
- Current runner hash
  `149bcd952916518bb803b1730518a8b59abb807127eab534f61b5f84a79dae13`,
  supervised wrapper hash
  `2da73b9d5fe821c72c85edec8519cb3c50d7b602518a10ec0927eb9d358142c3`,
  and validation adapter hash
  `f1b90be692659f098fa2f1d346eb17bd03e9e9049d4d489c4e539ab26f9f54b6`.

The current completion validator was rerun on those existing files and
reproduced `FULL_SENSOR_INPUT_AND_FLUSHED_POSE_LOG`: **600** input scans and
health groups, **600** DCReg rows, **597** valid flushed poses, **1,194**
evaluation rows with **1,154** valid local-motion rows, and **zero** invalid
pose records, resets or reference gaps. The actual pose/evaluation CSV counts
and logger shutdown counts agree. The retained DCReg parity summary accounts
for 597 valid and three startup-unavailable timestamps, with maximum absolute
eigenvalue difference `3.637978807091713e-11`. Playback has its normal
completion marker. The resource record shows exit status 0, elapsed 1:13.44
and maximum resident set 190,888 KB.

The ledger has exactly the first execution's four transitions:
RUNNING, REPLAYED, RUNNING, COMPLETED. No cached replay attempt is added.
Separately, the reviewer called the current `_run_scene` cache path on these
actual inputs/results with estimator launch, evidence writes and
postprocessing explicitly forbidden. It returned **CACHED**, called no
estimator-launch function, and left the run manifest hash unchanged. This
confirms that the recorded cache result follows the current production path;
it does not launch another development replay.

## Earlier software repairs remain closed

The current source still separates the historical T14 wrapper from the R3
wrapper, uses canonical scientific identities with only top-level
`code_revision`/`runtime_s` exclusions, retains per-generation per-scene raw
bookkeeping and hashes, verifies scientific input/source hashes and cleans
verified cached pair scratch. The complete test suite and adversarial checks
passed again. The 48-pair dummy regression still uses canonical and raw hash
fields separately, changes revision/runtime metadata, leaves scratch empty
after both passes and calls no `_run_scene`. Its mocked preparation remains
distinct from the real input-preparation regression. T16-R3-09 remains closed.

## T15-R3-01 — Remaining plan-level replication readiness gate

The original [execution plan](../AGENT_EXECUTION_PLAN.md), R3 acceptance,
states: “If replication or simulation remains blocked, record REVISE”.
The [Point-LIO smoke report](../evidence/T15_POINTLIO_SMOKE.md) and
[T15 handoff](../execution/handoffs/T15.md) explicitly report both the FAST-LIO
minimum-eigenvalue signal and the DCReg Schur-mask signal as not comparable
yet: no equivalent validated Point-LIO health/Hessian stream was exported.
The smoke satisfies its bounded pose-format feasibility task, but cannot
establish the comparable second-backend experiment required by the complete
study. The [completion plan](../execution/PAPER_COMPLETION_PLAN.md) also
requires Point-LIO indicator development and a separate development freeze
before any final-layout exposure. No approved primary-only waiver changes
the original R3 acceptance condition.

**Required next work:** define and implement the Point-LIO online measurement
stage and indicator adapter on development inputs; document any differences
from the FAST-LIO correspondence/update contract; validate its mathematical,
time/reset/availability and common-output behavior with analytic fixtures and
a pinned development replay. Obtain an independent review and immutable
replication development freeze. Any material change to the agreed measurement
contract needs the protocol/implementation amendment required by the
completion plan. Preserve Point-LIO's smoke-only interpretation until that
evidence exists. No held-out data are needed to close this readiness gate.

This is the remaining study-level requirement, rather than a failure of the
accepted FAST-LIO native lifecycle. A separate FAST-LIO-only PASS would narrow
the approved gate; this review does not make that scope change. The eventual
implementation freeze must also retain the dirty-tree patch/source snapshot
with its hash as required by the execution plan.

## Verification and limits

The complete suite was independently run under both system Python 3.14.4 /
NumPy 2.3.5 and frozen Python 3.12.14 / NumPy 2.5.3. **Each ran 125 tests:
124 passed and one optional SciPy check skipped.** The adversarial script
passed in both environments. Live backend checks, current completion
validation and the read-only production cache check passed. No implementation,
tests, status, inventory or native evidence were changed; only this review
entry was added. No final CLI was run outside mocked unit tests, and no
held-out geometry/input/result was generated, screened or inspected.

The earlier scientific limits remain: this is a synthetic single-motion,
box-geometry development study with ideal clocks/extrinsics and uncalibrated
stress values. DCReg is a detector adaptation on FAST-LIO correspondences.
Native lifecycle acceptance does not establish final recovery performance,
replication, generalization, novelty, publication readiness or flight safety.
Root summaries should now say the native repair is independently accepted
and that Point-LIO indicator/replication readiness keeps the overall R3 gate
open. `protocol/IMPLEMENTATION_FREEZE.md` remains absent.

---

The following fourth follow-up report is retained unchanged as historical
review evidence; the fifth follow-up above is the current verdict.

# R3 independent fourth follow-up — 29 September 2026

**T16-R3-09 is closed at software-review level.** The latest repair preserves
each regenerated scene's raw revision and optional manifest runtime after
scratch removal, with its exact manifest hash and the original archive intact.
The earlier canonical-cache and cleanup defects remain closed.
**T16-R3-10 remains open because the current native development lifecycle has
not run.** The overall R3 gate remains REVISE; no implementation freeze is
created and no held-out work is authorized.

## Exact reviewed input

This review used the **104-entry** inventory
`evidence/R3_REVIEW_INPUT_HASHES.json`, SHA-256
`3788c7053d8035c9b6ad382937694430231cc078e49170d610fa67ad01c3219d`,
with `heldout_inputs_opened=false`. All 104 named entries matched the worktree
before this report was edited. An independent parse and file read-back of the
R2 table matched **51/51 hashes**. Its current freeze-file hash is
`c7c623da2c06ddcef247b1ccbf33acf21b3b185011fea875bf08b73b05440367`.
The two pinned binary/revision entries match retained T14 provenance; they
are not a fresh verification of the unavailable native executable. The
inventory is unchanged and identifies the preceding review report as its
input. This dated report is the review output.

## T16-R3-09 — Provenance repair accepted

The generation `finally` block in `final_evaluation_runner.py` now records
`manifest_bookkeeping` for CORRIDOR and CONTROL in every new
`generation_history` entry. Each scene's `code_revision` and `runtime_s` are
copied exactly when present, alongside its raw manifest SHA-256. The separately
measured pair runtime remains distinct. An unreadable manifest has an explicit
unavailable reason. Previous history entries are preserved, and the first
archived manifest is not overwritten.

The strengthened regression uses the real `_prepare_pair` with a dummy
seed-14 generator and mocked paired-bag audit. It removes scratch after the
first preparation, regenerates identical scientific content with changed
revision/time fields, removes the regenerated scratch, and then verifies:

- Both first-generation raw hashes and both regenerated raw hashes remain in
  the matching history entries.
- Both scenes retain `fixture-revision-1` and their raw runtimes 1.0/2.0,
  followed by `fixture-revision-2` and raw runtimes 3.0/4.0.
- Both original archived raw manifests remain byte-identical.

That regression passed. A separate in-memory check repeated the lifecycle,
captured both scenes' exact hashes and bookkeeping before deletion, and
compared them to retained history after both scratch removals. It also ran
with the optional raw `runtime_s` field absent, matching the production
generator's current shape: absence remained explicit through an omitted key,
while revisions, hashes and measured pair runtime remained available. No
geometry generator or estimator was invoked.

Canonical identity still excludes exactly top-level `code_revision` and
`runtime_s`. Direct mutation checks confirmed that bag, reference and metadata
hashes, scan settings, route settings and generator/simulator/route source
hashes still change the canonical identity. The original scientific cache
identity remains binding; preserving bookkeeping does not relax it.

## Earlier cache and wrapper repairs remain accepted

The complete adversarial script passed again, including the production-shaped
canonical/raw hash fields in the 48-pair dummy cache fixture. Across its two
passes, all 48 pairs completed, scratch was empty after each pass, and
`_run_scene` was never called. This verifies the fast pair-cache path and its
cleanup; `_prepare_pair` is mocked in that fixture, so the independent real
preparation checks above provide the attempt-history evidence.

The historical and separate supervised wrapper hashes remain respectively
`a3465d33b85b7f0b0f59e444297c1b71447af1ee7aa3dd2773b33a0172ca3639`
and `2da73b9d5fe821c72c85edec8519cb3c50d7b602518a10ec0927eb9d358142c3`.
The retained T14 fingerprint again passes **9/9 source checks**, with the R3
wrapper bound separately. T16-R3-08 remains closed at source-validation level.
No new software defect was found in this focused re-review.

## T16-R3-10 — Native gate requirement remains

The current runner hash is
`149bcd952916518bb803b1730518a8b59abb807127eab534f61b5f84a79dae13`.
The retained native validation still records
`d1899726942d4fc78f4b2fdb45f82fe4dcc946f498a924cc0a5069106947fa6a`.
The Acer ROS environment is absent from the live mount table, so the current
wrapper, actual child supervision, shutdown flush and current postprocessing
remain unverified together. The required retained seed-14 development replay
and normal cached resumption must run under the pinned environment with
current source/wrapper/binary/runtime/output hashes before native acceptance.
This requirement follows the execution plan's reproducible-development and
ready-batch R3 acceptance, and the completion plan's explicit native lifecycle
step. Passing mocked regressions closes the software finding, not this gate.

## Verification and limits

The focused input-preparation suite passed **8/8 tests**. The complete suite
passed **124 of 125 tests, with one optional SciPy skip**, under Python 3.14.4 /
NumPy 2.3.5. The adversarial script and the independent temporary checks above
passed. These results are not a rerun under frozen Python 3.12.14 / NumPy
2.5.3. Implementation, tests, status, inventory and other artifacts were left
unchanged; only this review report was updated. No held-out layout or input
was generated, sampled, screened or inspected, and no final CLI was invoked
outside mocked unit tests.

Current top-level status summaries honestly retain REVISE and unavailable
native evidence; their pending software re-review statements can now be
updated to this acceptance. The earlier mathematical and scientific limits
remain. Point-LIO comparable indicators and its development freeze still
precede final-layout exposure in the full-paper plan. This review locks no
threshold and establishes no replication, final result, novelty or publication
readiness. `protocol/IMPLEMENTATION_FREEZE.md` remains absent.

---

The following third follow-up report is retained unchanged as historical
review evidence; the fourth follow-up above is the current verdict.

# R3 independent third follow-up — 29 September 2026

The canonical cache comparison and successful fast-cache cleanup are repaired.
**T16-R3-08 remains closed at source-validation level. T16-R3-09's previous
cache failures are closed, but per-generation raw revision provenance is still
lost after cleanup. T16-R3-10 remains open: the current native lifecycle has
not run.** No implementation freeze is created and held-out work remains gated.

This review used exactly the **104-entry** input inventory at
`evidence/R3_REVIEW_INPUT_HASHES.json`, SHA-256
`44bb9c3ea0aaba274888aa20bd8ee8899c13af8850023d8e0a570052e3e367c0`.
All 104 named entries matched before this report was edited; an independent
parse and read-back of the R2 checksum table matched **51/51 files**. Of the
104 entries, two are pinned binary/revision identifiers: they match retained
T14 provenance, but the unmounted native environment prevents a new live
binary verification. The input inventory is left unchanged and therefore
identifies the preceding report, not this new output. Repository HEAD is
`f56070b1b6eae61a5e6d22c07bce1cc0c5c0b8ae`; the worktree is dirty.

## Verified software repairs

- The historical T14 wrapper has SHA-256
  `a3465d33b85b7f0b0f59e444297c1b71447af1ee7aa3dd2773b33a0172ca3639`;
  the separate supervised R3 wrapper has SHA-256
  `2da73b9d5fe821c72c85edec8519cb3c50d7b602518a10ec0927eb9d358142c3`.
  Calling `_verify_t14_source_hashes` with the retained reference fingerprint
  verifies **9/9 sources**. Its source dictionary excludes the separate R3
  wrapper, which the R3 inventory binds directly. The helper regression passes;
  it does not execute `_check_backend` in ROS.
- `_input_manifest_identity` excludes exactly the two top-level keys
  `runtime_s` and `code_revision`. Bag/reference/metadata hashes, settings and
  generator/simulator/route hashes remain binding. `_verify_retained_input`
  rechecks the live file hashes and source identities. Changed-bag and
  changed-reference regressions reject regeneration. The first raw manifest
  archive stays byte-identical, and generation history retains successive raw
  manifest hashes and measured pair-generation times.
- Scene fingerprints write a canonical `input_manifest_sha256` separately
  from the raw `input_manifest_file_sha256`. The pair cache now compares
  canonical to canonical; it compares the saved run's original raw hash to the
  pair's saved original raw hash. Current bag/reference/metadata hashes,
  execution identity, threshold, completion records and retained output
  hashes are checked before reuse. The current raw regenerated manifest is
  allowed to differ only through the canonical identity's two exclusions.
- The successful fast-cache path resolves its prepared pair and scratch root,
  requires the former to be a descendant of the latter, and removes only
  that verified pair after all cache checks pass. It no longer skips cleanup.
- The 48-pair no-geometry regression now writes the production writer's
  canonical hash into `input_manifest_sha256` and a separate raw hash into
  `input_manifest_file_sha256`. It changes both `runtime_s` and
  `code_revision`, regenerates dummy scratch inputs in two passes, performs
  **96 pair preparations**, asserts all 48 pairs complete on each pass,
  asserts scratch is empty after each pass, and forbids `_run_scene` calls.
  The regression passed independently. Its `_prepare_pair`, backend and
  geometry screen are mocked; it proves the pair-cache branch, not the full
  native lifecycle or production attempt-history retention. Its run records
  contain the cache-consumed hash fields, not every native run-manifest field.

## T16-R3-09 — Remaining raw attempt provenance gap

**Medium priority; does not invalidate the repaired scientific cache identity.**

In `experiments/src/final_evaluation_runner.py:836–847`, a generation-history
entry records the two raw manifest hashes, start time and measured pair
runtime, but no per-scene `code_revision` or original manifest `runtime_s`.
Later successful regeneration preserves the first archived raw manifests;
fast-cache reuse preserves the original run records and then deletes the
regenerated manifests. Consequently, the new generation's revision exists
only in scratch and is lost. A retained SHA-256 cannot recover that value.

An independent temporary fixture called the real `_prepare_pair` using the
existing seed-14 dummy generator and mocked paired-bag audit. It prepared the
pair, removed its scratch folder, regenerated identical scientific bytes with
revision changing from `fixture-revision-1` to `fixture-revision-2`, and removed
scratch again. Both preparations succeeded; the first archive stayed intact,
and two generation-history entries remained. The second entry contained the
correct regenerated raw manifest hash, but **no retained file contained
`fixture-revision-2`**. The compatibility fixture's raw `runtime_s=3.0` was
also absent; the history's runtime is a separately measured pair runtime.

The current production generator already omits `runtime_s` from its manifest
and correctly retains measured generation time in attempt records. Its
`code_revision` is still emitted, so the revision-loss finding applies to the
production regeneration path. This is narrower than the earlier cache
failure: outputs are reused correctly, but the stated preservation of every
raw generation's bookkeeping is incomplete.

**Required repair:** retain per-scene `code_revision` and `runtime_s` when
present in every generation-history entry, together with its exact raw hash,
or retain each immutable raw generation manifest. Add a regression that
changes those fields, removes regenerated scratch, and verifies their exact
values remain available while the original archive and run provenance stay
intact. Keep the canonical exclusions unchanged. Rebuild the review inventory
after the repair; no input geometry or estimator replay is needed for it.

## T16-R3-10 — Required native acceptance still open

The retained native validation identifies runner SHA-256
`d1899726942d4fc78f4b2fdb45f82fe4dcc946f498a924cc0a5069106947fa6a`;
the reviewed current runner is
`e29c7d280d3ecd66857e6509bc4fe4340ba0df95a04ffe5d79417b046d5bda7d`.
The live mount table contains no Acer mount. The current wrapper's actual
ROS child supervision, playback completion, shutdown flush and current
postprocessing have therefore not been verified together.

This is required gate evidence, not an additional scientific experiment.
The execution plan's R3 acceptance requires code/configurations to reproduce
development evidence and the batch to be ready without further tuning; T16
also requires implemented, verified proposed interfaces. The completion
plan's first step explicitly requires one development replay through this
current lifecycle. Historical native output plus mocked path checks does not
establish that current integration. After the provenance repair, restore the
pinned environment, run the retained seed-14 development adapter with a new
run ID, preserve current source/wrapper/binary/runtime/output identities and
verify normal cached resumption without another estimator execution.

## Verification and gate limits

`python3 -m unittest discover -s research_paper/experiments/tests -q` completed
**125 tests: 124 passed, one optional SciPy skip**, under Python 3.14.4 /
NumPy 2.3.5. `python3 research_paper/reviews/r3_rereview_counterexamples.py`
passed, including the 48-pair regression. The raw-attempt counterexample
above was run independently in memory against temporary dummy fixtures.
No implementation or tests were edited, and no final CLI command was invoked
outside mocked unit tests. No held-out layout was generated, sampled,
screened or inspected; reserved numeric IDs appeared only in dummy schedules.

The earlier mathematical, repeatability and scientific limits remain as
documented below. Point-LIO has only pose-output smoke evidence; comparable
indicator instrumentation and its development freeze remain required before
final-layout exposure by the full-paper plan. This review does not establish
replication, novelty, final performance or publication readiness. The
development threshold remains a candidate, not an R3-locked operating point.
Root status documents correctly retain REVISE and missing native evidence;
they should additionally record the narrower raw-attempt provenance repair.
No `protocol/IMPLEMENTATION_FREEZE.md` was created.

---

The following second follow-up report is retained as historical review
evidence; the third follow-up above is the current verdict.

# R3 independent second follow-up — 28 September 2026

The historical T14 wrapper identity is repaired. **T16-R3-08 is closed at
source-validation level. T16-R3-09 remains open with narrower cache defects,
and T16-R3-10 remains open because the current native lifecycle has not run.**
No implementation freeze is created.

This review used exactly the **104-entry** inventory with SHA-256
`bbbfe066c562910abe56ff7cde699ddcf9fc6cf0ad98d5a41e88adedfbddf1e8`.
All entries matched the worktree before this report was edited, and all
**51 R2 file hashes** independently matched. The reviewed inventory is
preserved [here](history/R3_INPUT_INVENTORY_20260928_REREVIEW2_REVISE.json).
It identifies the prior report, as expected for an input snapshot. Repository
HEAD remains `f56070b1b6eae61a5e6d22c07bce1cc0c5c0b8ae`; changes are uncommitted.

## T16-R3-08 — Closed in source; native acceptance remains T16-R3-10

The original `run_simulation_smoke.sh` again has the exact historical T14 hash
`a3465d33b85b7f0b0f59e444297c1b71447af1ee7aa3dd2773b33a0172ca3639`.
The reviewer called `_verify_t14_source_hashes` with the retained T14 run's
source dictionary; all nine source checks passed. `_check_backend` calls this
helper and the separate `FINAL_RUN_SCRIPT` is bound into the R3 inventory.
The supervised wrapper currently hashes to
`2da73b9d5fe821c72c85edec8519cb3c50d7b602518a10ec0927eb9d358142c3`.
Its diff retains the estimator configuration, input topics and replay rate,
while adding child supervision and playback status checks. This removes the
previous deterministic T14-wrapper rejection. The helper regression is valid
for source identity; it does not execute the ROS/binary environment checks.

## T16-R3-09 — Still open: cache identity and fixture lineage

Moving measured generation time out of the scientific input manifest is a
valid repair. `_prepare_pair` retains timing in `generation_history`, and its
focused tests reject changed bags and reference bytes. Three narrower issues
remain:

1. **Commit metadata still invalidates identical regenerated inputs.**
   `heldout_simulation.write_sensor_input` still embeds live Git HEAD as
   `code_revision`; `_input_manifest_identity` excludes only `runtime_s`.
   A temporary seed-14 dummy-input fixture was generated, its scratch folder
   removed, and then generated again with only `code_revision` changed from
   `commit_before` to `commit_after`. Bags, references, configuration and
   generator hashes stayed fixed. `_prepare_pair` reproducibly raised
   `archived provenance mismatch: .../CORRIDOR/manifest.json`.
   Committing an already reviewed dirty snapshot can change this field
   without changing scientific content. Retain the attempt's Git revision as
   provenance, but use the frozen content identity consistently for cache
   matching, or explicitly pin the manifest revision before the first run.

2. **The pair cache compares two different kinds of hash.** `_run_scene`
   writes `_input_manifest_identity(input_manifest)` into
   `fingerprint.input_manifest_sha256` (canonical JSON). The batch cache
   compares that field to `sha256_file(manifest.json)` (formatted file bytes).
   They differ for ordinary manifests. The 48-pair regression manually writes
   the raw file hash into its mock run manifests, so those records do not
   match the production writer. Re-executing an in-memory copy of that
   regression with only its fingerprint assignment changed to the actual
   writer's canonical hash reaches the mocked `_run_scene` failure
   `estimator relaunch`. Precisely, this proves the **pair cache is missed**;
   the real scene-level cache may still return CACHED and prevent native
   relaunch. It does not prove duplicate estimator execution. Correct the
   comparison and use production-shaped complete fingerprints in the fixture.

3. **Successful pair-cache resumption retains regenerated scratch bags.**
   The fast-cache `continue` precedes the successful-pair cleanup. Once that
   path works with production fingerprints, one restart can accumulate all
   48 regenerated pairs instead of retaining only the current pair's scratch
   inputs. The fixture explicitly removes its whole scratch tree between
   repetitions and does not assert per-pair cleanup, masking this difference
   from the stated storage policy. Ensure verified cached pairs release their
   scratch inputs after retained provenance/output checks, and assert the
   expected bounded scratch state in the regression.

The existing 48-pair check was independently run and passes as written. Its
claim must be narrowed until its manifests and cleanup assertions represent
the production lifecycle. No real geometry or sensor bag was produced in
these counterexamples; all bytes came from temporary dummy fixtures.

## T16-R3-10 — Still open: current native replay

The retained native validation records runner hash
`d1899726942d4fc78f4b2fdb45f82fe4dcc946f498a924cc0a5069106947fa6a`;
this review's current runner hash is
`ce7cac66abf46f0e647522d4988df15a9fc43d7eae06c6ddf086b464c3fbba92`.
The Acer partition was absent from the live mount table during the review.
The current supervised wrapper, actual ROS completion/shutdown and current
postprocessing therefore remain unverified together. After cache repairs,
run the retained seed-14 development adapter with a new run ID and preserve
current source, wrapper, binary, environment and output hashes. Verify normal
cached resumption without additional estimator execution. This adds no
calibration event and requires no held-out data.

## Verification and gate limits

`python3 -m unittest discover -s research_paper/experiments/tests -q` completed
**125 tests: 124 passed, one skipped**. The existing adversarial script also
passed. The two additional counterexamples above were executed independently
in memory against temporary fixtures, without changing implementation or tests.
The inventory helper only calls `_r3_required_hashes`; it does not sample a
layout. This review called no final CLI command, real layout generator or
screening function. Reserved IDs appeared only in dummy scheduling fixtures.

The earlier scientific limits below still apply. Point-LIO comparable
indicators and its development freeze remain required by the full-paper plan
before final-layout exposure. Root summaries should now describe T16-R3-08
as source-repaired, T16-R3-09 as partially repaired, and T16-R3-10 as lacking
current native evidence. Rebuild the inventory after repairs and report
changes; preserve a dirty patch/hash or immutable source snapshot for any
eventual PASS.

---

The following first follow-up report is retained as historical review evidence;
the second follow-up above is the current verdict.

# R3 independent follow-up review — 28 September 2026

The repaired package closes several earlier defects, but the current final
runner cannot pass its own backend identity check and cannot resume normally
after successful scratch cleanup. These are reproducible implementation
failures. No implementation freeze is created and no held-out work is
authorized by this review.

Reviewed repository HEAD: `f56070b1b6eae61a5e6d22c07bce1cc0c5c0b8ae`,
with a dirty worktree. The exact **103-entry** input inventory matched every
current artifact before this report was written. Its SHA-256 was
`327a5d6bad48b122c6848e2cd138626b915f4a6673e95917b64cc40ba6d5b5ca`;
a byte-preserving copy is retained in
[the reviewed inventory](history/R3_INPUT_INVENTORY_20260928_REVISE.json).
This inventory identifies the pre-review report, not this new verdict.
The [initial review](history/R3_IMPLEMENTATION_INITIAL_REVISE.md) is preserved.

The reviewer inspected the current handoff, status, execution plan, R2 freeze,
repair report, final runner, native wrapper, held-out generator source,
development validation adapter, input/lifecycle tests, analysis and repeat
evidence. All computation was on development outputs or temporary dummy
fixtures. No held-out geometry, sensor data or estimation result was generated,
sampled, screened or inspected. No final CLI screen/run command was invoked.

## Required repairs

### T16-R3-08 — Reconcile the supervised wrapper with backend verification

**High priority; deterministic pre-replay failure.**

In `experiments/src/final_evaluation_runner.py:326`, the source dictionary
passed through the original T14 fingerprint comparison includes
`"replay_script": RUN_SCRIPT`. The loop at lines 331–333 requires this
file's current hash to equal the historical T14 value.

Independent read-back found:

| Identity | SHA-256 |
| --- | --- |
| T14 reference run's replay wrapper | `a3465d33b85b7f0b0f59e444297c1b71447af1ee7aa3dd2773b33a0172ca3639` |
| Current supervised replay wrapper | `1b12166983e975f52a5753bc17c0a3ffe06e1add258280c51f9bf9c0de679c40` |

Therefore, even with the correct ROS environment, source tree and native
binary, `_check_backend` raises
`frozen T14 source changed before final run: replay_script`. Both the final
batch and the development validation adapter call this function.

The D037 update to the R2 checksum table does not update the independently
retained T14 run fingerprint. This distinction is correct provenance, but the
current compatibility check does not accommodate the intentional wrapper
repair.

Preserve the historical wrapper and T14 fingerprints. Give the supervised
wrapper a separately reviewed identity, with a documented invariant that the
estimator, its configuration and scientific inputs remain the frozen T14
ones. Exercise the actual backend-validation path in a focused regression;
the current lifecycle fixtures mock process execution and do not establish
that this identity path succeeds. Rebuild the review inventory after repair.

### T16-R3-09 — Make cache resumption survive regenerated input manifests

**High priority; normal restart after successful cleanup fails.**

`heldout_simulation.py:290` embeds the measured `runtime_s` and repository
`code_revision` in every generated input manifest. The bag and analytic
reference can reproduce byte-for-byte while these provenance fields differ.
The final runner deletes successful scratch inputs at line 1083, regenerates
them on a later invocation, and checks the regenerated manifest against the
archived full manifest byte-for-byte at lines 825–830. Run and pair
fingerprints likewise contain the full input-manifest hash.

A development-only counterexample reused
`test_final_input_preparation.InputPreparationTests`, with seed 14 and
stratum `DEVELOPMENT_FIXTURE`. Its dummy generator wrote constant bag,
reference and metadata bytes, adding a different `runtime_s` to each
generation. No geometry generator ran. The sequence was:

1. Prepare and archive the pair successfully.
2. Remove only that temporary fixture's scratch folder, reproducing the
   final runner's successful cleanup.
3. Prepare the same pair again with identical sensor/reference bytes.

The result was `archived provenance mismatch:
.../results/inputs/DEVELOPMENT_FIXTURE_14/CORRIDOR/manifest.json`.
The regenerated bag hash was independently confirmed unchanged. The archive
retry repeats the same comparison and cannot repair it. At batch level the
exception overwrites the pair record with `FAILED_KEEP_INPUTS`, so an
already successful pair no longer resumes as cached. Existing tests cover
resumption while original scratch inputs remain, which does not cover this
normal later restart.

Separate immutable scientific input identity from generation-attempt
metadata. Retain the original provenance and record regeneration attempts
without overwriting it; compare sensor, reference, settings and relevant
source hashes explicitly. Ensure the run/pair cache uses the reconciled
identity. Add a completed-pair restart fixture that removes scratch, changes
only generation timing, and proves cached results survive without estimator
relaunch. Also verify changed bag/reference/configuration is still rejected.

### T16-R3-10 — Verify the repaired lifecycle in the native environment

**Required evidence before declaring the batch ready.**

The retained native seed-14 lifecycle evidence predates the 28 September
wrapper and completion changes. Its recorded runner hash is
`d1899726942d4fc78f4b2fdb45f82fe4dcc946f498a924cc0a5069106947fa6a`;
the runner reviewed here is
`3a1cf2ee1d2418aa9228a56739077d073588a17844ba9a173549f0c1bdacff9f`.

The Acer mount is absent in this review session, so the retained
Python 3.12.14 / NumPy 2.5.3 ROS environment and native backend could not be
used to repeat the replay. Current mocked checks establish individual paths,
but the live interaction between supervisor, ROS processes, logger shutdown,
bag completion and postprocessing remains unverified for the repaired source.

After T16-R3-08/09, restore the pinned environment and run the existing
seed-14 development adapter with a new run ID. Preserve previous evidence,
save current source/binary/runtime/output identities, and verify its
completion, unavailable-window handling and ordinary cached resumption.
This replay adds no calibration event. No held-out access is needed.

## Independently verified progress

- All 103 input-inventory entries matched. The runner's recursive R2 read-back
  also verified all 51 frozen file entries, including the previously omitted
  scene-screen dependency.
- `python3 -m unittest discover -s research_paper/experiments/tests -q`
  completed **121 tests: 120 passed, one optional SciPy test skipped**, using
  system Python 3.14.4 / NumPy 2.3.5. The unqualified `python` command was
  unavailable; no installation or environment mutation was performed.
- `python3 research_paper/reviews/r3_rereview_counterexamples.py` passed.
  It established trailing missing estimates remain completed/unavailable when
  full input diagnostics and logger counts exist; changed scene-audit content
  invalidates the gate; missing input/reference cache provenance is rejected;
  the exact shell supervision functions detect a failed child; and a surviving
  process group is detected after its wrapper PID disappears.
- The prior reset/debounce and missing-endpoint regressions pass in the full
  suite. The current source retains explicit invalid barriers and preserves
  planned unavailable windows. These checks support the corresponding
  T16-R3-04/05 repairs.
- The repeat audit was independently recomputed from all **64 development
  primaries and four repeats**. Loading verified their retained output hashes
  and input/backend parity. After JSON normalization and excluding environment
  labels, nonnumeric results matched exactly; 157 floating-point values
  differed by at most `2.220446049250313e-16` in this system environment.
  This is a cross-environment numerical check, not an exact reproduction in
  the frozen analysis environment.
- The seed-14 pre-batch substitute is accepted as disclosed exact-input repeat
  evidence: its scientific input and backend fingerprints match, and its
  differing provenance runner is explicitly accounted for. It must remain a
  repeat of the same geometry, never an additional event or calibration
  sample. Original failed scheduled attempts remain part of the ledger.
- Quantitative repeat evidence closes T14-R3-01/T16-R3-07: both corridor
  labels agree, but warning states and seed-45 DCReg delay vary. The delay
  changes from about 3.5003 s to 1.3003 s. Substituting either/both repeat pairs
  in the descriptive sample-size audit leaves the target at 48 pairs.
  This does not demonstrate general deterministic backend behavior.

## Scientific and freeze limits

The candidate FAST-LIO threshold remains `166.16366016039856`; this REVISE
review does not lock it or change it. The development recovery counts and
the original analysis retain their prior status. The mathematical comparator
is a DCReg detector adaptation on FAST-LIO correspondences, not full DCReg
registration. Current work does not establish publication novelty.

Point-LIO still has a pose-output smoke, with comparable health instrumentation
and replication outstanding. The full paper plan correctly requires that
development freeze before final-layout exposure. R3 cannot be described as
completion of the original minimum study while this remains unresolved.
The synthetic single-motion, box-geometry, ideal-clock/extrinsic and
uncalibrated-noise limits remain explicit.

The root README and current handoff honestly describe REVISE and missing
current native evidence, but must be refreshed with these specific remaining
findings. For a later PASS, preserve an immutable source snapshot or dirty
patch with hash, retain the final reviewed inventory, and write the freeze
only after its contents and acceptance evidence agree. No
`protocol/IMPLEMENTATION_FREEZE.md` was created by this review.
