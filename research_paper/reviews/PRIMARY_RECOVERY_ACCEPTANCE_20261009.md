# Independent complete primary development recovery acceptance

**Date:** 9 October 2026. **Decision: PASS for the fresh primary development
cohort, its default T16 reanalysis and four declared repeats only.** The
recovery establishes new complete provenance for the same frozen development
inputs. It does not recover missing historical runtime manifests, establish
identical historical outputs, pass overall R3, lock a final operating point,
or authorize held-out work.

The reviewer inspected the audit and repeat-policy extension and audited the
actual native/adapter/input files on Acer. No native replay, Point-LIO
production-file change or held-out generation/inspection was performed.

## Complete lineage and failure accounting

The actual cohort under
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/PRIMARY_DEVELOPMENT_RECOVERY_20261009/`
contains **64 completed primary scientific slots and four prescribed repeat
slots**, covering exactly seeds 14–45 in corridor/control pairs. The native
attempt inventory contains **69 attempts: 68 COMPLETED and one
INTERRUPTED_REPLAY**. The published summary retains 46 verified cached slots
and 22 newly completed slots; caches do not add events.

The reviewer freshly ran `audit_primary_recovery.audit` against all 68 slots.
Its entire returned result equals
[`primary_recovery_complete_audit_20261009.json`](../evidence/primary_recovery_complete_audit_20261009.json).
This rehashed actual inputs, native outputs and every adapter-linked output;
checked all native/adapter/cohort fingerprint and published adapter hashes;
and verified original T16 input identities and the ledger bridge. Current
read-only native backend preflight also matches the cohort identity, including
the recovered historical `4da32...` binary/source/configuration/runtime. The
reviewed recovery controller remains SHA-256
`1c00980bf1a6e7121d10f36a2b817b21fabf17a22e1db64c858e28944ce2ea51`.

The reviewer additionally reran the production complete-stream/flush validator
on **every completed native slot** and compared its result with that slot's
native manifest. All 68 agree: 600 input/health/diagnostic groups and 597 poses
each, totaling **40,800 input frames and 40,596 emitted poses**, including
repeats. Reference gaps, invalid poses and reset records remain absent under
these completion checks. Every native seed/scene/control/route identity agrees
with its scientific slot; recorded replay process groups have no live members.
The native producer and earlier accepted measurement/exporter contracts were
not replaced by adapter metadata.

The full append-only ledger has **274 state-transition rows**: 137 RUNNING,
68 REPLAYED, 68 COMPLETED and one INTERRUPTED_REPLAY. An independent row-by-row
reconciliation binds all 274 to the **69 unique native manifests** by run ID,
scheduled slot, seed/scene, attempt and input-bag hash; every final ledger
status agrees with its manifest. These are transition counts, not 274 attempts.

Seed-37 corridor's first attempt remains separately retained with its partial
files and `INTERRUPTED_REPLAY / recorded replay process is absent` record.
Its first allowed technical retry supplies the completed scientific slot;
the adapter binds the retry's actual manifest/output hashes while preserving
the original scientific slot ID. This adds no scene and no recovery label
for the failed technical attempt. Its `elapsed_s=0.0` is an initial unmeasured
placeholder after interruption, **not measured zero runtime**; return code is
unavailable. Do not use it as a resource measurement.

## Reanalysis independently reproduced

Using the frozen isolated runtime, the reviewer reran the unchanged default
T16 `analyze` function on all 64 actual primary adapters, with a fresh temporary
output folder and the new complete audit. The **entire serialized analysis
manifest and all six generated CSV hashes match**
[`primary_recovery_development_analysis_20261009.json`](../evidence/primary_recovery_development_analysis_20261009.json).
The limited generic-method parameters preserve FAST-LIO defaults; no Point-LIO
pose, score or outcome was used. Controls and repeats do not enter primary
threshold fitting. No held-out data entered this reanalysis.

| Development quantity | Historical recorded value | Fresh recovered value |
| --- | ---: | ---: |
| FAST-LIO candidate threshold | 166.16366016039856 | 166.16366016039856 |
| FAST-LIO recovery detections | 13/32 | 13/32 |
| FAST-LIO conditional initial false-healthy events | 1/31 | 1/31 |
| Fixed DCReg recovery detections | 29/32 | **30/32** |
| Fixed DCReg conditional initial false-healthy events | 0/31 | 0/31 |
| Paired interior sample SD, metres | 0.2494728850627583 | **0.2503454775041967** |
| Frozen-rule final geometry-pair requirement | 48 | 48 |

These are development-only quantities evaluated on the development cohort;
the tuned method's values are not independent performance estimates. The
fixed comparator still remains healthy after the documented relapse
(conditional post-relapse false-healthy event rate 1.0 in both recorded
analyses). Initial false-healthy and post-relapse outcomes must not be conflated.

Historical expected hashes provide **78 matches and 178 differences among
256 primary key outputs**. Changed evaluation run/event IDs contribute to
the hash differences, but they do not explain away changed DCReg outcomes or
sample variance. The fresh cohort must be described and frozen as new replay
evidence, with both historical and fresh reports preserved. No claim of exact
all-scene historical equivalence or cause of output variation is supported.

## Declared repeats independently reproduced

The reviewer reran `audit_t14_repeatability.audit` using
`repeat_policy='declared_repeats'`, the actual four fresh REPEAT1 adapters and
the newly recomputed analysis. The **entire repeat result agrees** with
[`primary_recovery_repeatability_20261009.json`](../evidence/primary_recovery_repeatability_20261009.json).
All four repeats are bound to the same input/backend/source identities as
their corresponding primary. Both corridor recovery labels agree. No
historical prebatch smoke is substituted in this new repeat policy; the old
default policy remains separately available for historical evidence.

The seed-14 control has maximum 1-second translation-error change
0.021809378 m and four confirmed DCReg state disagreements. Both corridor
comparisons and the seed-45 control have zero corresponding translation-error
change; the other confirmed-state comparisons are unchanged. Replacing
seed-14, seed-45 or both pairs for descriptive sensitivity still yields
48 geometry pairs. The threshold is not recalibrated, primary outputs are
not replaced and the repeats add **zero independent events**.

## Source and reproduction scope

The lineage auditor SHA-256 is
`2a0ee1b1fd30e3099be25bbc9a08264ed3a1d2de89eebf4a06c80de3f6bcab9b`;
the explicit repeat-policy auditor is
`847c8100959211036f621cd127a28843da946eeb69573615e301d2f7c4d41200`;
the generic/default T16 analysis is
`db506e8daca813b1f41c0cae4fdeeccdf9c23f3420a6232c453f650467b5900f`.
The readback calls were the production functions, not summaries of reported
completion. Temporary output was discarded after exact serialized/CSV-hash
comparison; retained original evidence was not altered.

For the reanalysis, use `analysis_contract` as the batch root,
`restoration_20261009` as provenance root, the new complete audit above,
and a fresh output directory. The generic command string embedded in the
T16 manifest still shows the original default-path example; it is not the
actual restoration invocation. The paths/provenance above describe the
verified recovery inputs precisely.

## Remaining gates

Primary development recovery is accepted within this scope. Preserve the
69 native manifests, all adapter/output/input identities, interrupted files,
ledger and fresh analysis/repeat reports in the next review bundle. Point-LIO
development replication and separate threshold/freeze acceptance remain
unfinished. Overall R3 also requires the complete final-ready implementation
bundle and claim/method review before an implementation freeze. No held-out
screen/run or final recovery/publication claim is authorized by this PASS.
