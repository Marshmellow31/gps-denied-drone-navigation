# IEEE revision checkpoint — 23 October 2026

The main paper and supporting material are written and compiled. The main paper is nine pages in IEEEtran conference format; the supplement is eleven pages, using IEEEtran in one column. The existing first draft, proposal, implementation freeze, scientific results and reproduction package are preserved.

Completed in this revision:

- Reframed the empirical contribution and updated the closest-work discussion using primary OCE, DCReg and ALIVE-LIO sources.
- Added five vector figures to the main paper: endpoint timing, matched geometry, operating points, geometry effects and two native example timelines.
- Added explicit elementary arguments for relative-motion frame invariance, the limits of a geometric Hessian as an error guarantee, and persistent health without a new transition. These are explanatory proofs, not new-theorem claims.
- Included exact backend YAML settings and build identities; all 64 revised-screen candidates; the original failed-screen history and unresolved historical digest; retained workflow failures; AUC/AP, tolerance and three-second rate sensitivity; development repeatability; all 192 policy-event rows and all 192 native receipts.
- Added reproducible document/asset build commands and source/output hashes. No estimator, geometry generation, threshold fitting or scientific bootstrap was run for the revision.

Validation:

- Both PDFs compile with Tectonic 0.17.0. No overfull content, missing glyphs or unresolved references/citations remain. Some ordinary underfull paragraph-spacing warnings remain in the two-column manuscript.
- All 20 final PDF pages were rendered and visually inspected for layout, figure placement and clipping. All fonts are embedded; body text uses the IEEEtran Times Roman default (Nimbus Roman implementation); figure text uses Times-compatible Liberation Serif TrueType.
- `audit_ieee.py`: PASS; primary counts/intervals, availability and miss counts match accepted exports; all referenced assets exist; 213 source hashes and 33 generated-asset hashes match; copied configurations/ledgers match.
- The portable reproduction package independently rechecked with `reproduce.py --verify-only`: 1,814 files verified. Existing `VALIDATION.json` records the earlier relocated offline reanalysis and 197-entry frozen implementation check; the current revision did not repeat full native estimation.

Remaining before submission:

1. Human authors/supervisor review the scientific argument, evidence limits and closest-work comparison.
2. Supply verified affiliations, corresponding-author details, contributions, funding/conflict statements and required AI-use disclosure.
3. Select a venue, check the exact template/page limit/anonymity requirements, and adapt this conference draft accordingly.
4. Assess whether the venue requires additional comparator or external-data evidence. The present claim is conditional on the screened simulation design; no real-world or flight-validation claim is made.

The paper is ready for that review. Formatting and transcription checks do not establish publication acceptance. The documents have not been submitted to a publication venue. Git synchronization is recorded in the repository history.
