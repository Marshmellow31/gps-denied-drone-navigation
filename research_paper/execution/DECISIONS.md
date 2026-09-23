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
