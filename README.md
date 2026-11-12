# CSV Data for "Algorithmic Optimization of Dense Sphere Packings in Non-Euclidean Spaces"

Researcher: Marian Ela J. Alibadbad (Region VIII, MCS-I). Every file was produced by `python3 build_all.py`.
Seeds 1-30 are used for evaluation and are listed in `seed_list.csv`; pilot seeds 9001-9004 are never used in the evaluation.
All files are UTF-8, comma-separated, with a header row. Scores are in radians (sphere) or in the units of the space (ball problems).

## Files

### area_fractions.csv  (4 rows)

- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `spherical_area`: 2 pi (1 - cos R) for R <= pi, else empty.
- `spherical_fraction_within_1_of_boundary`: Share of the spherical cap's area within distance 1 of its boundary.
- `hyperbolic_area`: 2 pi (cosh R - 1).
- `hyperbolic_fraction_within_1_of_boundary`: Share of the hyperbolic disk's area within distance 1 of its boundary.
- `euclidean_area`: pi R^2.
- `euclidean_fraction_within_1_of_boundary`: Same for the Euclidean disk.

### assumption_checks.csv  (99 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `alg_a`: First algorithm of a pair.
- `alg_b`: Second algorithm of a pair.
- `n_nonzero`: Number of seeds with a nonzero paired difference.
- `share_zero_diff`: Share of seeds with a zero paired difference.
- `skewness`: Sample skewness of the paired differences (Wilcoxon symmetry check).
- `wilcoxon_symmetry_flag`: 1 if |skewness| > 1.

### benchmark_values.csv  (15 rows)

- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `theta_deg`: Published optimal minimum angular distance in degrees.
- `theta_rad`: Same in radians.
- `status`: Reference status: verified optimum, published best known, or best found.
- `source`: Literature source.

### capacity_fixed_radius.csv  (12 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `target_radius`: Target disk radius.
- `largest_tested_n_that_fits`: Largest tested n whose best radius reached the target (0 if none).
- `best_radius_at_that_n`: Best radius over all runs at that n.

### conf_deficit_boundary.csv  (26 rows)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `label`: Condition label or space name.
- `group`: Confirmatory round: tammes, equal_area, or large.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `best_method`: Method with the highest mean score in the condition (1,500 sweeps).
- `r_best`: That highest mean score (disk radius).
- `deficit`: Density deficit 1 - density / reference density.
- `boundary_share`: Share of the ball's area within distance r_best of its boundary.
- `ref_density`: Reference density: upper bound on the density of any packing of disks of radius r_best in the whole space.

### conf_gd_minus_sa_equal_area.csv  (18 rows)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `mean_gd_minus_sa`: Mean over seeds of the relative score of GD minus that of SA.
- `space`: Space of the condition (R2, H2, S2cap, or S2).

### conf_kendall_w.csv  (33 rows)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `kendall_W`: Kendall's W of the six methods across the three budget levels.

### conf_mean_ranks.csv  (33 rows)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `mean_rank_bh`: Same for basin hopping.
- `mean_rank_gd`: Mean rank of GD within seeds (1 = best).
- `mean_rank_gdp`: Same for GD+P.
- `mean_rank_lbfgsb`: Same for L-BFGS-B.
- `mean_rank_ls`: Same for compression.
- `mean_rank_sa`: Same for SA.

### conf_retuned_vs_original.csv  (198 rows)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `budget`: Budget in sweeps for the variant.
- `rel_old`: Mean relative score with the original tuned value.
- `rel_new`: Mean relative score with the re-tuned value.

### conf_runs.csv  (11,880 rows)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `group`: Confirmatory round: tammes, equal_area, or large.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `budget`: Budget in sweeps for the variant.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `recomputed_score`: Score recomputed again from the stored final configuration (integrity check; equals score).
- `density`: Ball problems only: share of the container area covered by the n disks.
- `sweeps_used`: pair_evals divided by n(n-1)/2.
- `time_s`: Wall-clock seconds for the run.
- `reference_value`: Reference score in the same units as score.
- `reference_type`: verified optimum (published value) or best found (highest score of any run in that condition).
- `relative_score`: score divided by reference_value.
- `success_0.1pct`: 1 if relative_score >= 0.999, else 0.
- `success_1pct`: 1 if relative_score >= 0.99, else 0.

### conf_summary_by_condition.csv  (594 rows)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `budget`: Budget in sweeps for the variant.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `mean_score`: Mean of score over seeds.
- `mean_rel`: Mean relative score over 20 seeds.
- `sd_rel`: Standard deviation of the relative score.
- `success_0p1`: Share of seeds with relative score >= .999.
- `success_1`: Share of seeds with relative score >= .99.
- `mean_time_s`: Mean wall-clock seconds.
- `mean_sweeps`: Mean budget used, in sweeps.
- `label`: Condition label or space name.
- `reference_type`: verified optimum (published value) or best found (highest score of any run in that condition).

### conf_time_by_method.csv  (18 rows)

- `budget`: Budget in sweeps for the variant.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `median_time_s`: Median wall-clock seconds per run.
- `mean_sweeps_used`: Mean budget used, in sweeps.

### conf_walls_by_condition.csv  (468 rows)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `budget`: Budget in sweeps for the variant.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `mean_touch_share`: Mean touch_share.
- `ring_share`: Share of runs with ring = 1.

### conf_walls_by_method.csv  (18 rows)

- `budget`: Budget in sweeps for the variant.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `runs`: Number of runs.
- `mean_touch_share`: Mean touch_share.
- `ring_share`: Share of runs with ring = 1.
- `median_max_gap_over_r`: Median of max_gap_over_r.

### configurations.csv  (49,500 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `index`: Index of the point or disk within the configuration (0-based).
- `x0`: Coordinate 1. Sphere: x. Hyperbolic plane: hyperboloid coordinate x0 (x0 = cosh of distance from origin). Euclidean plane: x.
- `x1`: Coordinate 2. Sphere: y. Hyperbolic plane: hyperboloid coordinate x1. Euclidean plane: y.
- `x2`: Coordinate 3. Sphere: z. Hyperbolic plane: hyperboloid coordinate x2. Euclidean plane: empty.

### convergence_traces.csv  (121,770 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `budget_fraction`: Fraction of the budget used (41 log-spaced values from 0.001 to 1).
- `best_score`: Best score so far at that budget fraction (same units as score).

### figure_assertions.csv  (61 rows)

- `assertion`: Name of a figure accuracy assertion.
- `passed`: True if it passed.
- `detail`: Numerical detail.

### hypothesis_tests.csv  (15 rows)

- `hypothesis`: H1, H2, or H3.
- `test`: Description of the test.
- `n_S2`: H1: number of sphere conditions.
- `n_H2`: H1: number of hyperbolic conditions.
- `median_diff_S2`: H1: median over sphere conditions of the per-condition mean paired difference in relative score.
- `median_diff_H2`: H1: same for hyperbolic conditions.
- `U`: Mann-Whitney U statistic.
- `p`: Raw p value.
- `p_holm`: Holm-adjusted p value (family = all tests of the same kind within one space; H1 and H2 families as in analyze.py).
- `significant`: 1 if p_holm < .05.
- `median_diff_S2cap`: H1: median over spherical-cap settings of the per-setting mean paired difference in relative score.
- `median_diff_R2`: H1: same for Euclidean settings.
- `chi2`: Friedman chi-square statistic (2 df), or chi-square of the slope Friedman test.
- `mean_diff`: Mean of (alg_a score - alg_b score) over seeds; in hypothesis_tests.csv, difference of mean slopes.
- `supported`: H3: 1 if the success rate is at least 0.90 at every N in 4..14.
- `mean_slope_a`: H2: mean over seeds of the slope of relative score on log10 N for the first algorithm.
- `mean_slope_b`: H2: same for the second algorithm.
- `rbc`: Matched-pairs rank-biserial correlation (positive = alg_a higher).
- `dz`: Standardized mean difference of the paired differences (mean / SD).
- `min_success_rate`: H3: smallest success rate over N = 4..14.
- `n_N_below_0p9`: H3: number of N in 4..14 with success rate below 0.90.

### mean_ranks.csv  (99 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `mean_rank`: Mean within-seed rank (1 = highest score of the three).

### overall_by_space.csv  (12 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `mean_rank`: Mean within-seed rank (1 = highest score of the three).
- `mean_relative_score`: Mean relative score pooled over all conditions of the space.

### runs_raw.csv  (2,970 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `density`: Ball problems only: share of the container area covered by the n disks.
- `pair_evals`: Pair-distance evaluations used (the budget unit).
- `sweeps_used`: pair_evals divided by n(n-1)/2.
- `iterations`: Algorithm-specific count: gradient steps (gd), proposed moves (sa), time steps (ls).
- `time_s`: Wall-clock seconds for the run.
- `sweeps_to_99pct`: Sweeps used when the best score so far first reached 99% of the run's own final score.
- `recomputed_score`: Score recomputed again from the stored final configuration (integrity check; equals score).
- `reference_type`: verified optimum (published value) or best found (highest score of any run in that condition).
- `reference_value`: Reference score in the same units as score.
- `relative_score`: score divided by reference_value.
- `gap_to_reference`: reference_value minus score.
- `success_0.1pct`: 1 if relative_score >= 0.999, else 0.
- `success_1pct`: 1 if relative_score >= 0.99, else 0.

### runtime_scaling_exponents.csv  (3 rows)

- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `time_exponent`: Slope of log10 mean time on log10 N (sphere, N >= 13).
- `time_intercept`: Intercept of that fit.

### scaling_slopes_per_seed.csv  (30 rows)

- `gd`: Slope per decade of N for gradient descent (scaling_slopes_per_seed.csv).
- `sa`: Same for simulated annealing.
- `ls`: Same for compression.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).

### seed_list.csv  (30 rows)

- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).

### summary_by_condition.csv  (99 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `n_seeds`: Number of seeds.
- `mean_score`: Mean of score over seeds.
- `sd_score`: Standard deviation of score (n-1).
- `ci95_lo`: Lower end of the 95% t confidence interval of the mean score.
- `ci95_hi`: Upper end of the same interval.
- `median_score`: Median score.
- `min_score`: Minimum score.
- `max_score`: Maximum score.
- `mean_relative`: Mean relative_score.
- `sd_relative`: Standard deviation of relative_score.
- `rel_ci95_lo`: Lower end of the 95% t interval of mean relative score.
- `rel_ci95_hi`: Upper end.
- `reference_type`: verified optimum (published value) or best found (highest score of any run in that condition).
- `reference_value`: Reference score in the same units as score.
- `mean_gap`: Mean gap_to_reference.
- `success_rate_0p1pct`: Share of seeds with success_0.1pct = 1.
- `success_rate_1pct`: Share of seeds with success_1pct = 1.
- `mean_density`: Mean density (ball problems).
- `sd_density`: Standard deviation of density.
- `mean_time_s`: Mean wall-clock seconds.
- `sd_time_s`: Standard deviation of seconds.
- `mean_sweeps_to_99`: Mean of sweeps_to_99pct.
- `mean_pair_evals`: Mean pair-distance evaluations.

### supp_checks.csv  (24 rows)

- `check`: Independent recomputation of the score from final coordinates.
- `value`: Value of the tuned parameter (tuning_runs.csv) or of the check (supp_checks.csv).

### supp_equal_area_runs.csv  (2,790 rows)

- `design`: Supplementary equal-area design label.
- `area`: Area of the ball.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `density`: Ball problems only: share of the container area covered by the n disks.
- `sweeps_used`: pair_evals divided by n(n-1)/2.
- `recomputed`: Score recomputed from final coordinates.
- `reference_value`: Reference score in the same units as score.
- `relative_score`: score divided by reference_value.

### supp_equal_area_summary.csv  (31 rows)

- `design`: Supplementary equal-area design label.
- `area`: Area of the ball.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `mean_gd`: Mean relative score of gradient descent.
- `mean_sa`: Mean relative score of simulated annealing.
- `mean_ls`: Mean relative score of compression.
- `gd_minus_sa`: mean_gd minus mean_sa.
- `p_wilcoxon_gd_sa`: Unadjusted Wilcoxon signed-rank p, GD vs SA.
- `p_friedman`: Friedman p across the three algorithms.
- `p_holm_gd_sa`: Holm-adjusted Wilcoxon p, GD vs SA, within the equal-area family.

### supp_gd_polish_runs.csv  (990 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `check`: Independent recomputation of the score from final coordinates.
- `sweeps_used`: pair_evals divided by n(n-1)/2.
- `time_s`: Wall-clock seconds for the run.
- `relative_score`: score divided by reference_value.
- `reference_value`: Reference score in the same units as score.
- `reference_type`: verified optimum (published value) or best found (highest score of any run in that condition).

### supp_initialization_spread.csv  (15 rows)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `min`: Minimum over seeds.
- `median`: Median over seeds.
- `max`: Maximum over seeds.
- `std`: Standard deviation over seeds.
- `label`: Condition label or space name.

### supp_sensitivity_runs.csv  (1,800 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `variant`: Sensitivity variant (budget, soft-minimum exponent, annealing schedule, or starting configuration).
- `budget`: Budget in sweeps for the variant.
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `check`: Independent recomputation of the score from final coordinates.

### supp_timing.csv  (100 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `time_s`: Wall-clock seconds for the run.
- `sweeps_used`: pair_evals divided by n(n-1)/2.
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).

### test_friedman.csv  (33 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `n_seeds`: Number of seeds.
- `chi2`: Friedman chi-square statistic (2 df), or chi-square of the slope Friedman test.
- `df`: Degrees of freedom.
- `p`: Raw p value.
- `kendall_W`: Kendall's W of the six methods across the three budget levels.
- `p_holm`: Holm-adjusted p value (family = all tests of the same kind within one space; H1 and H2 families as in analyze.py).
- `significant`: 1 if p_holm < .05.

### test_pairwise_wilcoxon.csv  (99 rows)

- `W`: Smaller of the two signed-rank sums of the Wilcoxon test.
- `p`: Raw p value.
- `rbc`: Matched-pairs rank-biserial correlation (positive = alg_a higher).
- `dz`: Standardized mean difference of the paired differences (mean / SD).
- `mean_diff`: Mean of (alg_a score - alg_b score) over seeds; in hypothesis_tests.csv, difference of mean slopes.
- `ci_lo`: Lower end of the 95% t interval of mean_diff.
- `ci_hi`: Upper end.
- `n_nonzero`: Number of seeds with a nonzero paired difference.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `alg_a`: First algorithm of a pair.
- `alg_b`: Second algorithm of a pair.
- `mean_rel_diff`: Mean of (alg_a - alg_b) divided by the reference value.
- `share_zero_diff`: Share of seeds with a zero paired difference.
- `skewness`: Sample skewness of the paired differences (Wilcoxon symmetry check).
- `p_holm`: Holm-adjusted p value (family = all tests of the same kind within one space; H1 and H2 families as in analyze.py).
- `significant`: 1 if p_holm < .05.
- `practical`: 1 if |mean_rel_diff| >= 0.005 (practical-importance threshold).
- `significant_and_practical`: 1 if significant and practical.
- `winner`: Algorithm significantly higher after Holm correction, or none.

### winner_by_condition.csv  (33 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `best_mean_algorithm`: Algorithm with the highest mean score in the condition.

### confirmatory/

All files of the confirmatory round and its follow-ups. Frozen originals are never regenerated: the `PREREGISTRATION*.md` files, the `*.sha256` files, `CORRECTION_NOTE_1.md`, `tuned_params*.json` and `hardware.json`.

- Preregistration documents: `PREREGISTRATION.md` (main round), `PREREGISTRATION_ADDENDUM_1.md`, `PREREGISTRATION_MINIROUND.md`, `PREREGISTRATION_FOLLOWUP.md`, `PREREGISTRATION_ROUND3.md`; `CORRECTION_NOTE_1.md` is the correction note. Their SHA-256 hashes, taken before the data they govern were produced, are in `PREREGISTRATION.sha256`, `PREREG_ADDENDA.sha256`, `FOLLOWUP.sha256`, `ROUND3.sha256`, `CORRECTION.sha256`, `RETUNED.sha256`, `TUNED_AND_ENV.sha256` and `PLAN_FILES.sha256`; `ROUND3_START.txt` and `ROUND3_END.txt` record the time stamps of round 3.
- `runs_<cid>.csv` (33 files, condition ids 1000-1032; 11,880 rows in all): one row per condition, method, budget and seed of the confirmatory round (columns as in `runs_raw.csv` plus `condition_id`, `recomputed_score`, `sweeps_used`).
- `retuned/runs_<cid>.csv`: the same conditions rerun with the re-tuned parameters of ADDENDUM 1; `tuned_params_retuned.json`, `decisions_retuned.json` and `decisions_best_found_references.json` hold the parameters and the decisions.
- `walls_<cid>.csv`: wall metrics of the final configurations (conditions 1007-1032, ball problems); `configs/cfg_<cid>.npz`: every final configuration, arrays `X[budget, seed, method, n, dim]`, `budgets`, `seeds`, `algs`; `configs.log` is the log of that rerun (maximum difference of recomputed scores).
- `tuning_runs.csv`, `tuning_runs_extended.csv`, `tuned_params.json`: tuning runs and the tuned values; `decisions.json`: the decisions C1-C6; `extra.json`: post-hoc analyses; `hardware.json`: the machine and software versions of the runs; `packomania_values.csv`: reference radii.
- Count-based problem: `count_runs.csv`, `count_summary.csv`. Mini-round: `mini_design.csv`, `mini_scan.csv`, `mini_summary.csv`, `mini_lbfgsb_scan.csv`, `mini_lbfgsb_summary.csv`, `mini_both_methods_summary.csv`, `mini_decisions.json`. Follow-up: `followup_design.csv`, `followup_scan.csv`, `followup_summary.csv`, `followup_decisions.json`, `FOLLOWUP_RUNTIMES.txt`. Round 3: `r3a_runs.csv` and `r3a_runs_<cid>.csv`, `r3a_conditions.csv`, `r3b_design.csv`, `r3b_scan.csv`, `r3b_summary.csv`, `round3_decisions.json`. Logs: `run.log`, `count.log`, `mini.log`, `followup.log`, `retuned.log`, `round3.log`.
- Column definitions of the CSV files in this folder are given below.

#### confirmatory/count_runs.csv  (700 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `area`: Area of the ball.
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `reached`: 1 if the score reached the radius.

#### confirmatory/count_summary.csv  (6 rows)

- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `area`: Area of the ball.
- `radius`: Disk radius of the count-based problem.
- `n_ref`: Reference count of disks.
- `K`: Largest number of disks of radius 0.30 reached in at least half of 20 seeds.
- `K_over_n_ref`: K divided by the reference count.
- `share_at_K`: Share of seeds that reached the radius at K.

#### confirmatory/followup_design.csv  (33 rows)

- `cid`: Condition id of the mini-round.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `label`: Condition label or space name.
- `r0`: Mini-round: fixed disk radius.
- `b0`: Mini-round: design boundary share.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `n_ref`: Reference count of disks.

#### confirmatory/followup_scan.csv  (3,160 rows)

- `cid`: Condition id of the mini-round.
- `method`: Method that produced the row (gdp = gradient descent with compression, lbfgsb = L-BFGS-B; or the name of the best method in r3a_conditions.csv).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `success`: 1 if the score reached the fixed radius r0 (mini-round) .

#### confirmatory/followup_summary.csv  (33 rows)

- `cid`: Condition id of the mini-round.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `label`: Condition label or space name.
- `r0`: Mini-round: fixed disk radius.
- `b0`: Mini-round: design boundary share.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `n_ref`: Reference count of disks.
- `K_gdp`: Largest disk count reached in at least half of the seeds by gradient descent with compression.
- `K_lbfgsb`: Largest disk count reached in at least half of the seeds by L-BFGS-B.
- `K`: Largest number of disks of radius 0.30 reached in at least half of 20 seeds.
- `deficit0`: Mini-round: fixed-radius density deficit.
- `deficit0_gdp`: Fixed-radius density deficit using K_gdp.
- `deficit0_lbfgsb`: Fixed-radius density deficit using K_lbfgsb.

#### confirmatory/mini_both_methods_summary.csv  (18 rows)

- `cid`: Condition id of the mini-round.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `label`: Condition label or space name.
- `r0`: Mini-round: fixed disk radius.
- `b0`: Mini-round: design boundary share.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `n_ref`: Reference count of disks.
- `K`: Largest number of disks of radius 0.30 reached in at least half of 20 seeds.
- `deficit0`: Mini-round: fixed-radius density deficit.
- `K_lbfgsb`: Largest disk count reached in at least half of the seeds by L-BFGS-B.
- `K2`: Larger of K and K_lbfgsb (both methods combined).
- `deficit0_best`: Fixed-radius density deficit using K2 (best of both methods).

#### confirmatory/mini_design.csv  (18 rows)

- `cid`: Condition id of the mini-round.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `label`: Condition label or space name.
- `r0`: Mini-round: fixed disk radius.
- `b0`: Mini-round: design boundary share.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `n_ref`: Reference count of disks.

#### confirmatory/mini_lbfgsb_scan.csv  (1,760 rows)

- `cid`: Condition id of the mini-round.
- `method`: Method that produced the row (gdp = gradient descent with compression, lbfgsb = L-BFGS-B; or the name of the best method in r3a_conditions.csv).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `success`: 1 if the score reached the fixed radius r0 (mini-round) .

#### confirmatory/mini_lbfgsb_summary.csv  (18 rows)

- `cid`: Condition id of the mini-round.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `label`: Condition label or space name.
- `r0`: Mini-round: fixed disk radius.
- `b0`: Mini-round: design boundary share.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `n_ref`: Reference count of disks.
- `K_gdp`: Largest disk count reached in at least half of the seeds by gradient descent with compression.
- `K_lbfgsb`: Largest disk count reached in at least half of the seeds by L-BFGS-B.
- `K`: Largest number of disks of radius 0.30 reached in at least half of 20 seeds.
- `deficit0`: Mini-round: fixed-radius density deficit.
- `deficit0_gdp`: Fixed-radius density deficit using K_gdp.
- `deficit0_lbfgsb`: Fixed-radius density deficit using K_lbfgsb.

#### confirmatory/mini_scan.csv  (863 rows)

- `cid`: Condition id of the mini-round.
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `success`: 1 if the score reached the fixed radius r0 (mini-round) .

#### confirmatory/mini_summary.csv  (18 rows)

- `cid`: Condition id of the mini-round.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `label`: Condition label or space name.
- `r0`: Mini-round: fixed disk radius.
- `b0`: Mini-round: design boundary share.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `n_ref`: Reference count of disks.
- `K`: Largest number of disks of radius 0.30 reached in at least half of 20 seeds.
- `deficit0`: Mini-round: fixed-radius density deficit.

#### confirmatory/packomania_values.csv  (5 rows)

- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `radius`: Disk radius of the count-based problem.

#### confirmatory/r3a_conditions.csv  (144 rows)

- `cid`: Condition id of the mini-round.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `area`: Area of the ball.
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `best_method`: Method with the highest mean score in the condition (1,500 sweeps).
- `r_best`: That highest mean score (disk radius).
- `deficit`: Density deficit 1 - density / reference density.
- `b`: Boundary share of the best configuration (share of the covered area that lies within one radius of the wall).
- `cell`: Cell label of round 3 part A: area and disk count joined by an underscore.

#### confirmatory/r3a_runs.csv  (5,760 rows)

- `cid`: Condition id of the mini-round.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `area`: Area of the ball.
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `method`: Method that produced the row (gdp = gradient descent with compression, lbfgsb = L-BFGS-B; or the name of the best method in r3a_conditions.csv).
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `recomputed`: Score recomputed from final coordinates.
- `time_s`: Wall-clock seconds for the run.

#### confirmatory/r3b_design.csv  (20 rows)

- `cid`: Condition id of the mini-round.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `r0`: Mini-round: fixed disk radius.
- `b0`: Mini-round: design boundary share.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `n_ref`: Reference count of disks.

#### confirmatory/r3b_scan.csv  (913 rows)

- `cid`: Condition id of the mini-round.
- `method`: Method that produced the row (gdp = gradient descent with compression, lbfgsb = L-BFGS-B; or the name of the best method in r3a_conditions.csv).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `success`: 1 if the score reached the fixed radius r0 (mini-round) .

#### confirmatory/r3b_summary.csv  (20 rows)

- `cid`: Condition id of the mini-round.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `r0`: Mini-round: fixed disk radius.
- `b0`: Mini-round: design boundary share.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `n_ref`: Reference count of disks.
- `K`: Largest number of disks of radius 0.30 reached in at least half of 20 seeds.
- `K_pred`: Predicted disk count, floor(n_ref (1 - 0.46 b0) + 0.5) (round 3, part B, rule B1).
- `deficit0`: Mini-round: fixed-radius density deficit.

#### confirmatory/tuning_runs.csv  (576 rows)

- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `value`: Value of the tuned parameter (tuning_runs.csv) or of the check (supp_checks.csv).
- `pilot`: Index of the pilot condition.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `time_s`: Wall-clock seconds for the run.
- `rel`: Score relative to the best pilot score.

#### confirmatory/tuning_runs_extended.csv  (672 rows)

- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `value`: Value of the tuned parameter (tuning_runs.csv) or of the check (supp_checks.csv).
- `pilot`: Index of the pilot condition.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `time_s`: Wall-clock seconds for the run.
- `rel`: Score relative to the best pilot score.

#### confirmatory/runs_*.csv  (33 files)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `group`: Confirmatory round: tammes, equal_area, or large.
- `space`: Space of the condition (R2, H2, S2cap, or S2).
- `n`: Sphere: number of points N. Ball problems: number of disks n.
- `R`: Container (ball) radius in the units of the space; empty for the sphere.
- `area`: Area of the ball.
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `budget`: Budget in sweeps for the variant.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `recomputed_score`: Score recomputed again from the stored final configuration (integrity check; equals score).
- `density`: Ball problems only: share of the container area covered by the n disks.
- `sweeps_used`: pair_evals divided by n(n-1)/2.
- `time_s`: Wall-clock seconds for the run.

#### confirmatory/walls_*.csv  (26 files)

- `condition_id`: Integer id of the condition: 100-114 sphere (N = 4,5,...,14,24,30,40,60), 200-205 hyperbolic ball, 300-305 Euclidean ball, 400-405 spherical-cap ball; the six ball settings are (R,n) = (2,7),(2,12),(2,19),(3,12),(3,19),(3,30).
- `algorithm`: gd = gradient descent, sa = simulated annealing, ls = compression (Lubachevsky-Stillinger-style), gdp = gradient descent with a final max-min polishing step (supplementary files only).
- `budget`: Budget in sweeps for the variant.
- `seed`: Random seed 1-30 shared by all algorithms (the initial configuration depends only on seed and condition).
- `score`: Final score recomputed from the final coordinates: minimum geodesic distance in radians (sphere) or common disk radius (ball problems, units of the space).
- `touch_share`: Share of disks whose gap to the wall limit is at most 1% of the disk radius.
- `ring`: 1 if every disk lies within one disk radius of the wall limit.
- `max_gap_over_r`: Largest gap of a disk to the wall limit, in units of the disk radius.

### code/frozen/

Unchanged copies of the preregistration documents, their `.sha256` files and `packomania_values.csv`, kept next to the code so that the scripts can check them before every run.

### code/

All 38 Python source files (the same files as in Code_Listing.docx), including the confirmatory scripts `confirm_*.py`, `newalgs.py`, `supplementary.py` and `record_env.py`. To regenerate every result, run `python3 tests.py` and then `python3 build_all.py` from this folder; the scripts create a sibling `out/` folder with all data, figures, and documents (about 17 minutes for the first study, plus about 30 minutes for the supplementary analyses and about 1 hour for the confirmatory round on two processes; Python 3 with numpy, scipy, pandas, matplotlib, python-docx, Pygments, pdfplumber, Pillow; the document builders also need LibreOffice and the Liberation fonts).

### unit_test_output.txt

Complete output of `python3 tests.py` (validation tests, run before the experiments).

## Verification

`MANIFEST.sha256` lists the SHA-256 hash of every file. Check with `sha256sum -c MANIFEST.sha256` from this folder.
