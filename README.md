# Can a drone tell when its location estimate is trustworthy again?

**A research project about navigation when GPS is unavailable.** We study whether a navigation program can tell when it has recovered after passing through a place that is difficult to map, such as a long, plain tunnel.

**Authors:** Harshil Patel, Daksha Lingampeta, Nisarg Vyas

**Status (23 September 2026):** Research in progress. We have not proved that a drone can navigate safely with this work.

## The idea in everyday language

Imagine walking through a tunnel whose walls look almost the same everywhere. If you can only look at the walls, it is hard to tell exactly how far you have walked. When you leave the tunnel, trees, buildings and corners give you better clues again.

A robot can have the same problem. It uses **LiDAR** (a sensor that measures distances with laser light) and an **IMU** (a sensor that measures movement and turning) to estimate where it is. Its estimate can become unreliable in a repetitive place. Even after it leaves, the program may keep giving an answer that looks confident but is wrong.

Our question is: **When useful surroundings return, can existing “health signals” correctly tell us whether the robot's movement estimate is accurate again?** We also want to know how often a signal says “all good” too early, and how long it takes to recognize real recovery.

This is a study of *how trustworthy a warning or recovery signal is*. We are not building a new drone, flight controller, or complete navigation system.

## How we plan to test it

1. Use public recordings of LiDAR and IMU data, plus carefully controlled computer simulations. No drone purchase or physical flight is needed.
2. Run an existing navigation program on the data. It estimates movement without using GPS or a camera.
3. Record its health signals and movement estimates. Compare them with an **independent reference**—a separate measurement of what actually happened—only after the run. The navigation program must not see that reference while it is working.
4. Look at the moment the robot leaves the difficult area. Count early “safe again” signals, late signals, missing answers and failures, not just successful cases.

There are two different questions: “Is the robot measuring its *new movement* correctly?” and “Does it know its *total position* correctly?” Good new measurements do not automatically erase mistakes made inside the tunnel. We will report those separately.

## What has happened so far

- We reviewed related research and inspected candidate public recordings. The exact new contribution still needs to pass a careful comparison with earlier papers.
- We ran an existing LiDAR navigation program, FAST-LIO2, twice on one development recording. Both runs finished, but their estimated movement was far from the movement shown by the recording's reference. **A finished run is not a successful result.**
- We built an offline comparison tool and its eight small tests pass. But the recording does not clearly identify the exact physical point whose position its reference tracks. Comparing positions as though that detail were known could give a misleading score. Therefore the real-data error scores are marked **unavailable**, not zero.
- We have **not** completed the recovery experiment, a final test, or a research paper with findings. We cannot yet say which health signal works best—or that any works reliably for a drone.

The next decision is whether to get a clear explanation of that recording's reference measurements or use a different recording with better documentation. We will keep the unsuccessful runs visible either way. See the [current task status](research_paper/execution/STATUS.md) for the detailed record.

## What this project does not claim

The public recording used so far was collected on a ground vehicle, **not a flying drone**. Computer simulation and a ground-vehicle recording cannot prove flight safety. This project does not command a real aircraft and does not include a camera, landing controller, or complete GPS-free navigation system. The older safe-landing prototype is separate and is kept in [`old_data/`](old_data/README.md).

## Where to read more

- [Research goal](research_paper/RESEARCH_GOAL.md) — the full question, boundaries and proposed measurements.
- [Execution plan](research_paper/AGENT_EXECUTION_PLAN.md) — the step-by-step research plan and review gates.
- [Current status](research_paper/execution/STATUS.md) — what is finished, paused or still planned.
- [Development experiment](research_paper/experiments/README.md) — technical setup, exact inputs and run records.
- [T07 handoff](research_paper/execution/handoffs/T07.md) — why trustworthy error scores are currently unavailable.
- [Paper folder](research_paper/paper/README.md) — the proposal abstract and build instructions; it is not a results paper yet.
