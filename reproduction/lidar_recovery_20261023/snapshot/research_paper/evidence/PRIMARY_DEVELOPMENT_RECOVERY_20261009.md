# Fresh primary development recovery

Date: 9 October 2026. Scope: **development evidence only**. All 64 primary
corridor/control slots and four prescribed same-input repeats completed with
new provenance. The original incomplete output folders and numerical reports
were not replaced. No held-out geometry or outcome was inspected.

## Execution and lineage

The [complete audit](primary_recovery_complete_audit_20261009.json) verifies
all 68 scheduled slots, current scientific input hashes, native completion,
execution identities, output hashes, analysis-adapter links and native manifest
lineage. There are 69 unique native attempts: 68 completed, one interrupted
seed37 corridor attempt retained before its successful technical retry.
The interrupted record's initial elapsed-time placeholder is unmeasured time,
not evidence that its runtime was zero. State-transition ledger counts are
reported separately from unique attempts. Repeated runs add no new scenes.

The exact restored native executable is the original T14 binary at
`4da32e8bed7756de1e4d41883f58c91f4fc954fd6f2b6f4d9b052e3568697792`.
Scientific input reconstruction matched all 192 recording/reference/metadata
hashes. Both the initial bounded native trial and cached resumption passed
independent review. A later restart reused 46 completed runs; it did not
silently overwrite the interrupted attempt or count a retry as another scene.

Among four historical key output files per primary run, 78/256 hashes match
and 178 differ. Evaluation run/event identifiers changed in the new lifecycle,
and backend repeatability can change numeric values. Hash differences alone
are not proof of numeric equivalence or regression. The fresh cohort is
reanalysed coherently under the unchanged frozen rules.

## Fresh analysis

The [new analysis manifest](primary_recovery_development_analysis_20261009.json)
and its CSVs are preserved separately from the September analysis. All 32
corridor labels are reference-eligible and recovered; one later relapsed.

| Development outcome | FAST-LIO minimum-eigenvalue policy | DCReg detector adaptation |
| --- | ---: | ---: |
| Truth-recovered corridor events | 32 | 32 |
| Recovery events detected | 13/32 | 30/32 |
| Initial false-healthy events among available eligible cases | 1/31 | 0/31 |
| Post-relapse conditional false-healthy rate | 0/1 | 1/1 |

The scalar operating point remains `166.16366016039856`, selected only from
the 32 formal corridor development events using the frozen rule. Controls
and repeat runs do not train it. Its sensitivity on the selection data is
`13/32 = 0.40625`, and its conditional initial false-healthy rate is
`1/31 = 0.0322580645`. These are fitting-data descriptions, not final estimates.

DCReg now detects 30/32 events versus 29/32 in the historical cohort. This
difference is disclosed; the report does not claim all outcomes reproduce
identically. The paired interior sample standard deviation is now
`0.2503454775041967 m`, versus the historical `0.2494728851 m`. Reapplying the
frozen sample-size rule retains `n_test = 48` (12 per fixed stratum).

## 10 October threshold-candidate correction

An independent review found that the earlier threshold sweep enumerated scores
associated to the 10 Hz decision grid instead of every finite valid raw
diagnostic score required by the frozen rule. One valid terminal frame per
corridor was omitted. The shared selector now includes those raw scores while
keeping alarm evaluation on the original 10 Hz grid. FAST-LIO's corrected
candidate table contains 19,104 unique scores plus `NO_ALARMS`; its selected
threshold and all event metrics remain unchanged. The corrected analysis
manifest, full candidate table and independent acceptance are linked in the
[10 October analysis report](DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md) and
[FAST-LIO acceptance review](../reviews/FASTLIO_DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md).
The original 9 October analysis remains preserved as historical evidence.

## All four declared repeats

The [new repeat audit](primary_recovery_repeatability_20261009.json) uses the
explicitly scheduled seed14 and seed45 repeats, with no historical smoke
substitution. All four compare the same input and execution fingerprints.
Whole-run aligned one-second translation-error maximum changes are:

| Repeated development slot | Largest aligned error change |
| --- | ---: |
| Seed14 corridor | 0 m |
| Seed14 control | 0.0218093780 m |
| Seed45 corridor | 0 m |
| Seed45 control | 0 m |

This is bounded repeatability evidence from two geometries, not a general
estimate of stochastic backend variability. The unchanged plotting script
exports PNG/PDF/SVG under `figures/primary_recovery_20261009/`; its manifest
binds the audit, plotting source, rendering environment and all six exports.

## Reproduction and remaining gates

Raw native attempts, analysis adapters, fresh CSVs and repeat-analysis data:

`/run/media/harshil/Acer/GPS-Denied-Drone-Research/Hilti-Oxford-Exp18/PRIMARY_DEVELOPMENT_RECOVERY_20261009/`

The paired scientific inputs and shared reference remain under
`.../restoration_20261009/`. Source commands are the reviewed
`recover_primary_development.py`, `audit_primary_recovery.py`, the
unchanged-default `t16_development_analysis.py`, and
`audit_t14_repeatability.py --repeat-policy declared_repeats`.

Independent full-cohort acceptance is recorded separately. Completing this
primary stage does not pass overall R3. Point-LIO's complete development
replication, separate operating-point selection/freeze, a ready reviewed
final workflow and full implementation review remain necessary before any
held-out scene exposure. Final analysis, supported claims, full manuscript
and professor/submission package remain open.
