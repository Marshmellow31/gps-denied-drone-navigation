# R3 repair verification package

Updated 29 September 2026. The fifth independent R3 follow-up accepted the
software/provenance repairs and current native FAST-LIO seed-14 lifecycle;
**T16-R3-09 and T16-R3-10 are closed**. Overall R3 remains **REVISE** under
the original plan because Point-LIO comparability and development replication
readiness remain open. The exact T14 binary was rebuilt and the retained
seed-14 replay completed with cached resumption; see [native evidence](R3_NATIVE_SEED14_REPLAY_20260929.md).
No held-out layout, sensor input or estimation result has been generated,
screened or inspected.

## Repair evidence

| Repair | Current implementation and direct verification |
| --- | --- |
| T16-R3-01 | The declared route constant is defined. The run lifecycle persists a manifest before launching a subprocess. Mocked successful, crashed, timed-out, cached and interrupted paths verify the manifest and ledger transitions. |
| T16-R3-02 / R3-08 | The historical T14 `run_simulation_smoke.sh` is restored byte-for-byte and still matches the original T14 source fingerprint. A separate `run_final_evaluation_replay.sh` supervises ROS, FAST-LIO and the pose logger through playback and shutdown; its SHA is independently bound in the R3 inventory. The T14 backend verifier checks the original wrapper and accepts the separately reviewed R3 wrapper. The completion validator checks all 600 diagnostic timestamps/groups, health/DCReg horizons, logger flush/counts and evaluator/reference agreement. A completed replay may have zero or truncated pose output; planned missing windows stay unavailable in the fixed analysis denominator. |
| T16-R3-03 / R3-09 | The R3 inventory includes every file in the 51-row R2 freeze, including `audit_simulation_scene.py`. Canonical input identity excludes only attempt runtime and Git commit bookkeeping; sensor settings, bag/reference hashes, metadata and generator/source hashes remain binding. Each raw manifest hash and generation time stays in an append-only attempt history, and the original archived manifest is not overwritten. Input preparation and run/pair cache checks use the canonical identity; completed-pair fast-cache validation ties saved run manifests back to their original raw input hashes. A focused test changes only runtime/commit metadata, then removes scratch, regenerates inputs and verifies the archive remains intact. Separate tests reject changed bags/references. The full no-geometry batch fixture resumes all 48 completed pairs twice after scratch cleanup, confirms cleanup, and observes no estimator relaunch. |
| T16-R3-09 provenance follow-up | Each generation-history entry now stores per-scene `code_revision` and `runtime_s` values when present, next to exact raw manifest hashes and measured pair-generation time. A regression regenerates after scratch deletion with revisions changing from `fixture-revision-1` to `fixture-revision-2`, verifies both revisions and raw times survive, and confirms the original archived manifests are unchanged. Canonical cache exclusions are unchanged. The independent R3 follow-up accepted this software repair. |
| T16-R3-04 | Scalar and vectorized threshold-sweep debounce both reset at segment changes and count the first valid record in the new segment. Regression fixtures cover segment-reset parity. Development analysis was rerun in a separate output folder and reproduces the selected threshold and event counts. |
| T16-R3-05 | Planned post-exit 3-second rows with missing endpoints are retained as unavailable when their nominal endpoints fit the horizon. Regression fixtures cover missing endpoints; current complete-data counts reproduce. |
| T16-R3-06 / R3-10 | Input generation, paired-bag auditing, archival, replay and postprocessing have durable stage/attempt records. Interrupted partial bags remain in their original folder while a single technical retry uses a new folder. Resumption checks the recorded process and process group; an orphan fixture confirms that a surviving child blocks a second run. Terminal states are appended to the ledger. The current-source seed-14 native lifecycle completed, the same run resumed as `CACHED`, and the fifth independent R3 follow-up accepted this evidence. |
| T14-R3-01 / T16-R3-07 | The [repeat audit](T14_REPEATABILITY_AUDIT.md) verifies 64 primaries and four repeats, measures aligned errors/scores, raw and confirmed decisions, corridor labels/delays, and paired-interior substitution sensitivity. No repeat enters threshold fitting or independent-event counts. R3 accepts the seed-14 pre-batch pair as a disclosed same-input repeat, never as an additional event or calibration sample. |

## Test evidence

The previous 27 September suite ran **119 tests: 118 passed and one optional
SciPy-dependent scene test was skipped** in the frozen and system environments.
The follow-up code changes were re-run on 29 September under system Python
3.14.4: **125 tests, 124 passed, one optional skip**. The latest concise output
is saved in [r3_tests_system_20260928.log](r3_tests_system_20260928.log); the
same full suite was rerun after the provenance repair.
The earlier environment logs remain historical. The Acer Python 3.12.14 /
NumPy 2.5.3 ROS environment was used for the native T16-R3-10 replay on
29 September; its current run identity is in the linked native evidence report.

- Earlier frozen analysis environment: Python 3.12.14 / NumPy 2.5.3;
  [historical log](r3_tests_frozen.log), SHA-256
  `0699bd4b8c714d48d2ba12a0939432b2683f77e8c98d92223a2a760f20556d29`.
- Earlier system-environment log: Python 3.14.4 / NumPy 2.3.5;
  [historical log](r3_tests_system.log), SHA-256
  `d191c08fad37a3cbd40906728e4568b796f0d1a884be27206aab9673141d6350`.

The focused final-runner/input/lifecycle checks use mocked processes, temporary
files and development-shaped streams. Reserved numeric seed IDs
appear only in no-data plans and synthetic selection-rejection fixtures;
the tests never sample their geometry. Other focused checks include the five
repeat-audit tests, analyzer reset/missing-window regressions, and the
[adversarial review regression script](../reviews/r3_rereview_counterexamples.py).
The script verifies missing-pose accounting, the full R2/R3 dependency bundle,
cached-input provenance, backend child supervision and orphan detection. These
checks establish implementation behavior, not a publishable scientific result.
Its 28 September outcome summary is retained in
[r3_adversarial_regressions_20260928.log](r3_adversarial_regressions_20260928.log).
The current review bundle is generated by
[`prepare_r3_review_inventory.py`](../experiments/src/prepare_r3_review_inventory.py)
and stored as [R3_REVIEW_INPUT_HASHES.json](R3_REVIEW_INPUT_HASHES.json).

## Fresh native build and real development lifecycle

The temporary FAST-LIO workspace was lost when the machine restarted. A fresh
local clone at the original workspace path now reconstructs the pinned source,
submodule and patches. A final-newline restoration patch accounts for the
previously unarchived CMake newline: the source diff then matches T14 exactly,
SHA-256 `1397219a8765c2bc8c49adaf7e94dcc1e6006788acac06467e28e660876e51a0`.
This whitespace step changes no estimator expression or setting.

The first clean build exposed upstream's missing dependency edge to its
generated `Pose6D.h`. Building the declared message target before the executable
resolved it without changing the frozen estimator source. The initial failure,
message-generation log and successful build log remain under ignored
`experiments/generated/r3_backend_restore/`. The
[restore script](../experiments/restore_fastlio_workspace.sh) records these
steps and refuses to overwrite an existing workspace.

The rebuilt executable is byte-identical to T14:
`4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792`.
It uses the retained ROS environment; this was not a new Conda installation.
The environment's original history hash matches. The
[explicit package lock](ros_environment_explicit_lock.txt), SHA-256
`bd423e98ce6ee4b073742977e1bd3933e485aee9ee6339735e6c75ea02069c1b`,
preserves its package URLs for later reproduction.

The retained seed-14 development corridor bag previously ran through the
repaired lifecycle. That V2 replay finished with 600 health groups, 600 DCReg
rows, 597 recorded valid poses, 1,194 evaluation rows and zero reference gaps.
It predates the 28 September worker-supervision and unavailable-pose changes,
so it does not verify the current wrapper. The current replay and cached resume
are documented in the linked native evidence report. The earlier
[validation manifest](r3_development_validation.json) identifies that older
runner, script, runtime, backend, run manifest and retained output hashes; it
remains historical. Both replays are `development_only` and add no
primary/calibration event. The earlier V1 lifecycle replay is also retained as
development verification.

## 29 September native replay preflight — stopped before estimator launch

The Acer partition mounted normally at `/run/media/harshil/Acer` and showed
about 104 GB free at mount time. Its ROS environment reports Python 3.12.14,
NumPy 2.5.3 and a working `rospy` import. The retained seed-14 corridor input
is labeled `role=development`, `seed=14`, `control=false`; no held-out input
was inspected.

The pre-existing Acer `fastlio_ws` executable hash was
`08788d6567e5fa1ac633f7006a351fb49c1d76a0a8fd6a477f90532e970155a6`, not the
required T14 hash `4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792`.
The restore script successfully rebuilt the pinned source on Acer with the
expected source-diff hash, but produced binary hash
`181f1aed0e39fe799a8eaa71b3fb60e7b25920787489cbc099ca1aa1ea153781` at
`fastlio_ws_r3_20260929`. A second build used the recorded
`/tmp/fastlio-t13.XBDWGy/ws` name through an Acer-backed symlink; catkin
canonicalized it to the physical Acer path and produced
`6fc44efd8fb17f4d5311d07675cb909bf691947bb606bd29ec2e1a172ec23433`.
Neither binary was executed in a replay. Both workspaces and build logs are
preserved on Acer; the old workspace was not overwritten.

The previous validation used ext4 at `/tmp/fastlio-t13.XBDWGy/ws`. Catkin's
canonical-path behavior explains why the Acer-backed symlink did not reproduce
the expected build identity. After removing only that symlink, the restore
script rebuilt at the exact ext4 path and the binary matched T14. The workspace
occupies about 572 MB on Linux.
At the end of this preflight, no native replay had started. The user then
approved the temporary Linux build while preserving a 1 GB free-space reserve.
The exact-path binary matched T14, the replay completed and ordinary cache
resumption returned `CACHED`; see
[R3_NATIVE_SEED14_REPLAY_20260929.md](R3_NATIVE_SEED14_REPLAY_20260929.md).
After the build, Linux retained about 4.94 GB free; all replay outputs are on
Acer.

## Saved analysis and figures

The repaired T16 analyzer rechecks all 64 primary manifests and 768 listed
output files. The development threshold, 32/32 recovery count, one relapse and
48-pair final target reproduce. Its current manifest and the no-data final plan
are canonical; the preceding versions are preserved in `evidence/archive/`.

Both repeat figures are saved as PNG, PDF and SVG, with exact input/script/export
hashes in [the figure manifest](../figures/t14_repeat_figure_manifest.json).
Their layout was visually inspected. Earlier rendering drafts remain in
`experiments/generated/figure_drafts/t14_repeat_v1/` and `t14_repeat_v2/`.
The repeat report distinguishes event agreement from warning-state and delay
variability; no general repeatability claim is inferred from two layouts.

## Remaining audit and paper scope

The independent reviewer accepted the provenance repair, earlier
cache/wrapper software fixes, and the current native seed-14 replay with
cached resumption. Overall R3 remains **REVISE** because the original plan
requires Point-LIO indicator comparability and development replication
readiness; no primary-only waiver was approved. No implementation freeze or
held-out authorization exists yet. Point-LIO comparability, final statistical
results, the publication novelty audit and the complete manuscript remain
required under the user's [paper completion plan](../execution/PAPER_COMPLETION_PLAN.md).
