# Independent Point-LIO replication freeze review

Date: 10 October 2026. **Decision: PASS for the exact separate Point-LIO development/operating-point freeze below, pending overall R3.** No held-out access, native replay or freeze modification was performed by this reviewer.

Accepted artifact: [`POINTLIO_REPLICATION_FREEZE_20261010.json`](../protocol/POINTLIO_REPLICATION_FREEZE_20261010.json), SHA-256 **`87f31c5febff860fe774eb4533a1be584f68b663f0125ea40dc18e85cc587621`**. This report supplies independent acceptance of that immutable artifact; its embedded `PROPOSED_FOR_INDEPENDENT_REVIEW` field records the submitted state. A changed artifact requires a new hash/readback, rather than inheriting this exact-file acceptance.

## Audit

Every explicit artifact hash was checked against its actual file: R2 freeze, D050 amendment, METRICS, splits, completed native schedule, native acceptance anchor, producer snapshot inventory, corrected Point analysis and candidate table, both analysis sources, all five output CSVs, independent development acceptance, complete-suite log and development figure manifest. All match. Native binary/configuration, nine-file source identity/commit/dirty patch, Python runtime and glog overlay fields equal the independently accepted development cohort identity. The schedule and corrected analysis transitively bind all 64 native/evaluation manifests, historical producers, input identities and complete runtime records, including the conda-history digest.

The locked selection exactly equals the accepted corrected v2 result: **19,104 finite valid raw corridor scores plus `NO_ALARMS`; cutoff 123.80876977779258; 3/32 initial false-healthy events; 21/27 post-onset detections**. The full cohort and every candidate row were independently checked in the [development acceptance](POINTLIO_DEVELOPMENT_ACCEPTANCE_20261010.md); no feasibility, control or repeat event enters selection. The freeze keeps Point-LIO's own pose-derived labels, D050 frame-pooled common-basis measurement geometry, L=1/3/5 outputs, fixed strict DCReg `kappa > 10`, missing-data/failure policy and unchanged 48-pair primary budget.

The recorded complete-suite log contains `Ran 210 tests` and `OK (skipped=1)`, matching 209 passed and one skipped. Reading that log is a provenance check, not a fresh execution of the suite. Development results retain their fitting-population and simulation limitations.

## Bounded revisions resolved

The first proposed artifact, hash `de86c31cc7c3d7bbc2837f4720318cf890fc46cc3894f08598c8236af8d55154`, needed two wording repairs. Its decision summary did not restrict repeated-source reset to an inactive candidate, potentially contradicting METRICS' maintained confirmed-healthy state. It also grouped successful final screening with preconditions for opening final data, making the intended order ambiguous.

The accepted version explicitly scopes repeated-source handling to pending `INACTIVE` debounce and preserves an active healthy state while observations remain healthy and in the same segment. It separately requires overall R3, the overall implementation freeze and this independent acceptance before final geometry generation/screening; native replay additionally requires a passing frozen geometry screen and the exact same selected 48 pairs/input identities as primary FAST-LIO. These clarifications preserve the existing protocol and resolve both review findings.

## Gate limitation

The artifact explicitly declares `heldout_inputs_opened=false` and `heldout_generation_or_replay_authorized=false`. The actual current R3 report remains REVISE and no overall implementation-freeze file exists. This separate acceptance therefore opens no held-out gate. Final execution/analysis interfaces and their exact source dependencies still need the overall R3 review and freeze. No final-performance, cross-backend superiority, physical safety or publication-novelty conclusion follows from this PASS.
