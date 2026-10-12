"""Bind the revised geometry workflow to corrected development operating points.

Original R2 files and generator remain preserved. Version-two final execution
requires a new exact R3 inventory and freeze, including the geometry amendment.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path

import final_evaluation_runner as execution

ROOT = execution.ROOT
FAST_ANALYSIS = ROOT / 'research_paper/evidence/development_analysis_20261010/fastlio_development_manifest.json'
FAST_CANDIDATES = ROOT / 'research_paper/evidence/development_analysis_20261010/fastlio_threshold_candidates.csv'
POINT_ANALYSIS = ROOT / 'research_paper/evidence/development_analysis_20261010/pointlio_development_manifest.json'
POINT_CANDIDATES = ROOT / 'research_paper/evidence/development_analysis_20261010/pointlio_threshold_candidates.csv'
POINT_FREEZE = ROOT / 'research_paper/protocol/POINTLIO_REPLICATION_FREEZE_20261010.json'
POINT_FREEZE_REVIEW = ROOT / 'research_paper/reviews/POINTLIO_REPLICATION_FREEZE_REVIEW_20261010.md'
POINT_DEVELOPMENT_REVIEW = ROOT / 'research_paper/reviews/POINTLIO_DEVELOPMENT_ACCEPTANCE_20261010.md'
FAST_DEVELOPMENT_REVIEW = ROOT / 'research_paper/reviews/FASTLIO_DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md'
FINAL_PLAN = ROOT / 'research_paper/evidence/FINAL_HELDOUT_PLAN_GEOMETRY_V2_20261012.json'

_original_build_plan = execution.build_plan
_original_required_hashes = execution._r3_required_hashes


def _validate_point_freeze() -> tuple[dict, dict, str, str]:
    paths = (FAST_ANALYSIS, FAST_CANDIDATES, POINT_ANALYSIS, POINT_CANDIDATES,
             POINT_FREEZE, POINT_FREEZE_REVIEW)
    if any(not path.is_file() for path in paths):
        raise execution.FinalEvaluationError('corrected analysis or Point-LIO freeze evidence is missing')
    fast = json.loads(FAST_ANALYSIS.read_text())
    point = json.loads(POINT_ANALYSIS.read_text())
    freeze = json.loads(POINT_FREEZE.read_text())
    freeze_review = POINT_FREEZE_REVIEW.read_text()
    freeze_sha = execution.sha256_file(POINT_FREEZE)
    review_sha = execution.sha256_file(POINT_FREEZE_REVIEW)
    point_selection = point.get('pointlio_threshold_selection', {})
    frozen_selection = freeze.get('locked_development_selection', {})
    if (fast.get('status') != 'DONE' or fast.get('role') != 'development_only'
            or fast.get('heldout_inputs_opened') is not False
            or point.get('status') != 'DONE_DEVELOPMENT_ONLY'
            or point.get('heldout_inputs_opened') is not False
            or freeze.get('heldout_inputs_opened') is not False
            or freeze.get('heldout_generation_or_replay_authorized') is not False
            or freeze.get('analysis', {}).get('analysis_manifest_sha256')
                != execution.sha256_file(POINT_ANALYSIS)
            or freeze.get('analysis', {}).get('candidate_csv_sha256')
                != execution.sha256_file(POINT_CANDIDATES)
            or point_selection.get('threshold') != frozen_selection.get('threshold')
            or point_selection.get('threshold') is None
            or freeze.get('protocol', {}).get('r2_freeze_sha256')
                != execution.sha256_file(ROOT / 'research_paper/protocol/FREEZE.md')
            or freeze.get('protocol', {}).get('pointlio_amendment_sha256')
                != execution.sha256_file(ROOT / 'research_paper/protocol/POINTLIO_REPLICATION_AMENDMENT_20260929.md')
            or 'Decision: PASS' not in freeze_review
            or freeze_sha not in freeze_review):
        raise execution.FinalEvaluationError('corrected development evidence does not match its accepted Point-LIO freeze')
    if float(fast['fastlio_threshold_selection']['threshold']) != execution.LOCKED_DEVELOPMENT_THRESHOLD:
        raise execution.FinalEvaluationError('corrected FAST-LIO manifest differs from the locked operating point')
    return fast, point, freeze_sha, review_sha


def _required_hashes(review_path: Path):
    _, point, point_freeze_sha, point_freeze_review_sha = _validate_point_freeze()
    previous_t16, previous_plan = execution.T16_ANALYSIS_MANIFEST, execution.FINAL_PLAN
    try:
        execution.T16_ANALYSIS_MANIFEST = FAST_ANALYSIS
        execution.FINAL_PLAN = FINAL_PLAN
        result = _original_required_hashes(review_path)
    finally:
        execution.T16_ANALYSIS_MANIFEST, execution.FINAL_PLAN = previous_t16, previous_plan
    additional = {
        'geometry v2 generator': ROOT / 'research_paper/experiments/src/heldout_simulation_v2.py',
        'geometry v2 split': execution.SPLITS_PATH,
        'R2 geometry amendment': ROOT / 'research_paper/reviews/R2_GEOMETRY_AMENDMENT_20261012.md',
        'geometry revision proposal': ROOT / 'research_paper/protocol/GEOMETRY_REVISION_PROPOSAL_20261012.json',
        'geometry development validator': ROOT / 'research_paper/experiments/src/validate_geometry_development_input.py',
        'geometry development recorder': ROOT / 'research_paper/experiments/src/record_geometry_development_attempt.py',
        'geometry Point-LIO native wrapper': ROOT / 'research_paper/experiments/run_point_lio_geometry_development.sh',
        'geometry native validation runner': ROOT / 'research_paper/experiments/src/run_geometry_native_validation.py',
        'geometry v2 workflow tests': ROOT / 'research_paper/experiments/tests/test_geometry_v2_workflow.py',
        'geometry revision tests': ROOT / 'research_paper/experiments/tests/test_geometry_revision_dev.py',
        'geometry native validation summary': ROOT / 'research_paper/evidence/geometry_v2_native_validation_20261012.json',
        'geometry native validation report': ROOT / 'research_paper/evidence/GEOMETRY_V2_NATIVE_VALIDATION_20261012.md',
        'geometry v2 readiness test log': ROOT / 'research_paper/evidence/geometry_v2_readiness_tests_20261012.log',
        'geometry v2 inventory builder': ROOT / 'research_paper/experiments/src/prepare_geometry_r3_inventory.py',
        'corrected FAST-LIO development manifest': FAST_ANALYSIS,
        'corrected FAST-LIO candidate table': FAST_CANDIDATES,
        'corrected Point-LIO development manifest': POINT_ANALYSIS,
        'corrected Point-LIO candidate table': POINT_CANDIDATES,
        'Point-LIO development acceptance': POINT_DEVELOPMENT_REVIEW,
        'Point-LIO replication freeze': POINT_FREEZE,
        'Point-LIO replication freeze review': POINT_FREEZE_REVIEW,
        'FAST-LIO corrected analysis acceptance': FAST_DEVELOPMENT_REVIEW,
        'corrected development analysis report': ROOT / 'research_paper/evidence/DEVELOPMENT_ANALYSIS_ACCEPTANCE_20261010.md',
        'fresh primary recovery report': ROOT / 'research_paper/evidence/PRIMARY_DEVELOPMENT_RECOVERY_20261009.md',
        'fresh primary recovery audit': ROOT / 'research_paper/evidence/primary_recovery_complete_audit_20261009.json',
        'fresh primary repeatability audit': ROOT / 'research_paper/evidence/primary_recovery_repeatability_20261009.json',
        'fresh primary recovery acceptance': ROOT / 'research_paper/reviews/PRIMARY_RECOVERY_ACCEPTANCE_20261009.md',
        'FAST-LIO corrected scalar event metrics': ROOT / 'research_paper/evidence/development_analysis_20261010/fastlio_event_metrics.csv',
        'FAST-LIO corrected DCReg event metrics': ROOT / 'research_paper/evidence/development_analysis_20261010/fastlio_dcreg_event_metrics.csv',
        'FAST-LIO corrected truth labels': ROOT / 'research_paper/evidence/development_analysis_20261010/fastlio_truth_labels.csv',
        'Point-LIO corrected scalar event metrics': ROOT / 'research_paper/evidence/development_analysis_20261010/pointlio_scalar_event_metrics.csv',
        'Point-LIO corrected DCReg event metrics': ROOT / 'research_paper/evidence/development_analysis_20261010/pointlio_dcreg_event_metrics.csv',
        'Point-LIO corrected truth labels': ROOT / 'research_paper/evidence/development_analysis_20261010/pointlio_truth_labels.csv',
        'final dataset analysis caller': ROOT / 'research_paper/experiments/src/final_dataset_analysis.py',
        'final dataset analysis tests': ROOT / 'research_paper/experiments/tests/test_final_dataset_analysis.py',
        'held-out statistics': ROOT / 'research_paper/experiments/src/heldout_statistics.py',
        'held-out statistics tests': ROOT / 'research_paper/experiments/tests/test_heldout_statistics.py',
        'R3 evaluation workflow tests': ROOT / 'research_paper/experiments/tests/test_r3_evaluation_workflow.py',
        'development signal figure manifest': ROOT / 'research_paper/figures/development_signal_comparison_20261010/figure_manifest.json',
        'R3 readiness full-suite log': ROOT / 'research_paper/evidence/r3_readiness_tests_20261010.log',
        'R3 evaluation workflow': Path(__file__).resolve(),
        'Point-LIO final replication runner': ROOT / 'research_paper/experiments/src/run_pointlio_final_replication.py',
        'Point-LIO final analysis': ROOT / 'research_paper/experiments/src/pointlio_final_analysis.py',
        'Point-LIO final native wrapper': ROOT / 'research_paper/experiments/run_point_lio_final_replication.sh',
        'Point-LIO final recorder': ROOT / 'research_paper/experiments/src/record_pointlio_final_attempt.py',
        'Point-LIO final verifier': ROOT / 'research_paper/experiments/src/verify_pointlio_final_attempt.py',
        'Point-LIO final input validator': ROOT / 'research_paper/experiments/src/validate_pointlio_final_input.py',
        'Point-LIO final workflow tests': ROOT / 'research_paper/experiments/tests/test_pointlio_final_workflow.py',
        'Point-LIO launch helper': ROOT / 'research_paper/experiments/src/pointlio_runner_helpers.sh',
        'Point-LIO development input validator': ROOT / 'research_paper/experiments/src/validate_pointlio_development_input.py',
        'Point-LIO indicator exporter': ROOT / 'research_paper/experiments/src/pointlio_indicator_export.py',
        'Point-LIO information adapter': ROOT / 'research_paper/experiments/src/pointlio_information.py',
        'Point-LIO pose logger': ROOT / 'research_paper/experiments/src/pointlio_pose_logger.py',
        'Point-LIO base attempt recorder': ROOT / 'research_paper/experiments/src/record_pointlio_attempt.py',
        'Point-LIO input frame audit': ROOT / 'research_paper/experiments/src/audit_pointlio_input_frames.py',
        'Point-LIO feasibility output verifier': ROOT / 'research_paper/experiments/src/verify_pointlio_feasibility_pair.py',
        'Point-LIO simulation clock drain helper': ROOT / 'research_paper/experiments/src/drain_sim_clock.py',
        'Point-LIO accepted native identity anchor': ROOT / 'research_paper/evidence/pointlio_native_identity_20261009.json',
        'OCE overlap addendum': ROOT / 'research_paper/literature/RECOVERY_OVERLAP_ADDENDUM_20261010.md',
        'OCE novelty feasibility review': ROOT / 'research_paper/reviews/OCE_NOVELTY_FEASIBILITY_20261010.md',
        'Point-LIO simulation development config': ROOT / 'research_paper/configs/point_lio_simulation_development.yaml',
        'Point-LIO build compatibility patch': ROOT / 'research_paper/experiments/patches/point_lio_build_compat.patch',
        'Point-LIO deque header patch': ROOT / 'research_paper/experiments/patches/point_lio_deque_header.patch',
        'Point-LIO indicator sidecar patch': ROOT / 'research_paper/experiments/patches/point_lio_indicator_sidecar.patch',
        'Point-LIO development runner': ROOT / 'research_paper/experiments/src/run_pointlio_development.py',
        'Point-LIO development analysis': ROOT / 'research_paper/experiments/src/pointlio_development_analysis.py',
        'Point-LIO development attempt verifier': ROOT / 'research_paper/experiments/src/verify_pointlio_development_attempt.py',
        'Point-LIO indicator feasibility script': ROOT / 'research_paper/experiments/run_point_lio_indicator_feasibility.sh',
        'Point-LIO smoke script': ROOT / 'research_paper/experiments/run_point_lio_smoke.sh',
        'Point-LIO development workflow tests': ROOT / 'research_paper/experiments/tests/test_pointlio_development_workflow.py',
        'Point-LIO indicator export tests': ROOT / 'research_paper/experiments/tests/test_pointlio_indicator_export.py',
        'Point-LIO information adapter tests': ROOT / 'research_paper/experiments/tests/test_pointlio_information.py',
        'Point-LIO native sidecar tests': ROOT / 'research_paper/experiments/tests/test_pointlio_native_sidecar.py',
        'Point-LIO pose logger tests': ROOT / 'research_paper/experiments/tests/test_pointlio_pose_logger.py',
        'Point-LIO runner helpers tests': ROOT / 'research_paper/experiments/tests/test_pointlio_runner_helpers.py',
        'Point-LIO feasibility pair tests': ROOT / 'research_paper/experiments/tests/test_pointlio_feasibility_pair.py',
        'Point-LIO attempt recorder tests': ROOT / 'research_paper/experiments/tests/test_pointlio_attempt_recorder.py',
        'Point-LIO one-seed acceptance': ROOT / 'research_paper/reviews/POINTLIO_ONE_SEED_ACCEPTANCE_20261009.md',
        'Point-LIO indicator parity audit': ROOT / 'research_paper/evidence/POINTLIO_INDICATOR_PARITY_AUDIT_20260929.md',
        'Point-LIO development workflow full suite log': ROOT / 'research_paper/evidence/development_workflow_full_tests_20261010.log',
        'primary recovery audit script': ROOT / 'research_paper/experiments/src/audit_primary_recovery.py',
        'primary recovery runner': ROOT / 'research_paper/experiments/src/recover_primary_development.py',
        'primary recovery tests': ROOT / 'research_paper/experiments/tests/test_primary_recovery.py',
        'development signal comparison plotter': ROOT / 'research_paper/experiments/src/plot_development_signal_comparison.py',
    }
    missing = [name for name, path in additional.items() if not path.is_file()]
    if missing:
        raise execution.FinalEvaluationError('R3 analysis inventory artifacts missing: ' + ', '.join(missing))
    result.update({name: execution.sha256_file(path) for name, path in additional.items()})
    result['POINTLIO_BINARY_SHA256'] = '80516da9cafba98262d56c17cc26ec4da76e214049d3af7776248b4c3a342b17'
    result['POINTLIO_UPSTREAM_COMMIT'] = '4b86a469eb5572e70ed575af25b5f15dd06e8e3c'
    return result


def build_plan(analysis_path: Path, splits_path: Path):
    if Path(analysis_path).resolve() != FAST_ANALYSIS.resolve():
        raise execution.FinalEvaluationError('R3 plan must use the corrected FAST-LIO analysis manifest')
    _, point, point_freeze_sha, point_freeze_review_sha = _validate_point_freeze()
    plan = _original_build_plan(FAST_ANALYSIS, splits_path)
    plan.update(geometry_profile=execution.heldout.GEOMETRY_PROFILE,
                original_geometry_ids_excluded=[100, 179],
                geometry_design_adapted_to_failed_screen=True,
                r2_geometry_amendment_sha256=execution.sha256_file(ROOT / "research_paper/reviews/R2_GEOMETRY_AMENDMENT_20261012.md"))
    plan.update(
        pointlio_development_analysis_sha256=execution.sha256_file(POINT_ANALYSIS),
        pointlio_replication_freeze_sha256=point_freeze_sha,
        pointlio_replication_freeze_review_sha256=point_freeze_review_sha,
        pointlio_locked_final_threshold=point['pointlio_threshold_selection']['threshold'],
        pointlio_final_runner_sha256=execution.sha256_file(ROOT / 'research_paper/experiments/src/run_pointlio_final_replication.py'),
        pointlio_final_analysis_sha256=execution.sha256_file(ROOT / 'research_paper/experiments/src/pointlio_final_analysis.py'),
        oce_novelty_review_sha256=execution.sha256_file(ROOT / 'research_paper/reviews/OCE_NOVELTY_FEASIBILITY_20261010.md'),
        r3_evaluation_workflow_sha256=execution.sha256_file(Path(__file__).resolve()),
    )
    return plan


def require_r3_pass(review_path: Path, freeze_path: Path):
    previous_t16, previous_plan = execution.T16_ANALYSIS_MANIFEST, execution.FINAL_PLAN
    previous_required = execution._r3_required_hashes
    try:
        execution.T16_ANALYSIS_MANIFEST = FAST_ANALYSIS
        execution.FINAL_PLAN = FINAL_PLAN
        execution._r3_required_hashes = _required_hashes
        result = execution._require_r3_pass(review_path, freeze_path)
    finally:
        execution.T16_ANALYSIS_MANIFEST, execution.FINAL_PLAN = previous_t16, previous_plan
        execution._r3_required_hashes = previous_required
    _, point, _, _ = _validate_point_freeze()
    if freeze_path.is_file():
        freeze = freeze_path.read_text(encoding="utf-8")
        blocks = __import__("re").findall(r"```json\s*(.*?)```", freeze, __import__("re").DOTALL)
        bundles = [json.loads(block) for block in blocks]
        matching = [bundle for bundle in bundles if isinstance(bundle, dict)
                    and bundle.get("schema") == "r3-implementation-freeze-v1"]
        if matching and matching[0].get("POINTLIO_MIN_EIG_G3_threshold") != point['pointlio_threshold_selection']['threshold']:
            raise execution.FinalEvaluationError("implementation freeze does not lock the exact Point-LIO threshold")
    result["POINTLIO_MIN_EIG_G3_threshold"] = point['pointlio_threshold_selection']['threshold']
    return result


@contextmanager
def corrected_runner_context():
    """Temporarily configure CLI screen/replay while preserving old source state."""
    previous = (execution.T16_ANALYSIS_MANIFEST, execution.FINAL_PLAN,
                execution.build_plan, execution._r3_required_hashes)
    try:
        execution.T16_ANALYSIS_MANIFEST = FAST_ANALYSIS
        execution.FINAL_PLAN = FINAL_PLAN
        execution.build_plan = build_plan
        execution._r3_required_hashes = _required_hashes
        yield execution
    finally:
        (execution.T16_ANALYSIS_MANIFEST, execution.FINAL_PLAN,
         execution.build_plan, execution._r3_required_hashes) = previous


def main():
    with corrected_runner_context():
        execution.main()


if __name__ == '__main__':
    main()
