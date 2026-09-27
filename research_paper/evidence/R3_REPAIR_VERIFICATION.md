# R3 repair verification package

27 September 2026. Status: implementation repairs and development verification
prepared for independent re-review. The initial R3 verdict remains **REVISE**
until that reviewer audits the current package. No actual held-out layout,
sensor input or estimation result has been generated, screened or inspected.

## Repair evidence

| Repair | Current implementation and direct verification |
| --- | --- |
| T16-R3-01 | The declared route constant is defined. The run lifecycle persists a manifest before launching a subprocess. Mocked successful, crashed, timed-out, cached and interrupted paths verify the manifest and ledger transitions. |
| T16-R3-02 | Completion requires all 600 input diagnostic timestamps, matching health/DCReg horizons, a populated pose stream spanning the run, normal playback completion, logger flush/count agreement and evaluation row/reference agreement. Header-only poses, truncated groups, early-exit prefixes and incomplete derived output are rejected. Invalid/unavailable estimates remain accepted evidence in a completed run; no accuracy threshold or exact valid-pose count is used to decide execution success. |
| T16-R3-03 | R3 requires one machine-readable JSON content inventory with named hash bindings and the exact threshold. Screen/run verify the current development manifest and derived plan, complete ascending candidate prefixes, unique selected seeds, all saved geometry-screen records, current sources and review/freeze lineage. The frozen Python/NumPy versions are checked before geometry access. Backend verification resolves the executable selected by `rosrun`, checks the source revision/diff and matches the saved dependency-history hash. Those identities enter every run fingerprint. Negative fixtures reject stale/duplicated selection before geometry or backend access. |
| T16-R3-04 | Scalar and vectorized threshold-sweep debounce both reset at segment changes and count the first valid record in the new segment. Regression fixtures cover segment-reset parity. Development analysis was rerun in a separate output folder and reproduces the selected threshold and event counts. |
| T16-R3-05 | Planned post-exit 3-second rows with missing endpoints are retained as unavailable when their nominal endpoints fit the horizon. Regression fixtures cover missing endpoints; current complete-data counts reproduce. |
| T16-R3-06 | Input generation, paired-bag auditing, archival, replay and postprocessing have durable stage/attempt records. Interrupted partial bags remain in their original folder while a single technical retry uses a new folder. Derived-output processing and interrupted archival resume on the same raw input with bounded retries. Confirmed live processes prevent concurrent resumption. Terminal run states are appended to the ledger. An incomplete batch exits nonzero and never substitutes geometry. |
| T14-R3-01 / T16-R3-07 | The [repeat audit](T14_REPEATABILITY_AUDIT.md) verifies 64 primaries and four repeats, measures aligned errors/scores, raw and confirmed decisions, corridor labels/delays, and paired-interior substitution sensitivity. No repeat enters threshold fitting or independent-event counts. The seed-14 smoke substitution remains for independent adjudication. |

## Test evidence

The complete suite runs **119 tests: 118 pass, one optional SciPy-dependent
scene test is skipped** in both environments:

- Frozen analysis environment: Python 3.12.14 / NumPy 2.5.3;
  [retained log](r3_tests_frozen.log), SHA-256
  `0699bd4b8c714d48d2ba12a0939432b2683f77e8c98d92223a2a760f20556d29`.
- System environment: Python 3.14.4 / NumPy 2.3.5;
  [retained log](r3_tests_system.log), SHA-256
  `d191c08fad37a3cbd40906728e4568b796f0d1a884be27206aab9673141d6350`.

The 28 focused final-runner/input/lifecycle checks use mocked processes,
temporary files and development-shaped streams. Reserved numeric seed IDs
appear only in no-data plans and synthetic selection-rejection fixtures;
the tests never sample their geometry. Other focused checks include the five
repeat-audit tests and the analyzer's reset/missing-window regressions.
Tests are evidence for these behaviors, not proof of a publishable finding.

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

The actual retained seed-14 development corridor bag then ran through the
repaired lifecycle. The current-source V2 replay finished with 600 health
groups, 600 DCReg rows, 597 recorded valid poses, 1,194 evaluation rows and
zero reference gaps. Logger/horizon completion checks passed. The
[validation manifest](r3_development_validation.json) identifies the exact
runner, script, runtime, backend, run manifest and all retained output hashes.
Its role is `development_only`; it adds no primary/calibration event. The
earlier V1 lifecycle replay is also retained as development verification.

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

The independent R3 reviewer must verify this package and the current source,
then decide PASS or further REVISE and produce an implementation freeze if
appropriate. A PASS would permit the specified primary held-out phase.
Point-LIO comparable indicators and replication, final statistical results,
the publication novelty audit and the complete manuscript remain required
under the user's [paper completion plan](../execution/PAPER_COMPLETION_PLAN.md).
