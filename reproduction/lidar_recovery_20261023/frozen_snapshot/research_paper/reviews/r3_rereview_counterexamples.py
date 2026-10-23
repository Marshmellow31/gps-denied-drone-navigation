"""Independent R3 repair regressions: temporary fixtures, no geometry/LIO.

Run with the frozen Python. These assertions check that the cited R3 defects
are rejected or represented as unavailable evidence after the repairs.
"""
import json
import os
from pathlib import Path
import signal
import shutil
import subprocess
import sys
import tempfile
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "research_paper/experiments/src"),
                str(ROOT / "research_paper/experiments/tests")]
import final_evaluation_runner as r
from test_final_run_lifecycle import complete_streams, write_csv
from test_final_evaluation_runner import FinalEvaluationRunnerTests


def missing_estimates():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        summaries = complete_streams(root)
        # All 600 health/Hessian updates and playback completion are present.
        # The estimator processed later scans but emitted no later odometry.
        poses = r._read_tsv_or_csv(root / "poses.csv")[:300]
        write_csv(root / "poses.csv", list(poses[0]), poses)
        write_csv(root / "evaluation.csv", ["timestamp_ns", "window_s"],
                  [{"timestamp_ns": p["timestamp_ns"], "window_s": w}
                   for p in poses for w in (1, 3)])
        (root / "pose_logger.log").write_text(
            "pose logger counts: " + repr({"valid": 300, "invalid": 0, "resets": 0}))
        summaries[2]["rows"] = 600
        result = r.validate_completed_streams(root, {"scans": 600}, *summaries)
        assert result["last_pose_timestamp_ns"] < 1_059_800_000_000
        assert result["completion_status"] == "FULL_SENSOR_INPUT_AND_FLUSHED_POSE_LOG"
        print("T16-R3-02: full playback with missing trailing estimates stays completed; later windows remain unavailable")


def missing_inventory_dependency():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        review, freeze = root / "review.md", root / "freeze.md"
        review.write_text("**Gate:** PASS\n")
        inventory = r._r3_required_hashes(review)
        freeze.write_text(FinalEvaluationRunnerTests.freeze_text(inventory))
        original_hash = r.sha256_file
        omitted = ROOT / "research_paper/experiments/src/audit_simulation_scene.py"
        consulted = []
        def mutated_hash(path):
            consulted.append(Path(path).resolve())
            return "0" * 64 if Path(path).resolve() == omitted else original_hash(path)
        with patch.object(r, "sha256_file", side_effect=mutated_hash):
            try:
                r._require_r3_pass(review, freeze)
            except r.FinalEvaluationError as exc:
                print("T16-R3-03: changed scene-screen dependency invalidates the R2/R3 content bundle:", exc)
            else:
                raise AssertionError("mutated scene-audit dependency passed the R3 gate")
        assert omitted in consulted
        assert omitted in {ROOT / "research_paper/experiments/src/audit_simulation_scene.py"}


def missing_cached_provenance():
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        helper = FinalEvaluationRunnerTests()
        analysis, plan, gate, screen = helper.make_screen_fixture(root)
        screen_path, review, freeze = root / "screen.json", root / "review.md", root / "freeze.md"
        screen_path.write_text(json.dumps(screen))
        review.write_text("fixture")
        freeze.write_text("FASTLIO_MIN_EIG_G3 " + str(r.LOCKED_DEVELOPMENT_THRESHOLD))
        runtime, backend = {"fixture": "runtime"}, {"binary_sha256": "fixture"}
        identity = {**gate, "runtime": runtime, "backend": backend,
                    "plan_sha256": r.sha256_file(plan), "screen_sha256": r.sha256_file(screen_path),
                    "analysis_sha256": r.sha256_file(analysis)}
        results = root / "results"
        for stratum, seeds in screen["selected_seeds_by_stratum"].items():
            for seed in seeds:
                scenes = []
                for scene in ("CORRIDOR", "CONTROL"):
                    run_id = f"fixture_{stratum}_{seed}_{scene}"
                    run_dir = results / "runs" / run_id
                    run_dir.mkdir(parents=True)
                    (run_dir / "output.txt").write_text("unchanged completed fixture output")
                    r._write_json(run_dir / "run_manifest.json", {
                        "status": "COMPLETED", "scene": scene, "seed": seed, "stratum": stratum,
                        "completion_validation": {"fixture": True},
                        "outputs": {"output.txt": r.sha256_file(run_dir / "output.txt")},
                        "fingerprint": {"execution_identity": identity}})
                    scenes.append({"status": "COMPLETED", "run_id": run_id})
                r._write_json(results / "pairs" / f"{stratum}_{seed}.json", {
                    "status": "COMPLETED", "scene_screen_sha256": r.sha256_file(screen_path),
                    "development_analysis_sha256": r.sha256_file(analysis),
                    "execution_identity": identity, "scene_runs": scenes,
                    "corridor_manifest_sha256": "missing", "control_manifest_sha256": "missing",
                    "reference_sha256": "missing"})
        # Same state as losing archived inputs/reference after scratch cleanup.
        assert not (results / "shared_reference.txt").exists()
        assert not (results / "inputs").exists()
        screens = {(row["seed"], row["stratum"]): row for row in screen["screened_layouts"]}
        with patch.object(r, "T16_ANALYSIS_MANIFEST", analysis), \
             patch.object(r, "FINAL_PLAN", plan), \
             patch.object(r, "_require_r3_pass", return_value=gate), \
             patch.object(r, "_check_analysis_runtime", return_value=runtime), \
             patch.object(r, "_check_backend", return_value=backend), \
             patch.object(r.heldout, "screen_layout", side_effect=lambda seed, stratum: screens[seed, stratum]), \
             patch.object(r.heldout, "sample_layout", side_effect=AssertionError("forbidden geometry")), \
             patch.object(r.heldout, "write_sensor_input", side_effect=AssertionError("forbidden input")), \
             patch.object(r, "_prepare_pair", side_effect=r.FinalEvaluationError(
                 "required raw input and reference provenance are unavailable")) as prepare:
            result = r.execute_final_batch(screen_path, plan, analysis, review, freeze,
                root / "ros", root / "ws", root / "binary", root / "scratch", results)
        assert result["status"] == "INCOMPLETE_KEEP_FAILURES" and result["completed_geometry_pairs"] == 0
        assert prepare.call_count == 48
        assert all(json.loads(path.read_text())["status"] == "FAILED_KEEP_INPUTS"
                   for path in (results / "pairs").glob("*.json"))
        print("T16-R3-03/06: cached outputs without reproducible sensor inputs/reference are rejected and kept failed")


def wrapper_exit_and_orphan():
    # Execute the exact worker-supervision functions with a harmless failed child.
    script = r.FINAL_RUN_SCRIPT.read_text()
    start = script.index("sim_pid_running() {")
    end = script.index("trap cleanup EXIT")
    functions = script[start:end]
    command = "set -euo pipefail\nsim_worker_pids=()\ndeclare -A sim_worker_names=()\n" + functions
    command += "bash -c 'exit 7' &\nsim_pid=$!\nsim_worker_pids+=(\"$sim_pid\")\nsim_worker_names[$sim_pid]=FAST-LIO\nsleep .05\nif sim_require_workers; then exit 1; fi\n"
    result = subprocess.run(["bash", "-c", command], capture_output=True)
    assert result.returncode == 0 and b"FAST-LIO exited before" in result.stderr
    print("T16-R3-02: exact wrapper supervisor detects a failed backend child before marking replay complete")
    # An actual wrapper can disappear while its process group still runs.
    process = subprocess.Popen(["/usr/bin/time", "bash", "-c", "sleep 30"],
                               start_new_session=True, stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
    try:
        time.sleep(.1)
        process.kill()
        process.wait(timeout=2)
        assert r._process_identity(process.pid) is None
        members = r._process_group_members(process.pid)
        assert members
        print(f"T16-R3-06: dead wrapper PID is detected as an orphaned run group with live members {members}")
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def completed_pair_cache_after_scratch_cleanup():
    """A later call re-generates identical inputs and reuses completed outputs."""
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        helper = FinalEvaluationRunnerTests()
        analysis, plan, gate, screen = helper.make_screen_fixture(root)
        screen_path, review, freeze = root / "screen.json", root / "review.md", root / "freeze.md"
        screen_path.write_text(json.dumps(screen))
        review.write_text("fixture review")
        freeze.write_text("FASTLIO_MIN_EIG_G3 " + str(r.LOCKED_DEVELOPMENT_THRESHOLD))
        runtime, backend = {"fixture": "runtime"}, {"binary_sha256": "fixture"}
        identity = {**gate, "runtime": runtime, "backend": backend,
                    "plan_sha256": r.sha256_file(plan), "screen_sha256": r.sha256_file(screen_path),
                    "analysis_sha256": r.sha256_file(analysis)}
        results, scratch = root / "results", root / "scratch"
        run_root, pair_root = results / "runs", results / "pairs"
        shared_reference = results / "shared_reference.txt"
        shared_reference.parent.mkdir(parents=True)
        shared_reference.write_text("one analytic reference shared by every fixture pair\n")
        paired_audit = {"paired_imu_identical": True, "fixture_only": True}
        reference_sha = r.sha256_file(shared_reference)

        def write_input(path, seed, stratum, control, generation):
            path.mkdir(parents=True)
            bag = f"fixture bag {stratum} {seed} {int(control)}\n".encode()
            (path / "sensors.bag").write_bytes(bag)
            (path / "reference.txt").write_bytes(shared_reference.read_bytes())
            (path / "reference_metadata.json").write_text("{\"fixture\":true}\n")
            manifest = {
                "role": "heldout", "seed": seed, "stratum": stratum, "control": control,
                "truth_in_sensor_bag": False, "scans": 600, "imu_messages": 12021,
                "route_profile": {"profile_id": r.PROFILE_ID},
                "generator_sha256": r.sha256_file(Path(r.heldout.__file__)),
                "simulator_sha256": r.sha256_file(ROOT / "research_paper/experiments/src/simulate_lidar.py"),
                "formal_route_sha256": r.sha256_file(ROOT / "research_paper/experiments/src/t14_formal_route.py"),
                "runtime_s": float(generation) / 10.0,
                "code_revision": f"fixture-commit-{generation}",
            }
            for name in ("sensors.bag", "reference.txt", "reference_metadata.json"):
                artifact = path / name
                manifest[name] = {"size_bytes": artifact.stat().st_size,
                                  "sha256": r.sha256_file(artifact)}
            r._write_json(path / "manifest.json", manifest)
            return manifest

        screens = {(row["seed"], row["stratum"]): row for row in screen["screened_layouts"]}
        scratch_generations = 0
        for stratum, seeds in screen["selected_seeds_by_stratum"].items():
            for seed in seeds:
                inputs = {}
                manifests = {}
                for scene, control in (("CORRIDOR", False), ("CONTROL", True)):
                    original = root / "original_inputs" / f"{stratum}_{seed}" / scene
                    manifests[scene] = write_input(original, seed, stratum, control, 0)
                    inputs[scene] = original
                    archive = results / "inputs" / f"{stratum}_{seed}" / scene
                    archive.mkdir(parents=True, exist_ok=True)
                    for name in ("manifest.json", "reference_metadata.json"):
                        shutil.copy2(original / name, archive / name)
                scene_runs = []
                for scene in ("CORRIDOR", "CONTROL"):
                    manifest = manifests[scene]
                    input_dir = inputs[scene]
                    run_id = f"fixture_{stratum}_{seed}_{scene}"
                    run_dir = run_root / run_id
                    run_dir.mkdir(parents=True)
                    output = run_dir / "output.txt"
                    output.write_text("verified completed fixture output\n")
                    fingerprint = {
                        "sensor_bag_sha256": manifest["sensors.bag"]["sha256"],
                        "input_manifest_sha256": r._input_manifest_identity(manifest),
                        "input_manifest_file_sha256": r.sha256_file(input_dir / "manifest.json"),
                        "reference_metadata_sha256": r.sha256_file(input_dir / "reference_metadata.json"),
                        "reference_sha256": manifest["reference.txt"]["sha256"],
                        "threshold_from_development_manifest": r.LOCKED_DEVELOPMENT_THRESHOLD,
                        "execution_identity": identity,
                    }
                    r._write_json(run_dir / "run_manifest.json", {
                        "status": "COMPLETED", "scene": scene, "seed": seed, "stratum": stratum,
                        "completion_validation": {"fixture": True}, "fingerprint": fingerprint,
                        "outputs": {"output.txt": r.sha256_file(output)},
                    })
                    scene_runs.append({"status": "COMPLETED", "run_id": run_id})
                r._write_json(pair_root / f"{stratum}_{seed}.json", {
                    "status": "COMPLETED", "stratum": stratum, "seed": seed,
                    "scene_screen_sha256": r.sha256_file(screen_path),
                    "development_analysis_sha256": r.sha256_file(analysis),
                    "execution_identity": identity,
                    "corridor_manifest_sha256": r.sha256_file(inputs["CORRIDOR"] / "manifest.json"),
                    "control_manifest_sha256": r.sha256_file(inputs["CONTROL"] / "manifest.json"),
                    "corridor_manifest_identity_sha256": r._input_manifest_identity(manifests["CORRIDOR"]),
                    "control_manifest_identity_sha256": r._input_manifest_identity(manifests["CONTROL"]),
                    "corridor_bag_sha256": manifests["CORRIDOR"]["sensors.bag"]["sha256"],
                    "control_bag_sha256": manifests["CONTROL"]["sensors.bag"]["sha256"],
                    "reference_sha256": reference_sha, "paired_bag_audit": paired_audit,
                    "scene_runs": scene_runs,
                })

        def regenerate(first_dir, results_root, _, seed, stratum, __, ___, ____):
            nonlocal scratch_generations
            scratch_generations += 1
            corridor = first_dir / "corridor"
            control = first_dir / "control"
            left = write_input(corridor, seed, stratum, False, scratch_generations)
            right = write_input(control, seed, stratum, True, scratch_generations)
            # Variable work time belongs to this attempt record, never the input manifest.
            r._write_json(results_root / "input_attempts" / f"{stratum}_{seed}_A1.json", {
                "schema": "fixture-attempt", "generation_runtime_s": float(scratch_generations) / 100.0})
            return first_dir, corridor, control, left, right, paired_audit

        with patch.object(r, "T16_ANALYSIS_MANIFEST", analysis), \
             patch.object(r, "FINAL_PLAN", plan), \
             patch.object(r, "_require_r3_pass", return_value=gate), \
             patch.object(r, "_check_analysis_runtime", return_value=runtime), \
             patch.object(r, "_check_backend", return_value=backend), \
             patch.object(r.heldout, "screen_layout", side_effect=lambda seed, stratum: screens[seed, stratum]), \
             patch.object(r.heldout, "sample_layout", side_effect=AssertionError("forbidden geometry")), \
             patch.object(r.heldout, "write_sensor_input", side_effect=AssertionError("forbidden real generator")), \
             patch.object(r, "_prepare_pair", side_effect=regenerate) as prepare, \
             patch.object(r, "_run_scene", side_effect=AssertionError("estimator relaunch")) as replay:
            for repeat in range(2):
                if repeat:
                    shutil.rmtree(scratch)
                result = r.execute_final_batch(screen_path, plan, analysis, review, freeze,
                    root / "ros", root / "ws", root / "binary", scratch, results)
                assert result["status"] == "COMPLETED" and result["completed_geometry_pairs"] == 48
                assert not list(scratch.iterdir())
        assert prepare.call_count == 96 and scratch_generations == 96
        replay.assert_not_called()
        print("T16-R3-09: all 48 completed pairs remained cached after scratch removal and regenerated setup timing; no estimator replay occurred")


if __name__ == "__main__":
    missing_estimates()
    missing_inventory_dependency()
    missing_cached_provenance()
    completed_pair_cache_after_scratch_cleanup()
    wrapper_exit_and_orphan()
