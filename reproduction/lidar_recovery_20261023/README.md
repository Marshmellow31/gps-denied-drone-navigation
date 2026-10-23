# LiDAR recovery study: reproduction package

This package lets another researcher check the saved evidence, rebuild the final tables and figures, and recompute recovery labels and event diagnoses from the recorded pose and health streams. It works without the Acer drive after copying this whole folder. No drone, ROS installation or new native estimator replay is needed for these steps.

The study contains 48 simulated corridor/control geometry pairs and 192 completed native estimator runs across FAST-LIO and Point-LIO. These are controlled simulation results. This package does not establish a new detector, physical flight safety or publication novelty. Exploratory failure diagnosis remains distinct from confirmatory results.

## Start here

Use Python 3.12. The package was checked with Python 3.12.14 on Linux. Run these commands from this folder, replacing the example output path with a directory that does not already exist:

```bash
python3.12 -m venv ~/lidar-reproduction-env
~/lidar-reproduction-env/bin/python -m pip install -r requirements.txt
~/lidar-reproduction-env/bin/python -B reproduce.py --verify-only
~/lidar-reproduction-env/bin/python -B reproduce.py --output ~/lidar-reproduction-results --reanalyze-streams
```

The environment and output directory must be new. The program refuses to reuse an output directory or write inside the package. It never launches native estimators, generates new scenes, fits thresholds or changes original evidence. To rebuild just tables and figures, omit `--reanalyze-streams`.

For Linux x86-64 with Python 3.12, installation can also work without internet using the included wheels (Python itself must already be installed):

```bash
~/lidar-reproduction-env/bin/python -m pip install --no-index --find-links wheels -r requirements.txt
```

Expected output: four byte-identical CSV/Markdown reports, four primary figures, sixteen exploratory figures (overview plus fifteen timelines), six matching stream-analysis exports, and `REPRODUCTION_REPORT.json`. Compressed CSV files are compared after decompression because gzip creation timestamps differ. Primary-window translation/rotation errors allow only `1e-12` absolute/relative numerical tolerance; every other window field, event, label and decision tick must match exactly. The fresh pip environment differed from the historical native environment by at most approximately `7.1e-15` in those window-error values. PNG bytes can differ across plotting/font environments; the numerical inputs and source files are checked with SHA-256.

## What is included

| Item | Location | Purpose |
| --- | --- | --- |
| Current code, settings, protocols, reviews, patches and small evidence | `snapshot/` | Preserves repository layout and current file bytes |
| Exact source tree used for frozen stream reanalysis | `frozen_snapshot/` | Same tree, with one reviewed test file recovered from Git history |
| Draft manuscript and its status | `snapshot/research_paper/paper/` | Unpublished working draft, not scientific acceptance |
| Recorded pose, health, indicator and reference streams | `native_streams/` | Recompute final event diagnoses without replaying estimators |
| Exact Python plotting dependencies | `requirements.txt` | Separate from the historical ROS environment |
| Native ROS environment lock and restoration record | `snapshot/research_paper/evidence/ros_environment_explicit_lock.txt`, `restoration_environment_20261009.json` | Native runtime provenance |
| Original-path to package-path map | `path_map.json` | Explicitly relocates files while retaining original hashes |
| Package content hashes | `SHA256SUMS.json` | Detect missing or changed packaged files |
| Original source hashes | `ORIGINAL_FILES_SHA256.json` | Check that source files were preserved |
| Large external file inventory | `EXTERNAL_DATA_INVENTORY.json` | States which raw files are outside this package |
| Repository revision and inclusion record | `PROVENANCE.json` | Distinguishes committed files from draft additions |

The original scripts and scientific rules are unchanged. `reproduce.py` uses `frozen_snapshot/` and adds local path aliases in a new working copy of the plotting manifest, after checking every original source digest. For stream reanalysis it translates the native manifest location in memory; the original manifest bytes, source checks, implementation gate, compatibility gate and numerical routines remain unchanged. The original and adapted plotting manifests are both retained in the output.

Packaging found one real provenance mismatch: the current `test_t16_development_analysis.py` was changed by a later test commit, after the implementation freeze. The current file is retained in `snapshot/`. The exact reviewed version was recovered from Git history, checked against the original frozen SHA-256, and placed only in `frozen_snapshot/`. `FROZEN_SOURCE_RESTORATION.json` records both identities and the historical revision. No current project file or frozen record was edited, and no acceptance check was bypassed.

The source snapshot also retains historical proposals and development failures for context. For final conclusions use `snapshot/research_paper/evidence/final_geometry_v2_results_20261012/RESULTS_REPORT.md` and the dated result audit, rather than older handoff statements. `snapshot/old_data/` is an archived landing prototype and is outside this study's claim.

## Data access and full native replay

The portable package includes all 868 files referenced by the exploratory source manifest, including copies of the consumed external streams. It excludes large sensor bags, raw Jacobian sidecars, native binaries and installed ROS environments. Their locations and sizes are recorded in the external inventory. A missing SHA-256 in that inventory means the inventory records location and size only; it is not a content verification claim.

The final cohort is synthetic. The generators, fixed configuration, selected layouts and split plans are in the snapshot; no outside dataset account is needed for the portable reproduction command. The Hilti-Oxford recording was development-only and is not required for the final tables or this stream reanalysis. Its historical inspection records remain in the snapshot; its large bag and the installed native environment remain on the research drive.

The original final native archive was located at:

```text
/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/final_heldout_geometry_v2_20261012
```

To preserve that whole final archive on another disk with sufficient space, use the supplied non-destructive copier. Replace BOTH paths with the actual mounted data parent and a new destination:

```bash
python3 copy_external_data.py --source-parent /path/to/Hilti-Oxford-Exp18 --output /other/disk/new-final-native-copy
```

It copies the inventoried final files, materializes readable symlinks, verifies known historical hashes, and checks every copied file against a freshly computed source hash. It does not copy the entire research drive, development archive, installed environments or native source workspaces. It never deletes or overwrites files. Its output includes a separate copy receipt.

Re-running the estimators from sensor inputs is a further reproduction level and was not executed while packaging. It needs Linux, the pinned ROS environment, both upstream native source trees, the supplied patches, matching compiled binaries and sufficient scratch space. Start with the preserved `snapshot/research_paper/experiments/README.md`, `snapshot/research_paper/execution/RESTORE_AFTER_UBUNTU_REINSTALL.md`, the explicit lock, and the native run manifests. These are historical setup records; their absolute paths must be restored or explicitly adapted. A Python pip environment alone cannot run ROS replay.

The final runner interfaces can be inspected without executing a replay:

```bash
python -B snapshot/research_paper/experiments/src/final_evaluation_runner.py --help
python -B snapshot/research_paper/experiments/src/run_pointlio_final_replication.py --help
```

Retain the original reviewed protocol, thresholds, selected cohort, unsuccessful attempts, denominator rules and unavailable states. Use fresh replay outputs. Do not select a new favorable cohort or tune on the exposed final data and present that as independent confirmation.

## Sharing and limitations

The sibling `.tar.gz` is a portable copy of this folder. Check its adjacent SHA-256 before extracting it. `VALIDATION.json` records the actual packaging checks. This is a local reproduction artifact; it has not been uploaded, assigned a DOI or approved for publication.

Before public release, confirm author/supervisor approval and redistribution terms for upstream code and any third-party recordings. The source snapshot retains original licensing files; this package does not grant new rights to third-party work. Review embedded historical local paths before public distribution.
