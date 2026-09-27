import sys
from pathlib import Path
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import audit_t14_repeatability as audit
import t16_development_analysis as analysis


class RepeatabilityAuditTests(unittest.TestCase):
    def test_alignment_discloses_missing_and_unavailable_samples(self):
        result = audit.numerical_comparison({1: 2.0, 2: None, 3: 4.0},
                                             {1: 3.0, 2: 1.0, 4: 9.0})
        self.assertEqual(result["shared_timestamps"], 2)
        self.assertEqual(result["jointly_available"], 1)
        self.assertEqual(result["availability_disagreements"], 1)
        self.assertEqual(result["primary_only_timestamps"], 1)
        self.assertEqual(result["repeat_only_timestamps"], 1)
        self.assertEqual(result["maximum_absolute_change"], 1.0)

    def test_missing_is_never_reported_as_zero_error(self):
        result = audit.numerical_comparison({1: None}, {1: None})
        self.assertEqual(result["jointly_available"], 0)
        self.assertIsNone(result["maximum_absolute_change"])
        self.assertIsNone(result["primary_median_jointly_available"])
        with self.assertRaises(ValueError):
            audit.numerical_comparison({1: float("inf")}, {1: 1.0})

    def make_run(self, scores):
        ticks = [analysis.DecisionTick(i, analysis.EPOCH_NS + i * analysis.TICK_NS,
                 True, score, score >= 10, analysis.EPOCH_NS + i * analysis.TICK_NS,
                 0, "") for i, score in enumerate(scores)]
        return SimpleNamespace(control=True, decisions={method: ticks for method in audit.METHODS})

    def test_small_score_change_can_change_fixed_threshold_decisions(self):
        first, second = self.make_run([10.1] * 6), self.make_run([9.9] * 6)
        result = audit.decision_comparison(first, second, audit.METHODS[0], 10.0)
        self.assertEqual(result["raw_healthy_disagreements_jointly_available"], 6)
        self.assertEqual(result["confirmed_state_disagreements_jointly_available"], 4)
        self.assertEqual(result["primary_alarm_times_s"], [0.2])
        self.assertEqual(result["repeat_alarm_times_s"], [])

    def test_identical_scores_and_decisions_have_zero_changes(self):
        run = self.make_run([8.0, 12.0, 12.0, 12.0])
        for method in audit.METHODS:
            result = audit.decision_comparison(run, run, method, 10.0)
            self.assertEqual(result["confirmed_state_disagreements_all_ticks"], 0)
            self.assertEqual(result["score_comparison_full_run"]["maximum_absolute_change"], 0.0)

    def test_unmatched_decision_grids_are_rejected(self):
        with self.assertRaises(ValueError):
            audit.decision_comparison(self.make_run([12.0] * 4),
                                      self.make_run([12.0] * 3), audit.METHODS[0], 10.0)


if __name__ == "__main__":
    unittest.main()
