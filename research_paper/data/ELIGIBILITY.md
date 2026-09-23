# Dataset eligibility for local-motion recovery evaluation

Audit date: 22 September 2026. This is a metadata audit for T03. No recording was downloaded and no test outcome was inspected. Properties are labelled **verified metadata**, **unknown until file inspection**, or **unsuitable**. Instrument specifications are not treated as demonstrated trajectory accuracy.

This is the original pre-replay ranking. After `Urban_Tunnel01` proved unusable for formal pose-error claims, a separate [replacement metadata audit](REPLACEMENT_AUDIT.md) and [actual Hilti Exp18 inspection](HILTI_EXP18_INSPECTION.md) were made on 23 September 2026. They do not retroactively change this T03 record.

## Decision summary

1. **Provisional development candidate: GEODE `Urban_Tunnel01` (`alpha`, vehicle).** It is the smallest listed urban-tunnel bag (3.2 GB), uses VLP-16 plus Xsens MTi-30, has claimed 6-DoF RTK/INS reference, and the official scenario description explicitly concerns tunnel entry/exit. T04 must verify actual topics, per-point time, calibration direction, reference columns/coverage, and a sufficiently long pre-event initialization segment before it is accepted.
2. **Alternatives: GEODE `Urban_Tunnel02` and `Urban_Tunnel03`.** They share the same sensor/platform/reference class and are 3.8 GB and 3.6 GB respectively. They are alternatives if `Urban_Tunnel01` lacks continuous reference around an exit or has incompatible streams. They are not independent validation evidence once inspected for development selection.
3. **Potential matched controls: GEODE `Flat_Surfaces_Smooth` and `Flat_Surfaces_Aggressive`.** They are small and have claimed Vicon 6-DoF truth, but contain no documented degenerate-to-rich geometry exit. They can be controls, not the real recovery transition required by T04/T09.
4. **NTNU tunnel/fog are unsuitable for the planned reference-labelled recovery metric.** They are the only verified aerial recordings in this audit and contain excellent transitions, but the official release/paper provides no continuous independent 6-DoF reference for either released bag. They may support qualitative scene evidence or an unsupported-estimator demonstration only; they cannot be used to fabricate ground truth.
5. **GEODE metro tunnels are unsuitable for full 6-DoF recovery.** Leica MS60 reference is position-only, so rotational recovery cannot be validated.
6. **GEODE `Stairs_Gamma` is unsuitable.** The authors explicitly state that a reliable ground-truth trajectory could not be generated. Alpha/beta stairs use PALoc map localization with unknown trajectory uncertainty and need separate scrutiny.

This choice narrows empirical platform claims: the provisional real transition is ground-vehicle data, not drone validation. Controlled simulation and the NTNU aerial scene context may still address aerial relevance, but no airborne-reference claim is supported by T03.

## NTNU LiDAR degeneracy release

Official sources: [dataset repository](https://github.com/ntnu-arl/lidar_degeneracy_datasets), [paper full text](https://arxiv.org/html/2403.05332), and public [Hugging Face files](https://huggingface.co/datasets/ntnu-arl/lidar_degeneracy_datasets), accessed 22 September 2026.

| Property | Status and evidence |
| --- | --- |
| Sequences | **Verified metadata:** `tunnel.bag` and `fog.bag`. |
| Platform | **Verified metadata:** manually flown aerial robot. |
| LiDAR | **Verified metadata:** Ouster OS0-128, 10 Hz, packet topics plus metadata. |
| Point timing | **Partly verified:** official paper says points are deskewed to a 10 Hz trigger/radar timestamp; repository says trigger-stamped LiDAR packet replay requires the linked driver. Exact packet profile/fields remain **unknown until file inspection**. |
| IMU | **Verified metadata:** VectorNav VN100 at 200 Hz. Exact recorded message type and acceleration/angular-rate units are **unknown until file inspection**. |
| Clock | **Verified metadata:** custom microcontroller triggers IMU/radar and supplies a 10 Hz LiDAR signal from a 1 ppm real-time clock; repository states IMU/radar header stamps originate from the triggering module. Absolute epoch and bag/header relationship remain unknown. |
| Extrinsics | **Verified metadata:** repository gives LiDAR translation `[-0.00171, 0.02149, 0.0358]` and quaternion `[x,y,z,w]=[0.000462,0.0008483,0.0028835,0.9999954]`, all with respect to IMU. |
| Download | **Verified metadata:** public Hugging Face files, 3.47 GB tunnel and 1.85 GB fog, with published SHA-256 hashes. No login was required to inspect file metadata. |
| License | **Verified metadata:** BSD-3-Clause in repository and dataset card. |
| Reference | **Unsuitable for planned metric:** paper reports motion-capture reference only for a separate arena experiment. Tunnel/fog results show estimator trajectories/return-to-start evidence, not an independently measured continuous 6-DoF reference for the released bags. |

Transition evidence is unusually strong: the tunnel starts at a non-self-similar rest area, traverses a long self-similar section, and lands at another non-self-similar rest area (paper Section IV-C); fog begins in a fog-filled narrow hall, exits to an open area where LiDAR works normally, and loops back (Section IV-D). Exact entry/exit times remain unknown without bag/video inspection. Reference inadequacy, not transition absence, rejects these as the primary quantitative recording.

## GEODE

Official sources: [project page and size table](https://thisparticle.github.io/geode/), [repository/data documentation](https://github.com/PengYu-Team/GEODE_dataset), and [paper full text](https://arxiv.org/html/2409.04961), accessed 22 September 2026. Repository revision inspected: `c6e930623d4fed450d7fc50e16e3ffe0288b692b`.

### Common sensing metadata

| Rig | Platform use | LiDAR | Point timing metadata | IMU | Calibration |
| --- | --- | --- | --- | --- | --- |
| `alpha` | handheld, UGV, sailboat, vehicle | Velodyne VLP-16, 10 Hz | Extracted point format includes `time` | Xsens MTi-30, 100 Hz | `cali/alpha_config.yaml` includes `T_IMU_LiDAR` |
| `beta` | handheld, UGV, sailboat | Ouster OS1-64, 10 Hz | Extracted point format includes `t`; separate sensor `metadata.json` link is advertised | Xsens MTi-30, 100 Hz; Ouster internal IMU also listed in paper | `cali/beta_config.yaml` includes `T_IMU_LiDAR` |
| `gamma` | handheld, UGV, sailboat | Livox Avia, 10 Hz | Published extracted format lists `[x,y,z,intensity,tag,line]` without per-point time; actual CustomMsg timing must be verified | Xsens MTi-30, 100 Hz; Livox BMI088 internal IMU also listed in paper | `cali/gamma_config.yaml` includes `T_IMU_LiDAR` |

All rigs use an FPGA synchronization module. The paper says GNSS TOD/PPS initializes outdoor synchronization and produces 1/10/100 Hz signals. Exact timestamp epoch, offset, jitter, and reference-clock relationship remain **unknown until actual-file inspection**.

The YAML files provide numeric extrinsics, but the key name alone is not a complete transform-direction convention. They also contain suspicious copied fields (`/os1_cloud_node1/points` and 16-channel resolution in all three rig files, duplicate camera-LiDAR keys in beta/gamma). T04/T06 must use actual bag topics and paper/driver semantics rather than blindly trusting these labels.

### Reference classes

| Families | Reference | Eligibility consequence |
| --- | --- | --- |
| Off-road, inland waterways, bridge, urban tunnel | CHCNAV CG610 RTK/INS, claimed 6-DoF; paper table lists 1 cm RTK accuracy | Potentially eligible. Accuracy is an instrument specification; actual fix status, covariance, outages, rate, and full interval coverage require T04. |
| Flat surfaces | Vicon, 6-DoF; paper table lists 1 mm system accuracy | Eligible as controls, but no documented recovery transition. |
| Shield/tunneling metro | Leica MS60 prism positions at 10 Hz; no attitudes | **Unsuitable for full rotational recovery.** Position-only reference cannot supply 6-DoF local error. |
| Stairs alpha/beta | PALoc trajectory against RTC360 map | Provisional/weak: estimator-derived reference with unknown trajectory uncertainty and independence. |
| Stairs gamma | PALoc could not produce reliable trajectory | **Unsuitable.** Map-only comparison cannot provide planned pose recovery. |

### Access and license

- The official page exposes a public Google Drive folder and sequence-level sizes. The link opens without presenting a documented login prerequisite, but actual automated download behavior remains for T04.
- The repository contains no `LICENSE` file and the project page/paper did not state dataset reuse terms in the inspected material. **License/reuse conditions are unknown.** T04 must not redistribute raw data and R1 must treat publication/release rights as unresolved until clarified.
- Current disk availability at T01 was 5.5 GiB. A 3.2 GB bag plus extracted data and a native ROS build may exceed safe local capacity. T04 must use a verified streaming/subset plan or obtain additional storage before download; it must not silently fill the system volume.

## Per-sequence audit

The machine-readable [inventory](inventory.csv) preserves all 64 official rows plus the two NTNU bags. Its `status` field is a metadata eligibility classification, not a performance ranking. Potential transition timestamps are deliberately `unknown_t04`; no interval was inferred from an indicator or error curve.

## Ranking for the exact question

| Rank | Sequence | Why | Blocking uncertainty |
| ---: | --- | --- | --- |
| 1 | GEODE `Urban_Tunnel01` | Explicit tunnel scenario, claimed 6-DoF RTK/INS, per-point time field, smallest of its family | Actual reference fields/coverage/fix quality; exact exit; 3.2 GB storage; dataset license; vehicle rather than aerial |
| 2 | GEODE `Urban_Tunnel03` | Same eligibility class, 3.6 GB | Same issues; larger |
| 3 | GEODE `Urban_Tunnel02` | Same eligibility class, 3.8 GB | Same issues; larger |
| 4 | GEODE `Bridge03` | Claimed 6-DoF RTK/INS and repetitive geometry, 3.4 GB | Official material does not explicitly confirm a usable weak-to-rich boundary; actual data needed |
| Control | GEODE `Flat_Surfaces_Smooth` | Smallest bag, Vicon 6-DoF reference | No documented recovery transition; handheld and Livox per-point timing requires verification |
| Rejected primary | NTNU `tunnel.bag` / `fog.bag` | Ideal aerial transitions and synchronized OS0-128/VN100 | No published continuous independent 6-DoF reference for these released bags |

## T04 entry criteria

Before accepting `Urban_Tunnel01`, T04 must verify, from actual files rather than README claims:

- available disk versus bag, extracted subset, build, and generated-output footprint;
- ROS version, topics, message definitions, rates, point time offsets, IMU units, and clock monotonicity;
- `T_IMU_LiDAR` transform direction and units;
- reference timestamp/pose format, quaternion order, frame, covariance/fix status, and continuous coverage across a candidate exit;
- a scene-evidence exit annotation independent of tested indicators and errors;
- a pre-event initialization segment long enough for FAST-LIO2;
- permitted research use or a documented unresolved license restriction.

Failure of any reference requirement rejects the sequence rather than substituting zero/estimated truth.
