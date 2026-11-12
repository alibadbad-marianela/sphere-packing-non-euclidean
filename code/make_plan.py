"""make_plan.py -- builds Research_Plan.docx / .pdf .

This plan states every design value
exactly as executed, adds the common-formulation spherical-cap condition family, and contains a Version History and Timing.
It contains no results.
"""
import os
import json
import inspect
from docbuilder import *
import experiments as E
import algorithms as A

PLAN_DATE = "December 3, 2026"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # folder that contains code/ and out/
OUT = os.path.join(ROOT, "out")

REFS = [
    "Absil, P.-A., Mahony, R., & Sepulchre, R. (2008). <i>Optimization algorithms on matrix manifolds</i>. Princeton University Press.",
    "Byrd, R. H., Lu, P., Nocedal, J., & Zhu, C. (1995). A limited memory algorithm for bound constrained optimization. <i>SIAM Journal on Scientific Computing, 16</i>(5), 1190–1208.",
    "Cohn, H. (n.d.). <i>Spherical codes</i> [Table of best known spherical codes]. Massachusetts Institute of Technology. https://cohn.mit.edu/spherical-codes/",
    "Danzer, L. (1963). <i>Endliche Punktmengen auf der 2-Sphäre mit möglichst grossem Minimalabstand</i> [Habilitation thesis]. Universität Göttingen.",
    "Fejes Tóth, L. (1943). Über eine Abschätzung des kürzesten Abstandes zweier Punkte eines auf einer Kugelfläche liegenden Punktsystems. <i>Jahresbericht der Deutschen Mathematiker-Vereinigung, 53</i>, 66–68.",
    "Hajek, B. (1988). Cooling schedules for optimal annealing. <i>Mathematics of Operations Research, 13</i>(2), 311–329. https://doi.org/10.1287/moor.13.2.311",
    "Liu, D. C., & Nocedal, J. (1989). On the limited memory BFGS method for large scale optimization. <i>Mathematical Programming, 45</i>(1–3), 503–528.",
    "Musin, O. R., & Tarasov, A. S. (2015). The Tammes problem for N = 14. <i>Experimental Mathematics, 24</i>(4), 460–468. https://doi.org/10.1080/10586458.2015.1022842",
    "Robinson, R. M. (1961). Arrangement of 24 points on a sphere. <i>Mathematische Annalen, 144</i>, 17–48.",
    "Saff, E. B., & Kuijlaars, A. B. J. (1997). Distributing many points on a sphere. <i>The Mathematical Intelligencer, 19</i>(1), 5–11.",
    "Schütte, K., & van der Waerden, B. L. (1951). Auf welcher Kugel haben 5, 6, 7, 8 oder 9 Punkte mit Mindestabstand Eins Platz? <i>Mathematische Annalen, 123</i>, 96–124.",
    "Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., ... SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. <i>Nature Methods, 17</i>(3), 261\u2013272. https://doi.org/10.1038/s41592-019-0686-2",
    "Wales, D. J., & Doye, J. P. K. (1997). Global optimization by basin-hopping and the lowest energy structures of Lennard-Jones clusters containing up to 110 atoms. <i>The Journal of Physical Chemistry A, 101</i>(28), 5111\u20135116. https://doi.org/10.1021/jp970984n",
    "Specht, E. (n.d.). <i>Packomania: Circles in a circle</i> [Data set]. http://www.packomania.com/",
    "Sloane, N. J. A., Hardin, R. H., Smith, W. D., & others. (n.d.). <i>Tables of spherical codes</i> [Data set]. http://neilsloane.com/packings/",
    "Tammes, P. M. L. (1930). On the origin of number and arrangement of the places of exit on the surface of pollen-grains. <i>Recueil des Travaux Botaniques Néerlandais, 27</i>, 1–84.",
    "Böröczky, K. (1978). Packing of spheres in spaces of constant curvature. <i>Acta Mathematica Academiae Scientiarum Hungaricae, 32</i>, 243\u2013261. https://doi.org/10.1007/BF01902361",
    "Cannon, J. W., Floyd, W. J., Kenyon, R., & Parry, W. R. (1997). Hyperbolic geometry. In S. Levy (Ed.), <i>Flavors of geometry</i> (pp. 59\u2013115). Cambridge University Press.",
    "Holm, S. (1979). A simple sequentially rejective multiple test procedure. <i>Scandinavian Journal of Statistics, 6</i>(2), 65\u201370.",
    "Kirkpatrick, S., Gelatt, C. D., Jr., & Vecchi, M. P. (1983). Optimization by simulated annealing. <i>Science, 220</i>(4598), 671\u2013680. https://doi.org/10.1126/science.220.4598.671",
    "Lubachevsky, B. D., & Stillinger, F. H. (1990). Geometric properties of random disk packings. <i>Journal of Statistical Physics, 60</i>, 561\u2013583. https://doi.org/10.1007/BF01025983",
    "Metropolis, N., Rosenbluth, A. W., Rosenbluth, M. N., Teller, A. H., & Teller, E. (1953). Equation of state calculations by fast computing machines. <i>The Journal of Chemical Physics, 21</i>(6), 1087\u20131092. https://doi.org/10.1063/1.1699114",
    "Musin, O. R., & Tarasov, A. S. (2012). The strong thirteen spheres problem. <i>Discrete & Computational Geometry, 48</i>(1), 128\u2013141. https://doi.org/10.1007/s00454-011-9392-2",
    "Wilcoxon, F. (1945). Individual comparisons by ranking methods. <i>Biometrics Bulletin, 1</i>(6), 80\u201383. https://doi.org/10.2307/3001968",
]

_hs = open(OUT + '/conf/PREREGISTRATION.sha256').read().split()
PRE_HASH, PRE_TIME = _hs[0], _hs[-1].replace('T', ' at ').replace('Z', '')
NS = E.S2_N
BALL = E.BALL_RN
NSEED = len(E.SEEDS)
dg = {n: {k: v.default for k, v in inspect.signature(fn).parameters.items() if v.default is not inspect._empty}
      for n, fn in (("gd", A.run_gd), ("sa", A.run_sa), ("ls", A.run_ls))}
N_TAM_RUNS = len(NS) * NSEED * 3
N_BALL_RUNS = 3 * len(BALL) * NSEED * 3
SET = ", ".join(f"({r:g}, {n})" for r, n in BALL)



def p10(x):
    """Format a power of ten such as 1e-05 as 10<sup>-5</sup>."""
    import math
    e = int(round(math.log10(x)))
    return f"10<sup>\u2212{abs(e)}</sup>" if e < 0 else f"10<sup>{e}</sup>"

def build(pg):
    d = APADoc(title=TITLE)
    d.title_page(PLAN_DATE)
    d.new_page()
    d.contents_page("Table of Contents", "Chapter", pg["toc"], "toc", field_instr='TOC \\o "1-3" \\z \\u')
    d.new_page()
    d.contents_page("List of Tables", "Table", pg["tables"], "list", in_toc=True)
    d.new_page()
    floats = []

    def F(fn, *a, **k):
        floats.append((fn, a, k))

    def FL():
        while floats:
            fn, a, k = floats.pop(0)
            fn(*a, **k)

    def HD(text, level=1):
        FL()
        return d.heading(text, level)

    p = d._para(align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run_font(p.add_run(TITLE), bold=True)

    # =========================================================== Rationale
    HD("Rationale", 1)
    d.body("This section explains the problem, the existing knowledge on which the study builds, the gap it addresses, and its significance.")
    HD("Background", 2)
    d.body("Packing equal disks or points as densely as possible is a classical problem of geometry. On the unit sphere, the Tammes problem asks for <i>N</i> points whose smallest pairwise geodesic distance is as large as possible. The problem is named for Tammes (1930). Optimal configurations have been proved for <i>N</i> = 3, 4, 6, and 12 (Fejes Tóth, 1943), <i>N</i> = 5, 7, 8, and 9 (Schütte & van der Waerden, 1951), <i>N</i> = 24 (Robinson, 1961), <i>N</i> = 10 and 11 (Danzer, 1963), <i>N</i> = 13 (Musin & Tarasov, 2012), and <i>N</i> = 14 (Musin & Tarasov, 2015); for most other <i>N</i>, the best known configurations come from computer search (Sloane et al., n.d.; Cohn, n.d.) and are not proven optimal. Methods for spreading many points over a sphere are surveyed by Saff and Kuijlaars (1997).")
    d.body("Curvature changes the geometry of packing. In the Euclidean plane the area of a disk grows as the square of its radius; in the hyperbolic plane it grows exponentially (Cannon et al., 1997), so most of the area of a large hyperbolic disk lies near its boundary. Böröczky (1978) proved density bounds for packings in spaces of constant curvature, where the definition of density is itself delicate. Computational methods for packing include energy minimization, Monte Carlo and annealing methods (Kirkpatrick et al., 1983; Metropolis et al., 1953), and compression of growing disks (Lubachevsky & Stillinger, 1990).")
    HD("Research Gap, Importance, and Societal Impact", 2)
    d.body("Established knowledge in this area includes the optimal Tammes configurations listed above, the area formulas of the three plane geometries, and the existence of the three families of methods. The proposed contribution of this project is narrower: a transparent, reproducible comparison of three simple optimizers under one shared protocol, with an equal computational budget and paired random seeds, on one bounded disk-packing problem posed identically in geodesic balls of the sphere (curvature +1), the Euclidean plane (0), and the hyperbolic plane (\u22121), together with the Tammes problem on the whole sphere. I did not find a study that compares these methods this way. The project proves no theorem and does not aim to set packing records.")
    d.body("Well-spread point sets are used to sample spheres and to place sensors or antennas over curved regions, and hyperbolic packings relate to embeddings of tree-like networks. A reproducible comparison can help students and researchers choose a method and see where each method fails.")

    # =========================================================== Research questions
    HD("Research Questions", 1)
    d.body("The study addresses four questions. RQ1: under an equal budget, which of gradient descent, simulated annealing, and compression reaches the best packings in each problem? RQ2: how does performance change as the number of points or disks grows? RQ3: for numbers of points with a proven optimum, how often does each method recover that optimum within a stated tolerance? RQ4 (exploratory): when the same bounded-disk problem is solved in spaces of curvature +1, 0, and −1, does the ranking of the methods change? This question is exploratory because curvature and area are confounded (a ball of the same radius has a different area in each space), only six settings per space are run, and the ball of radius 3 on the sphere covers nearly the whole sphere.")

    # =========================================================== Goals
    HD("Goals, Expected Outcomes, and Hypotheses", 1)
    d.body("This section lists the objectives, states the hypotheses, and fixes the rule that decides whether each hypothesis is supported.")
    HD("Goals and Expected Outcomes", 2)
    d.body(f"The objectives are (O1) to implement and validate the geometry and the three optimizers from scratch, (O2) to run {NSEED} paired seeds in each of {len(NS) + 3 * len(BALL)} conditions under an equal budget, (O3) to report all results, including failures, and (O4) to release code and data so that every table and figure can be regenerated. The expected outcome is a reproducible package that states which method performs best in which setting, with the size and the limits of each difference. No winner is assumed, and negative results will be reported.")
    HD("Hypotheses and Decision Rules", 2)
    d.body("Three hypotheses are tested, each with a decision rule stated in Table 1. This plan was finalized after some results had been seen (see Appendix A, History of Work Done, which states which rules were fixed before, and which after, results were seen), so every hypothesis result is to be reported as exploratory, and H1 most of all. The wording of H1 refers to the space, not to curvature alone, because only the bounded-disk problem is posed identically in all three spaces. Table 1 gives the rules.")
    F(d.table, "Hypotheses and Decision Rules",
      ["Hypothesis", "Test and measurable criterion", "Decision"],
      [["H1 (exploratory): the ranking of the algorithms depends on the space",
        "Common formulation (disks in a geodesic ball, six settings per space): Kruskal\u2013Wallis test across the three spaces of the per-setting mean paired difference in relative score, for each of the three algorithm pairs, Holm-adjusted over the three pairs; and the algorithm with the lowest mean rank in each space.",
        "Supported: some pair has adjusted <i>p</i> < .05 and the lowest-mean-rank algorithm is not the same in all three spaces. Partly supported: exactly one of the two. Not supported: neither."],
       ["H2: compression scales better with <i>N</i>",
        "Tammes problem, <i>N</i> \u2265 13: per-seed slope of relative score on log<sub>10</sub> <i>N</i>; Wilcoxon signed-rank tests of the compression slope against each other slope, Holm-adjusted over two tests.",
        "Supported: compression slope higher than both, adjusted <i>p</i> < .05. Partly supported: higher than one. Not supported: otherwise, including an opposite direction."],
       ["H3: every algorithm recovers the proven optimum for small <i>N</i>",
        "Tammes problem, <i>N</i> = 4 to 14: share of seeds with relative score \u2265 .999 (0.1% tolerance) at each <i>N</i>.",
        "Supported: share \u2265 .90 at every <i>N</i> for all three algorithms. Partly supported: for one or two algorithms. Not supported: for none."]],
      "Relative score = final score divided by the reference value (see Experimental Conditions). A 1% tolerance (relative score \u2265 .99) is reported as a sensitivity check only.",
      aligns=["l", "l", "l"], widths=[1.5, 2.9, 2.1], split=True)

    # =========================================================== Procedures
    HD("Procedures", 1)
    d.body("This section defines the spaces, problems, experimental conditions, algorithms, metrics, and validation tests. The parameter values given are tunable defaults, not requirements; the ranges examined in the sensitivity analysis are stated in the Data Analysis section.")
    HD("Spaces and Problems", 2)
    d.body("Three constant-curvature planes are used. The unit sphere <i>S</i><sup>2</sup> has curvature +1, with points as unit vectors <b><i>x</i></b> in <i>R</i><sup>3</sup> and geodesic distance given by Equation 1. The hyperbolic plane <i>H</i><sup>2</sup> has curvature \u22121; computations use the hyperboloid model, where a point satisfies [<b><i>x</i></b>, <b><i>x</i></b>] = \u22121 and <i>x</i><sub>0</sub> > 0 for the Lorentz product [<b><i>x</i></b>, <b><i>y</i></b>] = \u2212<i>x</i><sub>0</sub><i>y</i><sub>0</sub> + <i>x</i><sub>1</sub><i>y</i><sub>1</sub> + <i>x</i><sub>2</sub><i>y</i><sub>2</sub>, and distance is given by Equation 2; figures use the Poincaré disk. The Euclidean plane <i>R</i><sup>2</sup> has the usual distance.")
    d.equation("cos <i>d</i> = <b><i>x</i></b> \u00b7 <b><i>y</i></b>", 1)
    d.equation("cosh <i>d</i> = \u2212[<b><i>x</i></b>, <b><i>y</i></b>]", 2)
    d.body("Problem A (Tammes) places <i>N</i> points on <i>S</i><sup>2</sup> to maximize the smallest pairwise distance. Problem B places <i>n</i> equal disks in a closed geodesic ball of radius <i>R</i> about a fixed center, in each of the three spaces (a spherical cap, a Euclidean disk, and a hyperbolic disk), and maximizes the common radius <i>r</i>. A disk of radius <i>r</i> whose center is at distance <i>\u03c1</i><sub><i>i</i></sub> from the ball center lies inside the ball when <i>\u03c1</i><sub><i>i</i></sub> \u2264 <i>R</i> \u2212 <i>r</i>, and two disks do not overlap when <i>d</i><sub><i>ij</i></sub> \u2265 2<i>r</i>. Both problems maximize <i>\u2113</i><sub>min</sub> in Equation 3, where the second term is absent for Problem A; the score is <i>\u2113</i><sub>min</sub> for Problem A and <i>r</i> = <i>\u2113</i><sub>min</sub>/2 for Problem B. Problem B is a maximum-radius formulation for fixed <i>n</i> and <i>R</i>; the number of disks of a fixed radius that fit is derived from it.")
    d.equation("<i>\u2113</i><sub>min</sub> = min{ min<sub><i>i</i> < <i>j</i></sub> <i>d</i><sub><i>ij</i></sub>, min<sub><i>i</i></sub> 2(<i>R</i> \u2212 <i>\u03c1</i><sub><i>i</i></sub>) }", 3)
    d.body("The area of a disk of radius <i>r</i> is 2\u03c0(1 \u2212 cos <i>r</i>) on <i>S</i><sup>2</sup> (<i>r</i> \u2264 \u03c0), \u03c0<i>r</i><sup>2</sup> on <i>R</i><sup>2</sup>, and 2\u03c0(cosh <i>r</i> \u2212 1) on <i>H</i><sup>2</sup>. Packing density is <i>n</i> times the area of a disk of radius <i>r</i>, divided by the area of the ball of radius <i>R</i>.")
    HD("Comparability of the Problems", 2)
    d.body("Problem A and Problem B differ in their objective (a minimum distance against a common radius), in their constraints (no boundary against a boundary), and in scale, so their results are not compared with one another. Statements about curvature rest only on Problem B, which has the same formulation, the same <i>R</i> and <i>n</i>, and the same code in all three spaces. Even then, a ball of radius <i>R</i> has a different area in each space, so a difference between spaces can come from curvature, from area, or from both; the study does not separate them. Problem A is used for the comparison of the algorithms on the sphere, the recovery of proven optima, and scaling with <i>N</i>.")
    HD("Experimental Conditions", 2)
    d.body(f"Problem A uses <i>N</i> = {', '.join(str(n) for n in NS[:-1])}, and {NS[-1]}. Problem B uses the six settings (<i>R</i>, <i>n</i>) = {SET} in each of the three spaces. The evaluation seeds are 1 to {NSEED}; the initial configuration depends only on the seed and the condition, so the three algorithms start from the same configuration. Pilot runs for parameter tuning use seeds 9001 to 9004, which are never used in the evaluation. The total is {N_TAM_RUNS + N_BALL_RUNS:,} runs.")
    d.body(f"The Tammes problem accounts for {N_TAM_RUNS:,} runs ({len(NS)} values of <i>N</i> \u00d7 {NSEED} seeds \u00d7 3 algorithms), and each space accounts for {len(BALL) * NSEED * 3:,} runs in Problem B ({len(BALL)} settings \u00d7 {NSEED} seeds \u00d7 3 algorithms). The reference value of a condition is the proven optimum for Problem A with <i>N</i> = 4 to 14 and 24 (credited to Fejes Tóth, 1943; Schütte & van der Waerden, 1951; Robinson, 1961; Danzer, 1963; and Musin & Tarasov, 2012, 2015), the published best-known value where one is entered (Sloane et al., n.d.; Cohn, n.d.), and otherwise the highest score found by any run in that condition; the last two are not claimed to be optimal.")
    HD("Optimization Algorithms", 2)
    d.body("Three algorithms are implemented in Python with numpy. Table 2 gives the default value of every parameter; each is tunable. All three move points along geodesics and keep points on the manifold, and all report the best configuration they visited, scored exactly from its coordinates.")
    F(d.table, "Algorithm Parameters", ["Algorithm and parameter", "Value"],
      [["GD: energy, exponent", f"<i>E<sub>p</sub></i> = (1/<i>p</i>) ln \u03a3 <i>\u2113<sub>k</sub></i><sup>\u2212<i>p</i></sup> over pair distances and, in Problem B, doubled wall clearances; <i>p</i> from {dg['gd']['p0']:g} to {dg['gd']['pmax']:g}, geometric in the share of budget used"],
       ["GD: step, line search", "<i>\u03b7</i> = min(<i>m</i> \u2113<sub>min</sub><sup>2</sup>/<i>p</i>, 0.25 \u2113<sub>min</sub>/max|<i>g</i>|); <i>m</i> starts at 0.5, \u00d7 1.3 after success (maximum 2), \u00d7 0.5 after failure (minimum 0.001); on failure multiply <i>\u03b7</i> by 0.4, at most 5 trials"],
       ["SA: temperature", f"Geometric from {dg['sa']['T0f']:g} to {p10(dg['sa']['T1f'])} times the length scale \u221a(area/<i>n</i>)"],
       ["SA: move, adaptation", "Random geodesic step of length \u03b4(0.1 + 0.9<i>u</i>), <i>u</i> uniform on (0, 1); \u03b4 starts at 0.3 times the length scale; every 100 proposals \u03b4 \u00d7 1.15 if acceptance > .40, \u00d7 0.87 if < .25"],
       ["SA: point choice", f"Probability {dg['sa']['focus']:g}: an endpoint of the limiting pair or the point nearest the wall; otherwise uniform"],
       ["CP: time step, growth", f"Time step {dg['ls']['dt_f']:g} times the length scale at unit root-mean-square speed; common radius grows by \u03b3 d<i>t</i> per step, \u03b3 falling linearly from {dg['ls']['g0']:g} to {dg['ls']['g1']:g}, capped by half the smallest distance"],
       ["CP: collisions", "Velocity components along the line of centers exchanged if approaching; overlaps removed; wall reflection in Problem B; kinetic energy renormalized each step"]],
      "GD = gradient descent; SA = simulated annealing; CP = compression. The length scale is \u221a(area/<i>n</i>). The compression method is a simplified, time-stepped version of the method of Lubachevsky and Stillinger (1990). The values are defaults used in the reported runs, chosen on pilot seeds; they are not fixed by the design, and the ranges examined later are listed under Supplementary Exploratory Analyses.",
      aligns=["l", "l"], widths=[1.6, 4.9])
    HD("Budget, Initialization, and Stopping", 2)
    d.body(f"Every run receives a budget of {E.BUDGET_SWEEPS:,} sweeps, where one sweep is the <i>n</i>(<i>n</i> \u2212 1)/2 pair-distance evaluations needed to compute all distances once; a gradient step costs one sweep plus one sweep per line-search trial (in Problem B each evaluation also includes the <i>n</i> wall clearances), a simulated-annealing move costs <i>n</i> \u2212 1 evaluations, and a compression step costs two sweeps. Gradient descent and compression stop when their next step would exceed the budget; simulated annealing fixes its number of moves from the budget in advance and does not charge proposals rejected for lying outside the ball, so it may use slightly less than the budget. Initial points are uniform on <i>S</i><sup>2</sup> for Problem A and uniform by area in the ball of radius <i>R</i> \u2212 0.05 for Problem B.")
    HD("Evaluation Metrics", 2)
    d.body("The primary metric is the relative score, the final score divided by the reference value. A run succeeds if its relative score is at least .999; success rates are reported with a 1% sensitivity check (relative score at least .99). Convergence is the number of sweeps used when the best score first reached 99% of the run\u2019s own final score. Scaling is the per-seed slope of relative score on log<sub>10</sub> <i>N</i> for <i>N</i> \u2265 13, and the log\u2013log slope of mean run time on <i>N</i>. Computational cost is the wall-clock time, reported as descriptive information because the budget is fixed in distance evaluations. Mathematical optimality is claimed only where a published proof exists; elsewhere a result is called the best score found.")
    HD("Final Round: Design, Rules, and Timestamp", 2)
    d.body("A last round is planned to answer the one question that earlier rounds left open, whether curvature changes the density deficit once the boundary share is in the model, and to test one original rule. Its hypotheses, decision rules, seeds, and analysis code are fixed in PREREGISTRATION_ROUND3.md before any run; Table 3 gives its decision rules and Table 4 its design. Everything that happened in earlier rounds is in Appendix A.")
    _r3 = open(OUT + "/conf/ROUND3.sha256").read().split("\n")
    F(d.table, "Decision Rules of the Final Round",
      ["Question", "Decision rule"],
      [["A1: curvature adds a deficit at a given boundary share", "Fit <i>\u03b4</i> = <i>a</i> + <i>\u03b2 b</i> + <i>g</i><sub>H</sub> [hyperbolic] + <i>g</i><sub>S</sub> [cap]; the 95% interval of <i>g</i><sub>H</sub> is from 10,000 bootstrap resamples of the 48 cells. Detectable if the interval excludes 0 and <i>g</i><sub>H</sub> \u2265 .02; no detectable effect if the interval lies within \u00b1.02; otherwise inconclusive. The same rule is applied to the cap term."],
       ["A2: paired differences (descriptive)", "Mean difference in <i>\u03b4</i> between the hyperbolic disk (and the cap) and the Euclidean disk over the 48 cells, with a bootstrap interval."],
       ["B1: the number of disks can be predicted", "<i>K</i><sub>pred</sub> = floor(<i>n</i><sub>ref</sub>(1 \u2212 0.46 <i>b</i><sub>0</sub>) + 0.5), with <i>n</i><sub>ref</sub> the number of disks that would fit at the upper bound on the density and <i>b</i><sub>0</sub> the design boundary share. Supported if at least 80% of conditions have |<i>K</i> \u2212 <i>K</i><sub>pred</sub>| \u2264 1, the mean absolute error is at most 1.0 disk, the mean relative error is at most .10, and each space has a mean signed error within \u00b11 disk; not supported if fewer than 60% are within 1 or the mean absolute error exceeds 1.5; otherwise inconclusive."]],
      "The coefficient 0.46 was fitted in an earlier round and is not refitted. With the residual spread of the earlier round, the expected half-width of the interval of <i>g</i><sub>H</sub> is about .03, so the round can show an effect of .03 or more but may remain inconclusive; the plan states this before the data. Data: PREREGISTRATION_ROUND3.md.",
      aligns=["l", "l"], widths=[2.0, 4.5], split=True)
    F(d.table, "Design of the Final Round",
      ["Part", "Conditions", "Methods, budget, and seeds"],
      [["A: curvature at equal area", "Three spaces (Euclidean disk, hyperbolic disk, spherical cap) \u00d7 eight areas (2, 3, 4, 5, 6, 8, 10, 12) \u00d7 six numbers of disks (8, 12, 16, 20, 24, 32) = 144 conditions in 48 cells of equal area and equal <i>n</i>.", "Polished gradient descent and L-BFGS-B; 1,500 sweeps; fresh seeds 501 to 520; 5,760 runs."],
       ["B: a rule for the number of disks", "Disk radii 0.25 and 0.35 \u00d7 four design boundary shares (0.375 to 0.525) in the hyperbolic disk and the cap, and the four boundary shares in the Euclidean disk (no length scale) = 20 conditions.", "Polished gradient descent; 1,500 sweeps; fresh seeds 601 to 620; the number of disks <i>K</i> is the largest <i>n</i> reached in at least 10 of 20 seeds."]],
      "The ball radius of each condition follows from its area (Part A) or from the design boundary share and the disk radius (Part B). Data files named in PREREGISTRATION_ROUND3.md.",
      aligns=["l", "l", "l"], widths=[1.4, 3.3, 1.8], split=True)
    d.body(f"<b>Timestamp.</b> The preregistration file has the SHA-256 hash {_r3[0].split()[0]}, recorded by the author on {_r3[1].split(': ')[1].replace('T', ' at ').replace('Z', '')} UTC. A hash recorded by the author is not an independent time stamp. Before any run of the final round, the author will email the preregistration file, this plan, and the earlier preregistration files to the research adviser, and the date of that email is the time stamp; no run is started before it is sent. Any deviation will be listed in the Research Paper. This plan was finished before the Research Paper, and its body will not be changed after the final round has run; later events are recorded in the paper.")
    HD("Validation Tests", 2)
    d.body("The tests in Table 5 are executed before the experiments that depend on the code they check, and those experiments proceed only if every test passes. No test result is reported unless the test was executed.")
    F(d.table, "Validation Tests and Pass Criteria",
      ["Test group", "How it is performed", "Pass criterion"],
      [["Sphere distance", "300 pairs vs. arctangent form; closed forms", "Error < 10<sup>\u22129</sup>; closed forms < 10<sup>\u221212</sup>"],
       ["Hyperbolic distance", "Poincaré formula; law of cosines; area integral", "Relative error < 10<sup>\u22127</sup>; others < 10<sup>\u22126</sup>"],
       ["Euclidean control", "Distance of (0,0), (3,4); 7-disk hexagon", "Error < 10<sup>\u221212</sup>"],
       ["Spherical cap", "Poles, area, sampling, Euclidean limit", "Area < 10<sup>\u22126</sup>; limit within 0.2%"],
       ["Metric axioms", "Symmetry; 4,000 triples per space", "Asymmetry < 10<sup>\u221212</sup>; triangle < 10<sup>\u22129</sup>"],
       ["Exponential map", "Step length; point stays on manifold", "Error < 10<sup>\u22127</sup>"],
       ["Gradients", "Analytic gradient vs. finite differences", "Difference < 10<sup>\u22125</sup>"],
       ["Known Tammes optima", "Three polyhedra; optimizers, seeds 9101\u20139105", "Gap < 0.002 rad"]],
      "A failing test blocks the experiments. Recovery by each optimizer is hypothesis H3, not a validation criterion.",
      aligns=["l", "l", "l"], widths=[1.5, 2.9, 2.1], split=True)
    # =========================================================== Risk and safety
    HD("Risk and Safety", 1)
    d.body("The project is computational, so its risks are procedural. This section lists approvals and the measures that protect data integrity.")
    HD("Hazards and Approvals", 2)
    d.body("The project uses no hazardous materials, human participants, or vertebrate animals. It requires a risk assessment: Form 3 (Risk Assessment) is required for all projects, together with Form 1, Form 1A, and Form 1B and this Research Plan. Form 7 is required only if the project continues earlier research.")
    HD("Disclosure of AI Assistance and Researcher\u2019s Contribution", 2)
    d.body("Claude, an AI assistant developed by Anthropic, was used to assist with the writing of this document, including drafting, grammar checking, and language refinement. Other uses of AI assistance in this project, including its use in programming and analysis, are described in the separate AI Disclosure Agreement submitted to the research adviser and the Science Research Committee. GitHub was used to support code management and access to programming resources. The author\u2019s original contributions include the selection of the research problem, the formulation of the research questions, and the decisions regarding the research design. The author personally ran and checked the code, verified the results, and can explain and defend the programming procedures, methods, and findings. The author accepts full responsibility for the accuracy and integrity of every statement, numerical result, citation, and conclusion presented in this research. The code and data are provided to support reproducibility and independent verification of the results.")
    HD("Data Integrity, Backups, and Reproducibility", 2)
    d.body("One master script, build_all.py, runs the tests, experiments, statistics, figures, and documents with fixed seeds. Every result is saved to a CSV file; SHA-256 hashes of the delivered files are listed in MANIFEST.sha256 and can be checked with sha256sum. Copies of the code and data are to be kept in at least two separate places. Software versions are listed in the code listing, README.md describes every column of every file, and all results, including failures and negative findings, are retained.")

    # =========================================================== Data analysis
    HD("Data Analysis", 1)
    d.body("This section states exactly which observations are compared, which tests are used and why, how their assumptions are checked, and how significance is decided.")
    HD("Comparisons and Tests", 2)
    d.body(f"For each condition the observations are the {NSEED} final scores of each algorithm; scores of the same seed come from the same starting configuration and form a block. The Friedman test compares the three algorithms across the {NSEED} blocks, and the Wilcoxon signed-rank test (Wilcoxon, 1945) compares each pair on the {NSEED} within-seed differences. Nonparametric paired tests are chosen because scores are bounded, are tied or clustered at local optima, and are not normally distributed. Effect sizes are Kendall\u2019s <i>W</i> for the Friedman test and the matched-pairs rank-biserial correlation with the standardized mean difference <i>d<sub>z</sub></i> for pairs. Means carry 95% confidence intervals based on the <i>t</i> distribution; with 30 seeds these intervals are approximate for non-normal scores and are used descriptively.")
    HD("Assumptions, Multiplicity, and Significance", 2)
    d.body("The tests assume that blocks are independent, which holds because each seed gives an independent random start. The Wilcoxon test also assumes that paired differences are symmetric about their median; this is checked by the skewness of each set of differences (an absolute value above 1 is flagged), and the shares of zero differences are reported. Tests are corrected with the Holm procedure (Holm, 1979), where one family is all tests of the same kind within one space, and the hypothesis tests are corrected across their own pairs. A result is statistically significant when the Holm-adjusted <i>p</i> is below .05. Practical importance is judged separately: a difference counts as practically important when its mean is at least 0.5% of the reference value, so a significant but smaller difference is reported as such.")

    HD("Properties of the Algorithms and Supplementary Analyses", 2)
    d.body("Only some properties of the algorithms are proven. Proven: the soft-minimum energy lies between \u2212ln \u2113<sub>min</sub> and \u2212ln \u2113<sub>min</sub> + (ln <i>m</i>)/<i>p</i>, so it approaches the true objective as <i>p</i> grows; the gradient is checked against finite differences. Not proven: convergence of any of the three optimizers to a global optimum, and any statement that one is better in general; such statements are empirical and are limited to the conditions run. Supplementary analyses, all exploratory and reported separately in the paper, are planned or have been run for: (a) gradient descent followed by a max-min polishing step (a sequential linear program whose cost is not charged in the sweep count), with wall-clock time reported beside equal-sweep results, because simulated annealing costs much more time per sweep; (b) sensitivity to budget, to the soft-minimum exponent and annealing schedule, and to the starting configuration; (c) an equal-area version of the ball problem and larger balls; and (d) a check of scores against an independent computation. Parameter values named in this plan are defaults; the ranges tried are listed in the paper.")
    FL()
    d.new_page()
    HD("References", 1)
    for r in sorted(REFS, key=lambda s: s.replace("ö", "o").lower()):
        d.reference(r)
    d.new_page()
    HD("Appendix A: History of Work Done", 1)
    d.body("This appendix records what was done before the final round, in the order it happened, with the dates and hashes that the author recorded. It is a record of past work, not a plan; the plan is the body of this document. The Research Paper reports the results.")
    HD("Version History and Timing", 2)
    d.body("The plan was finalized after results existed, so the decision rules in Table 1 are not pre-registered in the strict sense; the dated history below states what was changed, and when, after results had been seen. Only the confirmatory round (version 3), the mini-round (version 4), and the follow-up (version 5) are preregistered, and one decision of the mini-round has been withdrawn (version 5.1), and each preregistration is dated by the hash given below, which the author recorded. The results of earlier versions are never changed by later ones.")
    d.body("<b>Version 1, October 25, 2026.</b> An earlier draft exists. This plan makes no claim that it preceded any experiment.")
    d.body("<b>Version 2, October 26, 2026.</b> States exact design values as executed. By then the 27 conditions of Problem A and of Problem B in <i>H</i><sup>2</sup> and <i>R</i><sup>2</sup> had been run, and the spherical-cap results had been seen. To the author\u2019s knowledge their analysis code was written before their results were inspected; the data package contains no dated record of the order. After those results were seen, the spherical-cap family (six settings) was added to study curvature in one common formulation; its analysis (Table 1, H1) was written into the analysis code before the cap runs were executed, but H1 as now worded is exploratory with respect to the earlier results. The 0.5% practical-importance threshold and the assumption checks were formalized after the first 27 conditions had been run; the compression method was simplified to a time-stepped scheme; the validation criterion for optimizer recovery was changed to the best of the three optimizers after compression failed an earlier per-optimizer version; and the wording of the second H1 criterion was clarified after the cap results were seen, from \u201cdiffers in at least two of the three spaces\u201d to \u201cis not the same in all three spaces\u201d (the two readings give the same decision).")
    d.body("<b>Version 2.1, October 28, 2026.</b> Statements about timing were corrected to match the records; the budget description in Procedures was clarified to match the code; and a sentence about work breaks was removed from Risk and Safety. After results were seen: the reference values for Tammes problems at <i>N</i> \u2265 30 were taken from published best-known values (Sloane\u2019s tables, via Cohn\u2019s compilation) rather than the best score found by the runs, and the relative scores were recomputed; the citations for the proven optima were corrected to Fejes T\u00f3th, Sch\u00fctte and van der Waerden, Danzer, Robinson, and Musin and Tarasov; all hypothesis results and RQ4 were labeled exploratory; supplementary exploratory analyses were added (gradient descent with a final polishing step, wall-clock time, sensitivity to budget, parameters and starting configuration, an equal-area comparison and larger balls); and an AI-assistance statement was added. The 27 conditions, the six cap settings, the three optimizers, the budget, and the decision rules in Table 1 were not changed.")
    d.body(f"<b>Version 3, October 29, 2026.</b> Adds a preregistered confirmatory round (see the next section), which uses fresh seeds, three budget levels, equal-area balls, added baselines, and a hardware record. Its preregistration file has the SHA-256 hash {PRE_HASH}, computed on {PRE_TIME} UTC before the pilot tuning and before any evaluation seed was run; the tuned parameters were hashed before the evaluation run. A hash recorded by the author is not an independent time stamp. No hypothesis, decision rule, or result of versions 1 to 2.1 was changed. Any further change will be recorded here and in the paper.")
    _ad = open(OUT + "/conf/PREREG_ADDENDA.sha256").read().split("\n")
    _h = lambda n: [l.split()[0] for l in _ad if l.endswith(n)][0]
    _rt = open(OUT + "/conf/RETUNED.sha256").read().split("\n")
    d.body(f"<b>Version 4, October 30, 2026.</b> After the results of the confirmatory round had been seen, the author recorded the following in a second file (PREREGISTRATION_ADDENDUM_1.md, SHA-256 {_h('ADDENDUM_1.md')}) and a mini-round file (PREREGISTRATION_MINIROUND.md, SHA-256 {_h('MINIROUND.md')}), both hashed on {[l for l in _ad if l.startswith('hashed')][0].split(': ')[1].replace('T', ' at ').replace('Z', '')} UTC before any run they describe: (1) the Packomania values for the Euclidean conditions were entered after the first analysis, which had used the best score found (the decisions were the same with both references); (2) the candidate ranges of compression and L-BFGS-B were extended, because their selected values lay at the edge of the old ranges, and both methods were run again (new tuned values hashed {[l for l in _rt if l.startswith('hashed')][0].split(': ')[1].replace('T', ' at ').replace('Z', '')} UTC, SHA-256 {[l.split()[0] for l in _rt if l.endswith('tuned_params_retuned.json')][0]}, before the evaluation); (3) the confirmatory round was run again with the same seeds and saved the final configuration of every run, and the wall contact is reported for all runs; (4) a mini-round with a fixed disk radius and a matched boundary share was added (seeds 301 to 320); and (5) the reference density is described as an upper bound on the density, not as the density of a densest packing. The first preregistration file was not edited, and no result of versions 1 to 3 was changed. Because the author recorded the hashes, they are not independent time stamps; the author reports having emailed the four preregistration files to the research adviser on October 30, 2026, after the runs of the confirmatory round and the mini-round and before the runs of the follow-up, and the adviser\u2019s email, not the author\u2019s hash, is the independent record (it cannot show that the first three files preceded their runs).")
    _fu = open(OUT + "/conf/FOLLOWUP.sha256").read().split("\n")
    _r3h = open(OUT + "/conf/ROUND3.sha256").read().split()[0]
    d.body(f"<b>Version 5, October 30, 2026.</b> Adds a preregistered follow-up to the mini-round (PREREGISTRATION_FOLLOWUP.md, SHA-256 {_fu[0].split()[0]}, hashed on {_fu[1].split(': ')[1].replace('T', ' at ').replace('Z', '')} UTC before its runs). It corrects a flaw of the mini-round: the Euclidean plane has no length scale, so the Euclidean conditions at disk radii 0.30 and 0.40 were the same problem and the six Euclidean conditions were three, which also overstated the degrees of freedom of rule M2. The follow-up uses five design boundary shares, three disk radii for the hyperbolic disk and the cap, one Euclidean condition per boundary share, seeds 401 to 420, and two methods (polished gradient descent and L-BFGS-B) for the number of disks <i>K</i>. No rule, result, or hash of versions 1 to 4 was changed; the mini-round decisions are reported as they were, with a sensitivity analysis without the duplicates.")
    _cr = open(OUT + "/conf/CORRECTION.sha256").read().split("\n")
    d.body(f"<b>Version 5.1, October 30, 2026 (a withdrawal).</b> The decision of rule M2 of the mini-round, \u201cno detectable curvature effect\u201d (hyperbolic term 0.007, interval \u22120.032 to 0.046, 13 degrees of freedom), is withdrawn. The Euclidean conditions at disk radii 0.30 and 0.40 are the same problem, so the 18 conditions were 15 and the degrees of freedom 10; without the duplicates (a post hoc analysis, decided after the result was seen) the interval is \u22120.058 to 0.060 and the decision is inconclusive. Earlier text, including the paper written before this correction, said that no curvature effect larger than .05 was found in the mini-round; that statement is withdrawn. The correction note (CORRECTION_NOTE_1.md, SHA-256 {_cr[0].split()[0]}, hashed {_cr[1].split(': ')[1].replace('T', ' at ').replace('Z', '')} UTC, recorded by the author) states this, and the mini-round decisions as originally computed are kept in mini_decisions.json and reported next to the corrected analysis.")
    d.body("The runs of the follow-up began about one minute after the hash of its file was recorded (23:34 UTC on October 29, 2026; run times in FOLLOWUP_RUNTIMES.txt), and the replacement boundary shares and the second method were in that file; the author reports that the four files had been emailed to the research adviser before the runs began. F1 to F3 are therefore preregistered by the author\u2019s hash, and the adviser\u2019s email is the independent record of the date of the files.")
    d.body(f"<b>Version 6, October 30, 2026.</b> The plan was restructured so that its body looks forward: it states the hypotheses, decision rules, seeds, and timestamp of one final round (PREREGISTRATION_ROUND3.md, SHA-256 {_r3h}), and the history of earlier work, including every version above, is kept in this appendix. The final round was preregistered to settle the curvature question that three earlier rounds left inconclusive (more equal-area conditions, with the bootstrap taken over cells of equal area and equal number of disks) and to test a rule for the number of disks. No rule, result, or hash of versions 1 to 5.1 was changed.")
    # ---- confirmatory round
    HD("Confirmatory Round", 2)
    d.body("This section describes a second round of experiments whose hypotheses, thresholds, and decision rules were written and hashed before any of its evaluation seeds was run. The full text is PREREGISTRATION.md in the data package.")
    HD("Prediction and Design", 3)
    d.body("Curvature and area are confounded in the first study, because a ball of a given radius has a different area in each space. The confirmatory round therefore compares balls of equal area. For <i>n</i> disks of radius <i>r</i> in a ball of radius <i>R</i>, the density deficit is <i>\u03b4</i> = 1 \u2212 [<i>n</i> Area(<i>r</i>) / Area(<i>R</i>)] / <i>\u03c1</i>*, where <i>\u03c1</i>* is an upper bound on the density of any packing of disks of radius <i>r</i> in the whole space (Fejes T\u00f3th, 1943; B\u00f6r\u00f6czky, 1978), and the boundary share is <i>b</i> = 1 \u2212 Area(<i>R</i> \u2212 <i>r</i>) / Area(<i>R</i>). The prediction is that <i>\u03b4</i> increases with <i>b</i> in every space, so that most of the deficit is a boundary effect and not a curvature effect.")
    d.body("The design uses fresh evaluation seeds 101 to 120, three budget levels of 500, 1,500, and 3,000 sweeps as part of the main design, and six methods: gradient descent, gradient descent with a polishing step, simulated annealing, compression, SciPy L-BFGS-B (Virtanen et al., 2020; Byrd et al., 1995), and basin hopping (Wales & Doye, 1997). Each method has one tuned parameter with six candidate settings, tuned on the same pilot conditions and pilot seeds 9101 to 9104. The 33 conditions are the Tammes problem for <i>N</i> = 9, 13, 14, 24, 30, 40, and 60; balls of equal area 3, 6, and 12 with 12 and 24 disks in the spherical cap, the Euclidean disk, and the hyperbolic disk; and hyperbolic balls of radius 2, 3, 6, and 8 with 24, 36, 50, and 70 disks, each paired with a Euclidean disk of the same area. Equal area in all three spaces is possible only up to 4\u03c0, so the large balls compare two spaces. The parameter values are tunable defaults, not requirements. The hardware and software are recorded before the run, and no run is excluded.")
    d.body("Reference values are the proven optimum or the published best-known value (Sloane\u2019s tables) for the Tammes problem, the Packomania value (Specht, n.d.) for the ten Euclidean conditions with 12, 24, 36, 50, or 70 disks (entered after the first analysis), and otherwise the best score found in the round, which is stated wherever it is used. As an original element, a count-based version of the disk problem asks for the largest number of disks of a fixed radius that fit in a ball of a given area; it is exploratory and has no decision rule.")
    HD("Decision Rules", 3)
    F(d.table, "Decision Rules of the Confirmatory Round",
      ["Question", "Decision rule (1,500 sweeps unless stated)"],
      [["C1: the density deficit follows the boundary share (26 ball conditions)", "Supported if Spearman <i>r</i><sub>s</sub> between <i>b</i> and <i>\u03b4</i> is at least .70 and the one-sided permutation <i>p</i> is below .05; not supported if <i>r</i><sub>s</sub> is below .30; otherwise inconclusive."],
       ["C2: curvature adds a deficit beyond the boundary share", "Least-squares fit of <i>\u03b4</i> on <i>b</i> and indicators of space; a detectable effect if the 95% bootstrap interval of the hyperbolic term excludes 0 and the term is at least .02; no effect if the whole interval lies within \u00b1.02."],
       ["C3: the ranking of gradient descent and annealing depends on the space (18 equal-area conditions)", "Dependent if the Kruskal\u2013Wallis <i>p</i> is below .05; independent if each 90% bootstrap interval of a difference of medians lies within \u00b1.01."],
       ["C4: stronger baselines matter; polished gradient descent is competitive", "L-BFGS-B or basin hopping beats both gradient descent and annealing in at least half of the 33 conditions; polished gradient descent ranks first or second in at least half."],
       ["C5: the ranking of the methods is stable across budgets", "Median Kendall\u2019s <i>W</i> over the three budget levels is at least .80."],
       ["C6: some method recovers the proven optimum for <i>N</i> = 9, 13, 14, 24", "The best share of seeds with relative score at least .999 is at least .90 for all four."]],
      "All six questions are separate, are reported whatever the outcome, and are not corrected for one another. Analyses not listed here are exploratory. Data: PREREGISTRATION.md.",
      aligns=["l", "l"], widths=[2.4, 4.1], split=True)
    HD("Mini-Round With a Matched Boundary Share", 3)
    d.body("The main round could not separate curvature from the boundary effect (C2 was inconclusive), and its boundary share depends on the radius each method finds. A mini-round fixes the disk radius <i>r</i><sub>0</sub> (0.30 or 0.40) and a design boundary share <i>b</i><sub>0</sub> (0.40, 0.45, or 0.50) and chooses the radius of each ball so that <i>b</i><sub>0</sub> is the same in the Euclidean disk, the hyperbolic disk, and the spherical cap (18 conditions). For each ball, <i>K</i> is the largest number of disks for which polished gradient descent at 1,500 sweeps reaches radius <i>r</i><sub>0</sub> in at least 10 of 20 fresh seeds (301 to 320), and the fixed-radius deficit is <i>\u03b4</i><sub>0</sub> = 1 \u2212 <i>K</i> Area(<i>r</i><sub>0</sub>) / (Area(<i>R</i>) <i>\u03c1</i>*). The full text is PREREGISTRATION_MINIROUND.md.")
    F(d.table, "Decision Rules of the Mini-Round",
      ["Question", "Decision rule"],
      [["M1: the fixed-radius deficit follows the design boundary share", "Supported if Spearman <i>r</i><sub>s</sub> between <i>b</i><sub>0</sub> and <i>\u03b4</i><sub>0</sub> is at least .50 and the one-sided permutation <i>p</i> (20,000 permutations) is below .05; not supported if <i>r</i><sub>s</sub> is below .20; otherwise inconclusive."],
       ["M2: curvature adds a deficit at a matched boundary share", "Least-squares fit of <i>\u03b4</i><sub>0</sub> on <i>b</i><sub>0</sub>, indicators of the hyperbolic disk and the cap, and <i>r</i><sub>0</sub> (13 degrees of freedom); a detectable effect if the 95% <i>t</i> interval of the hyperbolic term excludes 0 and the term is at least .05 in size; no detectable effect if the whole interval lies within \u00b1.05; otherwise inconclusive. The preregistered fit counted 13 degrees of freedom, which included three duplicated Euclidean conditions; the decision it produced is withdrawn (Version 5.1)."],
       ["M3: a boundary-loss model describes the other spaces", "<i>\u03b4</i><sub>0</sub> = <i>\u03bb b</i><sub>0</sub>, with <i>\u03bb</i> fitted on the six Euclidean conditions and not refitted; the model describes the other twelve conditions if their mean absolute error is at most .05, and does not if it exceeds .10; otherwise inconclusive."]],
      "The three rules are separate and are not corrected for the six rules of the main round. Analyses not listed here are exploratory. The decision of M2 is withdrawn (Version 5.1). Data: PREREGISTRATION_MINIROUND.md.",
      aligns=["l", "l"], widths=[2.4, 4.1], split=True)
    HD("Follow-Up to the Mini-Round", 3)
    d.body("The mini-round was inconclusive for M1, and its Euclidean conditions at two disk radii were the same problem (the Euclidean plane has no length scale). The follow-up uses five design boundary shares (0.35 to 0.55), three disk radii (0.20, 0.30, and 0.40) for the hyperbolic disk and the cap, one Euclidean condition per boundary share, and fresh seeds 401 to 420 (33 conditions). The number of disks <i>K</i> is computed with polished gradient descent and with L-BFGS-B, and the larger value is used because each is a lower bound. The full text is PREREGISTRATION_FOLLOWUP.md.")
    F(d.table, "Decision Rules of the Follow-Up",
      ["Question", "Decision rule"],
      [["F1: the fixed-radius deficit follows the design boundary share (33 conditions)", "Same thresholds as M1: supported if Spearman <i>r</i><sub>s</sub> is at least .50 and the one-sided permutation <i>p</i> is below .05; not supported if <i>r</i><sub>s</sub> is below .20; otherwise inconclusive."],
       ["F2: curvature adds a deficit at a matched boundary share", "Same rule as M2, fitted with indicators of the two radii other than 0.30 (27 degrees of freedom): detectable if the 95% <i>t</i> interval of the hyperbolic term excludes 0 and the term is at least .05; no detectable effect if the interval lies within \u00b1.05; otherwise inconclusive."],
       ["F3: a boundary-loss model describes the other spaces", "Same rule as M3, with <i>\u03bb</i> fitted on the five Euclidean conditions and used to predict the other 28; at most .05 describes, more than .10 does not. The model is a description, not an explanation."]],
      "The three rules are separate and are not corrected for the nine rules of the earlier rounds. Analyses not listed here, including the second method alone and the mini-round without duplicates, are exploratory. Data: PREREGISTRATION_FOLLOWUP.md.",
      aligns=["l", "l"], widths=[2.4, 4.1], split=True)
    d.body("Tables 6, 7, and 8 give the decision rules of the confirmatory round, the mini-round, and the follow-up. Analyses outside these rules, including the count-based problem and every robustness check, are exploratory and are labeled so in the paper.")

    FL()
    return d


def main():
    d0 = build({"toc": [], "tables": []})
    probe = [(l, t, 0) for l, t in d0.headings]
    tabs = [(n, t, 0) for k, n, t in d0.captions if k == "Table"]
    pg = {"toc": probe, "tables": tabs}
    for it in range(4):
        d = build(pg)
        path = OUT + "/Research_Plan.docx"
        d.save(path)
        pdf = to_pdf(path, OUT)
        pages = pdf_pages(pdf)
        body0 = next(i for i in range(1, len(pages)) if any(l.strip().startswith("Algorithmic Optimization") for l in pages[i].split("\n")[:4]))
        newtoc = []
        for lvl, text, _ in pg["toc"]:
            if text == "List of Tables":
                pnum = find_exact(pages, [text], start_page=2)[0]
            else:
                pnum = find_exact(pages, [text], start_page=body0)[0] or find_pages(pages, [text], start_page=body0)[0]
            newtoc.append((lvl, text, pnum))
        newtab = [(n, t, find_exact(pages, [f"Table {n}"], start_page=body0)[0]) for n, t, _ in pg["tables"]]
        new = {"toc": newtoc, "tables": newtab}
        if new == pg:
            break
        pg = new
    import omml
    omml.MODE = "omml"            # final .docx carries native Word equations; the PDF above used typeset images
    build(pg).save(path)
    print("plan pages:", len(pages), "| missing:", [e for k in pg for e in pg[k] if not e[2]])


if __name__ == "__main__":
    main()
