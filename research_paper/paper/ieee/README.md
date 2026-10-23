# IEEE manuscript and supporting material — 23 October 2026

The current manuscript is `recovery_transfer_ieee.tex`; `recovery_transfer_supplement.tex` contains the supporting material. Compiled PDFs are in `output/pdf/ieee_20261023/` at repository root. The original first draft and proposal files are preserved.

The main paper uses the unmodified [IEEEtran class, version 1.8b](https://ctan.org/pkg/ieeetran), conference mode, US Letter, two columns and the class's 10-point Times Roman body font. The embedded font is Nimbus Roman, a Times-compatible implementation. Equations retain the class's default mathematical fonts. Vector figures embed Liberation Serif, a Times-compatible TrueType font. The supplement uses the same class and body font in one column for readable ledgers and complete configurations. No custom margin overrides are used. A chosen venue may require a different IEEE template, page limit, anonymity or copyright block; this is not yet a venue-approved submission.

## Build

With Tectonic 0.17.0 available:

```bash
python3 research_paper/paper/ieee/build_ieee.py --tectonic /absolute/path/to/tectonic
```

The compiler downloads its TeX packages on first use and can reuse its cache later. The verified class and compiler download identities are recorded in `support/tooling_provenance.json`; the compiler binary itself is not included. IEEEtran's license and attribution are retained inside `IEEEtran.cls`.

The generated assets and tables are included. To regenerate them from existing evidence, use a Python environment with NumPy and Matplotlib (tested: Python 3.12.14, NumPy 2.5.3, Matplotlib 3.11.2):

```bash
python research_paper/paper/ieee/build_assets.py
python research_paper/paper/ieee/build_ieee.py --tectonic /absolute/path/to/tectonic
python research_paper/paper/ieee/audit_ieee.py
```

The reproduction package includes matching Python wheels. Asset generation reads retained exports and run manifests; it never launches an estimator, generates a new layout, fits a threshold or reruns the scientific bootstrap. No external-drive mount is needed for these document builds. Rebuilding a PDF or figure can change creation metadata and byte hashes; numerical claims remain tied to source hashes.

## Contents

- Main paper: five vector figures, primary counts and intervals, paired geometry effects, representative timelines, mathematical explanations, related work and reproduction statement.
- Supplement: three elementary proofs; timing rules; complete native configuration files and identities; all 64 revised-screen candidates; preserved unsuccessful screen and workflow history; AUC/AP, tolerance and three-second rate sensitivity tables; development repeatability; every one of the 192 policy-event rows.
- `support/complete_native_run_ledger.csv`: all 192 native run receipts, including control scenes.
- `support/complete_diagnostic_event_ledger.csv`: all 192 policy-event rows at full precision.
- `support/complete_geometry_screen.csv`: all 64 candidate geometries, including ineligible/unused candidates.
- `support/asset_manifest.json`: exact source and generated asset identities.
- `audit_ieee.py`: checks counts, primary numerical transcription, copied ledgers/configurations, file references, hashes and clean compiler logs. Its report is `support/ieee_audit.json`.

The sampling unit remains 48 geometry pairs. Policy rows and overlapping windows must not be counted as independent geometries. Proofs explain endpoint distinctions; they do not establish the physical cause of the observed failures or constitute new theorems.

## Literature and format verification

The format was checked against the distributed IEEEtran class and [CTAN metadata](https://ctan.org/pkg/ieeetran). The bibliography uses numbered IEEE-style citations. Related-work wording was checked against the primary [OCE article](https://link.springer.com/article/10.1007/s43684-026-00144-1), [DCReg v3](https://arxiv.org/html/2509.06285v3), and [ALIVE-LIO v2](https://arxiv.org/html/2604.02706v2). OCE already examines usability, false alarms and recovery; ALIVE-LIO examines temporal switching. The paper claims a bounded empirical transfer study, not invention of those concerns.

## Before submission

Human authors must check the manuscript, confirm names/order, supply affiliations/contact details, author contributions, funding/conflict declarations and any required AI-use disclosure. Select a venue, follow its exact instructions, and obtain supervisor/scientific review of the contribution and comparator fidelity. Publication acceptance cannot be established by these formatting or transcription checks.
