import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import t14_development_runner as runner


class T14DevelopmentRunnerTests(unittest.TestCase):
    def test_full_schedule_has_64_primary_and_four_predeclared_repeat_runs(self):
        schedule = runner.build_schedule(list(range(14, 46)))
        self.assertEqual(len(schedule), 68)
        primary = [row for row in schedule if not row["repeat"]]
        repeats = [row for row in schedule if row["repeat"]]
        self.assertEqual(len(primary), 64)
        self.assertEqual(len(repeats), 4)
        self.assertEqual({row["seed"] for row in repeats}, {14, 45})
        self.assertEqual(len({row["run_id"] for row in schedule}), 68)

    def test_repeat_schedule_uses_first_and_last_eligible_seed_only(self):
        schedule = runner.build_schedule([18, 23, 31])
        repeats = [row for row in schedule if row["repeat"]]
        self.assertEqual({row["seed"] for row in repeats}, {18, 31})

    def test_held_out_seeds_cannot_enter_a_schedule(self):
        with self.assertRaises(ValueError):
            runner.build_schedule([14, 100])

    def test_formal_entry_association_uses_epoch_plus_10_point_5_seconds(self):
        manifest = {"route_profile": {"entry_time_s": 10.5}}
        self.assertEqual(runner.evaluation_entry_start_ns(manifest), 1010500000000)

    def test_resume_cache_requires_the_same_fingerprint_and_intact_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            run_dir = Path(directory)
            artifact = run_dir / "stream.csv"
            artifact.write_text("checked\n", encoding="utf-8")
            fingerprint = {"input": "abc", "config": "123"}
            runner._write_json(run_dir / "run_manifest.json", {
                "status": "COMPLETED", "fingerprint": fingerprint,
                "outputs": {"stream.csv": runner.sha256_file(artifact)},
            })
            self.assertTrue(runner._verify_cached(run_dir, fingerprint))
            self.assertFalse(runner._verify_cached(run_dir, {"input": "other"}))
            artifact.write_text("changed\n", encoding="utf-8")
            self.assertFalse(runner._verify_cached(run_dir, fingerprint))


if __name__ == "__main__":
    unittest.main()
