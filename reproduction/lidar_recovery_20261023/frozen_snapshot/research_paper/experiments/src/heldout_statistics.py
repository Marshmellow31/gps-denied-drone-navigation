"""Frozen geometry-cluster uncertainty; usable on analytic fixtures before R3.

This module generates no geometry and reads no recording. Final callers must
verify the complete planned paired cohort before marking intervals confirmatory.
"""
from __future__ import annotations

import numpy as np

STRATA = ('TEST_SHORT_NARROW', 'TEST_SHORT_WIDE', 'TEST_LONG_NARROW', 'TEST_LONG_WIDE')
BOOTSTRAP_COUNT = 10000
BOOTSTRAP_SEED = 20260926


def clustered_draws(stratum_seeds, replicates=BOOTSTRAP_COUNT):
    if type(replicates) is not int or replicates <= 0:
        raise ValueError('bootstrap replicate count must be a positive integer')
    if set(stratum_seeds) != set(STRATA):
        raise ValueError('all four fixed strata are required')
    arrays = []
    for name in STRATA:
        seeds = list(stratum_seeds[name])
        if (not seeds or any(not isinstance(s, (int, np.integer)) or isinstance(s, (bool, np.bool_)) for s in seeds)
                or seeds != sorted(set(seeds))):
            raise ValueError('stratum seeds must be unique and ascending')
        arrays.append(np.asarray(seeds, dtype=np.int64))
    if len({len(a) for a in arrays}) != 1:
        raise ValueError('the frozen final design requires balanced strata')
    if len(set(np.concatenate(arrays))) != sum(len(a) for a in arrays):
        raise ValueError('a geometry seed appears in multiple strata')
    rng = np.random.Generator(np.random.PCG64(BOOTSTRAP_SEED))
    draws = []
    # The order is replicate then stratum, as specified in METRICS.md.
    for _ in range(replicates):
        draws.append([rng.choice(seeds, size=len(seeds), replace=True) for seeds in arrays])
    return arrays, draws


def paired_interval(stratum_seeds, per_seed_difference, replicates=BOOTSTRAP_COUNT):
    arrays, draws = clustered_draws(stratum_seeds, replicates)
    if set(per_seed_difference) != set(np.concatenate(arrays)):
        raise ValueError('paired outcome does not cover every planned geometry')
    values = {int(seed): float(value) for seed, value in per_seed_difference.items()}
    if not all(np.isfinite(v) for v in values.values()):
        return {'status': 'UNAVAILABLE_INCOMPLETE_PAIRED_OUTCOME', 'estimate': None, 'interval_95': None}
    stratum_means = {name: float(np.mean([values[int(s)] for s in seeds]))
                     for name, seeds in zip(STRATA, arrays)}
    samples = np.asarray([np.mean([np.mean([values[int(s)] for s in seeds]) for seeds in draw])
                          for draw in draws], dtype=np.float64)
    return {'status': 'AVAILABLE', 'estimate': float(np.mean(list(stratum_means.values()))),
            'stratum_means': stratum_means,
            'interval_95': np.percentile(samples, [2.5, 97.5], method='linear').tolist(),
            'bootstrap_replicates': replicates, 'bootstrap_seed': BOOTSTRAP_SEED,
            'uncertainty_unit': 'paired geometry seed, resampled within fixed strata',
            'confirmatory_replicate_count': replicates == BOOTSTRAP_COUNT}


def weighted_curve(scores, labels, weights):
    if any(not (isinstance(v, (bool, np.bool_)) or
                (isinstance(v, (int, np.integer)) and v in (0, 1))) for v in labels):
        raise ValueError('curve truth labels must be explicit Boolean classes, not unavailable values')
    score = np.asarray(scores, dtype=np.float64)
    truth = np.asarray(labels, dtype=bool)
    weight = np.asarray(weights, dtype=np.float64)
    if len(score) != len(truth) or len(score) != len(weight):
        raise ValueError('curve arrays differ in length')
    if not np.isfinite(score).all() or not np.isfinite(weight).all() or np.any(weight < 0):
        raise ValueError('curve values/weights must be finite and nonnegative')
    positive, negative = float(weight[truth].sum()), float(weight[~truth].sum())
    if positive == 0 or negative == 0:
        return None, None
    order = np.argsort(-score, kind='stable')
    score, truth, weight = score[order], truth[order], weight[order]
    ends = np.r_[np.flatnonzero(score[1:] != score[:-1]), len(score)-1]
    tp = np.cumsum(np.where(truth, weight, 0))[ends]
    fp = np.cumsum(np.where(~truth, weight, 0))[ends]
    tpr, fpr = np.r_[0., tp / positive], np.r_[0., fp / negative]
    auc = float(np.sum(np.diff(fpr) * (tpr[1:] + tpr[:-1]) / 2.))
    precision = np.divide(tp, tp+fp, out=np.zeros_like(tp), where=(tp+fp)>0)
    ap = float(np.sum(np.diff(tpr) * precision))
    return auc, ap


def event_weighted_curve_interval(stratum_seeds, event_scores_labels, replicates=BOOTSTRAP_COUNT):
    arrays, draws = clustered_draws(stratum_seeds, replicates)
    if set(event_scores_labels) != set(np.concatenate(arrays)):
        raise ValueError('curve event inventory must include every planned geometry, including no-score events')
    scores, labels, event_ids, base_weights = [], [], [], []
    for seed in np.concatenate(arrays):
        values, truth = event_scores_labels[int(seed)]
        if len(values) != len(truth):
            raise ValueError('event scores and labels differ in length')
        if len(values):
            scores.extend(values); labels.extend(truth)
            event_ids.extend([int(seed)] * len(values)); base_weights.extend([1./len(values)] * len(values))
    base = np.asarray(base_weights, dtype=np.float64)
    point = weighted_curve(scores, labels, base)
    aucs, aps, undefined = [], [], 0
    for draw in draws:
        unique, count = np.unique(np.concatenate(draw), return_counts=True)
        multiplicity = dict(zip(unique.tolist(), count.tolist()))
        weights = base * np.asarray([multiplicity.get(seed, 0) for seed in event_ids], dtype=np.float64)
        auc, ap = weighted_curve(scores, labels, weights)
        if auc is None:
            undefined += 1
        else:
            aucs.append(auc); aps.append(ap)
    result = {'roc_auc': point[0], 'average_precision': point[1], 'bootstrap_replicates': replicates,
              'undefined_replicates': undefined, 'events_with_scores': sum(len(v[0]) > 0 for v in event_scores_labels.values()),
              'planned_events': sum(len(a) for a in arrays), 'bootstrap_seed': BOOTSTRAP_SEED,
              'confirmatory_replicate_count': replicates == BOOTSTRAP_COUNT}
    if undefined or point[0] is None:
        result.update(status='UNAVAILABLE_CURVE_INTERVAL', roc_auc_interval_95=None, average_precision_interval_95=None)
    else:
        result.update(status='AVAILABLE',
            roc_auc_interval_95=np.percentile(aucs, [2.5,97.5], method='linear').tolist(),
            average_precision_interval_95=np.percentile(aps, [2.5,97.5], method='linear').tolist())
    return result
