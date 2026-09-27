# Execution decisions and changes

Append-only record for the LiDAR recovery-reliability study. Amendments must add a new dated entry instead of rewriting prior decisions.

For live status and next actions, use the [current handoff](CURRENT_HANDOFF.md) and [status ledger](STATUS.md). Earlier entries below are dated decisions, not necessarily the current work instruction.

## 2026-09-22 — D001: initialize from the active LiDAR scope

- **Decision:** Use `RESEARCH_GOAL.md`, `SCOPE_DECISION.md`, `AGENT_EXECUTION_PLAN.md`, and the root `AGENTS.md` as the controlling scope and execution order.
- **Rationale:** These documents explicitly supersede the camera proposal, broad recovery-policy recommendation, and archived safe-landing prototype.
- **Consequences:** Work remains inside `research_paper/` except for a necessary root status/link or ignore rule. `old_data/` is not evidence for this study and remains untouched. Final-test data must not be inspected during development.
- **Evidence:** Repository state and governing documents inspected during T01 on 22 September 2026.

## 2026-09-22 — D002: do not infer readiness from installed tools

- **Decision:** Record tool presence and machine capacity as environment facts only. Do not select a ROS distribution, container strategy, backend build recipe, or Python package layout during T01.
- **Rationale:** T06 must verify upstream FAST-LIO2 requirements against the selected recording and T05 contracts; tool presence alone does not establish compatibility.
- **Consequences:** Missing ROS 2, colcon, Docker/Podman, Ninja, and CUDA are not yet blockers. Installation and architecture choices remain deferred to their evidence-gated tasks.
- **Evidence:** `execution/ENVIRONMENT.md`.

## 2026-09-22 — D003: conserve local storage before data acquisition

- **Decision:** Check official published sizes and available storage before any recording or upstream build download, and begin with only the smallest eligible development sequence or subset.
- **Rationale:** The root filesystem had only 5.5 GiB available at T01, while dataset and native-build sizes remain unverified.
- **Consequences:** T03 and T04 must treat storage as an explicit feasibility constraint; whole-dataset downloads are prohibited until justified.
- **Evidence:** `df -h .` recorded in `execution/ENVIRONMENT.md`.

## 2026-09-22 — D004: provisionally use a GEODE vehicle transition, not the unreferenced NTNU aerial transitions

- **Decision:** Select GEODE `Urban_Tunnel01` as the provisional development recording, with `Urban_Tunnel03` and `Urban_Tunnel02` as alternatives. Reject the released NTNU tunnel/fog bags as primary quantitative recordings unless an independent continuous 6-DoF reference is later found.
- **Rationale:** The NTNU recordings contain the clearest aerial weak-to-rich geometry transitions but their official paper/release does not provide continuous independent truth for those two bags. GEODE urban tunnels have claimed 6-DoF RTK/INS reference and explicit tunnel entry/exit context.
- **Consequences:** The real-recording evidence is provisionally ground-vehicle evidence and cannot be called aerial validation. T04 must verify actual reference coverage, fields, fix quality, timing, calibration, and a scene-based exit before the choice is final. The 3.2 GB bag also requires a safe storage/subsetting plan.
- **Evidence:** `data/ELIGIBILITY.md` and `data/inventory.csv`.

## 2026-09-22 — D005: pause before overriding Google Drive's large-file warning

- **Decision:** Keep `Urban_Tunnel01` provisional and pause T04 before clicking Google Drive's “Download anyway” control for the 3.2 GB ROS bag.
- **Rationale:** The official separated files verified basic formats, but the bag is still needed to inspect actual ROS topics and retain a complete initialization-to-transition replay. Google Drive cannot virus-scan the bag and presents an explicit safety warning; accepting that warning requires the user's confirmation.
- **Consequences:** T04 is `BLOCKED`, not `DONE`. The retained 42-frame LiDAR prefix, full IMU text, full published reference text, and calibration file remain under the ignored generated-data tree. No transition time is fabricated from reference gaps or estimator behavior.
- **Evidence:** `data/DEVELOPMENT_SEQUENCE.md` and `execution/handoffs/T04.md`.

## 2026-09-22 — D006: accept Urban_Tunnel01's second exit for development only

- **Decision:** Use the manually annotated second tunnel exit in GEODE `Urban_Tunnel01` as the real-recording development event. Retain a complete-duration LiDAR+IMU bag and exclude the camera topics.
- **Rationale:** Actual LiDAR scenes show a weak-geometry entry and exit independent of estimator/indicator outputs. The released RTK/INS trajectory is absent through most of the tunnel but resumes during the exit boundary and remains available for 41.54 s, allowing post-exit local-motion recovery to be evaluated without bridging the gap. Complete pre-entry sensor history and a pre-entry reference segment are available.
- **Consequences:** The event is development data and cannot enter a held-out split. Evaluation must expose the 70.816 s reference gap, reference uncertainty, manual boundary interval, and ground-vehicle platform. The full camera-containing bag was checksummed and reduced to verified byte-identical LiDAR/IMU streams to conserve storage.
- **Evidence:** `data/DEVELOPMENT_SEQUENCE.md`, `data/transition_annotations.csv`, and `execution/handoffs/T04.md`.

## 2026-09-22 — D007: freeze transform/time semantics before backend integration

- **Decision:** Canonical pose rows represent `T_parent_body`, timestamps are integer nanoseconds, quaternions are Hamilton `qx,qy,qz,qw`, and estimator/reference comparisons require an explicitly common body frame. Local motion uses 1 s primary and 3 s sensitivity windows provisionally. Accumulated error uses one pre-entry `SE(3)` anchor with scale fixed to 1 and is never re-aligned after the event or a reset.
- **Rationale:** These choices remove implementation ambiguity while keeping local motion, accumulated drift, and online health distinct. Integer time and explicit invalid reasons prevent reference gaps and missing indicator decisions from becoming apparently valid zero-valued evidence.
- **Consequences:** T06 adapters must retain raw output and declare frame conversions; T07 must reject unresolved comparison frames and crossing-reset/gap windows. The 0.20 s reference bracket, ±0.05 s pose endpoint/anchor tolerances, window durations, and single-anchor alignment are development settings subject to T11/R2 review. Recovery tolerances, sustained duration, and indicator thresholds remain unset, so no recovery/false-reassurance/delay claim is permitted yet.
- **Evidence:** `protocol/DATA_CONTRACT.md` and `protocol/METRICS.md`.

## 2026-09-23 — D008: isolate FAST-LIO2 and preserve GEODE point acquisition times

- **Decision:** Build official FAST-LIO revision `7cc4175de6f8ba2edf34bab02a42195b141027e9` in a path without spaces using RoboStack ROS Noetic, a message-only Livox compatibility package, and a narrowly scoped C++17 build patch for PCL 1.15.1. Use a Velodyne replay adapter that shifts each cloud header and point offsets by the same minimum time so absolute point acquisition times are preserved.
- **Rationale:** The host has no ROS/container runtime. RoboStack resolved in an isolated environment, while ROS-generated scripts failed when installed under the repository's space-containing path. Upstream FAST-LIO requires C++14, but current PCL requires C++17. GEODE's actual point offsets are mostly negative and FAST-LIO expects scan-start offsets; the first actual cloud passed a maximum 3.824 ns preservation check after adaptation.
- **Consequences:** The backend builds and starts, but a scientific replay requires an effective calibration direction. GEODE names the published matrix `T_IMU_LiDAR` without defining its direction in inspected primary documentation. The user has been asked whether a flagged exploratory direct use is acceptable. No pose accuracy or recovery result is claimed yet.
- **Evidence:** `experiments/README.md`, `experiments/patches/fast_lio_pcl17.patch`, `experiments/src/velodyne_time_adapter.py`, and T06 handoff.

## 2026-09-23 — D009: retain the reproduced but inaccurate FAST-LIO2 runs

- **Decision:** Use GEODE's published `T_IMU_LiDAR` numbers directly as a provisional LiDAR-to-IMU transform for two development-only replays. Preserve both runs, their exact effective configuration, pose streams, warnings, resources and manifests. Stop parameter retries after the second run; do not report recovery or estimator accuracy from them.
- **Rationale:** The user could not adjudicate the matrix convention, and its notation is consistent with FAST-LIO's requested direction, so an explicitly exploratory replay was reasonable. The full run emitted poses but diverged catastrophically. A fresh run beginning 130 seconds into the recording retained 38 seconds of pre-entry initialization and avoided numeric explosion, yet grossly under-tracked translation across the covered post-exit interval. Both process replays completed; neither establishes useful local motion quality.
- **Consequences:** T06's technical reproduction acceptance is met, while scientific suitability remains unresolved. T07 must enforce the documented common-body requirement and may emit unavailable formal errors if GEODE's reference body cannot be established. R1 must review whether to move the already planned Point-LIO candidate forward on this sequence or select a reference-verified alternative recording; no backend or dataset is silently replaced.
- **Evidence:** `experiments/README.md`, ignored `experiments/generated/runs/T06_full/manifest.json` and `T06_event_local/manifest.json`, `execution/handoffs/T06.md`.

## 2026-09-23 — D010: inspect Hilti Exp18 as a replacement development candidate

- **Decision:** Keep GEODE failures unchanged and inspect Hilti-Oxford Exp18 as a new **development-only candidate**, without accepting it as a verified recovery event or final-test sequence. The user's Acer partition holds the publisher-hash-matching bag; no raw data enter Git.
- **Rationale:** Hilti documents the reference IMU frame and publishes LiDAR calibration, removing one GEODE comparison-body uncertainty. Actual LiDAR/IMU streams and point timestamps are readable. LiDAR-only snapshots suggest a 32–36 s scene transition within the reference span. The dense reference has gaps, ends before the bag, and is derived from the mobile LiDAR against a surveyed map; the transition's geometric meaning and backend performance remain unverified.
- **Consequences:** Build a Hesai-specific time-preserving adapter and perform one retained development replay before computing formal errors or making recovery claims. R1 must judge reference independence and event suitability. Do not treat the successful download or bag parsing as a completed scientific pilot.
- **Evidence:** `data/HILTI_EXP18_INSPECTION.md`, `experiments/src/inspect_hilti_exp18.py`, and ignored LiDAR-only inspection images.

## 2026-09-23 — D011: verify Hesai time conversion before backend replay

- **Decision:** Convert Hilti's absolute float64 per-point timestamps to float32 scan-start offsets in a Velodyne-shaped cloud for the pinned FAST-LIO input path, without changing LiDAR coordinates or using reference poses. Keep this as a development adapter, not an estimator modification.
- **Rationale:** The pinned backend lacks a Hesai handler, but its Velodyne path accepts `x,y,z,intensity,ring,time` and seconds input. All 1,094 actual Exp18 clouds passed ordered-point-time, schema, duration and header-agreement checks; maximum relative-time roundoff was 0.238 microseconds. Four focused adapter fixtures and the eight prior evaluator fixtures passed.
- **Consequences:** Only the offline payload conversion is verified. The ROS wrapper, calibration interpretation and motion estimate still require a fresh, retained development replay. No numerical recovery claim follows from this adapter check.
- **Evidence:** `experiments/src/hesai_time_adapter.py`, `experiments/src/verify_hesai_adapter.py`, `experiments/tests/test_hesai_time_adapter.py`, and `data/HILTI_EXP18_INSPECTION.md`.

## 2026-09-23 — D012: retain a successful but noncanonical Hilti FAST-LIO smoke replay

- **Decision:** Preserve one 55-second Hilti Exp18 LiDAR/IMU-only FAST-LIO development replay and its poses/logs/manifests on the Acer partition. Do not promote gross distance agreement to formal 6-DoF accuracy, recovery or indicator evidence.
- **Rationale:** The built pinned backend produced 546 valid continuous poses; the ROS Hesai adapter published 551 clouds with zero rejections. Three exploratory displacement lengths were close to the dense reference, unlike GEODE's gross under-tracking. Yet frame equivalence and quaternion convention still require verification, the reference is map-registration-derived, and the smoke run did not capture complete resource/provenance fields.
- **Consequences:** The technical feasibility signal is positive. Keep the run development-only and manifest status `partial`; perform explicit frame/reference review before T07 formal error calculation. The previous GEODE failures and R1 gate remain unchanged.
- **Evidence:** `data/HILTI_EXP18_REPLAY.md`, `configs/fastlio_hilti_exp18_exploratory.yaml`, `experiments/run_hilti_exp18_smoke.sh`, and the Acer-side `runs/exp18_first55_exploratory/manifest.json`.

## 2026-09-24 — D013: withhold formal Exp18 errors pending exact body-axis provenance

- **Decision:** Treat the Exp18 `_imu.txt` file as likely TUM `timestamp xyz xyzw` and FAST-LIO's `body` output as its IMU state, but do not set the comparison-body transform `verified: true` or calculate formal 6-DoF errors until the bag's `imu_sensor_frame`, released calibration's `imu`, and `_imu.txt` axes are reconciled with the publisher's rotated robot `base` frame.
- **Rationale:** The publisher's 2022 evaluator and frame FAQ support an IMU-body reference, and the pinned backend source supports an IMU-state output. However, inspected publisher files do not explicitly prove the coordinate-axis identity of the differently named IMU frames or explain the Exp18 `_imu.txt` conversion from the robot model's `base` convention. A guessed identity or 180-degree rotation could give misleading rotation and translation errors.
- **Consequences:** T07 remains BLOCKED for real-data acceptance. Sequence/event selection, gap partitioning and reset-marker repairs can proceed independently. The first replay remains a smoke test, not recovery evidence; publisher clarification or more direct source provenance is needed before metric release.
- **Evidence:** `data/HILTI_EXP18_FRAME_AUDIT.md` and its primary-source links; read-only SHA checks of the released reference and calibration.

## 2026-09-24 — D014: resolve Exp18 frame axes from raw gyroscope, not estimator error

- **Decision:** For a future **development-only** Exp18 comparison, interpret the released `_imu.txt` quaternions as `xyzw` world-from-IMU in the same axes as the bag's IMU measurements. Do not apply the robot-model `base` rotation. D013's no-error gate remains in effect until T07 repairs and sequence-specific metadata are completed; its need for a publisher reply on axis identity is superseded by this estimator-independent diagnostic.
- **Rationale:** Across 503 sufficiently sampled turning intervals, the reference-implied body angular rate and bag gyroscope differ by 0.0104 rad/s vector RMSE with near-unit per-axis correlations. Preselected 180-degree-base, inverse-pose and `wxyz` alternatives differ by 1.8640, 0.4906 and 1.3645 rad/s respectively. The test uses neither FAST-LIO poses nor error curves and is consistent with the publisher's reference/evaluator conventions.
- **Consequences:** A publisher reply is not required to continue the development pilot. The dense reference shares LiDAR/IMU inputs with its generation process, so this check establishes frame convention, **not** independent truth or accuracy. R1 must still judge reference suitability. No formal errors, recovery labels or indicators have been generated yet.
- **Evidence:** `data/HILTI_EXP18_FRAME_AUDIT.md`, `experiments/src/audit_hilti_gyro_reference.py`, and `experiments/tests/test_hilti_frame_audit.py`.

## 2026-09-24 — D015: repair T07 boundaries and record qualified Hilti metadata

- **Decision:** Record the Exp18 identity comparison-body choice in sequence-specific metadata for **development only**, with source hash, clock, provenance and reference gaps. Require an explicit event ID/entry timestamp, source-order reference partitioning, and preserved reset/invalid rows in T07. Do not compute event-anchored errors until the tentative scene transition is frozen from LiDAR geometry alone.
- **Rationale:** The raw-gyroscope frame audit resolves the practical body-axis choice without fitting FAST-LIO to reference, while the old evaluator could silently apply the GEODE anchor, sort across source-order coverage boundaries, or drop reset rows. The actual Hilti reference contains 789 rows, 20 coverage segments and 19 excluded gaps under the provisional 0.20 s rule.
- **Consequences:** The evaluator can be run with development-only Hilti metadata after a valid scene event is chosen, but its `verified` flag applies to the comparison-body convention, not reference independence or trajectory accuracy. T07 remains BLOCKED on real-data acceptance; no recovery label, error stream or final-test result was produced in this step.
- **Evidence:** `data/hilti_exp18_reference_metadata.json`, `experiments/src/trajectory_eval.py`, 21 passing experiment tests, and `execution/handoffs/T07.md`.

## 2026-09-24 — D016: keep Exp18 transition tentative after scene-only range audit

- **Decision:** Treat about 31.6–33.1 s as a confirmed near/confined-to-farther-structure scene change, but do not freeze it as a weak-to-rich localization-recovery event yet.
- **Rationale:** LiDAR-only range fractions and snapshots change sharply without examining estimator, indicator or error curves. Range does not measure whether 6-DoF scan registration is underconstrained before the transition or sufficiently constrained after it.
- **Consequences:** Perform a predeclared LiDAR-only structural-diversity check, then freeze or reject the event before running event-anchored T07 errors. T07 remains BLOCKED and no recovery claim is authorized.
- **Evidence:** `data/HILTI_EXP18_SCENE_GATE.md` and `experiments/src/audit_hilti_scene_ranges.py`.

## 2026-09-24 — D017: freeze an Exp18 scene exit, not a recovery label

- **Decision:** Use the LiDAR-only, prespecified structural audit to freeze an **exit-only candidate** interval 31.6–33.6 s relative to the first LiDAR header, nominal 32.6 s. Do not call it a degeneracy entry or a recovered-odometry time.
- **Rationale:** A fixed 10-scan before/after comparison increased the minimum direction-information eigenvalue after the transition for all six predeclared 6-DoF cap/rotation-scale combinations. This supports an environmental weak-to-richer-constraint interpretation without choosing the event from estimator error or indicator peaks. The scan-local proxy lacks FAST-LIO's map correspondences, weighting and IMU prior, and the recording starts inside the apparently confined section.
- **Consequences:** T07 may calculate event-anchored **development** errors. Its alignment target is explicitly pre-exit, not the originally planned pre-entry drift anchor. The event itself does not prove estimator recovery, and R1 still needs suitable independent reference coverage.
- **Evidence:** `protocol/HILTI_SCENE_STRUCTURE.md`, `data/hilti_exp18_scene_structure.csv`, `data/HILTI_EXP18_EVENT.md`, and tested `experiments/src/audit_hilti_scene_structure.py`.

## 2026-09-24 — D018: close T07 software acceptance but reject Hilti-only recovery inference

- **Decision:** Mark T07 DONE under its stated acceptance of tested offline metrics plus audited valid/invalid real-development streams. Do **not** mark T09 or R1 complete or infer sustained recovery from Exp18. Screen small reference/metadata files before another large dataset download.
- **Rationale:** The 55-s Hilti replay yields 1,092 provisional local-error rows, with 422/546 valid 1-s starts and 344/546 valid 3-s starts over the full replay. In the matched post-exit interval, only 13/56 1-s and 0/56 3-s windows are reference-valid. The publisher reference also partly uses LiDAR map registration, so it is not an independent final truth. Twenty-four experiment tests pass. Preliminary alternative screening finds multiple attractive scenes with position-only or discontinuous truth.
- **Consequences:** Hilti remains a qualified development pilot and possible failure/availability figure. A publishable transition-reliability claim needs an independently referenced, sufficiently covered real event or an explicitly narrowed simulation-primary question reviewed at R1. No final test or threshold selection occurred.
- **Evidence:** `evidence/HILTI_EXP18_T07_PILOT.md`, `data/ALTERNATIVE_REFERENCE_AUDIT.md`, `execution/handoffs/T07.md` and current status ledger.

## 2026-09-24 — D019: derive the conventional indicator from pinned FAST-LIO correspondences

- **Decision:** T08 will begin with the first six point-to-plane measurement-Jacobian columns in pinned FAST-LIO's `h_share_model`, after its own accepted-correspondence selection. A normalized measurement-only information matrix with declared rotational lever scales 1, 3 and 5 m is the conventional baseline. Keep the independent Hilti raw-scan structural proxy separate. T08 remains RUNNING until actual backend export, pose-parity and development replay evidence exist.
- **Rationale:** The pinned backend provides the exact accepted map planes, points and translation/rotation Jacobian at the relevant online stage. Their unweighted outer-product matrix is auditable; a raw-scan proxy lacks correspondences and would mislabel an unrelated quantity as the estimator's health. Scale sensitivity and accepted-point count prevent an arbitrary single eigenvalue from appearing self-explanatory. Four independent analytic/geometry fixtures pass; they do not prove replay integration.
- **Consequences:** No threshold, recovery decision, X-ICP reproduction or paper result is claimed. The export must be optional and checked against an unchanged pose stream. The full experiment test suite now passes 28/28.
- **Evidence:** `protocol/FASTLIO_INFORMATION_DIAGNOSTIC.md`, `experiments/src/fastlio_information.py`, and `experiments/tests/test_fastlio_information.py`.

## 2026-09-24 — D020: retain preliminary T08 export, stop before claiming acceptance

- **Decision:** Version the optional diagnostic patch and replay script, preserve the short export-on/off pose-parity result, and leave T08 RUNNING. The final patch's full 55-second replay was interrupted at the user's request and its partial output is not evidence. Stop the running process before the GitHub push.
- **Rationale:** The preliminary patch compiled; 12-second on/off pose CSVs were byte-identical, and a prior 55-second export produced valid rows but omitted startup-unavailable rows. The final patch adds explicit startup reasons and compiles, but has not completed the full replay/provenance audit. Treating the earlier output as final would hide a known coverage defect.
- **Consequences:** No indicator threshold, recovery comparison or T08 completion claim. The [T08 in-progress handoff](handoffs/T08.md) specifies the clean next run and checks. No large raw or partial generated data enter Git.
- **Evidence:** `experiments/patches/fast_lio_health_diagnostic.patch`, `experiments/run_hilti_health_smoke.sh`, and `protocol/FASTLIO_INFORMATION_DIAGNOSTIC.md`.

## 2026-09-26 — D021: close T08 software checks; preserve the research gate

- **Decision:** Accept T08 after fresh build, export audit and full on/off parity. Fix replay shutdown clock draining, not estimator behavior. Account for all 551 delivered scans: 547 valid, three startup-unavailable, one cutoff-incomplete IMU scan.
- **Evidence:** `evidence/T08_FINAL_PATCH_AUDIT.md`; corrected motion streams are byte-identical; scan point-time ends and the last IMU timestamp verify the cutoff exclusion.
- **Consequences:** T09 has a reviewed illustrative timeline, manifest and report but remains BLOCKED against the original independent recovery-reference criterion. The matched post-exit availability is still 13/56 and 0/56. No threshold, recovery label, final-test result or novelty claim is assigned. TIERS Indoor05 was rejected as independent truth because its published reference is FAST-LIO-derived. A simulation-primary amendment was proposed to the user, not silently adopted.

## 2026-09-26 — D022: approved simulation-primary evidence, feasibility not publication

- **Authority:** User answered “yes proceed” to the explicit simulation-primary proposal. The question remains LiDAR-health reliability against post-degeneracy local motion; real recordings become supporting illustrations.
- **Decision:** Record `SCOPE_AMENDMENT_SIMULATION.md`; permit T12 feasibility bootstrap before R1 to remove the dependency cycle, not full protocol or final tests.
- **Evidence:** Two v2 ray-cast LiDAR/IMU runs completed with exact isolated truth; all 320 scan groups per run accounted; 6,421 paired IMU messages identical. Shared v1 RNG stream was repaired before paired comparison; v1 attempts retained.
- **Review:** R1 returns REVISE. Full-motion/visibility/horizon assumptions and recent-paper overlap need repairs. Broad recovery/detection novelty is unsupported. No R2/R3 gate or recovery threshold is frozen.

## 2026-09-26 — D023: retain the repaired 40-second simulator as development evidence

- **Decision:** Replace the v2 feasibility input only for the new v3 pilot. Preserve all v1/v2 attempts. Close the room/corridor wall shoulders outside each doorway, use analytic smooth 3D motion and matched seeded IMU bias/noise, and extend each paired run to 40 s. Keep v3 explicitly development-only.
- **Rationale:** R1 identified open shoulders, yaw-only motion, zero bias and a short post-exit interval as simulator weaknesses. Geometric ray tests now cover both doorways, both shoulders and jamb edges. Independent finite differences validate translational acceleration and body angular rates. The 40 s interval supplies 15.75 s after layout exit. Pairing the complete IMU stream isolates the scene-feature change.
- **Evidence:** `evidence/SIMULATION_MOTION_V3.md`, `evidence/simulation_motion_v3_manifest.json`, `protocol/SIMULATION.md`, ten simulator tests and 40 passed/1 skipped in the full suite. Each replay accounts for 400 scans and 397 valid health groups; paired IMU message hashes match; each evaluator has 754/794 valid windows and zero reference gaps.
- **Consequences:** One synthetic scene pair and seed show an illustrative increase of local error inside the corridor and lower error after exit, with remaining fixed-alignment drift. This does not establish recovery timing, generalization, calibration or publication novelty. Bias levels are declared stress settings, not tied to a physical unit. R1 remains REVISE pending full literature overlap and independent review; T10/T11/full T12/R2 remain gated.

## 2026-09-26 — D024: pass R1 feasibility only after the full overlap refresh

- **Decision:** Supersede the first R1 REVISE disposition with **PASS for protocol design only** after a fresh GPT-6 evidence audit. Keep the first review and its rationale in the review history; do not treat this as a novelty, publication or generalization verdict.
- **Rationale:** The full available ICA article and official code README were audited, including its dynamic transition studies, RTE/ATE traces and definition of “recovery feasible”. DCReg v3 and its official four-page supplement were audited; they report temporal direction masks, over/under-detection, detection ratios, per-pair registration recall and trajectory/map error, but the inspected sources do not define a sustained post-exit local-motion label or causal detection-delay outcome. ALIVE-LIO explicitly notes slow recovery and missed corrective updates. The v3 pair supplies one measurable truth-isolated end-to-end transition.
- **Evidence:** `reviews/R1_FEASIBILITY.md`, `literature/INFORMED_CONSTRAINED_ALIGNED.md`, `literature/RECOVERY_OVERLAP_UPDATE.md`, v3 report/manifest and current audited outputs. The ICA supplementary video folder was not readable in its public viewer; this limitation is recorded and no numerical claim depends on it.
- **Consequences:** A narrow transition-level indicator-versus-sustained-local-motion study is feasible enough to specify. Generic degeneracy detection/reliability, RTE/ATE curves and local/global error separation are excluded as claimed novelties. Proceed to T10/T11/full T12 and R2; no batch or final-test evaluation before R2 PASS. Publication novelty remains uncertain.

## 2026-09-26 — D025: use DCReg's detector module as the published comparator

- **Decision:** T10 specifies DCReg's published Schur-condition directional detection module as the primary comparator to FAST-LIO's conventional measurement-information minimum eigenvalue. The comparator operates on the same accepted FAST-LIO point-to-plane correspondences; it does not replace FAST-LIO or run DCReg's PCG mitigation. Keep the published threshold `kappa_th=10` fixed. The implementation must be labelled a detector adaptation, not a complete DCReg reproduction.
- **Rationale:** DCReg is the closest recent published work for temporal degeneracy detection and explicit over/under-detection; its full text and supplement are now audited. It has an official detector implementation and direction-level output. X-ICP and SuperLoc remain close related work, but X-ICP's constrained registration changes the optimizer and SuperLoc couples confidence to a prior-assisted factor graph, making either less direct as the single indicator-stage comparator for this FAST-LIO study.
- **Evidence:** `protocol/INDICATORS.md`; DCReg Sections 4.2–4.4, 7.1.2–7.1.3 and 7.4.1–7.4.2; official implementation revision `8ce8451b15491a4bbe17cf85ab02a8bed6696861`; official supplementary tables and metrics in `literature/RECOVERY_OVERLAP_UPDATE.md`.
- **Consequences:** T10 is DONE as a specification. R2 must approve the shared-correspondence adaptation, basis mapping and analytic checks before T13 implements it. No method code, threshold fit or new result is claimed here.

## 2026-09-26 — D026: define a development recovery label and reserve layout splits

- **Decision:** Propose recovery as three consecutive non-overlapping 1 s relative-motion windows with both translation error ≤0.20 m and rotation error ≤5°; use 3 s error-rate windows as sensitivity. Define false-healthy, delay, availability, right-censoring and development-only threshold selection in `protocol/METRICS.md`. Reserve 32 randomized straight-corridor development layouts and at least 48 held-out layouts over four length/width strata; allow expansion to 80 using only the development precision rule.
- **Rationale:** The 0.20 m/5° cutoffs are adapted from DCReg's published registration-pair recall definition; they are not an aviation safety limit. The 4-seed v3 pilot has same-layout paired translation-difference SD 0.162 m; a 0.10 m confidence half-width implies 11 event pairs before rounding, while 48 held-out events target about ±14 percentage points worst-case for an event proportion. The 32 layout-dev set must recompute that variance before determining the final test count.
- **Evidence:** `evidence/SIMULATION_SEED_SENSITIVITY.md`, its manifest, `protocol/METRICS.md` and `data/SPLITS.csv`.
- **Consequences:** These are proposed protocol values, not frozen until R2. All v1/v2/v3 and seed-11–13 runs are development data. No held-out layouts or thresholds have been exposed. If the dev-based count exceeds 80, return to R2; do not trim or tune using held-out results.

## 2026-09-26 — D027: smoke-test a seeded randomized geometry layout

- **Decision:** Add an opt-in `randomized_straight_dev` layout family while preserving `fixed_v3` behavior. Randomized layouts use a seed-drawn corridor length/width, the same analytic trajectory, paired feature baffles and the same per-point LiDAR/IMU model. Keep the development seed range separate from reserved held-out seeds.
- **Rationale:** R1 passed only for protocol design; T12 needs executable evidence for the planned randomized layout model. A scene-only ray screen evaluates geometry before estimator outputs to avoid selecting layouts based on errors or health scores.
- **Evidence:** `experiments/src/simulate_lidar.py`, `write_simulation_bag.py`, `audit_simulation_scene.py`, 12 simulator tests, `evidence/SIMULATION_RANDOM_LAYOUT_SMOKE.md` and its manifest. Seed-14 corridor/control bags contain 600 scans/12,021 IMUs, share byte-identical IMU, pass the predeclared geometry screen, and both FAST-LIO runs have 597 poses, 1,154/1,194 valid evaluation rows and zero reference gaps. All 32 development geometry seeds 14–45 pass the scene-only screen; only seed 14 has bag/replay outputs.
- **Consequences:** T12 is DONE for protocol/feasibility. Held-out parameter strata remain unimplemented and ungenerated. The Acer partition has adequate free space but is currently mounted read-only; T14 must verify a writable target or use pairwise scratch bags and retain deterministic hashes before the large run budget is approved at R2.

## 2026-09-26 — D028: approve the R2 recovery deadline and formal route context

- **Authority:** The user approved both proposed protocol defaults on 26 September 2026.
- **Decision:** A recovery triple counts only when all three passing non-overlapping 1 s windows finish by `t_exit+20 s`; the actual associated third-window endpoint is the confirmation time. T14's formal route starts at x=-6 m, enters at 10.5 s and uses `t_exit=3+(6+L)/0.8 s` to provide at least 10 s of pre-entry context. The prior T12 seed-14 run remains feasibility-only.
- **Rationale:** A triple that finishes after the deadline uses motion outside the declared observation horizon. The existing x=-5 m smoke has only 9.25 s of pre-entry context and cannot satisfy the final protocol's 10 s minimum.
- **Consequences:** T14 must implement the formal route, regenerate all 32 development layouts under new run IDs, and rerun the geometry-only screen before LIO. These definitions do not by themselves pass R2; no batch or held-out run is authorized yet.

## 2026-09-26 — D029: verify deterministic scratch regeneration and artifact hashes

- **Decision:** Keep raw sensor bags out of Git and use one paired event at a time in `/tmp` scratch, retaining compact manifests/output hashes and failed inputs until diagnosed. Correct the randomized-layout manifest's geometry-screen filename to the checked-in artifact.
- **Evidence:** Current generator code regenerated the seed-10 fixed-v3 corridor/control pair and seed-14 randomized corridor/control pair. All four sensor-bag hashes and all four reference hashes matched their retained input manifests exactly. The retained v3/randomized input, reference, pose, health and evaluation hashes also rechecked. The four-seed manifest preserves the source hashes recorded at original generation and separately records the seed-10 current-code reproduction; this does not claim a current-code replay of seeds 11–13.
- **Resource check:** `/tmp` had about 7.0 GB free for a 162 MB paired 60 s input; the workspace had 1.8 GB free; Acer remained mounted read-only. Prior 60 s run outputs were about 704 KB each. T14 must check space before each pair and stop if projected output storage is insufficient; it need not remount Acer.
- **Consequences:** The existing 13–18 GB all-input-retained estimate is not the required scratch capacity. The sequential replay-time estimate remains provisional and must be measured during T14. No raw data were deleted or copied to the Acer partition in this check.

## 2026-09-26 — D030: accept R2 protocol content after independent review

- **Decision:** Record the final independent GPT-6 audit as **PASS for R2 protocol content only** after two earlier REVISE rounds. The accepted content includes the shared nearest-pose time-grid rule, alarm transition semantics, run-failure/availability denominators, development-only threshold rule, fixed-stratum uncertainty procedure, DCReg numerical boundaries, formal route and scratch/repeat plan.
- **Evidence:** [R2 protocol review](../reviews/R2_PROTOCOL.md) and T10–T12 protocol artifacts. The reviewer inspected the current content at the time of its report and requested only completion of an editorially truncated sentence; that sentence is now complete. The full governing-file checksums are being recorded in [FREEZE.md](../protocol/FREEZE.md).
- **Consequences:** No batch or held-out work is authorized until the dated freeze bundle is complete and re-read. T13/T14/T15/T16 and R3 remain outstanding. This PASS is not an implementation, novelty, publication or final-result verdict.

## 2026-09-26 — D031: complete the R2 hash read-back

- **Decision:** Close R2 as **PASS for protocol content and freeze integrity only** after rereading `protocol/FREEZE.md` and verifying all 51 listed SHA-256 values against current files.
- **Evidence:** `protocol/FREEZE.md`; the read-back command found 51/51 matches. The experiment suite remains 42 passed, one SciPy-dependent skip; compilation, JSON, shell syntax and whitespace checks pass.
- **Consequences:** T13/T14/T15/T16 development work is now eligible under the frozen rules. R2 does not authorize held-out generation or final evaluation; those remain behind R3. No code has been committed or pushed in this step.

## 2026-09-27 — D032: accept T15 Point-LIO smoke with a pose-only compatibility claim

- **Decision:** Close T15 as one pinned Point-LIO development smoke plus a byte-identical repeated pose replay. Accept only the common pose-output, timing and startup-reset checks. Do not claim Point-LIO parity for FAST-LIO `G_3m` or the DCReg Schur mask.
- **Evidence:** `evidence/T15_POINTLIO_SMOKE.md`, `evidence/t15_point_lio_smoke_manifest.json`, Point-LIO commit `4b86a469eb5572e70ed575af25b5f15dd06e8e3c`, 597 valid poses, 1,154 valid local-motion rows, no reference gaps; V2/V3 pose CSV hash match. One initial private-ROS-namespace setup failure and its GDB trace are retained.
- **Consequences:** The smoke remains development-only and is not backend replication or a recovery finding. The `camera_init/body` pose frame was checked against the simulator configuration, but no equivalent online Point-LIO information stream was exported. The build workspace is session-local; Acer remained read-only.

## 2026-09-27 — D033: complete frozen-rule T16 development analysis without opening held-out data

- **Decision:** Apply the R2 integer-window recovery labels and development-only FAST-LIO threshold rule to the 64 completed T14 primary runs. Do not use repeats as independent geometry events or include Point-LIO in the FAST-LIO threshold fit. Report a candidate threshold, not a final frozen value.
- **Evidence:** `evidence/DEVELOPMENT_REPORT.md` and `evidence/t16_development_analysis_manifest.json`; 768/768 primary output files re-hash-verified. All 32 corridor truth labels are eligible/recovered; one post-recovery relapse. Candidate `G_3m >= 166.16366016039856` gives 13/32 detections and 1/31 conditional false-healthy events. DCReg remains fixed and gives 29/32 detections, 0/31 initial false-healthy events, and one post-relapse false-healthy event. The interior sample standard deviation is 0.2494728851 m, yielding `n_test=48` (12 in each stratum). The held-out plan is `evidence/FINAL_HELDOUT_PLAN.json` and says no geometry was generated or screened.
- **Consequences:** The FAST-LIO threshold is optimistic because selection and scoring share development events; R3 must adjudicate T14's seed-14 repeat reconciliation, review the new held-out runner, and lock the exact threshold before any screen or replay. Acer is read-only; the final runner uses sequential 154 MiB scratch pairs and checks at least 1 GiB free.

## 2026-09-27 — D034: record T16 documentation hashes without changing R2 methods

- **Decision:** Refresh the root README's public checkpoint and append T15/T16 decisions to this log. Update only their entries in the R2 checksum table; preserve the original hashes and checksum-bundle identity here. No method, threshold rule, sample split, simulator input or held-out result changed.
- **Evidence:** The pre-edit R2 bundle hash was `34e9522beb259fb280ff662f3f4dfab9e3a152cf88ef57f04bd9eb257185af6d`. The original README and decision-log hashes were `bb9e4d80734e39b4db27de9cdae0e2636781de9c12580fada90bd6e417674b53` and `dabfd3c58c858f7fe8751a162e6c3e811fe63aea6ffb9b50c61eb1a440e183ba`. The updated README hash is `ab18c31907ece6b8320847ed7dbf92225dd04bf93546dfb7343de1034201d38f`; the current append-only decision-log hash is recorded in `protocol/FREEZE.md` after this entry.
- **Consequences:** The amended checksum table still has 51 entries; 49 governing artifacts retain their original hashes. R2 remains PASS for protocol content only, not R3. R3 must review the updated public status and task log along with the underlying T13–T16 evidence. No held-out geometry or result was opened.

## 2026-09-27 — D035: expand the public README and record current verification honestly

- **Decision:** Expand the root README into a plain-language guide to the complete task roadmap, protocol, development results, figures, verification, limits and remaining gates. Record the latest full-suite recheck as 91 discovered tests: 88 passed, two errored because the R3-required repeat-audit report files are missing, and one optional SciPy test was skipped. Do not describe the suite as passing or the research as publication-ready.
- **Rationale:** Readers and the professor need one accurate starting point that distinguishes development results from an untouched final test. The older README mixed an early Hilti pilot with the later simulation analysis and stale test counts.
- **Evidence:** Root `README.md`, [current status](STATUS.md), [R3 review](../reviews/R3_IMPLEMENTATION.md) and current test output. Before this amendment, README SHA-256 was `ab18c31907ece6b8320847ed7dbf92225dd04bf93546dfb7343de1034201d38f`, decision-log SHA-256 was `d7fb1c9d3eabeb1a8ee4e5337ae9c0a0954e5af76331e0d4f3aee98f5086db96`, and freeze-file SHA-256 was `8b6ef5fb83ff459f078bb89c9f0dc7b1708e44d23dfb586598d36ba59198031f`. The updated README SHA-256 is `f05f5aecdf06f27ead7fedf75d73d77e9a67f673bf022f1ab8d92086effed3cc`; the new decision-log hash is recorded in `protocol/FREEZE.md` after this entry. The README links the existing figure provenance and evidence reports instead of duplicating their methods.
- **Consequences:** This is a documentation and status amendment only. It does not alter protocol methods, thresholds, splits, analysis code, simulator inputs or results, and does not authorize held-out screening. The README and decision-log hashes are updated in the R2 checksum table; all other listed artifact hashes remain unchanged.
