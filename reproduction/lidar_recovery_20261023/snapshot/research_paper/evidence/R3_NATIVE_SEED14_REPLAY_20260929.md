# T16-R3-10 — current native replay and cached resume

**Date:** 29 September 2026
**Status:** Development-only lifecycle check completed and accepted by the
fifth independent R3 follow-up. Overall R3 remains **REVISE** because
Point-LIO comparability and development-replication readiness remain open.
No held-out layout or input was generated, screened or inspected.

## Purpose and scope

Run the retained seed-14 corridor input through the current supervised
FAST-LIO replay wrapper, then repeat the same run ID to prove that the saved
result is reused without launching FAST-LIO again. This is a software and
lifecycle check on an existing development input. It is not a new event, a
threshold-selection run, a final result or evidence of novelty.

The input manifest declares `role=development`, `seed=14`, and `control=false`.
Its raw manifest SHA-256 is
`1a8c6c0da541248ef5a683b336745f0e392b7573e1f9d77f99d36bca7423da02`; the
canonical scientific input identity is
`7659854ba1bfe95ad7c229d4fca9b84ea3accfb59471f0de97eeba2a26260675`.
The sensor-bag hash is
`89f4ac21b24a2b9dfc86b74cd3d082e48365ac1ed63207b08969e7aca25d4627`; the
reference hash is
`4f313d82398e75de996866a6cb864fa26a75ed5e095b1fdb72f03ee2e5db561a`; the
reference-metadata hash is
`f84ebe5f3094f2c707397c3ecc71416822eedd30c165af110588bad5954072a5`.

## Verified implementation and environment

- FAST-LIO upstream revision: `7cc4175de6f8ba2edf34bab02a42195b141027e9`.
- Rebuilt source diff: `1397219a8765c2bc8c49adaf7e94dcc1e6006788acac06467e28e660876e51a0`.
- Executed FAST-LIO binary: `4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792` (exact T14 hash).
- ROS environment: Python `3.12.14`, NumPy `2.5.3`; Conda history SHA-256 `90c14f8caa0cbc8a1a769f012c5bbcd9c1fbe7ba96d4626f22bbc077917b757f`.
- Current R3 runner SHA-256: `149bcd952916518bb803b1730518a8b59abb807127eab534f61b5f84a79dae13`.
- Supervised replay wrapper SHA-256: `2da73b9d5fe821c72c85edec8519cb3c50d7b602518a10ec0927eb9d358142c3`.
- Historical T14 wrapper SHA-256: `a3465d33b85b7f0b0f59e444297c1b71447af1ee7aa3dd2773b33a0172ca3639`.
- R3 validation script SHA-256: `f1b90be692659f098fa2f1d346eb17bd03e9e9049d4d489c4e539ab26f9f54b6`.

The expected source-diff and binary hashes matched before replay. The new
workspace was built at the recorded ext4 path `/tmp/fastlio-t13.XBDWGy/ws`;
build files occupy about 572 MB. Linux has about 4.94 GB free after the build,
so more than 1 GB remains free. All replay logs, manifests and outputs are on
the Acer partition.

## Commands and outcome

The first command performed the native development replay:

```bash
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python research_paper/experiments/src/run_r3_development_validation.py \
  --ros-env /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env \
  --workspace /tmp/fastlio-t13.XBDWGy/ws \
  --input-dir research_paper/experiments/generated/t14_retained_inputs/T14_FORMAL_DEV14_CORRIDOR_INPUT_XM6_V1 \
  --run-root /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/R3_NATIVE_SEED14_20260929 \
  --run-id R3_NATIVE_SEED14_20260929_A1 \
  --output-manifest /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/R3_NATIVE_SEED14_20260929/r3_development_validation_completed.json
```

It returned `COMPLETED` with `FULL_SENSOR_INPUT_AND_FLUSHED_POSE_LOG`:

| Check | Result |
| --- | ---: |
| Expected and audited LiDAR scans | 600 / 600 |
| FAST-LIO health groups | 600 |
| DCReg rows | 600 |
| Valid poses | 597 |
| Invalid pose records / reset records | 0 / 0 |
| Evaluated local-motion windows | 1,194 |
| Valid local-motion windows | 1,154 |
| Reference gaps | 0 |
| Health/Hessian parity | 600 timestamps; max absolute error `3.637978807091713e-11`; 597 valid and 3 startup-unavailable |
| Runtime / maximum resident set | 1:13.44 / 190,888 KB |
| Process exit status | 0 |

The same command was then repeated with the same run ID and a different
summary-manifest path. It returned **`CACHED`** immediately. Both summaries
point to the same `run_manifest.json` SHA-256
`4de6b50d6f4fc492dab6db2bb741c05894d2370f7ac695fd256764c7b3d99e31`; the
retained output hashes and metrics match. There was no FAST-LIO process before
or after the cache check, so the estimator was not relaunched.

## Retained evidence on Acer

Output folder:
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/R3_NATIVE_SEED14_20260929/`

- [Completed replay summary](/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/R3_NATIVE_SEED14_20260929/r3_development_validation_completed.json) — SHA-256 `7220729ded793d8444230687f692166082cf22ada05e4b2627114828d727d29b`.
- [Cached-resume summary](/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/R3_NATIVE_SEED14_20260929/r3_development_validation_cached_resume.json) — SHA-256 `74cbccb6061bb4d7333a49445ede20168c74403a345198dff724a023dfd559f2`.
- [Native run manifest](/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/R3_NATIVE_SEED14_20260929/R3_NATIVE_SEED14_20260929_A1/run_manifest.json) — SHA-256 `4de6b50d6f4fc492dab6db2bb741c05894d2370f7ac695fd256764c7b3d99e31`.
- Key stream hashes: health `e72043860f57108d6dcc066627d8ffbeccc91d2907869834ea322da2343d00c7`; Hessian sidecar `ba017155118cf769ba5dc057593be50a9b28ca30a6dabf83549149422a50b08d`; DCReg `9aa00cdca0ed7728fb19f210b78f6af461d7977ee9908e45928d051b44758420`; evaluation `0a8b067a6bcc0d6d692a3097e59e600250739963610e2c76c0eb6c1133cecd92`; poses `7667563843a95442c280f1c32059f371db2f7d2fceddcce11db77f9f39c21e54`.
- Resource log `resources.time.txt` SHA-256: `f96d3d7cae3f5c0153ca3cf1296de05ca28be095a9f1dfec148f07a6e7cd4ed9`.

The run manifest lists hashes for all retained outputs, post-processing logs,
input files and execution sources. The raw sensor bag was not copied into the
output folder or Git.

## Limits and next gate

This proves that the current source, exact T14 binary, Acer ROS environment,
supervised wrapper, playback shutdown, pose flush, post-processing and
scene-level cache resume worked together on one **development** input. It
does not establish a recovery-performance result, replication, generality,
publication novelty or flight safety. The fifth independent R3 follow-up
audited this replay and accepted T16-R3-10. Overall R3 remains **REVISE**
because the original plan still requires Point-LIO health-signal comparability
and a separate development freeze before an implementation freeze or
held-out phase.
