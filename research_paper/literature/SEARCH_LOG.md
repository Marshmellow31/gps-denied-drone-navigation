# Closest-work search log

Search date: 22 September 2026. The purpose was targeted primary-source checking for T02, not a systematic-review claim. Searches were performed through a web search engine, arXiv full-text HTML, IEEE Xplore metadata pages, official project pages, GitHub's repository API, and pinned shallow checkouts of official repositories.

## Queries

The following query strings were used. A query with no directly relevant result is evidence only about that query, not proof that no prior work exists.

1. `X-ICP localizability-aware LiDAR registration arXiv official code`
2. `SuperLoc predictive alignment risk localizability arXiv official code`
3. `AdaLIO robust adaptive lidar inertial odometry degenerate indoor environments arXiv official code`
4. `GEODE geometrically degenerate lidar dataset arXiv official GitHub`
5. `site:github.com X-ICP official Turcan Tuna`
6. `site:github.com SuperLoc Shibo Zhao official`
7. `site:github.com AdaLIO official Hyungtae Lim`
8. `site:github.com PengYu-Team GEODE_dataset`
9. `site:arxiv.org LiDAR degeneracy recovery transition localizability indicator detection delay false confidence`
10. `site:arxiv.org lidar inertial odometry degeneracy recovery after corridor observability`
11. `site:ieeexplore.ieee.org lidar degeneracy recovery detection transition localizability`
12. `site:arxiv.org "false reassurance" lidar localization`
13. `site:ieeexplore.ieee.org "X-ICP: Localizability-Aware LiDAR Registration"`
14. `site:ieeexplore.ieee.org "AdaLIO: Robust Adaptive LiDAR-Inertial Odometry"`
15. `site:doi.org "Heterogeneous LiDAR Dataset for Benchmarking Robust Localization"`
16. `site:doi.org "SuperLoc: The Key to Robust"`

Within each of the four full texts, `recovery`, `transition`, and `ground truth` were searched before relevant method and evaluation sections were read in context.

## Primary sources inspected

- [X-ICP arXiv v3 full text](https://arxiv.org/html/2211.16335v3), especially Sections III, V-VII, equations (2), (4)-(6), and (23), accessed 22 September 2026.
- [X-ICP official project page](https://sites.google.com/leggedrobotics.com/x-icp), accessed 22 September 2026. It linked paper, data placeholder, and videos but no official source repository was found in the inspected page/search results.
- [SuperLoc arXiv v1 full text](https://arxiv.org/html/2412.02901v1), especially Sections III-IV and equations (4), (5), and (9), accessed 22 September 2026.
- [SuperLoc official project explanation](https://superodometry.com/superloc.html), including its dataset and code links, accessed 22 September 2026.
- [SuperOdom official repository](https://github.com/superxslam/SuperOdom), shallow checkout of `ros2` revision `f10e65cd50007767b22e4c401689665e20d827d6`, accessed 22 September 2026.
- [AdaLIO arXiv v1 full text](https://arxiv.org/html/2304.12577), especially Sections 3-4, accessed 22 September 2026. No author-linked official implementation was found in the inspected paper/project searches.
- [GEODE arXiv full text](https://arxiv.org/html/2409.04961), especially Sections 3-6, accessed 22 September 2026.
- [GEODE official repository](https://github.com/PengYu-Team/GEODE_dataset), shallow checkout of `main` revision `c6e930623d4fed450d7fc50e16e3ffe0288b692b`, accessed 22 September 2026.

## Directly relevant follow-ups/cross-checks found

- [LA-LIO, IEEE IROS 2024](https://ieeexplore.ieee.org/document/10802825/): the accessible primary metadata describes stable degeneracy assessment plus adaptive weighting, but the full paper was not openly retrievable in this task. Recovery-transition definitions and delay/false-reassurance outcomes therefore remain **unverified**, not absent.
- [Unveiling Non-Reproducibility in LiDAR-Inertial Odometry, IEEE RA-L 2026](https://ieeexplore.ieee.org/document/11266943/): primary metadata directly supports repeated-run controls, particularly for geometrically degenerate scenes; it does not, from accessible metadata, establish a transition-recovery indicator study.
- [ALIVE-LIO, arXiv 2604.02706](https://arxiv.org/abs/2604.02706): a 2026 degeneracy-aware learned inertial-velocity mitigation method. Its abstract concerns reducing drift in degenerate directions, not the candidate evaluation question; full overlap remains to be checked if R1 needs a broader 2025-2026 audit.
- [Direction-Level Degeneracy-Aware Continuous Soft-Compensation, IEEE ECNCT 2026](https://ieeexplore.ieee.org/abstract/document/11661532/): accessible primary metadata describes a minimum-eigenvalue trigger, decoupled translational direction, continuous weights, and one long-corridor result. It is a relevant mitigation comparator but accessible metadata does not establish recovery labeling/delay analysis.
- [Degradation Resilient LiDAR-Radar-Inertial Odometry, arXiv 2403.05332](https://arxiv.org/abs/2403.05332): directly relevant aerial degeneracy data and mitigation context, but it adds radar and therefore does not answer a LiDAR/IMU-only indicator reliability question.
- [On Degeneracy of Optimization-Based State Estimation Problems, IEEE ICRA 2016](https://ieeexplore.ieee.org/document/7487211/): source of the conventional Hessian/eigendirection mitigation family and required background for T08/T10.

## Access and interpretation limits

- IEEE metadata pages were accessible, but some full texts were not openly available. Those entries are marked unverified rather than summarized beyond the accessible abstract/metadata.
- X-ICP's official page exposed no official source repository in the inspected material. A third-party minimal implementation appeared in search, but was not treated as official evidence.
- The current SuperOdom repository post-dates SuperLoc arXiv v1 and includes later changes. Its code was inspected as an available official implementation, not assumed to be the exact artifact used for the 2024 preprint or 2025 conference results.
- Search results include 2026 methods after the four planned anchors. R1 should decide whether their full texts materially narrow the candidate gap before a novelty statement is attempted.
