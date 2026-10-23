# Literature addendum: OCE overlap

Updated 10 October 2026 after the version of record appeared on 9 October.
This addendum supplements the frozen R2 literature bundle; it does not edit or
change any artifact listed in `protocol/FREEZE.md`.

## Closest new work

Zhang et al., [“OCE: an optimization convergence metric for LiDAR SLAM
degeneracy detection”](https://doi.org/10.1007/s43684-026-00144-1),
*Autonomous Intelligent Systems* 6, 21 (2026), directly overlaps the proposed
recovery-reliability question. The article's version of record is dated
9 October 2026.

Its controlled Gazebo test uses synchronized ground-truth poses while moving
through non-degenerate, semi-degenerate, and fully degenerate geometry. The
pose-usability label is a ground-truth short-window axial relative-displacement
error over 0.5 seconds (Eq. 12), with its cutoff calibrated from a nominal
interval (Eq. 13). Detector alarms are compared frame by frame against those
labels; results include false-positive rate, recall, and the delay to first
alarm (Sections 4.2, Table 1). A hysteresis study reports premature state
switches and mean recovery delay (Table 3). The conventional translational
Hessian eigenvalue ratio is a comparator. This already covers health versus
ground-truth local-motion usability through geometry transitions, false
alarms, and recovery timing.

The controlled quantitative comparison is one continuous simulation sequence.
The paper also reports UAV wind-tower and tunnel runs, described behaviorally.
It does not report a fixed event-level rule transferred across multiple
held-out scene templates, sustained joint translation-and-rotation labels,
or replication across independently instrumented FAST-LIO and Point-LIO
measurement stages. Those are possible distinctions for this project, but
they are not by themselves a novelty verdict. The paper states that data are
available on request and that code will be released with a subsequent paper;
these access limits do not demonstrate novelty.

## Research consequence

Do not claim that local-motion accuracy, false alarms, transition evaluation,
or recovery delay are new contributions. The remaining candidate is an
external multi-scene transfer and cross-backend replication study using the
already frozen outcome and availability protocol. An independent reviewer
must decide whether this is sufficiently distinct and useful before any
held-out geometry is exposed. If it is not, revise the question and protocol
before screening; do not invent a distinction after seeing final outcomes.

This is a focused update, not a systematic search or independent novelty
review. The final result-dependent novelty audit remains outstanding.
