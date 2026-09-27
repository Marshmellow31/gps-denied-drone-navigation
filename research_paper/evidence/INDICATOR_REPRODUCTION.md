# T13 — DCReg indicator implementation and reproduction

Updated: 27 September 2026. **T13 is DONE as an implementation and
reproducibility task.** This is not a recovery finding, threshold-selection
result, publication verdict, or final-test evaluation.

## What was implemented

The DCReg spectral detector is computed from the same scan-to-map Hessian FAST-LIO
already forms from accepted point-to-plane correspondences. The added
[`fast_lio_hessian_sidecar.patch`](../experiments/patches/fast_lio_hessian_sidecar.patch)
copies that 6×6 matrix, count, timestamp and validity into a sidecar CSV. The
Python implementation in
[`dcreg_schur.py`](../experiments/src/dcreg_schur.py) computes the rotational
and translational Schur spectra and their six direction ratios/flags. It does
not read reference poses, scene labels or trajectory errors.

The implementation follows the R2-frozen definitions in
[`INDICATORS.md`](../protocol/INDICATORS.md): it permutes FAST-LIO's
translation-first columns into DCReg's rotation-first order, uses float64,
forms both Schur complements, records unavailable cases, and flags only when
`kappa > 10`. The sidecar is additive; it does not feed back into mapping or
pose updates.

## Independent published-example check

The official DCReg repository was checked at pinned commit
[`8ce8451b15491a4bbe17cf85ab02a8bed6696861`](https://github.com/JokerJohn/DCReg/tree/8ce8451b15491a4bbe17cf85ab02a8bed6696861).
The new unit test reconstructs its `dcreg_minimal_example` Hessian from the
published basis and stiffness values and compares the resulting sorted Schur
eigenvalues and condition ratios with the official README's six-decimal
outputs:

| Quantity | Official example | Test result |
| --- | ---: | --- |
| Rotation Schur eigenvalues | 1.001796, 19.881966, 36.152505 | Within `5.1e-7` absolute tolerance |
| Translation Schur eigenvalues | 0.032394, 12.252030, 24.038714 | Within `5.1e-7` absolute tolerance |
| Rotation condition ratio | 36.087707 | Within `1e-5` |
| Translation condition ratio | 742.066396 | Within `1e-4` |

All **14 focused tests pass**, including isotropic, weak rotation/translation,
coupled subspaces, threshold equality, singular and non-PSD handling,
orthonormal basis changes, CSV serialization and the official example. The
formulation is the detector portion of DCReg's Schur method (paper Sections
4.2–4.4, Equations 18–21), not its full registration/PCG system.

## FAST-LIO integration reproduction

The development smoke used the seed-14 randomized corridor bag from T12. This
is a feasibility input with the earlier 9.25 s entry route, not the formal
T14 route. Its manifest says `truth_in_sensor_bag: false`; the replay receives
only `/sim/points` and `/sim/imu`.

| Artifact | Result |
| --- | --- |
| FAST-LIO source revision | `7cc4175de6f8ba2edf34bab02a42195b141027e9`, with the previously documented PCL/C++17 and T08 diagnostic changes plus the T13 sidecar patch |
| Input bag SHA-256 | `fd035425e6dde9470b9016de963fcc68ff3272b542cfeec7fab4836b8c00299a` |
| Input manifest SHA-256 | `564cad1c93898e74bea756c915c835d9ae406eacbe6f5e668d2791f8fc0afbec` |
| T13 detector source SHA-256 | `516e1da40c9cb8bc58e5a0e4c9c7964392a0877a77ba20e7139eae997783595e` |
| T13 sidecar patch SHA-256 | `4e85cce23aae900e3cbee37f9871d40454fb3c1203a794a8db419475033a1ace` |
| T13 test source SHA-256 | `18d43e2dd576043d40c226478d799e9acd056c94e428796661c562a3c3838c94` |
| Raw-Hessian sidecar | 600 timestamp rows; 597 valid, 3 unavailable; SHA-256 `d6c3ae778c4786be66861b60dcf10f65848cc358701b233d70bad4ad8bbf2b4d` |
| T13 output | 600 rows; 597 valid, 3 unavailable; SHA-256 `94cdbb12a1309d4be073f09c42ea2f353cb5a7378ce728fba2d69c0a7885ee2e` |
| T08 health output | 600 time groups; 597 valid; SHA-256 `3a931f5184f553063bbbac2df4dbd2d937a914d47cb7bbd22bbcf1264adb03e4` |

The T13 adapter matched T08's scale-3 eigenvalue export at every timestamp;
the maximum absolute eigenvalue difference was `3.64e-11` (the frozen audit
tolerances are `rtol=1e-8`, `atol=1e-8`). Timestamp sets, accepted counts,
validity and unavailable groups also matched exactly.

To isolate the sidecar's effect, the same bag was replayed with and without
the T13 patch in the same build workspace. The pose streams were byte-for-byte
identical (both SHA-256
`20a7a1443f41d7963cecb0c5b550e94d617991f69b8061ced5a61f90ad6c14e8`), as
were the T08 health exports (both SHA-256
`3a931f5184f553063bbbac2df4dbd2d937a914d47cb7bbd22bbcf1264adb03e4`). The
patched FAST-LIO package built successfully; compiler output included
third-party Boost deprecation and upstream CMake warnings.

## Reproduction commands

From the repository root, after preparing the ROS environment described in
[`experiments/README.md`](../experiments/README.md), create a fresh catkin
workspace. Start from the existing pinned FAST-LIO checkout with the PCL/C++17
and T08 patches already applied; apply the T13 patch only to a copy:

```bash
tmp_ws=$(mktemp -d /tmp/fastlio-t13-repro.XXXXXX)
mkdir -p "$tmp_ws/src"
cp -a research_paper/experiments/generated/upstream/FAST_LIO "$tmp_ws/src/fast_lio"
ln -s "$PWD/research_paper/experiments/ros/livox_ros_driver" "$tmp_ws/src/livox_ros_driver"
git -C "$tmp_ws/src/fast_lio" apply --check \
  "$PWD/research_paper/experiments/patches/fast_lio_hessian_sidecar.patch"
git -C "$tmp_ws/src/fast_lio" apply \
  "$PWD/research_paper/experiments/patches/fast_lio_hessian_sidecar.patch"
source "$ROS_ENV/etc/conda/activate.d/ros-noetic-catkin_activate.sh"
catkin build --workspace "$tmp_ws" fast_lio
```

Then replay the development-only sensor bag into a new output directory and
compute the comparator output:

```bash
research_paper/experiments/run_simulation_smoke.sh \
  "$ROS_ENV" "$tmp_ws" \
  research_paper/experiments/generated/simulation_bootstrap/sim-layout-dev14-v1/sensors.bag \
  research_paper/experiments/generated/runs/T13_reproduction

python3 research_paper/experiments/src/dcreg_schur.py \
  --hessian-csv research_paper/experiments/generated/runs/T13_reproduction/health.csv.hessian.csv \
  --health-csv research_paper/experiments/generated/runs/T13_reproduction/health.csv \
  --output-csv research_paper/experiments/generated/runs/T13_reproduction/dcreg.csv
```

The focused checks are `python3 -m unittest
research_paper.experiments.tests.test_dcreg_schur -v` and the full suite is
`python3 -m unittest discover -s research_paper/experiments/tests -v`.
Generated bags, builds and replay outputs stay ignored and must not be pushed
to Git.

## Limits and next step

This is a **shared-Hessian detector adaptation**, not a full DCReg implementation
or reproduction of DCReg's mapping, physical-axis labeling, preconditioner,
PCG solver or paper benchmarks. The Moore–Penrose treatment for singular
blocks is an explicitly declared adaptation; the inspected official code
returns unavailable when its LU blocks are not invertible. The T13 smoke does
not establish that either indicator predicts recovery, and its route is not
the formal profile. No threshold was fit, no held-out data were generated or
screened, and no recovery or publication conclusion is claimed.

**Next:** T14 implements the approved formal route starting at `x = -6 m`,
reruns the scene-only screen, regenerates the 32 development layouts under new
IDs, and executes only the permitted development runs and repeat pairs. Held-
out inputs remain barred until R3 passes.
