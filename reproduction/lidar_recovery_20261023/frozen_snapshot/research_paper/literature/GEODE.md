# GEODE evidence note

## Source and target

Primary sources: Zhiqiang Chen et al., [“Heterogeneous LiDAR Dataset for Benchmarking Robust Localization in Diverse Degenerate Scenarios,” arXiv:2409.04961](https://arxiv.org/html/2409.04961), and the [official dataset repository](https://github.com/PengYu-Team/GEODE_dataset), accessed 22 September 2026.

GEODE targets dataset breadth and system-level localization benchmarking across geometrically degenerate environments, heterogeneous LiDARs, platforms, and motion patterns. It is not itself a health indicator.

## Data, degeneration mechanisms, and truth

- Section 4.1 covers off-road, inland waterways, metro tunnels, stairs, flat ground, urban tunnels, and bridges. It identifies weak/repetitive geometry, motion, dynamics, and sensor-specific fields of view as challenges.
- Section 3 describes three rigs: VLP-16 (`alpha`), OS1-64 (`beta`), and Livox Avia (`gamma`) with Xsens MTi-30 IMU and cameras; platforms include handheld, sailboat, and UGV. This is not an aerial dataset.
- Section 3.2 describes FPGA-assisted timing; Sections 3.3 and 4.3 document calibration and ROS topics/rates.
- Section 4.4 is critical: outdoor off-road/inland/bridge/urban-tunnel sequences use 6-DoF RTK-INS; flat ground uses Vicon 6-DoF; metro tunnels use Leica MS60 **position-only** tracking; stairs use PALoc against an RTC360 map, and the `gamma` stairs trajectory could not be generated reliably.
- The repository supplies calibration files and conversion/evaluation scripts, but per-sequence eligibility still requires T03 and actual-file inspection in T04.

## Evaluation relevant to the candidate question

- Section 5 benchmarks seven systems primarily with ATE and denotes breakdown or errors above 100 m.
- Section 5.2 discusses general robustness limitations, lack of adaptation, and lack of failure detection/recovery at a system level.
- The paper includes severe degenerate sequences and entry/exit language for urban tunnels, but it does not identify a transition-specific indicator study.

## Recovery, reassurance, delay, and transfer

- `recovery` appears in the system-capability taxonomy and Section 5.2.3, not as a quantitative local-motion recovery label.
- **Not found in inspected material:** independent geometry exit annotations; sustained local translation/rotation recovery; indicator false-reassurance/delay curves; decision availability; or fixed pre-event-alignment drift timelines.
- GEODE provides strong scene/sensor breadth for transfer research, but much of its benchmark aggregates ATE per sequence. Metro tunnel position-only truth cannot validate rotational recovery; stairs truth is algorithm-derived and absent for one device.

## Official-repository inspection

Repository `main` revision `c6e930623d4fed450d7fc50e16e3ffe0288b692b` (17 October 2025) was inspected. It contains the README, three rig calibration YAML files, transformation scripts, `rmse.py`, and a rosbag extractor submodule link. No recordings were downloaded in T02. The README independently repeats the position-only metro truth and missing `gamma` stairs trajectory caveats.

## Exact evidence locations

- Scope/contributions: Abstract and Section 1.
- Sensors/platforms/timing/calibration: Sections 3.1-3.3 and Tables 2-3.
- Scenarios: Section 4.1.
- Topics/files: Section 4.3 and Tables 4-5.
- Truth: Section 4.4 and Figure 8.
- Benchmark and failure taxonomy: Sections 5.1-5.3 and Table 6.
- Known issues: Section 6.
