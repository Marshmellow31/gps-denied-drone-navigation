"""Validate the reviewed final lifecycle on a retained development bag only."""
import argparse
import json
from pathlib import Path
import sys

import final_evaluation_runner as runner


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ros-env", type=Path, required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--run-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    args = parser.parse_args()
    declared = json.loads((args.input_dir / "manifest.json").read_text())
    if declared.get("role") != "development" or declared.get("seed") != 14 or declared.get("control") is not False:
        raise runner.FinalEvaluationError("R3 smoke accepts only the retained seed-14 development corridor")
    for name in ("sensors.bag", "reference.txt", "reference_metadata.json"):
        if runner.sha256_file(args.input_dir / name) != declared.get(name, {}).get("sha256"):
            raise runner.FinalEvaluationError(f"development input hash mismatch: {name}")
    binary = args.workspace / "devel/.private/fast_lio/lib/fast_lio/fastlio_mapping"
    backend = runner._check_backend(args.ros_env, args.workspace, binary)
    identity = {"role": "development_r3_smoke", "backend": backend,
                "runtime": runner._check_analysis_runtime(),
                "runner_sha256": runner.sha256_file(Path(runner.__file__)),
                "validation_script_sha256": runner.sha256_file(Path(__file__))}
    print("Verified the restored T14 binary and development input", flush=True)
    result = runner._run_scene(args.run_id, 14, "DEVELOPMENT", "CORRIDOR",
        args.input_dir, args.run_root, args.ros_env, args.workspace, backend["binary_sha256"],
        runner.LOCKED_DEVELOPMENT_THRESHOLD, identity)
    path = args.run_root / result["run_id"] / "run_manifest.json"
    saved = json.loads(path.read_text())
    summary = {"schema": "r3-development-validation-v1", "role": "development_only",
               "heldout_inputs_opened": False, "status": result["status"],
               "run_manifest_path": str(path.resolve()), "run_manifest_sha256": runner.sha256_file(path),
               "execution_identity": identity, "completion_validation": saved.get("completion_validation"),
               "postprocess_summaries": saved.get("postprocess_summaries"),
               "retained_output_hashes": saved.get("outputs"),
               "scientific_use": "Lifecycle verification only; excluded from calibration and primary event counts."}
    runner._write_json(args.output_manifest, summary)
    print(json.dumps({"status": result["status"], "completion": summary["completion_validation"]}))
    if result["status"] not in ("COMPLETED", "CACHED"):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
