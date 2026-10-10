# Independent Point-LIO development acceptance

Date: 10 October 2026. **Decision: PASS for the completed 32-pair Point-LIO development cohort and corrected analysis v2.** The original analysis received REVISE for an incomplete threshold-candidate population; the bounded repair is accepted below. A separate development replication freeze can now be prepared from these exact identities. This report does not create that freeze or pass overall R3, authorize held-out access, or establish publication novelty or final performance.

## Evidence inspected

The review used the active scope, execution plan, frozen METRICS and D050 amendment, accepted one-seed/workflow reports, actual native outputs, all 64 saved verifications and offline evaluations, launch receipts, durable schedule and analysis source. No held-out geometry, input, screen or result was accessed; no native estimator was run. Temporary offline calculations/re-exports left native data unchanged.

The durable cohort is `/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/POINTLIO_DEVELOPMENT_20261009/`. Its schedule hash is `cae6c6039463b2aa76588596860842c586d57668c0b2e035a7866e23003c414d`. The exact scheduled population is seeds 14–45, each with one corridor and one control: 64 native directories, receipts, verifications and evaluations, with no extra or substituted slot. The two cached slots retain their original completed attempts; the other 62 completed normally. All receipts are `PROCESS_EXITED`, return code zero, bound to the same cohort identity and correct input slot. All required native subprocess exits are accepted by the verifier.

The reviewer re-ran the production verifier and loader for **all 64 actual native attempts**, checked each result against its saved verification and schedule, and independently reconciled receipt/native/cohort identities. This rechecks every native output hash/file set, actual input bag headers, development input/reference/metadata hashes, native source/config/binary, repository producer sources, Python binary/conda history and glog overlay, plus complete frame IDs and truth-free pose segment joins. The 39-file preserved producer snapshot and all five original analysis CSV hashes match. The R2 bundle still reads back **53/53 hashes matching**.

The retained native binary is `80516da9cafba98262d56c17cc26ec4da76e214049d3af7776248b4c3a342b17`; config is `d23bd8799c3834ac0acc1d23476a0a0c0cd72b09f7b7c542b5bfbe9813a4c98b`. Native commit is `4b86a469eb5572e70ed575af25b5f15dd06e8e3c`, dirty patch `1270c63b553f660ade9cd787c0e377d1486ac4f49018650f400f2cf52eb3445c`. Runtime is Python 3.12.14 / NumPy 2.5.3, bound to the recorded interpreter and environment hashes. These are unchanged from the accepted workflow.

## Actual coverage and outcome accounting

The 64 attempts contain 38,400 input/indicator frames, 38,208 emitted poses and valid indicator frames, 11,968,592 group-ledger records and 14,780,097 Jacobian rows. Each attempt has exactly two startup-initialization and one map-initialization unavailable frame: 192 explicit unavailable frames overall. There are zero resets and no failed/incomplete attempt in this formal cohort. Earlier feasibility failures remain separate preserved evidence; this statement does not erase them.

All 64 evaluations retain 76,416 rows: 38,208 each for the 1 s and 3 s windows, 73,856 valid local windows and zero reference-invalid rows. The three lever-scale outputs remain preserved for every frame. Startup and end-of-recording unavailability are not converted into healthy decisions or zero errors.

The reviewer independently re-exported the final seed-45 corridor and control from their complete raw frame/group/Jacobian CSVs using the frozen runtime. Both regenerated indicator CSVs and segmented pose CSVs are byte-identical to the native outputs. This extends the previously accepted exact seed-14 pair re-export. Raw numerical reconstruction was sampled at those endpoints; it was not independently repeated for every Jacobian in all 64 runs. Full-cohort hashes, coverage and native/export contracts were checked for every run.

All 32 corridor labels use Point-LIO's own segmented poses and analytic reference. An independent earliest-valid-triple/relapse calculation over their own-pose windows agrees with the saved recovery outcomes: **27 recovered, five without recovery within the horizon, one relapse**. All 32 corridors are truth-label eligible; controls have no recovery labels and never enter fitting. The scalar's post-exit decision availability is 6,400/6,400 ticks. All 27 recovered events remain in its sensitivity denominator, including six detection misses.

| Development quantity | Point-LIO scalar | Point-LIO DCReg |
| --- | ---: | ---: |
| Initial false-healthy events / eligible available events | 3/32 | 11/32 |
| Post-onset detections / truth-recovered events | 21/27 | 20/27 |
| Median delay among detected events only | 3.200277779 s | 1.750277779 s |
| Post-relapse false-healthy events / available relapsed events | 0/1 | 1/1 |

The original complete method summaries, including controls and denominators, match a fresh shared-rule recomputation. The independent candidate state calculation described below also reproduces every original scalar candidate's false-healthy/detection counts. These are development descriptions measured on the fitting population. DCReg's fixed rule has no fitted scalar cutoff; its larger false-healthy rate is retained rather than optimized away. Backend-specific truth-recovery counts differ, so raw detection counts should not be interpreted as a common-denominator superiority result.

## Candidate-population defect and accepted repair

METRICS lines 239–240 and 255–257, and D050's selection rule, require every unique finite valid corridor score plus `NO_ALARMS`. The original shared selector instead formed candidates from the scores selected by 10 Hz association. This omitted one terminal valid record per corridor: frame 600, timestamp `1059999722221` ns. Those 32 omitted scores are listed below. The decision grid defines alarm timing; no inspected frozen rule restricted the candidate population to associated records.

The original Point analysis under `analysis_20261010/` is retained as superseded evidence. Its manifest hash is `c80d0b7ac6eb5b7d5ceb2d5f7b7334b3014d24a93d083b02bf319a90f0e0975b`; its candidate CSV hash is `e19e8bbed9eaf321c40f65bcb4e2593f9a6cf1ee83876768b037a2ef5333e8e9`. It enumerated 19,072 scores plus `NO_ALARMS`, instead of 19,104 plus `NO_ALARMS`.

The repaired shared selector takes candidates from finite valid raw diagnostic records while preserving the frozen decision association, debounce, objective, denominators and tie rule. The reviewer inspected this bounded source change and the synthetic unassociated-score/invalid-row fixture. Independently implemented candidate-by-event state calculations enumerated all **19,105** allowed candidates and compared every row of the official corrected CSV, including threshold, numerator, denominator, rate and feasibility flag. All agree. The higher-threshold tie rule still selects **123.80876977779258**, yielding 3/32 false-healthy events and 21/27 detections. No native replay or protocol amendment is required for this correction.

The accepted official output is `analysis_20261010_v2/`:

- Manifest: `e3a03d83f5854c5705177bc7610cb6ff18d9f0d331f50783c23dcd036b6ce254`.
- Candidate CSV: `78338dddfa6fc777f06f0a7e87a704269dc09ceb12cd303b89456832688cac58`.
- Shared `t16_development_analysis.py`: `f34fa9479e95bfa78823e3be8f70d63445631d09f3d46fe59a75331ae2975077`.
- Point analysis source: `ff8968a8bf7658ebfe6b35dd9a7ebf268f2c28c817c6d1d261f2890acec21c7b`.

All five corrected CSV hashes read back. Relative to the original analysis, only threshold candidate metadata, the candidate CSV and shared-source identity change; labels, event-metric CSVs, lever-scale CSV, native/evaluation provenance and all method metrics are identical. The same original defect affected FAST-LIO. The independent raw-score calculation preserves its 166.16366016039856 cutoff and 1/31, 13/32 event counts; acceptance of the separately regenerated FAST-LIO artifact remains outside this Point report.

## Freeze readiness and limits

A separate Point-LIO development freeze may bind the corrected analysis and candidate rule, source/config/runtime identities, all native and evaluation manifests, accepted measurement adaptation and this report. Preserve the original producer snapshot when future final-interface code changes: changed current files must not be misrepresented as the historical native producer. The Point cutoff is separate from FAST-LIO; the planned 48 final geometry pairs remain unchanged. Overall R3 still requires the complete final execution/analysis interfaces and exact implementation freeze. This PASS supplies no held-out authorization by itself.

Simulation realism, final uncertainty and final performance remain unproven here. Stored 3 s windows and L=1/5 m scores are available for the frozen sensitivity reporting; this review does not claim the full final sensitivity analysis or manuscript is finished.

### Omitted original terminal candidate scores

All rows below refer to formal corridor frame 600 at timestamp `1059999722221` ns; they are now included in v2.

| Seed | G3 score |
| --- | ---: |
| 14 | 121.79658584956745 |
| 15 | 83.64628264804941 |
| 16 | 128.7413481762822 |
| 17 | 134.05552096301994 |
| 18 | 97.54042901495215 |
| 19 | 108.11230832463612 |
| 20 | 69.23956378505063 |
| 21 | 92.87114389046839 |
| 22 | 66.94022567937154 |
| 23 | 191.274718975748 |
| 24 | 120.65796948270898 |
| 25 | 131.13805264162448 |
| 26 | 139.60493872439588 |
| 27 | 69.36610795905953 |
| 28 | 83.55152356797598 |
| 29 | 73.85604751000957 |
| 30 | 64.37358910218074 |
| 31 | 125.18600015218708 |
| 32 | 144.0435648904058 |
| 33 | 173.36872155615035 |
| 34 | 128.63106182031984 |
| 35 | 168.6734359755361 |
| 36 | 70.99995677820827 |
| 37 | 66.4215698176892 |
| 38 | 131.15138537533124 |
| 39 | 131.2954842097838 |
| 40 | 55.05178426213665 |
| 41 | 95.07179934815446 |
| 42 | 78.95961149225252 |
| 43 | 143.02057536790898 |
| 44 | 46.80239215841273 |
| 45 | 116.31100511779948 |
