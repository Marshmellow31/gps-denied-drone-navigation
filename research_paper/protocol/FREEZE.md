# R2 protocol freeze — 26 September 2026

**Gate:** PASS for protocol content only.  
**Review:** [R2_PROTOCOL.md](../reviews/R2_PROTOCOL.md), final independent
GPT-6 Astra review.  
**Repository:** branch `main`, HEAD
`f09f62fa805082b8138a44a2f43833f68e0c39d3`. The worktree is dirty. The
content hashes below, not HEAD alone, identify the reviewed state.  
**Scope:** simulation-primary study of whether existing LiDAR registration
health indicators predict reference-defined local motion after a weak-geometry
exit. This freezes the experiment protocol, not implementation correctness,
novelty, publication readiness, real-world accuracy or flight safety.

**Hash read-back:** 51/51 listed files matched on 26 September and again after
the D035 amendment on 27 September 2026. The
freeze-file SHA-256 is recorded in the execution handoff; it is not part of its
own checksum table.

**Editorial read-back amendment (27 September 2026):** The public root
[`README.md`](../../README.md) now describes the completed T16 development
checkpoint, and the append-only [decision log](../execution/DECISIONS.md)
records T15/T16. These are explanatory/status records only: no frozen
indicator, label, simulator, split, threshold rule or test outcome was
changed. Their table hashes are updated below; the previous README, decision
log and freeze-file hashes are preserved in decision D034. The other 49 listed
artifact hashes are unchanged. This amendment does not pass R3 or authorize
held-out generation or screening.

**Editorial read-back amendment D035 (27 September 2026):** The root README now
collects the full task roadmap, development-only results, available figures,
verification state and remaining gates in plain language. It also reports the
latest suite accurately: 88 passed, two errors caused by the still-missing T14
repeat-audit artifacts, and one optional SciPy skip (91 tests discovered).
The append-only decision log records this README update. This is documentation
only: no protocol method, threshold, split, input or scientific result changed.
The pre-amendment freeze SHA-256 was
`8b6ef5fb83ff459f078bb89c9f0dc7b1708e44d23dfb586598d36ba59198031f`; the
previous README and decision-log hashes are recorded in D035. Their two table
entries are refreshed below; the other 49 listed artifact hashes are unchanged.
R2 remains PASS for protocol content only. R3 remains REVISE and no held-out
screening or run is authorized.

R1 passed only to permit protocol design. R2 had two REVISE rounds; the final
review accepted the revised content. The user approved the 20 s full-triple
deadline and the formal x=-6 m route. T13–T16 and R3 remain outstanding.

## Frozen research question and limits

For the fixed FAST-LIO implementation, do its online geometric health signals
identify when short-window translation and rotation accuracy has returned
after an independently annotated geometry exit? The outcomes are false
healthy declarations, recovery sensitivity/delay, availability, non-recovery
and relapse. Accumulated pose drift stays separate. This is an evaluation of
existing signals, not a new estimator or detector.

The primary evidence is synthetic and has exact analytic truth independent of
FAST-LIO computation; it is not an independent physical measurement. Sensor
noise/bias settings are uncalibrated stress values, geometry is axis-aligned
rectangular, and clocks/extrinsics are ideal. Hilti Exp18 is supporting only:
its post-exit reference is sparse and partly LiDAR-map-derived. No claim of
flight safety, new topology transfer or “first” novelty is frozen.

## Frozen methods

1. `FASTLIO_MIN_EIG_G3`: the T08 measurement-only point-to-plane information
   from the first six columns at FAST-LIO's accepted correspondence stage,
   normalized by `N*0.001` with rotation lever scale 3 m. Require `N>=6`;
   larger finite `G_3m` is healthier. It is not the EKF posterior.
2. `DCREG_SCHUR_MASK`: DCReg's Section 4.2 Schur-complement directional
   condition detector, adapted to those same accepted FAST-LIO correspondences
   using the declared translation/rotation block permutation. It is not the
   full DCReg optimizer or PCG mitigation. Use Moore-Penrose `rcond=1e-12`,
   float64, symmetrized Schur matrices, negative-eigen tolerance
   `1e-10*max(abs(eigenvalues))`, clamp only small negative values, and report
   `UNAVAILABLE` for non-finite/materially non-PSD cases. Fewer than six rows
   is `INSUFFICIENT_CORRESPONDENCES`. Set a ratio infinite when
   `lambda_i<=1e-12*lambda_max`, or when that subspace has zero maximum
   eigenvalue. Flag only `kappa_i>10` (equality is not flagged). The continuous
   health score for curves is `1/max(all six kappa_i)`, zero when any ratio is
   infinite. Serialize infinite ratios as null/blank plus an explicit
   unbounded flag, never as a non-finite numeric value.

The DCReg equations/threshold are grounded in the main paper Sections 4.2–4.4,
Equations 18–21; the Moore-Penrose generalization is cited there. Official
implementation revision inspected: `8ce8451b15491a4bbe17cf85ab02a8bed6696861`.
FAST-LIO revision: `7cc4175de6f8ba2edf34bab02a42195b141027e9`.

## Frozen outcomes and decisions

- Local motion uses transform-relative translation norm and SO(3) rotation
  angle without re-alignment at either endpoint. The primary 1 s local window
  passes at translation `<=0.20 m` and rotation `<=5 degrees`; the 3 s
  sensitivity rates are `<=0.20 m/s` and `<=5 degrees/s`. Half/double label
  sensitivities are `0.10 m/2.5 degrees` and `0.40 m/10 degrees`. These are
  study cutoffs adapted from DCReg registration-pair recall, not safety limits.
- Nominal 1 s windows use integer simulation-clock boundaries. Associate each
  boundary once to the nearest valid estimator pose within `±0.05 s`, tie to
  the earlier pose, and reuse that pose for adjacent windows. Boundaries must
  be unique, strictly increasing and same-segment; the first used start must
  be strictly after `t_exit`. Use actual associated times and actual duration.
- Recovery onset is the actual start boundary of the earliest three
  consecutive passing non-overlapping windows. All three actual endpoints
  must be `<=t_exit+20 s`; truth-recovery confirmation is the actual third
  endpoint. A crash/timeout/incomplete run is failed/incomplete, not
  non-recovery. One documented technical retry is allowed only with identical
  input/config/code; use the first successful attempt and retain all failures.
- A later failed-threshold or invalid-estimate window in a completed run marks
  relapse at its associated actual start boundary. The first recovery episode
  remains the primary onset; later recoveries are descriptive only. Relapse
  false-healthy outcomes are reported separately.
- Health decisions use 0.1 s ticks from simulation time zero. Associate the
  latest record, valid or invalid, at or before the tick, maximum age 0.2 s,
  same estimator segment. A newer invalid record, reset or segment boundary is
  an unavailable barrier; do not fall back to an older valid value. Debounce
  is `INACTIVE -> CONFIRMED_HEALTHY` after three distinct healthy source
  records on consecutive ticks. Confirmation time is the third decision tick;
  source timestamps are retained separately. A continuous active run does not
  emit repeated alarms; unhealthy/unavailable resets it.
- A pre-onset confirmed healthy state is a premature false-healthy declaration
  and cannot count as recovery sensitivity. Primary sensitivity requires a
  new inactive-to-confirmed transition at/after onset and before relapse or
  deadline. No-score events are sensitivity misses. Event and time
  false-healthy rates are reported conditional on available decisions and
  unconditionally; decision availability is separate. Controls have no
  recovery label and are reported as healthy-scene context only.
- FAST-LIO operating-point calibration uses corridor runs from randomized
  development seeds 14–45 only; fixed-layout seeds 10–13 and controls do not
  train the threshold. There is no fitted score model, so this is development
  threshold calibration, not cross-validation. Candidate thresholds are all
  unique finite valid scores plus `NO_ALARMS`; healthy means `score>=threshold`.
  Choose maximum post-onset sensitivity subject to conditional event
  false-healthy rate `<=10%`; ties choose the higher numeric threshold. If the
  denominator is zero or every feasible threshold has zero sensitivity, report
  `NO_FEASIBLE_OPERATING_POINT`. Lock the chosen numeric threshold at R3 before
  held-out outputs are opened. DCReg `kappa_th=10` is fixed and never tuned.
- Time-point ROC/PR uses recovered/unrecovered hindsight labels and an
  event-balanced weight of `1/valid_ticks_in_geometry_cluster`. FAST-LIO `G_3m`
  and DCReg `1/max(kappa)` are higher-is-healthier scores. Ties are grouped;
  ROC-AUC is trapezoidal and AP is the right-step sum. If pooled labels or a
  bootstrap resample has one class, its curve or interval is unavailable, not
  silently dropped.

## Frozen simulation, splits and sample size

- Formal T14 route starts at x=-6 m, with entry at 10.5 s and
  `t_exit=3+(6+L)/0.8 s`; length 18 m exits at 33 s. Each run lasts 60 s,
  giving at least 27 s after exit. T14 must implement this as a named profile,
  regenerate all development seeds with new run IDs, and rerun the geometry
  screen before LIO. The old x=-5 m seed-14 run remains feasibility-only.
- Each split seed is both `layout_seed` and `sensor_seed`; corridor/control
  share them. Geometry uses `SeedSequence([layout_seed,0x4C494441])`; the
  sensor seed spawns separate IMU-white-noise, LiDAR-noise and bias streams in
  that order. T14 records NumPy version and seed/spawn mapping.
- Geometry-only eligibility before any LIO: corridor midpoint x-normal fraction
  `<=0.10`, feature control `>=0.15`, and room at exit+5 s `>=0.20`. Re-run this
  screen for the formal route. A development seed failing the frozen screen
  returns to R2; do not substitute from outside 14–45. Held-out seeds are not
  generated or screened until after R3.
- Development: seeds 14–45, 32 independent geometry clusters, central ranges
  `L=9–13 m`, half-width `1.6–2.4 m`. Fixed v3 seeds 10–13 are one separate
  feasibility cluster. Held-out strata remain the four rows in `SPLITS.csv`:
  short/narrow 100–119; short/wide 120–139; long/narrow 140–159; long/wide
  160–179. Select the lowest eligible reserved seed IDs in each stratum,
  expanding equally by one per stratum per round from 12 to at most 20 each.
  Geometry rejection is logged and advances only within the same stratum; if a
  stratum cannot meet its target, return to R2 before LIO.
- Compute `s_dev` from exactly 32 complete development geometry pairs. Interior
  is body x in `[L/4,3L/4)`, with nominal integer-second windows. Require at
  least five planned windows and all valid in both scenes per seed; any
  missing pair returns to R2 without omission/substitution. For each seed,
  subtract control from corridor per-scene median translation error. `s_dev`
  is the sample SD with denominator `n-1`. Set
  `n_cont=ceil((1.96*s_dev/0.10m)^2)`, round up to a multiple of four, and
  `n_test=max(48,n_cont)`. If `n_test>80`, return to R2 without test inspection.
- Event proportions use 95% Wilson score intervals, pooled and per stratum.
  For continuous paired outcomes, report the equal-stratum mean of per-seed
  medians. Bootstrap 10,000 times with `Generator(PCG64(20260926))`, fixed
  stratum order short/narrow, short/wide, long/narrow, long/wide, drawing `n_h`
  geometry seeds with replacement within each stratum and preserving each
  corridor/control pair. Percentiles use NumPy `method="linear"`. Freeze the
  analysis environment at Python 3.12.14/NumPy 2.5.3. If any final geometry pair
  remains incomplete after one technical retry, keep it in the failure ledger,
  do not replace it, and treat final estimates as descriptive only (no
  confirmatory interval/claim under the planned sample size).

## Repetitions, tuning, resources and downstream gates

- T14 is development-only: one corridor/control pair for each seed 14–45, plus
  one exact-input repeat of the first and last geometry seeds eligible under
  the scene-only screen (four repeat FAST-LIO runs). Repeats assess backend
  repeatability only; they are not independent events or threshold-training
  records. No held-out input or screen before R3 PASS.
- R2 freezes simulator/noise/bias factors, geometry screen, comparator rules,
  recovery cutoffs, denominators and analysis. The only scientific operating
  value selected after R2 is one global FAST-LIO threshold via the frozen rule;
  all other LIO settings stay fixed. Correctness fixes that affect scores need
  a dated amendment and regenerated development evidence. No per-scene tuning.
- If retained, raw bags would require about 13–18 GB. Use one pair at a time in
  scratch (about 162 MB per 60 s pair); retain output hashes/manifests and
  successful compact outputs; keep failed inputs until diagnosed. Check free
  space before every pair and stop if projected output space is insufficient.
  Acer had 104 GB free but is read-only; no remount is required for the scratch
  plan. 60 s runtime is a scaled planning estimate (about 2–5.6 h for the
  planned 80–112 primary pairs, before audits); T14 must time its first formal
  pair and update the budget.
- With this hash bundle re-read, R2 permits T13 comparator implementation,
  T14 formal development runs, and T15's single pinned Point-LIO development
  smoke. T16 reports all development results and prepares the final handoff.
  R3 must freeze implementation before any held-out generation, screen or
  evaluation. None of those implementation/results gates are passed by R2.

## Reviewed content hashes

These SHA-256 values cover the current content, including untracked files.
They supplement (not replace) HEAD because the worktree is dirty. Files that
only report live task status are not part of the scientific freeze. Verify a
listed file with `sha256sum <path>` before implementation; any mismatch in a
governing file invalidates this freeze until an amendment/re-review.

| File | SHA-256 |
| --- | --- |
| `AGENTS.md` | `eaa9e4584d866150cf30ff50f3820ea81aeef1d677df469372c075d341cc02dd` |
| `README.md` | `f05f5aecdf06f27ead7fedf75d73d77e9a67f673bf022f1ab8d92086effed3cc` |
| `research_paper/AGENT_EXECUTION_PLAN.md` | `18ade8e8130abcb492616ad03de19c0fee60a60017c6f43a67102b4079f6a392` |
| `research_paper/RESEARCH_GOAL.md` | `4feca0c33246405bce20e0f4ed2be0cfe78b1fb5c2df1629a08564d4c2c6ce33` |
| `research_paper/SCOPE_DECISION.md` | `feb85397efcc8e222785881b9b28a3b4d7b899a893de0269ad9208a5ff337d32` |
| `research_paper/SCOPE_AMENDMENT_SIMULATION.md` | `edfda5a59a376f10d4184d3e0d9451d1435267e67fd7a9854d70b30ba17dcfbc` |
| `research_paper/execution/DECISIONS.md` | `8a22fe99421e8aa5439d0e7554979183136a33fd06e2fd9048d4d7349dea5fe4` |
| `research_paper/literature/COMPARISON.md` | `411e52abb3469b205a7cdb891a388749a9ab8ac5fe56295beff54e88f57b0a7f` |
| `research_paper/literature/GAP_DECISION.md` | `e5188eaf327386c3a5470e3cd758410bbe83cf626e890739a344634ed0650b9c` |
| `research_paper/literature/RECOVERY_OVERLAP_UPDATE.md` | `117e4c40ed3b98906739d0dace28493b7f297a709f20aa72834cc8583d581255` |
| `research_paper/literature/INFORMED_CONSTRAINED_ALIGNED.md` | `4c6367805186a8121c09ee81bd75295d2d81c3798abd973f9d1a378bad72de8d` |
| `research_paper/literature/SEARCH_LOG.md` | `d73e0893f9dc70c522e72fa03787de2d341a4198ce782223a9b77e08d5bf1da7` |
| `research_paper/reviews/R1_FEASIBILITY.md` | `358186ea18202c558ed52bb8d0013b7a14a387ce577191a2375b6d1086dec5cf` |
| `research_paper/reviews/R2_PROTOCOL.md` | `2895379745daaee5f009bc2aa67d5812a5e47693207a2a4e45b96b9bcc9cc961` |
| `research_paper/protocol/DATA_CONTRACT.md` | `c06d112996cf66460c1eb87aba54da78c1fb9d31dfff2e4f59a3aa4b453ae95a` |
| `research_paper/protocol/FASTLIO_INFORMATION_DIAGNOSTIC.md` | `6723a9b4838756b76d9be3835d587c4487eb4ee40b9ccde4e49c04c3009b36a8` |
| `research_paper/protocol/INDICATORS.md` | `510056955e3c9d7b943897da6c2533ab8cd8b870afdecd070de89db8fd2250e2` |
| `research_paper/protocol/METRICS.md` | `06f5bf3950a3784fdd95c1eb6767dfec83ace8237e7d99a275f3ed13074d03cc` |
| `research_paper/protocol/SIMULATION.md` | `27ae3e937de17b12d81f66149a443ba752febb61a4547d1a32c3a2d0b2221811` |
| `research_paper/data/SPLITS.csv` | `d9d5496a55a2bb55cbf4a294be87df41ebb3b57ff24bdfd0e6fc0fcc8d682172` |
| `research_paper/data/ALTERNATIVE_REFERENCE_AUDIT.md` | `0751ef48773b3b6b7e04d11615c5e16d8cdd89bb2fba0e5b5702ab3e98eeac34` |
| `research_paper/data/HILTI_EXP18_EVENT.md` | `5df0f283b2ff09429f95815423439d69d7c5d06a769a26c27763c7a5060e4c04` |
| `research_paper/data/hilti_exp18_reference_metadata.json` | `070105fcbf14b97f0407dde3fd905a4b956f5e3efefebd4676812c1bfedea418` |
| `research_paper/data/simulation_motion_v3_reference_metadata.json` | `459f841c21c4c638fbc1fb4df2b21d9f4b2668ac0ea2793ee7f59146afa23f40` |
| `research_paper/data/simulation_random_layout_reference_metadata.json` | `f632a5b1f87060e5807ada2a34851bbcc3429a5b54d25366e35846fc0957abda` |
| `research_paper/configs/fastlio_simulation_bootstrap.yaml` | `b1f937855f08c1ff2cba66606d43cd65877869404e18807c4185f385404d0a67` |
| `research_paper/experiments/run_simulation_smoke.sh` | `a3465d33b85b7f0b0f59e444297c1b71447af1ee7aa3dd2773b33a0172ca3639` |
| `research_paper/experiments/src/simulate_lidar.py` | `897028bf99eb2b97e44088328991c745189f0df12a295e316440c2b49c747370` |
| `research_paper/experiments/src/write_simulation_bag.py` | `30013904c8956ce569538176c565491b49f1504781f29adc3d119fff79f62ba2` |
| `research_paper/experiments/src/audit_simulation_scene.py` | `1c51029c5c3e17e2dfe8eabaf6bcc729781bdf9b0ec3b21b6b2ce3ac00585b3b` |
| `research_paper/experiments/src/audit_paired_simulation_bags.py` | `14944d470c0d90bc0c5e0837bdf187c06c6f5ab6bef02fbebb0aeedca518c593` |
| `research_paper/experiments/src/audit_health_export.py` | `fff0e55b88e129e94f3808b88955d5f6213c8bfac98b25acc12f09e5f3a29ba8` |
| `research_paper/experiments/src/trajectory_eval.py` | `d505376135daf5395be9d338d471b57c0e6b1ebf86307672fcd238ffce5d3fba` |
| `research_paper/experiments/src/fastlio_information.py` | `f83d8d52f8fc5d1e39a4d2190de78f17fc7672c49c7f511fc203900e3f91ea1e` |
| `research_paper/experiments/src/summarize_simulation_bootstrap.py` | `19e803ab4a52e0855aac2a24d48ffa0c9f3cab29f1445454e35fc6c9103d3139` |
| `research_paper/experiments/src/summarize_simulation_seed_sensitivity.py` | `bf72f0eacd09eba6e90770c6424c0cde0eb1b7cf96656e313e720ae4330d89b4` |
| `research_paper/experiments/tests/test_simulate_lidar.py` | `816ce1a792d604369fe8c30af361b775055ec744a90cd29c260ef704be25503e` |
| `research_paper/experiments/tests/test_health_export_audit.py` | `7f0a05c5ee7734c0b4564768ecf927bbd89e35278da529d97a2fdd7e3da69f12` |
| `research_paper/experiments/tests/test_fastlio_information.py` | `1e5d7ef7f6f25d06037af53ee78d1c74d3fa3b19e4d8baef66212b9266da2b91` |
| `research_paper/experiments/tests/test_trajectory_eval.py` | `da05c6866a58fc8880cab179586ab0b15f9c0f6dbbc2fb8d5c65d18efe83627c` |
| `research_paper/experiments/patches/fast_lio_health_diagnostic.patch` | `ea9cb9a061eb42593a4944252bf92e5edc507086652ada602e19c7772ea320a2` |
| `research_paper/experiments/patches/fast_lio_pcl17.patch` | `6e60c082d6b39f5fb9f6adda43204aac170cf31f7ef9ec05764e89071fee5275` |
| `research_paper/evidence/SIMULATION_MOTION_V3.md` | `db072def2335336463864a5c74998315b03d275728c6619c90af0375d8aac2cb` |
| `research_paper/evidence/SIMULATION_RANDOM_LAYOUT_SMOKE.md` | `659d6e7a63de8382a6c7d4ab8604535450f734bd6d8353394e426fc84a89ff1c` |
| `research_paper/evidence/SIMULATION_SEED_SENSITIVITY.md` | `68bd7d59e28e7c61bd080af1687275affa1f49f2df21c5f38f7fb911f6a9221c` |
| `research_paper/evidence/HILTI_EXP18_T07_PILOT.md` | `27290102170124aa9b45c81d155e2476027c6a007cd08f38e5ca0a1b43982a01` |
| `research_paper/evidence/T08_FINAL_PATCH_AUDIT.md` | `01f3ed07ed07ad110ff8341d902ce6d13bd39a92032824fe3db511a68e16acab` |
| `research_paper/evidence/simulation_motion_v3_manifest.json` | `b66c36e72c5a7b31544652e87373b438f43bbd0e6d89db99b7ded77df82e9691` |
| `research_paper/evidence/simulation_random_layout_manifest.json` | `71bc00b4bde8b82adb08ead394ddbc8919a0b9f17250d3720af18a54c9e336a3` |
| `research_paper/evidence/simulation_seed_sensitivity_manifest.json` | `5f071e4c1e95b068087d6a1c8287ca1680a5e8e2deafe2c98fe20f8e38293be4` |
| `research_paper/evidence/randomized_layout_geometry_screen_dev14_45.json` | `1a7533d421e16d299ce9f1ea77860dcdea96abae5ab0ac43f6182a0b7b120b35` |

The seed-sensitivity manifest intentionally preserves the original generator
source hashes for seeds 10–13; its separate current-code check proves exact
seed-10 regeneration only. The randomized manifest's current-code check proves
exact seed-14 input/reference regeneration only. Neither asserts that the
current generator re-created every historical seed-11–13 run.
