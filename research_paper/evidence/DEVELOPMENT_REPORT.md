# T16 — Development analysis report

Updated: 27 September 2026. **T16 is complete for development analysis and
handoff preparation only.** No held-out layout was generated or screened, no
final-test replay was run, and no publication or real-world claim follows from
these results.

## Plain-language result

We replayed the same 32 synthetic corridor/control pairs through FAST-LIO and
asked two questions: did the trajectory become accurate again by the agreed
rule, and did each online health signal say “healthy” at the right time?
According to the frozen motion rule, **all 32 corridor runs recovered**. The
fixed DCReg comparison marked 29 of those 32 recoveries, while the fitted
FAST-LIO minimum-eigenvalue threshold marked 13. That threshold also produced
one premature “healthy” event among the 31 events with an available decision
in the initial unrecovered interval.

These are development-only numbers. The FAST-LIO threshold was selected and
scored on the same 32 events, so its result is optimistic until checked on
untouched data. The 32 runs also share one simulated route and idealized sensor
assumptions; they are not 32 physical drone flights.

## Inputs and verification

- 32 randomized development geometry clusters, seeds 14–45; each has one
  corridor run and its matched feature-rich control (64 primary replays).
- All 64 primary run manifests were checked against their **768 listed output
  file hashes** before analysis. The T14 batch audit reports every primary
  completed and confirms that held-out data were not opened.
- Every corridor event had full analytic-reference coverage for the required
  post-exit windows. T16 built primary windows on the frozen integer-second
  grid, associated each boundary to the nearest pose within 50 ms (ties to the
  earlier pose), and used the same pose at adjacent boundaries.
- The 1-second recovery rule is the frozen three consecutive windows, each
  with translation error at most 0.20 m and rotation error at most 5 degrees;
  all three must finish within 20 seconds after exit.
- Health decisions use the frozen 0.1-second tick, 0.2-second record-age
  limit, invalid-record barrier and three-distinct-record debounce. The
  conventional FAST-LIO threshold search uses corridor runs only; controls
  are excluded from tuning. DCReg keeps its fixed `kappa_th=10` rule.
- The analysis ran in the frozen Python 3.12.14 / NumPy 2.5.3 environment.
  Machine-readable provenance and event outputs are in the
  [T16 manifest](t16_development_analysis_manifest.json); compact CSVs,
  including all 19,073 FAST-LIO threshold candidates, are in the ignored
  `experiments/generated/t16_analysis_v1/` folder.

## Frozen-rule outcomes

| Outcome | Development result |
| --- | ---: |
| Corridor truth-label coverage | 32/32; no missing reference endpoints |
| Recovered under primary 1-second rule | 32/32 (100%; descriptive Wilson 95% interval 89.3–100%) |
| Non-recoveries by `exit + 20 s` | 0/32 |
| Relapses after the first recovery | 1/32; seed 24, at 30.9997 s |
| Recovered with half-size error limits | 32/32 |
| Recovered with double-size error limits | 32/32 |
| Primary corridor/control runs completed | 64/64 |

The median truth-recovery onset was 26.0 s after the simulation clock began;
the median confirmation endpoint was 29.0 s. Those times vary with each
randomized corridor's exit. The lone relapse remains a relapse; it does not
move the first recovery onset.

## Online-signal comparison

The development-only FAST-LIO threshold selected by the frozen rule was
`G_3m >= 166.16366016039856`. Its conditional false-healthy rate was 1/31
(3.2%; descriptive Wilson interval 0.6–16.2%), below the frozen 10% ceiling.
It detected 13/32 truth-recovered events (40.6%), with 0.90 s median delay
among those detections. This value is only a **candidate to review and lock at
R3**; it is not a final operating setting.

| Signal and rule | False-healthy events | Recovery detections | Median delay when detected | Availability in event horizon |
| --- | ---: | ---: | ---: | ---: |
| FAST-LIO minimum eigenvalue, selected development threshold | 1/31 available events | 13/32 recovered events | 0.90 s | 100% |
| DCReg Schur mask, fixed `kappa_th=10` | 0/31 available events | 29/32 recovered events | 3.80 s | 100% |

The event denominator is conditional on at least one available decision during
the initial unrecovered interval; 31 of 32 events had such a tick. DCReg had
no premature healthy declaration in that initial interval, but it remained
healthy after the one observed relapse (1/1 relapsed events). FAST-LIO's
selected threshold did not remain healthy after that relapse. This is a
development observation, not evidence that either signal will behave the same
on new layouts.

The time-point curves were weighted so each geometry event contributed total
weight one. Development ROC-AUC / average precision were 0.864 / 0.985 for
FAST-LIO and 0.786 / 0.972 for DCReg. These curves are class-imbalanced: their
event-weighted tick labels contain positive weight 29.67 and negative weight
2.33 because most runs recover soon after exit. They are descriptive, not
independent-frame evidence or final performance estimates.

On the 3-second rate sensitivity check, 5,440/5,440 valid post-exit windows
were available in each scene type. The equal-event mean pass fraction was
98.7% for corridors and 98.1% for controls. These windows overlap and do not
create new independent samples or recovery labels.

Controls had 99.3% mean diagnostic availability. The mean fraction of
available control ticks marked raw-healthy was 18.1% for the selected FAST-LIO
threshold and 34.4% for DCReg; after the debounce state machine, the
corresponding confirmed-healthy fractions were 16.4% and 31.3%. Controls have
no recovery onset and are reported as healthy-scene context only.

## Development variance and held-out count

For each of the 32 geometry seeds, T16 used the frozen interior windows and
calculated the corridor median 1-second translation error minus its paired
control median. All 32 pairs had at least five planned interior windows, all
valid in both scenes, so the frozen sample-size calculation was permitted.

| Quantity | Value |
| --- | ---: |
| Sample standard deviation of 32 paired differences, `s_dev` | 0.2495 m |
| Unrounded continuous-outcome count | 24 geometry pairs |
| Count rounded to a multiple of four | 24 |
| Required final count, `max(48, 24)` | **48 geometry pairs** |
| Per-stratum count | **12 pairs in each of four strata** |

The equal-stratum candidate ranges are already fixed in `data/SPLITS.csv`:
100–119 short/narrow, 120–139 short/wide, 140–159 long/narrow and 160–179
long/wide. The no-data
[final evaluation plan](FINAL_HELDOUT_PLAN.json) lists them for the later
scene-only screen; it does **not** say which layouts pass and contains no
generated geometry or sensor input.

## Repeats, failures and limitations

- T14's 64 primary corridor/control run slots all completed. Of the four
  scheduled backend repeat slots, the two seed-45 repeats completed. Both
  scheduled seed-14 repeats and their allowed technical retries failed during
  the earlier `/tmp` quota incident. The earlier exact-input smoke pair is
  disclosed in the T14 audit; its corridor measurement streams matched, but
  its control streams differed. R3 must adjudicate that repeat substitution
  and repeatability before final testing.
- The T14 attempt ledger retains 66 `COMPLETED`, 4 `CRASHED` and 4
  `INVALID_INPUT` records. No failed attempt was recoded as non-recovery or
  replaced with a new geometry.
- The only fitted scientific value is the one global FAST-LIO threshold above.
  Its development performance is measured on its own selection events.
- The reference is analytic simulation truth, not a physical tracking sensor.
  Geometry is axis-aligned, clocks/extrinsics are ideal, and simulated noise
  settings are uncalibrated stress values.
- T15's Point-LIO smoke confirms a shared pose-file path only. It did not
  establish Point-LIO equivalents for the FAST-LIO health indicators and is
  not mixed into these FAST-LIO results.
- This study does not establish flight safety, transfer to different scene
  topologies, or publication novelty.

## R3 repair evidence update — 27 September

The repaired analyzer was rerun in a new output folder,
`experiments/generated/t16_analysis_r3_v2/`, using Python 3.12.14 / NumPy 2.5.3.
It reverified the 64 primary outputs. The selected candidate threshold,
32/32 recovery count, one relapse, signal event counts and 48-pair sample-size
target reproduce. The prior manifest and no-data plan are preserved under
`evidence/archive/`; the canonical manifest and plan now identify the rerun.
The removed censoring-duration median is not presented as a survival median.

The new [repeatability audit](T14_REPEATABILITY_AUDIT.md) quantifies all four
retained repeats. Corridor recovery labels and event-detection booleans agree
for these two repeated layouts, but scores, full-run warning states and some
detection delays vary. Substitution sensitivity leaves the 48-pair target
unchanged. Repeats remain outside threshold training and the independent
event count. The saved figures include PNG, PDF and SVG exports. R3 has not
yet re-reviewed this update, and no held-out geometry has been opened.

## Next gate after these repairs

R3 must inspect this report, the T16 machine manifest, the T14 repeat
reconciliation, the Point-LIO limitation and all implementation/source hashes.
Only after R3 PASS may the final runner screen reserved layouts and run the 48
held-out geometry pairs. The
[final-evaluation handoff](../execution/FINAL_EVALUATION_HANDOFF.md) contains
the exact gated commands, time/storage estimate and stop rules. **No held-out
screen or final batch has been run.**
