# Final Held-Out Geometry Screening Report — 12 October 2026

**Status:** `STOP_RETURN_TO_R2_INSUFFICIENT_ELIGIBLE_LAYOUTS`  
**Gate:** Live R3 Implementation Gate PASS; Geometry Screening FAILED  
**Output Artifact:** `/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/final_heldout_v1/scene_screen.json` (SHA-256: `3b4ec4b38d77a5a81ca04df489bc83be608fa8fa038d1ee72856f6ba3a84b0f0`)

---

## 1. Readiness Verification Summary

Read-only gate verification executed under `/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python` (Python 3.12.14, NumPy 2.5.3):
- **Gate Status:** PASS (`r3_evaluation_workflow.require_r3_pass` returned clean gate dictionary).
- **R3 Inventory:** Exactly 179 entries verified, including 53 / 53 R2 frozen artifacts.
- **Locked Thresholds:**
  - FAST-LIO: `166.16366016039856`
  - Point-LIO: `123.80876977779258`
- **FAST-LIO Backend:**
  - Binary SHA-256: `4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792`
  - Upstream Commit: `7cc4175de6f8ba2edf34bab02a42195b141027e9`
  - Worktree Diff SHA-256: `1397219a8765c2bc8c49adaf7e94dcc1e6006788acac06467e28e660876e51a0`
  - Launched Binary Path: `/tmp/fastlio-t13.XBDWGy/ws/devel/lib/fast_lio/fastlio_mapping` (verified via `rosrun`)
- **Point-LIO Backend:**
  - Binary SHA-256: `80516da9cafba98262d56c17cc26ec4da76e214049d3af7776248b4c3a342b17`
  - Upstream Commit: `4b86a469eb5572e70ed575af25b5f15dd06e8e3c`
  - Glog Overlay SHA-256: `f6493cebf3d627baf4a98fdcaa5a2c741144dd77a19a064fd500e50f5afa72ea`
- **Storage Headroom:** 167.8 GiB available on Acer; 6.9 GiB available on `/tmp`.

---

## 2. Geometry Screening Execution

### Reproduction Command
```bash
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python \
  research_paper/experiments/src/r3_evaluation_workflow.py screen \
  --plan research_paper/evidence/FINAL_HELDOUT_PLAN_20261010.json \
  --r3-review research_paper/reviews/R3_IMPLEMENTATION.md \
  --implementation-freeze research_paper/protocol/IMPLEMENTATION_FREEZE.md \
  --output /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/final_heldout_v1/scene_screen.json
```

### Screening Rules (`audit_simulation_scene.py` / `heldout_simulation.py`)
To be eligible, a parameterized geometry layout must satisfy:
1. `degraded["axial_normal_fraction"] <= 0.10` (weak geometry at corridor midpoint)
2. `control["axial_normal_fraction"] >= 0.15` (rich geometry at control midpoint)
3. `post["axial_normal_fraction"] >= 0.20` (recovery geometry at exit + 5.0 s)

Target: exactly **12 eligible geometry pairs per stratum** (48 pairs total). Candidates are evaluated in strictly ascending order within their reserved seed intervals.

---

## 3. Screening Results by Stratum

| Stratum | Reserved Seeds | Target | Examined | Eligible Found | Deficit | Outcome |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **TEST_SHORT_NARROW** | 100–119 | 12 | 12 | **12** | 0 | **PASS** |
| **TEST_SHORT_WIDE** | 120–139 | 12 | 20 (all) | **10** | 2 | **EXHAUSTED** |
| **TEST_LONG_NARROW** | 140–159 | 12 | 20 (all) | **0** | 12 | **FAILED** |
| **TEST_LONG_WIDE** | 160–179 | 12 | 16 | **12** | 0 | **PASS** |

### Selected Seeds
- `TEST_SHORT_NARROW`: `[100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]` (12 / 12)
- `TEST_SHORT_WIDE`: `[120, 124, 126, 128, 132, 133, 134, 136, 137, 139]` (10 / 20)
- `TEST_LONG_NARROW`: `[]` (0 / 20)
- `TEST_LONG_WIDE`: `[160, 161, 162, 163, 164, 166, 167, 168, 170, 172, 173, 175]` (12 / 16)

---

## 4. Rejection Diagnosis

1. **`TEST_LONG_NARROW` (Seeds 140–159):**
   - **Diagnosis:** All 20 candidate seeds failed the control midpoint threshold (`control["axial_normal_fraction"] >= 0.15`).
   - In `TEST_LONG_NARROW`, corridor length is 15.0–18.0 m while half-width is 1.3–1.5 m. The 4 feature baffles are spaced at `x = length * index / 5.0` (separated by 3.0–3.6 m along x). At corridor midpoint ($x = \text{length}/2$), the narrow baffle width (`0.35 * half_width = 0.455–0.525 m`) and wide baffle spacing result in an axial normal ray return fraction of only **0.1120–0.1372**, never reaching the 0.15 threshold.
   - De-graded corridor returns (0.0214–0.0276) and post-exit returns (0.2531–0.2898) passed without issue.

2. **`TEST_SHORT_WIDE` (Seeds 120–139):**
   - **Diagnosis:** 10 of 20 candidate seeds failed:
     - 5 seeds failed `degraded <= 0.10` (e.g. seeds 122, 125, 127, 131, 135 had degraded fractions 0.1002–0.1059 due to wide doorways admitting ambient wall returns).
     - 3 seeds failed `post >= 0.20` (seeds 121, 129 had post fractions 0.1924, 0.1943).
     - 2 seeds failed both (seeds 123, 138).
   - Only 10 seeds met all three criteria before the reserved seed pool (120–139) was exhausted.

---

## 5. Protocol Requirement & Boundary Enforcement

Under `FINAL_EVALUATION_HANDOFF.md` (lines 100–103), `final_evaluation_runner.py` (lines 262, 305, 1275–1276), and the non-negotiable protocol rules:
- **Rule:** *"If any stratum cannot provide 12 eligible layouts, stop and return to R2; do not borrow seeds from another stratum or inspect any LIO result to choose layouts."*
- **Execution Boundary:** Both `final_evaluation_runner.py` and `run_pointlio_final_replication.py` require `screen.get("status") == "SCENE_SCREEN_PASS"`. When screening returns `STOP_RETURN_TO_R2_INSUFFICIENT_ELIGIBLE_LAYOUTS`, execution halts with exit code 2.
- **Integrity Preserved:** No estimator replay was attempted on invalid geometry, no thresholds were relaxed, and no seed bounds were altered.

## 6. Later provenance reconciliation and repair checkpoint

The digest printed above is retained as originally reported. The current external screen bytes hash to `6613844123abf75303e65872e9ea143042a4fb212d00f06618a4779013cc96f7`, not that digest. The discrepancy is unresolved: original bytes matching the reported digest are unavailable. A [current byte-preserved snapshot](../../evidence/failed_geometry_screen_snapshot_20261012.json) and [receipt](../../evidence/screening_provenance_reconciliation_20261012.json) record the actual inspected version. Its embedded identities match the original live freeze and its counts match this report. This addendum does not retroactively verify the previously reported digest.

A separate [geometry repair checkpoint](../GEOMETRY_REPAIR_20261012.md) implements and tests a development-only bounded-spacing control candidate and proposes fresh larger pools. It preserves this failed screen, the original source, and the original freeze. Revised final execution still requires a new R2 amendment and R3 acceptance.
