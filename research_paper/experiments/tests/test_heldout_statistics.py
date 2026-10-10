import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import heldout_statistics as stats
import t16_development_analysis as existing


class GeometryUncertaintyTests(unittest.TestCase):
    def design(self):
        return {name: [10*i+1, 10*i+2] for i, name in enumerate(stats.STRATA)}

    def test_fixed_draw_order_matches_literal_protocol_rng(self):
        arrays, draws = stats.clustered_draws(self.design(), 3)
        rng = np.random.Generator(np.random.PCG64(20260926))
        expected = [[rng.choice(a, size=2, replace=True) for a in arrays] for _ in range(3)]
        np.testing.assert_array_equal(np.asarray(draws), np.asarray(expected))

    def test_constant_paired_effect_has_exact_degenerate_interval(self):
        design = self.design()
        result = stats.paired_interval(design, {s: 2.5 for a in design.values() for s in a}, 10)
        self.assertEqual(result['estimate'], 2.5)
        self.assertEqual(result['interval_95'], [2.5,2.5])
        self.assertFalse(result['confirmatory_replicate_count'])

    def test_missing_or_nonfinite_pair_cannot_be_zero_filled(self):
        design = self.design(); values = {s: 1. for a in design.values() for s in a}
        values[1] = float('nan')
        self.assertEqual(stats.paired_interval(design, values, 3)['status'], 'UNAVAILABLE_INCOMPLETE_PAIRED_OUTCOME')
        del values[1]
        with self.assertRaises(ValueError): stats.paired_interval(design, values, 3)

    def test_tie_weighted_curve_matches_frozen_existing_definition(self):
        score=[3.,3.,2.,1.]; labels=[True,False,True,False]; weights=[.5,.5,1.,1.]
        old=existing._curve(score,labels,weights);new=stats.weighted_curve(score,labels,weights)
        self.assertAlmostEqual(old['roc_auc'],new[0]);self.assertAlmostEqual(old['average_precision'],new[1])

    def test_undefined_bootstrap_replicates_are_not_dropped(self):
        design=self.design(); events={s: ([1.],[s==1]) for a in design.values() for s in a}
        result=stats.event_weighted_curve_interval(design,events,20)
        self.assertGreater(result['undefined_replicates'],0)
        self.assertEqual(result['status'],'UNAVAILABLE_CURVE_INTERVAL')
        self.assertIsNone(result['roc_auc_interval_95'])

    def test_balanced_disjoint_strata_are_required(self):
        design=self.design();design[stats.STRATA[0]]=[1]
        with self.assertRaises(ValueError):stats.clustered_draws(design,3)

    def test_full_frozen_10000_draw_stream_matches_independent_literal_rng(self):
        arrays, draws = stats.clustered_draws(self.design())
        rng = np.random.Generator(np.random.PCG64(20260926))
        expected = [[rng.choice(a, size=len(a), replace=True) for a in arrays]
                    for _ in range(10000)]
        np.testing.assert_array_equal(np.asarray(draws), np.asarray(expected))

    def test_nonconstant_paired_percentiles_match_literal_cluster_aggregation(self):
        design = self.design()
        differences = {s: float(s*s) for seeds in design.values() for s in seeds}
        result = stats.paired_interval(design, differences, 17)
        rng = np.random.Generator(np.random.PCG64(20260926))
        samples = []
        for _ in range(17):
            means = []
            for name in stats.STRATA:
                draw = rng.choice(design[name], size=2, replace=True)
                means.append(sum(differences[int(s)] for s in draw)/2)
            samples.append(sum(means)/4)
        self.assertEqual(result['estimate'], sum(differences.values())/8)
        np.testing.assert_array_equal(result['interval_95'],
                                      np.percentile(samples, [2.5,97.5], method='linear'))

    def test_frame_duplication_cannot_increase_one_geometry_events_total_weight(self):
        design = self.design()
        events = {s: ([3.,2.], [True,False]) for seeds in design.values() for s in seeds}
        events[1] = ([0.,1.], [True,False])
        first = stats.event_weighted_curve_interval(design, events, 23)
        events[1] = (events[1][0]*19, events[1][1]*19)
        second = stats.event_weighted_curve_interval(design, events, 23)
        self.assertEqual(first['planned_events'], 8)
        for key in ('roc_auc', 'average_precision'):
            self.assertAlmostEqual(first[key], second[key], places=12)
        np.testing.assert_allclose(first['roc_auc_interval_95'], second['roc_auc_interval_95'], atol=1e-12)
        np.testing.assert_allclose(first['average_precision_interval_95'], second['average_precision_interval_95'], atol=1e-12)

    def test_no_score_events_remain_in_inventory_and_all_empty_is_unavailable(self):
        design = self.design()
        events = {s: ([], []) for seeds in design.values() for s in seeds}
        result = stats.event_weighted_curve_interval(design, events, 7)
        self.assertEqual(result['planned_events'], 8)
        self.assertEqual(result['events_with_scores'], 0)
        self.assertEqual(result['undefined_replicates'], 7)
        self.assertIsNone(result['roc_auc'])
        self.assertIsNone(result['average_precision_interval_95'])
        self.assertEqual(result['status'], 'UNAVAILABLE_CURVE_INTERVAL')

    def test_unavailable_truth_is_not_silently_converted_to_a_negative_class(self):
        for missing in (None, float('nan'), 'UNAVAILABLE'):
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                stats.weighted_curve([2.,1.], [True,missing], [1.,1.])

    def test_event_numpy_arrays_are_supported_without_ambiguous_truth_coercion(self):
        design = self.design()
        events = {s: (np.array([2.,1.]), np.array([True,False]))
                  for seeds in design.values() for s in seeds}
        result = stats.event_weighted_curve_interval(design, events, 5)
        self.assertEqual(result['status'], 'AVAILABLE')
        self.assertEqual(result['events_with_scores'], 8)

    def test_invalid_replicate_counts_and_noninteger_seed_ids_are_rejected(self):
        for count in (0, -1, 2.5, True):
            with self.subTest(replicates=count), self.assertRaises(ValueError):
                stats.clustered_draws(self.design(), count)
        design = self.design()
        design[stats.STRATA[0]] = [1.1, 2.1]
        with self.assertRaises(ValueError):
            stats.clustered_draws(design, 3)


if __name__ == '__main__': unittest.main()
