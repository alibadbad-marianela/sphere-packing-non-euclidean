# Addendum 1 to the Preregistration of the Confirmatory Round

Study: Algorithmic Optimization of Dense Sphere Packings in Non-Euclidean Spaces (M. E. J. Alibadbad, Region VIII, MCS-I).

The confirmatory round (PREREGISTRATION.md, SHA-256 39bee69da1ffb2a23961dcbfeafafe9e63b421b5f88c9c79c27036cfadeaa7a0) was run and analyzed before this addendum was written.
Everything below was therefore decided **after the results of that round had been seen**. This addendum records what is changed, what is added, and what is not changed. No
result of the round is deleted or altered; the original runs_<cid>.csv files and decisions are kept. The hash of this file is recorded before any of the work below is run.

## 1. Corrections of wording (no change of analysis)

* In PREREGISTRATION.md the reference density rho* is described as "the density of the densest packing of disks of radius r in the whole space". The correct description is
  **an upper bound on the density of any packing of disks of radius r in the whole space** (Fejes Toth 1943, sphere; Thue and Fejes Toth, plane; Boroczky 1978, hyperbolic plane).
  The formulas and all computations are unchanged. The frozen file is not edited; this addendum is the correction.

## 2. Packomania reference values (entered after analysis)

* PREREGISTRATION.md allowed the Euclidean references to be the Packomania values "entered by the author before analysis". They were entered after the first analysis, which had used the best score found in the round.
  The analysis was repeated with the Packomania values (radius for container radius 1, scaled by the container radius of each condition); the decisions C1 to C6 are compared with the earlier ones
  and both sets are kept (decisions_best_found_references.json and decisions.json). A best score found that exceeds its Packomania value would be reported as a discrepancy.

## 3. Final configurations and the wall-ring analysis (added; exploratory)

* The confirmatory round is run again with identical seeds, parameters, and budgets, and now saves the final configuration of every run (out/conf/configs/). Every score of the rerun must equal the
  score of the original run to within 1e-9; any difference is reported.
* For each run in a ball condition with radius r (the score) let g_i = R - rho_i - r be the gap between disk i and the wall limit. Disk i **touches the wall** if g_i <= 0.01 r. Per run: touch share = share of
  disks that touch the wall; **wall-ring run** = a run in which every disk has g_i <= r (all disks lie within one disk radius of wall contact). Reported per condition and method: mean touch share and the share of wall-ring runs.
  This analysis is exploratory; it has no decision rule and no threshold.

## 4. Re-tuning of compression and L-BFGS-B (deviation, post hoc)

* In the confirmatory round the selected values of compression (initial growth rate 0.70) and L-BFGS-B (p_max 700) lay at the upper edge of their candidate ranges. The candidate settings are extended, for these two methods only:
  compression {0.10, 0.15, 0.25, 0.35, 0.50, 0.70, 1.0, 1.4, 2.0}; L-BFGS-B p_max {40, 80, 150, 250, 400, 700, 1000, 1500, 2500}. The same four pilot conditions, pilot seeds 9101 to 9104, budget, and selection rule
  (highest mean score relative to the best score seen in the pilot condition over all settings of both grids) are used. The tuning effort is now unequal (nine settings for these two methods and six for the others); this is stated in the paper.
* If a method is again selected at the new upper edge, no further extension is made and this is reported as a limitation.
* The two methods are then run again on all 33 conditions, three budgets, and seeds 101 to 120 (same starting configurations), with the new values. The decisions C4 and C5 are recomputed with the re-tuned methods and reported **next to** the
  original decisions; the original decisions remain the preregistered ones. The new tuned values are hashed before the evaluation runs.

## 5. Methods of non-circularity (added; see PREREGISTRATION_MINIROUND.md)

* The boundary share b and the density deficit delta in C1 both depend on the radius that a method finds, so C1 is partly circular. PREREGISTRATION_MINIROUND.md adds a test at a fixed disk radius, and a boundary-loss model, in a new
  preregistered mini-round with seeds 301 to 320. C1 and C2 are not changed.

## 6. Not changed

The design, conditions, seeds 101-120, budgets, methods, decision rules C1 to C6 and their thresholds, and the data of the confirmatory round.
