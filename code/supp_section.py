"""supp_section.py -- writes the section 'Supplementary Exploratory Analyses' of the paper from the supp_*.csv files.

Every number in the section is computed here from the data files; nothing is typed in by hand.
"""
import numpy as np
import pandas as pd
from scipy import stats

LABEL = {109: "Tammes <i>N</i> = 13", 112: "Tammes <i>N</i> = 30", 404: "Cap, <i>R</i> = 3, <i>n</i> = 19",
         304: "Euclidean, <i>R</i> = 3, <i>n</i> = 19", 204: "Hyperbolic, <i>R</i> = 3, <i>n</i> = 19"}
ORDER = [109, 112, 404, 304, 204]
AB = {"gd": "GD", "gdp": "GD+P", "sa": "SA", "ls": "CP"}
FULL = {"gd": "gradient descent", "gdp": "gradient descent with polishing", "sa": "simulated annealing", "ls": "compression"}


def build_section(d, FF, HD, Tb, f, pstr, DATA, runs, BUDGET):
    rd = lambda n: pd.read_csv(f"{DATA}/{n}")
    sens, gdp, tim = rd("supp_sensitivity_runs.csv"), rd("supp_gd_polish_runs.csv"), rd("supp_timing.csv")
    eqr, eqs, chk, spr = rd("supp_equal_area_runs.csv"), rd("supp_equal_area_summary.csv"), rd("supp_checks.csv"), rd("supp_initialization_spread.csv")
    C = dict(zip(chk.check, chk.value))
    ref = runs.groupby("condition_id").reference_value.first()
    sens["rel"] = sens.score / sens.condition_id.map(ref)
    main_mean = runs.groupby(["condition_id", "algorithm"]).relative_score.mean()
    gdp["rel"] = gdp.score / gdp.condition_id.map(ref)

    HD("Supplementary Exploratory Analyses", 2)
    d.body("The analyses in this section were added after the main results had been seen, in response to the limitations listed in the Conclusions. "
           "They use the same seeds, the same starting configurations, and the same budget unless stated, and none of them is used to decide H1, H2, or H3. "
           "Their code is supplementary.py, and their data are the files whose names begin with supp_.")
    # ---- headline numbers for the summary paragraph (same definitions as the tables below)
    _m = {a: runs[(runs.space == "S2") & (runs.n >= 24) & (runs.algorithm == a)].groupby("condition_id").relative_score.mean().mean() for a in ("gd", "sa")}
    _mp = gdp[(gdp.space == "S2") & (gdp.n >= 24)].assign(rel=lambda x: x.score / x.condition_id.map(ref)).groupby("condition_id").rel.mean().mean()
    def _succ(df, a):
        sub = df[(df.space == "S2") & (df.n <= 14) & (df.algorithm == a)]
        return int(((sub.score / sub.condition_id.map(ref) >= 0.999).groupby(sub.n).mean() >= 0.90).sum())
    _sc = {"gd": _succ(runs, "gd"), "gdp": _succ(gdp, "gdp"), "sa": _succ(runs, "sa")}
    _t = tim.groupby(["condition_id", "algorithm"]).time_s.mean()
    _rr = [_t[(c, "sa")] / _t[(c, "gd")] for c in ORDER]
    _extra = float((tim[tim.algorithm == "gdp"].groupby("condition_id").time_s.mean() - tim[tim.algorithm == "gd"].groupby("condition_id").time_s.mean()).mean())
    _ea = eqs[eqs.design == "equal-area"]
    _kw = stats.kruskal(*[_ea[_ea.space == sp].gd_minus_sa.values for sp in ("S2cap", "R2", "H2")])
    d.body("<i>Summary of the supplementary results.</i> " +
           f"(1) Numerical accuracy: all {int(C['n_scores_checked']):,} scores agreed with an independent recomputation to within {C['max_abs_diff_score_vs_independent']:.0e}. "
           f"(2) Polishing: gradient descent followed by a max-min polishing step raised the mean relative score on the sphere for <i>N</i> = 24 to 60 from {f(_m['gd'], 3, lead=False)} to {f(_mp, 3, lead=False)} (simulated annealing: {f(_m['sa'], 3, lead=False)}) "
           f"and the number of <i>N</i> from 4 to 14 with a success share of at least .90 from {_sc['gd']} to {_sc['gdp']} of 11 (simulated annealing: {_sc['sa']}); the polishing step uses a linear program that the sweep count does not charge, which added {f(_extra, 2)} seconds per run on average. "
           f"(3) Time: at equal sweeps, simulated annealing took {f(min(_rr), 1)} to {f(max(_rr), 1)} times as long as gradient descent. "
           f"(4) Sensitivity: moving one parameter at a time changed gradient descent and annealing very little and compression a great deal, and compression stayed last at every budget and parameter setting tried. "
           f"(5) Equal area: the gradient-descent minus annealing difference did not differ detectably across the three spaces (Kruskal–Wallis {pstr(float(_kw.pvalue))}), while larger balls reproduced the main-study sign pattern, so the apparent effect of the space is tied to ball size and is not shown to be caused by curvature. All of this is exploratory.")

    # ------------------------------------------------------------------ numerical accuracy
    HD("Numerical Accuracy and Independent Recomputation", 3)
    d.body(f"Every one of the {int(C['n_scores_checked']):,} final scores was recomputed from the saved coordinates with formulas that do not use the geometry code: the arctangent form of the sphere distance, the Poincaré-disk formula for the hyperbolic plane, and direct Euclidean distances. "
           f"The largest difference from the stored score was {C['max_abs_diff_score_vs_independent']:.1e}, the largest manifold error of any saved point was {C['max_manifold_error']:.1e}, and no disk extended beyond the wall of its ball (largest excess {C['max_disk_excess_beyond_wall']:.1f}). "
           f"These errors are many orders of magnitude below the 0.1% success tolerance, so rounding does not affect any success rate. "
           f"The distance code uses arcsine and arcsinh forms, which stay accurate for small distances where an arccosine would lose digits. These checks show that the stored scores are numerically sound; they do not show that any configuration is optimal.")

    # ------------------------------------------------------------------ gradient descent with polishing
    HD("Gradient Descent With a Polishing Step, and Wall-Clock Time", 3)
    grp = {"Sphere, <i>N</i> = 4 to 14": lambda r: (r.space == "S2") & (r.n <= 14), "Sphere, <i>N</i> = 24 to 60": lambda r: (r.space == "S2") & (r.n >= 24),
           "Spherical cap": lambda r: r.space == "S2cap", "Euclidean disk": lambda r: r.space == "R2", "Hyperbolic disk": lambda r: r.space == "H2"}
    two = runs.copy(); two["rel"] = two.relative_score
    allr = pd.concat([two[["space", "condition_id", "n", "algorithm", "seed", "rel"]], gdp[["space", "condition_id", "n", "algorithm", "seed", "rel"]]])
    rows = []
    gm = {}
    for lab, fn in grp.items():
        sub = allr[fn(allr)]
        cm = sub.groupby(["condition_id", "algorithm"]).rel.mean().groupby("algorithm").mean()
        gm[lab] = cm
        rows.append([lab] + [f(cm[a], 3, lead=False) for a in ("gd", "gdp", "sa", "ls")])
    sc = {}
    for a in ("gd", "gdp", "sa", "ls"):
        sub = allr[(allr.space == "S2") & (allr.n <= 14) & (allr.algorithm == a)]
        sh = (sub.assign(ok=(sub.rel >= 0.999)).groupby("n").ok.mean())
        sc[a] = int((sh >= 0.90).sum())
    rows.append(["<i>N</i> with success share ≥ .90 (of 11)"] + [str(sc[a]) for a in ("gd", "gdp", "sa", "ls")])
    FF("table", "gdp", "Mean Relative Score of Gradient Descent With and Without a Polishing Step",
       ["Problem group", "GD", "GD+P", "SA", "CP"], rows,
       "GD = gradient descent; GD+P = gradient descent on the first 85% of the budget followed by a max-min polishing step on the remaining 15%; SA = simulated annealing; CP = compression. "
       "Cells are the mean relative score over the conditions of the group (30 seeds each); the last row counts the values of <i>N</i> from 4 to 14 at which at least 90% of seeds reached a relative score of .999. "
       "GD, SA, and CP are the main-study runs. A value above 1.000 means the result exceeds the reference, which in the ball problems is the best score found in the main study, so values above 1.000 are possible there. Data: runs_raw.csv, supp_gd_polish_runs.csv.",
       aligns=["l", "c", "c", "c", "c"], widths=[2.7, 0.95, 0.95, 0.95, 0.95])
    s2 = gm["Sphere, <i>N</i> = 4 to 14"]; s3 = gm["Sphere, <i>N</i> = 24 to 60"]
    d.body(f"The main study suggested that the final precision of gradient descent, not its search, limits its success rate (the bound in Equation 7 allows a smoothing bias). To test this, gradient descent was followed by a max-min polishing step: the first 85% of the budget was used by the unchanged gradient descent, and the remaining 15% by a sequential linear program that maximizes the smallest distance within a shrinking trust region, with every polishing iteration charged as one sweep. "
           f"The step is a local refinement of the same kind as the L-BFGS refinement of a smoothed energy (Liu & Nocedal, 1989; Byrd et al., 1995), which was used as a baseline in the Confirmatory Round. With the same total budget, polishing changed the mean relative score on the sphere from {f(s2['gd'], 3, lead=False)} to {f(s2['gdp'], 3, lead=False)} for <i>N</i> = 4 to 14 and from {f(s3['gd'], 3, lead=False)} to {f(s3['gdp'], 3, lead=False)} for <i>N</i> = 24 to 60 ({Tb('gdp')}). "
           f"The number of values of <i>N</i> from 4 to 14 at which at least 90% of seeds reached the proven optimum within 0.1% changed from {sc['gd']} to {sc['gdp']} of 11 (simulated annealing: {sc['sa']}; compression: {sc['ls']}). "
           f"This is exploratory evidence about the explanation, not a revision of H3, which was decided on the three algorithms of the main study.")
    # timing
    tm = tim.groupby(["condition_id", "algorithm"]).time_s.mean()
    rows = []
    for cid in ORDER:
        rows.append([LABEL[cid]] + [f(tm[(cid, a)], 2) for a in ("gd", "gdp", "sa", "ls")] + [f(tm[(cid, "sa")] / tm[(cid, "gd")], 1)])
    FF("table", "timing", "Mean Wall-Clock Time per Run at Equal Budget",
       ["Condition", "GD", "GD+P", "SA", "CP", "SA / GD"], rows,
       f"Seconds per run at {BUDGET:,} sweeps, mean of 5 runs (seeds 1 to 5) per cell, measured in one process with nothing else running on the same computer. SA / GD = ratio of simulated-annealing time to gradient-descent time. "
       "The sweep budget is equal, but the time per sweep differs between methods and between implementations; times describe this Python code only. The main-study times are in summary_by_condition.csv. Data: supp_timing.csv.",
       aligns=["l", "c", "c", "c", "c", "c"], widths=[2.3, 0.7, 0.75, 0.7, 0.7, 0.85])
    rr = [tm[(c, "sa")] / tm[(c, "gd")] for c in ORDER]
    d.body(f"Equal sweeps do not mean equal time ({Tb('timing')}). Simulated annealing took {f(min(rr), 1)} to {f(max(rr), 1)} times as long as gradient descent per run in these five conditions, so the small advantage of annealing in some conditions was obtained with a much longer wall-clock time; "
           f"the polishing step added {f(float((tim[tim.algorithm == 'gdp'].groupby('condition_id').time_s.mean() - tim[tim.algorithm == 'gd'].groupby('condition_id').time_s.mean()).mean()), 2)} seconds per run on average because each polishing iteration solves a linear program that the sweep count does not charge.")

    # ------------------------------------------------------------------ sensitivity
    HD("Sensitivity to the Budget, the Parameters, and the Starting Configuration", 3)
    rows, same = [], 0
    for cid in ORDER:
        means = {}
        for a in ("gd", "sa", "ls"):
            m500 = sens[(sens.condition_id == cid) & (sens.algorithm == a) & (sens.variant == "budget 500")].rel.mean()
            m3000 = sens[(sens.condition_id == cid) & (sens.algorithm == a) & (sens.variant == "budget 3000")].rel.mean()
            rows.append([LABEL[cid] if a == "gd" else "", AB[a], f(m500, 3, lead=False), f(main_mean[(cid, a)], 3, lead=False), f(m3000, 3, lead=False)])
            means[a] = (m500, main_mean[(cid, a)], m3000)
        best = [max(("gd", "sa", "ls"), key=lambda a: means[a][k]) for k in range(3)]
        same += int(len(set(best)) == 1)
    FF("table", "budget", "Mean Relative Score at Three Budgets",
       ["Condition", "Algorithm", "500 sweeps", "1,500 sweeps", "3,000 sweeps"], rows,
       "Mean over 30 seeds, relative to the reference value of the main study (a value above 1.000 would exceed it). The 1,500-sweep column is the main study; the other columns use the same starting configurations and random streams. "
       "GD = gradient descent; SA = simulated annealing; CP = compression. Data: runs_raw.csv, supp_sensitivity_runs.csv.",
       aligns=["l", "l", "c", "c", "c"], widths=[2.4, 1.0, 1.0, 1.1, 1.1])
    gain = {a: np.mean([sens[(sens.condition_id == c) & (sens.algorithm == a) & (sens.variant == "budget 3000")].rel.mean() - main_mean[(c, a)] for c in ORDER]) for a in ("gd", "sa", "ls")}
    d.body(f"Tripling the budget from 500 to 1,500 sweeps and doubling it to 3,000 raised the mean relative score for every algorithm, and doubling from 1,500 to 3,000 sweeps changed it by {f(gain['gd'], 3, lead=False)} for gradient descent, {f(gain['sa'], 3, lead=False)} for simulated annealing, and {f(gain['ls'], 3, lead=False)} for compression on average over the five conditions ({Tb('budget')}). "
           f"The algorithm with the highest mean was the same at all three budgets in {same} of 5 conditions. The budget therefore matters, the conclusion that compression is last holds at every budget tested, and the ordering of gradient descent and simulated annealing depends on the condition and the budget.")
    # parameters
    rows = []
    spec = [("GD", "gd", "<i>p</i><sub>max</sub> = 75", "gd pmax=75"), ("GD", "gd", "<i>p</i><sub>max</sub> = 150 (default)", None), ("GD", "gd", "<i>p</i><sub>max</sub> = 300", "gd pmax=300"),
            ("SA", "sa", "<i>T</i><sub>0</sub> = 0.005 (default 0.02)", "sa T0=0.005"), ("SA", "sa", "<i>T</i><sub>0</sub> = 0.02 (default)", None), ("SA", "sa", "<i>T</i><sub>0</sub> = 0.08", "sa T0=0.08"),
            ("CP", "ls", "<i>γ</i><sub>0</sub> = 0.10", "ls g0=0.1"), ("CP", "ls", "<i>γ</i><sub>0</sub> = 0.25 (default)", None), ("CP", "ls", "<i>γ</i><sub>0</sub> = 0.50", "ls g0=0.5")]
    spread_ = {}
    for ab, a, lab, var in spec:
        vals = [(main_mean[(c, a)] if var is None else sens[(sens.condition_id == c) & (sens.algorithm == a) & (sens.variant == var)].rel.mean()) for c in ORDER]
        spread_.setdefault(a, []).append(vals)
        rows.append([f"{ab}: {lab}"] + [f(v, 3, lead=False) for v in vals] + [f(float(np.mean(vals)), 3, lead=False)])
    FF("table", "sens", "Mean Relative Score With One Parameter Changed",
       ["Setting"] + ["<i>N</i> = 13", "<i>N</i> = 30", "Cap", "Euclid.", "Hyperb."] + ["Mean"], rows,
       "Mean relative score over 30 seeds at 1,500 sweeps; <i>N</i> = 13 and <i>N</i> = 30 are Tammes problems; “Cap”, “Euclid.”, and “Hyperb.” are the balls with <i>R</i> = 3 and <i>n</i> = 19. "
       "<i>p</i><sub>max</sub> = final exponent of gradient descent; <i>T</i><sub>0</sub> = initial temperature of simulated annealing as a multiple of the length scale; <i>γ</i><sub>0</sub> = initial growth rate of compression. One parameter was changed at a time. Data: runs_raw.csv, supp_sensitivity_runs.csv.",
       aligns=["l", "c", "c", "c", "c", "c", "c"], widths=[2.1, 0.7, 0.7, 0.6, 0.75, 0.75, 0.6])
    rng_ = {a: (max(np.mean(v) for v in spread_[a]) - min(np.mean(v) for v in spread_[a])) for a in spread_}
    d.body(f"Changing one parameter at a time within the ranges in {Tb('sens')} moved the mean relative score by at most {f(rng_['gd'], 3, lead=False)} for gradient descent, {f(rng_['sa'], 3, lead=False)} for simulated annealing, and {f(rng_['ls'], 3, lead=False)} for compression (differences between the best and worst setting, averaged over the five conditions). "
           f"Only three of the nine values were tuned on the pilot seeds, so this is a local sensitivity check, not a new tuning: it asks whether the main conclusions depend on the exact default values, and it does not search for better ones.")
    # initialization spread
    rows = []
    for cid in ORDER:
        row = [LABEL[cid]]
        for a in ("gd", "sa", "ls"):
            r = spr[(spr.condition_id == cid) & (spr.algorithm == a)].iloc[0]
            row.append(f"{f(r['median'], 3, lead=False)} ({f(r['min'], 3, lead=False)}\u2013{f(r['max'], 3, lead=False)})")
        rows.append(row)
    FF("table", "spread", "Spread of the Relative Score Over 30 Starting Configurations",
       ["Condition", "GD", "SA", "CP"], rows,
       "Median relative score, with the minimum and maximum in parentheses, of single runs at 1,500 sweeps (seeds 1 to 30); each seed gives one starting configuration shared by the three algorithms. GD = gradient descent, SA = simulated annealing, CP = compression. Standard deviations are in supp_initialization_spread.csv. Data: runs_raw.csv.",
       aligns=["l", "c", "c", "c"], widths=[2.2, 1.45, 1.45, 1.45])
    sd13 = spr[(spr.condition_id == 109)].set_index("algorithm")["std"]
    d.body(f"The spread over starting configurations ({Tb('spread')}) shows local optima directly. For the Tammes problem with <i>N</i> = 13 the standard deviation of the relative score was {f(sd13['gd'], 3, lead=False)} for gradient descent, {f(sd13['sa'], 3, lead=False)} for simulated annealing, and {f(sd13['ls'], 3, lead=False)} for compression, "
           f"and no run reached the proven optimum, so different starts end in nearby but different local optima, and the best of 30 starts is a better estimate of what the method can reach than a single start. Whether a given local optimum is a strict local maximum was not tested.")

    # ------------------------------------------------------------------ equal area
    HD("Equal-Area and Larger-Ball Comparison", 3)
    ea = eqs[eqs.design == "equal-area"]
    rows = []
    for A in sorted(ea.area.unique()):
        for sp, lab in (("S2cap", "Cap"), ("R2", "Euclidean"), ("H2", "Hyperbolic")):
            g = ea[(ea.area == A) & (ea.space == sp)]
            rows.append([f"{A:g}", lab, f(g.R.min(), 2) + "–" + f(g.R.max(), 2) if g.R.nunique() > 1 else f(g.R.iloc[0], 2),
                         f(g.mean_gd.mean(), 3, lead=False), f(g.mean_sa.mean(), 3, lead=False), f(g.mean_ls.mean(), 3, lead=False), f(g.gd_minus_sa.mean(), 3, lead=False)])
    lg = eqs[eqs.design == "large-ball"]
    for r in lg.itertuples():
        rows.append([f"{r.area:.0f}", {"R2": "Euclidean", "H2": "Hyperbolic"}[r.space] + f", <i>n</i> = {r.n}", f(r.R, 2), f(r.mean_gd, 3, lead=False), f(r.mean_sa, 3, lead=False), f(r.mean_ls, 3, lead=False), f(r.gd_minus_sa, 3, lead=False)])
    FF("table", "equal", "Balls of Equal Area in the Three Spaces, and Larger Balls",
       ["Area", "Space", "<i>R</i>", "GD", "SA", "CP", "GD − SA"], rows,
       "The first nine rows are balls of equal area (3, 6, and 12) in the three spaces, averaged over <i>n</i> = 12, 19, and 30 (the radius <i>R</i> is the same for all <i>n</i>); the last four rows are single larger balls in the Euclidean and hyperbolic planes, which the sphere cannot contain. "
       "Cells are mean relative scores over 30 seeds, relative to the best score found in the same condition; GD − SA is the mean paired difference. Data: supp_equal_area_runs.csv, supp_equal_area_summary.csv.",
       aligns=["c", "l", "c", "c", "c", "c", "c"], widths=[0.6, 1.9, 0.9, 0.7, 0.7, 0.7, 0.9])
    gdsa = {sp: ea[ea.space == sp].gd_minus_sa.values for sp in ("S2cap", "R2", "H2")}
    kw = stats.kruskal(*gdsa.values())
    rk = eqr[eqr.design == "equal-area"].copy()
    rk["rank"] = rk.groupby(["condition_id", "seed"]).score.rank(ascending=False)
    mr = rk.groupby(["space", "algorithm"])["rank"].mean().unstack()
    best_eq = {sp: mr.loc[sp].idxmin() for sp in mr.index}
    h2l = lg[lg.space == "H2"]; r2l = lg[lg.space == "R2"]
    d.body(f"The main study could not separate curvature from area. To control for area, balls of the same area (3, 6, and 12) were packed in the three spaces with <i>n</i> = 12, 19, and 30 disks ({Tb('equal')}). "
           f"At equal area, the difference between gradient descent and simulated annealing did not differ detectably across the three spaces (median {f(np.median(gdsa['S2cap']), 4)} in the cap, {f(np.median(gdsa['R2']), 4)} in the Euclidean disk, and {f(np.median(gdsa['H2']), 4)} in the hyperbolic disk; Kruskal–Wallis <i>χ</i><sup>2</sup>(2) = {f(kw.statistic, 2)}, {pstr(kw.pvalue)}, nine settings per space), "
           f"and the algorithm with the lowest mean rank was {FULL[best_eq['S2cap']]} in the cap, {FULL[best_eq['R2']]} in the Euclidean disk, and {FULL[best_eq['H2']]} in the hyperbolic disk (mean ranks in the hyperbolic disk: {f(mr.loc['H2','gd'], 2)} for gradient descent and {f(mr.loc['H2','sa'], 2)} for simulated annealing). "
           f"In the two larger balls, which can exist only in the Euclidean and hyperbolic planes, the sign pattern of the main study returned: gradient descent minus simulated annealing was {f(r2l.gd_minus_sa.min(), 3, lead=False)} to {f(r2l.gd_minus_sa.max(), 3, lead=False)} in the Euclidean disk and {f(h2l.gd_minus_sa.min(), 3, lead=False)} to {f(h2l.gd_minus_sa.max(), 3, lead=False)} in the hyperbolic disk "
           f"(Holm-adjusted {pstr(float(h2l.p_holm_gd_sa.min()))} at the smallest in the hyperbolic disk, two settings only). "
           f"Together these results suggest that the apparent dependence of the ranking on the space in the main study is tied to the size of the ball and not shown to be caused by curvature, but this design cannot establish that: equal area is possible only up to 4π on the sphere, where hyperbolic curvature has little room to act, and the larger balls differ in both area and curvature.")

    # ------------------------------------------------------------------ robustness of H1
    d.heading("Robustness of the H1 Result", 3)
    d.body(f"The H1 contrast (gradient descent minus simulated annealing across the cap, the Euclidean disk, and the hyperbolic disk) gave a Kruskal–Wallis statistic of {f(C['H1_kruskal_chi2_mean_difference'], 2)} ({pstr(C['H1_kruskal_p_mean_difference'])} before Holm adjustment). "
           f"Replacing the per-setting mean difference by the median gave {f(C['H1_kruskal_chi2_median_difference'], 2)} ({pstr(C['H1_kruskal_p_median_difference'])}); a permutation test of the same statistic over the 18 settings (20,000 random relabelings of the three spaces) gave {pstr(C['H1_permutation_p_20000'])}; "
           f"restricting to the three settings with <i>R</i> = 2 gave {pstr(C['H1_kruskal_p_R2_settings'])} and to the three with <i>R</i> = 3 gave {pstr(C['H1_kruskal_p_R3_settings'])}. "
           f"All of these unadjusted values are of the same size as the original one, and multiplying any of them by 3 for the three algorithm pairs puts it above .05, so the conclusion is unchanged: the evidence is suggestive and not significant after correction. "
           f"For two headline paired differences, bootstrap percentile intervals agreed with the <i>t</i> intervals reported in the Statistical Comparison: for <i>N</i> = 60 on the sphere (gradient descent minus simulated annealing, in relative score) the mean was {f(C['gd_minus_sa_S2_N60_mean_relative'], 4)}, 95% <i>t</i> interval [{f(C['gd_minus_sa_S2_N60_t_lo'], 4)}, {f(C['gd_minus_sa_S2_N60_t_hi'], 4)}] and bootstrap interval [{f(C['gd_minus_sa_S2_N60_boot_lo'], 4)}, {f(C['gd_minus_sa_S2_N60_boot_hi'], 4)}]; "
           f"for the hyperbolic ball with <i>R</i> = 3 and <i>n</i> = 19 the mean was {f(C['gd_minus_sa_H2_R3_n19_mean_relative'], 4)}, [{f(C['gd_minus_sa_H2_R3_n19_t_lo'], 4)}, {f(C['gd_minus_sa_H2_R3_n19_t_hi'], 4)}] and [{f(C['gd_minus_sa_H2_R3_n19_boot_lo'], 4)}, {f(C['gd_minus_sa_H2_R3_n19_boot_hi'], 4)}]. "
           f"These robustness checks use the same 18 settings and the same seeds as the main analysis; they cannot add power, and they do not address the confounding of curvature with area.")
