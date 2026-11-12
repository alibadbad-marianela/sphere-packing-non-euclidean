# Preregistration of the Confirmatory Round

Study: Algorithmic Optimization of Dense Sphere Packings in Non-Euclidean Spaces (M. E. J. Alibadbad, Region VIII, MCS-I).

This file fixes the design, hypotheses, thresholds, and decision rules of a new round of experiments (the confirmatory round)
**before** any evaluation seed of that round is run. Its SHA-256 hash is recorded in PREREGISTRATION.sha256 together with the UTC time
at which it was computed; the hash is quoted in the Research Plan. The earlier study (seeds 1-30) is not confirmatory; its results
are not changed by this round. A hash recorded by the author is not an independent time stamp: the file and its hash should also be sent to
the research adviser (for example by e-mail) before the evaluation runs.

## 1. Question and prediction

Curvature and area are confounded in the earlier study (a ball of a given radius has a different area in each space). The confirmatory round
compares balls of **equal area**. For a packing of n equal disks of radius r in a ball of radius R in a space of curvature k define

* reference density rho*(k, r): the density of the densest packing of disks of radius r in the whole space (Fejes Toth 1943 for the sphere,
  Thue and Fejes Toth for the plane, Boroczky 1978 for the hyperbolic plane): the density of the disks inside the regular triangle whose vertices are the
  centers of three mutually tangent disks. (Euclidean: pi / sqrt(12); hyperbolic: 3 a (cosh r - 1) / (pi - 3 a) with cos a = cosh 2r / (cosh 2r + 1);
  spherical: 3 a (1 - cos r) / (3 a - pi) with cos a = cos 2r / (1 + cos 2r).)
* density deficit  delta = 1 - [n * Area(r) / Area(R)] / rho*(k, r);
* boundary share  b = 1 - Area(R - r) / Area(R), the share of the ball's area within distance r of its boundary.

**Prediction (C1).** The density deficit follows the boundary share: conditions with a larger b have a larger delta, in every space, so that most of the
deficit is a boundary effect and not a curvature effect.

## 2. Design

* Fresh evaluation seeds 101-120 (20 seeds). Pilot (tuning) seeds 9101-9104. No seed of the earlier study is reused.
* The starting configuration depends only on the seed and the condition; every method and every budget level starts from the same configuration.
* Budget levels (in sweeps; one sweep = n(n-1)/2 pair-distance evaluations, plus n wall clearances per evaluation in ball problems): **500, 1,500, 3,000**.
  1,500 sweeps is the main budget for the decisions below; the other two levels are part of the main design.
* Methods (six): gradient descent on the soft-minimum energy (GD), GD followed by a max-min polishing step (GD+P), simulated annealing (SA),
  compression (CP), SciPy L-BFGS-B on the soft-minimum energy with the exponent raised in ten stages and random restarts until the budget is used (LBFGSB),
  and basin hopping with L-BFGS-B local minimization (scipy.optimize.basinhopping) on the soft-minimum energy at p = 60 (BH).
* Equal tuning: every method has one tuned parameter with six candidate settings; each setting is run on the same four pilot conditions (Tammes N = 11 and 33;
  hyperbolic and Euclidean balls of area 8 with 16 disks) and the same four pilot seeds at 1,500 sweeps; the setting with the highest mean score relative to the best
  score seen in that pilot condition is kept. Candidate settings: GD p_max {40,80,150,250,400,700}; GD+P polishing share {.05,.10,.15,.25,.35,.50};
  SA initial temperature {.005,.01,.02,.04,.08,.16} times the length scale; CP initial growth rate {.10,.15,.25,.35,.50,.70}; LBFGSB p_max {40,80,150,250,400,700};
  BH step {.05,.10,.20,.40,.80,1.50} times the length scale. The tuned values are written to tuned_params.json and hashed before any evaluation run.
* Conditions (33): Tammes problem N = 9, 13, 14, 24, 30, 40, 60 (7); equal-area balls of area 3, 6, 12 with n = 12 and 24 disks in the spherical cap,
  the Euclidean disk, and the hyperbolic disk (18); and large balls with hyperbolic radius 2, 3, 6, 8 (area 17.4, 57.0, 1261.1, 9358.7; n = 24, 36, 50, 70) in the
  hyperbolic plane and in the Euclidean disk of the same area (8). Equal area among all three spaces is possible only up to 4 pi = 12.57 because
  the sphere has finite area, so the large balls compare only the hyperbolic and Euclidean planes.
* Reference values: Tammes problem: the proven optimum (N = 9, 13, 14, 24; Schutte and van der Waerden 1951; Musin and Tarasov 2012, 2015; Robinson 1961) or the published best-known value
  (N = 30, 40, 60; Sloane's tables). Euclidean balls: the value in Packomania (circles in a circle), entered by the author before analysis. Hyperbolic balls and spherical caps:
  no published tables of best packings are known to the author, so the reference is the best score found by any method, budget, and seed of this round in that condition, and
  the result is reported against the density reference rho* as well. Relative score = score / reference value. No run is excluded.
* Count-based problem (original element, exploratory, no decision rule): for balls of area 6 and 12 in the three spaces and disks of radius 0.30, K is the largest n for which GD+P at 1,500 sweeps reaches a radius of at least
  0.30 in at least half of 20 fresh seeds (201-220), scanned downward from n = floor(rho* Area(R) / Area(0.30)).

## 3. Hypotheses and decision rules (all at 1,500 sweeps unless stated)

**C1 (primary; boundary-share prediction).** Over the 26 ball conditions, let r_c be the highest mean score among the six methods and compute delta_c and b_c from it.
Supported if the Spearman correlation between b_c and delta_c is at least .70 and the one-sided permutation p-value (20,000 permutations of delta_c) is below .05. Not supported if the correlation is below .30.
Otherwise inconclusive. The sign of the correlation within each space is also reported (not part of the decision).

**C2 (curvature beyond boundary share).** Over the same 26 conditions, fit delta = a + beta b + g_H [hyperbolic] + g_S [cap] by ordinary least squares. Curvature adds a detectable deficit if the 95% bootstrap interval
(10,000 resamples of conditions) of g_H excludes 0 and the estimate is at least .02; there is no detectable curvature effect if the whole interval lies within -.02 to .02; otherwise inconclusive.

**C3 (ranking at equal area).** Over the 18 equal-area conditions let d_c be the mean over seeds of the relative score of GD minus that of SA, and compare the three spaces (six conditions each).
The ranking depends on the space if the Kruskal-Wallis p-value is below .05; it does not depend on the space if, for each pair of spaces, the 90% bootstrap interval of the difference of medians of d_c lies within -.01 to .01;
otherwise inconclusive.

**C4 (baselines).** A stronger baseline matters if, in at least half of the 33 conditions, the highest mean relative score of LBFGSB and BH exceeds those of both GD and SA. Separately, GD+P is competitive if its mean rank among the six methods
(ranks within seed, averaged) is first or second in at least half of the 33 conditions.

**C5 (budget).** Kendall's W of the six methods' mean relative scores across the three budget levels is computed in each condition; the ranking is stable across budgets if the median W is at least .80.

**C6 (Tammes recovery).** Supported if, for each of N = 9, 13, 14, 24, at least one method has a relative score of at least .999 in at least 90% of seeds.

Also reported without decision rules: wall-clock time by method (hardware in section 4), sweeps used (L-BFGS-B stops by its own convergence test and then restarts), success rates at .99 and .999, the count-based results, and every table of the earlier supplementary section repeated for the new data.

## 4. Other commitments

* Hardware and software are recorded in hardware.json before the evaluation run. Wall-clock times are comparable only within the round.
* Multiplicity: the six decisions are separate pre-specified questions and are not corrected for one another; all are reported whatever the outcome.
* Analyses not listed here are exploratory and are labeled so. Any deviation from this file will be listed in the Research Paper.
* The earlier study's data, tables and conclusions are not altered by this round.
