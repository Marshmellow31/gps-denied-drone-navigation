# LiDAR Localization Reliability for GNSS-Denied Navigation

A research project about **reliable localization after geometric degeneracy**, using public LiDAR/IMU recordings and controlled simulation. No physical hardware is required. The research contribution determines the scope.

**Authors:** Harshil Patel, Daksha Lingampeta, Nisarg Vyas

**Last reviewed:** 20 September 2026

> **Candidate question:** After weak geometric constraints end, how reliably do LiDAR health indicators identify the return of accurate local motion estimation?

[Research goal and weekly milestones](research_paper/RESEARCH_GOAL.md) · [Existing work and scope decision](research_paper/SCOPE_DECISION.md)

## Why we chose this

Reliable localization matters even when an estimator continues producing poses: those poses may no longer describe motion accurately. Studying how reliability returns after difficult geometry gives us a specific, testable question within GPS-denied navigation.

This scope supports a focused paper within the November timeline using existing algorithms, public recordings and controlled simulation. Our intended contribution is evidence about recovery indicators, rather than building an entire drone navigation system. The topic was selected for its research relevance; owning or purchasing a particular LiDAR is not required.

The exact research gap still needs verification against the closest papers. We will refine the question if their experiments already answer it.

## Current status

| Item | Status |
| --- | --- |
| Modality | LiDAR + IMU; camera proposal superseded |
| Research direction | Transition-focused recovery reliability study |
| Prior-work check | Targeted check complete; exact novelty not yet established |
| Primary literature | X-ICP, SuperLoc, AdaLIO, GEODE |
| Candidate backends | FAST-LIO2 and Point-LIO; not locally reproduced |
| Data and simulation | Candidate sources identified; reference/transition eligibility pending |
| Protocol and experiments | Not implemented or frozen |
| Manuscript | Proposal abstract only; no findings |
| Deadline | First week of November, with weekly professor reviews |
| Venue | Unselected; depends on evidence |

## What the question means

In a long, repetitive corridor, LiDAR may poorly constrain motion along the corridor. After the robot exits, new geometry may make current scan matching informative again. That does not necessarily correct old drift.

We will distinguish geometric localizability, accurate local motion, and accumulated pose error. The distinction itself is established reasoning; the candidate contribution is a rigorous comparison of indicator reliability during recovery, including false reassurances, delay and transfer to unseen scenes.

## Evidence flow

```mermaid
flowchart LR
    DATA[Public LiDAR + IMU recordings] --> LIO[Existing LIO backends]
    SIM[Controlled timed LiDAR + IMU simulation] --> LIO
    LIO --> IND[Published health indicators]
    LIO --> POSE[Pose + status + reset logs]
    IND --> EVAL[Recovery reliability evaluation]
    POSE --> EVAL
    GT[Independent reference] --> EVAL
    EVAL --> OUT[Tradeoffs + failure cases + paper]
```

Cameras, radar and GNSS are not estimator inputs. A reference system may supply evaluator truth if its accuracy and independence are documented. Recorded motion is fixed: replay is not adaptive-flight validation.

## Scope

One failure mechanism: geometric degeneracy and the transition out of it. One primary LIO backend plus a replication backend; compare a conventional indicator with a relevant published localizability/risk measure. One controlled geometry family plus eligible public recordings.

No new full navigation stack, hardware purchase, physical flight, embedded deployment, camera system or landing controller. Public aerial data are preferred for UAV claims; ground-platform evidence must be labeled accurately.

## Weekly plan

```mermaid
flowchart TD
    A[Week 1: Exact literature gap + one transition pilot] --> B{Useful and measurable?}
    B -- No --> C[Refine the question]
    C --> A
    B -- Yes --> D[Week 2: Freeze protocol and data splits]
    D --> E[Week 3: Reproduction + development experiments]
    E --> F[Week 4: Final evaluation and replication]
    F --> G[Week 5: Analysis and limitations]
    G --> H[Week 6: Manuscript + professor review]
```

The [goal](research_paper/RESEARCH_GOAL.md) gives dates from September 21 to November 1, with early-November revision time subject to the exact deadline.

## What we will measure

A **health indicator** is a signal intended to describe estimation quality or how strongly the observed geometry constrains motion. **Recovery** means sustained return to a prespecified level of local-motion accuracy, checked against an independent reference. The exact thresholds and durations remain open until the development pilot.

- False reassurance versus recovery-detection delay and indicator availability.
- Sustained local relative-error recovery, independently labeled.
- Accumulated original-frame drift, reported separately.
- Missing output, resets, crashes, non-recovery and backend repeatability.
- Transfer across held-out trajectories/scenes, with uncertainty by independent trajectory/event.

Do not call a local geometric indicator wrong merely because it does not correct historical global drift. Do not hide resets through post-event realignment. Thresholds, windows, scene splits and repetition counts are frozen after development pilots.

Planned figures: geometry-transition schematic, indicator/error/drift timeline, false-reassurance versus delay plot, and held-out comparisons with uncertainty.

## Immediate next step and open decisions

The first professor-review package should contain:

1. A comparison of the exact question with X-ICP, SuperLoc, AdaLIO and GEODE, including their experiments and limitations.
2. A shortlist of recorded sequences with trustworthy reference trajectories and a clear transition out of weak geometry.
3. One small transition pilot showing indicator values, local-motion error and accumulated drift on the same timeline.
4. A go/no-go decision: is the question both distinct from prior evidence and measurable with the available data?

Final dataset sequences, simulation model, indicator implementations, recovery thresholds, sample counts and venue are **not selected yet**. There are no research experiment commands or results to reproduce yet; current build instructions cover the LaTeX abstract only.

## What the paper will deliver

A verified problem statement, a reproducible evaluation protocol, comparisons of established indicators, results with uncertainty, and explained failure cases. We will write the methods and evidence incrementally, then revise the abstract and conclusions around the actual findings. A useful empirical contribution does not require inventing a new SLAM algorithm, and positive results are not assumed.

## Novelty and publication gate

Generic LiDAR degeneracy detection and robust fusion already exist. X-ICP, SuperLoc, AdaLIO and GEODE must be compared before making a contribution claim. [The scope decision](research_paper/SCOPE_DECISION.md) records what is known and what still needs verification.

Aim for a focused empirical paper. A predictable drift demonstration is insufficient. Strong-venue suitability requires a useful new finding and convincing validation; no acceptance guarantee is implied. A workshop paper may be non-archival and is not equivalent to an ICRA/IROS main-track paper.

## Files and maintenance

```text
research_paper/RESEARCH_GOAL.md       Current LiDAR goal and evaluation direction
research_paper/SCOPE_DECISION.md      Prior work and publication assessment
research_paper/PLAN_REVIEW.md         Historical broad-proposal review
research_paper/paper/main.tex         Proposal abstract
research_paper/paper/README.md        Build instructions
output/pdf/main.pdf                  Compiled abstract
old_data/                            Archived safe-landing prototype
```

[LaTeX/build instructions](research_paper/paper/README.md) · [Abstract PDF](output/pdf/main.pdf) · [Archived prototype](old_data/README.md)

Update status and link evidence at each professor-review milestone. Record rejected ideas, protocol changes and failures. Rewrite the abstract around findings when they exist.

User resources: 16 GB RAM/RTX 4060 laptop; this supports the work but does not define its scientific value. Old synthetic landing results are separate evidence. Run archived commands inside old_data, preserve its held-out seeds and boundaries, and keep this project independent of VERGE-CUAS.
