"""r3_section.py -- the 'Final Round' section of the paper.  Every number is read from the round3_* and r3* files."""
import json
import pandas as pd
import confirm_design as C
import conf_figures as CF


def build_section(d, FF, HD, Tb, Fg, f, pstr, DATA, CONF):
    dec = json.load(open(CONF + "/round3_decisions.json"))
    a1, a2, b1 = dec["A1"], dec["A2"], dec["B1"]
    best = pd.read_csv(CONF + "/r3a_conditions.csv")
    sb = pd.read_csv(CONF + "/r3b_summary.csv")
    r3 = open(CONF + "/ROUND3.sha256").read().split("\n")
    h_r3, t_r3 = r3[0].split()[0], r3[1].split(": ")[1]
    t0 = open(CONF + "/ROUND3_START.txt").read().strip()
    t1 = open(CONF + "/ROUND3_END.txt").read().strip()
    pl = open(CONF + "/PLAN_FILES.sha256").read().split("\n")
    u = lambda t: t.replace("T", " ")[:16] + " UTC"
    sp_lab = {"R2": "Euclidean", "H2": "Hyperbolic", "S2cap": "Cap"}

    HD("Final Round: An Equal-Area Test of Curvature and a Rule for the Number of Disks", 2)
    d.body(f"Three earlier tests of curvature, the confirmatory round, the mini-round, and the follow-up (Appendix B), were inconclusive. The final round was designed to answer that one question with many more equal-area conditions, and to test one original rule for the number of disks. "
           f"Its hypotheses, decision rules, seeds, and analysis code were written in PREREGISTRATION_ROUND3.md (SHA-256 {h_r3}, recorded by the author on {u(t_r3)}), and the file, the Research Plan, and the earlier preregistration files were emailed to the research adviser before any run was started; the author reports this, and the adviser&rsquo;s email is the independent record of the date. "
           f"The runs began at {u(t0)} and ended at {u(t1)} (ROUND3_START.txt and ROUND3_END.txt). The Research Plan, finished before this paper, states the rules, and the analysis below follows them.".replace("&rsquo;", "’"))
    HD("Design and Preregistered Rules", 3)
    d.body(f"Part A used three spaces, eight ball areas (2, 3, 4, 5, 6, 8, 10, and 12), and six numbers of disks (8, 12, 16, 20, 24, and 32), {a1['n_conditions'] + a1['n_excluded']} conditions in {a1['n_cells']} cells of equal area and equal <i>n</i>, with polished gradient descent and L-BFGS-B at 1,500 sweeps and fresh seeds 501 to 520 ({dec['A_methods']['n_runs']:,} runs). "
           "For each condition the radius is the larger of the two methods&rsquo; mean radii, the density deficit <i>δ</i> and the boundary share <i>b</i> are computed from it, and rule A1 fits <i>δ</i> = <i>a</i> + <i>β b</i> + <i>g</i><sub>H</sub> [hyperbolic] + <i>g</i><sub>S</sub> [cap]. The interval of each term comes from resampling the cells, not the conditions, because the three balls of a cell are paired. "
           "A curvature effect is detectable if the interval of <i>g</i><sub>H</sub> excludes 0 and <i>g</i><sub>H</sub> is at least .02, and absent if the interval lies within ±.02. "
           "Part B used the rule <i>K</i><sub>pred</sub> = floor(<i>n</i><sub>ref</sub>(1 − 0.46 <i>b</i><sub>0</sub>) + 0.5), where <i>n</i><sub>ref</sub> is the number of disks of radius <i>r</i><sub>0</sub> that would fit in the ball at the upper bound on the density, <i>b</i><sub>0</sub> is the boundary share at <i>r</i><sub>0</sub>, and 0.46 is the loss coefficient fitted in the follow-up and not refitted, for 20 new conditions and seeds 601 to 620.".replace("&rsquo;", "’"))
    HD("Result for Curvature", 3)
    rows = [["Hyperbolic term, <i>g</i><sub>H</sub> (A1)", f(a1["g_H"], 3), f"{f(a1['g_H_ci'][0], 3)} to {f(a1['g_H_ci'][1], 3)}", a1["decision"].capitalize()],
            ["Cap term, <i>g</i><sub>S</sub> (A1, secondary)", f(a1["g_S"], 3), f"{f(a1['g_S_ci'][0], 3)} to {f(a1['g_S_ci'][1], 3)}", a1["decision_cap_secondary"].capitalize()],
            ["Boundary-share slope, <i>β</i>", f(a1["beta_b"], 3), "not part of the rule", "—"],
            ["Hyperbolic − Euclidean at equal area and <i>n</i> (A2)", f(a2["hyperbolic_minus_euclid"]["mean"], 3), f"{f(a2['hyperbolic_minus_euclid']['ci95'][0], 3)} to {f(a2['hyperbolic_minus_euclid']['ci95'][1], 3)}", "Descriptive"],
            ["Cap − Euclidean at equal area and <i>n</i> (A2)", f(a2["cap_minus_euclid"]["mean"], 3), f"{f(a2['cap_minus_euclid']['ci95'][0], 3)} to {f(a2['cap_minus_euclid']['ci95'][1], 3)}", "Descriptive"]]
    FF("table", "r3a", "Curvature Terms in the Final Round at Equal Area", ["Quantity", "Estimate", "95% interval", "Decision"], rows,
       f"{a1['n_conditions']} conditions in {a1['n_cells']} cells; intervals are percentile intervals of 10,000 resamples of the cells (seed 20261030). <i>δ</i> = density deficit; <i>b</i> = boundary share; the decision rule is in the text. Data: r3a_runs.csv, r3a_conditions.csv, round3_decisions.json.",
       aligns=["l", "c", "c", "l"], widths=[2.6, 0.9, 1.6, 1.4])
    FF("figure", "r3def", "Density Deficit Against Boundary Share in the Final Round", CF.fig_r3(best, dec), 4.4,
       f"Each point is one of the {a1['n_conditions']} equal-area conditions, using the larger mean radius of the two methods at 1,500 sweeps. The three fitted lines have a common slope and differ only in their intercepts.",
       "Symbols and lines: circles and orange line = Euclidean disk, squares and purple line = hyperbolic disk, triangles and blue line = spherical cap. <i>δ</i> = 1 − density / upper bound on the density for disks of the radius found; <i>b</i> = share of the ball&rsquo;s area within one disk radius of its wall (both dimensionless).".replace("&rsquo;", "’"),
       "Scatter plot of density deficit against boundary share for 144 packing conditions with three fitted lines.")
    verdict = {"curvature adds a detectable deficit": "curvature adds a detectable deficit: the hyperbolic disk has a larger density deficit than the Euclidean disk at the same boundary share, by the amount of the hyperbolic term",
               "no detectable curvature effect": "there is no detectable curvature effect: the whole interval lies within ±.02, so any difference between the spaces at the same boundary share is smaller than .02 of the upper bound",
               "inconclusive": "the result is again inconclusive"}[a1["decision"]]
    d.body(f"The preregistered answer is that {verdict}. The hyperbolic term was {f(a1['g_H'], 3)} (95% interval {f(a1['g_H_ci'][0], 3)} to {f(a1['g_H_ci'][1], 3)}) and the cap term {f(a1['g_S'], 3)} ({f(a1['g_S_ci'][0], 3)} to {f(a1['g_S_ci'][1], 3)}; {a1['decision_cap_secondary']}), with {a1['n_conditions']} conditions and a residual standard deviation of {f(a1['residual_sd'], 3, lead=False)}; the plan expected a half-width of about .03 for a residual of .058, and the half-width found for the hyperbolic term was {f((a1['g_H_ci'][1] - a1['g_H_ci'][0]) / 2, 3, lead=False)} ({Tb('r3a')}; {Fg('r3def')}). "
           f"The decision means that no effect as large as .02 was found, not that the effect is zero: both intervals exclude 0, the hyperbolic term is positive and the cap term negative, and both are about 1% of the bound, so small effects of opposite sign remain possible and are not explained here. The slope on the boundary share was {f(a1['beta_b'], 2)}: in all three spaces the deficit rose with the boundary share. At equal area and equal number of disks the hyperbolic disk differed from the Euclidean disk by {f(a2['hyperbolic_minus_euclid']['mean'], 3)} and the cap by {f(a2['cap_minus_euclid']['mean'], 3)} in <i>δ</i>, which include the effect of the different boundary share and are descriptive. "
           "For each condition the larger mean radius of polished gradient descent and L-BFGS-B was used, so the conclusion concerns what these two optimizers find at 1,500 sweeps, not every possible packing.")
    HD("Result for the Rule for the Number of Disks", 3)
    rows = [[sp_lab[r.space], f"{r.r0:.2f}", f"{r.b0:.3f}", str(int(r.n_ref)), str(int(r.K)), str(int(r.K_pred)), f"{int(r.K - r.K_pred):+d}" if r.K != r.K_pred else "0"] for r in sb.assign(o=sb.space.map({"R2": 0, "H2": 1, "S2cap": 2})).sort_values(["o", "r0", "b0"]).itertuples()]
    FF("table", "r3b", "Predicted and Found Number of Disks in the Final Round", ["Space", "<i>r</i><sub>0</sub>", "<i>b</i><sub>0</sub>", "Reference count", "<i>K</i> found", "<i>K</i> predicted", "Error"], rows,
       "<i>K</i> found = largest number of disks of radius <i>r</i><sub>0</sub> reached by polished gradient descent in at least 10 of 20 fresh seeds (601 to 620); <i>K</i> predicted = floor(<i>n</i><sub>ref</sub>(1 − 0.46 <i>b</i><sub>0</sub>) + 0.5); error = found − predicted. Data: r3b_design.csv, r3b_scan.csv, r3b_summary.csv.",
       aligns=["l", "c", "c", "c", "c", "c", "c"], widths=[1.2, 0.6, 0.7, 1.2, 0.9, 1.0, 0.7], split=True)
    bias = b1["mean_signed_error_by_space"]
    d.body(f"The rule predicted the number of disks within one disk in {f(b1['share_within_1'] * 100, 0)}% of the {b1['n_conditions']} new conditions and exactly in {f(b1['share_exact'] * 100, 0)}% ({Tb('r3b')}); the mean absolute error was {f(b1['mean_abs_error_disks'], 2)} disks, the mean relative error {f(b1['mean_rel_error'], 3, lead=False)}, and the mean signed errors were {f(bias['R2'], 2)} for the Euclidean disk, {f(bias['H2'], 2)} for the hyperbolic disk, and {f(bias['S2cap'], 2)} for the cap. "
           f"The preregistered decision is that the rule is {b1['decision']}. The rule is a description of what these optimizers find at this budget: it gives the number of disks that fit as the number at the upper bound times (1 − 0.46 <i>b</i><sub>0</sub>), it does not explain why the loss is proportional to the boundary share, and its coefficient was fitted on one earlier round and then held fixed. "
           "It is original in the sense that it turns the count-based problem into a prediction that can be checked, but it is a rule for small balls (at most 46 disks here) and for the two methods used, and the number of disks found is a lower bound on the true maximum.")
