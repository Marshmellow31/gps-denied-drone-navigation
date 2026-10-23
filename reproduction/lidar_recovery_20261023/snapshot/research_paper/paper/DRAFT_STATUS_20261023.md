# First manuscript draft — 23 October 2026

The current draft is [recovery_transfer_draft_20261023.tex](recovery_transfer_draft_20261023.tex). The September `main.tex` proposal and the preliminary methods draft are preserved as historical sources; neither is the current paper. This dated addendum does not alter any scientific freeze or historical status ledger.

The draft contains an abstract, introduction, related work, formal definitions, diagnostic methods, experimental design, primary results, exploratory failure analysis, discussion, limitations, conclusion, evidence-availability statement and ten primary references. The standalone timing diagram is conceptual, not a new experimental figure. The draft uses the already completed 48-geometry / 192-run evaluation; no new native run, threshold fitting or statistical reanalysis was performed.

## What remains beyond writing the manuscript

| Work | Why it matters | Required now or conditional? |
| --- | --- | --- |
| Scientific contribution review | Assess whether the observed fixed-policy transfer findings add enough beyond OCE/DCReg/ICA; internal software/accounting acceptance cannot decide publication novelty | Required before a submission-ready claim |
| Reproduction package | Inventory native builds, dependencies, configurations, scripts, raw/compact data, access conditions, licenses and portable paths; verify the exact package intended for release | Required; current clone alone lacks external raw streams/environments |
| Coauthor details and approval | Confirm author order, affiliations, corresponding author, actual contributions, funding/conflicts, AI assistance disclosure and final approval | Required before submission; no details should be invented |
| Venue selection | Match scope and evidence to current article requirements, format, anonymity, fees and deadlines | Required before final submission preparation; no venue selected |
| External scientific feedback and response | Have professor/domain feedback assess contribution, endpoint interpretation and comparison adequacy | Strongly recommended before submission; no external contact authorized or sent |
| A closer comparator | Could address a specific objection about the current adaptation's fairness or scientific value | Conditional on the claim/review; requires fidelity assessment and a dated protocol |
| Fresh controlled confirmation | Could test a width/visibility/measurement hypothesis suggested by exposed outcomes | Conditional; freeze hypothesis, controls and endpoints before fresh evaluation |
| Real-data recovery validation | Needed to support a real-world recovery claim | Conditional on expanding the present simulation claim; current Hilti/GEODE evidence is insufficient |

The existing planned simulation batch does not need repeating by default. Do not retune or add final cases to improve the existing results. Existing final scenes are exposed and cannot serve as untouched confirmation of new hypotheses.

## Editorial work remaining in the draft

1. Obtain scientific criticism of the candidate contribution and the new-declaration endpoint.
2. Refresh the full literature comparison, including the ALIVE-LIO v2 revision dated 13 October. This draft checks its primary abstract/metadata and makes only a broad framework claim; it does not claim a full new comparison of that revision.
3. Integrate print-readable plots and native timelines from the accepted figure sources; preserve existing figures/manifests. Add a dimensioned revised corridor/control schematic if useful.
4. Complete supplementary sensitivity/ROC/AP reporting, exact native build/configuration details, screening history, repeatability and the full event ledger. Do not imply those appendices already exist as a submission supplement.
5. Confirm all human details, artifact-release conditions and venue-specific disclosures.
6. Select a venue, format, review citations/claims, compile and visually check the final PDF.

## Draft provenance and checks

The evidence audit script [audit_draft_evidence_20261023.py](audit_draft_evidence_20261023.py) compares core numerical table rows with accepted compact analysis exports, recounts missed-declaration categories from the all-event CSV, validates citation keys and hashes the consumed evidence. Its JSON report is a manuscript consistency check, not an independent scientific review or a rerun of native evidence.

The main numerical sources are the [accepted results](../evidence/final_geometry_v2_results_20261012/RESULTS_REPORT.md), both final analysis JSONs, [exploratory failure report](../evidence/final_failure_analysis_20261012/FAILURE_ANALYSIS_REPORT.md), [claim map](../evidence/CLAIM_EVIDENCE_MAP_20261012.md), frozen metric/indicator rules and accepted geometry amendment. The manuscript narrows its scope to the documented screened simulation design.

Primary reference metadata was checked against publisher/arXiv pages on 23 October. The Point-LIO publisher record resolves the DOI and author/title details. OCE is explicitly identified as closest overlap. Ten citations are included; this is a first-draft bibliography rather than a completed systematic novelty review.

## Build

The document is standalone: bibliography, tables and timing diagram are contained in the source. Open the `.tex` file in Codex for its source editor and PDF preview. The built-in compiler was attempted first; on this host it failed to retrieve its TeX bundle. An official Tectonic 0.17.0 Linux binary was therefore downloaded to `/tmp/lidar-paper-compiler-20261023/tectonic` for local PDF export. That temporary binary is not part of the repository.

From repository root, with Tectonic available:

```bash
mkdir -p output/pdf
tectonic --keep-logs --outdir output/pdf research_paper/paper/recovery_transfer_draft_20261023.tex
python3 research_paper/paper/audit_draft_evidence_20261023.py
pdftoppm -r 100 -png output/pdf/recovery_transfer_draft_20261023.pdf tmp/pdfs/recovery_transfer_20261023/page
```

The first manuscript draft is a review artifact. A successful compilation or numeric consistency check does not make it ready for submission.

## Verification outcome

- Local Tectonic 0.17.0 export succeeded: **11 A4 pages** at `output/pdf/recovery_transfer_draft_20261023.pdf`.
- All rendered pages were visually inspected in contact sheets, with the failure table additionally checked at full-page size. No clipping or overlapping elements was observed. The final draft has no overfull-box, undefined-reference or missing-character diagnostics; minor underfull-box spacing warnings remain.
- The consistency audit passed all four primary result rows, all four interval rows, all four missed-declaration partitions and all ten citation keys. It reads the different FAST-LIO and Point-LIO export schemas explicitly.
- This task did not rerun the native experiments, recompute their scientific estimates or run the full experiment regression suite. Existing frozen protocols, native evidence, previous drafts and scientific results were preserved.
