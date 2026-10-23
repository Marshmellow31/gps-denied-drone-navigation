# Independent restoration and recovery review

**Date:** 9 October 2026. **Decision: PASS for the bounded input-restoration
approach and fresh development-replay recovery path; REVISE for current
primary-evidence completeness and overall R3.** This is not acceptance of a
completed restoration, fresh replay batch, or new scientific result.

Missing runtime evidence can defensibly be replaced by newly recorded
same-input development replays before R3, with complete new provenance and
fresh analysis under the unchanged frozen method. These are new technical
attempts of the same development scenes, not recovered historical runtime
manifests and not additional independent events. The original loss must
remain visible.

## Evidence independently checked

The reviewer read the restoration helper, formal-route adapter, simulator bag
writer, tracked T16 input identities, current machine-loss audit, prior R3
review, accepted Point-LIO amendment and paper completion gates. No native
replay, held-out generation or held-out inspection was performed.

All 320 primary T14 manifest/key-stream entries in
[`restoration_artifact_audit_20261009.json`](../evidence/restoration_artifact_audit_20261009.json)
were independently checked against current files: **67 hash matches, 253
missing, zero mismatches, two retained run manifests and zero complete
five-artifact primary sets**. Audit SHA-256:
`51d7990cdafd1655b8142f0d9ec763c9546782a77d106e00f95df80aeb64abce`.
The audit covers the listed manifest and four key streams, not every original
log, Hessian or repeat artifact. Complete raw retention needs a wider audit.

The historical input hash anchor is the tracked
`t16_development_analysis_manifest.json`, SHA-256
`3cf0c51aa04367cdffdd208ffe3914233c5478e7a12cd6a0854ac3359b6f0d17`.
It records input bag, analytic reference and reference-metadata identities
for exactly 32 development corridor/control pairs. The reviewer independently
rehashed the first **13 completed restored input triples and new generator
manifests** from a snapshot of the running restoration report; all matched.
This is a partial check while generation is running, not a 64-input PASS.
The live report is
[`development_input_restoration_20261009.json`](../evidence/development_input_restoration_20261009.json).

## Helper and frozen-method assessment

`restore_development_inputs.py` (SHA-256
`3e487c3e3ac97543a72a3f898c2a447a14b99bd78f0382331f74856b36341fcc`)
requires exactly seeds 14–45 crossed with corridor/control, invokes the
development-only formal generator, and checks actual bag/reference/metadata
bytes against the historical identities. It checks development role, sensor
and layout seed, control identity and absence of truth in the sensor bag.
It reports new generator manifest hashes separately from original manifest
hashes, leaves historical runtime restoration explicitly false, and atomically
saves progress/failure. Existing input folders are checked, not overwritten.
The formal adapter also refuses existing output paths, non-development seeds
and durations other than 60 seconds. There is no backend replay, estimator
result synthesis, threshold fitting or final-data access in this helper.

The reviewed formal-route adapter translates the frozen start to x=-6 m
without changing sensor random streams or motion derivatives. Matched hashes
establish the restored scientific input bytes, independent of whether new
generation time/revision bookkeeping differs. This does not establish old
runtime provenance or estimator output equivalence.

The helper checks the 1 GiB Linux and output-filesystem floors before each
input. This is a minimum guard, not a projected full-batch storage guarantee;
reserve enough space for remaining inputs and raw native diagnostics before
replay. Retain the actual helper/generator files, exact commands, isolated
runtime versions and source hashes with the final restoration record. The
new helper itself can be untracked during execution, so a Git dirty-diff hash
alone does not identify it. A recorded standalone helper hash is necessary.

## Required recovery artifacts and gates

1. Complete and independently hash-check all **64** restored input triples;
   retain every new raw generator manifest. Verify the existing development
   geometry-screen lineage against current frozen route/simulator/audit source
   identities. Any hash discrepancy must stop that restoration/replay; do not
   change geometry, noise or seeds to force a match.
2. Restore the approved FAST-LIO source, configuration and isolated runtime,
   verifying pinned source/dirty patches and executed binary identity. The
   historical T14 binary was
   `4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792`.
   Validate a fresh bounded development replay, full-stream/flush checks and
   safe lifecycle before a large replay batch. A changed binary/runtime must
   be disclosed and reviewed for equivalence; it is not silently the old run.
3. Use separate dated replay IDs/output directories and an append-only
   attempt ledger. Retain immutable new input/runtime/run manifests, raw pose,
   health and Hessian streams, exporter/evaluation/comparator files, logs,
   source/configuration/binary/runtime fingerprints and all failures. Do not
   create old manifests from remembered hashes or splice unattested fragments
   into a purported historical completed run.
4. Establish a complete coherent 64-run development analysis input set with
   exact correspondence to the 32 original paired scenes. Compare new key
   streams against every historical expected hash and retained fragment;
   explicitly distinguish identical output, numeric-equivalent regeneration
   and substantively changed outcome. Preserve original and new versions.
   Differences are evidence about reproducibility, not a reason to retry
   until a favored historical answer appears.
5. Recompute all development labels, unavailable/failure denominators,
   threshold-selection curves, event outcomes, relapse/missing-window results
   and sample-size calculation under the existing frozen rules. Reconcile
   historical T16 tables and the candidate FAST-LIO threshold with the new
   evidence. Exact input hashes alone do not restore those conclusions.
   The historical candidate is not an R3-locked operating point; any
   discrepancy must be resolved/disclosed under the frozen development rule
   before freezing, without method changes or final-data tuning.
6. Recover or newly record the required seed-14/seed-45 repeatability evidence
   and its source/output provenance; repeat the quantitative repeat audit.
   Repeats never increase the event denominator. Retain prior failure and
   substitution disclosures. Independently accept the new primary recovery
   bundle, complete Point-LIO development replication and its separate freeze,
   then seek overall R3 acceptance and implementation freeze.

## Effect on Point-LIO and study status

The main-agent runtime audit additionally reports that the preserved FAST-LIO
source commit/dirty patch and nine replay/analysis source hashes match, but
neither available copied binary equals the historical T14 executed binary.
The copied `fastlio-t13.XBDWGy` executable hashes to
`6fc44efd8fb17f4d5311d07675cb909bf691947bb606bd29ec2e1a172ec23433`;
`fastlio_ws_r3_20260929` hashes to
`181f1aed0e39fe799a8eaa71b3fb60e7b25920787489cbc099ca1aa1ea153781`.
These values are supplied by that audit, rather than a second independent
binary check in this review. Exact historical binary replay is currently
**BLOCKED**. Investigate genuine retained binary/object recovery; if exact
identity cannot be recovered, record the changed build and obtain bounded
equivalence acceptance before representing fresh replays as a recovery of
the old implementation. Matching source alone does not close this issue.

The loss does **not** invalidate the independently accepted preserved
Point-LIO one-seed R2 pair, whose actual raw outputs, input and source
identities remain verified. It does not require stopping preparation or
development-only Point-LIO replication once each required restored input,
runtime and runner check passes. Its own 32 pairs use Point-LIO poses and the
separate frozen development threshold rule; they must not depend on missing
FAST-LIO labels or copy the primary estimator's outputs.

For resource efficiency, verify one fresh primary recovery replay before
launching a large native batch. Run native replays sequentially. Completing
Point-LIO replication cannot repair the missing primary evidence. Current
primary readiness therefore remains **REVISE**, irrespective of successful
input restoration or Point-LIO replication. No implementation freeze,
held-out screen/run, final-performance statement or new manuscript conclusion
is supported until primary recovery, separate replication freeze and R3 PASS.

## Follow-up: first restored primary native replay

**Decision: PASS for A2 development lifecycle; REVISE for numerical
reproducibility/equivalence; hold the large primary recovery batch.** The
changed executable has not demonstrated acceptable restoration equivalence.
This additional blocker does not change the independently verified Point-LIO
one-seed acceptance.

The completed input-restoration report is now PASS. The reviewer independently
rehashed all **192** scientific input artifacts across the 64 development
slots: every bag/reference/metadata hash matches its tracked historical
identity. This supersedes the earlier partial 13-input check for scientific
input bytes; historical estimator outputs/runtime manifests remain missing.

The reviewer inspected
[`fastlio_restoration_smoke_20261009.json`](../evidence/fastlio_restoration_smoke_20261009.json),
the relink report
[`fastlio_binary_restoration_20261009.json`](../evidence/fastlio_binary_restoration_20261009.json),
the preserved native R3 seed-14 manifest/raw streams, copied source and build
flags, runtime history, current library resolution and prior repeatability
audit. All 11 A2 output hashes were independently rechecked. A2 completed in
72.29 seconds with 600 diagnostic groups, 597 poses/valid diagnostic frames,
1,154/1,194 valid local windows and zero reference gaps. The preserved A1
restoration failure remains separate. Successful lifecycle is not numerical
equivalence.

Independent comparison of A2 against the preserved native seed-14 stream
confirms timestamp/frame availability agreement but substantial output
differences: maximum x difference **1.602700388 m**, maximum 1-second local
translation-error change **0.399867788 m**, maximum 3-second change
**0.741261665 m**, and 100 changed DCReg state rows. These are algorithmic
output differences, not numerical CSV-rounding tolerance. The first emitted
pose differs only around `1e-18 m`; position differences exceed `1e-6 m` at
simulation time about 11.10 s, `1 mm` at 16.80 s, `0.1 m` at 21.20 s and
`1 m` at 58.70 s. The first changed accepted-correspondence count occurs at
15.60 s (261 versus 262). Small early numerical differences followed by
growth and changed correspondences are observed; their cause is unresolved.

The reviewer independently verified the configuration hash, FAST-LIO parent
HEAD and dirty-diff hash against the preserved R3 fingerprint. The ikd-Tree
submodule is clean at
`e2e3f4e9d3b95a9e66b1ba83dc98d4a05ed8a3c4`, equal to its parent gitlink.
The current conda-history hash also matches the historical fingerprint.
This rules out those inspected identity changes; it does **not** establish
all compiler/header/object/dynamic-library identities. The current recorded
flags include `-O3`, OpenMP and `MP_PROC_NUM=3`; native code uses parallel
correspondence search and an asynchronous ikd-Tree rebuild thread. These are
concrete candidate repeatability/numerical-amplification paths, not a proven
diagnosis. Relinking retained objects produces the copied `6fc44...` binary,
not the original `4da32...` binary. An unchanged source commit or environment
history is insufficient to certify identical machine code or loaded library
bytes. ROOT_DIR relocation by itself has not been shown to explain the result.

The historical repeatability audit already reports some same-input/backend
variability: seed-14 corridor was identical, whereas seed-14 control had a
maximum 1-second translation-error change of 0.11591 m; seed-45 corridor/control
had 0.16840/0.41596 m. Seed-45 corridor had 112 confirmed DCReg disagreements.
Those different scenes and processed decision definitions are not a numerical
acceptance bound for the present seed-14 discrepancy. Neither the existence
of prior variability nor complete stream coverage justifies treating A2 as an
equivalent restored primary run.

**Next bounded investigation:** preserve A2 unchanged and compare the proposed
identical A3 replay (same input/configuration/executable/library environment)
to both A2 and the preserved historical seed-14 stream. Record the earliest
pose/Hessian/correspondence divergence, numeric differences, raw and confirmed
state disagreements and unchanged completion/availability fields. If A2/A3
agree while both differ from history, prioritize build/header/object/compiler
and loaded-library identities. If A2/A3 differ materially, investigate native
parallel/asynchronous repeatability and replay scheduling without asserting
that restoration changes are absent. Both explanations can coexist. A third
replay agreeing with a favored historical answer would not repair historical
binary provenance or justify discarding the others.

Capture compiler version, object hashes and compile definitions, Eigen/PCL
header identities, actual resolved library paths/hashes and thread settings
before further diagnostic changes. Search retained historical build material
for corresponding identities. Additional experimental controls, such as
changing native thread scheduling, belong in separately recorded diagnostic
builds/runs; they must not silently replace the approved backend or frozen
primary protocol. Do not fit a threshold, launch the 64-run primary recovery
batch, assert restoration equivalence or expose held-out data while this
blocker is unresolved. Input restoration itself cannot diagnose it.

**A3 follow-up:** the reviewer independently verified the A3 output hashes in
[`fastlio_restoration_repeat_20261009.json`](../evidence/fastlio_restoration_repeat_20261009.json).
A3 completed in 72.11 seconds; its pose, health, Hessian and DCReg streams are
byte-identical to A2. Evaluation fields are identical except the new run ID.
Thus the observed two-run restored seed-14 workflow is stable and both runs
have the same discrepancy from the historical native result. Ordinary
between-repeat variation was not observed in this controlled comparison.
This narrows the next investigation toward build/runtime restoration
differences; two stable repeats alone do not establish their precise cause
or rule out every timing-sensitive effect.

The current executable's `.comment` records Ubuntu GCC 15.2.0 and conda-forge
GCC 14.3.0 signatures. Current dynamic resolution uses conda `libgomp` and
`libstdc++` but system `libm`/glibc. No corresponding historical compiler,
object, header or resolved-library hash baseline is present in the inspected
native run fingerprint. The reviewed source's ROOT_DIR uses concern file
paths/output; it has not been shown to alter estimator equations. Rebuilding
with the exact preserved recipe at historical
`/tmp/fastlio-t13.XBDWGy/ws`, while capturing these identities and observing
the Linux storage floor, is a concrete bounded recovery investigation. It
must use a separately retained build/output identity. If it reproduces the
historical binary SHA-256, follow with one bounded native comparison before
the large recovery batch. If it does not, preserve the difference and locate
the changed compile/dependency/runtime identity; do not accept numerical
equivalence from source/hash-of-history agreement. No equivalence acceptance
is granted by this follow-up.

**Historical-path rebuild follow-up:** independent hashing confirms that the
new build at `/tmp/fastlio-t13.XBDWGy/ws` reproduces the exact historical T14
executed binary SHA-256
`4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792`.
The reviewer also verified source HEAD/diff, ikd-Tree submodule commit,
configuration and conda-history identities against the preserved native
fingerprint. Build-log SHA-256 is
`f6af33bd02a70c7a87a9deae35f79b8b8799998ac4ad69585c8c9225e17ccc4e`.
This closes exact executable recovery for this build. It does not yet close
native-output reproducibility; the proposed A4 bounded replay must be
compared with preserved historical raw streams. Matching historical bytes
after the historical-path recipe is observed evidence, not proof of the
mechanism behind moved-build trajectory differences. A1–A3 remain preserved
as separately identified attempts.

**A4 acceptance: PASS for restored primary seed-14 lifecycle and output
reproduction.** The reviewer independently checked all 11 output hashes of
the completed A4 manifest and confirmed the exact historical binary identity.
A4 completed in 72.27 seconds. Raw poses, health, Hessians and DCReg are
byte-identical to the preserved native R3 seed-14 outputs; all 1,194 evaluation
rows agree exactly after excluding only new run/event identifiers. See
[`fastlio_historical_binary_replay_20261009.json`](../evidence/fastlio_historical_binary_replay_20261009.json).
The bounded native recovery blocker and corresponding large-primary-batch
hold above are now closed **for this exact recovered build**. The moved
`6fc44...` executable remains a separately preserved, nonequivalent attempt;
this PASS does not establish the mechanism of its trajectory difference.

**Portable backend preflight repair: PASS within its identity-only scope.**
The reviewer inspected the small `_read_t14_backend_reference` fallback,
its two new tests and updated existing identity test. The compact snapshot
SHA-256 `0fdb0ccc18285fdce7e41d0072beeb354391a6b1887619b9f13c9002fd6a8213`
is hard-bound in code and added to the required R3 freeze inventory.
Independent comparison confirms its `backend`, `sources` and `runtime`
objects exactly equal the surviving seed-31 corridor manifest fingerprint,
whose actual SHA-256 is
`a02a97a75075289447a8c5073be87ec6437073c75d755ebb04313002380ea416`.
The snapshot supplies no completion status, outputs or scientific outcome.
It fixes source/backend lookup when the historical seed-14 manifest is
absent; it does not manufacture that run or restore its results.

All three focused backend-reference tests passed under the frozen isolated
Python. A direct read-only `_check_backend` call on the recovered historical
workspace also passed, including actual `rosrun` executable resolution,
binary, source/diff, history, nine source hashes and frozen patches. The
fallback cannot bypass final R3/implementation-freeze/runtime gates: those
checks remain intact, and the additional snapshot inventory requirement must
be accepted in a future freeze. Metrics, threshold rules, splits and protocol
are unchanged by this repair.

Primary recovery may now proceed using the exact recovered native build,
restored hash-matched development inputs, fresh dated provenance and the
unchanged frozen method. One reproduced seed is not restored 64-run evidence;
all remaining completeness, reanalysis, repeatability and Point-LIO
replication/freeze requirements above remain. Overall R3 stays **REVISE** and
held-out work remains sealed.
