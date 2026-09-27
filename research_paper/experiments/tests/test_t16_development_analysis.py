import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import t16_development_analysis as t16
import trajectory_eval as trajectory


def pose(timestamp_ns, x, *, valid=True, segment=0):
    return trajectory.Pose(
        timestamp_ns,
        np.array([float(x), 0.0, 0.0]),
        np.array([0.0, 0.0, 0.0, 1.0]),
        segment=segment,
        valid=valid,
        event="POSE" if valid else "RESET",
    )


def identity_reference(positions):
    low, high = positions[0][0], positions[-1][0]
    seconds = np.arange(low * 10, high * 10 + 1) / 10.0
    anchors_t = np.asarray([item[0] for item in positions], dtype=float)
    anchors_x = np.asarray([item[1] for item in positions], dtype=float)
    xs = np.interp(seconds, anchors_t, anchors_x)
    rows = [pose(t16.EPOCH_NS + round(second * 1e9), x)
            for second, x in zip(seconds, xs)]
    return trajectory.ReferenceIndex(rows)


class T16DevelopmentAnalysisTests(unittest.TestCase):
    def test_nearest_boundary_tie_selects_earlier_pose(self):
        earlier = pose(950, 0)
        later = pose(1050, 1)
        selected = t16.associate_nearest_valid_pose([later, earlier], 1000, 50)
        self.assertIs(selected, earlier)

    def test_integer_window_uses_relative_motion_without_global_alignment(self):
        estimates = [pose(t16.EPOCH_NS, 15), pose(t16.EPOCH_NS + 1_000_000_000, 16)]
        reference = identity_reference([(0, 0), (1, 1)])
        window = t16.window_at_integer_start(estimates, reference, np.eye(4), 0)
        self.assertTrue(window.valid)
        self.assertAlmostEqual(window.translation_error_m, 0.0)
        self.assertAlmostEqual(window.rotation_error_rad, 0.0)

    def test_recovery_requires_three_consecutive_windows_and_tracks_first_relapse(self):
        reference = identity_reference([(second, second) for second in range(21)])
        poses = [pose(t16.EPOCH_NS + second * 1_000_000_000,
                      100.0 if second == 5 else second)
                 for second in range(21)]
        windows, truth_ok, reason = t16.build_primary_windows(
            poses, reference, np.eye(4), exit_time_s=0.5)
        self.assertTrue(truth_ok, reason)
        label = t16.find_recovery(windows, exit_time_s=0.5)
        self.assertEqual(label.status, "RECOVERED")
        self.assertEqual(label.triple_window_starts_s, (1, 2, 3))
        self.assertEqual(label.onset_s, 1.0)
        self.assertEqual(label.confirmation_s, 4.0)
        self.assertEqual(label.relapse_s, 4.0)
        self.assertEqual(label.recovery_end_s, 4.0)

    def test_missing_endpoint_breaks_triple_and_does_not_create_recovery(self):
        reference = identity_reference([(second, second) for second in range(21)])
        estimates = [pose(t16.EPOCH_NS + second * 1_000_000_000, second)
                     for second in range(12) if second != 4]
        windows, truth_ok, reason = t16.build_primary_windows(
            estimates, reference, np.eye(4), exit_time_s=0.5)
        self.assertTrue(truth_ok, reason)
        self.assertFalse(next(row for row in windows if row.nominal_start_s == 3).valid)
        label = t16.find_recovery(windows, exit_time_s=0.5)
        self.assertEqual(label.status, "RECOVERED")
        self.assertEqual(label.triple_window_starts_s, (5, 6, 7))

    def test_missing_later_window_endpoint_causes_relapse_at_shared_start_boundary(self):
        reference = identity_reference([(second, second) for second in range(21)])
        estimates = [pose(t16.EPOCH_NS + second * 1_000_000_000, second)
                     for second in range(21) if second != 6]
        windows, truth_ok, reason = t16.build_primary_windows(
            estimates, reference, np.eye(4), exit_time_s=0.5)
        self.assertTrue(truth_ok, reason)
        relapse_window = next(row for row in windows if row.nominal_start_s == 5)
        self.assertFalse(relapse_window.valid)
        self.assertIsNotNone(relapse_window.start_ns)
        label = t16.find_recovery(windows, exit_time_s=0.5)
        self.assertEqual(label.triple_window_starts_s, (1, 2, 3))
        self.assertEqual(label.relapse_s, 5.0)

    def test_uncovered_reference_makes_label_unavailable_not_nonrecovery(self):
        windows = [t16.MotionWindow(k, None, None, None, None, False, "")
                   for k in range(1, 5)]
        label = t16.find_recovery(windows, 0.5, truth_eligible=False,
                                  truth_reason="REFERENCE_GAP")
        self.assertEqual(label.status, "TRUTH_LABEL_UNAVAILABLE")
        self.assertEqual(label.reason, "REFERENCE_GAP")

    def test_debounce_repeated_source_cannot_count_and_confirmation_records_sources(self):
        decisions = []
        sources = [100, 100, 200, 300, 400, 500]
        for index, source in enumerate(sources):
            decisions.append(t16.DecisionTick(
                index, index * t16.TICK_NS, True, 10.0, None, source, 0, ""))
        states, transitions, alarms = t16.debounce(
            decisions, "FASTLIO_MIN_EIG_G3", threshold=5.0)
        self.assertEqual(np.flatnonzero(transitions).tolist(), [4])
        self.assertEqual(alarms[0]["source_timestamps_ns"], [200, 300, 400])
        self.assertTrue(states[4])
        self.assertTrue(states[5])

    def test_unavailable_tick_resets_debouncer(self):
        decisions = [
            t16.DecisionTick(0, 0, True, 10.0, None, 100, 0, ""),
            t16.DecisionTick(1, 1, True, 10.0, None, 200, 0, ""),
            t16.DecisionTick(2, 2, False, None, None, 300, 0, "DIAGNOSTIC_INVALID"),
            t16.DecisionTick(3, 3, True, 10.0, None, 400, 0, ""),
            t16.DecisionTick(4, 4, True, 10.0, None, 500, 0, ""),
            t16.DecisionTick(5, 5, True, 10.0, None, 600, 0, ""),
        ]
        states, transitions, _ = t16.debounce(
            decisions, "FASTLIO_MIN_EIG_G3", threshold=5.0)
        self.assertEqual(np.flatnonzero(transitions).tolist(), [5])
        self.assertFalse(states[2])
        self.assertTrue(states[5])

    def test_reset_starts_a_new_three_record_run_in_scalar_debouncer(self):
        decisions = [
            t16.DecisionTick(index, index * t16.TICK_NS, True, 10.0, None,
                             t16.EPOCH_NS + index * t16.TICK_NS,
                             0 if index < 3 else 1, "")
            for index in range(7)
        ]
        states, transitions, alarms = t16.debounce(
            decisions, "FASTLIO_MIN_EIG_G3", threshold=5.0)
        self.assertEqual(np.flatnonzero(transitions).tolist(), [2, 5])
        self.assertEqual([row["segment_id"] for row in alarms], [0, 1])
        self.assertFalse(states[3])
        self.assertTrue(states[5])

    def test_weighted_curve_groups_tied_scores(self):
        result = t16._curve([0.9, 0.9, 0.1, 0.1],
                            [True, False, True, False], [0.5, 0.5, 0.5, 0.5])
        self.assertEqual(result["status"], "AVAILABLE")
        self.assertAlmostEqual(result["roc_auc"], 0.5)
        self.assertAlmostEqual(result["average_precision"], 0.5)

    def test_wilson_zero_denominator_is_unavailable(self):
        self.assertIsNone(t16.wilson_interval(0, 0))

    def test_development_threshold_sweep_obeys_false_alarm_limit_and_sensitivity(self):
        decisions = []
        for tick in range(600):
            score = 0.0 if tick < 5 else 10.0
            source = t16.EPOCH_NS + tick * t16.TICK_NS
            decisions.append(t16.DecisionTick(
                tick, source, True, score, None, source, 0, ""))
        label = t16.RecoveryLabel("RECOVERED", True, "", 0.2, 20.2,
                                  0.5, 1.0, None, 20.2, (1, 2, 3), 19)
        run = t16.DevelopmentRun(
            "T14_DEV14_CORRIDOR_XM6_P1", 14, "CORRIDOR", False, 0.2, 10.0,
            Path("."), {}, {}, [], None, np.eye(4), [], label, {},
            {"FASTLIO_MIN_EIG_G3": decisions}, [],
        )
        selected, candidates = t16.select_fastlio_threshold([run], batch_size=2)
        self.assertEqual(selected["status"], "SELECTED_DEVELOPMENT_THRESHOLD")
        self.assertEqual(selected["threshold"], 10.0)
        self.assertEqual(selected["conditional_false_healthy_rate"], 0.0)
        self.assertEqual(selected["recovery_sensitivity"], 1.0)
        self.assertEqual(len(candidates), 3)  # two scores plus NO_ALARMS

    def test_threshold_sweep_and_scalar_state_machine_agree_across_reset(self):
        decisions = []
        for tick in range(600):
            score = 0.0 if tick < 5 else 10.0
            segment = 0 if tick < 7 else 1
            source = t16.EPOCH_NS + tick * t16.TICK_NS
            decisions.append(t16.DecisionTick(
                tick, source, True, score, None, source, segment, ""))
        label = t16.RecoveryLabel("RECOVERED", True, "", 0.2, 20.2,
                                  0.5, 1.0, None, 1.2, (1, 2, 3), 19)
        run = t16.DevelopmentRun(
            "T14_DEV14_CORRIDOR_XM6_P1", 14, "CORRIDOR", False, 0.2, 10.0,
            Path("."), {}, {}, [], None, np.eye(4), [], label, {},
            {"FASTLIO_MIN_EIG_G3": decisions}, [],
        )
        selected, _ = t16.select_fastlio_threshold([run], batch_size=2)
        self.assertEqual(selected["threshold"], 10.0)
        scalar_states, scalar_transitions, _ = t16.debounce(
            decisions, "FASTLIO_MIN_EIG_G3", threshold=10.0)
        self.assertEqual(np.flatnonzero(scalar_transitions).tolist(), [9])
        self.assertEqual(selected["recovery_sensitivity"], 1.0)
        self.assertTrue(scalar_states[9])

    def test_three_second_missing_endpoint_remains_in_planned_denominator(self):
        run = t16.DevelopmentRun(
            "T14_DEV14_CONTROL_XM6_P1", 14, "CONTROL", True, 1.0, 12.0,
            Path("."), {}, {}, [], None, np.eye(4), [], None, {}, {},
            [
                {"window_s": "3.0", "timestamp_ns": str(t16.EPOCH_NS + 1_000_000_000),
                 "window_end_ns": "", "local_valid": "false",
                 "unavailable_reason": "WINDOW_INCOMPLETE"},
                {"window_s": "3.0", "timestamp_ns": str(t16.EPOCH_NS + 1_100_000_000),
                 "window_end_ns": str(t16.EPOCH_NS + 4_100_000_000),
                 "local_valid": "true", "local_translation_error_rate_mps": "0.1",
                 "local_rotation_error_rate_radps": "0.01", "unavailable_reason": ""},
                {"window_s": "3.0", "timestamp_ns": str(t16.EPOCH_NS + 19_000_000_000),
                 "window_end_ns": "", "local_valid": "false",
                 "unavailable_reason": "WINDOW_END_AFTER_DEADLINE"},
            ],
        )
        summary = t16.summarize_three_second_sensitivity([run])["control"]
        self.assertEqual(summary["planned_window_count_total"], 2)
        self.assertEqual(summary["valid_window_count_total"], 1)
        self.assertEqual(summary["events"][0]["unavailable_post_exit_3s_windows"], 1)


if __name__ == "__main__":
    unittest.main()
