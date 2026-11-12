"""supplementary.py -- post hoc, exploratory analyses added after the main study (see the Research Plan, version 2.1).

None of these results is used to decide H1-H3.  Same algorithms, parameters (except where a parameter is the thing varied),
budget (1,500 sweeps unless varied), seeds 1-30, starting configurations, and random streams as the main study.

  1. equal-area balls (cap, Euclidean disk, hyperbolic disk) and two larger balls in R2 and H2;
  2. budget sensitivity (500 and 3,000 sweeps) and parameter sensitivity (one parameter of each algorithm, two values each);
  2b. gradient descent followed by a max-min polishing step (sequential linear programming), same total budget;
  3. independent recomputation of every score from the saved coordinates, robustness of H1, bootstrap intervals, spread over starts.

Usage:  python3 supplementary.py            (reuses cached run files in out/data if present)
        python3 supplementary.py --rerun    (recomputes the runs; about 40 minutes on two cores)
"""
import os
import sys
import time
import numpy as np
import pandas as pd
from multiprocessing import Pool
from scipy import stats
from algorithms import Problem, RUNNERS, ALGS, run_algorithm

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "out", "data")
SEEDS = range(1, 31)
BUDGET = 1500
AREAS = [3.0, 6.0, 12.0]
NS = [12, 19, 30]
LARGE = [(4.0, 30), (5.0, 60)]
# five conditions of the main study (same condition ids, hence the same starting configurations)
SENS_CONDS = [("S2", 13, None, 109), ("S2", 30, None, 112), ("S2cap", 19, 3.0, 404), ("R2", 19, 3.0, 304), ("H2", 19, 3.0, 204)]
VARIANTS = [("budget 500", "all", 500, {}), ("budget 3000", "all", 3000, {}),
            ("gd pmax=75", "gd", 1500, dict(pmax=75.0)), ("gd pmax=300", "gd", 1500, dict(pmax=300.0)),
            ("sa T0=0.005", "sa", 1500, dict(T0f=0.005)), ("sa T0=0.08", "sa", 1500, dict(T0f=0.08)),
            ("ls g0=0.1", "ls", 1500, dict(g0=0.1)), ("ls g0=0.5", "ls", 1500, dict(g0=0.5))]


def radius(space, A):
    """Radius of the geodesic ball of area A in each space (Equation 4 inverted)."""
    if space == "S2cap":
        return float(np.arccos(1 - A / (2 * np.pi)))
    if space == "R2":
        return float(np.sqrt(A / np.pi))
    return float(np.arccosh(1 + A / (2 * np.pi)))


def _problem(sp, n, R):
    return Problem("S2" if sp == "S2cap" else sp, n, R)


# ---------------------------------------------------------------- 1. equal area
def equal_area_conditions():
    conds = []
    for A in AREAS:
        for n in NS:
            for sp in ("S2cap", "R2", "H2"):
                conds.append((sp, n, radius(sp, A), "equal-area", A))
    for R, n in LARGE:
        for sp in ("R2", "H2"):
            area = np.pi * R * R if sp == "R2" else 2 * np.pi * (np.cosh(R) - 1)
            conds.append((sp, n, R, "large-ball", float(area)))
    return conds


def _equal_area_job(args):
    cid, (sp, n, R, kind, A) = args
    P = _problem(sp, n, R)
    rows = []
    for seed in SEEDS:
        X0 = P.initial(np.random.default_rng([seed, cid, 0]))
        for aid, alg in ALGS.items():
            res = run_algorithm(alg, P, X0, BUDGET * P.sweep, [seed, cid, aid])
            rows.append(dict(design=kind, area=A, space=sp, condition_id=cid, n=n, R=R, algorithm=alg, seed=seed,
                             score=res["score"], density=P.density(res["score"]), sweeps_used=res["pe"] / P.sweep,
                             recomputed=res["final_check"]))
    return rows


def run_equal_area():
    conds = list(enumerate(equal_area_conditions(), start=500))
    with Pool(2) as pool:
        out = pool.map(_equal_area_job, conds, chunksize=1)
    d = pd.DataFrame([r for o in out for r in o])
    best = d.groupby("condition_id").score.transform("max")
    d["reference_value"] = best
    d["relative_score"] = d.score / best
    d.to_csv(f"{DATA}/supp_equal_area_runs.csv", index=False)
    return d


def summarize_equal_area(d):
    w = d.pivot_table(index=["design", "area", "space", "condition_id", "n", "R", "seed"], columns="algorithm", values="relative_score").reset_index()
    rows = []
    for (des, A, sp, cid, n, R), g in w.groupby(["design", "area", "space", "condition_id", "n", "R"]):
        diff = g.gd - g.sa
        pg = stats.wilcoxon(diff).pvalue if diff.abs().sum() > 0 else 1.0
        rows.append(dict(design=des, area=round(A, 2), space=sp, n=n, R=round(R, 3), mean_gd=g.gd.mean(), mean_sa=g.sa.mean(),
                         mean_ls=g.ls.mean(), gd_minus_sa=diff.mean(), p_wilcoxon_gd_sa=pg,
                         p_friedman=stats.friedmanchisquare(g.gd, g.sa, g.ls).pvalue))
    s = pd.DataFrame(rows)
    s["p_holm_gd_sa"] = np.nan
    for des, idx in s.groupby("design").groups.items():          # Holm family = the conditions of one design
        p = s.loc[idx, "p_wilcoxon_gd_sa"].values
        order = np.argsort(p)
        adj = np.empty(len(p))
        run = 0.0
        for k, i in enumerate(order):
            run = max(run, (len(p) - k) * p[i])
            adj[i] = min(run, 1.0)
        s.loc[idx, "p_holm_gd_sa"] = adj
    s.to_csv(f"{DATA}/supp_equal_area_summary.csv", index=False, float_format="%.6g")
    return s


# ---------------------------------------------------------------- 2. sensitivity
def _sens_job(c):
    sp, n, R, cid = c
    P = _problem(sp, n, R)
    rows = []
    for seed in SEEDS:
        X0 = P.initial(np.random.default_rng([seed, cid, 0]))
        for aid, alg in ALGS.items():
            for vname, valg, bud, kw in VARIANTS:
                if valg not in ("all", alg):
                    continue
                res = RUNNERS[alg](P, X0, bud * P.sweep, np.random.default_rng([seed, cid, aid]), **kw)
                rows.append(dict(space=sp, condition_id=cid, n=n, R=R, algorithm=alg, seed=seed, variant=vname, budget=bud,
                                 score=res["score"], check=P.score(res["X"])))
    return rows


def run_sensitivity():
    with Pool(2) as pool:
        out = pool.map(_sens_job, SENS_CONDS, chunksize=1)
    d = pd.DataFrame([r for o in out for r in o])
    d.to_csv(f"{DATA}/supp_sensitivity_runs.csv", index=False)
    return d


# ---------------------------------------------------------------- 2b. gradient descent with polishing
def _gdp_job(cond):
    import experiments as E
    kind, n, R = cond
    cid = E.COND_ID[cond]
    P = _problem(kind, n, R)
    rows = []
    for seed in E.SEEDS:
        X0 = P.initial(np.random.default_rng([seed, cid, 0]))
        t0 = time.perf_counter()
        res = RUNNERS["gdp"](P, X0, E.BUDGET_SWEEPS * P.sweep, np.random.default_rng([seed, cid, 1]))
        dt = time.perf_counter() - t0
        rows.append(dict(space=kind, condition_id=cid, n=n, R=(R if R is not None else float("nan")), algorithm="gdp", seed=seed,
                         score=res["score"], check=P.score(res["X"]), sweeps_used=res["pe"] / P.sweep, time_s=dt))
    return rows


def run_gdp_all():
    import experiments as E
    with Pool(2) as pool:
        out = pool.map(_gdp_job, list(E.conditions()), chunksize=1)
    d = pd.DataFrame([r for o in out for r in o])
    ref = pd.read_csv(f"{DATA}/runs_raw.csv").groupby("condition_id")[["reference_value", "reference_type"]].first().reset_index()
    d = d.merge(ref, on="condition_id")
    d["relative_score"] = d.score / d.reference_value
    d.to_csv(f"{DATA}/supp_gd_polish_runs.csv", index=False)
    return d


# ---------------------------------------------------------------- 2c. wall-clock benchmark (one process, nothing else running)
def run_timing(seeds=range(1, 6)):
    rows = []
    for sp, n, R, cid in SENS_CONDS:
        P = _problem(sp, n, R)
        for seed in seeds:
            X0 = P.initial(np.random.default_rng([seed, cid, 0]))
            for alg, aid in (("gd", 1), ("gdp", 1), ("sa", 2), ("ls", 3)):
                t0 = time.perf_counter()
                res = RUNNERS[alg](P, X0, BUDGET * P.sweep, np.random.default_rng([seed, cid, aid]))
                rows.append(dict(space=sp, condition_id=cid, n=n, R=R, algorithm=alg, seed=seed, time_s=time.perf_counter() - t0,
                                 sweeps_used=res["pe"] / P.sweep, score=res["score"]))
    d = pd.DataFrame(rows)
    d.to_csv(f"{DATA}/supp_timing.csv", index=False)
    return d


# ---------------------------------------------------------------- 3. checks
def _indep_score(space, X, R):
    """Score recomputed with formulas that do not use geometry.py (arctan2, Poincare disk)."""
    n = len(X)
    iu = np.triu_indices(n, 1)
    if space in ("S2", "S2cap"):
        cr = np.cross(X[:, None, :], X[None, :, :])
        d = np.arctan2(np.linalg.norm(cr, axis=-1), X @ X.T)[iu]
        man = abs(np.linalg.norm(X, axis=1) - 1).max()
        rho = np.arctan2(np.hypot(X[:, 0], X[:, 1]), X[:, 2])
    elif space == "H2":
        z = (X[:, 1] + 1j * X[:, 2]) / (1 + X[:, 0])
        den = (1 - np.abs(z)[:, None] ** 2) * (1 - np.abs(z)[None, :] ** 2)
        d = np.arccosh(1 + 2 * np.abs(z[:, None] - z[None, :]) ** 2 / den)[iu]
        man = abs(-X[:, 0] ** 2 + X[:, 1] ** 2 + X[:, 2] ** 2 + 1).max()
        rho = 2 * np.arctanh(np.abs(z))
    else:
        d = np.sqrt(((X[:, None, :] - X[None, :, :]) ** 2).sum(-1))[iu]
        man = 0.0
        rho = np.hypot(X[:, 0], X[:, 1])
    l = d.min()
    if R is not None:
        l = min(l, (2 * (R - rho)).min())
    return (l / 2 if R is not None else l), man, (None if R is None else float((rho + l / 2 - R).max()))


def run_checks():
    runs = pd.read_csv(f"{DATA}/runs_raw.csv")
    cfg = pd.read_csv(f"{DATA}/configurations.csv")
    res = {}
    rows = []
    for (sp, cid, alg, seed), g in cfg.groupby(["space", "condition_id", "algorithm", "seed"], sort=False):
        Rv = g.R.iloc[0]
        Rv = None if np.isnan(Rv) else float(Rv)
        X = g[["x0", "x1", "x2"]].values if sp != "R2" else g[["x0", "x1"]].values
        s, man, ex = _indep_score(sp, X, Rv)
        rows.append((sp, cid, alg, seed, s, man, ex))
    ch = pd.DataFrame(rows, columns=["space", "condition_id", "algorithm", "seed", "indep", "manifold_err", "wall_excess"])
    m = runs.merge(ch, on=["space", "condition_id", "algorithm", "seed"])
    res["n_scores_checked"] = len(m)
    res["max_abs_diff_score_vs_independent"] = float((m.score - m.indep).abs().max())
    res["max_abs_diff_score_vs_recomputed"] = float((m.score - m.recomputed_score).abs().max())
    res["max_manifold_error"] = float(m.manifold_err.max())
    res["max_disk_excess_beyond_wall"] = float(m.wall_excess.dropna().max())
    # H1 robustness
    w = runs.pivot_table(index=["space", "condition_id", "seed"], columns="algorithm", values="relative_score").reset_index()
    w["gdsa"] = w.gd - w.sa
    b = w[w.space.isin(["S2cap", "R2", "H2"])]
    mean_d = b.groupby(["space", "condition_id"]).gdsa.mean().reset_index()
    med_d = b.groupby(["space", "condition_id"]).gdsa.median().reset_index()

    def kw(df):
        return stats.kruskal(*[df[df.space == s].gdsa.values for s in ("S2cap", "R2", "H2")])

    k1, k2 = kw(mean_d), kw(med_d)
    res["H1_kruskal_chi2_mean_difference"], res["H1_kruskal_p_mean_difference"] = float(k1.statistic), float(k1.pvalue)
    res["H1_kruskal_chi2_median_difference"], res["H1_kruskal_p_median_difference"] = float(k2.statistic), float(k2.pvalue)
    rng = np.random.default_rng(20261028)
    code = mean_d.space.map({"S2cap": 0, "R2": 1, "H2": 2}).values
    vals = mean_d.gdsa.values
    H = lambda lab: stats.kruskal(*[vals[lab == i] for i in range(3)]).statistic
    obs = H(code)
    res["H1_permutation_p_20000"] = float(np.mean([H(rng.permutation(code)) >= obs - 1e-12 for _ in range(20000)]))
    for tag, ids in (("R2_settings", [0, 1, 2]), ("R3_settings", [3, 4, 5])):
        sub = mean_d[mean_d.condition_id.mod(100).isin(ids)]
        kk = kw(sub)
        res[f"H1_kruskal_chi2_{tag}"], res[f"H1_kruskal_p_{tag}"] = float(kk.statistic), float(kk.pvalue)

    def ci(x, B=10000):
        x = np.asarray(x, float)
        h = stats.t.ppf(.975, len(x) - 1) * x.std(ddof=1) / np.sqrt(len(x))
        bs = rng.choice(x, (B, len(x))).mean(1)
        return x.mean(), x.mean() - h, x.mean() + h, np.percentile(bs, 2.5), np.percentile(bs, 97.5)

    for tag, cid in (("S2_N60", 114), ("H2_R3_n19", 204)):
        mu, tlo, thi, blo, bhi = ci(w[w.condition_id == cid].gdsa.values)
        res[f"gd_minus_sa_{tag}_mean_relative"] = float(mu)
        res[f"gd_minus_sa_{tag}_t_lo"], res[f"gd_minus_sa_{tag}_t_hi"] = float(tlo), float(thi)
        res[f"gd_minus_sa_{tag}_boot_lo"], res[f"gd_minus_sa_{tag}_boot_hi"] = float(blo), float(bhi)
    pd.DataFrame({"check": list(res), "value": list(res.values())}).to_csv(f"{DATA}/supp_checks.csv", index=False, float_format="%.10g")
    # spread of relative score over the 30 starting configurations
    sel = {109: "Tammes N = 13", 112: "Tammes N = 30", 404: "Cap, R = 3, n = 19", 304: "Euclidean, R = 3, n = 19", 204: "Hyperbolic, R = 3, n = 19"}
    sp_ = runs[runs.condition_id.isin(sel)].groupby(["condition_id", "algorithm"]).relative_score.agg(["min", "median", "max", "std"]).reset_index()
    sp_["label"] = sp_.condition_id.map(sel)
    sp_.to_csv(f"{DATA}/supp_initialization_spread.csv", index=False, float_format="%.6g")
    return res


def main(rerun=False):
    os.makedirs(DATA, exist_ok=True)
    t0 = time.time()
    f1, f2 = f"{DATA}/supp_equal_area_runs.csv", f"{DATA}/supp_sensitivity_runs.csv"
    d1 = run_equal_area() if (rerun or not os.path.exists(f1)) else pd.read_csv(f1)
    summarize_equal_area(d1)
    if rerun or not os.path.exists(f2):
        run_sensitivity()
    if rerun or not os.path.exists(f"{DATA}/supp_gd_polish_runs.csv"):
        run_gdp_all()
    if rerun or not os.path.exists(f"{DATA}/supp_timing.csv"):
        run_timing()
    run_checks()
    print("supplementary analyses finished in %.0f s" % (time.time() - t0))


if __name__ == "__main__":
    main(rerun="--rerun" in sys.argv)
