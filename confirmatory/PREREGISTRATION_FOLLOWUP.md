# Preregistration of the Follow-Up to the Mini-Round

Study: Algorithmic Optimization of Dense Sphere Packings in Non-Euclidean Spaces (M. E. J. Alibadbad, Region VIII, MCS-I).

This file is written after the mini-round (PREREGISTRATION_MINIROUND.md, SHA-256 3b6702f683023611d6f4a7549317d3e11be674fff08a85ed451bf46969df5492) had been run and analyzed, and its result for M1 was inconclusive
(Spearman 0.31, one-sided permutation p = .103). The hash of this file is recorded before any run of the follow-up. The earlier files are not edited.

## 1. A flaw in the mini-round that this follow-up corrects

* The Euclidean plane has no length scale: a packing of disks of radius r0 in a disk of radius R is a scaled copy of a packing of disks of radius 1 in a disk of radius R/r0. For a given design boundary share b0, the
  ratio R/r0 is the same for r0 = 0.30 and r0 = 0.40, so the Euclidean conditions with r0 = 0.30 and r0 = 0.40 are the same problem (the same K and the same deficit in every case).
  The six Euclidean conditions of the mini-round are therefore three distinct conditions, and the boundary-loss model M3 was fitted on three independent points, not six. The 13 degrees of freedom stated for M2 are overstated for the same reason.
  The hyperbolic disk and the spherical cap have a length scale (the curvature is fixed), so their conditions at different r0 are different problems.
* The mini-round decisions are reported as they were. A repeat of its analysis with the Euclidean duplicates removed is reported as an exploratory sensitivity analysis.

## 2. Design

* Fresh seeds 401-420; the starting configuration depends on the seed, the condition, and n only.
* Disk radii r0 in {0.20, 0.30, 0.40} and design boundary shares b0 in {0.35, 0.40, 0.45, 0.50, 0.55}. The ball radius R of each condition solves b0 = 1 - Area(R - r0) / Area(R) (as in the mini-round).
* Hyperbolic disk and spherical cap: all pairs (r0, b0), except that b0 = 0.35 is not used with r0 = 0.40 in any space (the reference count of the hyperbolic ball is 175, which is too costly). Hyperbolic disks: 14 conditions; caps: 14 conditions.
* Euclidean disk: one condition for each b0 (five conditions), run at r0 = 0.30 only, because the results do not depend on r0. Total: 33 conditions.
* Two methods, each at 1,500 sweeps: polished gradient descent (GD+P, polishing share 0.25) and L-BFGS-B (soft-minimum exponent continuation with the re-tuned value 2,500 of tuned_params_retuned.json).
* For each method and condition, K_method = the largest n, scanning n = n_ref, n_ref - 1, ..., 1 (n_ref = floor(rho*(r0) Area(R) / Area(r0)), rho* an upper bound on the density of any packing of disks of radius r0 in the whole space), for which the method
  reaches a disk radius of at least r0 - 1e-9 in at least 10 of 20 seeds. A scan stops at a value of n as soon as 10 successes or 11 failures are reached. K = max(K_GD+P, K_L-BFGS-B) is the primary number of disks of a condition;
  a failure to find n disks does not prove that n disks do not fit, so K is a lower bound on the true maximum.
* Fixed-radius density deficit delta0 = 1 - K Area(r0) / (Area(R) rho*(r0)).

## 3. Decision rules (the same thresholds as the mini-round)

**F1.** Spearman correlation between b0 and delta0 over the 33 conditions (primary K). Supported if it is at least .50 and the one-sided permutation p (20,000 permutations, seed 7) is below .05; not supported if below .20; otherwise inconclusive.

**F2.** Least-squares fit delta0 = a + beta b0 + g_H [hyperbolic] + g_S [cap] + e1 [r0 = 0.20] + e2 [r0 = 0.40] (27 degrees of freedom; Euclidean conditions are the baseline at r0 = 0.30). A detectable curvature effect if the 95% t interval of g_H excludes 0 and
|g_H| >= .05; no detectable effect if the whole interval lies within -.05 to .05; otherwise inconclusive. g_S is reported with the same rule.

**F3.** Boundary-loss model delta0 = lambda b0, lambda fitted by least squares through the origin on the five Euclidean conditions and not refitted, used to predict the 28 hyperbolic and cap conditions. The model describes them if the mean absolute error is at most .05, and does not if it exceeds .10; otherwise inconclusive.
The model is a description of the data: it has one parameter and no derivation, and agreement with it does not show that the boundary causes the loss.

## 4. Exploratory analyses (labeled so; no decision rule)

* The same three analyses with K of each method alone; the share of conditions in which L-BFGS-B found a larger K than GD+P, the same, and a smaller K.
* The mini-round conditions (seeds 301-320) with L-BFGS-B added, and the mini-round analysis with the Euclidean duplicates removed (15 conditions).
* The mini-round and the follow-up pooled (distinct conditions only).

## 5. Other commitments

* No run is excluded. Hardware is recorded in hardware.json. Any deviation from this file is listed in the Research Paper. The three rules are not corrected for the nine rules of the earlier rounds.
