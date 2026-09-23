# X-ICP evidence note

## Source and target

Primary source: Turcan Tuna et al., [“X-ICP: Localizability-Aware LiDAR Registration for Robust Localization in Extreme Environments,” arXiv:2211.16335v3](https://arxiv.org/html/2211.16335v3), accessed 22 September 2026. Official [project page](https://sites.google.com/leggedrobotics.com/x-icp) also inspected.

The claimed target is robust point-cloud registration under insufficient geometric constraints. X-ICP couples a fine-grained localizability detector with constrained ICP; it is not a standalone LIO recovery classifier.

## Formulation and online inputs

- Section III-A, equations (1)-(2), defines scan-to-map point-to-plane ICP and the six-dimensional quadratic information/Hessian construction from matched scan/map points and surface normals.
- Section V uses separate translational and rotational Hessian eigenspaces, information-pair contributions, filtering, and three categories: localizable, partially localizable, and non-localizable. Equation (6) projects force/torque-like contributions into the eigenspaces.
- Section V-C defines parameters `kappa_1`, `kappa_2`, and `kappa_3`; the paper argues these relate to optimizer convergence rather than environment-specific eigenvalue thresholds, but it still gives numeric example/settings and system-dependent guidance.
- Section VI, equation (23), constrains non-localizable directions and controls partially localizable updates using the pose prior/initial guess.
- Online inputs are the current reading cloud, map/reference cloud, point-normal correspondences, and a transformation prior. Independent truth is not an online input.

## Experiments relevant to the candidate question

- Section VII-C uses controlled simulated translational, rotational, and combined degeneracy and plots localizability categories with resulting map errors.
- Sections VII-D-F use an underground mine, construction site, and city park with different LiDARs/environments. The Seemühle evaluation reports APE, 10 m RPE, end-position error, and map error; the paper uses a Leica-derived ground-truth map/trajectory.
- The paper explicitly discusses smooth changes between partial and non-localizability (Section V-C and Section VII-E), so transition behavior is not wholly absent.

## Recovery, reassurance, delay, and transfer

- A text search found no use of the term `recovery` in the inspected full text.
- **Not found in inspected material:** an independently labelled exit time from weak geometry; a definition of sustained recovered local motion; false-reassurance rate; recovery-detection delay; right-censored non-recovery; or availability-conditioned decisions.
- This is not recorded as “not studied” in an absolute sense: figures show changing categories and trajectories traverse mixed geometry, but the reported endpoints/aggregate errors do not directly measure post-exit recovery reliability.
- Scene/sensor transfer is strongly represented through multiple simulated geometries, multiple real sites, and VLP-16 versus OS0-128 experiments. However, unseen-scene transfer of a frozen recovery decision rule is not identified in the inspected evaluation.

## Relevance and limitations

X-ICP is a close method comparator because it produces direction-wise localizability states from registration correspondences. It also shows that a naive minimum-eigenvalue baseline is not equivalent to the published method. The candidate study must not claim that multi-category transition detection itself is new. The narrower unresolved question is whether such health states agree with independently measured sustained local-motion recovery and with what delay/false reassurance after geometry improves.

No official X-ICP source repository was linked on the inspected project page or found by the targeted repository search. The page's additional-data link was not treated as code. Any reproduction in T10/T13 must therefore distinguish a paper-based reimplementation from official-code parity.

## Exact evidence locations

- Target/contributions: Abstract and Section I, especially contributions list.
- ICP model: Section III-A, equations (1)-(2).
- Directional detector: Section V-A, equations (4)-(6); Section V-B; Section V-C.
- Constraints: Section VI, equations (20)-(23).
- Simulation and real tests: Sections VII-C through VII-F.
- Seemühle truth and metrics: Section VII-D, Tables I-II.
- Smooth localizability changes: Section VII-E, discussion around Figures 13-14.
