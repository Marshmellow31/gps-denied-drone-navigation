# Continue after reinstalling Ubuntu

Prepared on 1 October 2026. GitHub saves the code and small research records.
It does not save the recordings, full run output or installed environments.

## What to back up separately

1. Copy the **whole** `GPS-Denied-Drone-Research` folder from the root of the
   Windows drive labelled **Acer** to another drive. On Linux its location is
   `/run/media/harshil/Acer/GPS-Denied-Drone-Research/`.
   In Windows, open the Acer drive and look directly in its root, not Downloads.
   The drive letter depends on Windows; it is not recorded here.
2. Preserve the complete Ubuntu project folder, including hidden and ignored
   files: `/home/harshil/Desktop/GPS Denied Drone navigation/`.
   In particular, `research_paper/experiments/generated/` contains about 4 GB
   of development inputs, outputs, reference files and local dependencies.
   These are excluded from GitHub. Windows normally cannot read this Ubuntu
   partition, so save this folder before formatting Ubuntu.

Prefer a Linux tar archive for the Ubuntu folder so symbolic links and file
permissions survive. A file-manager copy to Windows storage may not preserve
those details. Links to files outside the archive need their targets saved too.
Old reports mention temporary paths under `/tmp` and `/run/user/1000`; those
are not durable backups and some original bags may already be absent. Preserve
available retained evidence and disclose missing inputs rather than assuming
the complete old environment survives.

The Acer folder currently contains:

- `Hilti-Oxford-Exp18/exp18_corridor_lower_gallery_2.bag` (about 8.7 GB),
  its reference text and `lidar_calibration.yaml`.
- `Hilti-Oxford-Exp18/runs/`: the original failed Point-LIO attempt,
  successful retry `POINTLIO_INDICATOR_FEASIBILITY_20260929_R2`, FAST-LIO
  native seed-14 evidence and the exploratory Hilti run.
- `Hilti-Oxford-Exp18/fastlio_ws`, `fastlio_ws_r3_20260929`,
  `point_lio_ws_r2_20260929`, `point_lio_glog_20260929`, `ros_env` and other
  supporting files. Keep the entire parent folder to avoid guessing dependencies.

These locations were inspected on 1 October 2026. This guide is an inventory,
not proof that a second backup has been created. Check file counts and hashes
after making your backup. Do not format the Acer partition.

## What GitHub contains

The repository includes scripts, tests, native FAST-LIO/Point-LIO patches in
`research_paper/experiments/patches/`, configuration, dependency lock evidence,
protocols, small manifests, review reports and figures. The latest seed-14
verification JSON and runner repairs are included with this restoration guide.
Large data and local environments remain outside Git.

## Resume on the new Ubuntu installation

1. Clone `https://github.com/Marshmellow31/gps-denied-drone-navigation`.
2. Restore the ignored development files from the Ubuntu backup and mount Acer.
   Absolute links and recorded paths may need repair if the username or mount
   location changes; preserve the original manifests rather than rewriting them.
3. Read `CURRENT_HANDOFF.md`, `STATUS.md`, then
   `../AGENT_EXECUTION_PLAN.md`. The older `antigravity.md` and root scope
   summaries may describe the failed attempt; the newer handoff records the retry.
4. Use `ENVIRONMENT.md`, `../experiments/README.md`,
   `../evidence/ros_environment_explicit_lock.txt` and native replay/implementation
   reports to reconstruct dependencies and pinned estimator sources. Copied
   environments may need rebuilding; merely cloning GitHub is insufficient.
5. Verify restored file hashes against run manifests, rerun the relevant tests,
   and obtain independent acceptance of the retained Point-LIO feasibility pair
   before the 32-pair development replication.

The retry has local verification PASS. Independent one-seed acceptance is still
recorded as pending. Overall R3 is REVISE; held-out data remain sealed. No final
performance or publication conclusion follows from this backup.

The user currently assigns Codex review and next-instruction duties;
Antigravity handles implementation and experiment execution.
