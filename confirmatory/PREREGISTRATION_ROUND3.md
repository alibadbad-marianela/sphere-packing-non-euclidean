# Preregistration of the Final Round: an Equal-Area Test of Curvature and a Predictive Rule for the Number of Disks

Study: Algorithmic Optimization of Dense Sphere Packings in Non-Euclidean Spaces (M. E. J. Alibadbad, Region VIII, MCS-I).

Status: written before any run of this round. The SHA-256 hash of this file and the time it was recorded are written to ROUND3.sha256 before any run, and the files are to be emailed to the research adviser before any run is started;
the adviser's email is the independent time stamp. The code that produces the data is `confirm_round3.py` (SHA-256 306012a9857f6f630f8b1a603d29e39c31fa23560f57ab0a18b41a793cc0f0ec; it uses the scan function of `confirm_followup.py`,
SHA-256 cc33b0d00c5338d39537bb232a1f72b265af46754bcf22e94b921fe05d37039a, and the ball radius function of `confirm_mini.py`, SHA-256 90a83792f9decbba9d3cd24abb50fd56283736d53c8a0c4dd9a1a282fa327fd3).
Earlier rounds remain as they are; their files are not edited. Past results are the reason for the design: the curvature question (C2 of the confirmatory round, M2 of the mini-round, F2 of the follow-up) was inconclusive in three rounds,
mainly because the number of independent conditions was small (26, 15, and 33, with conditions paired by area).

## 1. Question 1: does curvature change the density deficit once the boundary share is held in the model?

**Design A.** Three spaces (Euclidean disk, hyperbolic disk, spherical cap) x eight ball areas {2, 3, 4, 5, 6, 8, 10, 12} x six numbers of disks {8, 12, 16, 20, 24, 32} = 144 conditions. The three balls of one (area, n) pair have equal area and equal n;
that pair is a **cell** (48 cells). The ball radius of each condition follows from its area (the sphere has area 4 pi, so every area is below 4 pi). Disk radius is the free variable: each run maximizes the common radius of n disks in the ball (problem B of the study).
Methods: polished gradient descent (polishing share 0.25) and L-BFGS-B (exponent 2,500, the re-tuned value of tuned_params_retuned.json). Budget 1,500 sweeps. Fresh seeds 501 to 520 (20 seeds); the starting configuration of a seed and a condition is shared by both methods. 5,760 runs.
No run is excluded.

**Outcome.** For each condition, r = the largest mean radius over the 20 seeds of the two methods. Density deficit delta = 1 - [n Area(r) / Area(R)] / rho*(r), where rho*(r) is the upper bound on the density of any packing of disks of radius r in the whole space
(Fejes Toth 1943; Thue and Fejes Toth; Boroczky 1978; formulas of the study). Boundary share b = 1 - Area(R - r) / Area(R). A condition whose rho* is undefined (a cap disk radius above pi/3) is excluded and reported; none is expected.

**Rule A1 (curvature).** Least-squares fit delta = a + beta b + g_H [hyperbolic] + g_S [cap] over all conditions. The 95% interval of g_H is the percentile interval of 10,000 bootstrap resamples of the **48 cells** (all three spaces of a cell together, with replacement; seed 20261030),
which respects the pairing of the conditions. Decision for g_H: **detectable curvature effect** if the interval excludes 0 and g_H >= .02; **no detectable curvature effect** if the whole interval lies within -.02 to .02; **inconclusive** otherwise. The same rule is applied to g_S as a secondary result.
These are the thresholds of the confirmatory round (C2).

**Precision stated before the data.** With the residual SD of the confirmatory round (.058) the expected 95% half-width of g_H in this design is about .03, and about .02 if the residual SD is .04. The design can therefore show an effect of .03 or more;
it can show "no detectable effect" within the margin of .02 only if the residual SD is about .04 or less. An inconclusive result is possible, and it will be reported as such, with the interval.

**Rule A2 (paired, secondary).** For each cell, the mean difference in delta between the hyperbolic disk and the Euclidean disk, and between the cap and the Euclidean disk, with the 95% percentile interval of 10,000 bootstrap resamples of the cells. These differences include the effect of the different boundary share and are descriptive.

## 2. Question 2: can the number of disks that fit be predicted from the geometry alone?

**Predictive rule (fixed here, not refitted).** Let n_ref = floor(rho*(r0) Area(R) / Area(r0)), the number of disks of radius r0 that fit in a ball of radius R if the packing reached the whole-space upper bound, and b0 = 1 - Area(R - r0) / Area(R), the boundary share at the design radius.
**K_pred = floor(n_ref (1 - 0.46 b0) + 0.5)** (round half up). The constant 0.46 is the loss coefficient fitted by the follow-up on its five Euclidean conditions (0.4596) and rounded; it is not refitted on the data of this round.

**Design B.** Disk radii r0 in {0.25, 0.35} for the hyperbolic disk and the cap, design boundary shares b0 in {0.375, 0.425, 0.475, 0.525}, giving 8 conditions per space; the Euclidean disk has no length scale, so it is run once per b0 at r0 = 0.30 (4 conditions). 20 conditions in all, radii of the balls from b0 as in the mini-round.
K = the largest n, scanning n = n_ref, n_ref - 1, ..., for which polished gradient descent at 1,500 sweeps reaches radius r0 - 1e-9 in at least 10 of 20 fresh seeds (601 to 620); a scan at one n stops at 10 successes or 11 failures. (The second method of the follow-up never found a larger K than polished gradient descent in 33 conditions, so it is not used here.)

**Rule B1.** Let e = K - K_pred for each condition. **Supported** if the share of conditions with |e| <= 1 disk is at least .80, the mean |e| is at most 1.0 disk, the mean of |e| / K is at most .10, and the mean signed error of each space is within +/-1.0 disk.
**Not supported** if the share with |e| <= 1 is below .60 or the mean |e| exceeds 1.5 disks. **Inconclusive** otherwise. The rule is an empirical description of what these optimizers find; it is not derived from a theory of how a wall disturbs a packing, and agreement shows prediction, not mechanism.

## 3. Other commitments

* The two questions are separate and are not corrected for the earlier rules. No run is excluded; hardware is in hardware.json. Analyses not listed here are exploratory and labeled so; all deviations are listed in the Research Paper.
* Hypotheses in plain words: H-A, curvature adds a deficit at a given boundary share (the rule decides, in either direction); H-B, K can be predicted to within one disk in at least 80% of new conditions.
