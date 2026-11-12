"""make_paper.py -- builds Research_Paper.docx / .pdf (version 2).  Every number comes from the CSV files
or the test log; table and figure numbers come from one registry so that text and floats cannot disagree."""
import os
import re
import sys
import json
import confirm_design as _C
import inspect
import platform
import importlib.metadata as md
import numpy as np
import pandas as pd
from docbuilder import *
import algorithms as A
import experiments as E

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # folder that contains code/ and out/
OUT = os.path.join(ROOT, "out")
DATA = OUT + "/data"
FIG = OUT + "/figures"
PAPER_DATE = "December 3, 2026"

runs = pd.read_csv(f"{DATA}/runs_raw.csv")
summ = pd.read_csv(f"{DATA}/summary_by_condition.csv")
pw = pd.read_csv(f"{DATA}/test_pairwise_wilcoxon.csv")
fr = pd.read_csv(f"{DATA}/test_friedman.csv")
hyp = pd.read_csv(f"{DATA}/hypothesis_tests.csv")
over = pd.read_csv(f"{DATA}/overall_by_space.csv")
caps = pd.read_csv(f"{DATA}/capacity_fixed_radius.csv")
area = pd.read_csv(f"{DATA}/area_fractions.csv")
bench = pd.read_csv(f"{DATA}/benchmark_values.csv")
rte = pd.read_csv(f"{DATA}/runtime_scaling_exponents.csv")
asm = pd.read_csv(f"{DATA}/assumption_checks.csv")
cfgall = pd.read_csv(f"{DATA}/configurations.csv")
unit_txt = open(f"{OUT}/unit_test_output.txt").read()
ALG = ["gd", "sa", "ls"]
AB = {"gd": "GD", "sa": "SA", "ls": "CP"}
SPACES = ["S2cap", "R2", "H2"]
SLAB = {"S2": "<i>S</i><sup>2</sup>", "S2cap": "Cap", "R2": "<i>R</i><sup>2</sup>", "H2": "<i>H</i><sup>2</sup>"}
NS2 = sorted(runs[runs.space == "S2"].n.unique())
BALL = E.BALL_RN
SEEDS = runs.seed.nunique()
BUDGET = E.BUDGET_SWEEPS
NRUN = len(runs)
NCOND = runs.condition_id.nunique()
_kn = sorted(int(x) for x in runs[(runs.space == "S2") & (runs.reference_type == "published best known")].n.unique())
_bf = sorted(int(x) for x in runs[(runs.space == "S2") & (runs.reference_type == "best found")].n.unique())


def _nlist(v):
    return (", ".join(map(str, v[:-1])) + (" and " if len(v) > 1 else "") + str(v[-1])) if v else ""


KNOWN_TXT = ("<i>N</i> = " + _nlist(_kn) + "; Sloane et al., n.d.; Cohn, n.d.") if _kn else "none was entered"
STARNOTE = ((("a published best-known value (<i>N</i> = " + _nlist(_kn) + ")") if _kn else "") + ("; " if _kn and _bf else "")
            + (("the best value found by any run (<i>N</i> = " + _nlist(_bf) + ")") if _bf else ""))

TABLES = ["stages", "area", "params", "vtests", "s2res", "ballres", "capacity", "sweeps", "pairwise", "hyp", "gdp", "timing", "equal", "cmeth", "cdec", "crel", "cdef", "cbud", "ccount", "cwall", "r3a", "r3b", "cmini", "cmini2", "cfollow"]
FIGS = ["rank", "framework", "sphere", "curv", "conv", "perf", "runtime", "dist", "cdef", "cbud", "r3def"]
APP = {"budget": "A1", "sens": "A2", "spread": "A3"}        # sensitivity tables, in Appendix A
CONFDIR = OUT + "/conf"
TN = {k: i + 1 for i, k in enumerate(TABLES)}
FN = {k: i + 1 for i, k in enumerate(FIGS)}



def p10(x):
    """Format a power of ten such as 1e-05 as 10<sup>-5</sup>."""
    import math
    e = int(round(math.log10(x)))
    return f"10<sup>\u2212{abs(e)}</sup>" if e < 0 else f"10<sup>{e}</sup>"

def Tb(k):
    return f"Table {APP[k]}" if k in APP else f"Table {TN[k]}"


def Fg(k):
    return f"Figure {FN[k]}"


# ------------------------------------------------------------ formatting helpers
def f(x, d=3, lead=True):
    s = f"{x:.{d}f}"
    if not lead and s.startswith("0."):
        s = s[1:]
    if not lead and s.startswith("-0."):
        s = "-" + s[2:]
    return s.replace("-", "\u2212")


def pstr(p):
    return "<i>p</i> < .001" if p < 0.001 else "<i>p</i> = " + f(p, 3, lead=False)


def S(space, n, alg, R=None):
    g = summ[(summ.space == space) & (summ.n == n) & (summ.algorithm == alg)]
    if R is not None:
        g = g[g.R == R]
    return g.iloc[0]


def PW(space, n, a, b, R=None):
    g = pw[(pw.space == space) & (pw.n == n) & (pw.alg_a == a) & (pw.alg_b == b)]
    if R is not None:
        g = g[g.R == R]
    return g.iloc[0]


def ov(space, alg, col):
    return float(over[(over.space == space) & (over.algorithm == alg)][col].iloc[0])


def wins(space, a, b, who):
    g = pw[(pw.space == space) & (pw.alg_a == a) & (pw.alg_b == b)]
    return int((g.winner == who).sum()), len(g)


def words(s):
    return len(re.findall(r"[A-Za-z0-9\u2212\-\.]+", re.sub(r"<[^>]+>", "", s)))


def best_count(space, alg):
    k = 0
    for R, n in BALL:
        m = {a: S(space, n, a, R=R).mean_score for a in ALG}
        k += int(max(m, key=m.get) == alg)
    return k


def sci(x):
    m, e = f"{x:.1e}".split("e")
    return f"{m} \u00d7 10<sup>\u2212{abs(int(e))}</sup>" if int(e) < 0 else f"{m} \u00d7 10<sup>{int(e)}</sup>"


def test_err(pattern):
    m = re.search(pattern + r".*?\[(?:max rel err|max err) ([0-9.e+-]+)", unit_txt)
    return float(m.group(1))


dflt = {n: {k: v.default for k, v in inspect.signature(fn).parameters.items() if v.default is not inspect._empty}
        for n, fn in (("gd", A.run_gd), ("sa", A.run_sa), ("ls", A.run_ls))}

# ------------------------------------------------------------ derived headline numbers
mrel = {sp: {a: ov(sp, a, "mean_relative_score") for a in ALG} for sp in ("S2", "S2cap", "R2", "H2")}
mrank = {sp: {a: ov(sp, a, "mean_rank") for a in ALG} for sp in ("S2", "S2cap", "R2", "H2")}
best_rank = {sp: min(ALG, key=lambda a: mrank[sp][a]) for sp in mrank}
NAMEL = {"gd": "gradient descent", "sa": "simulated annealing", "ls": "compression"}
assert all(mrank[sp]["ls"] > 2.9 for sp in mrank)          # compression ranks last in every space
fr_sig, fr_n = int(fr.significant.sum()), len(fr)
H1o = hyp[(hyp.hypothesis == "H1") & (hyp.test == "gd-sa")].iloc[0]
H1c = hyp[(hyp.hypothesis == "H1c") & hyp.test.str.contains("across K")]
H1c_gdsa = H1c[H1c.test.str.startswith("gd-sa")].iloc[0]
H1c_h2 = hyp[(hyp.hypothesis == "H1c") & hyp.test.str.contains("H2 minus R2")].iloc[0]
H1c_cap = hyp[(hyp.hypothesis == "H1c") & hyp.test.str.contains("S2cap minus R2")].iloc[0]
h1_a = bool((H1c.p_holm < 0.05).any())                          # criterion (a)
h1_b = len(set(best_rank[s] for s in SPACES)) > 1               # criterion (b)
H1_DECISION = ("Supported" if (h1_a and h1_b) else ("Partly supported" if (h1_a or h1_b) else "Not supported")) + " (exploratory)"
h2_gd = hyp[(hyp.hypothesis == "H2") & (hyp.test == "slope ls - slope gd")].iloc[0]
h2_sa = hyp[(hyp.hypothesis == "H2") & (hyp.test == "slope ls - slope sa")].iloc[0]
ls_higher = [(h2_gd.mean_diff > 0 and h2_gd.p_holm < .05), (h2_sa.mean_diff > 0 and h2_sa.p_holm < .05)]
H2_DECISION = ("Supported" if all(ls_higher) else ("Partly supported" if any(ls_higher) else "Not supported")) + " (exploratory)"
h3 = {a: hyp[(hyp.hypothesis == "H3") & (hyp.test.str.startswith(a + ":"))].iloc[0] for a in ALG}
n3 = sum(int(h3[a].supported) for a in ALG)
H3_DECISION = ("Supported" if n3 == 3 else ("Partly supported" if n3 > 0 else "Not supported")) + " (exploratory)"
s2sm = runs[(runs.space == "S2") & (runs.n <= 14)]
rate1 = {a: s2sm[s2sm.algorithm == a].groupby("n")["success_1pct"].mean() for a in ALG}
below1 = {a: [int(n) for n, v in rate1[a].items() if v < 0.9] for a in ALG}
gd4 = runs[(runs.space == "S2") & (runs.n == 4) & (runs.algorithm == "gd")]
stuck = int((gd4.score < 1.6).sum())
sc_ls_small = {n: S("S2", n, "ls").success_rate_0p1pct for n in (4, 5, 6)}
vers = {p: md.version(p) for p in ("numpy", "scipy", "pandas", "matplotlib", "python-docx", "Pygments", "pdfplumber", "Pillow")}
PYV = platform.python_version()


def table_group_counts():
    lines = [l for l in unit_txt.split("\n") if l.startswith("PASS") or l.startswith("FAIL")]

    def cnt(pred):
        sel = [l for l in lines if pred(l)]
        return len(sel), sum(1 for l in sel if l.startswith("PASS"))
    return [
        ("Sphere distance", "300 random pairs against the arctangent form; closed forms", "Error < 10<sup>\u22129</sup>; closed forms < 10<sup>\u221212</sup> (antipode < 10<sup>\u22127</sup>)",
         *cnt(lambda l: "S2 distance matches" in l or "S2 closed-form" in l)),
        ("Hyperbolic distance", "Poincaré formula, radius tanh(<i>s</i>/2), law of cosines, area integral", "Relative error < 10<sup>\u22127</sup>; others < 10<sup>\u22129</sup>, 10<sup>\u22128</sup>, 10<sup>\u22126</sup>",
         *cnt(lambda l: "H2 hyperboloid" in l or "H2 point" in l or "H2 distance equals" in l or "H2 disk area" in l)),
        ("Euclidean control", "Distance of (0,0) and (3,4); 7-disk hexagon in a ball of radius 3", "Error < 10<sup>\u221212</sup>", *cnt(lambda l: "R2 distance of" in l or "R2 hexagonal" in l)),
        ("Spherical cap", "Pole, equator, antipode, area, sampling, Euclidean limit, clipping", "Area error < 10<sup>\u22126</sup>; sampling within 4 s.e.; limit within 0.2%", *cnt(lambda l: "S2 cap:" in l)),
        ("Metric axioms", "Symmetry and 4,000 random triples per space", "Asymmetry < 10<sup>\u221212</sup>; triangle violation < 10<sup>\u22129</sup>", *cnt(lambda l: "symmetry and triangle" in l)),
        ("Exponential map", "Step length equals vector length; point stays on the manifold", "Error < 10<sup>\u22127</sup>; manifold error < 10<sup>\u22129</sup>", *cnt(lambda l: "exponential map" in l)),
        ("Gradients", "Analytic Riemannian gradient against central finite differences", "Difference < 10<sup>\u22125</sup> max(1, |gradient|)", *cnt(lambda l: "analytic Riemannian gradient" in l)),
        ("Known Tammes optima", "Three polyhedra; optimizers on seeds 9101 to 9105", "Distance error < 10<sup>\u221212</sup>; best gap < 0.002 rad", *cnt(lambda l: "Closed-form Tammes" in l or "Optimizer suite recovers" in l)),
    ]


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
    "Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., ... SciPy 1.0 Contributors. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. <i>Nature Methods, 17</i>(3), 261–272. https://doi.org/10.1038/s41592-019-0686-2",
    "Wales, D. J., & Doye, J. P. K. (1997). Global optimization by basin-hopping and the lowest energy structures of Lennard-Jones clusters containing up to 110 atoms. <i>The Journal of Physical Chemistry A, 101</i>(28), 5111–5116. https://doi.org/10.1021/jp970984n",
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

DEC = json.load(open(CONFDIR + "/decisions.json"))
_FD = json.load(open(CONFDIR + "/followup_decisions.json"))["primary"]
_MD = json.load(open(CONFDIR + "/mini_decisions.json"))
_cr = pd.read_csv(f"{DATA}/conf_runs.csv")
_cr = _cr[(_cr.label == "Tammes N = 13")] if "label" in _cr.columns else _cr[_cr.condition_id == 1001]
_N13H, _N13N = int(_cr["success_0.1pct"].sum()), len(_cr)
_R3 = json.load(open(CONFDIR + "/round3_decisions.json"))
abstract = (
    f"This study compares optimization algorithms for dense packings on the sphere, the Euclidean plane, and the hyperbolic plane under one protocol with an equal budget and paired seeds. "
    f"In a preregistered confirmatory round (six methods, 33 conditions, three budgets; {DEC['n_runs']:,} runs), polished gradient descent had the best mean rank ({f(DEC['C4']['mean_rank_by_method']['gdp'], 2)}), and L-BFGS-B or basin hopping beat both gradient descent and simulated annealing in all {DEC['C4']['n_conditions']} conditions; compression ranked last. "
    f"The shortfall of a packing from the density bound rose with the share of the ball near its wall (Spearman {f(DEC['C1']['spearman'], 2, lead=False)}, partly circular because both come from the radius found; {f(_FD['F1']['spearman'], 2, lead=False)} at a fixed radius). "
    f"A final preregistered round of {_R3['A1']['n_conditions']} equal-area conditions found no curvature effect larger than .02 of the bound (hyperbolic {f(_R3['A1']['g_H'], 3)}, cap {f(_R3['A1']['g_S'], 3)}), though both intervals excluded zero. "
    f"A rule, the number of disks at the bound times (1 \u2212 0.46 times the boundary share), predicted the number of disks that fit within one disk in all {_R3['B1']['n_conditions']} new conditions. "
    f"No method reached a .90 success share for 13 points ({_N13H} of {_N13N} runs). Results concern the budgets and implementations tested and set no records."
)

KEYWORDS = "sphere packing, Tammes problem, hyperbolic plane, optimization algorithms, curvature"


def build(pg):
    d = APADoc(title=TITLE)
    d.title_page(PAPER_DATE)
    d.new_page()
    d.front_heading("Abstract")
    p = d._para(indent_first=0.0, align=WD_ALIGN_PARAGRAPH.LEFT)
    d.add_marked(p, abstract)
    p = d._para(indent_first=0.5, align=WD_ALIGN_PARAGRAPH.LEFT)
    set_run_font(p.add_run("Keywords:"), italic=True)
    set_run_font(p.add_run(" " + KEYWORDS))
    d.new_page()
    d.contents_page("Table of Contents", "Chapter", pg["toc"], "toc", field_instr='TOC \\o "1-3" \\z \\u')
    d.new_page()
    d.contents_page("List of Figures", "Figure", pg["figs"], "list", in_toc=True)
    d.new_page()
    d.contents_page("List of Tables", "Table", pg["tabs"], "list", in_toc=True)
    d.new_page()

    floats = []

    appfloats = []

    def FF(kind, key, *a, **k):
        (appfloats if key in APP else floats).append((kind, key, a, k))

    def FL():
        while floats:
            kind, key, a, k = floats.pop(0)
            if kind == "table":
                assert d.ntab + 1 == TN[key], (key, d.ntab, TN[key])
                d.table(*a, **k)
            else:
                assert d.nfig + 1 == FN[key], (key, d.nfig, FN[key])
                d.figure(*a, **k)

    def HD(text, level=1):
        FL()
        return d.heading(text, level)

    p = d._para(align=WD_ALIGN_PARAGRAPH.CENTER)
    set_run_font(p.add_run(TITLE), bold=True)

    # ====================================================================== Introduction
    HD("Introduction", 1)
    d.body("This paper compares optimization methods for dense packings on the sphere, the Euclidean plane, and the hyperbolic plane: three methods in a first, exploratory study, and six in the preregistered rounds that followed. This section reviews what is known, states the gap, the questions, and the hypotheses, and separates established knowledge from the contribution of this study.")
    HD("Background and Related Work", 2)
    d.body("On the unit sphere, the Tammes problem asks for <i>N</i> points whose smallest pairwise geodesic distance is as large as possible. The problem is named for Tammes (1930). Optimal configurations have been proved for <i>N</i> = 3, 4, 6, and 12 (Fejes Tóth, 1943), <i>N</i> = 5, 7, 8, and 9 (Schütte & van der Waerden, 1951), <i>N</i> = 24 (Robinson, 1961), <i>N</i> = 10 and 11 (Danzer, 1963), <i>N</i> = 13 (Musin & Tarasov, 2012), and <i>N</i> = 14 (Musin & Tarasov, 2015). For most other <i>N</i>, the best known configurations come from computer search (Sloane et al., n.d.; Cohn, n.d.), and their optimality is unproven. Energy-minimization methods for spreading many points over a sphere are surveyed by Saff and Kuijlaars (1997).")
    d.body("Curvature changes the geometry of packing. In the Euclidean plane the area of a disk grows as the square of its radius; in the hyperbolic plane it grows exponentially (Cannon et al., 1997), so most of the area of a large hyperbolic disk lies near its boundary. Böröczky (1978) proved density bounds for packings in spaces of constant curvature, where the definition of density is itself delicate. Computational methods for packing include energy minimization, Monte Carlo and annealing methods (Kirkpatrick et al., 1983; Metropolis et al., 1953), and compression of growing disks (Lubachevsky & Stillinger, 1990).")
    HD("Research Gap and Contribution", 2)
    d.body("Established knowledge in this area includes the optimal Tammes configurations listed above, the area formulas of the three plane geometries, and the existence of the three families of methods. I did not find a study that runs several of these methods on the sphere, the Euclidean plane, and the hyperbolic plane under one shared protocol with an equal budget and paired seeds. The contribution of this project is that comparison: three simple optimizers, one bounded disk-packing problem posed identically in geodesic balls of curvature +1, 0, and \u22121, the Tammes problem on the whole sphere, validation against closed-form and published values, and a full report of failures. The study proves no theorem and sets no packing record.")
    HD("Research Questions and Hypotheses", 2)
    d.body(f"RQ1: under an equal budget, which algorithm reaches the best packings in each problem? RQ2: how does performance change with the number of points or disks? RQ3: for numbers of points with a proven optimum, how often does each algorithm recover it within a stated tolerance? RQ4 (exploratory): when the same bounded-disk problem is solved in spaces of curvature +1, 0, and −1, does the ranking of the algorithms change? Three hypotheses were stated in the Research Plan, and {Tb('hyp')} gives each one with its measurable decision rule and its result. Because the plan was finalized after some results had been seen (see Deviations From the Research Plan), every hypothesis result is reported as exploratory. RQ4 and H1 are exploratory in a stronger sense: curvature and area are confounded, because a ball of the same radius has a different area in each space; only six settings per space were run; and the ball of radius 3 on the sphere covers nearly the whole sphere. H1 therefore refers to the space, not to curvature alone.")

    R3 = json.load(open(CONFDIR + "/round3_decisions.json"))
    import conf_figures as _CF
    _mrk = pd.read_csv(f"{DATA}/conf_mean_ranks.csv", index_col=0)
    _conds = {c["cid"]: c for c in _C.conditions()}
    _rk = DEC["C4"]["mean_rank_by_method"]
    HD("Main Results at a Glance", 1)
    d.body(f"Four results carry the paper, and the rest of the text supports them. First, the ranking of the methods: across the {DEC['C4']['n_conditions']} conditions of the preregistered confirmatory round, polished gradient descent had the best mean rank ({f(_rk['gdp'], 2)}), followed by L-BFGS-B ({f(_rk['lbfgsb'], 2)}), basin hopping ({f(_rk['bh'], 2)}), simulated annealing ({f(_rk['sa'], 2)}), gradient descent ({f(_rk['gd'], 2)}), and the simplified compression method ({f(_rk['ls'], 2)}); the better of L-BFGS-B and basin hopping beat both gradient descent and simulated annealing in all {DEC['C4']['n_conditions']} conditions ({Fg('rank')}). "
           f"Second, the boundary: the share by which a packing falls short of the upper bound on the density rises with the share of the ball&rsquo;s area near its wall, in all three spaces (Spearman {f(DEC['C1']['spearman'], 2, lead=False)} in the confirmatory round, a test that is partly circular, and {f(json.load(open(CONFDIR + '/followup_decisions.json'))['primary']['F1']['spearman'], 2, lead=False)} at a fixed disk radius in a follow-up). "
           f"Third, curvature: in a final preregistered round of {R3['A1']['n_conditions']} equal-area conditions, once the boundary share is in the model the hyperbolic disk differed from the Euclidean disk by {f(R3['A1']['g_H'], 3)} (95% interval {f(R3['A1']['g_H_ci'][0], 3)} to {f(R3['A1']['g_H_ci'][1], 3)}) and the cap by {f(R3['A1']['g_S'], 3)}, so no curvature effect larger than .02 of the upper bound was found, where three earlier rounds had been inconclusive. "
           f"Fourth, a rule: the number of disks of a given radius that fit in a ball is predicted by the number at the upper bound times (1 &minus; 0.46 times the boundary share), within one disk in {f(R3['B1']['share_within_1'] * 100, 0)}% of {R3['B1']['n_conditions']} new conditions.".replace("&rsquo;", "’").replace("&minus;", "−"))
    d.body("Two cautions apply to all four. The results hold for the budgets, implementations, and sizes tested (the rule for the number of disks was tested only for balls of at most 46 disks), and no packing found is claimed to be optimal. The first study, which preceded these rounds and is exploratory, is reported in the Findings; the mini-round, the follow-up, and a decision that was withdrawn are in Appendix B.")
    FF("figure", "rank", "Mean Rank of the Six Methods in the 33 Conditions of the Confirmatory Round", _CF.fig_rank(_mrk, _conds), 4.7,
       "Polished gradient descent has the best mean rank over the 33 conditions and the best or second-best rank in most of them; compression has the worst mean rank in almost every condition.",
       "Each cell is the mean rank (1 = best, 6 = worst) of the method within seeds at 1,500 sweeps, over 20 seeds; darker blue = better rank. Columns are ordered by mean rank over all conditions (bottom row, in bold). GD = gradient descent; GD+P = GD with a polishing step; SA = simulated annealing; CP = compression.",
       "Heat map of the mean rank of six methods in 33 conditions, with the mean over conditions in the bottom row.")
    FDEC = json.load(open(CONFDIR + "/followup_decisions.json"))
    MDEC = json.load(open(CONFDIR + "/mini_decisions.json"))
    _hs = open(CONFDIR + "/PREREGISTRATION.sha256").read().split()
    _ad = open(CONFDIR + "/PREREG_ADDENDA.sha256").read().split("\n")
    _fu = open(CONFDIR + "/FOLLOWUP.sha256").read().split("\n")
    _u = lambda t: t.replace("T", " ")[:16] + " UTC"
    _r3h = open(CONFDIR + "/ROUND3.sha256").read().split("\n")[1].split(": ")[1]
    d.body(f"The study has six stages, which {Tb('stages')} lists in order so that the findings in the following pages can be placed. Only the stages with a hash were written before their runs, and all hashes were recorded by the author.")
    FF("table", "stages", "Stages of the Study", ["Stage", "Purpose and data", "Preregistered", "Main result"],
       [["First study", f"Three methods (gradient descent, simulated annealing, compression) in {NCOND} conditions on the sphere, the Euclidean disk, the hyperbolic disk, and the spherical cap; seeds 1 to 30; {NRUN:,} runs.", "No. The plan was finalized after results had been seen, so every result is exploratory.",
         f"Simulated annealing had the best mean rank on the sphere, in the cap, and in the Euclidean disk, and gradient descent in the hyperbolic disk; compression was last; no dependence on the space after correction (Holm-adjusted {pstr(H1c_gdsa.p_holm)})."],
        ["Confirmatory round", f"Six methods, three budgets, 33 conditions including equal-area balls; seeds 101 to 120; {DEC['n_runs']:,} runs.", f"Yes; hash recorded {_u(_hs[-1])}, before the pilot tuning and every evaluation run.",
         f"Polished gradient descent had the best mean rank ({f(DEC['C4']['mean_rank_by_method']['gdp'], 2)}); the added baselines beat gradient descent and annealing; the deficit followed the boundary share (Spearman {f(DEC['C1']['spearman'], 2, lead=False)}); curvature was inconclusive; no method recovered every proven optimum."],
        ["Addendum", "Changes decided after seeing the confirmatory results: Packomania references, wider tuning ranges for two methods and a rerun, saved configurations, wall analysis, wording of the reference density.", f"Written and hashed {_u(_ad[-2].split(": ")[1])} before the runs it describes; it adds no hypothesis.", "No decision changed; compression moved inside its tuning range, and L-BFGS-B stayed at the edge."],
        ["Mini-round (Appendix B)", "Fixed disk radius and matched boundary share, 18 conditions (15 distinct), polished gradient descent; seeds 301 to 320.", f"Yes; hash recorded {_u(_ad[-2].split(": ")[1])}, before its runs.", f"M1 {MDEC['M1']['decision']}; M2 computed as \u201c{MDEC['M2']['decision']}\u201d, a decision withdrawn because 3 of the 18 conditions duplicated others (inconclusive without them, post hoc); M3 {MDEC['M3']['decision']}."],
        ["Follow-up (Appendix B)", "Five boundary shares, three radii, 33 distinct conditions, two methods; seeds 401 to 420.", f"Yes; hash recorded {_u(_fu[1].split(': ')[1])}, before its runs.", f"F1 {FDEC['primary']['F1']['decision']}; F2 {FDEC['primary']['F2']['decision']}; F3 {FDEC['primary']['F3']['decision']}."],
        ["Final round", f"Equal-area balls ({R3['A1']['n_conditions']} conditions, 48 area-by-count cells, seeds 501 to 520) and a count rule at fixed radius (20 conditions, seeds 601 to 620); two methods.", f"Yes; hash recorded {_u(_r3h)}, before its runs (06:42 to 06:52 UTC on October 31).", f"No curvature effect larger than .02 (hyperbolic {f(R3['A1']['g_H'], 3)}, cap {f(R3['A1']['g_S'], 3)}); the rule for the number of disks {R3['B1']['decision']}."]],
       "The confirmatory round and the final round have their own sections; the addendum, mini-round, and follow-up, and a decision that was withdrawn, are in Appendix B. Hashes are SHA-256 values recorded by the author (see the section on the Confirmatory Round for what they do and do not show). UTC = Coordinated Universal Time.",
       aligns=["l", "l", "l", "l"], widths=[1.0, 2.1, 1.6, 1.8], split=True)

    # ====================================================================== Framework
    HD("Framework", 1)
    d.body(f"{Fg('framework')} is a conceptual illustration of the study design; it shows no data. The study moves from the research problem to the geometric spaces and the definitions of distance and score, then to the three algorithms and their implementation. The implementation is accepted only if the unit tests pass; otherwise it is corrected and retested. Passing code is run in repeated trials with fixed seeds, the trials are summarized by performance measures, and the measures are analyzed statistically to evaluate the hypotheses. This section defines the geometry, the problems and their comparability, the experimental design, the algorithms, and the validation, statistical, and reproducibility procedures.")
    FF("figure", "framework", "Framework of the Study", f"{FIG}/framework.png", 4.2,
       "Conceptual illustration of the study design (no experimental data). Rectangles are processes, rounded rectangles are inputs and outputs, and the diamond is a decision. If any unit test fails, the implementation is corrected and retested before trials begin.",
       "", "Flowchart from the research problem through geometric spaces, distance definitions, algorithms, implementation, unit tests, a pass-or-fail decision, repeated trials, performance measures, statistical analysis, and findings.")
    HD("Geometry of the Spaces", 2)
    d.body("The unit sphere <i>S</i><sup>2</sup> has curvature +1. Its points are unit vectors <b><i>x</i></b> in <i>R</i><sup>3</sup>, and the geodesic distance is given by Equation 1. The hyperbolic plane <i>H</i><sup>2</sup> has curvature \u22121. Computations use the hyperboloid model, where a point is <b><i>x</i></b> = (<i>x</i><sub>0</sub>, <i>x</i><sub>1</sub>, <i>x</i><sub>2</sub>) with <i>x</i><sub>0</sub> > 0 and Lorentz product [<b><i>x</i></b>, <b><i>y</i></b>] = \u2212<i>x</i><sub>0</sub><i>y</i><sub>0</sub> + <i>x</i><sub>1</sub><i>y</i><sub>1</sub> + <i>x</i><sub>2</sub><i>y</i><sub>2</sub> = \u22121 for <b><i>y</i></b> = <b><i>x</i></b>, and figures use the Poincaré disk. The Euclidean plane <i>R</i><sup>2</sup> has the usual distance.")
    d.equation("cos <i>d</i> = <b><i>x</i></b> \u00b7 <b><i>y</i></b>", 1)
    d.equation("cosh <i>d</i> = \u2212[<b><i>x</i></b>, <b><i>y</i></b>]", 2)
    d.body("The Poincaré disk coordinate of a hyperboloid point is <i>z</i> = (<i>x</i><sub>1</sub> + <i>i</i> <i>x</i><sub>2</sub>)/(1 + <i>x</i><sub>0</sub>), and the distance between disk points <i>z</i> and <i>w</i> is given by Equation 3. A hyperbolic ball of radius <i>R</i> centered at the origin is the Euclidean circle of radius tanh(<i>R</i>/2).")
    d.equation("cosh <i>d</i> = 1 + 2|<i>z</i> \u2212 <i>w</i>|<sup>2</sup> / [(1 \u2212 |<i>z</i>|<sup>2</sup>)(1 \u2212 |<i>w</i>|<sup>2</sup>)]", 3)
    FL()
    d.body("<i>Proof sketch that Equations 2 and 3 agree.</i> The inverse of the coordinate map is <i>x</i><sub>0</sub> = (1 + |<i>z</i>|<sup>2</sup>)/(1 \u2212 |<i>z</i>|<sup>2</sup>) and (<i>x</i><sub>1</sub>, <i>x</i><sub>2</sub>) = 2<i>z</i>/(1 \u2212 |<i>z</i>|<sup>2</sup>). Substituting into \u2212[<b><i>x</i></b>, <b><i>y</i></b>], where <i>w</i><sup>*</sup> is the complex conjugate of <i>w</i>, gives [(1 + |<i>z</i>|<sup>2</sup>)(1 + |<i>w</i>|<sup>2</sup>) \u2212 4 Re(<i>z</i> <i>w</i><sup>*</sup>)] / [(1 \u2212 |<i>z</i>|<sup>2</sup>)(1 \u2212 |<i>w</i>|<sup>2</sup>)]. The right side of Equation 3 has the same value, because (1 \u2212 |<i>z</i>|<sup>2</sup>)(1 \u2212 |<i>w</i>|<sup>2</sup>) + 2|<i>z</i> \u2212 <i>w</i>|<sup>2</sup> = (1 + |<i>z</i>|<sup>2</sup>)(1 + |<i>w</i>|<sup>2</sup>) \u2212 4 Re(<i>z</i> <i>w</i><sup>*</sup>). The disk areas follow from the area elements sin <i>\u03c1</i> d<i>\u03c1</i> d<i>\u03b8</i>, <i>\u03c1</i> d<i>\u03c1</i> d<i>\u03b8</i>, and sinh <i>\u03c1</i> d<i>\u03c1</i> d<i>\u03b8</i>, and are given by Equation 4.")
    d.equation("Area(<i>r</i>) = 2\u03c0(1 \u2212 cos <i>r</i>) on <i>S</i><sup>2</sup>;  \u03c0<i>r</i><sup>2</sup> on <i>R</i><sup>2</sup>;  2\u03c0(cosh <i>r</i> \u2212 1) on <i>H</i><sup>2</sup>", 4)
    d.body(f"{Tb('area')} gives the area of a ball of radius <i>R</i> and the share of it that lies within distance 1 of its boundary, computed from Equation 4 and stored in area_fractions.csv. In the Euclidean plane this share shrinks toward zero as <i>R</i> grows, but in the hyperbolic plane it tends to 1 \u2212 <i>e</i><sup>\u22121</sup>, which is .632 to three decimals. On the sphere a ball can have radius at most \u03c0, so the table has no spherical entries for larger <i>R</i>. Density is therefore always reported relative to the area of the container.")
    arows = []
    for r in area[area.R.isin([2.0, 3.0, 6.0])].itertuples():
        sph = ("\u2014", "\u2014") if np.isnan(r.spherical_area) else (f(r.spherical_area, 2), f(r.spherical_fraction_within_1_of_boundary, 3, lead=False))
        arows.append([f"{r.R:g}", sph[0], sph[1], f(r.euclidean_area, 2), f(r.euclidean_fraction_within_1_of_boundary, 3, lead=False), f(r.hyperbolic_area, 2), f(r.hyperbolic_fraction_within_1_of_boundary, 3, lead=False)])
    FF("table", "area", "Area Within Distance 1 of the Boundary of a Ball of Radius R",
       ["<i>R</i>", "<i>S</i><sup>2</sup> area", "<i>S</i><sup>2</sup> share", "<i>R</i><sup>2</sup> area", "<i>R</i><sup>2</sup> share", "<i>H</i><sup>2</sup> area", "<i>H</i><sup>2</sup> share"], arows,
       "",
       aligns=["c"] * 7, widths=[0.5, 1.0, 1.0, 0.95, 0.95, 1.05, 1.05])

    HD("Packing Problems and Comparability", 2)
    d.body(f"Problem A is the Tammes problem on <i>S</i><sup>2</sup>: place <i>N</i> points to maximize the smallest pairwise distance. Problem B places <i>n</i> equal disks in a closed geodesic ball of radius <i>R</i> about a fixed center, in each of the three spaces (a spherical cap, a Euclidean disk, and a hyperbolic disk), and maximizes the common radius <i>r</i>. A disk of radius <i>r</i> whose center is at distance <i>\u03c1</i><sub><i>i</i></sub> from the center of the ball lies inside the ball when <i>\u03c1</i><sub><i>i</i></sub> \u2264 <i>R</i> \u2212 <i>r</i>, and two disks do not overlap when <i>d</i><sub><i>ij</i></sub> \u2265 2<i>r</i>. Both problems maximize <i>\u2113</i><sub>min</sub> in Equation 5, where the second term is absent for Problem A; the score is <i>\u2113</i><sub>min</sub> for Problem A and <i>r</i> = <i>\u2113</i><sub>min</sub>/2 for Problem B. Packing density in Problem B is <i>n</i> Area(<i>r</i>)/Area(<i>R</i>) from Equation 4.")
    d.equation("<i>\u2113</i><sub>min</sub> = min{ min<sub><i>i</i> < <i>j</i></sub> <i>d</i><sub><i>ij</i></sub>, min<sub><i>i</i></sub> 2(<i>R</i> \u2212 <i>\u03c1</i><sub><i>i</i></sub>) }", 5)
    d.body(f"Problem B fixes <i>n</i> and <i>R</i> and maximizes <i>r</i>, which gives a continuous score that all three algorithms can improve smoothly; the number of disks of a fixed radius that fit is derived from it. The comparability of the problems is limited, and the limits shape every conclusion. Problems A and B differ in objective (a minimum distance against a common radius), in constraints (no boundary against a boundary), and in scale, so no result of Problem A is compared with a result of Problem B. Statements about curvature rest on Problem B alone, which has the same formulation, the same <i>R</i> and <i>n</i>, and the same code in all three spaces. Even there, a ball of radius <i>R</i> has a different area in each space ({Tb('area')}), so a difference between spaces can come from curvature, from area, or from both, and this study does not separate them. A comparison at equal area is a different design; a supplementary one was run after the main study and is reported separately as exploratory (see Supplementary Exploratory Analyses), and it is not part of the hypothesis tests.")

    HD("Experimental Design", 2)
    d.body(f"Problem A uses <i>N</i> = {', '.join(str(int(n)) for n in NS2[:-1])}, and {int(NS2[-1])}. Problem B uses the six settings (<i>R</i>, <i>n</i>) = {', '.join(f'({r:g}, {n})' for r, n in BALL)} in each of the three spaces. The evaluation seeds are 1 to {SEEDS}. The initial configuration depends only on the seed and the condition, so the three algorithms start from the same configuration, and initial points are uniform on <i>S</i><sup>2</sup> for Problem A and uniform by area in the ball of radius <i>R</i> \u2212 0.05 for Problem B. Pilot runs for parameter tuning used seeds 9001 to 9004 only, which never appear in the evaluation. The total is {NRUN:,} runs.")
    ntam = len(NS2) * SEEDS * 3
    nb = len(BALL) * SEEDS * 3
    d.body(f"The Tammes problem accounts for {ntam:,} runs ({len(NS2)} values of <i>N</i> \u00d7 {SEEDS} seeds \u00d7 3 algorithms), and each of the three spaces accounts for {nb:,} runs in Problem B ({len(BALL)} settings \u00d7 {SEEDS} seeds \u00d7 3 algorithms).")
    d.body(f"Every run receives a budget of {BUDGET:,} sweeps, where one sweep is the <i>n</i>(<i>n</i> \u2212 1)/2 pair-distance evaluations needed to compute all distances once. A gradient step costs one sweep plus one sweep per line-search trial (in Problem B each evaluation also includes the <i>n</i> wall clearances), a simulated-annealing move costs <i>n</i> \u2212 1 evaluations, and a compression step costs two sweeps. Counting evaluations keeps the comparison independent of implementation speed. Gradient descent and compression stop when their next step would exceed the budget. Simulated annealing fixes its number of moves from the budget in advance and does not charge proposals rejected for lying outside the ball, so in the ball problems it used slightly less than the budget (at least {runs[runs.algorithm == 'sa'].sweeps_used.min():,.0f} of {BUDGET:,} sweeps in every run); this can only disadvantage annealing. Every run reports the best configuration it visited, scored exactly from its coordinates.")
    d.body(f"The reference value of a condition is the proven optimum for Problem A with <i>N</i> = 4 to 14 and 24 (credited to Fejes Tóth, 1943; Schütte & van der Waerden, 1951; Robinson, 1961; Danzer, 1963; and Musin & Tarasov, 2012, 2015; the values for <i>N</i> = 4, 6, and 12 were also derived in closed form); for the other values of <i>N</i> it is the published best-known value where one was entered ({KNOWN_TXT}) and otherwise the highest score found by any run in that condition. A best-known value is not proven optimal, and a best-found value is a computational result, so relative scores near 1 mean agreement with that reference, not optimality. The published best-known values for <i>N</i> = 30, 40, and 60 replaced the best values found after the main results were seen (see Deviations From the Research Plan). The relative score of a run is its score divided by the reference value. A run succeeds when its relative score is at least .999, and a 1% tolerance (at least .99) is a sensitivity check. Convergence is the number of sweeps after which the best score first reached 99% of the run\u2019s own final score. Scaling is the per-seed slope of relative score on log<sub>10</sub> <i>N</i> for <i>N</i> \u2265 13 and the log\u2013log slope of mean run time on <i>N</i>. Cost is the wall-clock time, reported descriptively because the budget is fixed in distance evaluations.")

    HD("Optimization Algorithms", 2)
    d.body(f"All three algorithms move points along geodesics and keep points on the manifold. {Tb('params')} gives every parameter.")
    FF("table", "params", "Algorithm Parameters", ["Algorithm and parameter", "Value"],
       [["GD: energy, exponent", f"<i>E<sub>p</sub></i> of Equation 6 over pair distances and, in Problem B, doubled wall clearances; <i>p</i> from {dflt['gd']['p0']:g} to {dflt['gd']['pmax']:g}, geometric in the share of budget used"],
        ["GD: step, line search", "<i>\u03b7</i> = min(<i>m</i> \u2113<sub>min</sub><sup>2</sup>/<i>p</i>, 0.25 \u2113<sub>min</sub>/max|<i>g</i>|); <i>m</i> starts at 0.5, \u00d7 1.3 after success (maximum 2), \u00d7 0.5 after failure (minimum 0.001); on failure multiply <i>\u03b7</i> by 0.4, at most 5 trials"],
        ["SA: temperature", f"Geometric from {dflt['sa']['T0f']:g} to {p10(dflt['sa']['T1f'])} times the length scale \u221a(area/<i>n</i>)"],
        ["SA: move, adaptation", "Random geodesic step of length \u03b4(0.1 + 0.9<i>u</i>), <i>u</i> uniform on (0, 1); \u03b4 starts at 0.3 times the length scale; every 100 proposals \u03b4 \u00d7 1.15 if acceptance > .40, \u00d7 0.87 if < .25"],
        ["SA: point choice", f"Probability {dflt['sa']['focus']:g}: an endpoint of the limiting pair or the point nearest the wall; otherwise uniform"],
        ["CP: time step, growth", f"Time step {dflt['ls']['dt_f']:g} times the length scale at unit root-mean-square speed; common radius grows by \u03b3 d<i>t</i> per step, \u03b3 falling linearly from {dflt['ls']['g0']:g} to {dflt['ls']['g1']:g}, capped by half the smallest distance"],
        ["CP: collisions", "Velocity components along the line of centers exchanged if approaching; overlaps removed; wall reflection in Problem B; kinetic energy renormalized each step"]],
       "GD = gradient descent; SA = simulated annealing; CP = compression. The length scale is \u221a(area/<i>n</i>). Defaults are read from algorithms.py.",
       aligns=["l", "l"], widths=[1.6, 4.9])
    FL()
    d.body("The parameter values were chosen on pilot seeds 9001 to 9004 at the same budget in four pilot conditions (Tammes <i>N</i> = 13 and 30, hyperbolic disk (<i>R</i>, <i>n</i>) = (2, 12), Euclidean disk (3, 19)) from grids of 11 settings for gradient descent, 4 for annealing, and 10 for compression, ranked by mean score. The gradient-descent and annealing settings used are grid points; the compression setting lies between grid points and was set by inspection. The spherical-cap family was not used for tuning, and the parameters were not changed for it. All values were fixed before the evaluation.")
    HD("Gradient Descent on a Soft-Minimum Energy", 3)
    d.body(f"Let <i>\u2113</i><sub>1</sub>, \u2026, <i>\u2113</i><sub><i>m</i></sub> be the pair distances and, in Problem B, the doubled wall clearances 2(<i>R</i> \u2212 <i>\u03c1</i><sub><i>i</i></sub>). The energy in Equation 6 is a smooth stand-in for \u2212ln <i>\u2113</i><sub>min</sub>. It satisfies the bound in Equation 7, because the sum lies between its largest term and <i>m</i> times that term. The exponent <i>p</i> grows geometrically from {dflt['gd']['p0']:g} to {dflt['gd']['pmax']:g} over the budget, and each step follows the negative Riemannian gradient with backtracking.")
    d.equation("<i>E<sub>p</sub></i> = (1/<i>p</i>) ln \u03a3<sub><i>k</i></sub> <i>\u2113<sub>k</sub></i><sup>\u2212<i>p</i></sup>", 6)
    d.equation("\u2212ln <i>\u2113</i><sub>min</sub> \u2264 <i>E<sub>p</sub></i> \u2264 \u2212ln <i>\u2113</i><sub>min</sub> + (ln <i>m</i>)/<i>p</i>", 7)
    HD("Simulated Annealing", 3)
    d.body(f"Simulated annealing moves one point at a time by a random geodesic step and accepts the move by the Metropolis rule (Metropolis et al., 1953) applied to \u2212<i>\u2113</i><sub>min</sub>, with a geometric cooling schedule (Kirkpatrick et al., 1983). With probability {dflt['sa']['focus']:g} the point chosen is one that currently limits <i>\u2113</i><sub>min</sub>. Because of this focused choice and the nonuniform step distribution, the method is an optimizer, not a sampler of the Boltzmann distribution.")
    HD("Compression Method", 3)
    d.body("The compression method follows the idea of Lubachevsky and Stillinger (1990) in a simplified, time-stepped form, not an event-driven one. Points move with random initial velocities; overlapping disks exchange the velocity components along the line of centers and are pushed apart; the common radius grows at a rate that falls linearly over the budget, limited by the room available. Because contacts are resolved only at the end of each time step, the scheme is approximate, which limits its final precision.")
    HD("Properties of the Algorithms: Proven and Observed", 2)
    d.body("This subsection separates what is mathematically established from what this study only observed. Nothing below is a guarantee that an algorithm finds a globally optimal packing, and the empirical statements are given in the Findings, not here.")
    d.body("<i>Gradient descent.</i> Proven here: Equation 7 holds because <i>\u2113</i><sub>min</sub><sup>\u2212<i>p</i></sup> \u2264 \u03a3<sub><i>k</i></sub> <i>\u2113<sub>k</sub></i><sup>\u2212<i>p</i></sup> \u2264 <i>m</i> <i>\u2113</i><sub>min</sub><sup>\u2212<i>p</i></sup>, so the energy approaches \u2212ln <i>\u2113</i><sub>min</sub> as <i>p</i> grows, with an error of at most (ln <i>m</i>)/<i>p</i>. Not established: the energy is not convex, so a stationary point can be a local optimum or a saddle; the exponent <i>p</i> changes at every step, so the energy does not decrease monotonically over a run; and the standard convergence theory for Riemannian gradient methods with a backtracking line search (Absil et al., 2008) concerns a fixed smooth objective, so it does not cover this schedule. The true objective <i>\u2113</i><sub>min</sub> is not differentiable where distances tie, and its maxima are rigid configurations with many contacts. No theorem is claimed that gradient descent reaches a stationary point of <i>\u2113</i><sub>min</sub> or a global maximum.")
    d.body("<i>Simulated annealing.</i> Proven for finite-state Markov chains (Hajek, 1988): the probability of being at a global optimum tends to 1 under a logarithmic cooling schedule <i>T</i><sub><i>k</i></sub> = <i>c</i>/ln(<i>k</i> + 1) if and only if <i>c</i> is at least the depth of the deepest local minimum that is not global. Not applicable here: the state space is continuous, the cooling is geometric over a fixed number of moves, the step size adapts, and 30% of the moves target the limiting pair. The method is therefore a heuristic optimizer without a convergence guarantee in this study, and its final configuration is not a sample from a known distribution.")
    d.body("<i>Compression.</i> The method of Lubachevsky and Stillinger (1990) is an event-driven simulation of disks whose radii grow, and this study uses a simplified time-stepped version that resolves contacts only at the end of each step. No theorem guaranteeing convergence of either version to a densest packing is known to me, and none is claimed. Because contacts are resolved at the end of each step, positions are accurate only to about the distance a disk moves in one step, which is a plausible reason for the lower final precision of this implementation; this explanation was not tested separately.")
    d.body(f"<i>Stopping and numerical precision.</i> All three methods use the same stopping rule, a fixed budget of pair-distance evaluations with no early stopping, so differences in the final score are not caused by different stopping criteria; the exception, unused budget in simulated annealing near the wall, is described under Experimental Design. Because the budget is fixed, the results describe performance at that budget and not convergence to a limit ({Fg('conv')} shows how the best score rose during the budget). Distances use arcsine and arcsinh forms that stay accurate for small distances; floating-point error is examined in the Findings.")
    HD("Validation Procedures", 2)
    d.body(f"Unit tests checked the geometry and the code before the experiments: the 23 tests of the sphere, hyperbolic, Euclidean, and optimizer code passed before the first 27 conditions were run, and the 6 spherical-cap tests passed before the cap conditions were run. The test log in this paper is the complete run of all 29 tests with the final code, and three of the first 27 conditions (Tammes <i>N</i> = 13, hyperbolic disk (2, 12), Euclidean disk (2, 7)) were rerun with the final code and reproduced every score exactly. {Tb('vtests')} states how each group of tests is performed and what counts as passing; a single failure in any group would have blocked the experiments. The test for recovery of known optima requires the best of the three optimizers on five test seeds (9101 to 9105), because recovery by each optimizer is hypothesis H3 and not a validation criterion.")
    HD("Statistical Analysis", 2)
    d.body(f"For each condition the observations are the {SEEDS} final scores of each algorithm. Scores of the same seed come from the same starting configuration and form a block. The Friedman test compares the three algorithms across the {SEEDS} blocks, and the Wilcoxon signed-rank test (Wilcoxon, 1945) compares each pair on the {SEEDS} within-seed differences. Nonparametric paired tests are used because scores are bounded, are tied or clustered at local optima, and are not normally distributed. Effect sizes are Kendall\u2019s <i>W</i> for the Friedman test and the matched-pairs rank-biserial correlation (<i>r</i><sub>rb</sub>) with the standardized mean difference (<i>d<sub>z</sub></i>) for pairs. Means carry 95% confidence intervals based on the <i>t</i> distribution, which are approximate for non-normal scores and used descriptively.")
    d.body("The tests assume independent blocks, which holds because each seed gives an independent random start. The Wilcoxon test also assumes that the paired differences are symmetric about their median. This was checked through the skewness of each set of differences (an absolute value above 1 is flagged) and the share of zero differences, which are stored in assumption_checks.csv. Tests were corrected with the Holm procedure (Holm, 1979), taking as one family all tests of the same kind within one space; hypothesis tests are corrected across their own pairs. A result is statistically significant when the Holm-adjusted <i>p</i> is below .05. Practical importance is judged separately: a difference is practically important when its mean is at least 0.5% of the reference value. This threshold and the assumption checks were formalized after the first 27 conditions had been run. The Friedman test assumes independent blocks whose scores can be ranked; ties are corrected by the implementation, and with three algorithms and 30 blocks the chi-square approximation is generally considered adequate. The Wilcoxon test discards zero differences and uses an exact <i>p</i> value only when there are no ties or zeros (otherwise the normal approximation of the implementation). The rank-biserial correlation and <i>d</i><sub><i>z</i></sub> describe the size of a paired difference, and the intervals are <i>t</i> intervals of the mean, checked against bootstrap intervals for two headline differences (see Supplementary Exploratory Analyses). Holm\u2019s procedure controls the familywise error rate without assuming that the tests are independent (Holm, 1979), which matters because all tests in one space share the same 30 seeds.")
    HD("Reproducibility and Data Integrity", 2)
    files = sorted(f_ for f_ in os.listdir(DATA) if f_.endswith(".csv"))
    d.body(f"All code is in Code_Listing.docx and, as source files, in the code folder of CSV_Data.zip. The reported runs used Python 3.12.3 with numpy 2.4.4, scipy 1.17.1, pandas 3.0.2, and matplotlib 3.10.8; an independent full rerun (python3 build_all.py --rerun) under Python 3.13.18 with numpy 2.5.3, scipy 1.18.1, pandas 3.0.5, and matplotlib 3.11.2 reproduced every score, test statistic, and p-value in the CSV files exactly; only the wall-clock times differ. The command python3 tests.py runs the validation tests, and python3 build_all.py runs the tests, all experiments, the statistics, the figures, and the building of every document; adding --rerun recomputes every run, which took {runs.time_s.sum() / 60:.0f} minutes of run time on one core in the run reported here. Seeds are fixed (evaluation seeds 1 to {SEEDS}, pilot seeds 9001 to 9004, test seeds 9101 to 9105), so a rerun reproduces every value. CSV_Data.zip holds {len(files)} CSV files (among them runs_raw.csv with all {NRUN:,} runs, configurations.csv with every final configuration, and convergence_traces.csv), unit_test_output.txt, README.md, which defines every column of every file, and MANIFEST.sha256, whose SHA-256 hashes can be checked with sha256sum. Every table and figure note names the file from which its values were computed. No run was excluded: all {NRUN:,} runs are in the data, including failures such as the {stuck} of {SEEDS} seeds in which gradient descent stalled for <i>N</i> = 4 (see Conclusions). The forms required by the competition are submitted separately and are not reproduced here.")
    HD("Deviations From the Research Plan", 2)
    d.body("The Research Plan was finalized after the results of all 33 conditions had been seen (see Appendix A of the Research Plan), so the hypotheses and decision rules are not strictly pre-registered. Its Appendix A, History of Work Done, lists the changes, which are summarized here. First, the compression method was implemented as a time-stepped scheme, not an event-driven one. Second, the spherical-cap condition family was added after the results of the other 27 conditions had been seen, to obtain a common formulation across curvatures; its analysis was written into the code before the cap runs were executed, but the resulting evaluation of H1 is exploratory with respect to the earlier results. Third, the practical-importance threshold and the assumption checks were formalized after the first 27 conditions had been run. Fourth, the validation criterion for optimizer recovery was changed to the best of three optimizers after compression failed an earlier per-optimizer version. Pilot tuning and the validation tests preceded the main runs they support (see Validation Procedures); the data package contains no dated log of when each run was executed. After the main results had been seen, five further changes were made, all recorded in the plan: the references for <i>N</i> = 30, 40, and 60 were replaced by published best-known values (they had been the best values found, which changed the relative scores for those values of <i>N</i> and therefore the scaling slopes); the citations of the proven optima were corrected; the result of every hypothesis is labeled exploratory; the supplementary analyses and a polished gradient-descent variant were added; and a statement on AI assistance was added. None of them changes a run, a seed, a parameter, or a decision rule of the main study. The Confirmatory Round was added after all of these, with its own preregistration, hashed before its pilot tuning and before every evaluation run; it did not change any result of the first study. After the results of the Confirmatory Round had been seen, the following were added, each listed in a second preregistration file and in the section on the Confirmatory Round: Packomania reference values for the Euclidean conditions (entered after the first analysis of the round; the decisions were the same with both references), extended tuning ranges and a re-run of compression and L-BFGS-B, the saved final configurations with the wall analysis, a correction of the wording of the reference density, and a mini-round with a fixed radius and a matched boundary share, whose own preregistration was hashed before its runs. A withdrawn mini-round decision, a follow-up, and a final round followed; the final round was preregistered, its rules were written in the Research Plan before the paper, and its runs followed the adviser email that the author reports sending. The withdrawal is in Appendix B.")

    # ====================================================================== Findings
    HD("Disclosure of AI Assistance and Researcher\u2019s Contribution", 2)
    d.body("Claude, an AI assistant developed by Anthropic, was used to assist with the writing of this document, including drafting, grammar checking, and language refinement. Other uses of AI assistance in this project, including its use in programming and analysis, are described in the separate AI Disclosure Agreement submitted to the research adviser and the Science Research Committee. GitHub was used to support code management and access to programming resources. The author\u2019s original contributions include the selection of the research problem, the formulation of the research questions, and the decisions regarding the research design. The author personally ran and checked the code, verified the results, and can explain and defend the programming procedures, methods, and findings. The author accepts full responsibility for the accuracy and integrity of every statement, numerical result, citation, and conclusion presented in this research. The code and data are provided to support reproducibility and independent verification of the results.")

    HD("Findings", 1)
    d.body("This section reports the validation of the code, the results on the sphere and in geodesic balls, convergence, scaling and cost, the statistical comparison, and the resolution of the hypotheses. Every value comes from the files named in the table and figure notes.")
    HD("Validation Results", 2)
    gc = table_group_counts()
    tot_n = sum(g[3] for g in gc)
    tot_p = sum(g[4] for g in gc)
    assert tot_n == int(re.search(r"(\d+) of (\d+) tests passed", unit_txt).group(2)) and tot_p == int(re.search(r"(\d+) of (\d+) tests passed", unit_txt).group(1))
    d.body(f"All {tot_p} of {tot_n} unit tests passed ({Tb('vtests')}).")
    FF("table", "vtests", "Validation Tests, Pass Criteria, and Results", ["Test group", "How it is performed", "Pass criterion", "Passed"],
       [[g[0], g[1], g[2], f"{g[4]} of {g[3]}"] for g in gc] + [["Total", "", "", f"{tot_p} of {tot_n}"]],
       "Full output is in unit_test_output.txt. Passed = tests passed of tests run in the group.",
       aligns=["l", "l", "l", "c"], widths=[1.15, 2.35, 2.2, 0.8])

    FL()
    d.body(f"Distances on <i>S</i><sup>2</sup> matched the arctangent form to a maximum error of {sci(test_err('S2 distance matches'))} rad, and distances on <i>H</i><sup>2</sup> matched the Poincaré disk formula to a maximum relative error of {sci(test_err('H2 hyperboloid distance'))}. The analytic gradients matched finite differences, the closed-form tetrahedron, octahedron, and icosahedron gave the Tammes values arccos(\u22121/3), \u03c0/2, and arctan 2 for <i>N</i> = 4, 6, and 12, and the spherical-cap code reproduced the Euclidean limit. These tests show that the geometry code measures distances correctly and that the optimizers move points as the mathematics prescribes; they do not show that any optimizer finds optimal packings.")
    HD("Packing Performance on the Sphere", 2)
    d.body(f"The reference values are stored in benchmark_values.csv with the source of each (in degrees and radians; the radian values are in the Reference column of {Tb('s2res')}); the proofs are credited in the Introduction. {Fg('sphere')} shows the best configuration found for six values of <i>N</i>, and {Tb('s2res')} gives the mean final minimum distance and the success rate for every <i>N</i>.")
    FF("figure", "sphere", "Best Configurations on the Sphere for Six Values of N", f"{FIG}/fig_sphere_configs.png", 5.4,
       "Orthographic view of the best configuration over all algorithms and seeds for <i>N</i> = 12, 13, 14, 24, 30, and 60. Data: configurations.csv.",
       "Points: filled = on the visible hemisphere, open = on the hidden hemisphere. Circles: spherical caps whose angular radius is half the minimum distance of that configuration. Black arcs: great-circle arcs joining points whose distance is within 0.0001 rad of the minimum. Color: algorithm that found the configuration (blue = gradient descent, red = simulated annealing, green = compression).",
       "Six orthographic views of points on a sphere with circles around each point and great-circle arcs joining touching points, for 12, 13, 14, 24, 30, and 60 points.")
    r12 = {a: S("S2", 12, a) for a in ALG}
    r13 = {a: S("S2", 13, a) for a in ALG}
    r60 = {a: S("S2", 60, a) for a in ALG}
    d.body(f"For <i>N</i> = 12, gradient descent and simulated annealing both reached the icosahedral value (<i>M</i> = {f(r12['gd'].mean_score)} and {f(r12['sa'].mean_score)} rad; the optimum is {f(r12['gd'].reference_value)} rad), whereas compression stopped lower (<i>M</i> = {f(r12['ls'].mean_score)}, <i>SD</i> = {f(r12['ls'].sd_score)}). For <i>N</i> = 13, no algorithm reached the proven optimum of {f(r13['gd'].reference_value)} rad on average (gradient descent <i>M</i> = {f(r13['gd'].mean_score)}, simulated annealing {f(r13['sa'].mean_score)}, compression {f(r13['ls'].mean_score)}). For <i>N</i> = 60, simulated annealing led with <i>M</i> = {f(r60['sa'].mean_score)}, ahead of gradient descent ({f(r60['gd'].mean_score)}) and compression ({f(r60['ls'].mean_score)}); there the reference is the best value found, not a proven optimum.")
    from geometry import Space as _Sp
    def contacts(cid):
        g = runs[runs.condition_id == cid].sort_values("score", ascending=False).iloc[0]
        X = cfgall[(cfgall.condition_id == cid) & (cfgall.algorithm == g.algorithm) & (cfgall.seed == g.seed)].sort_values("index")[["x0", "x1", "x2"]].values
        Dm = _Sp("S2").pair_dist(X)
        c = (Dm < g.score + 1e-3)
        np.fill_diagonal(c, False)
        return int(c.sum() // 2), int((c.sum(1) == 0).sum())
    cinfo = {n: contacts(100 + NS2.index(n)) for n in (12, 13, 14, 24, 30, 60)}
    d.body("Counting pairs whose distance is within 0.001 rad of the minimum shows how rigid each displayed configuration is (contacting pairs, points without contact): " + "; ".join(f"<i>N</i> = {n}, {c[0]} pairs and {c[1]} free points" for n, c in cinfo.items()) + ". Free points can move without changing the minimum distance. Free points in the larger configurations (<i>N</i> = 30 and 60) suggest that the search has not reached a jammed packing within the budget; for a small <i>N</i> such as 13, a free point can also belong to an optimal packing.")
    GDNEAR = ", ".join(str(int(n)) for n in NS2 if n <= 14 and S("S2", n, "gd").success_rate_0p1pct == 0 and S("S2", n, "gd").mean_relative >= 0.995)
    SA_ALL = ", ".join(str(int(n)) for n in NS2 if n <= 14 and S("S2", n, "sa").success_rate_0p1pct >= 0.999)
    GD_ALL = ", ".join(str(int(n)) for n in NS2 if n <= 14 and S("S2", n, "gd").success_rate_0p1pct >= 0.999)
    d.body(f"At the 0.1% tolerance, simulated annealing succeeded in all {SEEDS} seeds for <i>N</i> = {SA_ALL}, and gradient descent for <i>N</i> = {GD_ALL}. Gradient descent never met the tolerance for <i>N</i> = {GDNEAR} even though its mean relative scores there were at least .995, which suggests that its final precision, not its search, limits the success rate. Compression met the tolerance in at most {f(max(sc_ls_small.values()) * 100, 0)}% of seeds for <i>N</i> = 4 to 6 and never beyond. For <i>N</i> \u2265 24 no algorithm succeeded in more than {f(max(S('S2', n, a).success_rate_0p1pct for n in NS2 if n >= 24 for a in ALG) * 100, 0)}% of seeds, so the large-<i>N</i> results are comparisons of average quality, not recoveries of optima.")
    rows = []
    for n in NS2:
        row = [str(int(n)), f(S("S2", n, "gd").reference_value) + ("*" if S("S2", n, "gd").reference_type != "verified optimum" else "")]
        for a in ALG:
            s_ = S("S2", n, a)
            row.append(f"{f(s_.mean_score)} ({f(s_.sd_score)})")
        row.append(" / ".join(f"{S('S2', n, a).success_rate_0p1pct * 100:.0f}" for a in ALG))
        rows.append(row)
    FF("table", "s2res", "Final Minimum Distance and Success Rate on the Sphere by Algorithm", ["<i>N</i>", "Reference (rad)", "GD <i>M</i> (<i>SD</i>)", "SA <i>M</i> (<i>SD</i>)", "CP <i>M</i> (<i>SD</i>)", "Success (%) GD / SA / CP"], rows,
       f"Distances in radians over {SEEDS} seeds. Success = percentage of seeds with relative score \u2265 .999. GD = gradient descent; SA = simulated annealing; CP = compression. An asterisk marks a reference that is not proven optimal: {STARNOTE}. Data: summary_by_condition.csv.",
       aligns=["c"] * 6, widths=[0.55, 0.85, 1.1, 1.1, 1.1, 1.8])

    HD("Packing Performance in Geodesic Balls", 2)
    d.body(f"{Fg('curv')} shows the best packing of 19 disks in a ball of radius 3 in each of the three spaces. {Tb('ballres')} reports the mean radius and the packing density for all 18 conditions, and {Tb('capacity')} turns the best radii into a statement about capacity: the largest tested number of disks that fit when the radius must reach a target value. These capacity entries are lower bounds from the tested values of <i>n</i> only.")
    FF("figure", "curv", "Best Packings of 19 Disks in a Ball of Radius 3 in Three Spaces", f"{FIG}/fig_curvature_packing.png", 6.4,
       "Best packing found for <i>R</i> = 3 and <i>n</i> = 19 in each space (best run over all algorithms and seeds), with the resulting radius <i>r</i> in the panel title. The panels use different projections: the spherical cap is shown in azimuthal equidistant projection, where the distance from the center is preserved and shapes are distorted; the Euclidean disk is shown undistorted; the hyperbolic disk is shown in the Poincaré disk, where hyperbolic disks are exact Euclidean circles. Data: configurations.csv.",
       "Shaded regions: disks of radius <i>r</i>. Dots: disk centers. Solid circle: container, a ball of radius 3 (Euclidean radius tanh(3/2) in the Poincaré disk). Dotted circle: boundary at infinity of the Poincaré disk. Color: algorithm that found the packing (blue = gradient descent, red = simulated annealing).",
       "Three panels showing 19 disks in a ball of radius 3: stretched disks in a spherical cap, equal circles in a Euclidean disk, and circles that look smaller toward the edge in a hyperbolic disk.")
    gdh = {sp: runs[(runs.condition_id == (400 if sp == "S2cap" else 300 if sp == "R2" else 200) + 4)].sort_values("score", ascending=False).iloc[0] for sp in SPACES}
    d.body(f"The best radii were {f(gdh['S2cap'].score, 4)} in the cap, {f(gdh['R2'].score, 4)} in the Euclidean disk, and {f(gdh['H2'].score, 4)} in the hyperbolic disk. These radii are not comparable as measures of packing quality, because the balls have different areas; the densities in {Tb('ballres')} are the better guide. In the hyperbolic plane, gradient descent had the highest mean radius in {best_count('H2', 'gd')} of 6 settings and simulated annealing in {best_count('H2', 'sa')}. In the Euclidean disk, simulated annealing had the highest mean radius in {best_count('R2', 'sa')} of 6 and gradient descent in {best_count('R2', 'gd')}. In the cap, simulated annealing had the highest mean radius in {best_count('S2cap', 'sa')} of 6 and gradient descent in {best_count('S2cap', 'gd')}. Compression never had the highest mean radius ({best_count('H2', 'ls') + best_count('R2', 'ls') + best_count('S2cap', 'ls')} of 18 conditions).")
    rows = []
    for sp in SPACES:
        for R, n in BALL:
            c = [S(sp, n, a, R=R) for a in ALG]
            rows.append([SLAB[sp], f"{R:g}", str(n)] + [f"{f(x.mean_score)} ({f(x.sd_score)})" for x in c] + [" / ".join(f"{x.mean_density * 100:.0f}" for x in c)])
    FF("table", "ballres", "Mean Disk Radius and Packing Density in a Ball by Algorithm", ["Space", "<i>R</i>", "<i>n</i>", "GD <i>r</i> (<i>SD</i>)", "SA <i>r</i> (<i>SD</i>)", "CP <i>r</i> (<i>SD</i>)", "Density (%) GD / SA / CP"], rows,
       f"Radius <i>r</i> over {SEEDS} seeds, in the units of the space. Density = percentage of the ball\u2019s area covered by the disks, averaged over seeds. Cap = spherical cap. GD = gradient descent; SA = simulated annealing; CP = compression. Data: summary_by_condition.csv.",
       aligns=["l", "c", "c", "c", "c", "c", "c"], widths=[0.7, 0.4, 0.4, 1.1, 1.1, 1.1, 1.7])
    rows = []
    for sp in SPACES:
        for R in (2.0, 3.0):
            g = caps[(caps.space == sp) & (caps.R == R)].sort_values("target_radius")
            cells = [f"{int(x.largest_tested_n_that_fits)} ({f(x.best_radius_at_that_n)})" if x.largest_tested_n_that_fits > 0 else "none" for x in g.itertuples()]
            rows.append([SLAB[sp], f"{R:g}"] + cells)
    FF("table", "capacity", "Largest Tested Number of Disks That Fit at a Target Radius", ["Space", "<i>R</i>", "<i>r</i> \u2265 0.4", "<i>r</i> \u2265 0.5"], rows,
       "Largest tested <i>n</i> (best radius). Cap = spherical cap. Data: capacity_fixed_radius.csv.",
       aligns=["l", "c", "c", "c"], widths=[1.0, 0.8, 2.35, 2.35])

    HD("Convergence, Scaling, and Cost", 2)
    sw = {a: S("S2", 60, a).mean_sweeps_to_99 for a in ALG}
    d.body(f"Convergence effort is the number of sweeps a run needed to first reach 99% of its own final score ({Tb('sweeps')}). For <i>N</i> = 60 the mean was {sw['gd']:,.0f} sweeps for gradient descent, {sw['sa']:,.0f} for simulated annealing, and {sw['ls']:,.0f} for compression, out of a budget of {BUDGET:,}. A value near the budget means that the run was still improving when the budget ended, so its final score is a lower bound on what a longer run could reach. {Fg('conv')} shows how the best score so far rose with the budget, {Fg('perf')} shows the final relative score for every condition, {Fg('runtime')} shows run time, and {Fg('dist')} shows the spread over seeds.")
    rows = []
    for lab, sp, n, R in (("<i>S</i><sup>2</sup>, <i>N</i> = 60", "S2", 60, None),
                          ("Cap, <i>R</i> = 3, <i>n</i> = 19", "S2cap", 19, 3.0), ("<i>R</i><sup>2</sup>, <i>R</i> = 3, <i>n</i> = 19", "R2", 19, 3.0), ("<i>H</i><sup>2</sup>, <i>R</i> = 3, <i>n</i> = 19", "H2", 19, 3.0)):
        rows.append([lab] + [f"{S(sp, n, a, R=R).mean_sweeps_to_99:,.0f}" for a in ALG])
    FF("table", "sweeps", "Mean Sweeps Needed to Reach 99% of the Final Score", ["Condition", "GD", "SA", "CP"], rows,
       f"Budget = {BUDGET:,} sweeps. Cap = spherical cap. Data: summary_by_condition.csv.",
       aligns=["l", "c", "c", "c"], widths=[2.6, 1.3, 1.3, 1.3])
    lsm = lambda n: S("S2", n, "ls").mean_relative
    d.body(f"On the sphere, gradient descent and simulated annealing had relative scores of at least {f(min(S('S2', n, a).mean_relative for n in NS2 if n <= 12 for a in ('gd', 'sa')), 3, lead=False)} for <i>N</i> \u2264 12, whereas compression first fell below .990 at <i>N</i> = {int(min(n for n in NS2 if lsm(n) < 0.99))} and then declined steadily, reaching a mean of {f(r60['ls'].mean_relative, 2)} of the reference at <i>N</i> = 60, against {f(r60['gd'].mean_relative, 2)} for gradient descent and {f(r60['sa'].mean_relative, 2)} for simulated annealing. Simulated annealing took the longest and its time grew almost linearly with <i>N</i> (log\u2013log slope {f(float(rte[rte.algorithm == 'sa'].time_exponent.iloc[0]), 2)}), because each of its moves costs one row of distances. Gradient descent and compression took much less time (slopes {f(float(rte[rte.algorithm == 'gd'].time_exponent.iloc[0]), 2)} and {f(float(rte[rte.algorithm == 'ls'].time_exponent.iloc[0]), 2)}), because their vectorized steps are dominated by fixed overhead at these sizes; these slopes describe this implementation, not the algorithms in general.")
    FF("figure", "conv", "Convergence of the Best Score During the Budget", f"{FIG}/fig_convergence.png", 4.7,
       f"Mean of the best score so far divided by the reference value, over {SEEDS} seeds, for six conditions. The horizontal axis is logarithmic and the vertical axes do not start at zero. Data: convergence_traces.csv.",
       "Lines: mean of the best score so far (blue solid with circles = gradient descent, red dashed with squares = simulated annealing, green dash-dot with triangles = compression). Shaded bands: 95% confidence intervals over seeds. Dotted line: reference value (1.0). Cap = spherical cap, <i>R</i> = ball radius, <i>n</i> = number of disks, <i>N</i> = number of points.",
       "Six line charts of best score versus fraction of budget for three algorithms.")
    FF("figure", "perf", "Final Relative Score by Condition", f"{FIG}/fig_performance_vs_size.png", 4.4,
       f"Mean relative score over {SEEDS} seeds with 95% confidence intervals. The top panel is the Tammes problem and the other panels are disks in a ball; vertical axes do not start at zero. Data: summary_by_condition.csv.",
       "Markers and lines as in the previous figure (blue circles = gradient descent, red squares = simulated annealing, green triangles = compression). Error bars: 95% confidence intervals. Dotted line: reference value (1.0), which is a proven optimum for <i>N</i> ≤ 14 and <i>N</i> = 24, a published best-known value where stated in the text, and the best value found otherwise. Horizontal labels in the lower panels: ball radius <i>R</i>, number of disks <i>n</i>.",
       "Four stacked line charts of relative score for three algorithms: the Tammes problem by number of points, and the spherical cap, Euclidean disk, and hyperbolic disk by setting.")
    FF("figure", "runtime", "Mean Run Time on the Sphere by Number of Points", f"{FIG}/fig_runtime_scaling.png", 4.5,
       f"Mean wall-clock time per run over {SEEDS} seeds at equal budget. Data: summary_by_condition.csv.",
       "Blue circles = gradient descent, red squares = simulated annealing, green triangles = compression. Error bars: 95% confidence intervals. Both axes logarithmic; time in seconds.",
       "Log-log line chart of run time versus number of points for three algorithms.")
    q = {a: np.percentile(runs[(runs.space == "S2") & (runs.n == 60) & (runs.algorithm == a)].relative_score, [25, 75]) for a in ALG}
    dis = lambda a, b: a[1] < b[0] or b[1] < a[0]
    nov60 = dis(q["gd"], q["sa"]) and dis(q["gd"], q["ls"]) and dis(q["sa"], q["ls"])
    d.body(f"For <i>N</i> = 60 the interquartile ranges of the three algorithms {'do not overlap' if nov60 else 'overlap in part'} ({Fg('dist')}).")
    FF("figure", "dist", "Distribution of Relative Scores Over Seeds", f"{FIG}/fig_distribution.png", 4.5,
       f"Box plots over {SEEDS} seeds for six conditions; the pair in parentheses is (<i>R</i>, <i>n</i>). Data: runs_raw.csv.",
       "Box: interquartile range. Black line: median. Whiskers: 1.5 interquartile ranges. Markers: outliers. Dotted line: reference value. Blue = gradient descent, red = simulated annealing, green = compression. Cap = spherical cap.",
       "Box plots of relative score for three algorithms in six conditions.")

    HD("Statistical Comparison of Algorithms", 2)
    mx = float(fr.p_holm.max())
    d.body(f"The Friedman test found a significant difference among the three algorithms in {fr_sig} of {fr_n} conditions (largest Holm-adjusted <i>p</i> {('< .001' if mx < 0.001 else '= ' + f(mx, 3, lead=False))}), with Kendall\u2019s <i>W</i> between {f(float(fr.kendall_W.min()), 2, lead=False)} and {f(float(fr.kendall_W.max()), 2, lead=False)}. {Tb('pairwise')} counts, for each space and pair, the conditions in which one algorithm was significantly higher after Holm correction and, in the last column, how many of those differences were also practically important (mean difference at least 0.5% of the reference). Compression was significantly lower than gradient descent in {sum(wins(sp, 'gd', 'ls', 'gd')[0] for sp in ('S2', 'S2cap', 'R2', 'H2'))} of {fr_n} conditions and lower than simulated annealing in {sum(wins(sp, 'sa', 'ls', 'sa')[0] for sp in ('S2', 'S2cap', 'R2', 'H2'))} of {fr_n}.")
    rows = []
    for sp in ("S2", "S2cap", "R2", "H2"):
        for a, b in (("gd", "sa"), ("gd", "ls"), ("sa", "ls")):
            g = pw[(pw.space == sp) & (pw.alg_a == a) & (pw.alg_b == b)]
            ka, nn = wins(sp, a, b, a)
            kb, _ = wins(sp, a, b, b)
            rows.append([SLAB[sp], f"{AB[a]} vs. {AB[b]}", str(ka), str(kb), str(nn - ka - kb), str(int(g.significant_and_practical.sum()))])
    FF("table", "pairwise", "Conditions in Which One Algorithm Was Significantly Higher", ["Space", "Comparison", "First higher", "Second higher", "No difference", "Also practical"], rows,
       "Counts of conditions (15 for <i>S</i><sup>2</sup>, 6 for each other space) from Wilcoxon signed-rank tests with Holm-adjusted <i>p</i> < .05. First = first-named algorithm. Also practical = significant differences of at least 0.5% of the reference. Cap = spherical cap. GD = gradient descent; SA = simulated annealing; CP = compression. Data: test_pairwise_wilcoxon.csv.",
       aligns=["l", "l", "c", "c", "c", "c"], widths=[0.9, 1.4, 1.0, 1.1, 1.1, 1.0])
    d.body(f"Significance does not always mean a large difference. For <i>N</i> = 5, 6, and 12, gradient descent was significantly higher than simulated annealing with <i>r</i><sub>rb</sub> = 1.00, yet the mean differences were only {f(PW('S2', 5, 'gd', 'sa').mean_diff * 1000, 1)}, {f(PW('S2', 6, 'gd', 'sa').mean_diff * 1000, 1)}, and {f(PW('S2', 12, 'gd', 'sa').mean_diff * 1000, 1)} milliradians, which is below the 0.5% threshold. Of the {int(pw.significant.sum())} significant pairwise results, {int(pw.significant_and_practical.sum())} were also practically important. For <i>N</i> = 60 on the sphere, gradient descent minus simulated annealing was {f(PW('S2', 60, 'gd', 'sa').mean_diff, 3)} rad, 95% CI [{f(PW('S2', 60, 'gd', 'sa').ci_lo, 3)}, {f(PW('S2', 60, 'gd', 'sa').ci_hi, 3)}], <i>r</i><sub>rb</sub> = {f(PW('S2', 60, 'gd', 'sa').rbc, 2, lead=False)}, <i>d<sub>z</sub></i> = {f(PW('S2', 60, 'gd', 'sa').dz, 2)}, {pstr(PW('S2', 60, 'gd', 'sa').p_holm)}. For 19 hyperbolic disks in a ball of radius 3 the same difference was {f(PW('H2', 19, 'gd', 'sa', R=3.0).mean_diff, 3)}, 95% CI [{f(PW('H2', 19, 'gd', 'sa', R=3.0).ci_lo, 3)}, {f(PW('H2', 19, 'gd', 'sa', R=3.0).ci_hi, 3)}], <i>r</i><sub>rb</sub> = {f(PW('H2', 19, 'gd', 'sa', R=3.0).rbc, 2, lead=False)}, <i>d<sub>z</sub></i> = {f(PW('H2', 19, 'gd', 'sa', R=3.0).dz, 2)}, {pstr(PW('H2', 19, 'gd', 'sa', R=3.0).p_holm)}.")
    flagged = pw[pw.skewness.abs() > 1.0]
    allzero = int((pw.n_nonzero == 0).sum())
    clear = int((flagged.rbc.abs() >= 0.90).sum())
    zero_txt = "in no comparison were all paired differences zero" if allzero == 0 else f"in {allzero} comparisons all paired differences were zero"
    d.body(f"The assumption checks show where the Wilcoxon results need care. The absolute skewness of the paired differences exceeded 1 in {len(flagged)} of {len(pw)} comparisons, so the symmetry assumption is doubtful there, and {zero_txt}. Of the flagged comparisons, {clear} had an absolute rank-biserial correlation of at least .90, where the sign of the difference is nearly constant and the conclusion does not rest on symmetry; the remaining {len(flagged) - clear} should be read with caution (all values are in test_pairwise_wilcoxon.csv). Mean ranks (1 = best of three) were {f(mrank['S2']['sa'], 2)} for simulated annealing, {f(mrank['S2']['gd'], 2)} for gradient descent, and {f(mrank['S2']['ls'], 2)} for compression on the sphere; {f(mrank['S2cap']['sa'], 2)}, {f(mrank['S2cap']['gd'], 2)}, and {f(mrank['S2cap']['ls'], 2)} in the cap; {f(mrank['R2']['sa'], 2)}, {f(mrank['R2']['gd'], 2)}, and {f(mrank['R2']['ls'], 2)} in the Euclidean disk; and {f(mrank['H2']['gd'], 2)} for gradient descent, {f(mrank['H2']['sa'], 2)} for simulated annealing, and {f(mrank['H2']['ls'], 2)} for compression in the hyperbolic disk.")

    HD("Hypothesis Evaluation", 2)
    d.body(f"{Tb('hyp')} states the decision rules and resolves the three hypotheses; the text after it gives the reasoning.")
    h1_txt = f"Kruskal\u2013Wallis for GD\u2013SA across spaces, <i>\u03c7</i><sup>2</sup>(2) = {f(H1c_gdsa.chi2, 2)}, Holm {pstr(H1c_gdsa.p_holm)}; lowest mean rank: cap {AB[best_rank['S2cap']]}, Euclidean {AB[best_rank['R2']]}, hyperbolic {AB[best_rank['H2']]}"
    FF("table", "hyp", "Hypotheses, Decision Rules, and Results", ["Hypothesis", "Decision rule", "Result", "Decision"],
       [["H1: the ranking depends on the space",
         "Disks in a geodesic ball: Kruskal\u2013Wallis test across the three spaces of the per-setting mean paired difference in relative score, per algorithm pair, Holm-adjusted over three pairs; and the lowest-mean-rank algorithm in each space. Supported if some pair has adjusted <i>p</i> < .05 and the lowest-mean-rank algorithm is not the same in all spaces; partly if exactly one holds.",
         h1_txt, H1_DECISION],
        ["H2: compression scales better",
         "Tammes problem, <i>N</i> \u2265 13: Wilcoxon tests of the compression slope of relative score on log<sub>10</sub> <i>N</i> against each other slope, Holm-adjusted over two tests. Supported if higher than both (adjusted <i>p</i> < .05); partly if higher than one.",
         f"Slope per decade of <i>N</i>: CP {f(h2_gd.mean_slope_a, 3)}, GD {f(h2_gd.mean_slope_b, 3)}, SA {f(h2_sa.mean_slope_b, 3)}; Holm {pstr(h2_gd.p_holm)}", H2_DECISION],
        ["H3: all recover the proven optimum for small <i>N</i>",
         "Tammes problem, <i>N</i> = 4 to 14: share of seeds with relative score \u2265 .999. Supported if the share is \u2265 .90 at every <i>N</i> for all three algorithms; partly if for one or two.",
         f"<i>N</i> with share \u2265 .90: GD {11 - int(h3['gd'].n_N_below_0p9)} of 11, SA {11 - int(h3['sa'].n_N_below_0p9)} of 11, CP {11 - int(h3['ls'].n_N_below_0p9)} of 11", H3_DECISION]],
       "GD = gradient descent; SA = simulated annealing; CP = compression. A 1% tolerance (relative score \u2265 .99) is a sensitivity check only. Data: hypothesis_tests.csv, scaling_slopes_per_seed.csv.",
       aligns=["l", "l", "l", "l"], widths=[1.1, 2.5, 1.9, 1.0])
    d.body(f"<i>H1</i> is {H1_DECISION.lower()}. Criterion (b) holds: simulated annealing has the lowest mean rank in the cap and in the Euclidean disk, and gradient descent in the hyperbolic disk. Criterion (a) fails: the difference between gradient descent and simulated annealing does not differ significantly across the three spaces after Holm correction (raw {pstr(H1c_gdsa.p)}, adjusted {pstr(H1c_gdsa.p_holm)}), and the other two pairs show no significant difference (adjusted <i>p</i> = {f(float(H1c[H1c.test.str.startswith('gd-ls')].p_holm.iloc[0]), 3, lead=False)} and {f(float(H1c[H1c.test.str.startswith('sa-ls')].p_holm.iloc[0]), 3, lead=False)}). The median per-setting difference (gradient descent minus simulated annealing, in relative score) was {f(H1c_gdsa.median_diff_S2cap, 4)} in the cap, {f(H1c_gdsa.median_diff_R2, 4)} in the Euclidean disk, and {f(H1c_gdsa.median_diff_H2, 4)} in the hyperbolic disk, so the cap resembles the Euclidean disk and the hyperbolic disk differs. A paired contrast of that difference against the Euclidean disk over the six settings gave raw {pstr(H1c_h2.p)} (adjusted {pstr(H1c_h2.p_holm)}) for the hyperbolic disk and raw {pstr(H1c_cap.p)} for the cap. With six settings per space the smallest possible two-sided <i>p</i> of this contrast is .031, so the study has little power here. For completeness, the contrast between the sphere (Tammes) and the hyperbolic disk that was specified first gave an adjusted <i>p</i> of {f(H1o.p_holm, 3, lead=False)} for the gradient descent\u2013simulated annealing pair; it compares different problems and is not used to attribute the difference to curvature. In summary, the evidence is consistent with a difference in the hyperbolic disk, but it is not significant after correction, it cannot separate curvature from area, and it was explored after the first results were seen.")
    d.body(f"<i>H2</i> is {H2_DECISION.lower()}: compression scaled worse, not better. Its relative score fell by {f(abs(h2_gd.mean_slope_a), 3)} per decade of <i>N</i> for <i>N</i> \u2265 13, much faster than that of gradient descent ({f(abs(h2_gd.mean_slope_b), 3)}) or simulated annealing ({f(abs(h2_sa.mean_slope_b), 3)}), with {pstr(h2_gd.p_holm)} against both. For <i>N</i> = 30, 40, and 60 the reference is not a proven optimum; a reference that is too low raises all relative scores in a condition by the same factor, so it cannot reverse the order of the three algorithms within a condition, but it can change slopes across <i>N</i>. The compression method is also a simplified version, so this result does not describe the event-driven original.")
    d.body(f"<i>H3</i> is {H3_DECISION.lower()} at the 0.1% tolerance. Success rates reached .90 at {11 - int(h3['sa'].n_N_below_0p9)} of 11 values of <i>N</i> for simulated annealing, {11 - int(h3['gd'].n_N_below_0p9)} for gradient descent, and {11 - int(h3['ls'].n_N_below_0p9)} for compression. As a sensitivity check, at the 1% tolerance gradient descent fell below .90 only at <i>N</i> = {', '.join(str(n) for n in below1['gd'])}, simulated annealing at <i>N</i> = {', '.join(str(n) for n in below1['sa'])}, and compression at {len(below1['ls'])} of 11 values. The bound in Equation 7 shows that the smoothing error of gradient descent can reach (ln <i>m</i>)/<i>p</i> in the logarithm of the score, which at the final exponent is not small compared with a 0.1% tolerance; the shortfall of gradient descent is consistent with this bias, but the study did not test that explanation.")

    # ====================================================================== Conclusions
    import supp_section
    supp_section.build_section(d, FF, HD, Tb, f, pstr, DATA, runs, BUDGET)
    import conf_section
    conf_section.build_section(d, FF, HD, Tb, Fg, f, pstr, DATA, CONFDIR, part="main")
    import r3_section
    r3_section.build_section(d, FF, HD, Tb, Fg, f, pstr, DATA, CONFDIR)

    HD("Conclusions", 1)
    d.body("This section summarizes how the results answer the research questions, states the limits of the study, and points to implications and next steps.")
    HD("Summary of Findings", 2)
    FD = json.load(open(CONFDIR + "/followup_decisions.json"))["primary"]
    MD = json.load(open(CONFDIR + "/mini_decisions.json"))
    _tm = pd.read_csv(f"{DATA}/conf_summary_by_condition.csv")
    _tm = _tm[(_tm.budget == 1500) & _tm.label.str.startswith("Tammes")]
    _tp = _tm.pivot(index="label", columns="algorithm", values="mean_rel")
    _bs = _tm.groupby("label").success_0p1.max()
    _mr = DEC["C4"]["mean_rank_by_method"]
    d.body(f"The findings rest first on the preregistered confirmatory round (fresh seeds, three budget levels, six methods, 33 conditions, {DEC['n_runs']:,} runs) and then on the first study, which is exploratory. "
           f"Answering RQ1 on the confirmatory round, polished gradient descent had the best mean rank ({f(_mr['gdp'], 2)}, against {f(_mr['lbfgsb'], 2)} for L-BFGS-B, {f(_mr['bh'], 2)} for basin hopping, {f(_mr['sa'], 2)} for simulated annealing, {f(_mr['gd'], 2)} for gradient descent, and {f(_mr['ls'], 2)} for compression), and the better of the added L-BFGS-B and basin-hopping baselines beat both gradient descent and simulated annealing in all {DEC['C4']['n_conditions']} conditions, so the ranking of the first study, in which simulated annealing and gradient descent led, is a ranking among weaker methods; the best method at 1,500 sweeps was the best at 3,000 sweeps in only {f(DEC['C5']['share_same_top_method_1500_vs_3000'] * 100, 0)}% of conditions, although the whole ordering was stable across budgets (median Kendall’s <i>W</i> {f(DEC['C5']['median_W'], 2, lead=False)}). "
           f"Answering RQ2, the relative score of compression fell from {f(_tp.loc['Tammes N = 9', 'ls'], 3, lead=False)} at <i>N</i> = 9 to {f(_tp.loc['Tammes N = 60', 'ls'], 3, lead=False)} at <i>N</i> = 60 and that of gradient descent from {f(_tp.loc['Tammes N = 9', 'gd'], 3, lead=False)} to {f(_tp.loc['Tammes N = 60', 'gd'], 3, lead=False)}, while polished gradient descent, L-BFGS-B, and basin hopping stayed at or above {f(min(_tp.loc[:, 'gdp'].min(), _tp.loc[:, 'lbfgsb'].min(), _tp.loc[:, 'bh'].min()), 3, lead=False)} for <i>N</i> from 13 to 60, so the number of points hurts the weaker methods most. "
           f"Answering RQ3, no method recovered the proven optimum within 0.1% in at least 90% of seeds for all of <i>N</i> = 9, 13, 14, and 24 (C6 not supported): the best shares were {f(DEC['C6']['by_N']['9']['best_share'], 2, lead=False)} at <i>N</i> = 9, {f(DEC['C6']['by_N']['13']['best_share'], 2, lead=False)} at <i>N</i> = 13, {f(DEC['C6']['by_N']['14']['best_share'], 2, lead=False)} at <i>N</i> = 14, and {f(DEC['C6']['by_N']['24']['best_share'], 2, lead=False)} at <i>N</i> = 24. "
           f"Answering RQ4, the ranking of gradient descent and simulated annealing depended on the space ({pstr(DEC['C3']['kruskal_p'])}) but by less than .01 in relative score. The confirmatory round, the mini-round, and the follow-up could not settle whether curvature itself lowers the density; the final round of {R3['A1']['n_conditions']} equal-area conditions did: with the boundary share in the model, the hyperbolic term was {f(R3['A1']['g_H'], 3)} (95% interval {f(R3['A1']['g_H_ci'][0], 3)} to {f(R3['A1']['g_H_ci'][1], 3)}) and the cap term {f(R3['A1']['g_S'], 3)} ({f(R3['A1']['g_S_ci'][0], 3)} to {f(R3['A1']['g_S_ci'][1], 3)}), so the preregistered decision is that no curvature effect as large as .02 of the density bound was detected. The intervals exclude zero, with opposite signs, so small effects of about 1% of the bound are not ruled out; the earlier withdrawn decision is in Appendix B. "
           f"The boundary-share prediction is supported in the confirmatory round (Spearman {f(DEC['C1']['spearman'], 2, lead=False)}), but that test is partly circular, because the deficit and the boundary share are both computed from the radius that the methods find, and its 26 conditions are paired. At a fixed radius, which removes the circularity, the mini-round was inconclusive (M1 {f(MD['M1']['spearman'], 2, lead=False)}) and the follow-up supported the correlation ({f(FD['F1']['spearman'], 2, lead=False)}, {pstr(FD['F1']['perm_p_one_sided'])}); the loss model is a description, not an explanation. "
           f"Beyond benchmarking, the final round tested a rule for the number of disks that fit in a ball: it was within one disk in {f(R3['B1']['share_within_1'] * 100, 0)}% of {R3['B1']['n_conditions']} new conditions (mean absolute error {f(R3['B1']['mean_abs_error_disks'], 2)} disks), for balls of at most 46 disks.")
    d.body(f"The first study (exploratory; {SEEDS} paired seeds, {NCOND} conditions, one budget, three methods) found that gradient descent and simulated annealing were close to each other and clearly ahead of the simplified compression method in all four settings (on the sphere, mean relative scores of {f(mrel['S2']['gd'], 3, lead=False)} for gradient descent, {f(mrel['S2']['sa'], 3, lead=False)} for simulated annealing, and {f(mrel['S2']['ls'], 3, lead=False)} for compression). Simulated annealing had the best mean rank on the sphere, in the cap, and in the Euclidean disk, and gradient descent in the hyperbolic disk, and the difference between spaces was not significant after correction. "
           "In exploratory follow-up runs (see Supplementary Exploratory Analyses), a max-min polishing step raised the mean relative score of gradient descent and the number of values of <i>N</i> with a success share of at least .90 (its linear programs are not charged in the sweep count and added about 0.3 seconds per run), which the confirmatory round then confirmed for the ranking, and at equal area the ranking did not differ detectably across the three spaces, a result that the preregistered comparison C3 did not reproduce, although the difference it found is smaller than .01 in relative score. "
           f"For <i>N</i> = 13, no method reached a success share of .90, and {_N13H} of {_N13N} runs recovered the optimum within 0.1% (see Confirmatory Round).")
    d.body(f"<b>What we can actually conclude.</b> Five conclusions are supported by the preregistered rounds and do not depend on exploratory labels. First, at an equal budget of distance evaluations, the stronger baselines (L-BFGS-B and basin hopping) and polished gradient descent beat plain gradient descent and simulated annealing in every one of 33 conditions, and compression, as implemented here, is the weakest. Second, the order of the methods is stable across the three budgets, but the single best method changes with the budget. Third, packing density in a bounded ball falls short of the whole-space upper bound by an amount that grows with the share of the ball near its wall, in all three spaces. Fourth, recovery of the proven or best-known configuration within 0.1% depended on <i>N</i>: at 1,500 sweeps some method reached it in at least {f(min(_bs['Tammes N = 9'], _bs['Tammes N = 14'], _bs['Tammes N = 24'], _bs['Tammes N = 30']) * 100, 0)}% of seeds for <i>N</i> = 9, 14, 24, and 30, but none did for <i>N</i> = 13, and the best shares were only {f(_bs['Tammes N = 40'], 2, lead=False)} for <i>N</i> = 40 and {f(_bs['Tammes N = 60'], 2, lead=False)} for <i>N</i> = 60. "
           "Fifth, in the final preregistered round no curvature effect larger than .02 of the density bound was found at equal area, and the number of disks that fit in a ball was predicted within one disk by a one-coefficient rule. Three things are not concluded: that curvature has exactly no effect (the final-round intervals exclude zero, with opposite signs, within about 1% of the bound), whether the boundary causes the loss (the boundary-loss model describes the data and does not explain them), and whether the configurations found are optimal. The practical recommendation rests on the first two conclusions: for a fixed budget, use polished gradient descent, L-BFGS-B, or basin hopping, not plain gradient descent, annealing, or this compression method; the polishing step helps in the confirmatory round and costs wall-clock time that the sweep count does not charge.")
    cfgs = cfgall
    srow = gd4[gd4.score < 1.6].iloc[0]
    X4 = cfgs[(cfgs.condition_id == srow.condition_id) & (cfgs.algorithm == "gd") & (cfgs.seed == srow.seed)].sort_values("index")[["x0", "x1", "x2"]].values
    coplanar = np.linalg.svd(X4, compute_uv=False)[2] < 1e-6
    STUCKDESC = "four points on one great circle" if coplanar else "an arrangement of four points that is not the tetrahedron"
    assert abs(float(srow.score) - np.pi / 2) < 1e-3
    d.body(f"One failure is worth recording. In {stuck} of {SEEDS} seeds, gradient descent for <i>N</i> = 4 converged to {STUCKDESC}, with a minimum distance of \u03c0/2 instead of the tetrahedral value, which shows why repeated seeds matter even for four points.")
    HD("Limitations on the Research Design and Material", 2)
    d.body(f"The conclusions are limited as follows. (a) The first study used one budget level ({BUDGET:,} sweeps); the confirmatory round used three levels (500, 1,500, and 3,000), and a larger budget could still change the ordering, especially for compression. (b) The compression method is a simplified, time-stepped version of the method of Lubachevsky and Stillinger (1990). (c) In the first study, algorithm parameters were tuned on four pilot seeds in four pilot conditions with grids of different sizes, and unequal tuning effort could favor one method; the confirmatory round used the same effort for all six methods (one parameter, six settings), but two methods were selected at the edge of their range, and after their ranges were extended (post hoc, nine settings for those two methods) L-BFGS-B was again selected at the edge. (d) Where no optimum is proven, the reference is a published best-known value ({KNOWN_TXT}) or else the best value found, so relative scores near 1 do not establish optimality; the polished variant exceeded the best value found in some ball conditions, which shows that a best-found reference can lie below what is reachable. (e) Problem B maximizes the radius for fixed <i>n</i> and <i>R</i>, and uses {len(BALL)} settings with <i>R</i> = 2 or 3. The first study did not compare equal areas, so curvature and area are confounded in it; the confirmatory round compares equal areas, but only up to 4\u03c0 for the sphere, and its boundary-share and curvature analyses rest on 26 conditions; and the cap with <i>R</i> = 3 covers almost the whole sphere. (f) The comparison of curvatures rests on six settings per space and an exploratory analysis, which is why RQ4 and H1 are exploratory. (g) The Wilcoxon symmetry assumption was doubtful in part of the comparisons, and the 0.1% success tolerance interacts with the exponent cap of gradient descent. (h) Run times describe this Python implementation on one machine. (i) No claim of global optimality is made for any configuration found. (j) Equal sweeps are not equal time: simulated annealing took several times longer per run than gradient descent ({Tb('timing')}), and the polishing step is charged in sweeps but not for the time to solve its linear programs. (k) The polishing step is one refinement (max-min by sequential linear programming), and its time is not charged in sweeps. (l) The confirmatory round used one machine with two processes, 20 seeds, six methods with one tuned parameter each, a reference that is the best score found in {DEC['reference_types'].get('best found in this round', 0)} of 33 conditions, and a self-recorded preregistration hash. (m) The boundary-share test C1 is partly circular, because the density deficit and the boundary share are both computed from the radius that the methods find, and the 26 ball conditions are paired by area or by number of disks, so its permutation test assumes more independence than the design has. The mini-round designed to remove the circularity was inconclusive for M1 (Spearman {f(MDEC['M1']['spearman'], 2, lead=False)}), its decision M2 was withdrawn when three duplicated Euclidean conditions were removed, and the follow-up, with a second method, supported F1 (Appendix B); the boundary-loss model is a description, not an explanation.  (n) The final round used two methods at one budget (1,500 sweeps), balls of at most 46 disks for the counting rule (a lower bound on the number that fit, from 20 seeds), and a loss coefficient (0.46) fitted in the follow-up; its curvature decision means that no effect above .02 was detected, not that the effect is zero, and its self-recorded hash is independent of the adviser\u2019s email only by the author\u2019s report. (o) The wall ring (every disk within one disk radius of the wall) occurred only in the two largest hyperbolic balls (radii 6 and 8) and is not a general result.")
    HD("Implications and Future Directions", 2)
    d.body("Well-spread point sets on spheres are used for sampling and for placing sensors or antennas, and packings in hyperbolic space relate to embeddings of tree-like networks. Within the limits above, the results suggest a practical rule that rests on the confirmatory round: at a fixed budget, use polished gradient descent, L-BFGS-B, or basin hopping, which beat gradient descent and annealing in all 33 conditions, and not the simplified compression method; the polishing step\u2019s linear programs are not charged in the sweep count and cost extra wall-clock time, and the first study\u2019s preference for gradient descent or annealing applies only among those weaker methods. Natural extensions are an event-driven compression method, larger budgets, more ball radii, equal-area and equal-density designs at areas beyond what the sphere can hold (in the Euclidean and hyperbolic planes only), a count-based version of Problem B for balls larger than the 46 disks tested here, and proofs or certified bounds for the best configurations found.")

    FL()
    d.new_page()
    HD("References", 1)
    for r in sorted(REFS, key=lambda s: s.replace("ö", "o").lower()):
        d.reference(r)
    d.new_page()
    HD("Appendix A: Sensitivity of the Main Results to Budget, Parameters, and Starting Configuration", 1)
    d.body(f"This appendix holds the three sensitivity tables referred to in the Supplementary Exploratory Analyses: {Tb('budget')} gives the mean relative score at three budgets, {Tb('sens')} the effect of changing one parameter at a time, and {Tb('spread')} the spread over starting configurations.")
    while appfloats:
        kind, key, a, k = appfloats.pop(0)
        d.table(*a, label=APP[key], **k)
    d.new_page()
    HD("Appendix B: Mini-Round, Follow-Up, and the Withdrawn Decision", 1)
    d.body("This appendix keeps the history of the work between the confirmatory round and the final round, including a decision that was withdrawn. It is not needed to follow the main results. The Research Plan holds the dated version history in its Appendix A.")
    conf_section.build_section(d, FF, HD, Tb, Fg, f, pstr, DATA, CONFDIR, part="appendix")
    FL()
    return d


def main():
    d0 = build({"toc": [], "figs": [], "tabs": []})
    pg = {"toc": [(l, t, 0) for l, t in d0.headings],
          "figs": [(n, t, 0) for k, n, t in d0.captions if k == "Figure"],
          "tabs": [(n, t, 0) for k, n, t in d0.captions if k == "Table"]}
    fast = "--fast" in sys.argv and os.path.exists(OUT + "/paper_pages.json")
    if fast:
        old = json.load(open(OUT + "/paper_pages.json"))
        if all(len(old[k]) == len(pg[k]) for k in pg):
            pg = {k: [(int(e[0]) if k == "toc" else int(e[0]), e[1], int(e[2])) for e in v] for k, v in old.items()}
    for it in range(1 if fast else 5):
        d = build(pg)
        path = OUT + "/Research_Paper.docx"
        d.save(path)
        pdf = to_pdf(path, OUT)
        pages = pdf_pages(pdf)
        body0 = next(i for i in range(1, len(pages)) if any(l.strip().startswith("Algorithmic Optimization") for l in pages[i].split("\n")[:4]))
        newtoc = []
        for (l, t, _) in pg["toc"]:
            if t in ("List of Figures", "List of Tables"):
                pnum = find_exact(pages, [t], start_page=3)[0]
            else:
                pnum = find_exact(pages, [t], start_page=body0)[0] or find_pages(pages, [t], start_page=body0)[0]
            newtoc.append((l, t, pnum))
        newfigs = [(n, t, find_pages(pages, [f"Figure {n}. {t}"], start_page=body0)[0]) for n, t, _ in pg["figs"]]
        newtabs = [(n, t, find_exact(pages, [f"Table {n}"], start_page=body0)[0]) for n, t, _ in pg["tabs"]]
        new = {"toc": newtoc, "figs": newfigs, "tabs": newtabs}
        if new == pg:
            break
        pg = new
    import omml
    omml.MODE = "omml"            # final .docx carries native Word equations; the PDF above used typeset images
    build(pg).save(path)
    json.dump({k: [list(map(str, e)) for e in v] for k, v in pg.items()}, open(OUT + "/paper_pages.json", "w"))
    print("pages:", len(pages), "| body starts at page", body0 + 1)
    print("abstract words:", words(abstract))
    print("entries without page:", [e for k in ("toc", "figs", "tabs") for e in pg[k] if not e[2]])


if __name__ == "__main__":
    main()
