# Preregistration of the Matched-Boundary Mini-Round

Study: Algorithmic Optimization of Dense Sphere Packings in Non-Euclidean Spaces (M. E. J. Alibadbad, Region VIII, MCS-I).

Purpose: the confirmatory round could not separate a curvature effect from the boundary effect (C2 inconclusive), and its boundary share depends on the radius found by each method (partly circular).
This mini-round fixes the disk radius in advance and matches the boundary share across the three spaces by design, so that curvature differs while the boundary share does not.
The hash of this file is recorded before any run of the mini-round. It is run after, and informed by, the confirmatory round; it is confirmatory only for the rules below.

## 1. Definitions

* Reference density rho*(k, r): an upper bound on the density of any packing of disks of radius r in the whole space of curvature k (Fejes Toth 1943; Thue and Fejes Toth; Boroczky 1978); formulas as in PREREGISTRATION.md.
* Design boundary share  b0 = 1 - Area(R - r0) / Area(R) for a fixed disk radius r0. It depends only on the design (R and r0), not on any result.
* For each space, disk radius r0, and target b0, the ball radius R is the solution of the equation for b0 (Euclidean disk, hyperbolic disk, spherical cap). Curvature differs between spaces; b0 and r0 are the same.
* Reference count n_ref = floor(rho*(r0) Area(R) / Area(r0)).
* K = the largest n, scanning n = n_ref, n_ref - 1, ..., 1, for which GD+P (gradient descent with a polishing step; polishing share 0.25 as tuned in the confirmatory round) at 1,500 sweeps reaches a disk radius of at least r0 - 1e-9 in at least 10 of 20 seeds. K = 0 if no n qualifies.
* Fixed-radius density deficit  delta0 = 1 - K Area(r0) / (Area(R) rho*(r0)).  (A lower bound on the true deficit, because failing to find a packing does not prove that none exists.)

## 2. Design

* Fresh seeds 301-320; the starting configuration depends on the seed, the condition, and n only. One method (GD+P), one budget (1,500 sweeps).
* Conditions (18): r0 in {0.30, 0.40}; b0 in {0.40, 0.45, 0.50}; spaces: Euclidean disk, hyperbolic disk, spherical cap.
* Hardware and software are recorded (hardware.json). No run is excluded.

## 3. Hypotheses and decision rules

**M1 (non-circular boundary prediction).** delta0 increases with b0. Spearman correlation between b0 and delta0 over the 18 conditions; supported if it is at least .50 and the one-sided permutation p-value (20,000 permutations) is below .05; not supported if it is below .20; otherwise inconclusive.

**M2 (curvature at matched boundary share).** Least-squares fit delta0 = a + beta b0 + g_H [hyperbolic] + g_S [cap] + e [r0 = 0.40] over the 18 conditions. A detectable curvature effect if the 95% t-interval (13 degrees of freedom) of g_H excludes 0 and |g_H| >= .05; no detectable curvature effect if the whole interval lies within -.05 to .05; otherwise inconclusive. g_S is reported with the same rule as a secondary result.

**M3 (boundary-loss model).** Model: the boundary layer packs with a loss lambda relative to the upper bound and the interior at the bound, so delta0 = lambda b0. lambda is fitted by least squares through the origin on the six Euclidean conditions only and used, without refitting, to predict delta0 for the twelve hyperbolic and cap conditions. The model describes the other spaces if the mean absolute prediction error over those twelve is at most .05; it does not if the error exceeds .10; otherwise inconclusive.

The same model is applied, as an exploratory analysis labeled post hoc, to the ball conditions of the confirmatory round (delta on b, with lambda fitted on the Euclidean conditions).

## 4. Other commitments

* Analyses not listed here are exploratory and are labeled so. The six decisions of the confirmatory round and the three of this mini-round are not corrected for one another.
* Any deviation from this file is listed in the Research Paper.
