# Hilti Exp18 development pilot analysis plan

Fixed 24 September 2026 after the scene interval was frozen, before summarizing T07 error distributions. Applies only to the first 55-second FAST-LIO development replay; it is not a final-test protocol or recovery-label rule.

## Inputs and outcomes

Use the frozen [scene event](../data/HILTI_EXP18_EVENT.md), the [qualified reference metadata](../data/hilti_exp18_reference_metadata.json), the original replay poses, and the offline evaluator. Report 1 s and 3 s local translation/rotation errors and their actual-duration rates. Use the explicit 25.0 s **pre-exit** alignment only for descriptive accumulated error; do not call it original pre-entry drift. Keep every invalid row and its reason. No error threshold, recovery time, false-reassurance claim or indicator operating point is selected in this pilot.

For transparent before/after context, classify each window by its **start** time relative to the first LiDAR header:

- `pre_scene`: `[26.0, 31.6)` s;
- `transition`: `[31.6, 33.6)` s;
- `matched_post_scene`: `[35.0, 40.6)` s (equal duration to `pre_scene`, leaving a buffer after the visual change);
- `other`: all remaining starts, retained in overall availability counts.

For each group and each window length, report planned row count, local-valid count, invalid reasons, median and 90th percentile among valid local translation and rotation errors, and median accumulated error only among alignment-valid rows. Do not pool adjacent scans as independent research replicates or use a frame-level significance test. Report the entire replay's availability separately. Reference gaps and window incompleteness remain missing—not zero, not failure-to-recover. The comparison is descriptive because it is one handheld recording with a map-registration-derived reference and one backend run. A genuine paper claim needs independent trajectories, matched-motion controls, a frozen indicator comparison, and an R1 novelty/validity review.
