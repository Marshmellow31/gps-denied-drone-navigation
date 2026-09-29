**Gate:** REVISE

# Independent Point-LIO R2 amendment review — 29 September 2026

The proposed first-six-column signal, common-basis transport, frame pooling,
common `0.001` normalization and native-row DCReg adaptation are mathematically
defensible for the declared measurement-geometry question. The draft needs
the bounded contract repairs below before it becomes an accepted dated R2
amendment. This is a protocol review, not implementation or replication
acceptance. No adapter, Point-LIO replay, threshold fitting or held-out work
was performed.

## Exact input and source lineage

Reviewed draft SHA-256:
`ed634096bc43b088a0558bf1b1860796961676cf05dba26b19d02254bc1b4656`.
Both frozen reference files matched:

- `protocol/INDICATORS.md`:
  `510056955e3c9d7b943897da6c2533ab8cd8b870afdecd070de89db8fd2250e2`.
- `protocol/METRICS.md`:
  `06f5bf3950a3784fdd95c1eb6767dfec83ace8237e7d99a275f3ed13074d03cc`.

The source checkout is pinned to official Point-LIO revision
`4b86a469eb5572e70ed575af25b5f15dd06e8e3c`. All five requested source
hashes matched, and each file's bytes also matched `git show HEAD:<path>`:

| Pinned source | SHA-256 |
| --- | --- |
| `src/Estimator.cpp` | `6dc75bcafe1f989b7f0b1035484434d34f174452f1fec97a603edbc708e6e501` |
| `src/laserMapping.cpp` | `89d0207b6e11c6eeda8a3d05a4acf6253255d98418b8b9568e6488d1a08393a7` |
| `include/common_lib.h` | `01ff9df9a46c2315d9b3dca305c912768b3073149b4a428cc79fe074c77b67ff` |
| `include/IKFoM/IKFoM_toolkit/esekfom/esekfom.hpp` | `b019a724dbb94a77b725a37784263e642e9837ddd16ae03b05615da0558254fa` |
| `src/parameters.cpp` | `91428ddbcc7f754c4661c424925a843aea8804d9cb1080c65fede7652380e304` |

The checkout's compatibility-only worktree diff still hashes to
`7fc1a91619a310a1e4b44885e95f415f8af89f3885e54556ad14e2bca7668ce3`.
The T15 configuration and both compatibility-patch hashes match the source
audit note. Supplemental inspection covered `li_initialization.cpp`,
`IMU_Processing.cpp`, the SO3 `boxplus` implementation and the shared pose
logger to assess unavailable-frame and reset behavior.

## Accepted mathematical decisions

`h_model_output` constructs world-translation/right-body-rotation rows
`[n_W^T, (p_B × R_g^T n_W)^T]` with zero extrinsic columns under the frozen
fixed-extrinsic configuration. The SO3 update multiplies on the right. The
transport `J_rotation,world = J_rotation,body R_g^T` is correct; it equals
`(R_g p_B × n_W)^T`. Pooling those common-basis rows is a frame-pooled geometry
diagnostic, not the dynamic information/posterior of one scan-end state.

The pinned filter has `maximum_iter=1`. Its state changes between point-time
groups, while map insertion occurs after the frame. Counting each native
accepted group once is appropriate. The common `0.001` factor preserves the
declared geometric scale without changing the configured `0.01`. The draft
correctly records the pinned IKFoM branch-dependent treatment of `M_Noise` and
avoids claiming that division by `0.01` reproduces native posterior information.

Applying the frozen Schur detector to the raw common-basis Hessian is a
supported detector adaptation on Point-LIO's own rows. It must preserve the
block permutation, pseudoinverse/PSD tolerances, strict `kappa>10` and
unbounded-ratio serialization. It does not establish shared-correspondence
parity or reproduce the full DCReg registration solver.

Independent in-memory analytic checks confirmed the transport identity,
orthonormal world-frame invariance of the pooled/scaled spectrum, and that
changing only `0.001` to `0.01` divides every eigenvalue by ten. A call to the
frozen DCReg numerical routine confirmed that finite PSD singular geometry
with six accepted rows is valid/degenerate, whereas five rows is unavailable.
No sensor data or geometry layout was generated for these checks.

## Required draft repairs

### PL-R2-01 — Resolve singular and partial-frame validity contradictions

**High priority.** Draft acceptance item 2 (lines 132–134) says singular and
partial-group behavior is explicitly unavailable. That conflicts with both
the frozen comparator and the draft's lines 106–115.

Replace it with distinct expected outcomes: finite PSD rank-deficient geometry
with `N_frame>=6` remains a valid minimum-eigenvalue score, possibly zero, and
a valid DCReg `DEGENERATE` result with unbounded ratios. A completed frame
containing some ordinary zero-correspondence groups remains valid when total
accepted rows are at least six and no reset/numerical failure occurred. Those
groups contribute no rows and are counted separately. A native accepted group
may have fewer than six rows; apply the six-row minimum to the frame aggregate,
not each group. Insufficient total rows, non-finite/materially non-PSD results,
reset-crossing and incomplete processing are unavailable for their explicit
reasons. An incomplete/crashed execution remains a run failure as well.

### PL-R2-02 — Specify emission coverage and timestamps for skipped frames

**High priority.** The proposal promises one diagnostic per frame and an empty
frame barrier, but the pinned PointCloud2 callback only queues nonempty
preprocessed clouds (`li_initialization.cpp:90–96`), while IMU/map initialization
paths skip normal updates (`laserMapping.cpp:500–547`). An exporter only in
`h_model_output` or after the point-group loop cannot fulfill that promise.

Specify exactly one record for every scheduled/input LiDAR frame, including
startup, empty/fully filtered and map-initialization cases. Name their
unavailable reasons and the observation-only hooks that emit them. Define the
timestamp when no usable point exists: for the current fixed-rate synthetic
profile, a supported explicit choice is header start plus the configured
nominal 0.1 s period, with its nominal-timestamp provenance recorded. For normal
frames retain actual `lidar_end_time`, derived from the maximum available
per-point offset, without snapping it to evaluation ticks or reusing a stale
end time. Define incomplete-loop emission/retention separately from an ordinary
zero-correspondence group.

Correct lines 73–75 to say approximately 10 Hz frame-end records are associated
to the frozen 10 Hz decision grid; native scan-end timestamps need not coincide
with that grid. Retain group sub-times, processed/planned group counts and
one-to-one frame identities to verify completeness and uniqueness.

### PL-R2-03 — Pin the rotation snapshot and shared reset contract

**Medium priority.** Define `R_g` as the exact pre-update rotation used to build
that same group's accepted rows, captured before `x_.boxplus(dx_)`. A rotation
read after the successful update does not give the stated transport. Keep row
construction, transport and accumulation in float64 and require each accepted
row to be counted once.

Also define reset detection and shared pose/diagnostic segmentation, the
invalid barrier timestamp/reason, and which segment contains the affected
frame. The existing pose logger recognizes timestamp regression or frame-ID
changes; it does not observe arbitrary internal filter/map resets. The pinned
LiDAR/IMU callbacks return on regressing input timestamps without reliably
providing such a shared segment event, and the first `ImuProcess::Reset()` is
normal startup (`IMU_Processing.cpp:77–81`). Do not equate that startup message
with a later estimator reset. Specify an observable common reset boundary
without changing estimator state updates, and test that both streams invalidate
cross-boundary windows and clear the diagnostic accumulator consistently.

### PL-R2-04 — Make threshold extension and inherited outputs explicit

**Medium priority; no different selection objective is requested.** Explicitly
extend the full frozen deterministic rule to one global Point-LIO threshold:
seeds 14–45 corridor runs only, unique finite Point-LIO scores plus NO_ALARMS,
the same false-healthy constraint/objective, higher-threshold ties, and the
same zero-denominator/zero-sensitivity infeasibility outcomes. Controls and
fixed feasibility runs do not enter fitting. Apply the unchanged recovery
definitions to Point-LIO's own poses and reference, rather than copying
FAST-LIO recovery labels, threshold, event outcomes or caches. Neither Point-LIO
variance nor results may silently alter the already planned primary sample
size. Failed runs remain in their planned denominators/ledger under the frozen
failure policy.

Preserve the frozen `L=1,3,5 m` eigenvalue/scale-sensitivity exports, with 3 m
primary, or explicitly justify and review their omission as an amendment.
The current draft only specifies the 3 m output, while the frozen T08 contract
requires the two fixed sensitivity scales too. DCReg stays at `kappa_th=10`.
Keep a separate Point-LIO method/stage identity so the pooled adaptation cannot
be confused with the original FAST-LIO exporter.

## One-seed feasibility and subsequent batch gate

After these repairs are independently accepted and the dated amendment's
exact hashes are recorded, a bounded development-only sidecar and retained
seed-14 feasibility check may precede the 32-pair batch. That check should
establish analytic/source reconstruction, exporter on/off pose parity,
per-frame timestamps/coverage, reset/availability behavior and durable flush
and identity records. It performs no threshold selection; fitting remains in
the declared 32-pair development analysis. All feasibility attempts are
recorded and add no independent geometry event or training repeat.

The current REVISE draft authorizes neither adapter implementation nor a
Point-LIO replay. The full batch additionally requires the amended protocol
and the one-seed implementation checks to pass. The separate replication
development freeze and overall R3 acceptance still precede any held-out
exposure. This review creates no R2/R3 freeze and changes no code, draft,
protocol, status, README, existing R3 report or data.

---

# Independent second review — amendment v2 — 29 September 2026

**Gate:** PASS for the Point-LIO R2 measurement-adaptation specification.

This is the current protocol-review verdict for v2. The first review above
remains unchanged as historical evidence for the superseded first draft.
PASS does not establish implementation parity, authorize threshold fitting
from feasibility runs, pass overall R3, or permit held-out exposure.

## Exact reviewed version

V2 draft SHA-256:
`6504ba5d794ba45fd330041dd94fd06b7ebc8b40c69a5262970488b3ad55592c`.
The frozen `INDICATORS.md` and `METRICS.md` again matched the first review's
exact hashes. The source checkout again matched pinned Point-LIO commit
`4b86a469eb5572e70ed575af25b5f15dd06e8e3c`. The five measurement source
files listed above, plus `li_initialization.cpp`, `IMU_Processing.cpp` and
SO3 `SOn.hpp`, were rechecked against their committed upstream bytes; all
eight matched. No draft, source, configuration or data was changed.

## Closure of the four repair requirements

| Finding | Verdict and v2 evidence |
| --- | --- |
| PL-R2-01 | CLOSED. Finite PSD rank deficiency with at least six aggregate rows remains valid; zero minimum eigenvalues and unbounded DCReg ratios remain explicit degeneracy. Ordinary zero-row groups do not invalidate an otherwise complete finite frame. The six-row minimum applies to the frame, not each native group. Numerical/reset/incomplete cases retain distinct unavailable or run-failure states. Acceptance item 2 now tests these separate cases correctly. |
| PL-R2-02 | CLOSED with the implementation interpretations below. A callback ledger precedes empty-cloud filtering, carries a source-frame ID through the estimator, accounts for startup/map/empty/skipped frames, and checks exactly one diagnostic per input frame. Normal records retain actual `lidar_end_time`; unavailable frames without usable offsets have an explicitly marked nominal header-plus-0.1 s timestamp. Neither is snapped to decision ticks. Pending/missing frames and incomplete scheduled group processing are execution failures. |
| PL-R2-03 | CLOSED with the implementation interpretations below. V2 requires the exact pre-update rotation used for each group's accepted rows, transports rotation columns by `R_g^T`, records later reset events directly, distinguishes initial startup Reset, clears the aggregate, and joins pose/diagnostic segments using shared source-frame identity and timestamps. Forced-reset fixtures precede scientific runs; the sidecar changes no estimator state/covariance update. |
| PL-R2-04 | CLOSED. Point-LIO uses its own poses for unchanged recovery definitions, its own global development threshold on seeds 14–45 corridor primaries, and the full frozen candidate/objective/tie/infeasibility rule. Controls and feasibility attempts do not fit the threshold. FAST-LIO's threshold and primary sample size remain independent. L=1/3/5 exports are explicit, with 3 m primary, and DCReg remains fixed at kappa=10. |

The pooled formula and common `0.001` normalization require no correction.
They define a geometry diagnostic rather than native posterior information.
The raw common-basis Hessian is the appropriate input for the specified Schur
adaptation; the original method's settings and availability semantics remain.
Per-group capture is the single pre-update callback linearization, not a
relinearization at the final state. The world translation/world rotation
transport has the same declared geometry-score spectrum as any single common
orthonormal block-basis expression, while pooling remains a separately named
Point-LIO adaptation across evolving group states.

## Implementation interpretations that belong to the accepted contract

These resolve stage bookkeeping and join direction; they add no operating
threshold, estimator setting, numerical detector parameter or tuning choice.
Include them by reference to this review, or spell them out when promoting
the draft to the dated hash-recorded amendment:

1. `expected_group_count` counts native measurement-group updates scheduled
   for that frame's stage. A startup/map-initialization or callback-dropped
   empty frame schedules no measurement update and has expected/processed
   counts zero; its required unavailable diagnostic does not by itself make
   the run incomplete. For a measurement-stage frame, every native group,
   including a zero-correspondence group, is processed and accounted for.
   A skipped startup frame must not inherit a nonzero expected-update count
   merely because native code constructed `time_seq` before its initialization
   `continue`. Any raw geometric group count may be retained separately.
2. The pose join is directed from each **emitted pose row** to its unique
   diagnostic/frame-ledger entry. A missing/ambiguous identity, inconsistent
   timestamp or unmatched emitted pose is a contract failure. It does not
   require a pose for every unavailable startup/empty/reset frame. Preserve
   absent or invalid estimates as unavailable windows under the frozen R2
   outcome rules; diagnose actual logger/publisher truncation separately
   through flushed-count and lifecycle checks. Do not replace an absent pose
   with a fabricated state or silently label it recovered.
3. Capture `R_g` at the same callback evaluation as `h_x`, before the EKF's
   `boxplus`, and retain that snapshot through aggregation. Include an
   analytic fixture where the update changes orientation, so using the
   post-update rotation demonstrably fails reconstruction. Startup remains
   segment zero; a later reset has one shared explicit boundary, an invalid
   intersecting frame and consistent following-frame segments in both streams.

The normal frame timestamp is an actual source cutoff, not guaranteed to be
an exact 0.1 s decision tick. The source offset/header conventions and maximum
0.2 s diagnostic-age rule remain unchanged. The nominal fallback only stamps
unavailable records in this fixed-rate synthetic profile.

## Eligible next bounded work

After the accepted dated amendment and these review interpretations are
hash-recorded, the specified analytic/contract fixtures and a development-only
exporter may be implemented. The retained seed-14 sidecar-on/off feasibility
check may then precede the full 32-pair batch. It verifies source/row
reconstruction, exact pose parity, frame identity/timestamp coverage,
unavailable/forced-reset behavior and durable flush/provenance; it performs
no threshold fitting and contributes no additional geometry event.

The 32-pair development batch is eligible only after the amendment read-back
and one-seed implementation acceptance pass. Its own primary seed-14 run is
one of the 32 calibration geometry clusters; separately named seed-14
feasibility/repeat attempts are excluded from fitting and never become extra
independent events. Freeze Point-LIO's reviewed implementation, environment
and selected global threshold before held-out exposure. Overall R3 and the
replication development freeze remain separate, unfinished gates.

This second review performed source/hash read-back and protocol analysis
only. It ran no Point-LIO build/replay, threshold fit or held-out operation.
Only this append-only review section was written.

---

# Independent final review — accepted dated amendment — 29 September 2026

**Gate:** PASS for the accepted Point-LIO R2 measurement-adaptation
specification.

## Exact reviewed version

Accepted amendment:
[`POINTLIO_REPLICATION_AMENDMENT_20260929.md`](../protocol/POINTLIO_REPLICATION_AMENDMENT_20260929.md)

SHA-256:
`5c67330fe596e74a811b7e00202cef8d460a214bf4d6ff50e8ea10b86e9e4ed0`.

The technical body is byte-for-byte identical to the earlier
PASS-reviewed `e01a2c4b...` version; only the title/status and acceptance-gate
wording were updated. The amended wording keeps the required order: dated hash
read-back before implementation, analytic fixtures before the seed-14
feasibility replay, no threshold fitting from that replay, one-seed acceptance
before the 32-pair development batch, and overall R3 plus replication freeze
before any held-out exposure. The pinned Point-LIO source and the then-current
frozen `INDICATORS.md`/`METRICS.md` matched their audited identities. All eight
Point-LIO source files inspected for the amendment matched the pinned upstream
commit.

No remaining protocol ambiguity or over-authorization was found. This PASS
accepts only the measurement-adaptation specification; it does not accept an
implementation, establish indicator parity, authorize threshold fitting or
the 32-pair batch, pass overall R3, or permit held-out access. No files were
edited by the reviewer; no build/replay, fitting or held-out operation was
performed.

---

# Canonical-document consistency read-back — 29 September 2026

The cross-document check confirmed that the accepted amendment's formula,
separate Point-LIO score/threshold rule, and implementation gates are
consistent with the current `INDICATORS.md` SHA-256
`f9c72f12fae2c294b4e8372684df1dae3fa571c7d3905eb23b05d8b747409a4d` and final
`METRICS.md` SHA-256
`1d808cd1af24bb4390b70706f6a415878fe52fcad074a371223797bc56acf58b`.
FAST-LIO's formulas, outcomes, original threshold-selection procedure and
primary sample-size/uncertainty rules remain unchanged. The initial consistency
pass found a wording issue assigning a replication freeze to FAST-LIO; the
final read-back confirmed it is corrected: FAST-LIO locks at primary R3, while
Point-LIO locks with its separate replication development freeze, both before
held-out exposure. No other inconsistency remains. This review changed no
files and performed no implementation, replay, fitting or held-out operation.
