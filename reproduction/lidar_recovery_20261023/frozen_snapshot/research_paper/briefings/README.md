# Professor briefing - 19 October 2026

[Open the illustrated PDF](../../output/pdf/lidar_research_professor_briefing_2026-10-19.pdf).

Eight pages explain the original landing prototype, the narrowed recovery question,
implemented workflow, frozen experiment, main results, failure patterns, current
difficulties and proposed next steps. The scientific evidence checkpoint is
12 October; repository code was refreshed to `5971024` on 19 October before
preparation. Publication novelty and the full manuscript remain unfinished.

The charts read accepted compact numerical exports directly. The early-health
chart uses the unconditional denominator of 48 events; recovery detection uses
each backend's own truth-recovered events. Confidence whiskers use Wilson 95%
intervals. No simulation, native replay, threshold fitting or new scientific
analysis was run to prepare the briefing.

## Rebuild

With Python 3, `reportlab` and the Lato font family installed:

```bash
python3 research_paper/briefings/build_professor_briefing.py
```

The script writes the PDF and a [source-hash manifest](../../output/pdf/lidar_research_professor_briefing_2026-10-19.sources.json).
Visual review: render the PDF with `pdftoppm -r 100 -png`, then inspect every page.
The briefing supplements the frozen scientific records without modifying them.
