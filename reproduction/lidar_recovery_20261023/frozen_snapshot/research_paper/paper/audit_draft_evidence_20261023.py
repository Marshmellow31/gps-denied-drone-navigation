"""Check first-draft numerical transcription against existing compact evidence.

This does not rerun estimators, calculate new scientific estimates or review
novelty. Run from any directory with the repository evidence available.
"""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAPER = Path(__file__).resolve().parent
DRAFT = PAPER / "recovery_transfer_draft_20261023.tex"
RESULTS = ROOT / "evidence/final_geometry_v2_results_20261012"
FAILURES = ROOT / "evidence/final_failure_analysis_20261012"


def main():
    tex = DRAFT.read_text()
    paths = [DRAFT, Path(__file__).resolve()]
    analyses = {}
    for backend in ("fastlio", "pointlio"):
        path = RESULTS / f"{backend}_analysis.json"
        analyses[backend] = json.loads(path.read_text())
        paths.append(path)
        a = analyses[backend]
        assert a["status"] == "CONFIRMATORY_COMPLETE", backend
        assert a["completed_geometry_pairs"] == a["planned_geometry_pairs"] == 48
        assert a["native_scene_runs_loaded"] == 96
        if backend == "fastlio":
            assert a["threshold_selected_on_test"] is False
        else:
            assert a["threshold_fit_performed"] is False
            assert a["threshold_locked_from_development"] == a["POINTLIO_MIN_EIG_G3_threshold"]
    methods = [
        ("fastlio", "FASTLIO_MIN_EIG_G3", "FAST-LIO", "Scalar", "FAST scalar"),
        ("fastlio", "DCREG_SCHUR_MASK", "FAST-LIO", "Fixed Schur", "FAST fixed Schur"),
        ("pointlio", "POINTLIO_MIN_EIG_G3", "Point-LIO", "Scalar", "Point scalar"),
        ("pointlio", "POINTLIO_DCREG_SCHUR_MASK", "Point-LIO", "Fixed Schur", "Point fixed Schur"),
    ]
    diagnosis_path = FAILURES / "event_diagnosis.csv"
    paths.append(diagnosis_path)
    with diagnosis_path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 192
    verified = []
    for backend, method, label, policy, miss_label in methods:
        m = analyses[backend]["method_metrics"][method]
        if backend == "pointlio":
            m = m["summary"]
        fh = m["false_healthy_events"]
        den = m["false_healthy_conditional_denominator"]
        recovered = m["truth_recovered_events"]
        detected = m["detected_recovery_events"]
        delay = m["detection_delay_median_s_detected_only"]
        expected = (
            f"{label} & {policy} & {fh}/{den} & {detected}/{recovered} & "
            f"{recovered-detected} & {delay:.3f}"
        )
        assert expected in tex, ("primary table mismatch", expected)
        ci = m["event_proportion_intervals"]
        fhci = ci["initial_false_healthy_conditional"]["wilson_95"]
        detci = ci["recovery_detection_given_truth_recovered"]["wilson_95"]
        expected_ci = (
            f"{label} & {policy} & {100*fh/den:.1f} "
            f"[{100*fhci[0]:.1f}, {100*fhci[1]:.1f}] & "
            f"{100*detected/recovered:.1f} [{100*detci[0]:.1f}, {100*detci[1]:.1f}]"
        )
        assert expected_ci in tex, ("interval table mismatch", expected_ci)
        assert m["available_decision_ticks"] == m["planned_decision_ticks"] == 9600
        selected = [r for r in rows if r["backend"] == backend and r["method"] == method]
        assert len(selected) == 48
        missed = [r for r in selected if r["missed_recovery"] == "True"]
        counts = Counter(r["miss_pattern"] for r in missed)
        assert len(missed) == recovered-detected
        no_raw = counts["NO_RAW_HEALTHY_TICK_IN_RECOVERY_INTERVAL"]
        no_confirmation = counts["RAW_HEALTHY_TICKS_WITHOUT_THREE_RECORD_CONFIRMATION"]
        active = counts["ACTIVE_STATE_WITHOUT_NEW_POST_ONSET_TRANSITION"]
        # Exact labels are validated below, so a renamed category cannot vanish.
        assert no_raw + no_confirmation + active == len(missed), dict(counts)
        expected_miss = f"{miss_label} & {no_raw} & {no_confirmation} & {active} & {len(missed)}"
        assert expected_miss in tex, ("miss table mismatch", expected_miss)
        verified.append({"backend": backend, "method": method, "primary_row": expected,
                         "interval_row": expected_ci, "miss_row": expected_miss})
    cites = set()
    for group in re.findall(r"\\cite\{([^}]+)\}", tex):
        cites.update(group.split(","))
    bib = set(re.findall(r"\\bibitem\{([^}]+)\}", tex))
    assert cites == bib, {"undefined": sorted(cites-bib), "unused": sorted(bib-cites)}
    for rel in [
        "protocol/METRICS.md", "protocol/INDICATORS.md",
        "protocol/POINTLIO_REPLICATION_AMENDMENT_20260929.md",
        "protocol/IMPLEMENTATION_FREEZE_GEOMETRY_V2_20261012.md",
        "reviews/R2_GEOMETRY_AMENDMENT_20261012.md",
        "reviews/FINAL_GEOMETRY_V2_RESULT_AUDIT_20261012.md",
        "evidence/final_geometry_v2_results_20261012/RESULTS_REPORT.md",
        "evidence/final_failure_analysis_20261012/FAILURE_ANALYSIS_REPORT.md",
        "evidence/CLAIM_EVIDENCE_MAP_20261012.md",
        "literature/CLOSEST_WORK_MATRIX_20261012.md",
    ]:
        paths.append(ROOT / rel)
    report = {
        "status": "PASS", "scope": "core numerical transcription and citation-key consistency only",
        "native_runs_rerun": False, "new_scientific_analysis": False,
        "publication_novelty_accepted": False, "verified_method_rows": verified,
        "citations": sorted(cites),
        "source_sha256": {str(p.relative_to(ROOT.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in paths},
    }
    out = PAPER / "draft_evidence_audit_20261023.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: four primary/interval/miss table rows and {len(cites)} citation keys; {out}")


if __name__ == "__main__":
    main()
