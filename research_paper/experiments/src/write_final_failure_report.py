"""Present exploratory failure exports; no new statistical test or tuning."""
import csv
import json
from pathlib import Path
from statistics import median

from analyze_final_failure_cases import METHODS
from t16_development_analysis import sha256_file

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT/'research_paper/evidence/final_failure_analysis_20261012'
FIGURES = ROOT/'research_paper/figures/final_failure_analysis_20261012'


def write():
    manifest = json.loads((EVIDENCE/'manifest.json').read_text())
    for name,digest in manifest['output_sha256'].items():
        if sha256_file(EVIDENCE/name)!=digest:raise ValueError('Changed exploratory source')
    rows=list(csv.DictReader((EVIDENCE/'event_diagnosis.csv').open()))
    figures=json.loads((FIGURES/'case_captions.json').read_text())
    text=['# Exploratory final failure analysis — 12 October 2026', '',
          '**Step 4 complete: all final corridor events examined; no threshold, frozen result or estimator changed. Mechanisms and publication novelty remain unproven.**', '',
          'Read and hash-checked consumed streams from all 192 completed corridor/control native slots. Reused the frozen reference association, primary windows, recovery labels and causal state machine. All 96 corridor labels and 192 diagnostic event rows exactly reproduce the accepted final analyses. This is a post-result investigation, not a new confirmatory study or independent review.', '',
          '## What “missed recovery” means', '',
          'The frozen endpoint requires a **new confirmed-healthy transition after retrospective recovery onset**, before relapse/deadline. An already-active healthy state can therefore coexist with a missed new declaration. Such an event is not equivalent to a detector remaining unhealthy. This distinction was not introduced to repair outcomes: the rule and all original counts are unchanged.', '',
          '| Backend / policy | Missed recoveries | No raw healthy tick | Raw healthy, no three-record confirmation | Active state, no new post-onset transition |',
          '| --- | ---: | ---: | ---: | ---: |']
    for b,methods in METHODS.items():
        for m in methods:
            group=[r for r in rows if r['method']==m]
            counts=manifest['miss_patterns'][m]
            text.append(f"| {b} / {'scalar' if m==methods[0] else 'fixed Schur'} | {sum(r['missed_recovery']=='True' for r in group)} | {counts.get('NO_RAW_HEALTHY_TICK_IN_RECOVERY_INTERVAL',0)} | {counts.get('RAW_HEALTHY_TICKS_WITHOUT_THREE_RECORD_CONFIRMATION',0)} | {counts.get('ACTIVE_STATE_WITHOUT_NEW_POST_ONSET_TRANSITION',0)} |")
    text += ['', 'All missed-event recovery intervals contain available decision ticks. These mutually exclusive classes describe observable policy behavior, not physical causes. “Active state” means active at some time in the recovered interval, with no qualifying new transition; it need not remain active for the whole interval.', '',
             '![All-event failure patterns and accepted measurement/score summaries](../../figures/final_failure_analysis_20261012/failure_patterns.png)', '',
             'The top bars partition every missed recovery. The bottom scatter includes all 48 corridors per backend: red marks an initial false-healthy event, amber a missed recovery without an initial false-healthy event, blue neither; crosses mark non-recovery. Red takes priority if event categories overlap. Dashed lines show the locked scalar thresholds. A median over the whole post-exit horizon is descriptive and does not reconstruct a particular tick or determine the event label.', '',
             '## Initial false-healthy behavior', '',
             '| Backend / policy | Initial false-healthy events | Active at first initial-interval tick | With a new transition inside initial interval |',
             '| --- | ---: | ---: | ---: |']
    for b,methods in METHODS.items():
        for m in methods:
            group=[r for r in rows if r['method']==m and r['false_healthy']=='True']
            text.append(f"| {b} / {'scalar' if m==methods[0] else 'fixed Schur'} | {len(group)} | {sum(r['initial_state_active_at_first_tick']=='True' for r in group)} | {sum(int(r['new_initial_transitions'])>0 for r in group)} |")
    text += ['', 'The initial endpoint counts active health before sustained recovery onset, including carried-in state. Onset is retrospective and only known after three passing windows. A premature healthy tick is not proof that an instantaneous pose error is large: an interval can precede the first qualifying sustained triple even while some local windows are accurate. The timeline’s later window-end error samples must not be read as online information at the earlier tick. The two descriptive columns above are not generally guaranteed to be mutually exclusive.', '',
             '## Measurement support and score scaling', '',
             'For every scene, take medians over valid diagnostic records in the fixed [exit, exit + 20 s) horizon. The table then takes the median across corridor events within the displayed, post-result outcome group. Counts are accepted measurement rows under each backend’s own instrumentation; compare within a backend, not as a cross-backend point-density ranking.', '',
             '| Backend / scalar outcome group | Events | Median of event median accepted counts | Median of event median scalar scores |',
             '| --- | ---: | ---: | ---: |']
    predicates=[('recovered, missed',lambda r:r['missed_recovery']=='True'),
                ('recovered, detected',lambda r:r['truth_status']=='RECOVERED' and r['missed_recovery']=='False'),
                ('non-recovered',lambda r:r['truth_status']!='RECOVERED')]
    for b,methods in METHODS.items():
        cohort=[r for r in rows if r['backend']==b and r['method']==methods[0]]
        for name,predicate in predicates:
            group=[r for r in cohort if predicate(r)]
            count=median(float(r['post_exit_accepted_count_median']) for r in group)
            score=median(float(r['post_exit_scalar_score_median']) for r in group)
            text.append(f'| {b} / {name} | {len(group)} | {count:.2f} | {score:.3f} |')
    text += ['', 'FAST scalar misses and detections have almost identical group median accepted counts, but different group median scores. Point non-recoveries have more accepted rows at the group-median level than its recovered/detected group. These summaries do not support a simple monotonic “more accepted measurements means recovered” account. They do not rule out effects of directional distribution, correspondence quality, visibility, biases or map history.', '',
             'The scalar geometry score already includes accepted-count normalization and the fixed 3 m rotation lever scale. Holding those formulas fixed allows score/decision behavior to be inspected; it does not calibrate physical uncertainty or identify a scaling defect. The recorded six Schur flags and their fraction are retained in the exports. They describe detector-defined eigenspace degeneracy, not independently verified world-axis observability. No final rescaling or alternative threshold was tried.', '',
             '## Every failure remains visible', '',
             '| Method | Initial false-healthy seeds | Missed recovery seeds | Non-recovery seeds |',
             '| --- | --- | --- | --- |']
    for methods in METHODS.values():
        for m in methods:
            cohort=sorted([r for r in rows if r['method']==m],key=lambda r:int(r['seed']))
            lists=[', '.join(r['seed'] for r in cohort if predicate(r)) or 'None' for predicate in
                   [lambda r:r['false_healthy']=='True',lambda r:r['missed_recovery']=='True',lambda r:r['truth_status']!='RECOVERED']]
            text.append('| '+m+' | '+' | '.join(lists)+' |')
    text += ['', 'A seed can appear in more than one column and method. Non-recovery is not a recovery-detection miss. Relapse remains in the unchanged accepted event rows. Full flags, interval fractions, scores, control summaries and geometry dimensions are in [event diagnosis](event_diagnosis.csv); all primary windows and causal ticks are retained, including successful cases. No failed native slot was discarded; the two earlier workflow failures are documented in the accepted results and are not new native samples.', '',
             '## Illustrated timelines', '',
             'Choose the lowest selected seed per backend/method for initial false-healthy, missed recovery, successful detection, non-recovery and each observed miss-pattern category. Deduplicate backend/seed pairs. This deterministic rule was selected after results and only chooses illustrations; all events determine the summaries. The [selection receipt](case_selection.json) records every category and seed.', '',
             'Each plot has five aligned panels: accepted count with paired control; scalar score and locked threshold with paired control; corridor Schur score with the fixed 0.1 score boundary; primary local translation/rotation errors divided by their frozen limits; and confirmed-health states/new transition triangles. Errors are plotted at the actual window end, and only post-exit primary windows are shown. Blank pre-exit error space is not zero error. Log/symmetric-log axes preserve visible ranges; unavailable values remain gaps. Black is the independently fixed exit; green dashed is retrospective onset, green dotted its truth confirmation, purple a relapse when present. Truth does not feed the causal diagnostic.', '']
    for figure in figures:
        b,seed=figure['backend'],figure['seed']
        text += [f'### {b} seed {seed}', '',
                 f"![{b} seed {seed} aligned failure/success timeline](../../figures/final_failure_analysis_20261012/{figure['image']})", '',
                 'Illustrates: '+', '.join(figure['selection_categories'])+'.', '']
        for e in figure['events']:
            diagnosis=next(r for r in rows if r['backend']==b and int(r['seed'])==seed and r['method']==e['method'])
            text.append(f"- {e['method']}: truth {e['truth_status']}; initial false-healthy {e['false_healthy_in_initial_unrecovered_interval']}; post-onset detection {e['detected_post_onset']}; observed miss pattern `{diagnosis['miss_pattern']}`.")
        text.append('')
    text += ['## Interpretation and next decision', '',
             'The available evidence supports writing a bounded empirical evaluation of fixed-policy trade-offs, including the important distinction between recovered motion, active healthy state and a new recovery declaration. The investigation identifies decision-level explanations for misses and rejects a simplistic count-only story at the displayed group-summary level. It does not establish the physical reason for the width pattern or prove a novel mechanism.', '',
             'A manuscript can report these findings with the existing protocol/exposure disclosures. A stronger causal width or measurement-normalization claim would need a new, development-validated and frozen factor-controlled study on fresh geometry IDs. No such experiment, comparator or sample expansion was run here. Publication novelty still requires scientific review against the closest literature.', '',
             '## Verification and reproduction', '',
             'All consumed native manifests, pose/diagnostic streams and reference/metadata bytes were rehashed. All own-backend labels and event rows exactly matched the independently audited exports. Raw bags, Jacobian sidecars and offline evaluation CSVs were not reprocessed for this exploratory task. Five analytic miss-classification fixtures passed; the full suite ran 254 tests: 253 passed, one optional SciPy skip, with native reset compilation enabled. [Test log](regression_tests.log). This is author verification, not independent acceptance of the new analysis.', '',
             'From repository root, use the recorded isolated Python and fresh output directories:', '',
             '```bash',
             '"$RESEARCH_PY" research_paper/experiments/src/analyze_final_failure_cases.py \\',
             '  --root "$FINAL_ROOT" --output /tmp/failure-analysis-reproduction',
             '"$RESEARCH_PY" research_paper/experiments/src/plot_final_failure_cases.py \\',
             '  --evidence /tmp/failure-analysis-reproduction --output /tmp/failure-figures-reproduction',
             '```', '',
             'The plotter additionally reads the accepted analysis JSON files from the repository’s `research_paper/evidence/final_geometry_v2_results_20261012` directory and verifies their recorded hashes. The [report generator](../../experiments/src/write_final_failure_report.py) presents the checked-in exports and figures from repository root. [Analysis manifest](manifest.json) binds consumed files and derived outputs; [figure manifest](../../figures/final_failure_analysis_20261012/manifest.json) binds the images and selection. No frozen scientific file was modified.', '']
    (EVIDENCE/'FAILURE_ANALYSIS_REPORT.md').write_text('\n'.join(text))
    report_manifest={'scope':'Exploratory presentation; no tuning or new significance test',
        'analysis_manifest_sha256':sha256_file(EVIDENCE/'manifest.json'),
        'figure_manifest_sha256':sha256_file(FIGURES/'manifest.json'),
        'test_log_sha256':sha256_file(EVIDENCE/'regression_tests.log'),
        'report_generator_sha256':sha256_file(Path(__file__)),
        'report_sha256':sha256_file(EVIDENCE/'FAILURE_ANALYSIS_REPORT.md')}
    (EVIDENCE/'report_manifest.json').write_text(json.dumps(report_manifest,indent=2)+'\n')


if __name__=='__main__':write()
