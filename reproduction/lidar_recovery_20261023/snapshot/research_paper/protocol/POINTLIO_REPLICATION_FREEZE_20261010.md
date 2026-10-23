# Point-LIO development replication freeze

**Status:** Independently accepted for the separate Point-LIO replication
freeze. The immutable JSON retains `PROPOSED_FOR_INDEPENDENT_REVIEW` as the
submitted state; the acceptance is recorded in
[`POINTLIO_REPLICATION_FREEZE_REVIEW_20261010.md`](../reviews/POINTLIO_REPLICATION_FREEZE_REVIEW_20261010.md).
This does not pass overall R3 or authorize held-out work.

The machine-readable freeze is
[`POINTLIO_REPLICATION_FREEZE_20261010.json`](POINTLIO_REPLICATION_FREEZE_20261010.json),
SHA-256 `87f31c5febff860fe774eb4533a1be584f68b663f0125ea40dc18e85cc587621`.
It binds the accepted D050 amendment, Point-LIO native binary/config/source,
runtime and producer snapshot, all 64 development slots, the corrected
analysis and exhaustive candidate table, the independent development review,
the test log and development figure identity.

The selected global Point-LIO `G_3m` threshold is
`123.80876977779258`. Its candidate population contains every unique finite
valid raw score from the 32 formal corridor development events, plus
`NO_ALARMS`. It yields 21 detections among 27 Point-LIO truth-recovered events
and three initial false-healthy events among 32 events with a decision. The
fixed Point-LIO DCReg comparator retains strict `kappa > 10` and has no fitted
cutoff. Controls, feasibility runs and repeats did not enter threshold fitting.

For any later final replication, use Point-LIO's own segmented poses and the
frozen time association, debounce, reset, truth and relapse rules. Run it on
the same 48 geometry pairs selected for the primary FAST-LIO evaluation; do
not change the primary sample target from Point-LIO development outcomes.
Keep every technical attempt and unavailable output visible.

Overall R3 must pass before final geometry is generated or screened. A passing
screen and frozen input hashes are required before native final replay. This
Point-LIO freeze alone leaves the held-out gate closed.
