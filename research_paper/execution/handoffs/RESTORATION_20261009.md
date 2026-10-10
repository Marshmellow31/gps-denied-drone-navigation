# Research restoration and acceptance checkpoint

Date: 9 October 2026. Status: **DONE for the bounded restoration/one-seed
acceptance stage**. Full primary evidence recovery, Point-LIO development
replication, R3 and manuscript completion remain open. No held-out input was
generated, screened or inspected; no operating threshold was fitted.

## Verified outcome

- Restored 262 tracked working files and Git metadata at revision
  `5583b9edbb57a6deefd1f1b00f2927aea4e924b9`, preserving existing ignored files.
- Original R2 freeze bundle: 53/53 recorded hashes match. Governing methods,
  splits and decision log were not changed.
- Independent Point-LIO one-seed acceptance: PASS. Reviewer checked raw input,
  native/repository source, executable/configuration/output hashes, all 600
  frames, 181,903 groups, 222,498 Jacobian rows and 597 byte-identical poses.
  The isolated runtime exactly re-exported the preserved indicator CSV.
  All 40 focused tests passed including the compiled native reset fixture.
- Rebuilt all 64 development inputs in fresh Acer storage. All 192 recording,
  reference and reference-metadata hashes match the saved T16 identities.
  All 32 corridor/control IMU and stream-coverage audits pass. New runtime
  manifests remain new; missing historical runtime manifests were not invented.
- Recovered the exact historical FAST-LIO executable by rebuilding at the
  original path. Its SHA-256 is
  `4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792`.
  The rebuilt source diff and upstream/submodule identities also match.
- Fresh historical-binary seed-14 replay: 600 diagnostic groups, 597 poses,
  1,154/1,194 valid local windows and zero reference gaps. Poses, health,
  Hessian and DCReg CSVs reproduce preserved native R3 bytes exactly.
  Evaluation fields reproduce exactly apart from the explicit new run/event IDs.
- Full isolated suite: 167 executed, 166 passed, one optional SciPy scene
  audit skipped, no failures. Shell whitespace checks and helper compilation
  checks pass. The new compact backend-reference fallback and native replay
  received independent bounded acceptance.

## Preserved failures and limitations

The historical primary T14 cohort is incomplete locally: 67/320 checked
manifest/key-stream artifacts match; 253 are missing and no run has its complete
checked set. This audit covers the manifest plus four key streams per primary
run, not every file ever generated. Past task acceptance and numerical reports
remain historical evidence, not proof that those raw outputs are available now.

The moved Acer FAST-LIO binaries did not match the expected executable. Two
fresh same-input runs were byte-identical to each other but differed substantially
from preserved R3 outputs (up to 1.6027 m in x). Relinking retained objects did
not recover historical executable bytes. These attempts are preserved; the
precise cause of moved-build behaviour has not been established. The original-
path rebuild did recover the original binary and reproduced the old outputs.

Attempt A1 failed because the legacy replay wrapper starts roscore at port
11311 while the requested ROS master used a different port. The diagnosed
failure remains recorded. A2/A3 used the idle loopback default port and completed
with moved-build outputs. A4 used the recovered original executable and exactly
reproduced the historical development example.

No complete primary recovery batch, Point-LIO 32-pair development batch,
replication threshold, replication freeze, implementation freeze or final-test
result exists at this checkpoint. No claim of publication readiness follows.
All changes are local; no commit or push was performed.

## Evidence and durable locations

- [Independent one-seed review](../../reviews/POINTLIO_ONE_SEED_ACCEPTANCE_20261009.md)
- [Independent restoration review](../../reviews/RESTORATION_RECOVERY_REVIEW_20261009.md)
- [Artifact loss inventory](../../evidence/restoration_artifact_audit_20261009.json)
- [Input regeneration and exact hashes](../../evidence/development_input_restoration_20261009.json)
- [32 paired sensor audits](../../evidence/restored_development_pair_audit_20261009.json)
- [Exact build identity and loaded-library hashes](../../evidence/fastlio_historical_build_restoration_20261009.json)
- [Exact native replay comparison](../../evidence/fastlio_historical_binary_replay_20261009.json)
- [Passing full suite log](../../evidence/restored_test_run_20261009.log)
- [Earlier failing full suite log](../../evidence/restoration_test_run_20261009.log)

Raw new inputs and all native attempts are under
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/restoration_20261009/`.
The recovered executable is backed up there under
`historical_fastlio_binary/fastlio_mapping`; its bytes were verified after copying.
The active workspace `/tmp/fastlio-t13.XBDWGy/ws` is session-local. Do not
assume it survives reboot. Rebuild at that exact path to reproduce the recorded
executable, rather than using the differing older Acer workspace binaries.

## Successful restoration recipe

The original `restore_fastlio_workspace.sh` recipe was followed, with the valid
preserved upstream Git source used instead of the partial ignored Linux source
tree. Clone its clean upstream revision and submodule into the exact original
workspace:

```bash
git clone --no-hardlinks --recurse-submodules \
  /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/fastlio-t13.XBDWGy/ws/src/fast_lio \
  /tmp/fastlio-t13.XBDWGy/ws/src/fast_lio
```

Apply the four repository patches listed in `restore_fastlio_workspace.sh`
to that clean source. Require tracked source diff SHA-256
`1397219a8765c2bc8c49adaf7e94dcc1e6006788acac06467e28e660876e51a0`.
Link the restored repository's `experiments/ros/livox_ros_driver` into workspace
`src/livox_ros_driver`. Activate the existing Acer `ros_env` and execute:

```bash
catkin config --workspace /tmp/fastlio-t13.XBDWGy/ws --cmake-args \
  -DCMAKE_POLICY_VERSION_MINIMUM=3.5 -DCMAKE_BUILD_TYPE=Release
catkin build --workspace /tmp/fastlio-t13.XBDWGy/ws livox_ros_driver -j 1 --no-status
catkin build --workspace /tmp/fastlio-t13.XBDWGy/ws fast_lio --no-deps --no-status \
  --make-args fast_lio_generate_messages
catkin build --workspace /tmp/fastlio-t13.XBDWGy/ws -j 1 --no-status
```

The full build log and exact compile/link/object/library identities are preserved
in the linked build report. Native commands and exit codes are in each new
attempt manifest. All replays used only the known development seed 14.

The backend-only fallback fixture was extracted from the independently
hash-verified surviving seed-31 manifest. It does not contain output/status
claims; its SHA is pinned in the preflight code and in the required R3 inventory.
This repairs a missing-file dependency without passing the scientific data gate.

## Next eligible work and storage

Recover the full 64 primary development runs and prescribed repeats in fresh
folders with durable lifecycle manifests, using the exact restored binary and
192 verified input identities. Reconcile all surviving old outputs, reapply the
unchanged frozen analysis/threshold rule, and report differences honestly.
Complete the separately eligible 32 Point-LIO development pairs with its own
poses and threshold selection. Independently review both full cohorts and the
replication freeze before proposing R3 PASS. Held-out work stays sealed.

Latest storage: approximately 3.1 GiB free on Linux, 171 GiB on Acer, and
7.1 GiB in `/tmp` tmpfs. Keep the Linux 1 GiB floor. Large inputs/results remain
on Acer. No user data or caches were deleted.
