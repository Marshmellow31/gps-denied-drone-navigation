# Final held-out evaluation handoff

Updated: 27 September 2026. **Final evaluation is prepared but not executed.**
Do not run the screen or replay commands until both R3 artifacts explicitly
report PASS.

## Frozen evaluation size and selection

T16 calculated `n_test = 48` independent geometry pairs. This is 12 eligible
corridor/control pairs in each of the four fixed strata. The no-data plan is
[FINAL_HELDOUT_PLAN.json](../evidence/FINAL_HELDOUT_PLAN.json), SHA-256
`e6da5646243f95f8bae1befb39524ac58d660cd51491260f0f84d27c70ec501c`. It only
lists the already reserved seed ranges and explicitly records that no held-out
geometry or input was generated.

After R3 PASS, the scene-only screen examines each stratum's reserved IDs in
ascending order and keeps the first 12 that pass the frozen normal-axis
fractions. It writes every examined layout and rejection reason. If any
stratum cannot provide 12 eligible layouts, stop and return to R2; do not
borrow seeds from another stratum or inspect any LIO result to choose layouts.

## Exact commands

Use the same frozen ROS/FAST-LIO environment. These paths were verified while
preparing the handoff; the runner also checks the backend binary and frozen
source hashes before creating any held-out input.

First, the no-data plan can be regenerated (this command does not screen a
layout or create a bag):

```bash
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python \
  research_paper/experiments/src/final_evaluation_runner.py plan \
  --analysis research_paper/evidence/t16_development_analysis_manifest.json \
  --splits research_paper/data/SPLITS.csv \
  --output research_paper/experiments/generated/final_evaluation_plan.json
```

Only after the R3 review and implementation freeze both say `Gate: PASS`, run
the geometry-only screen:

```bash
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python \
  research_paper/experiments/src/final_evaluation_runner.py screen \
  --plan research_paper/evidence/FINAL_HELDOUT_PLAN.json \
  --r3-review research_paper/reviews/R3_IMPLEMENTATION.md \
  --implementation-freeze research_paper/protocol/IMPLEMENTATION_FREEZE.md \
  --output research_paper/experiments/generated/final_heldout_scene_screen.json
```

If that screen passes, run the paired FAST-LIO batch. Successful raw bags are
processed one geometry pair at a time and removed only after both scene
outputs and their manifests are verified; any failed pair's exact bags remain
for diagnosis.

```bash
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env/bin/python \
  research_paper/experiments/src/final_evaluation_runner.py run \
  --screen research_paper/experiments/generated/final_heldout_scene_screen.json \
  --analysis research_paper/evidence/t16_development_analysis_manifest.json \
  --r3-review research_paper/reviews/R3_IMPLEMENTATION.md \
  --implementation-freeze research_paper/protocol/IMPLEMENTATION_FREEZE.md \
  --ros-env /run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/ros_env \
  --workspace /tmp/fastlio-t13.XBDWGy/ws \
  --fastlio-binary /tmp/fastlio-t13.XBDWGy/ws/devel/.private/fast_lio/lib/fast_lio/fastlio_mapping \
  --scratch-root /tmp/gps-denied-heldout-scratch \
  --results-root research_paper/experiments/generated/final_heldout_v1 \
  --minimum-free-mb 1024
```

The R3 implementation-freeze document must copy the exact development-selected
FAST-LIO threshold `166.16366016039856` for `FASTLIO_MIN_EIG_G3`. The final
runner rejects a missing R3 PASS, a different threshold, a changed R2 split or
an incompatible backend/configuration. DCReg stays at its frozen
`kappa_th=10`; neither value may be tuned on held-out outcomes.

## Immutable implementation and protocol hashes

These values were read back while preparing the handoff. R3 must repeat the
read-back and include these values plus its own source/freezing records before
passing the gate.

| Artifact | SHA-256 / revision |
| --- | --- |
| Current R2 protocol freeze (after editorial D035) | See current freeze SHA-256 in [`CURRENT_HANDOFF.md`](CURRENT_HANDOFF.md); verify it again before any future gate. |
| Frozen metrics | `06f5bf3950a3784fdd95c1eb6767dfec83ace8237e7d99a275f3ed13074d03cc` |
| Reserved development/held-out split table | `d9d5496a55a2bb55cbf4a294be87df41ebb3b57ff24bdfd0e6fc0fcc8d682172` |
| FAST-LIO simulation configuration | `b1f937855f08c1ff2cba66606d43cd65877869404e18807c4185f385404d0a67` |
| FAST-LIO source revision | `7cc4175de6f8ba2edf34bab02a42195b141027e9` |
| FAST-LIO binary used by T14 | `4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792` |
| PCL17 / T08 / T13 backend patches | `6e60c082d6b39f5fb9f6adda43204aac170cf31f7ef9ec05764e89071fee5275` / `ea9cb9a061eb42593a4944252bf92e5edc507086652ada602e19c7772ea320a2` / `4e85cce23aae900e3cbee37f9871d40454fb3c1203a794a8db419475033a1ace` |
| T16 analysis implementation | `5a74d395cb606f6ba46b3789a4612fba1f5a2b7d10504920625ee989c6ed02eb` |
| Held-out geometry/input generator | `81804905abebf0ae4eaed7e16e52ae8cb0f6f72c9b4cfaf3b40dc7e565d6f811` |
| Final screen/replay runner | `3de7593bc74675c9b144b2646271a91806ae7222fb2e81296afadac4c6a4fd29` |
| DCReg / evaluator / replay script | `516e1da40c9cb8bc58e5a0e4c9c7964392a0877a77ba20e7139eae997783595e` / `d505376135daf5395be9d338d471b57c0e6b1ebf86307672fcd238ffce5d3fba` / `a3465d33b85b7f0b0f59e444297c1b71447af1ee7aa3dd2773b33a0172ca3639` |
| T16 analysis manifest / no-data plan | `1a716973445616ad0a09b207d50acd49dcfd8e3a87fac09c6d567726acc5b011` / `e6da5646243f95f8bae1befb39524ac58d660cd51491260f0f84d27c70ec501c` |

The current FAST-LIO workspace is session-local under `/tmp`. If it disappears,
rebuild from the pinned source and reviewed patches; do not proceed unless its
binary hash and the complete implementation-freeze record match. The runner
stops on a mismatch.

## Resource estimate and stop conditions

- A T14 60-second sensor bag is 80,742,421 bytes. Keeping both bags for all 48
  pairs would require about **7.22 GiB**. The runner uses one pair at a time
  (about **154 MiB** of raw bag data) and retains verified manifests/outputs,
  not every successful raw bag.
- T14 measured a mean of **71.63 seconds per scene replay**. The 96 final
  corridor/control scene replays therefore plan for about **1.91 hours**, plus
  geometry screening, bag generation and analysis. T14 outputs average about
  1.37 MB per scene; 96 scenes are expected to add roughly 132 MB before
  manifests.
- The runner checks at least 1 GiB free on scratch and result filesystems
  before each pair. Stop on insufficient space, input/reference hash mismatch,
  changed frozen source/configuration, incomplete scene coverage or a failed
  pair after its single technical retry.
- Keep every failed attempt and seed in the ledger. Never replace a failed
  seed. Any incomplete final sample makes confirmatory estimates descriptive
  only under the frozen protocol.
- After the 27 September safe cache cleanup, the Linux filesystem showed
  about 7.0 GB free. Recheck free space immediately before any future run; this
  value changes as the computer is used.
  The Acer NTFS partition is still mounted read-only, so the user's requested
  Downloads-folder move has not happened. If Acer is made writable, put scratch
  in a dedicated Downloads subfolder; otherwise the measured sequential
  scratch plan fits the current Linux free space, provided the runner's live
  checks continue to pass.

## Reproducibility status

The plan command was executed and verified. The screen and batch interfaces
compile and their R3 gate behavior is tested, but **they were intentionally
not run**: R3 has not passed, and no held-out layout was generated, screened or
replayed. The implementation is in
[`heldout_simulation.py`](../experiments/src/heldout_simulation.py) and
[`final_evaluation_runner.py`](../experiments/src/final_evaluation_runner.py);
R3 must audit these files, the patch hashes and the T16 manifest before
unlocking either command. After the final batch, a separate held-out analysis
must apply the locked threshold and frozen metrics without retuning.
