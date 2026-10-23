# T14 — Formal-route development batch and recovery record

Updated: 27 September 2026. **T14 is complete as a development execution and
provenance task, with a repeat-execution deviation disclosed for R3 review.**
This is not a recovered-threshold result, final-test evaluation, publication
verdict or scientific conclusion.

## What was run

- Named route: `T14_FORMAL_X_MINUS_6_V1`; body starts at `x=-6 m`, enters at
  `10.5 s`, exits at `3 + (6 + corridor_length_m) / 0.8 s`, and runs for 60 s.
  A -1 m translation wraps the frozen R2 simulator; the sensor model, random
  streams, motion derivatives and geometry implementation were not changed.
- Scene-only eligibility passed **32/32** development layouts, seeds 14–45.
  See the [final screen](randomized_layout_geometry_screen_t14_xminus6_dev14_45_v2.json).
- Every primary corridor/control run for all 32 seeds completed: **64/64**.
  All 32 paired-bag audits found identical IMU streams and the expected 600
  LiDAR scans / 12,021 IMU records. Sensor bags contain no truth/reference.
- Each of the 64 primary outputs contains 600 diagnostic groups, 597 valid
  DCReg rows and 1,154 valid local-motion rows. The three unavailable startup
  groups remain explicit. The audit verified **768 primary output files** and
  24 seed-45-repeat output files.
- Seed 45 corridor and control repeat replays also completed. Thus all four
  seed-45 primary/repeat outputs exist and are hash-audited.
- The run ledger is in
  [`runs/T14_FORMAL_BATCH`](../experiments/generated/runs/T14_FORMAL_BATCH).
  Its final summary has 62 exact-hash cache hits, four new completed seed-45
  runs, and two failed scheduled seed-14 repeat entries. “Cached” means the
  earlier completed run manifest and every output hash were revalidated; it
  does not mean the replay was skipped without checking its identity.

The machine-measured mean primary replay time was `71.625 s` (median
`71.639 s`). GNU time reported a maximum observed replay-command RSS of
`192,852 KiB` across the audited primary/seed-45-repeat runs; this is not a
whole-machine or Raspberry Pi measurement. The 64 generated sensor bags total
`5,167,514,944 bytes` (`4.813 GiB`). They are reproducible development inputs,
not files to commit.

## Repeat evidence and the quota deviation

The first and last eligible layouts were 14 and 45. The seed-45 corridor and
control repeat runs used the exact same input/config/backend fingerprints as
their primary runs. Their measurement streams were not byte-identical to the
primary outputs, so T16 must quantify this run-to-run variability rather than
assume deterministic FAST-LIO replay.

For seed 14, the [pre-batch smoke pair](../experiments/generated/runs/T14_PREBATCH_SMOKE)
is retained as repeat evidence alongside the primary pair. Both smoke and
primary runs used the same bag, reference, configuration, FAST-LIO binary,
backend patch hashes and analysis/replay sources. The provenance-only runner
source hash differs because runtime-version fingerprinting was added after
the smoke. In the corridor, the five measurement/evaluation CSVs match
byte-for-byte. In the control, all five differ despite identical inputs and
backend; this is a repeatability observation, not a result to hide.

The two formal in-batch seed-14 repeat launches and their one permitted
technical retries failed at ROS environment setup with `OSError [Errno 122]
Disk quota exceeded`, before FAST-LIO replay. Those four failed launches remain
in `failure_ledger.csv` and their manifests. The pre-batch smoke pair was
executed before any outcomes were inspected and is being used to cover the
first-seed repeat pair. **R3 must explicitly adjudicate this reconciliation**;
if it rejects counting the earlier exact-input smoke pair, the repeatability
gate remains incomplete and the study scope must be amended/re-reviewed before
any held-out work.

The quota also prevented seed-45 input generation on the first pass. The
partial 13 MB corridor-bag attempt, preflight manifests and original batch
summary were preserved under `runs/T14_FORMAL_BATCH/failure_attempts/` and
`/run/user/1000/t14-formal-failed-inputs-20260927/`. After freeing quota using
verified completed bags, seed 45 was regenerated, its hashes and paired IMU
were checked, and the primary/repeat runs completed. The append-only ledger
contains **74 entries**: 66 completed, four crash attempts and four input
preflight failures. No failed attempt was removed or replaced by another
layout.

## Durable provenance and limitations

The small, persistent [input provenance bundle](../experiments/generated/t14_formal_input_provenance_v1)
contains all 64 input manifests and their per-run reference metadata, plus the
shared analytic reference file (SHA-256
`4f313d82398e75de996866a6cb864fa26a75ed5e095b1fdb72f03ee2e5db561a`). Sensor
bags are omitted there; their exact hashes and sizes remain in the manifests.
Eleven raw bags were also retained in the ignored
[`t14_retained_inputs`](../experiments/generated/t14_retained_inputs) directory
(seed-14 corridor; both scenes for seeds 15–18; both seed-45 scenes). The other
53 bag files remain under `/tmp`; their current symlinks include session-local
`/run/user/1000` targets. Regenerate those from the saved seeds/hashes if the
session ends before T16 finishes using them.
Several temporary bag files were moved to `/run/user/1000` to work around the
6 GiB per-user `/tmp` quota, so those copies and current `/tmp` symlinks are
session-local. If they disappear, regenerate from the saved manifests/seeds
before any replay; do not silently substitute a different input.

The machine-readable [batch audit](t14_development_batch_manifest.json),
[current handoff](../execution/handoffs/T14.md) and [status ledger](../execution/STATUS.md)
record the exact checks. All data remain development-only. No held-out input
was generated or screened, no threshold was fitted, and no recovery labels or
publication conclusion were produced. T16 must calculate the frozen
reference-defined recovery outcomes and development-only operating point;
R3 must review the repeat deviation, run-to-run variability, simulator and
implementation before any final-test data are opened.
