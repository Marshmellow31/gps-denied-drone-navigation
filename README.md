# Can a robot tell when it knows where it is again?

This is a research project about navigation when GPS is not available. We want to learn whether a robot can tell when its movement estimate has become reliable again after passing through a confusing place. The idea could help future GPS-denied drones, but **we have not tested a flying drone**.

**Authors:** Harshil Patel, Daksha Lingampeta, Nisarg Vyas

**Status (23 September 2026):** Early experiments. No proven recovery result or flight-safety claim yet.

## The problem, in simple words

Imagine walking through a long passage where every wall looks alike. It is hard to tell how far you have walked. When you reach a larger room with corners and objects, there are more clues. But seeing more clues does not magically erase a wrong guess you made in the passage.

A robot has a similar problem. It can use **LiDAR** (a laser distance sensor) and an **IMU** (a movement-and-turning sensor) to guess how it moved. We want to test the program's **health signal**: does it say “my movement estimate is good again” at the right time, or does it become confident too early?

We will keep two questions separate:

1. Is the robot measuring its **new movement** correctly now?
2. Is its **total position** still wrong because of earlier mistakes?

That difference is the heart of this research. We are testing existing warning signals, not building a new drone or a new complete navigation system.

## Pictures from the new recording

These are real LiDAR measurements from the **Hilti-Oxford Exp18** recording. The blue dot is the sensor. Dark marks show where the laser measured surfaces. Both pictures use the **same scale**, so the wider pattern on the right is not just a zoom effect.

![Two top-down LiDAR scans from the Hilti-Oxford Exp18 recording: most returns are close to the sensor at 25 seconds, while much more distant structure is visible at 40 seconds.](research_paper/figures/exp18_lidar_before_after.png)

This suggests that the surroundings change, but it does **not** prove that the position estimate has recovered. The possible change around 32–36 seconds still needs a careful scene check.

The next picture shows how much data we have. The laser and IMU recording lasts about 109 seconds. The published “answer key” path stops after about 87 seconds and has gaps. Our first trial used only the first 55 seconds. The gold band marks the possible scene change, **not** a measured recovery time.

![Timeline of the Hilti-Oxford Exp18 data: sensor measurements last about 109 seconds, the reference path has gaps and stops at about 87 seconds, and our first trial covers 55 seconds.](research_paper/figures/exp18_data_timeline.png)

The pictures are made from the downloaded recording; their [source, method and limits](research_paper/figures/README.md) are documented. Data credit: [Hilti-Oxford Dataset](https://hilti-challenge.com/dataset-2022), used under [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).

## What we have actually done

We ran an existing LiDAR-and-IMU navigation program, **FAST-LIO**, on the first 55 seconds of the new recording. It read 551 laser scans and produced 546 estimated positions without crashing. We then did one basic check: how far did it say the sensor moved over each time span?

| Time span in the recording | Program's movement | Published reference's movement |
| --- | ---: | ---: |
| 10–30 seconds | 7.82 m | 7.85 m |
| 30–50 seconds | 12.02 m | 11.94 m |
| 35–54 seconds | 9.47 m | 9.46 m |

The distances are close. That is **encouraging, but not a score for accuracy**. Two paths can have almost the same length while taking different turns or ending in different places. We have not yet checked the full path, turning error, or whether any health signal correctly detects recovery. See the [trial report](research_paper/data/HILTI_EXP18_REPLAY.md) for the exact numbers and limits.

Before this, we tried another public recording called GEODE. Its runs finished, but the movement estimates were clearly poor, and the reference path did not clearly identify the sensor frame needed for a fair comparison. We have kept those failures visible. Our offline comparison code now passes **12 small tests**, but passing code tests is not the same as proving the research idea.

## What still needs to happen

- Check that the new recording's reference path and the program's path describe the **same physical point and directions**. Only then can we calculate fair position-and-turning errors.
- Treat missing reference sections as **unknown**, never as “zero error.” The available reference was made partly using LiDAR data, so it is not a completely independent answer key.
- Mark the scene change carefully without looking at the program's mistakes or health signal, then test whether the signal announces recovery too early, too late, or not at all.
- Repeat the study on separate scenes and in controlled simulation before making a general conclusion.

No cameras were used by the navigation program. This new recording was collected with a **handheld sensor**, not a drone. Neither these data nor simulation can prove flight safety. The older, separate safe-landing prototype is kept in [`old_data/`](old_data/README.md).

## Read more

- [Research goal](research_paper/RESEARCH_GOAL.md) — the precise scientific question.
- [Current status](research_paper/execution/STATUS.md) — what is done and what remains.
- [New recording inspection](research_paper/data/HILTI_EXP18_INSPECTION.md) and [first trial](research_paper/data/HILTI_EXP18_REPLAY.md) — evidence behind this page.
- [Execution plan](research_paper/AGENT_EXECUTION_PLAN.md) — the next research steps and review gates.
- [Proposal manuscript](research_paper/paper/README.md) — not a results paper yet.
