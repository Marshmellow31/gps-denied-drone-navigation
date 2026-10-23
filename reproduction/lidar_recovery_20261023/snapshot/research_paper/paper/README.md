# Manuscript

Current scope: LiDAR recovery-indicator reliability. The earlier visual-degradation abstract has been superseded following the user's LiDAR preference. Novelty is provisional; see the scope decision before developing the manuscript.

As of 23 September 2026, the Hilti Exp18 replay is only a development smoke test; there is no measured recovery or final-test result to write up. Use the [current handoff](../execution/CURRENT_HANDOFF.md) and [status ledger](../execution/STATUS.md) for the evidence gate before adding results.

`main.tex` is a venue-neutral LaTeX article template. It contains the authors in the requested order and only a provisional abstract as manuscript content. Affiliations have not been supplied. Future sections are commented scaffolding, so no empty sections appear in the PDF. The proposal abstract must be rewritten around actual findings before submission.

From the repository root, compile using a LaTeX installation with the geometry, lmodern, microtype, and hyperref packages:

```bash
mkdir -p output/pdf
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=output/pdf research_paper/paper/main.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=output/pdf research_paper/paper/main.tex
```

Alternatively, use Tectonic:

```bash
mkdir -p output/pdf
tectonic --outdir output/pdf research_paper/paper/main.tex
```

The compiled deliverable is [main.pdf](../../output/pdf/main.pdf). Build auxiliaries are ignored. A venue-specific class and citation style will be selected after venue requirements are known.

Verified on 20 September 2026 with Tectonic 0.17.0: successful compilation, one A4 page, correct author metadata and extracted text, and a visual render with no clipping or overlap. The compiler was downloaded to a temporary directory and is not part of the repository.
