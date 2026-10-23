# Independent Point-LIO one-seed acceptance

**Date:** 9 October 2026. **Decision: PASS for the preserved seed-14
sidecar-on/off feasibility pair only.** This satisfies step 3 of the accepted
Point-LIO amendment. It permits preparation/execution of the 32 development
corridor/control pairs under that amendment, subject to restored input,
runtime and provenance checks. It does not pass replication, its separate
freeze, overall R3, held-out evaluation, or publication claims.

An independent reviewer audited the raw preserved R2 pair, production
exporter/verifier, native patched source and focused tests, rather than
accepting the earlier summary alone. Repository revision inspected:
`5583b9edbb57a6deefd1f1b00f2927aea4e924b9`. Sources of the acceptance contract
were `AGENTS.md`, `execution/CURRENT_HANDOFF.md`, `AGENT_EXECUTION_PLAN.md`,
the implementation verification note, and accepted amendment SHA-256
`5c67330fe596e74a811b7e00202cef8d460a214bf4d6ff50e8ea10b86e9e4ed0`.

## Evidence inspected and independently checked

Raw run root:
`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/runs/POINTLIO_INDICATOR_FEASIBILITY_20260929_R2/`.
The `on` and `off` manifests remain respectively
`a327c5dff5ef43f6241cf4b32a2aadb92e6ddce6b19b7a3006f47117ee2f5880` and
`f0ead0d62c5fde1483c204c1700315ad721d57efd9161cc8ad59db4a37fc53e4`.
Fresh independent `verify_pair(on, off)` returned PASS. Every manifested
output was rehashed, with exact file-set agreement and no added/missing file.
The main-agent recheck is retained in
[`pointlio_feasibility_pair_recheck_20261009.json`](../evidence/pointlio_feasibility_pair_recheck_20261009.json).

| Identity | SHA-256 verified against actual current bytes |
| --- | --- |
| Retained development seed-14 input bag | `89f4ac21b24a2b9dfc86b74cd3d082e48365ac1ed63207b08969e7aca25d4627` |
| Simulation development configuration | `d23bd8799c3834ac0acc1d23476a0a0c0cd72b09f7b7c542b5bfbe9813a4c98b` |
| Preserved native binary | `80516da9cafba98262d56c17cc26ec4da76e214049d3af7776248b4c3a342b17` |
| On/off pose CSV, identical bytes | `851e8b3709e26e2c1bc607d8d6507e1c303746129e8d2bd19c761f8efce727ee` |
| Native tracked dirty patch (`git diff --binary`) | `1270c63b553f660ade9cd787c0e377d1486ac4f49018650f400f2cf52eb3445c` |

The preserved native tree at
`.../point_lio_ws_r2_20260929/src/point_lio` has upstream HEAD
`4b86a469eb5572e70ed575af25b5f15dd06e8e3c`; all nine manifest-listed native
files match, including the two added sidecar files. All 27 manifest-listed
repository source/test/compatibility files also match. On/off input,
configuration, binary, native source, build-overlay metadata and repository
source identity records agree. The pinned binary's identity is established;
this review does not claim a reproducible native rebuild or current replay.

Fresh read-only `rosbag.Bag` inspection of `/sim/points` with the isolated
`ros_env/bin/python` reproduced all 600 preserved header timestamps in order.
Native and indicator frame IDs are exactly `1..600` in order. All 181,903
scheduled groups were processed; 222,498 accepted Jacobian rows and 25,367
ordinary empty groups are accounted for. All frames are `COMPLETE` and use
actual timestamps. Frames 1–2 are explicitly
`STARTUP_INITIALIZATION`, frame 3 `MAP_INITIALIZATION`; each has zero scheduled
measurement groups. Frames 4–600 have valid diagnostics and exactly 597
monotonic frame-associated poses. There are no observed resets, and every
retained row belongs to segment 0. On/off pose bytes agree exactly; this
bounded replay supports absence of an observed estimator-output perturbation,
not universal noninterference.

The reviewer freshly ran `export_sidecar` over all raw frames, groups and
Jacobian rows, writing only to temporary directories. Its reconstruction
checks, rotation checks, group/count checks, availability rules and pose/reset
join all passed. Reconstructed segmented poses equal preserved bytes exactly.
Repeating the full export with the preserved isolated `ros_env/bin/python`
also regenerated the indicator CSV **byte-for-byte**, matching SHA-256
`814d484981cec55e58661cdb034324ca082c1943f986436227928b00aa7f7074`.
All fixed `L=1,3,5 m` fields are present. An additional export with system
Python preserved every identity, validity, reason, mask, unbounded flag and
count, but differed in floating-point final digits. All numeric comparisons
passed `math.isclose(rel_tol=1e-10, abs_tol=1e-10)`; the largest absolute
discrepancy across fields was `5.820766091346741e-11` and primary
`lambda_min_3m` maximum absolute discrepancy was `4.135358722123783e-12`.
This confirms environment sensitivity of byte-level numerical reproduction;
use the preserved isolated runtime for the replication workflow. Historical
outputs were not changed.

## Tests and scope checks

The independent focused run was:

```bash
POINTLIO_SOURCE_ROOT='/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/point_lio_ws_r2_20260929/src/point_lio' \
  python3 -m unittest discover -s research_paper/experiments/tests \
  -p 'test_pointlio*.py' -v
```

**40 tests passed, zero skips**, including freshly compiling the native reset
fixture against the exact preserved `IndicatorSidecar.cpp`. The fixture
exercises a post-start reset, shared pose/diagnostic segments `0 -> 1`, invalid
reset-frame pose, and rejection of a substituted later rotation. Analytic
tests cover known row transport, pooled Hessian/scales, rank deficiency,
ordinary empty groups, insufficient rows, nonfinite data, incomplete groups,
startup, pose joins and reset-ledger errors. Manifest/lifecycle tests reject
changed output identities, unmanifested files, failed logger/master and
interrupted replay. The reset fixture establishes the bounded sidecar/join
contract; it is not evidence that the full estimator experienced a real reset
in the retained seed-14 replay.

Native source inspection locates the pre-update rotation capture in
`h_model_output`, copies of its accepted measurement Jacobian into the sidecar,
frame/group scheduling in `laserMapping.cpp`, and the later reset branch.
The sidecar records diagnostic state and CSVs; it has no estimator state or
covariance writes. The current configuration uses `use_imu_as_input: 0` and
frame-end odometry, consistent with the instrumented output path.

Both attempts are explicitly development-seed14-feasibility-only, with
`threshold_fit_performed=false` and `heldout_inputs_opened=false`; this review
used only this retained development bag/raw output and analytic fixtures.
No native replay, threshold fit, held-out geometry generation or held-out
inspection was performed. Manifest flags are declarations, not proof about
every possible historical action. The reviewed bounded runner/exporter path
contains no threshold selection or held-out evaluation.

## Remaining boundaries

There is **no unresolved defect blocking this one-seed acceptance**. The
initial failed sidecar-on attempt remains preserved separately and is not
reclassified by this PASS. The current main-agent restoration audit reports
loss of some historical T14 primary manifests; recovery/reproduction of that
primary development provenance is separate and remains necessary for overall
R3. This review does not accept a new batch's runtime or missing inputs by
inference from the preserved R2 success.

Next eligible work is Point-LIO development replication preparation, followed
by the 32 corridor/control development pairs, independent threshold selection
on the formal development batch (never this feasibility attempt), complete
failure accounting and a separately reviewed replication freeze. Overall R3
remains **REVISE**; held-out work stays sealed.
