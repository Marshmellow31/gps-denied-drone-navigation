"""Build the evidence-linked professor briefing; never run scientific experiments.

Requires reportlab and the Lato TTF family (Debian/Ubuntu fonts-lato).
Run from any directory. Charts read the accepted compact CSV exports directly.
"""
from pathlib import Path
from collections import Counter
import csv
import hashlib
import json
import math
import os
from datetime import datetime, timezone

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output/pdf/lidar_research_professor_briefing_2026-10-19.pdf"
RESULTS = "research_paper/evidence/final_geometry_v2_results_20261012/"
FAILURES = "research_paper/evidence/final_failure_analysis_20261012/"
SOURCE_REVISION = "5971024"
GITHUB = f"https://github.com/Marshmellow31/gps-denied-drone-navigation/blob/{SOURCE_REVISION}/"
SOURCES = [
    ("S1", "Original landing prototype", "old_data/README.md"),
    ("S2", "Research goal and evidence boundaries", "research_paper/RESEARCH_GOAL.md"),
    ("S3", "Accepted final results and numerical exports", RESULTS + "RESULTS_REPORT.md"),
    ("S4", "Independent result-accounting audit", "research_paper/reviews/FINAL_GEOMETRY_V2_RESULT_AUDIT_20261012.md"),
    ("S5", "Exploratory failure investigation", FAILURES + "FAILURE_ANALYSIS_REPORT.md"),
    ("S6", "Candidate contribution and literature overlap", "research_paper/literature/CONTRIBUTION_ASSESSMENT_20261012.md"),
    ("S7", "Claim-to-evidence map", "research_paper/evidence/CLAIM_EVIDENCE_MAP_20261012.md"),
    ("S8", "Current manuscript source", "research_paper/paper/main.tex"),
    ("S9", "Metrics and recovery definitions", "research_paper/protocol/METRICS.md"),
]

W, H = 595.276, 841.89
M, CW = 44, W - 88
NAVY = HexColor("#142A3B")
TEAL = HexColor("#007F7B")
BLUE = HexColor("#2878A8")
AMBER = HexColor("#BC7425")
RED = HexColor("#BB5250")
INK = HexColor("#273D4B")
MUTED = HexColor("#607481")
PALE = HexColor("#EDF4F5")
LINE = HexColor("#D8E3E6")
BG = HexColor("#FAFCFC")


def read_csv(path):
    with (ROOT / path).open(newline="") as f:
        return list(csv.DictReader(f))


methods = read_csv(RESULTS + "method_summary.csv")
strata = read_csv(RESULTS + "stratum_summary.csv")
diagnosis = read_csv(FAILURES + "event_diagnosis.csv")
assert len(methods) == 4 and len(diagnosis) == 192
assert [int(r["detected_recovery_events"]) for r in methods] == [14, 38, 27, 25]


def register_fonts():
    for name, filename in [("Lato", "Lato-Regular.ttf"), ("Lato-Bold", "Lato-Bold.ttf"), ("Lato-Italic", "Lato-Italic.ttf")]:
        pdfmetrics.registerFont(TTFont(name, f"/usr/share/fonts/truetype/lato/{filename}"))
    pdfmetrics.registerFontFamily("Lato", normal="Lato", bold="Lato-Bold", italic="Lato-Italic", boldItalic="Lato-Bold")


class Briefing:
    def __init__(self):
        OUT.parent.mkdir(parents=True, exist_ok=True)
        self.c = canvas.Canvas(str(OUT), pagesize=(W, H), invariant=1, pageCompression=1)
        self.c.setTitle("LiDAR Recovery Reliability | Professor Briefing | 19 October 2026")
        self.c.setAuthor("Harshil Patel, Daksha Lingampeta, Nisarg Vyas")
        self.c.setSubject("Evidence-linked progress briefing; controlled simulation findings and next scientific decisions")
        self.page = 0
        self.bounds = []

    def text(self, text, x, y, size=11, color=INK, bold=False):
        self.c.setFillColor(color)
        self.c.setFont("Lato-Bold" if bold else "Lato", size)
        self.c.drawString(x, H-y-size, text)

    def para(self, text, x, y, width=CW, size=10.8, color=INK, leading=None):
        style = ParagraphStyle("p", fontName="Lato", fontSize=size, leading=leading or size*1.42, textColor=color)
        p = Paragraph(text, style)
        _, height = p.wrap(width, H)
        assert y + height <= H-48, (self.page, text[:65], y, height)
        p.drawOn(self.c, x, H-y-height)
        self.bounds.append((self.page, x, y, width, height))
        return y+height

    def rect(self, x, y, width, height, color=PALE, radius=10, stroke=None):
        self.c.setFillColor(color)
        self.c.setStrokeColor(stroke or color)
        self.c.roundRect(x, H-y-height, width, height, radius, fill=1, stroke=bool(stroke))

    def line(self, x1, y1, x2, y2, color=LINE, width=1):
        self.c.setStrokeColor(color)
        self.c.setLineWidth(width)
        self.c.line(x1, H-y1, x2, H-y2)

    def arrow(self, x1, y1, x2, y2, color=TEAL):
        self.line(x1, y1, x2, y2, color, 1.6)
        a = math.atan2(y2-y1, x2-x1)
        for delta in [-.55, .55]:
            self.line(x2, y2, x2-7*math.cos(a+delta), y2-7*math.sin(a+delta), color, 1.6)

    def start(self, kicker, title, subtitle, sources):
        if self.page:
            self.c.showPage()
        self.page += 1
        self.c.setFillColor(BG)
        self.c.rect(0, 0, W, H, fill=1, stroke=0)
        self.rect(M, 33, 31, 4, TEAL, 1)
        self.text(kicker.upper(), M, 48, 9, TEAL, True)
        self.text(title, M, 72, 25, NAVY, True)
        self.para(subtitle, M, 111, size=10.5, color=MUTED)
        self.line(M, 787, W-M, 787)
        self.text("PROFESSOR BRIEFING  |  19 OCT 2026", M, 799, 7.4, MUTED)
        self.text(f"SOURCES {sources}  |  {self.page:02d} / 08", 365, 799, 7.4, MUTED)

    def card(self, x, y, width, height, label, body, accent=TEAL):
        self.rect(x, y, width, height, PALE)
        self.rect(x, y, 3, height, accent, 1)
        self.text(label, x+14, y+12, 12, accent, True)
        self.para(body, x+14, y+34, width-28, size=10.2)

    def note(self, text, y, color=TEAL, height=60):
        self.rect(M, y, CW, height, PALE)
        self.rect(M, y, 4, height, color, 1)
        self.para(text, M+15, y+11, CW-30, size=10.3)

    def bullet(self, label, body, y, number=None, color=TEAL):
        if number is not None:
            self.rect(M, y+1, 25, 25, color, 7)
            self.text(str(number), M+8, y+5, 11, white, True)
        self.text(label, M+38, y, 12, color, True)
        return self.para(body, M+38, y+21, CW-38, size=10.6)


def cover(b):
    b.start("Research progress / meeting copy", "When can we trust recovery?", "LiDAR recovery reliability in GPS-denied navigation", "S2-S8")
    b.rect(M, 159, CW, 138, NAVY)
    b.text("CONTROLLED EVALUATION COMPLETE", M+20, 177, 10, HexColor("#72D5CD"), True)
    b.para("We tested whether existing LiDAR health signals recognize the return of accurate movement estimation after difficult corridor geometry.", M+20, 202, CW-40, 17, white, 23)
    for i, (n, label) in enumerate([("48", "paired geometries"), ("192", "completed scene runs"), ("2", "odometry systems")]):
        x = M+i*174
        b.text(n, x, 325, 34, TEAL, True)
        b.text(label, x, 369, 10, MUTED)
    b.text("The project in one minute", M, 418, 16, NAVY, True)
    b.para("We began with a simulated safe-landing baseline, then narrowed the research to a specific reliability question. We built a controlled LiDAR/IMU evaluation, calibrated on development data, froze the settings, and completed experiments in FAST-LIO and Point-LIO.", M, 449, size=11.4)
    b.note("<b>Main finding:</b> fixed health policies show different trade-offs between premature reassurance and missed recovery declarations in the evaluated geometries.", 554, height=70)
    b.para("<b>Where we stand:</b> experiments, result accounting and failure analysis are complete. The physical explanation of some patterns, publication novelty and the full manuscript remain unfinished.", M, 652, size=11.2)
    b.para("Harshil Patel  /  Daksha Lingampeta  /  Nisarg Vyas<br/>Prepared 19 October 2026. Scientific evidence checkpoint: 12 October 2026.<br/>Repository refreshed to 5971024, including the 19 October test additions.", M, 731, size=8.7, color=MUTED)


def origins(b):
    b.start("01 / Starting point and research focus", "From landing to localization", "We narrowed a broad drone problem to a measurable question about estimation reliability.", "S1-S2")
    b.card(M, 163, 244, 144, "Original implementation", "Synthetic terrain + noisy distance sensing + a height map. Check slope, roughness, obstacles and the full vehicle footprint before selecting a target.")
    b.card(M+263, 163, 244, 144, "Why the scope changed", "Navigation, mapping, landing and control are separate problems. A focused study can isolate one scientific question using existing software and controlled data.", BLUE)
    b.para("<b>Archived baseline:</b> 100 synthetic cases; all produced targets passed synthetic truth checks. Targets were available in 45/80 cases containing safe terrain (56.25%). These findings belong to the earlier landing study.", M, 324, size=10.4)
    b.text("Why a corridor is difficult", M, 407, 16, NAVY, True)
    b.rect(M, 440, CW, 135, white, stroke=LINE)
    for yy in [470, 535]:
        b.line(72, yy, 330, yy, MUTED, 4)
    for xx, yy, ww, hh in [(375, 459, 22, 22), (446, 516, 25, 20), (400, 538, 18, 18), (486, 467, 21, 21)]:
        b.rect(xx, yy, ww, hh, HexColor("#A7CEC9"), 2)
    b.arrow(106, 503, 452, 503)
    b.text("Repeated side walls", 86, 548, 9, MUTED)
    b.text("New geometric features", 365, 548, 9, TEAL)
    b.text("CONCEPTUAL TOP VIEW - NOT A MEASURED SCENE", 76, 446, 7, MUTED)
    b.para("Similar-looking surfaces give weak clues about movement along the corridor. This is <b>geometric degeneracy</b>. On exit, richer geometry may improve new movement estimates while earlier position drift remains.", M, 591, size=10.7)
    width = (CW-20)/3
    for i, (label, body) in enumerate([("Geometry", "Are useful movement constraints present?"), ("Local motion", "Are the newly estimated movements accurate?"), ("Total drift", "How much earlier position error remains?")]):
        b.card(M+i*(width+10), 674, width, 94, label, body, [TEAL, BLUE, AMBER][i])


def workflow(b):
    b.start("02 / What we implemented", "A complete evidence workflow", "Existing estimators, read-only diagnostics and a separate reference-based evaluator.", "S2-S3,S5")
    b.card(M, 159, 240, 73, "Simulated LiDAR + IMU", "Sensor data supplied to the estimator.")
    b.card(328, 159, 223, 73, "Separate true trajectory", "Used offline for evaluation only.", BLUE)
    b.arrow(164, 235, 164, 251)
    b.card(M, 255, 240, 73, "FAST-LIO / Point-LIO", "Pinned existing odometry backends.")
    b.arrow(164, 331, 164, 347)
    b.card(M, 351, 240, 90, "Health decisions", "Minimum eigenvalue + fixed DCReg directional adaptation; causal confirmation.")
    b.arrow(286, 291, 318, 291, BLUE)
    b.arrow(439, 235, 439, 251, BLUE)
    b.card(328, 255, 223, 90, "Local movement errors", "Compare estimated motion with truth; derive sustained recovery offline.", BLUE)
    b.arrow(439, 348, 439, 456, BLUE)
    b.arrow(164, 444, 164, 456)
    b.rect(M, 461, CW, 63, NAVY)
    b.para("<b>Compare decisions with recovery:</b> early health, new recovery declarations, delay, availability, non-recovery and uncertainty.", M+15, 474, CW-30, 11, white)
    b.text("Why simulation is the primary evidence", M, 552, 16, NAVY, True)
    y = b.para("<b>GEODE:</b> development replays did not supply usable recovery evidence; failures were retained.<br/><b>Hilti-Oxford Exp18:</b> a development replay worked, but reference coverage and independence were insufficient for sustained final recovery claims.<br/><b>Simulation:</b> supplies controlled geometry and known motion, with truth kept outside the estimator and online health decision.", M, 584, size=10.7)
    b.note("We implemented diagnostic export, reference association, reset handling, resumable runners, input/output identities, failure accounting and figures. The DCReg detector adaptation excludes full DCReg registration mitigation.", y+20, height=77)


def design(b):
    b.start("03 / Fair experimental design", "Freeze first. Evaluate second.", "Development calibration and final-outcome evaluation were kept separate.", "S3-S4,S9")
    labels = [("Short / narrow", "12 pairs"), ("Short / wide", "12 pairs"), ("Long / narrow", "12 pairs"), ("Long / wide", "12 pairs")]
    for i, (label, n) in enumerate(labels):
        x = M+(i%2)*263
        y = 161+(i//2)*84
        b.rect(x, y, 244, 70, PALE)
        b.text(label, x+14, y+12, 12, NAVY, True)
        b.text(n + "  /  corridor + matched feature control", x+14, y+38, 8.5, MUTED)
    b.para("<b>48 pairs x 2 scenes x 2 backends = 192 completed runs.</b><br/>Each pair contains a corridor and a control with extra geometric features and matched motion. Both backends received identical corresponding sensor inputs. There are 48 shared geometry units, not 192 independent geometries.", M, 337, size=10.9)
    b.text("Reference-defined recovery", M, 430, 16, NAVY, True)
    for i in range(3):
        x = M+i*119
        b.rect(x, 467, 107, 62, HexColor("#DCEFEA"), 5)
        b.text(f"Window {i+1}", x+13, 478, 11, TEAL, True)
        b.text("1 second", x+13, 503, 10, MUTED)
    b.arrow(393, 496, 420, 496)
    b.text("Confirmed", 430, 477, 11, TEAL, True)
    b.text("recovery", 430, 496, 11, TEAL, True)
    b.para("Each consecutive, non-overlapping movement window must have translation error <= 0.20 m and rotation error <= 5 degrees. The three-window confirmation must finish within 20 seconds of the predefined exit. These are research tolerances.", M, 549, size=10.7)
    b.note("<b>Online health is separate:</b> decisions use causal diagnostic data on a 10 Hz grid with three-tick confirmation. Offline recovery labels use reference motion; future reference samples never enter the online indicator.", 628, height=74)
    b.para("<b>Design disclosure:</b> an earlier failed geometry screen informed the revised control spacing and candidate pools. Its IDs were excluded. Fresh scenes were selected using geometry criteria before estimator execution; final accuracy results did not select scenes or change thresholds.", M, 719, size=9.6, color=MUTED)


def wilson(k, n):
    z = 1.96
    p = k/n
    center = (p+z*z/(2*n))/(1+z*z/n)
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return center-half, center+half


def results_page(b):
    b.start("04 / Main findings", "Low early health can hide misses", "The locked policies show different trade-offs under the evaluated simulation design.", "S3-S4")
    b.card(M, 155, 244, 78, "FAST-LIO: 46 / 48 recovered", "Two did not recover within the horizon.")
    b.card(307, 155, 244, 78, "Point-LIO: 32 / 48 recovered", "Sixteen did not recover within the horizon.", BLUE)
    x1, x2, pw = 233, 401, 118
    b.text("Early healthy", x1, 257, 11, AMBER, True)
    b.text("New declaration", x2, 257, 11, TEAL, True)
    b.text("all 48 events", x1, 275, 8.5, MUTED)
    b.text("actual recoveries", x2, 275, 8.5, MUTED)
    for x in [x1, x2]:
        for tick in [0, .5, 1]:
            b.text(f"{tick*100:.0f}%", x+pw*tick-5, 303, 7.5, MUTED)
            b.line(x+pw*tick, 323, x+pw*tick, 522, LINE, .6)
    for i, r in enumerate(methods):
        y = 336+i*49
        backend = r["backend"]
        method = "Minimum eigenvalue" if "MIN_EIG" in r["method"] else "DCReg adaptation"
        b.text(backend, M, y-4, 10.6, NAVY, True)
        b.text(method, M, y+12, 9.1, MUTED)
        for x, k, n, col in [(x1, int(r["false_healthy_events"]), 48, AMBER), (x2, int(r["detected_recovery_events"]), int(r["truth_recovered_events"]), TEAL)]:
            b.rect(x, y, pw*k/n, 8, col, 2)
            lo, hi = wilson(k, n)
            b.line(x+pw*lo, y+4, x+pw*hi, y+4, NAVY, 1)
            b.line(x+pw*lo, y+1, x+pw*lo, y+7, NAVY, 1)
            b.line(x+pw*hi, y+1, x+pw*hi, y+7, NAVY, 1)
            b.text(f"{k}/{n}  ({100*k/n:.1f}%)", x, y+13, 9, col, True)
    b.para("Early healthy means active health before sustained-recovery onset; it is not proof of instantaneous pose error. Bars show event rates; whiskers are 95% Wilson intervals. Early health uses <b>all 48 events</b>; detection uses each backend's own recovered events. These denominators differ and do not form an estimator leaderboard.", M, 544, size=9.3, color=MUTED, leading=12.5)
    b.note("<b>Example:</b> FAST-LIO minimum eigenvalue had only 1/48 early-healthy events, but declared recovery in just 14/46 recovered cases. A cautious policy can miss useful recovery notifications.", 620, height=70)
    b.para("Detected-only median delays: FAST scalar 0.85 s; FAST DCReg adaptation 6.80 s; Point scalar 3.40 s; Point DCReg adaptation 3.00 s. Misses have no observed delay, so a short median does not imply better overall responsiveness. Full horizon decision availability was 100% for all four policies.", M, 710, size=9.7)


def failures_page(b):
    b.start("05 / What the failures taught us", "A missed alarm has several meanings", "Post-result analysis reproduced the original labels and kept all frozen counts unchanged.", "S3,S5,S7")
    categories = [("NO_RAW_HEALTHY_TICK_IN_RECOVERY_INTERVAL", "No raw healthy tick", RED), ("RAW_HEALTHY_TICKS_WITHOUT_THREE_RECORD_CONFIRMATION", "No confirmation", AMBER), ("ACTIVE_STATE_WITHOUT_NEW_POST_ONSET_TRANSITION", "Active, no new alarm", BLUE)]
    for i, (_, label, col) in enumerate(categories):
        x = M+i*170
        b.rect(x, 161, 8, 8, col, 1)
        b.text(label, x+13, 158, 8.4, MUTED)
    for i, r in enumerate(methods):
        counts = Counter(d["miss_pattern"] for d in diagnosis if d["method"] == r["method"])
        y = 203+i*41
        label = ("FAST" if r["backend"] == "FAST-LIO" else "Point") + (" / scalar" if "MIN_EIG" in r["method"] else " / DCReg adapt.")
        b.text(label, M, y, 9.8, NAVY, True)
        x = 190
        for key, _, col in categories:
            n = counts[key]
            if n:
                width = n*9
                b.rect(x, y, width, 20, col, 2)
                b.text(str(n), x+width/2-(3 if n<10 else 6), y+3, 10, white, True)
                x += width
        b.text(f"{sum(counts[k] for k,_,_ in categories)} misses", x+9, y+3, 9, MUTED)
    b.note("<b>Endpoint distinction:</b> five of the seven Point-LIO DCReg-adaptation misses had an active healthy state during the recovered interval, but no new qualifying transition. A missed new declaration does not always mean continuous unhealthy status.", 383, height=81)
    b.text("Recovery also varies across geometry groups", M, 493, 16, NAVY, True)
    headers = ["Short / narrow", "Short / wide", "Long / narrow", "Long / wide"]
    for i, label in enumerate(headers):
        x = 158+i*98
        b.text(label, x, 530, 8.6, MUTED)
    for row, backend in enumerate(["FAST-LIO", "Point-LIO"]):
        y = 552+row*55
        b.text(backend, M, y+14, 10, NAVY, True)
        for i, r in enumerate([s for s in strata if s["backend"] == backend and "MIN_EIG" in s["method"]]):
            recovered = int(r["recovered"])
            x = 158+i*98
            col = HexColor("#DCEFEA") if recovered == 12 else HexColor("#F4E5D3")
            b.rect(x, y, 87, 43, col, 5)
            b.text(f"{recovered}/12", x+23, y+12, 15, TEAL if recovered==12 else AMBER, True)
    b.para("Point-LIO recovered in 24/24 narrow versus 8/24 wide corridors. Emphasizing width after seeing outcomes is <b>exploratory</b>; the data do not establish a causal width law. Each group has only 12 geometries.", M, 681, size=10.3)
    b.para("Measurement-count summaries do not support a simple count-only explanation: FAST scalar's missed and detected groups had almost identical median accepted counts. Directional distribution, visibility, correspondence quality and estimator history remain possible explanations.", M, 738, size=9.2, color=MUTED)


def status_page(b):
    b.start("06 / Current position and difficulties", "The scientific argument is unfinished", "Implementation acceptance, scientific novelty and real-world reliability are separate questions.", "S3-S8")
    rows = [
        ("COMPLETE", "Controlled simulation, two backends and diagnostic recording", TEAL),
        ("COMPLETE", "Development calibration, protocol freeze and final 192 runs", TEAL),
        ("COMPLETE", "Scoped result-accounting audit, failure analysis and figures", TEAL),
        ("OPEN", "Physical explanation of geometry-dependent outcomes", AMBER),
        ("OPEN", "Precise contribution beyond the closest existing literature", AMBER),
        ("OPEN", "Full manuscript; main source still contains a proposal abstract", AMBER),
    ]
    for i, (state, label, col) in enumerate(rows):
        y = 159+i*37
        b.rect(M, y, 73, 25, col, 5)
        b.text(state, M+10, y+7, 8, white, True)
        b.para(label, M+86, y+5, CW-86, 10.3)
    b.text("Difficulties that determine the next work", M, 409, 16, NAVY, True)
    b.bullet("Distinct contribution", "OCE already studies local-motion usability and recovery delay. Our candidate contribution concerns fixed-policy transfer across fresh geometry groups in two LIO backends. Its usefulness and novelty need scientific review.", 443, 1)
    b.bullet("Mechanism and endpoint interpretation", "Width patterns are observations. We still need to explain the behavior and clarify when an application needs active health versus a new recovery notification.", 537, 2)
    b.bullet("Fair comparison and generalization", "The directional method is a detector adaptation. Broader claims need a faithful comparator and suitable additional validation. Current real recordings do not establish sustained recovery.", 619, 3)
    b.note("<b>Claim boundary:</b> the evidence applies to the evaluated simulated straight-corridor design and fixed settings. It does not establish a new detector, estimator superiority, universal reliability or flight safety. The scoped audit is not journal peer review.", 706, height=72)


def next_page(b):
    b.start("07 / Next steps and discussion", "Turn the evidence into a paper", "Proposed sequence for professor feedback; no new experiment is implied by this briefing.", "S6-S9")
    steps = [
        ("Write the full draft", "Present the question, frozen design, results, failures and limitations using the existing evidence."),
        ("Resolve contribution and endpoint", "Compare closely with OCE/DCReg and explain active health versus a new declaration without replacing the frozen headline results."),
        ("Choose a justified validation step", "Assess comparator feasibility. If one mechanism matters to the claim, freeze a focused study on fresh scenes before collecting outcomes."),
        ("Obtain scientific review and revise", "Ask whether the empirical finding is distinct and useful, and which additional evidence would resolve a specific objection."),
    ]
    for i, (label, body) in enumerate(steps):
        b.bullet(label, body, 158+i*77, i+1)
    b.note("<b>Questions for ma'am:</b> Is the transfer trade-off a sufficient contribution? Should we emphasize active health, new declarations or both? Would a closer comparator, focused simulation or better real reference add the most value?", 480, height=77)
    b.para("The final cohort is now exposed. New explanations are exploratory; confirmation needs a prespecified hypothesis, controls, endpoints and fresh geometry IDs. No retuning on final outcomes.", M, 572, size=9.8, color=MUTED)
    b.text("Evidence index - clickable repository sources", M, 627, 12, NAVY, True)
    for i, (sid, title, path) in enumerate(SOURCES):
        x = M if i<5 else 310
        y = 655+(i if i<5 else i-5)*22
        b.para(f'<link href="{GITHUB+path}" color="#007F7B"><b>{sid}</b>  {title}</link>', x, y, 239, 8.1, leading=10.5)
    b.para("Charts read accepted CSVs directly; no estimator was rerun. Early-health denominators on p.5 use all 48 events; the accepted report also provides conditional rates. The PDF sources manifest records the input hashes and revision.", M, 768, size=7.7, color=MUTED, leading=10)


def main():
    # Fixed document-date metadata keeps rebuilds byte-reproducible.
    os.environ["SOURCE_DATE_EPOCH"] = str(int(datetime(2026, 10, 19, tzinfo=timezone.utc).timestamp()))
    register_fonts()
    b = Briefing()
    for page in [cover, origins, workflow, design, results_page, failures_page, status_page, next_page]:
        page(b)
    assert b.page == 8
    b.c.save()
    inputs = sorted(set([p for _, _, p in SOURCES] + [RESULTS+"method_summary.csv", RESULTS+"stratum_summary.csv", FAILURES+"event_diagnosis.csv", "research_paper/briefings/build_professor_briefing.py"]))
    manifest = {
        "document_date": "2026-10-19", "scientific_checkpoint": "2026-10-12",
        "source_revision": SOURCE_REVISION, "pages": b.page,
        "scope": "Professor briefing derived from existing evidence; no new scientific experiment or threshold fitting.",
        "output": str(OUT.relative_to(ROOT)),
        "pdf_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest(),
        "sources_sha256": {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs},
        "chart_notes": "Rates from method_summary.csv; Wilson z=1.96; geometry recovery from scalar rows of stratum_summary.csv; miss taxonomy counted from event_diagnosis.csv.",
    }
    OUT.with_suffix(".sources.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(f"Created {OUT} ({OUT.stat().st_size:,} bytes; {b.page} pages)")


if __name__ == "__main__":
    main()
