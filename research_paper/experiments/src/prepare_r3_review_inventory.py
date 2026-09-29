"""Export hashes for a read-only, no-held-out R3 implementation review."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import final_evaluation_runner as runner


def main() -> None:
    root = runner.ROOT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", type=Path,
                        default=root / "research_paper/reviews/R3_IMPLEMENTATION.md")
    parser.add_argument("--output", type=Path,
                        default=root / "research_paper/evidence/R3_REVIEW_INPUT_HASHES.json")
    parser.add_argument("--native-run-root", type=Path,
                        help="Optional Acer folder containing the retained T16-R3-10 replay summaries and run manifest")
    args = parser.parse_args()
    artifacts = runner._r3_required_hashes(args.review)
    native_report = root / "research_paper/evidence/R3_NATIVE_SEED14_REPLAY_20260929.md"
    artifacts["T16-R3-10 native replay report"] = runner.sha256_file(native_report)
    pointlio_audit = root / "research_paper/evidence/POINTLIO_INDICATOR_PARITY_AUDIT_20260929.md"
    artifacts["Point-LIO indicator comparability audit"] = runner.sha256_file(pointlio_audit)
    if args.native_run_root is not None:
        native_root = args.native_run_root.resolve()
        native_files = {
            "T16-R3-10 completed summary": native_root / "r3_development_validation_completed.json",
            "T16-R3-10 cached-resume summary": native_root / "r3_development_validation_cached_resume.json",
            "T16-R3-10 native run manifest": native_root / "R3_NATIVE_SEED14_20260929_A1/run_manifest.json",
        }
        missing = [name for name, path in native_files.items() if not path.is_file()]
        if missing:
            raise FileNotFoundError(f"native replay evidence is missing: {', '.join(missing)}")
        artifacts.update({name: runner.sha256_file(path) for name, path in native_files.items()})
    bundle = {
        "schema": "r3-review-input-inventory-v1",
        "status": "PREPARED_FOR_INDEPENDENT_REVIEW",
        "heldout_inputs_opened": False,
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
    }
    runner._write_json(args.output, bundle)
    print(f"Prepared {len(artifacts)} named hashes; no held-out data were accessed.")
    print(f"Inventory SHA-256: {runner.sha256_file(args.output)}")


if __name__ == "__main__":
    main()
