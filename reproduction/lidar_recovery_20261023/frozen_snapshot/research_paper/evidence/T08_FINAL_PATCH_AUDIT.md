# Final-patch development diagnostic audit

26 September 2026. This is a software verification result, **not a recovery result**.

The versioned diagnostic patch was reverse-application checked against FAST-LIO
`7cc4175de6f8ba2edf34bab02a42195b141027e9` and rebuilt in a fresh temporary
workspace. All three catkin packages succeeded (47.7 s); existing upstream
CMake/Boost/library-path warnings remained. Acer was mounted read-only.

## Complete replays

Both runs used the checked-in Hilti configuration, LiDAR/IMU topics only,
the existing Hesai adapter, and 55 s replay duration at real-time speed.
No reference data entered the online diagnostic.

| Check | Result |
| --- | --- |
| Adapter delivered / rejected clouds | 551 / 0 in export-on run |
| Exported timestamp groups | 549; three scales each; 1,647 rows |
| Valid groups | 546 |
| Explicit unavailable groups | first scan, empty undistorted cloud, map initialization; one each |
| Complete CSV width, scales, monotonic times, finite ascending valid eigenvalues | Passed automated audit |
| Motion outputs | 546 poses in both runs; byte-identical CSVs |
| Export-on / export-off wall time | 64.96 / 64.53 s including setup and shutdown |
| Observed maximum child-process RSS | 203,664 / 204,608 KiB; not simultaneous process-tree memory |

Motion CSV SHA-256 in both runs:
`fe8da4ba0f9a411f2281546edff5bd4930aa5cc44303da9fa949ca70f53a8369`.

Health CSV SHA-256:
`444934a1a1421eb494f13e488f1eebae442f3a3e5b9979b6b76474c8ee9e5596`.

The initial two missing groups were investigated rather than hidden.
The stopped simulated clock left one final scan pending; a shutdown-only
clock advance (no extra sensor measurements) allowed its processing.
The corrected runs below supersede the initial pair for acceptance.
Wall-time differences from one pair are not a reliable overhead estimate.

## Accepted cutoff/drain check

The versioned replay script now advances `/clock` after the player stops so
ROS's simulated-time Rate can drain queued callbacks. Both corrected runs
completed successfully: 547 byte-identical poses, 550 diagnostic groups,
547 valid groups and the same three startup-unavailable groups.
The 551st scan is excluded as `REPLAY_CUTOFF_IMU_INCOMPLETE`, not healthy.
Its raw point times span 1649856282.6210558–1649856282.721027 s, while the
last supplied IMU timestamp is 1649856282.6417108 s. The preceding scan ends
at 1649856282.6210527 s and now appears in the diagnostic. This matches the
pinned `sync_packages` requirement that IMU reaches the scan end.

Corrected motion SHA-256:
`ed78b420159634f50a44992f2019e0e77434d0b172aa96083df0c9d6c86ff687`.
Corrected health SHA-256:
`716ad775f1856192fcbea85c4b3e412543b77c64310e2c7a804e47691ee9b3e3`.
Corrected evaluated stream: 1,094 rows, 768 local-valid rows; SHA-256
`1692a5446a3508b5a21ced214104df3ab0c0b160be8e3ffb6c2375d08c463cab`.
Wall times on/off: 66.99/67.00 s; observed maximum child RSS:
205,216/203,268 KiB. This is not a total simultaneous memory benchmark.

Patch SHA-256 `ea9cb9a061eb42593a4944252bf92e5edc507086652ada602e19c7772ea320a2`;
C++17 patch SHA-256 `6e60c082d6b39f5fb9f6adda43204aac170cf31f7ef9ec05764e89071fee5275`;
configuration SHA-256 `4e041bcd1f3e74778e739dcc8383f0c9069b4ab3af728463bb587c270f4ba3a8`.
T08 software acceptance is complete. No calibrated recovery decision exists.

## Reproduction and retained outputs

From the repository root, after rebuilding the pinned patched backend:

```bash
bash research_paper/experiments/run_hilti_health_smoke.sh WORKSPACE NEW_ON_DIR 55 on
bash research_paper/experiments/run_hilti_health_smoke.sh WORKSPACE NEW_OFF_DIR 55 off
python3 research_paper/experiments/src/audit_health_export.py NEW_ON_DIR/health.csv
cmp NEW_ON_DIR/poses.csv NEW_OFF_DIR/poses.csv
python3 -m unittest discover -s research_paper/experiments/tests -q
```

Raw CSVs and logs are retained locally under ignored
`research_paper/experiments/generated/runs/T08_20260926/{on55,off55,drained_on55,drained_off55}/`.
Temporary build workspace: `/tmp/fastlio-health-6qmzET` (not durable).
The test run executed 31 tests: 30 passed and one SciPy-dependent scene check
was skipped. This is not a 31/31 complete pass.

Next: the [pilot timeline](PILOT_REPORT.md) supports a diagnostic illustration
only. Hilti's inadequate independent reference still prevents R1 PASS and
quantitative recovery claims.
