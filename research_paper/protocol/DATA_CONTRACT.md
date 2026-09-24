# Data contract for LiDAR recovery-reliability experiments

Version: provisional `0.1`, 22 September 2026. This contract governs T06–T09 development work. Numerical outcome rules remain provisional until T11/R2, but the units, transform direction, time representation, missing-data behavior, and truth isolation below are normative now.

**Dataset update (24 September 2026):** The GEODE-specific examples below describe the original development sequence. A [Hilti Exp18 replacement trial](../data/HILTI_EXP18_REPLAY.md), [frame audit](../data/HILTI_EXP18_FRAME_AUDIT.md), and [sequence metadata](../data/hilti_exp18_reference_metadata.json) now exist. Publisher conventions and an estimator-independent gyroscope check strongly support its `xyzw` world-from-IMU reference in the bag IMU axes for development. T07's evaluator boundaries were repaired; freeze or reject the Hilti scene event before formal errors. Do not carry over GEODE timestamps, frame assumptions or event anchors. Hilti reference gaps and map-registration dependence must remain explicit. See the [current handoff](../execution/CURRENT_HANDOFF.md).

## Conventions

### Transforms and frames

`T_A_B` is a homogeneous rigid transform that maps coordinates expressed in frame `B` into frame `A`:

```text
p_A = T_A_B p_B
T_A_C = T_A_B T_B_C
```

Every frame is right-handed. Positions and translations are metres. Rotations are proper `SO(3)` rotations. A pose row represents `T_parent_body(t)`: the declared body frame mapped into the declared parent/world frame. Neither a filename nor an upstream field name may be used to infer transform direction.

Quaternions use Hamilton convention and column order `qx,qy,qz,qw`. They represent the active rotation `R_parent_body` contained in `T_parent_body`. Writers must normalize finite quaternions and reject norms outside `[1 - 1e-5, 1 + 1e-5]` before normalization. Readers treat `q` and `-q` as the same rotation and enforce a consistent hemisphere before interpolation.

Evaluation requires estimator and reference poses for one declared **comparison body frame** `B`. A source pose in another body frame may be converted only using a versioned, direction-explicit static transform. For example, if an estimator emits `T_W_L` and the comparison body is the IMU, a verified `T_L_I` gives `T_W_I = T_W_L T_L_I`. The manifest must cite the transform source. If direction or body identity is unresolved, the comparison is unavailable; the evaluator must not guess or use an identity transform.

Estimator world `W` and reference world `G` may differ. They are related only by the single fixed alignment `T_G_W` defined in [METRICS.md](METRICS.md). Metric LIO scale is fixed at 1.0; no similarity transform or scale fit is permitted.

### Time

Canonical timestamps are signed integer nanoseconds in `timestamp_ns`. `clock_id` identifies the source clock, such as `geode_ros_header_unix`. Decimal text timestamps are parsed exactly as decimals and rounded once to the nearest integer nanosecond using round-half-to-even. Binary ROS `sec/nsec` fields are combined without floating-point conversion.

For a recording, `time_origin_ns` is the first valid LiDAR message header timestamp. `time_s = (timestamp_ns - time_origin_ns) / 1e9` is a derived display value only; joins use `timestamp_ns`. For `Urban_Tunnel01`, the origin is `1693022008716670513` ns (`1693022008.716670513` s). An adapter must preserve source timestamps; it must not estimate an offset, rescale time, or substitute receipt time silently.

All artifacts declare a clock. Streams with different clocks are not associated until a documented synchronization mapping is supplied in reference metadata. The current GEODE development sequence uses the released ROS/reference epoch timestamps directly; no additional offset is fitted in T05.

### Missing values

Unavailable is a first-class state, never numeric zero. Every row with `valid=false` has a non-empty `unavailable_reason`. Numeric quantities that do not exist are blank in CSV or `null` in JSON, not zero, infinity, or a sentinel. `NaN` may be used only inside transient numeric arrays and must become explicit null/unavailable state at an artifact boundary.

Required reason codes are:

- `REFERENCE_UNCOVERED`, `REFERENCE_GAP`, `REFERENCE_AMBIGUOUS`, `REFERENCE_BODY_UNKNOWN`;
- `POSE_MISSING`, `POSE_INVALID`, `POSE_RESET_BOUNDARY`, `POSE_CLOCK_UNMAPPED`;
- `INDICATOR_NOT_EMITTED`, `INDICATOR_INPUT_INVALID`, `INDICATOR_NUMERIC_FAILURE`;
- `WINDOW_INCOMPLETE`, `WINDOW_CROSSES_RESET`, `ALIGNMENT_UNAVAILABLE`;
- `RUN_CRASHED`, `RUN_TIMEOUT`, `NOT_APPLICABLE`, and `OTHER` with a free-text detail.

Do not drop invalid rows if doing so would hide a reset, outage, crash, or unavailable decision.

## Artifact interfaces

Small metadata artifacts are UTF-8 JSON or CSV with LF line endings. JSON files use schema version `lidar-recovery/0.1`. Bulk point clouds and ROS bags remain source artifacts referenced by hash; this contract does not duplicate them.

### 1. Run manifest — `manifest.json`

The manifest is written even for a failed run. It contains:

| Field | Requirement |
| --- | --- |
| `schema_version`, `run_id`, `sequence_id`, `role` | `role` is one of `development`, `final_test`, `control`, or `simulation`; it is immutable for the run. |
| `input` | Absolute or repository-relative path, byte size, SHA-256, topic/stream selection, dataset source URL/ID, and license status. |
| `code` | Repository commit, dirty boolean, machine-readable dirty diff hash when dirty, upstream backend name/revision, adapter revision, and submodule/container image digests if used. |
| `configuration` | Effective backend, sensor, extrinsic, replay, indicator, and evaluation configuration or content-addressed paths; record defaults after resolution. |
| `seed` | Integer for stochastic work; `null` plus `deterministic=true` when no seed applies. |
| `environment` | OS, architecture, CPU, RAM, relevant package/compiler/ROS versions, hostname pseudonym, and container identity. No credentials or personal paths beyond reproducibility needs. |
| `invocation` | Exact argv as an array, working directory, start/end UTC in RFC 3339, source `time_origin_ns`, wall runtime seconds, maximum observed RSS bytes and measurement method. |
| `status` | `planned`, `running`, `completed`, `failed`, or `partial`; exit code, warnings, failure stage/reason, processed time span, expected/output pose counts, reset count. |
| `outputs` | Paths, SHA-256 hashes, sizes, schemas, and row counts for pose, indicator, status/reset, log, evaluation, and figure artifacts that exist. Missing expected outputs remain listed with a reason. |

Configuration values containing transforms must repeat `parent_frame_id`, `child_frame_id`, units, quaternion order if applicable, direction, and provenance. The ambiguous upstream `T_IMU_LiDAR` key is not sufficient provenance by itself.

### 2. Pose stream — `poses.csv`

Required columns, in order:

```text
timestamp_ns,clock_id,parent_frame_id,body_frame_id,
x_m,y_m,z_m,qx,qy,qz,qw,valid,unavailable_reason,
segment_id,event
```

`event` is one of `POSE`, `RESET`, `START`, or `END`. `segment_id` is a non-negative integer that changes after each reset/reinitialization or declared output-frame discontinuity. A reset marker has `valid=false`, blank pose fields, and reason `POSE_RESET_BOUNDARY`. Pose timestamps must be nondecreasing; two valid poses with the same timestamp are invalid unless byte/numerically identical and explicitly deduplicated in the adapter log. Frame IDs are constant within a segment; changes require a new segment.

Both raw backend output and any canonical-body conversion are retained. A converted stream uses a distinct filename and manifest entry; it must never overwrite the raw stream.

### 3. Indicator stream — `indicators.csv`

Required scalar envelope columns are:

```text
timestamp_ns,clock_id,method_id,method_version,output_name,
value,unit,direction,valid,unavailable_reason,source_stage,segment_id
```

One timestamp may have multiple `output_name` rows or reference an additional versioned JSON object for vectors/eigenvalues. `direction` is `higher_is_healthier`, `lower_is_healthier`, or `component_only`. Raw values are preserved. Thresholds and binary decisions are separate evaluation configuration/output and never overwrite raw indicator values. `source_stage` identifies where the diagnostic was computed (for example, scan-to-map linearization before update). Indicator code receives online LiDAR/IMU/backend state only; it has no API parameter or file handle for reference poses, transition annotations, recovery labels, or evaluated errors.

### 4. Transition annotations — `data/transition_annotations.csv`

The current required columns are the 21 columns in the checked-in file: event/sequence/role; origin; entry/exit interval and nominal times in relative and epoch seconds; annotation method; scene evidence; reference coverage; independence flag; and status. Future writers should additionally retain integer-nanosecond values in a versioned successor rather than editing the current evidence row destructively.

An interval denotes annotation uncertainty, not an error tolerance. `entry_nominal` and `exit_nominal` are fixed scene anchors selected without viewing indicators or estimator error. Evaluators may report sensitivity across the predeclared boundary interval but must not move a boundary to improve an indicator result.

### 5. Reference metadata — `reference_metadata.json`

Required fields are:

- source artifact URL/ID/path/hash, format, column order, and collection system;
- `clock_id`, timestamp parsing rule, synchronization evidence, and any applied fixed mapping;
- original `parent_frame_id`, `body_frame_id`, transform direction, axis/datum, and comparison-body conversion with provenance;
- reference method, estimator-input independence, claimed instrument specification separately from demonstrated trajectory accuracy;
- position/orientation accuracy and covariance when published, otherwise `null` with limitations;
- ordered valid coverage segments `[start_ns,end_ns]`, excluded gaps, duplicate/out-of-order counts and resolution policy;
- calibration source/revision and every static transform used;
- known quality/fix flags, or an explicit statement that none were released.

For `Urban_Tunnel01`, frame/datum and exact body convention remain unresolved. A T06/T07 adapter may perform a clearly labeled provisional development comparison only after documenting the assumed reference body and testing transform alternatives; it cannot promote that assumption to verified metadata. R1 must audit this limitation.

### 6. Evaluation stream — `evaluation.csv`

Required columns are:

```text
event_id,run_id,timestamp_ns,window_s,window_end_ns,segment_id,
reference_valid,pose_valid,local_valid,local_translation_error_m,
local_rotation_error_rad,local_translation_error_rate_mps,
local_rotation_error_rate_radps,alignment_valid,
accumulated_translation_error_m,accumulated_rotation_error_rad,
recovery_label,indicator_method_id,indicator_output_name,
indicator_value,indicator_decision,evaluation_valid,unavailable_reason
```

`recovery_label` and `indicator_decision` are nullable until their development-only rules are frozen. Joining an indicator to an evaluation timestamp uses a separately recorded causal association rule; missing decisions remain unavailable. Summary tables must be reproducible from this row-level stream plus the manifest and frozen metrics configuration.

## Reference preparation and association

1. Parse source timestamps exactly and preserve original row number.
2. Partition by published/observed coverage gaps before sorting. Sorting is allowed only within an independently declared continuous coverage segment.
3. For equal timestamps, retain one pose only when position differs by at most `1e-9 m` and quaternion angular difference by at most `1e-9 rad`; otherwise mark the timestamp `REFERENCE_AMBIGUOUS`.
4. Normalize valid quaternions and make adjacent signs consistent within each segment.
5. At an estimator timestamp, interpolate translation linearly and rotation with shortest-arc SLERP only when the timestamp is bracketed by two valid reference samples in the same segment and their separation is at most `0.20 s` (provisional).
6. Do not extrapolate. Do not bridge a declared gap, invalid fix interval, reset, body-frame change, or segment boundary. Exact timestamp matches are valid without interpolation.

The provisional `0.20 s` maximum admits the measured 0.1703 s worst post-exit spacing in the development reference while rejecting its 0.771 s pre-entry hole and all long tunnel outages. T11 must reassess it using reference uncertainty and development evidence before protocol freeze.

Estimator output is evaluated at its own valid timestamps. A local window ends at the first valid pose in the same segment within `±0.05 s` of `t + tau` (provisional); ties choose the earlier pose. Both endpoint timestamps are independently associated to reference. The actual elapsed duration, not nominal `tau`, is stored and used for rate metrics.

## Reset, gap, and failure handling

- A relative-motion window cannot cross a pose `segment_id`, reset marker, reference segment, or invalid endpoint.
- The fixed pre-event alignment is never recomputed after a reset. If a backend preserves its original world frame, accumulated error continues and the discontinuity remains visible. If it silently changes world-frame semantics, accumulated error is unavailable from that point with a reason; it is not repaired by re-alignment.
- A crashed or timed-out run keeps its partial streams. All expected later timestamps are counted unavailable at summary level; a crash is not converted into non-recovery with a fabricated recovery time.
- Reference truth is read only by the offline evaluator. Backend and indicator processes receive the LiDAR/IMU subset and effective calibration only. File permissions/process separation are recommended in T06; at minimum, APIs and manifests must demonstrate this one-way boundary:

```text
LiDAR + IMU + calibration -> backend -> pose + online diagnostics
reference + annotations + pose + diagnostics -> offline evaluator
```

## Open items deliberately deferred

- Final local-error windows, quality tolerances, sustained-recovery duration, indicator operating points, and post-event horizon: T11.
- Verified GEODE comparison-body convention, transform direction, and point-time interpretation: T06/R1.
- Published-indicator vector formats and causal timestamp semantics: T08/T10.
- Final split assignments and test-data access controls: T11/R2.
