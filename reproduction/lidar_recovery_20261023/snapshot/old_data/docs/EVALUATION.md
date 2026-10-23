# Evaluation Plan

## Objective

Demonstrate that the geometry-first pipeline can find usable landing regions consistently, explain its decisions, and expose its failure modes. If navigation or SLAM is added, evaluate those components separately before reporting end-to-end results.

## Dataset design

Create deterministic synthetic scenes across several terrain families:

- flat terrain with isolated obstacles;
- uniformly sloped terrain;
- mixed flat and sloped patches;
- rough or rocky terrain;
- steps, ledges, pits, and walls;
- multiple plausible landing zones of different quality; and
- scenes with no genuinely safe landing zone.

For each family, vary obstacle density, terrain scale, sensor noise, missing observations, and point density. Retain the random seed and parameters for every generated scene.

## Ground truth

Define a landing footprint and safety rules before evaluating the detector. A ground-truth location is safe only if the complete footprint satisfies the agreed constraints for slope, roughness, clearance, and support area.

Ground-truth masks should be generated from the original synthetic terrain, before simulated sensor noise is added.

## Landing-zone metrics

| Metric | Purpose |
| --- | --- |
| Precision | Fraction of predicted-safe area that is truly safe |
| Recall | Fraction of truly safe area recovered by the detector |
| F1 score | Balance of precision and recall |
| False-safe rate | Frequency of unsafe regions being accepted |
| Target localization error | Distance between selected and best valid target |
| Valid footprint rate | Fraction of chosen targets whose full footprint is safe |
| Ranking regret | Difference between chosen and best available safety score |
| Processing time | Suitability for iterative or near-real-time use |

Because an unsafe acceptance is more serious than rejecting a usable patch, false-safe rate and valid footprint rate should be highlighted rather than hidden inside overall accuracy.

## Navigation metrics (extension)

- successful arrival and landing rate;
- collision rate;
- minimum obstacle clearance;
- path length and path-efficiency ratio;
- planning and replanning time; and
- final landing position error.

## Localization/SLAM metrics (extension)

- absolute trajectory error;
- relative pose error or drift per distance travelled;
- map consistency or point-cloud alignment error;
- processing time per update; and
- end-to-end landing performance with and without localization noise.

## Experiment protocol

1. Freeze a train/tuning subset and an unseen evaluation subset, even for a threshold-based method.
2. Tune thresholds only on the tuning subset.
3. Run each noisy condition over multiple fixed random seeds.
4. Report mean, spread, and worst-case results.
5. Save configuration, seed, runtime, predictions, and metric output for every run.
6. Include failed scenes and qualitative overlays in the final report.

## Minimum credible result

A successful core submission should include:

- several reproducible terrain families;
- ground-truth safe-region masks;
- an explainable detector using at least slope, roughness, area, and clearance;
- a ranked target output;
- quantitative results across clean and noisy scenes; and
- a documented analysis of false-safe cases and limitations.
