"""Analytic fixtures for exploratory miss classification; no final data needed."""
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from analyze_final_failure_cases import miss_pattern


class MissClassificationTests(unittest.TestCase):
    def classify(self, states, raw, available=(True,True,True), recovered=True, detected=False):
        return miss_pattern(recovered, detected, np.array(states),
                            np.array([False,True,True]),np.array(raw),np.array(available))

    def test_nonrecovery_is_not_detection_miss(self):
        self.assertEqual(self.classify([False]*3,[False]*3,recovered=False),'NOT_A_MISSED_RECOVERY')

    def test_unavailable_interval_is_not_threshold_failure(self):
        self.assertEqual(self.classify([False]*3,[False]*3,available=[True,False,False]),
                         'NO_AVAILABLE_TICK_IN_RECOVERY_INTERVAL')

    def test_earlier_active_state_differs_from_no_healthy_evidence(self):
        self.assertEqual(self.classify([True,True,False],[True,True,False]),
                         'ACTIVE_STATE_WITHOUT_NEW_POST_ONSET_TRANSITION')

    def test_no_healthy_tick_ignores_preonset_score(self):
        self.assertEqual(self.classify([False]*3,[True,False,False]),
                         'NO_RAW_HEALTHY_TICK_IN_RECOVERY_INTERVAL')

    def test_intermittent_raw_health_and_detected_endpoint(self):
        self.assertEqual(self.classify([False]*3,[False,True,False]),
                         'RAW_HEALTHY_TICKS_WITHOUT_THREE_RECORD_CONFIRMATION')
        self.assertEqual(self.classify([False,False,True],[False,True,True],detected=True),
                         'NOT_A_MISSED_RECOVERY')


if __name__=='__main__':
    unittest.main()
