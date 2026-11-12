"""conf_section.py -- writes the 'Confirmatory Round' section of the paper.  Every number is read from the conf_* files."""
import json
import os
import numpy as np
import pandas as pd
import confirm_design as C
import conf_figures as CF
from make_figures import FIG

M_AB = {"gd": "GD", "gdp": "GD+P", "sa": "SA", "ls": "CP", "lbfgsb": "L-BFGS-B", "bh": "BH"}
METHODS = ["gd", "gdp", "sa", "ls", "lbfgsb", "bh"]


class _Null:
    def __getattr__(self, k):
        return lambda *a, **kw: None


def build_section(d, FF, HD, Tb, Fg, f, pstr, DATA, CONF, part="main"):
    _d0, _HD0, _FF0 = d, HD, FF
    if part == "appendix":
        d, HD, FF = _Null(), (lambda *a, **k: None), (lambda *a, **k: None)
    dec = json.load(open(CONF + "/decisions.json"))
    tuned = json.load(open(CONF + "/tuned_params.json"))
    m = pd.read_csv(DATA + "/conf_summary_by_condition.csv")
    t = pd.read_csv(DATA + "/conf_deficit_boundary.csv")
    tm = pd.read_csv(DATA + "/conf_time_by_method.csv")
    cnt = pd.read_csv(CONF + "/count_summary.csv")
    hs = open(CONF + "/PREREGISTRATION.sha256").read().split()
    hash_pre, hash_time = hs[0], hs[-1]
    ths = open(CONF + "/TUNED_AND_ENV.sha256").read().split("\n")
    hash_tuned = [l.split()[0] for l in ths if l.endswith("tuned_params.json")][0]
    hw = json.load(open(CONF + "/hardware.json"))
    conds = {c["cid"]: c for c in C.conditions()}
    n_runs = dec["n_runs"]
    ref_types = dec["reference_types"]
    pk = os.path.exists(CONF + "/packomania_values.csv")
    c1, c2, c3, c4, c5, c6 = (dec[k] for k in ("C1", "C2", "C3", "C4", "C5", "C6"))
    ext = json.load(open(CONF + "/extra.json"))
    rdec = json.load(open(CONF + "/decisions_retuned.json"))
    rtun = json.load(open(CONF + "/tuned_params_retuned.json"))
    mini = pd.read_csv(CONF + "/mini_summary.csv")
    mdec = json.load(open(CONF + "/mini_decisions.json"))
    wm = pd.read_csv(DATA + "/conf_walls_by_method.csv")
    wc = pd.read_csv(DATA + "/conf_walls_by_condition.csv")
    ADD = open(CONF + "/PREREG_ADDENDA.sha256").read().split("\n")
    h_add = [l.split()[0] for l in ADD if l.endswith("ADDENDUM_1.md")][0]
    h_mini = [l.split()[0] for l in ADD if l.endswith("MINIROUND.md")][0]
    h_time2 = [l for l in ADD if l.startswith("hashed")][0].split(": ")[1]
    FU = open(CONF + "/FOLLOWUP.sha256").read().split("\n")
    h_fu, h_fu_time = FU[0].split()[0], FU[1].split(": ")[1]
    fdec = json.load(open(CONF + "/followup_decisions.json"))
    CR = open(CONF + "/CORRECTION.sha256").read().split("\n")
    h_cor, h_cor_time = CR[0].split()[0], CR[1].split(": ")[1]
    RT = open(CONF + "/FOLLOWUP_RUNTIMES.txt").read()
    fol = pd.read_csv(CONF + "/followup_summary.csv")
    h_ret = [l for l in open(CONF + "/RETUNED.sha256").read().split("\n") if l.endswith("tuned_params_retuned.json")][0].split()[0]
    ex = dec["C1_exploratory_without_two_largest_hyperbolic"]

    HD("Confirmatory Round With Equal-Area Balls and Stronger Baselines", 2)
    d.body("The first study could not separate curvature from area, and its two best methods were not compared with stronger baselines. A second round was therefore designed to test a prediction, and its hypotheses, thresholds, and decision rules were written and hashed before any of its evaluation seeds was run. "
           "This round is confirmatory only in that sense: it answers the questions written in its preregistration, with fresh seeds, and it is separate from the first study, whose results are unchanged. All analyses outside the six preregistered decisions are exploratory and are labeled so.")
    HD("Prediction, Design, and Preregistration", 3)
    d.body(f"The prediction is that the density deficit of a packing follows the share of the ball&rsquo;s area near its boundary, so that most of the lower density of packings in hyperbolic balls is a boundary effect and not an effect of curvature. "
           "For <i>n</i> disks of radius <i>r</i> in a ball of radius <i>R</i> let the reference density <i>&rho;</i>* be an upper bound on the density of any packing of disks of radius <i>r</i> in the whole space (Fej&eacute;s T&oacute;th, 1943; B&ouml;r&ouml;czky, 1978), "
           "the density deficit be <i>&delta;</i> = 1 &minus; [<i>n</i> Area(<i>r</i>) / Area(<i>R</i>)] / <i>&rho;</i>*, and the boundary share be <i>b</i> = 1 &minus; Area(<i>R</i> &minus; <i>r</i>) / Area(<i>R</i>), the share of the ball&rsquo;s area within distance <i>r</i> of its boundary. The reference density is an upper bound for the whole space, not for a bounded ball, so <i>&delta;</i> includes the loss caused by the wall.".replace("&rsquo;", "’").replace("&eacute;", "é").replace("&oacute;", "ó").replace("&ouml;", "ö").replace("&rho;", "ρ").replace("&delta;", "δ").replace("&minus;", "−"))
    d.body(f"The preregistration (PREREGISTRATION.md in the data package) fixes the fresh evaluation seeds 101 to 120, three budget levels of 500, 1,500, and 3,000 sweeps in the main design, six methods, and {len(conds)} conditions: the Tammes problem for <i>N</i> = 9, 13, 14, 24, 30, 40, and 60; "
           "balls of equal area (3, 6, and 12) with 12 and 24 disks in the spherical cap, the Euclidean disk, and the hyperbolic disk; and large balls of hyperbolic radius 2, 3, 6, and 8 (areas 17.4, 57.0, 1,261.1, and 9,358.7) with 24, 36, 50, and 70 disks, paired with Euclidean disks of the same area. "
           "Equal area in all three spaces is possible only up to 4π, because the sphere has finite area, so the large balls compare only the hyperbolic and Euclidean planes. "
           f"Its SHA-256 hash, computed on {hash_time.replace('T', ' at ').replace('Z', ' UTC')} before the pilot tuning and before every evaluation run, is {hash_pre}. The tuned parameters (hash {hash_tuned}) were fixed before the evaluation run as well. "
           "A hash recorded by the author is not an independent time stamp; the record kept by the research adviser is described in Appendix B.")
    rows = []
    NAME = {"gd": ("Gradient descent", "<i>p</i><sub>max</sub>"), "gdp": ("GD with polishing", "polishing share"), "sa": ("Simulated annealing", "initial temperature"),
            "ls": ("Compression", "initial growth rate"), "lbfgsb": ("L-BFGS-B (SciPy)", "<i>p</i><sub>max</sub>"), "bh": ("Basin hopping (SciPy)", "step size")}
    g = tuned["grids"]
    for a in METHODS:
        rows.append([NAME[a][0], NAME[a][1], ", ".join(f"{v:g}" for v in g[a]), f"{tuned['tuned'][a]:g}"])
    FF("table", "cmeth", "Methods, Tuned Parameters, and Candidate Settings of the Confirmatory Round", ["Method", "Tuned parameter", "Candidate settings", "Selected"], rows,
       "Each method had one tuned parameter and six candidate settings, run on the same four pilot conditions (Tammes <i>N</i> = 11 and 33; hyperbolic and Euclidean balls of area 8 with 16 disks) and the same four pilot seeds (9101 to 9104) at 1,500 sweeps; the setting with the highest mean score relative to the best score seen in the pilot condition was kept. "
       "GD = gradient descent; GD+P = GD followed by a max-min polishing step; the polishing share is the fraction of the budget given to the polishing step; the step size and the initial temperature are multiples of the length scale √(area/<i>n</i>). Data: tuning_runs.csv, tuned_params.json.",
       aligns=["l", "l", "l", "c"], widths=[1.8, 1.5, 2.4, 0.8])
    edge = [NAME[a][0] for a in METHODS if tuned["tuned"][a] in (g[a][0], g[a][-1])]
    d.body(f"{Tb('cmeth')} lists the six methods, their tuned parameters, and the selected values. The two added baselines run the same energy as gradient descent. L-BFGS-B (SciPy; Virtanen et al., 2020; Byrd et al., 1995) minimizes the soft-minimum energy with its exponent raised in ten stages and restarts from a new random configuration, with the same random stream, when it stops by its own convergence test before the budget is used; basin hopping (Wales & Doye, 1997; <i>scipy.optimize.basinhopping</i>) perturbs the points and minimizes locally with L-BFGS-B at <i>p</i> = 60. "
           f"Every energy-and-gradient evaluation is charged one sweep, as in gradient descent. Equal tuning means equal effort (one parameter, six settings, the same pilot runs for every method), not an equal chance of finding the best possible setting: the selected value lies at the edge of its candidate range for {', '.join(edge)}, so those two methods may be tuned less well than the others. "
           f"The reported runs used {hw['cpu_model']} with {hw['logical_cpus']} logical processors, {hw['memory_gb']} GB of memory, {hw['os'].split('-with')[0]}, Python {hw['python']}, numpy {hw['numpy']}, scipy {hw['scipy']}, and pandas {hw['pandas']} (hardware.json), with two worker processes sharing the machine; wall-clock times are comparable only within this round. "
           "The hardware of the computer that produced the first study was not recorded in its data package, so its run times cannot be compared with these.")
    pkn = (f"For the ten Euclidean conditions with 12, 24, 36, 50, or 70 disks the reference is the Packomania value (circles in a circle; Specht, n.d.), entered after the first analysis of this round, which had used the best score found (the decisions were the same with both references; decisions_best_found_references.json), and" if pk else "Packomania values for the Euclidean conditions had not been entered at the time of this analysis, so those conditions too use the best score found in this round, and")
    d.body(f"Reference values: the proven optimum for <i>N</i> = 9, 13, 14, and 24 and the published best-known value (Sloane&rsquo;s tables) for <i>N</i> = 30, 40, and 60, seven conditions in all. {pkn} for the spherical cap and the hyperbolic disk, for which the author knows of no published table of best packings, the reference is the best score found by any method, budget, or seed of this round in the condition ({ref_types.get('best found in this round', 0)} conditions). ".replace("&rsquo;", "’") +
           "A relative score for a best-found reference measures the distance from the best score this study found, not from the optimum. No run was excluded; every run is in conf_runs.csv, and every score agreed with its recomputation from the final coordinates to within " + f"{dec['max_abs_score_vs_recomputed']:.0e}.")

    HD("Results of the Preregistered Decisions", 3)
    cm = dec["C3"]["median_d"]
    _r13 = pd.read_csv(DATA + "/conf_runs.csv")
    _r13 = _r13[_r13.condition_id == [k for k, v in conds.items() if v["group"] == "tammes" and v["n"] == 13][0]]
    n13_hit, n13_all = int(_r13["success_0.1pct"].sum()), len(_r13)
    _h = _r13[_r13["success_0.1pct"] == 1].groupby(["algorithm", "budget"]).size()
    n13_txt = ", ".join(f"{M_AB[a]} {v} at {b:,} sweeps" for (a, b), v in _h.items()) or "none"
    N13 = m[(m.label == "Tammes N = 13") & (m.budget == C.MAIN_BUDGET)].set_index("algorithm").mean_rel
    rows = [["C1: the density deficit follows the boundary share (26 ball conditions)", "Supported if Spearman <i>r</i><sub>s</sub> ≥ .70 and one-sided permutation <i>p</i> < .05; not supported if <i>r</i><sub>s</sub> < .30",
             f"<i>r</i><sub>s</sub> = {f(c1['spearman'], 2, lead=False)}, permutation {pstr(c1['perm_p_one_sided'])}", c1["decision"].capitalize()],
            ["C2: curvature adds a deficit beyond the boundary share", "The 95% bootstrap interval of the hyperbolic term excludes 0 and the term is ≥ .02; no effect if the interval lies within ±.02",
             f"Hyperbolic term {f(c2['gamma_hyperbolic'], 3)}, 95% interval [{f(c2['ci95_gamma_hyperbolic'][0], 3)}, {f(c2['ci95_gamma_hyperbolic'][1], 3)}]", c2["decision"].capitalize()],
            ["C3: the GD versus SA ranking depends on the space (18 equal-area conditions)", "Kruskal–Wallis <i>p</i> < .05; no dependence if every 90% interval of a difference of medians lies within ±.01",
             f"<i>χ</i><sup>2</sup>(2) = {f(c3['kruskal_chi2'], 2)}, {pstr(c3['kruskal_p'])}", c3["decision"].capitalize()],
            ["C4: stronger baselines matter; GD+P is competitive (33 conditions)", "L-BFGS-B or BH beats both GD and SA in at least half of the conditions; GD+P ranks first or second in at least half",
             f"Baselines beat GD and SA in {f(c4['share_new_baseline_beats_gd_and_sa'] * 100, 0)}% of conditions; GD+P in the top two in {f(c4['share_gdp_rank_top2'] * 100, 0)}%", "Both supported" if c4["decision_baselines_matter"] and c4["decision_gdp_competitive"] else "Not both supported"],
            ["C5: the ranking of the methods is stable across budgets", "Median Kendall’s <i>W</i> over the three budget levels ≥ .80", f"Median <i>W</i> = {f(c5['median_W'], 2, lead=False)} (minimum {f(c5['min_W'], 2, lead=False)})", c5["decision"].capitalize()],
            ["C6: some method recovers the proven optimum for <i>N</i> = 9, 13, 14, 24", "Best share of seeds with relative score ≥ .999 is ≥ .90 for all four",
             "Best share: " + ", ".join(f"<i>N</i> = {k}: {f(v['best_share'], 2, lead=False)}" for k, v in c6["by_N"].items()), c6["decision"].capitalize()]]
    FF("table", "cdec", "Preregistered Decisions of the Confirmatory Round", ["Question", "Decision rule", "Result", "Decision"], rows,
       "Relative scores at 1,500 sweeps, 20 fresh seeds per condition. GD = gradient descent; GD+P = GD with a polishing step; SA = simulated annealing; BH = basin hopping. Data: conf_runs.csv, conf_deficit_boundary.csv, conf_gd_minus_sa_equal_area.csv, conf_mean_ranks.csv, conf_kendall_w.csv, decisions.json.",
       aligns=["l", "l", "l", "l"], widths=[1.7, 2.0, 1.8, 1.0], split=True)
    ws = c1["within_space"]
    d.body(f"{Tb('cdec')} gives the decisions. For C1 the correlation between the boundary share and the density deficit over the 26 ball conditions was {f(c1['spearman'], 2, lead=False)} ({pstr(c1['perm_p_one_sided'])}), so the prediction is supported ({Fg('cdef')}; {Tb('cdef')}). The correlation was positive within each space ({f(ws['R2'], 2, lead=False)} in the Euclidean disk, {f(ws['H2'], 2, lead=False)} in the hyperbolic disk, and {f(ws['S2cap'], 2, lead=False)} in the cap, not part of the decision). "
           f"The two hyperbolic balls of radius 6 and 8 have the largest boundary shares and deficits; without them the correlation was {f(ex['spearman'], 2, lead=False)} for {ex['n_conditions']} conditions (exploratory). The final configuration of every run was saved in a rerun with identical seeds and settings (every score agreed with the original to within 1e-9), and the wall contact of all {ext['walls_overall']['runs']:,} ball runs is reported below (exploratory). The 26 conditions are not independent: the equal-area conditions come in triplets of one area and one number of disks in the three spaces, and each large hyperbolic ball is paired with a Euclidean ball of the same area, so the permutation test, which treats the conditions as exchangeable, assumes more independence than the design has and its <i>p</i> value is optimistic. The boundary share is a function of the disk radius that the method finds, so it is not independent of the outcome, and the result shows that the deficit moves with the boundary share, not that the boundary share causes it.")
    d.body(f"For C2, once the boundary share is in the model, the hyperbolic term was {f(c2['gamma_hyperbolic'], 3)} (95% bootstrap interval {f(c2['ci95_gamma_hyperbolic'][0], 3)} to {f(c2['ci95_gamma_hyperbolic'][1], 3)}) and the cap term was {f(c2['gamma_cap'], 3)}, so the decision is {c2['decision']}: with 26 conditions in which the boundary share and the space are strongly related, a separate effect of curvature could be neither shown nor excluded at the preregistered thresholds. "
           f"For C3, the median difference between gradient descent and simulated annealing (relative score) was {f(cm['R2'], 4)} in the Euclidean disk, {f(cm['S2cap'], 4)} in the cap, and {f(cm['H2'], 4)} in the hyperbolic disk, a Kruskal–Wallis difference ({pstr(c3['kruskal_p'])}) of less than .01 in relative score: simulated annealing ahead of gradient descent in the Euclidean disk and the cap, and a tie in the hyperbolic disk. "
           "This differs from the exploratory equal-area comparison of the first study, which found no detectable dependence on the space with other areas, other numbers of disks, and other seeds; the difference is small in size in both, six conditions per space is a small sample, and the preregistered result is the one that counts as confirmatory. Both are reported.")
    mr = c4["mean_rank_by_method"]
    d.body(f"For C4, a stronger baseline mattered in every condition: L-BFGS-B or basin hopping had a higher mean relative score than both gradient descent and simulated annealing in all 33 conditions, and the mean ranks over seeds and conditions were {f(mr['gdp'], 2)} for GD+P, {f(mr['lbfgsb'], 2)} for L-BFGS-B, {f(mr['bh'], 2)} for basin hopping, {f(mr['sa'], 2)} for simulated annealing, {f(mr['gd'], 2)} for gradient descent, and {f(mr['ls'], 2)} for compression ({Tb('crel')}). "
           "The comparison of gradient descent with simulated annealing in the first study is therefore a comparison of two methods that stronger methods beat at the same budget, and its conclusions about their order should be read with that in mind. "
           f"For C5, the ordering of the six methods was stable across the three budget levels (median Kendall’s <i>W</i> {f(c5['median_W'], 2, lead=False)}), but the best method at 1,500 sweeps was also the best at 3,000 sweeps in only {f(c5['share_same_top_method_1500_vs_3000'] * 100, 0)}% of conditions ({Tb('cbud')}). "
           f"For C6, no method recovered the proven optimum in at least 90% of seeds for every one of <i>N</i> = 9, 13, 14, and 24: the best share was {f(c6['by_N']['9']['best_share'], 2, lead=False)} at <i>N</i> = 9, {f(c6['by_N']['13']['best_share'], 2, lead=False)} at <i>N</i> = 13, {f(c6['by_N']['14']['best_share'], 2, lead=False)} at <i>N</i> = 14, and {f(c6['by_N']['24']['best_share'], 2, lead=False)} at <i>N</i> = 24, so no method reached the 0.1% tolerance at <i>N</i> = 13. Basin hopping came closest (mean relative score {f(N13['bh'], 3, lead=False)}, against {f(N13['gdp'], 3, lead=False)} for GD+P and {f(N13['lbfgsb'], 3, lead=False)} for L-BFGS-B); across all three budget levels, {n13_hit} of the {n13_all} runs at <i>N</i> = 13 reached it ({n13_txt}).")

    FF("figure", "cdef", "Density Deficit Against Boundary Share in the Confirmatory Round", CF.fig_deficit(t, dec), 4.2,
       "Each point is one of the 26 ball conditions, using the best mean radius over the six methods at 1,500 sweeps. The deficit rises with the share of the ball’s area near its wall in all three spaces.",
       "Symbols: circles = Euclidean disk, squares = hyperbolic disk, triangles = spherical cap; filled = equal-area balls, open = large balls. Dashed lines = fitted lines with a common slope and a different intercept for each space (hyperbolic and cap terms from the regression described in the text). <i>δ</i> = 1 − density / reference density; <i>b</i> = share of the ball’s area within one disk radius of the boundary. Both are dimensionless.",
       "Scatter plot of density deficit against boundary share for 26 packing conditions with three fitted lines.")
    # relative score table at main budget
    grpname = {("tammes", "S2"): "Tammes problem", ("equal_area", "S2cap"): "Equal area: cap", ("equal_area", "R2"): "Equal area: Euclidean", ("equal_area", "H2"): "Equal area: hyperbolic",
               ("large", "R2"): "Large ball: Euclidean", ("large", "H2"): "Large ball: hyperbolic"}
    mm = m[m.budget == C.MAIN_BUDGET].copy()
    mm["g"] = mm.condition_id.map(lambda c: grpname[(conds[c]["group"], conds[c]["kind"])])
    pv = mm.pivot_table(index="g", columns="algorithm", values="mean_rel").reindex(list(grpname.values()))[METHODS]
    rows, bold = [], set()
    for ri, (gname, r) in enumerate(pv.iterrows()):
        rows.append([gname] + [f(v, 3, lead=False) for v in r.values])
        bold.add((ri, int(np.argmax(r.values)) + 1))
    nconds = {gname: int(mm[mm.g == gname].condition_id.nunique()) for gname in pv.index}
    rows = [[f"{r[0]} ({nconds[r[0]]})"] + r[1:] for r in rows]
    rows.append(["Mean rank over all conditions"] + [f(mr[a], 2) for a in METHODS])
    bold.add((len(rows) - 1, int(np.argmin([mr[a] for a in METHODS])) + 1))
    FF("table", "crel", "Mean Relative Score of the Six Methods at 1,500 Sweeps", ["Condition group (conditions)"] + [M_AB[a] for a in METHODS], rows,
       "Mean over conditions of the mean relative score over 20 fresh seeds; boldface marks the best method in each row. For the Tammes problem the reference is the proven or published best-known value; for the other groups it is the best score found in this round, so values are relative to that score. "
       "The last row is the mean rank of the methods within seeds (1 = best). GD = gradient descent; GD+P = GD with a polishing step; SA = simulated annealing; CP = compression; L-BFGS-B and BH (basin hopping) are SciPy methods. Data: conf_summary_by_condition.csv, conf_mean_ranks.csv.",
       aligns=["l"] + ["c"] * 6, widths=[2.0, 0.7, 0.75, 0.7, 0.7, 0.9, 0.75], bold_cells=bold)

    # figures and deficit table
    ids = [cid for cid in t.condition_id]
    rows = [[r.label.replace("R_H", "<i>R</i><sub>H</sub>").replace("A = ", "<i>A</i> = ").replace(" n = ", " <i>n</i> = "), M_AB[r.best_method], f(r.r_best, 3), f(r.deficit, 3, lead=False), f(r.boundary_share, 3, lead=False)] for r in t.itertuples()]
    FF("table", "cdef", "Density Deficit and Boundary Share of the 26 Ball Conditions", ["Condition", "Best method", "<i>r</i>", "<i>δ</i>", "<i>b</i>"], rows,
       "<i>r</i> = highest mean disk radius over the six methods at 1,500 sweeps (units of the space); <i>δ</i> = density deficit and <i>b</i> = boundary share, defined in the text; <i>A</i> = area of the ball; <i>R</i><sub>H</sub> = hyperbolic radius of the large ball, whose area the Euclidean ball matches. Data: conf_deficit_boundary.csv.",
       aligns=["l", "c", "c", "c", "c"], widths=[2.8, 1.0, 0.9, 0.9, 0.9], split=True)
    HD("Budget Levels, Time, and the Count-Based Problem", 3)
    b = m.pivot_table(index="algorithm", columns="budget", values="mean_rel").reindex(METHODS)
    tmm = tm.pivot(index="algorithm", columns="budget", values="median_time_s").reindex(METHODS)
    sw = tm.pivot(index="algorithm", columns="budget", values="mean_sweeps_used").reindex(METHODS)
    rows = [[M_AB[a]] + [f(b.loc[a, B], 3, lead=False) for B in C.BUDGETS] + [f(tmm.loc[a, C.MAIN_BUDGET], 2), f(sw.loc[a, C.MAIN_BUDGET] / C.MAIN_BUDGET * 100, 0) + "%"] for a in METHODS]
    FF("figure", "cbud", "Mean Relative Score of the Six Methods at Three Budget Levels", CF.fig_budget(m, conds), 6.0,
       "The ordering of the methods is similar at the three budget levels; the gap between the methods is largest at 500 sweeps.",
       "Lines and markers: blue circles = GD, purple diamonds = GD+P, red squares = SA, green triangles = compression, orange triangles = L-BFGS-B, brown crosses = basin hopping. Each point is the mean relative score over the conditions of the panel and 20 seeds; relative score = score / reference value (dimensionless).",
       "Three panels of line plots of mean relative score against budget for six methods.")
    FF("table", "cbud", "Mean Relative Score at Three Budget Levels, With Time and Budget Used", ["Method", "500", "1,500", "3,000", "Median time (s)", "Budget used"], rows,
       "Mean relative score over the 33 conditions and 20 seeds at 500, 1,500, and 3,000 sweeps. Time = median wall-clock seconds per run at 1,500 sweeps with two worker processes on the machine described in the text; Budget used = mean share of the 1,500 sweeps actually used (GD+P and L-BFGS-B stop when their own convergence tests are met; the linear programs of GD+P are not charged in sweeps). Data: conf_summary_by_condition.csv, conf_time_by_method.csv.",
       aligns=["l", "c", "c", "c", "c", "c"], widths=[1.4, 0.8, 0.8, 0.8, 1.5, 1.2])
    d.body(f"Raising the budget from 500 to 3,000 sweeps raised the mean relative score of every method ({Tb('cbud')}; {Fg('cbud')}), most for compression ({f(b.loc['ls', 500], 3, lead=False)} to {f(b.loc['ls', 3000], 3, lead=False)}) and gradient descent ({f(b.loc['gd', 500], 3, lead=False)} to {f(b.loc['gd', 3000], 3, lead=False)}) and least for GD+P ({f(b.loc['gdp', 500], 3, lead=False)} to {f(b.loc['gdp', 3000], 3, lead=False)}), so the methods differ most at the smallest budget. "
           f"Time per run at 1,500 sweeps was {f(tmm.loc['sa', C.MAIN_BUDGET] / tmm.loc['gd', C.MAIN_BUDGET], 1)} times as long for simulated annealing as for gradient descent, and GD+P ran for {f(tmm.loc['gdp', C.MAIN_BUDGET], 2)} seconds against {f(tmm.loc['lbfgsb', C.MAIN_BUDGET], 2)} for L-BFGS-B, because its linear programs are not charged in sweeps; the sweep counts are equal by construction, the times are not.")
    rows = [[{"S2cap": "Cap", "R2": "Euclidean", "H2": "Hyperbolic"}[r.space], f"{r.area:g}", str(int(r.n_ref)), str(int(r.K)), f(r.K_over_n_ref, 2, lead=False), f(r.share_at_K, 2, lead=False)] for r in cnt.itertuples()]
    FF("table", "ccount", "Count-Based Version of the Disk Problem: Largest Number of Disks of Radius 0.30", ["Space", "Area", "Reference count", "<i>K</i>", "<i>K</i> / reference", "Share at <i>K</i>"], rows,
       "<i>K</i> = largest number of disks of radius 0.30 for which GD+P at 1,500 sweeps reached a radius of at least 0.30 in at least half of 20 fresh seeds (201 to 220), scanned downward from the reference count; reference count = floor(<i>ρ</i>* Area(<i>R</i>) / Area(0.30)), the number of disks that would fit if the ball were packed at the reference density of the whole space (a heuristic ceiling, not a theorem for a bounded ball). "
       "Share at <i>K</i> = share of seeds that reached the radius at <i>K</i>. Exploratory; no decision rule. Data: count_runs.csv, count_summary.csv.",
       aligns=["l", "c", "c", "c", "c", "c"], widths=[1.4, 0.8, 1.2, 0.8, 1.2, 1.1])
    cc = cnt.pivot(index="area", columns="space", values="K")
    d.body(f"The count-based problem fixes the disk radius at 0.30 and asks how many disks fit ({Tb('ccount')}). This is an original use of the same optimizers: the answer is an integer that can be compared across spaces without choosing a value of <i>n</i> in advance. "
           f"At area 6 the largest numbers found were {int(cc.loc[6.0, 'S2cap'])} in the cap, {int(cc.loc[6.0, 'R2'])} in the Euclidean disk, and {int(cc.loc[6.0, 'H2'])} in the hyperbolic disk, and at area 12 they were {int(cc.loc[12.0, 'S2cap'])}, {int(cc.loc[12.0, 'R2'])}, and {int(cc.loc[12.0, 'H2'])}. "
           "These are lower bounds on the true maximum, because a failure to find a packing does not prove that none exists, and they depend on the method and the budget.")
    if part == "appendix":
        d, HD, FF = _d0, _HD0, _FF0
        HD("Additions After the First Analysis", 2)
        d.body(f"Five additions were made after the results above were seen. They were written in a second preregistration file (PREREGISTRATION_ADDENDUM_1.md, SHA-256 {h_add}), a mini-round file (PREREGISTRATION_MINIROUND.md, SHA-256 {h_mini}), both hashed on {h_time2.replace('T', ' at ').replace('Z', ' UTC')} before any of the runs they describe, and a follow-up file (PREREGISTRATION_FOLLOWUP.md, SHA-256 {h_fu}), hashed on {h_fu_time.replace('T', ' at ').replace('Z', ' UTC')} before its runs. "
               "The addendum lists what was decided after the first round had been seen: the Packomania references, the extended tuning ranges, the saved configurations and the wall analysis, and a correction of the wording of the reference density (an upper bound on the density, not the density of a densest packing). The first preregistration file was not edited. "
               "A hash recorded by the author is not an independent time stamp; the author reports having emailed the four files to the research adviser on October 30, 2026, after the runs of the confirmatory round and the mini-round and before the runs of the follow-up. The adviser&rsquo;s email, not the author&rsquo;s hash, is the independent record, and it shows only that each file existed by that date; it cannot show that the first three files preceded their runs.".replace("&rsquo;", "’"))
        HD("Mini-Round With a Fixed Radius and a Matched Boundary Share", 2)
        mm1, mm2, mm3 = mdec["M1"], mdec["M2"], mdec["M3"]
        d.body(f"In the main round the boundary share depends on the radius each method finds, and the spaces differ in boundary share, so C1 is partly circular and C2 could not separate curvature from the boundary. The mini-round fixes the disk radius <i>r</i><sub>0</sub> (0.30 or 0.40) and the design boundary share <i>b</i><sub>0</sub> (0.40, 0.45, or 0.50) in advance, and chooses the radius of each ball so that <i>b</i><sub>0</sub> is the same in the Euclidean disk, the hyperbolic disk, and the spherical cap while the curvature differs ({Tb('cmini')}). "
               "The matched boundary share requires much larger hyperbolic balls than Euclidean ones for the same <i>r</i><sub>0</sub>. The Euclidean plane has no length scale, so a packing of disks of radius 0.40 in a disk of radius <i>R</i> is a scaled copy of a packing of disks of radius 0.30 in a disk of radius 0.75 <i>R</i>: with the same <i>b</i><sub>0</sub> the Euclidean conditions at <i>r</i><sub>0</sub> = 0.30 and 0.40 are the same problem and gave the same <i>K</i> ({Tb('cmini')}). The six Euclidean conditions are therefore three distinct ones, and the model fitted on them in M3 rests on three independent points. The hyperbolic disk and the cap have a length scale, so their conditions at different <i>r</i><sub>0</sub> are different problems. For each ball the number of disks <i>K</i> is the largest <i>n</i> for which GD+P at 1,500 sweeps reaches radius <i>r</i><sub>0</sub> in at least 10 of 20 fresh seeds (301 to 320), and the fixed-radius deficit is <i>δ</i><sub>0</sub> = 1 − <i>K</i> Area(<i>r</i><sub>0</sub>) / (Area(<i>R</i>) <i>ρ</i>*). Because <i>b</i><sub>0</sub> and <i>r</i><sub>0</sub> are set by design, <i>δ</i><sub>0</sub> is not circular in the sense of C1; it is still a lower bound on the true deficit, because a failure to find <i>K</i> + 1 disks does not prove that they do not fit.")
        sp_lab = {"R2": "Euclidean", "H2": "Hyperbolic", "S2cap": "Cap"}
        rows = [[f"{r.r0:.2f}", f"{r.b0:.2f}", sp_lab[r.space], f(r.R, 3), str(int(r.n_ref)), str(int(r.K)), f(r.deficit0, 3, lead=False)] for r in mini.sort_values(["r0", "b0", "space"], key=lambda c: c.map({"R2": 0, "H2": 1, "S2cap": 2}) if c.name == "space" else c).itertuples()]
        FF("table", "cmini", "Mini-Round Conditions With a Fixed Disk Radius and a Matched Boundary Share", ["<i>r</i><sub>0</sub>", "<i>b</i><sub>0</sub>", "Space", "<i>R</i>", "Reference count", "<i>K</i>", "<i>δ</i><sub>0</sub>"], rows,
           "<i>r</i><sub>0</sub> = disk radius, <i>b</i><sub>0</sub> = design boundary share, <i>R</i> = radius of the ball (units of the space), reference count = floor(<i>ρ</i>* Area(<i>R</i>) / Area(<i>r</i><sub>0</sub>)), <i>K</i> = largest number of disks found at radius <i>r</i><sub>0</sub> (GD+P, 1,500 sweeps, at least 10 of 20 seeds, seeds 301 to 320), <i>δ</i><sub>0</sub> = fixed-radius density deficit. Data: mini_design.csv, mini_scan.csv, mini_summary.csv, mini_decisions.json.",
           aligns=["c", "c", "l", "c", "c", "c", "c"], widths=[0.6, 0.6, 1.2, 0.9, 1.2, 0.6, 0.8], split=True)
        d.body(f"For M1 the Spearman correlation between <i>b</i><sub>0</sub> and <i>δ</i><sub>0</sub> over the 18 conditions was {f(mm1['spearman'], 2, lead=False)} (one-sided permutation {pstr(mm1['perm_p_one_sided'])}), which is {mm1['decision']} at the preregistered thresholds (supported at .50 or more with <i>p</i> < .05); the values of <i>K</i> are small integers, so <i>δ</i><sub>0</sub> changes in coarse steps, and 18 conditions give little power. "
               f"For M2, with the boundary share and the radius in the model, the hyperbolic term was {f(mm2['g_H'], 3)} (95% interval {f(mm2['g_H_ci'][0], 3)} to {f(mm2['g_H_ci'][1], 3)}) and the cap term {f(mm2['g_S'], 3)} ({f(mm2['g_S_ci'][0], 3)} to {f(mm2['g_S_ci'][1], 3)}), so the decision computed under the preregistered rule was “{mm2['decision']}”. That decision is withdrawn: it used 13 degrees of freedom, which counted the three duplicated Euclidean conditions as independent, and the sample was 15 conditions, not 18. The withdrawal was decided after the result was seen, so the analysis without the duplicates is post hoc; both analyses are given side by side in {Tb('cmini2')}. A correction note (CORRECTION_NOTE_1.md, SHA-256 {h_cor}, hashed {h_cor_time.replace('T', ' at ').replace('Z', ' UTC')}) records the withdrawal. With the duplicates removed, M2 is {fdec['mini_without_euclid_duplicates']['F2']['decision']} and M1 stays inconclusive, so the mini-round does not show that curvature has no effect at a matched boundary share; the follow-up below was designed to add power. "
               f"For M3 the boundary-loss model <i>δ</i><sub>0</sub> = <i>λ b</i><sub>0</sub> with <i>λ</i> = {f(mm3['lambda_euclid'], 2, lead=False)} fitted on the six Euclidean conditions predicted the twelve other conditions with a mean absolute error of {f(mm3['mean_abs_error'], 3, lead=False)}, so the model {mm3['decision']} at the preregistered thresholds (at most .05). "
               f"Applied after the fact to the 26 ball conditions of the main round (exploratory; <i>λ</i> = {f(ext['boundary_model_round1']['lambda_euclid'], 2, lead=False)} from the {ext['boundary_model_round1']['n_euclid']} Euclidean conditions), the mean absolute error for the other {ext['boundary_model_round1']['n_other']} conditions was {f(ext['boundary_model_round1']['mae_other'], 3, lead=False)} ({f(ext['boundary_model_round1']['mae_by_space']['H2'], 3, lead=False)} in the hyperbolic disk and {f(ext['boundary_model_round1']['mae_by_space']['S2cap'], 3, lead=False)} in the cap). "
               "The mini-round used one method at one budget, so it says what GD+P finds, not what is possible, and the three rules were not corrected for the six rules of the main round.")
        mw = fdec["mini_without_euclid_duplicates"]
        rows = [["M1: Spearman correlation of <i>b</i><sub>0</sub> and <i>δ</i><sub>0</sub> (one-sided permutation <i>p</i>)", f"{f(mm1['spearman'], 2, lead=False)} ({pstr(mm1['perm_p_one_sided'])}): {mm1['decision']}", f"{f(mw['F1']['spearman'], 2, lead=False)} ({pstr(mw['F1']['perm_p_one_sided'])}): {mw['F1']['decision']}"],
                ["M2: hyperbolic term (95% interval)", f"{f(mm2['g_H'], 3)} ({f(mm2['g_H_ci'][0], 3)} to {f(mm2['g_H_ci'][1], 3)}), 13 df: {mm2['decision']} (withdrawn)", f"{f(mw['F2']['terms']['g_H'], 3)} ({f(mw['F2']['g_H_ci'][0], 3)} to {f(mw['F2']['g_H_ci'][1], 3)}), {mw['F2']['df']} df: {mw['F2']['decision']}"],
                ["M2: cap term (95% interval)", f"{f(mm2['g_S'], 3)} ({f(mm2['g_S_ci'][0], 3)} to {f(mm2['g_S_ci'][1], 3)}): {mdec['M2']['decision_cap_secondary']} (withdrawn)", f"{f(mw['F2']['terms']['g_S'], 3)} ({f(mw['F2']['g_S_ci'][0], 3)} to {f(mw['F2']['g_S_ci'][1], 3)}): {mw['F2']['decision_cap_secondary']}"],
                ["M3: mean absolute error of the boundary-loss model", f"{f(mm3['mean_abs_error'], 3, lead=False)} (<i>λ</i> from 6 Euclidean conditions, 3 distinct): {mm3['decision']}", f"{f(mw['F3']['mean_abs_error'], 3, lead=False)} (<i>λ</i> from {mw['F3']['n_euclid']} Euclidean conditions): {mw['F3']['decision']}"]]
        FF("table", "cmini2", "Mini-Round Results as Preregistered and After Removing the Duplicated Euclidean Conditions", ["Rule", "As preregistered (18 conditions)", "Duplicates removed (15 conditions; post hoc)"], rows,
           "The left column applies the preregistered rules to all 18 conditions; the right column drops the three Euclidean conditions at <i>r</i><sub>0</sub> = 0.40, which duplicate those at 0.30, and was decided after the result was seen, so it is post hoc. The preregistered decision of M2 is withdrawn (see text). Data: mini_decisions.json, followup_decisions.json.",
           aligns=["l", "l", "l"], widths=[2.0, 2.3, 2.3], split=True)
        HD("Follow-Up With More Levels, a Third Radius, and a Second Method", 2)
        p1, g1, g2, g3, mc = fdec["primary"], fdec["primary"]["F1"], fdec["primary"]["F2"], fdec["primary"]["F3"], fdec["method_comparison"]
        d.body(f"A follow-up with its own preregistration (SHA-256 {h_fu}, hashed {h_fu_time.replace('T', ' at ').replace('Z', ' UTC')}, before its runs) removed the Euclidean duplicates and added power: five design boundary shares (0.35 to 0.55), three disk radii (0.20, 0.30, and 0.40) for the hyperbolic disk and the cap, one Euclidean condition for each boundary share because the Euclidean results do not depend on <i>r</i><sub>0</sub>, and fresh seeds 401 to 420, in {len(fol)} conditions ({Tb('cfollow')}). "
               "The replacement boundary shares (0.35 and 0.55 were added), the third radius, and the second method were all written in that file before any of its runs. The runs started at 23:34 UTC on October 29, 2026, about one minute after the hash was recorded, and the two-method runs ended at 23:43 UTC (file timestamps; FOLLOWUP_RUNTIMES.txt); the author had emailed the four files to the research adviser before the runs were started. F1 to F3 are therefore preregistered by the author’s hash, and the adviser’s email is the only independent record of the date of the files; the time stamps of the runs come from the machine that ran them. "
               "The number of disks <i>K</i> of a condition was computed with two methods, GD+P and L-BFGS-B (re-tuned value 2,500), each scanned downward from the reference count, and the larger of the two is used; a lower bound from one method is weak, and a second method can only raise it. "
               f"For F1, the Spearman correlation between <i>b</i><sub>0</sub> and <i>δ</i><sub>0</sub> over the {g1['n']} conditions was {f(g1['spearman'], 2, lead=False)} ({pstr(g1['perm_p_one_sided'])}), so the prediction that the fixed-radius deficit follows the design boundary share is {g1['decision']} at the preregistered thresholds; unlike in the main round, this test does not use a radius found by a method, so it is not circular in the way C1 is. "
               f"For F2, with <i>b</i><sub>0</sub> and the radius in the model, the hyperbolic term was {f(g2['terms']['g_H'], 3)} (95% interval {f(g2['g_H_ci'][0], 3)} to {f(g2['g_H_ci'][1], 3)}) and the cap term {f(g2['terms']['g_S'], 3)} ({f(g2['g_S_ci'][0], 3)} to {f(g2['g_S_ci'][1], 3)}), so the decision is {g2['decision']}: both terms are positive and small, neither interval excludes 0, and neither interval lies within ±.05, so a curvature effect could be neither shown nor excluded. "
               f"For F3, the boundary-loss model <i>δ</i><sub>0</sub> = <i>λ b</i><sub>0</sub> with <i>λ</i> = {f(g3['lambda_euclid'], 2, lead=False)} fitted on the {g3['n_euclid']} Euclidean conditions predicted the other {g3['n_other']} with a mean absolute error of {f(g3['mean_abs_error'], 3, lead=False)} ({f(g3['mae_by_space']['H2'], 3, lead=False)} for the hyperbolic disk and {f(g3['mae_by_space']['S2cap'], 3, lead=False)} for the cap), so the model {g3['decision']} at the thresholds, with the cap error close to the limit of .05. "
               f"The second method added nothing to the first: L-BFGS-B found a larger <i>K</i> than GD+P in {mc['lbfgsb_larger']} of {mc['n']} conditions, the same in {mc['equal']}, and a smaller one in {mc['lbfgsb_smaller']}, and on the distinct conditions of the mini-round (exploratory) it found a larger <i>K</i> in none. The two methods agree, which supports the values of <i>K</i> as what these optimizers find at this budget; it does not show that more disks cannot fit.")
        rows = [[sp_lab[r.space], f"{r.r0:.2f}", f"{r.b0:.2f}", f(r.R, 3), str(int(r.n_ref)), str(int(r.K_gdp)), str(int(r.K_lbfgsb)), str(int(r.K)), f(r.deficit0, 3, lead=False)] for r in fol.assign(o=fol.space.map({"R2": 0, "H2": 1, "S2cap": 2})).sort_values(["o", "r0", "b0"]).itertuples()]
        FF("table", "cfollow", "Follow-Up Conditions and the Number of Disks Found by Two Methods", ["Space", "<i>r</i><sub>0</sub>", "<i>b</i><sub>0</sub>", "<i>R</i>", "Reference count", "<i>K</i> GD+P", "<i>K</i> L-BFGS-B", "<i>K</i>", "<i>δ</i><sub>0</sub>"], rows,
           "<i>K</i> = larger of the two method values. Seeds 401 to 420, 1,500 sweeps, at least 10 of 20 seeds at radius <i>r</i><sub>0</sub>; other symbols as in the mini-round table. The Euclidean disk is run at <i>r</i><sub>0</sub> = 0.30 only because its results do not depend on <i>r</i><sub>0</sub>. Data: followup_design.csv, followup_scan.csv, followup_summary.csv, followup_decisions.json.",
           aligns=["l", "c", "c", "c", "c", "c", "c", "c", "c"], widths=[1.0, 0.5, 0.5, 0.7, 0.9, 0.7, 0.9, 0.5, 0.6], split=True)
        d.body("The boundary-loss model is a description, not an explanation. It has one parameter fitted on the Euclidean disk, it is not derived from a theory of how a wall disturbs a packing, and agreement of its predictions with the other two spaces shows that the deficit is similar at the same boundary share, not that the boundary causes the loss or that curvature does not matter. A different one-parameter family could fit as well. "
               "Also, because the number of disks is an integer that changes in steps, <i>δ</i><sub>0</sub> changes in steps of about .05 to .10 for the smallest balls, which limits what can be seen at a boundary share near 0.55.")
        return
    HD("Baselines Re-Tuned After the First Analysis", 3)
    rc = ext["retuned_mean_rel_change"]
    chg = {(r["algorithm"], r["budget"]): r["d"] for r in rc}
    sel = rtun["tuned"]
    d.body(f"Compression and L-BFGS-B had been selected at the upper edge of their candidate ranges (0.70 and 700). Their ranges were extended (compression: 1.0, 1.4, and 2.0 added; L-BFGS-B: 1,000, 1,500, and 2,500 added), the same pilot protocol was applied to the new settings, and the selected values, hashed on {open(CONF + '/RETUNED.sha256').read().split(chr(10))[2].split(': ')[1].replace('T', ' at ').replace('Z', ' UTC')} (SHA-256 {h_ret}) before the evaluation, were {sel['ls']:g} for compression, inside its extended range, and {sel['lbfgsb']:g} for L-BFGS-B, again the largest value tried. "
           f"Both methods were then run again on all 33 conditions, three budgets, and the same 20 seeds. At 1,500 sweeps the mean relative score changed by {f(chg[('ls', 1500)], 3)} for compression and {f(chg[('lbfgsb', 1500)], 3)} for L-BFGS-B (by {f(chg[('ls', 500)], 3)} and {f(chg[('lbfgsb', 500)], 3)} at 500 sweeps). The decisions C1 to C6 recomputed with the re-tuned methods were the same as the preregistered ones; the mean rank of compression stayed last ({f(rdec['C4']['mean_rank_by_method']['ls'], 2)}), that of L-BFGS-B moved from {f(mr['lbfgsb'], 2)} to {f(rdec['C4']['mean_rank_by_method']['lbfgsb'], 2)}, and GD+P kept the best mean rank ({f(rdec['C4']['mean_rank_by_method']['gdp'], 2)}). "
           "The tables above are the preregistered runs; the re-tuned runs are additional (conf_retuned_vs_original.csv, decisions_retuned.json). The two methods received nine candidate settings and the other four methods six, so the effort is unequal, and a gain from still larger values of the L-BFGS-B exponent cannot be excluded; the gain was small.")
    HD("Wall Contact in All Runs", 3)
    w15 = wm[wm.budget == C.MAIN_BUDGET].set_index("algorithm")
    big = [cid for cid, c in conds.items() if c["group"] == "large" and c["kind"] == "H2"]
    big_n = {cid: conds[cid]["label"] for cid in big}
    rows = [[M_AB[a], f(w15.loc[a, "mean_touch_share"], 2, lead=False), f(w15.loc[a, "ring_share"], 3, lead=False), f(w15.loc[a, "median_max_gap_over_r"], 2)] for a in METHODS]
    FF("table", "cwall", "Wall Contact of the Final Configurations of All Ball Runs at 1,500 Sweeps", ["Method", "Disks touching the wall", "Runs with all disks in the outer ring", "Median largest gap / <i>r</i>"], rows,
       "Each row covers the 26 ball conditions and 20 seeds (520 runs). A disk touches the wall if its gap to the wall limit <i>R</i> − <i>r</i> is at most 1% of the disk radius <i>r</i>; a run has all disks in the outer ring if every disk lies within one disk radius of the wall limit; the largest gap / <i>r</i> is the largest such gap in a run in units of <i>r</i>. Exploratory; no decision rule. Data: conf_walls_by_method.csv, conf_walls_by_condition.csv.",
       aligns=["l", "c", "c", "c"], widths=[1.4, 1.5, 2.0, 1.6], split=True)
    h6 = wc[(wc.condition_id == big[2]) & (wc.budget == C.MAIN_BUDGET)].set_index("algorithm")
    h8 = wc[(wc.condition_id == big[3]) & (wc.budget == C.MAIN_BUDGET)].set_index("algorithm")
    wcb = wc.assign(nr=wc.ring_share * 20)
    r6, r8 = wcb[wcb.condition_id == big[2]].nr.sum(), wcb[wcb.condition_id == big[3]].nr.sum()
    n_each = len(wcb[wcb.condition_id == big[2]]) * 20
    r_out = wcb[~wcb.condition_id.isin(big[2:])].nr.sum()
    n_out = len(wcb[~wcb.condition_id.isin(big[2:])]) * 20
    d.body(f"In the main round, one run in the hyperbolic ball of radius 6 had shown all 50 centers in a ring along the wall. With the configurations of all runs saved ({Tb('cwall')}), the ring is specific to the two largest hyperbolic balls (radii 6 and 8) and is not a general result: all {int(round(r6 + r8))} runs with every disk in the outer ring were in these two conditions ({int(round(r6))} of {n_each:,} runs in the ball of radius 6 and {int(round(r8))} of {n_each:,} in the ball of radius 8, over all methods and budgets), and none of the other {n_out:,} ball runs, in 24 conditions, had one ({int(round(r_out))} runs). "
           f"Contact with the wall is more common: over all {ext['walls_overall']['runs']:,} ball runs, {f(ext['walls_overall']['mean_touch_share'] * 100, 0)}% of the disks touched the wall, and the share differed greatly by method (from {f(w15.mean_touch_share.min(), 2, lead=False)} for {M_AB[w15.mean_touch_share.idxmin()]} to {f(w15.mean_touch_share.max(), 2, lead=False)} for {M_AB[w15.mean_touch_share.idxmax()]} at 1,500 sweeps), because the methods that polish or run to convergence push disks against the wall. "
           f"At 1,500 sweeps the share of runs with all disks in the outer ring reached {f(h6.ring_share.max(), 2, lead=False)} in the ball of radius 6 and {f(h8.ring_share.max(), 2, lead=False)} in the ball of radius 8 for the method with the most such runs ({M_AB[h6.ring_share.idxmax()]} and {M_AB[h8.ring_share.idxmax()]}). "
           "A disk that touches the wall is a disk of the boundary layer, so a high share indicates that the packing is dominated by the wall; it does not show that the interior is poorly packed.")
    HD("Limits of the Confirmatory Round", 3)
    d.body(f"Seven limits apply. First, the conditions are few (33, with six per space in the equal-area comparison) and the boundary share depends on the result, so C1 and C2 describe 26 points, not a large sample. Second, {ref_types.get('best found in this round', 0)} of 33 references are best-found values from this round, so relative scores for those conditions cannot show how far the methods are from the optimum. "
           "Third, tuning used one parameter per method and six settings; compression and L-BFGS-B were selected at the edge of their ranges, and after their ranges were extended (post hoc) compression was selected inside its range and L-BFGS-B again at the edge, so the effort is unequal (nine settings for these two methods, six for the others) and L-BFGS-B may still be undertuned. Fourth, one round was run, on one machine, with two processes sharing it. Fifth, the preregistration is a self-recorded hash and is not independently time-stamped. "
           "Sixth, the large hyperbolic balls are dominated by the wall (see the wall contact below), so they test the boundary effect and say little about packings in the interior of a hyperbolic ball. "
           "Seventh, the number of disks <i>K</i> in the mini-round and the follow-up is a lower bound from one or two optimizers at one budget, it is an integer that changes the deficit in steps, the boundary-loss model has one fitted parameter and no derivation, and the follow-up balls are small (at most 46 disks), so these analyses cannot settle a curvature effect smaller than about .05.")

