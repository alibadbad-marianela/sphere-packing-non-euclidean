"""confirm_analyze.py -- analysis of the confirmatory round, exactly as specified in PREREGISTRATION.md.

Reads out/conf/runs_<cid>.csv (+ optional out/conf/packomania_values.csv), writes the conf_*.csv files to out/data and
out/conf/decisions.json.  Nothing here uses a result to choose a rule.
"""
import glob
import json
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
import confirm_design as C
from experiments import BENCH_DEG, BEST_KNOWN_DEG

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF, DATA = ROOT + "/out/conf", ROOT + "/out/data"
METHODS = ["gd", "gdp", "sa", "ls", "lbfgsb", "bh"]
MAIN = C.MAIN_BUDGET
rng = np.random.default_rng(20261029)          # fixed seed of the permutation and bootstrap procedures


def load():
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(CONF + "/runs_*.csv"))], ignore_index=True)
    conds = {c["cid"]: c for c in C.conditions()}
    pk = {}
    f = CONF + "/packomania_values.csv"
    if os.path.exists(f):
        p = pd.read_csv(f)
        pk = dict(zip(p.n.astype(int), p.radius.astype(float)))
    refs, rtype = {}, {}
    bf = d.groupby("condition_id").score.max()
    for cid, c in conds.items():
        if c["group"] == "tammes":
            N = c["n"]
            if N in BENCH_DEG:
                refs[cid], rtype[cid] = float(np.radians(BENCH_DEG[N])), "proven optimum"
            else:
                refs[cid], rtype[cid] = float(np.radians(BEST_KNOWN_DEG[N])), "published best known (Sloane)"
        elif c["kind"] == "R2" and c["n"] in pk:
            refs[cid], rtype[cid] = pk[c["n"]] * c["R"], "published best known (Packomania)"
        else:
            refs[cid], rtype[cid] = float(bf.get(cid, np.nan)), "best found in this round"
    d["reference_value"] = d.condition_id.map(refs)
    d["reference_type"] = d.condition_id.map(rtype)
    d["relative_score"] = d.score / d.reference_value
    d["success_0.1pct"] = (d.relative_score >= 0.999).astype(int)
    d["success_1pct"] = (d.relative_score >= 0.99).astype(int)
    return d, conds


def spearman_perm(x, y, nperm=20000):
    obs = stats.spearmanr(x, y)[0]
    cnt = 0
    for _ in range(nperm):
        if stats.spearmanr(x, rng.permutation(y))[0] >= obs - 1e-12:
            cnt += 1
    return float(obs), (cnt + 1) / (nperm + 1)


def main():
    d, conds = load()
    d.to_csv(DATA + "/conf_runs.csv", index=False)
    m = d.groupby(["condition_id", "budget", "algorithm"]).agg(mean_score=("score", "mean"), mean_rel=("relative_score", "mean"), sd_rel=("relative_score", "std"),
                                                              success_0p1=("success_0.1pct", "mean"), success_1=("success_1pct", "mean"),
                                                              mean_time_s=("time_s", "mean"), mean_sweeps=("sweeps_used", "mean")).reset_index()
    lab = {cid: c["label"] for cid, c in conds.items()}
    m["label"] = m.condition_id.map(lab)
    m["reference_type"] = m.condition_id.map(d.groupby("condition_id").reference_type.first())
    m.to_csv(DATA + "/conf_summary_by_condition.csv", index=False)
    out = {}

    # ---- C1 and C2 : density deficit versus boundary share over the 26 ball conditions
    rows = []
    for cid, c in conds.items():
        if c["group"] == "tammes":
            continue
        g = m[(m.condition_id == cid) & (m.budget == MAIN)]
        best = g.loc[g.mean_score.idxmax()]
        r = float(best.mean_score)
        rows.append(dict(condition_id=cid, label=c["label"], group=c["group"], space=c["kind"], n=c["n"], R=c["R"], area=c["area"], best_method=best.algorithm,
                         r_best=r, deficit=C.deficit(c["kind"], c["R"], c["n"], r), boundary_share=C.boundary_share(c["kind"], c["R"], r),
                         ref_density=C.ref_density(c["kind"], r)))
    t = pd.DataFrame(rows)
    t.to_csv(DATA + "/conf_deficit_boundary.csv", index=False)
    rho, p = spearman_perm(t.boundary_share.values, t.deficit.values)
    within = {sp: float(stats.spearmanr(g.boundary_share, g.deficit)[0]) for sp, g in t.groupby("space")}
    out["C1"] = dict(n_conditions=len(t), spearman=rho, perm_p_one_sided=p, within_space=within,
                     decision=("supported" if rho >= 0.70 and p < 0.05 else "not supported" if rho < 0.30 else "inconclusive"))
    # exploratory robustness of C1 (not part of the decision): without the two hyperbolic balls of radius 6 and 8, which have the largest b
    t2 = t[~((t.space == "H2") & (t.group == "large") & (t.R >= 6))]
    rho2, p2 = spearman_perm(t2.boundary_share.values, t2.deficit.values, nperm=5000)
    out["C1_exploratory_without_two_largest_hyperbolic"] = dict(n_conditions=len(t2), spearman=rho2, perm_p_one_sided=p2)
    X = np.c_[np.ones(len(t)), t.boundary_share, (t.space == "H2").astype(float), (t.space == "S2cap").astype(float)]
    beta = np.linalg.lstsq(X, t.deficit.values, rcond=None)[0]
    boots = []
    for _ in range(10000):
        ix = rng.integers(0, len(t), len(t))
        boots.append(np.linalg.lstsq(X[ix], t.deficit.values[ix], rcond=None)[0][2])
    lo, hi = np.percentile(boots, [2.5, 97.5])
    gh = float(beta[2])
    out["C2"] = dict(intercept=float(beta[0]), beta_boundary=float(beta[1]), gamma_hyperbolic=gh, gamma_cap=float(beta[3]), ci95_gamma_hyperbolic=[float(lo), float(hi)],
                     decision=("curvature adds a detectable deficit" if lo > 0 and gh >= 0.02 else "no detectable curvature effect" if lo >= -0.02 and hi <= 0.02 else "inconclusive"))

    # ---- C3 : GD minus SA at equal area across spaces
    w = d[(d.budget == MAIN) & d.condition_id.isin([cid for cid, c in conds.items() if c["group"] == "equal_area"])].pivot_table(index=["condition_id", "seed"], columns="algorithm", values="relative_score")
    dc = (w.gd - w.sa).groupby("condition_id").mean().rename("mean_gd_minus_sa").reset_index()
    dc["space"] = dc.condition_id.map(lambda c: conds[c]["kind"])
    dc.to_csv(DATA + "/conf_gd_minus_sa_equal_area.csv", index=False)
    grp = {sp: g.mean_gd_minus_sa.values for sp, g in dc.groupby("space")}
    kw = stats.kruskal(*grp.values())
    pairs, inside = {}, []
    for a, b in (("S2cap", "R2"), ("S2cap", "H2"), ("R2", "H2")):
        diffs = [np.median(rng.choice(grp[a], len(grp[a]))) - np.median(rng.choice(grp[b], len(grp[b]))) for _ in range(10000)]
        lo, hi = np.percentile(diffs, [5, 95])
        pairs[f"{a}-{b}"] = [float(lo), float(hi)]
        inside.append(lo >= -0.01 and hi <= 0.01)
    out["C3"] = dict(kruskal_chi2=float(kw.statistic), kruskal_p=float(kw.pvalue), median_d={k: float(np.median(v)) for k, v in grp.items()}, ci90_median_difference=pairs,
                     decision=("ranking depends on the space" if kw.pvalue < 0.05 else "ranking does not depend on the space (equivalence)" if all(inside) else "inconclusive"))

    # ---- C4 : baselines and ranks
    g1 = m[m.budget == MAIN].pivot(index="condition_id", columns="algorithm", values="mean_rel")
    new_best = (g1[["lbfgsb", "bh"]].max(axis=1) > g1[["gd", "sa"]].max(axis=1))
    rk = d[d.budget == MAIN].copy()
    rk["rank"] = rk.groupby(["condition_id", "seed"]).score.rank(ascending=False)
    mr = rk.groupby(["condition_id", "algorithm"])["rank"].mean().unstack()
    mr.add_prefix("mean_rank_").to_csv(DATA + "/conf_mean_ranks.csv")
    gdp_top2 = (mr.rank(axis=1)["gdp"] <= 2)
    out["C4"] = dict(share_new_baseline_beats_gd_and_sa=float(new_best.mean()), n_conditions=int(len(g1)), share_gdp_rank_top2=float(gdp_top2.mean()),
                     mean_rank_by_method=mr.mean().round(3).to_dict(),
                     decision_baselines_matter=bool(new_best.mean() >= 0.5), decision_gdp_competitive=bool(gdp_top2.mean() >= 0.5))

    # ---- C5 : Kendall's W across budgets
    Ws, same_top = [], []
    for cid, g in m.groupby("condition_id"):
        P = g.pivot(index="algorithm", columns="budget", values="mean_rel").reindex(METHODS)
        R = P.rank(axis=0)
        S = ((R.sum(axis=1) - R.sum(axis=1).mean()) ** 2).sum()
        Ws.append(12 * S / (3 ** 2 * (6 ** 3 - 6)))
        same_top.append(P[1500].idxmax() == P[3000].idxmax())
    out["C5"] = dict(median_W=float(np.median(Ws)), min_W=float(np.min(Ws)), share_same_top_method_1500_vs_3000=float(np.mean(same_top)),
                     decision=("ranking stable across budgets" if np.median(Ws) >= 0.80 else "ranking not stable across budgets"))
    pd.DataFrame(dict(condition_id=sorted(m.condition_id.unique()), kendall_W=Ws)).to_csv(DATA + "/conf_kendall_w.csv", index=False)

    # ---- C6 : Tammes recovery
    rec = {}
    for N in (9, 13, 14, 24):
        cid = [cid for cid, c in conds.items() if c["group"] == "tammes" and c["n"] == N][0]
        g = m[(m.condition_id == cid) & (m.budget == MAIN)]
        rec[N] = dict(best_share=float(g.success_0p1.max()), best_method=g.loc[g.success_0p1.idxmax(), "algorithm"])
    out["C6"] = dict(by_N=rec, decision=("supported" if all(v["best_share"] >= 0.9 for v in rec.values()) else "not supported"))

    # ---- descriptive : time, sweeps used, success
    tt = d.groupby(["budget", "algorithm"]).agg(median_time_s=("time_s", "median"), mean_sweeps_used=("sweeps_used", "mean")).reset_index()
    tt.to_csv(DATA + "/conf_time_by_method.csv", index=False)
    out["reference_types"] = d.groupby("condition_id").reference_type.first().value_counts().to_dict()
    out["n_runs"] = int(len(d))
    out["max_abs_score_vs_recomputed"] = float((d.score - d.recomputed_score).abs().max())
    json.dump(out, open(CONF + "/decisions.json", "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
