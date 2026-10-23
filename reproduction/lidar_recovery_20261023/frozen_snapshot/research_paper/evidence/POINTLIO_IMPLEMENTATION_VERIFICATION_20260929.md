# Point-LIO implementation verification checkpoint

**Date:** 29 September 2026
**Status:** Implementation, runner process repairs, and local checks complete;
startup failure diagnosed (prior-boot kernel ntfs3 iomap fault). Fresh
retained seed-14 sidecar-on/off feasibility replay completed with byte-identical
poses and full frame coverage; pair verification passed (`feasibility_pair=PASS`).
Awaiting independent one-seed acceptance before development replication.

## What was implemented

- A frame-pooled Point-LIO measurement-geometry score at fixed lever arms
  `L=1, 3, 5 m`, plus the frozen DCReg Schur adaptation. This is not the
  Point-LIO posterior covariance, a new estimator, or a recovery result.
- A read-only native sidecar that records accepted measurement rows,
  pre-update rotations, frame/group counts, reset events, and durable output
  status without changing estimator updates.
- A CSV exporter that checks each input frame, group, row, source-basis
  reconstruction, pose identity and reset segment. Invalid numeric evidence is
  unavailable, not converted into a positive score.
- Attempt manifests use atomic replacement, preserve the original run
  identity, and hash every output file. The runner records a `RUNNING` attempt
  before ROS setup and keeps failure recording active through final output
  persistence.
- The runner selects a private loopback ROS master, verifies its process, and
  records ROS, estimator, bag and pose-logger exit statuses. Shutdown waits
  are bounded and escalate from interrupt to terminate/kill; a failed logger
  or master cannot be reported as a completed pair.
- Runner process-group management and liveness detection: robust zombie-state
  detection, recursive descendant tree cleanup, active worker monitoring during
  playback, and reliable signal escalation guarantee no orphaned rosbag processes.

## Verification performed

The complete experiment test suite ran with the native C++ reset fixture
enabled and runner helper unit tests:

```text
Ran 165 tests
OK (skipped=2)
```

The skips are optional SciPy scene-audit tests. The native reset fixture
compiled the exact patched `IndicatorSidecar.cpp` on the Acer partition, forced
a reset after startup, and passed its frame ledger, reset event, synthetic
pose stream and export through the production Python exporter/joiner. It confirmed segments
`0 -> 1`, marked an emitted reset-frame pose invalid, and rejected a substituted
post-update rotation because it could not reconstruct the stored common-basis
Jacobian rows.

Additional checks passed:

- `bash -n research_paper/experiments/run_point_lio_indicator_feasibility.sh`
- `git diff --check`
- Shell mock and unit tests: liveness detection, recursive tree kill, signal
  escalation, process-group signaling, recorder failure/success flags.
- Manifest tests: atomic replacement, identity preservation, and intact prior
  manifest after serialization failure.
- Adversarial exporter/pair tests: non-finite common rows, finite improper
  rotations, changed output hashes, unmanifested files, invalid indicator
  states, failed logger and failed ROS master all reject or remain unavailable
  as specified.

System storage was checked after verification: Linux had **4.4 GB free** and
the Acer partition had **113 GB free**.

## Exact code identities

| Artifact | SHA-256 |
| --- | --- |
| `src/pointlio_information.py` | `c141d5dfc86df130310beaba3224726e60a7b8224d6958d846d0ae98575d5f19` |
| `src/pointlio_indicator_export.py` | `06d2c71c9aa55d33f4009e89b6605c481a7af7b3969bd6a919ae9df766d2f8b0` |
| `src/verify_pointlio_feasibility_pair.py` | `00e5e6a1c34ff05cacc0beceb3ddb5bf6edb2619467ebe3b2b3e0cb8c43b79af` |
| `src/record_pointlio_attempt.py` | `9acce5d1981781b4427cb35bcc9815410a6e69a97fe395127ba9ea0d433ffcf5` |
| `src/pointlio_pose_logger.py` | `041aebef03bd8a972282e42f7ba1521e8943385c352e0edd3c11ec2eb87bdd3d` |
| `src/pointlio_runner_helpers.sh` | `1e8a8f60a6524fb045c45e91d24c026027b7f7085c3acaa6954e5b5d91697aeb` |
| `tests/test_pointlio_runner_helpers.py` | `7fda751a0f2164f24bf174fa21390e6c6e329b627ca07d1a07ec5bd42b881de7` |
| `run_point_lio_indicator_feasibility.sh` | `287145820339fc15de3698334b2c9df19e2f5ba8b97434533f0c7f35b5aa3ce3` |
| native patch | `9df4d1eb3203bf097df94d25e5d59f566c0eff4a2f11f26b5ebcc6fb8cb71d24` |
| native reset fixture | `47a6cb75b0f28cf5b20b9d9a8ebb710153471d6821b6bd630a63850cde36be06` |

The built Point-LIO binary remains SHA-256
`80516da9cafba98262d56c17cc26ec4da76e214049d3af7776248b4c3a342b17` at the
pinned T15 source revision `4b86a469eb5572e70ed575af25b5f15dd06e8e3c`.

## First bounded feasibility attempt (Preserved)

Output root on Acer:
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/POINTLIO_INDICATOR_FEASIBILITY_20260929/`

| Mode | Status | Audited inputs | Poses | Health rows/groups | Manifest SHA-256 |
| --- | --- | ---: | ---: | ---: | --- |
| Sidecar off | `COMPLETED` | 600 | 597 | not applicable | `e84e4592653886d11eea8f1497bb0bf47993a2e2a11640eee06a04f66264d3ad` |
| Sidecar on | `RUN_FAILED` | 600 | 0 | 0 | `beb6aac745bfb5eabac86191c77b1642ff3c6e29d72b2ae7ba9c622ea1256c43` |

### Diagnosis of startup failure in first attempt

Kernel ring buffer logs (`journalctl -b -2 -k`) revealed that during the prior
boot session, the in-tree kernel `ntfs3` driver (`Linux 7.0.0-34-generic`) hit
`kernel BUG at fs/iomap/buffered-io.c:1061!` during buffered folio write
operations on the NTFS Acer mount. When PID 121718 (`pointlio_mapping`) started
and opened its redirected log file on Acer, calling `write()`, `ntfs3` triggered
a fatal kernel BUG (`Oops: [#2]`), abruptly terminating the process before it
could register ROS subscribers (`sub_pcl`, `sub_imu`). Rosbag therefore waited
indefinitely for subscribers that never registered. After reboot into boot 0,
the runner process cleanup was upgraded, and redirected file writes executed cleanly.
Both initial runs are permanently preserved under `.../POINTLIO_INDICATOR_FEASIBILITY_20260929/`.

## Second bounded feasibility attempt (R2 — Verified)

Output root on Acer:
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/POINTLIO_INDICATOR_FEASIBILITY_20260929_R2/`

| Mode | Status | Audited inputs | Poses | Health rows/groups | Manifest SHA-256 |
| --- | --- | ---: | ---: | ---: | --- |
| Sidecar off | `COMPLETED` | 600 | 597 | not applicable | `f0ead0d62c5fde1483c204c1700315ad721d57efd9161cc8ad59db4a37fc53e4` |
| Sidecar on | `COMPLETED` | 600 | 597 | 600 / 181,903 | `a327c5dff5ef43f6241cf4b32a2aadb92e6ddce6b19b7a3006f47117ee2f5880` |

### Feasibility pair verification results

Verification executed:
```bash
python3 research_paper/experiments/src/verify_pointlio_feasibility_pair.py \
  --sidecar-on /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/POINTLIO_INDICATOR_FEASIBILITY_20260929_R2/on \
  --sidecar-off /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/POINTLIO_INDICATOR_FEASIBILITY_20260929_R2/off \
  --output research_paper/evidence/pointlio_feasibility_pair_verification_20260929.json
```

Output: `feasibility_pair=PASS output=research_paper/evidence/pointlio_feasibility_pair_verification_20260929.json`
Verification manifest SHA-256: `ccb5aeda0bb4b89c5a8b5a4ed7ed57d89cd673b3eb1f481bd287815014ca8052`

- **Byte-identical pose streams:** Both sidecar-on and sidecar-off runs produced
  identical `poses.csv` files with SHA-256
  `851e8b3709e26e2c1bc607d8d6507e1c303746129e8d2bd19c761f8efce727ee`.
- **Full input frame coverage:** All 600 raw input frames are accounted for in
  the sidecar frame ledger and exported indicators with monotonic IDs `1..600`.
- **Complete measurement groups:** 181,903 measurement groups and 222,498
  Jacobian rows were recorded without dropped frames.
- **Startup unavailability parity:** Exactly 3 startup-unavailable frames
  (frames 1..3, matching FAST-LIO's 3 startup unavailable frames).
- **Clean process shutdown:** All processes exited cleanly: rosbag `0`,
  pointlio `0`, pose_logger `0`, roscore `0`, exporter `0` (on) / `-2` (off).
- **No threshold fit / no held-out access:** `threshold_fit_performed=false`,
  `heldout_inputs_opened=false`.

## Next required gate

Independent acceptance of this one-seed feasibility check must be obtained
before the 32-pair Point-LIO development replication batch is started.
Overall R3 remains **REVISE**; no implementation freeze, final evaluation, or
publication claim is authorized.
