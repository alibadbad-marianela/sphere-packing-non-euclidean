"""analyze.py -- summary statistics, paired nonparametric tests, hypothesis tests.

Reads data/runs_raw.csv, writes summary and test CSV files into data/.
Significance: Holm-adjusted p < .05 (family = all pairwise tests within one space).
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # folder that contains code/ and out/
OUT = os.path.join(ROOT, "out")
DATA = OUT + "/data"
ALG = ["gd", "sa", "ls"]
PAIRS = [("gd", "sa"), ("gd", "ls"), ("sa", "ls")]
ALPHA = 0.05
PRACTICAL = 0.005   # practical-importance threshold: 0.5% of the reference value


def ci95(x):
    x = np.asarray(x, float)
    n = len(x)
    m = x.mean()
    if n < 2 or x.std(ddof=1) == 0:
        return m, m
    h = stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n)
    return m - h, m + h


def holm(pvals):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    run = 0.0
    for rank, idx in enumerate(order):
        run = max(run, (m - rank) * p[idx])
        adj[idx] = min(run, 1.0)
    return adj


def wilcoxon_paired(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    nz = d[d != 0]
    if len(nz) == 0:
        return dict(W=0.0, p=1.0, rbc=0.0, dz=float("nan"), mean_diff=0.0, ci_lo=0.0, ci_hi=0.0, n_nonzero=0)
    ranks = stats.rankdata(np.abs(nz))
    wpos = ranks[nz > 0].sum()
    wneg = ranks[nz < 0].sum()
    try:
        res = stats.wilcoxon(d, zero_method="wilcox", alternative="two-sided")
        p = float(res.pvalue)
    except ValueError:
        p = 1.0
    sd = d.std(ddof=1)
    lo, hi = ci95(d)
    return dict(W=float(min(wpos, wneg)), p=p, rbc=float((wpos - wneg) / (wpos + wneg)),
                dz=float(d.mean() / sd) if sd > 0 else float("nan"), mean_diff=float(d.mean()),
                ci_lo=float(lo), ci_hi=float(hi), n_nonzero=int(len(nz)))


def main():
    runs = pd.read_csv(f"{DATA}/runs_raw.csv")
    # ---------------------------------------------------------------- summary
    rows = []
    for (sp, cid, n, R, alg), g in runs.groupby(["space", "condition_id", "n", "R", "algorithm"], dropna=False):
        lo, hi = ci95(g["score"])
        rlo, rhi = ci95(g["relative_score"])
        rows.append(dict(space=sp, condition_id=cid, n=n, R=R, algorithm=alg, n_seeds=len(g),
                         mean_score=g["score"].mean(), sd_score=g["score"].std(ddof=1), ci95_lo=lo, ci95_hi=hi,
                         median_score=g["score"].median(), min_score=g["score"].min(), max_score=g["score"].max(),
                         mean_relative=g["relative_score"].mean(), sd_relative=g["relative_score"].std(ddof=1),
                         rel_ci95_lo=rlo, rel_ci95_hi=rhi,
                         reference_type=g["reference_type"].iloc[0], reference_value=g["reference_value"].iloc[0],
                         mean_gap=g["gap_to_reference"].mean(),
                         success_rate_0p1pct=g["success_0.1pct"].mean(), success_rate_1pct=g["success_1pct"].mean(),
                         mean_density=g["density"].mean(), sd_density=g["density"].std(ddof=1),
                         mean_time_s=g["time_s"].mean(), sd_time_s=g["time_s"].std(ddof=1),
                         mean_sweeps_to_99=g["sweeps_to_99pct"].mean(), mean_pair_evals=g["pair_evals"].mean()))
    summ = pd.DataFrame(rows).sort_values(["space", "condition_id", "algorithm"])
    summ.to_csv(f"{DATA}/summary_by_condition.csv", index=False, float_format="%.10g")

    # ---------------------------------------------------------- Friedman + pairwise
    fr_rows, pw_rows, rank_rows = [], [], []
    for (sp, cid, n, R), g in runs.groupby(["space", "condition_id", "n", "R"], dropna=False):
        piv = g.pivot(index="seed", columns="algorithm", values="score")[ALG]
        arr = piv.values
        if np.all(arr == arr[:, [0]]):
            chi, p = 0.0, 1.0
        else:
            chi, p = stats.friedmanchisquare(arr[:, 0], arr[:, 1], arr[:, 2])
        W = chi / (len(arr) * (3 - 1))
        fr_rows.append(dict(space=sp, condition_id=cid, n=n, R=R, n_seeds=len(arr), chi2=float(chi), df=2,
                            p=float(p), kendall_W=float(W)))
        ranks = np.apply_along_axis(lambda r: stats.rankdata(-r), 1, arr)   # rank 1 = highest score
        for k, a in enumerate(ALG):
            rank_rows.append(dict(space=sp, condition_id=cid, n=n, R=R, algorithm=a, mean_rank=float(ranks[:, k].mean())))
        refv = float(g["reference_value"].iloc[0])
        for a, b in PAIRS:
            r = wilcoxon_paired(piv[a].values, piv[b].values)
            dd = piv[a].values - piv[b].values
            r.update(space=sp, condition_id=cid, n=n, R=R, alg_a=a, alg_b=b, mean_rel_diff=float(dd.mean() / refv),
                     share_zero_diff=float(np.mean(dd == 0)), skewness=float(stats.skew(dd)) if dd.std() > 0 else 0.0)
            pw_rows.append(r)
    fr = pd.DataFrame(fr_rows)
    pw = pd.DataFrame(pw_rows)
    pw["p_holm"] = np.nan
    for sp in pw["space"].unique():
        m = pw["space"] == sp
        pw.loc[m, "p_holm"] = holm(pw.loc[m, "p"].values)
    fr["p_holm"] = np.nan
    for sp in fr["space"].unique():
        m = fr["space"] == sp
        fr.loc[m, "p_holm"] = holm(fr.loc[m, "p"].values)
    pw["significant"] = (pw["p_holm"] < ALPHA).astype(int)
    pw["practical"] = (pw["mean_rel_diff"].abs() >= PRACTICAL).astype(int)
    pw["significant_and_practical"] = pw["significant"] * pw["practical"]
    pw["winner"] = np.where(pw["significant"] == 1, np.where(pw["mean_diff"] > 0, pw["alg_a"], pw["alg_b"]), "none")
    fr["significant"] = (fr["p_holm"] < ALPHA).astype(int)
    fr.to_csv(f"{DATA}/test_friedman.csv", index=False, float_format="%.10g")
    pw.to_csv(f"{DATA}/test_pairwise_wilcoxon.csv", index=False, float_format="%.10g")
    ranks_df = pd.DataFrame(rank_rows)
    ranks_df.to_csv(f"{DATA}/mean_ranks.csv", index=False, float_format="%.10g")

    # ---------------------------------------------------------------- hypotheses
    hyp = []
    # H1: does curvature change the algorithm ordering?  per-condition mean paired difference
    # in relative score, S2 conditions versus H2 conditions (Mann-Whitney U), Holm over 3 pairs.
    cm = runs.groupby(["space", "condition_id", "algorithm"])["relative_score"].mean().unstack("algorithm")
    h1 = []
    for a, b in PAIRS:
        d = cm[a] - cm[b]
        s2 = d[d.index.get_level_values("space") == "S2"].values
        h2 = d[d.index.get_level_values("space") == "H2"].values
        u = stats.mannwhitneyu(s2, h2, alternative="two-sided")
        h1.append(dict(hypothesis="H1", test=f"{a}-{b}", n_S2=len(s2), n_H2=len(h2), median_diff_S2=float(np.median(s2)),
                       median_diff_H2=float(np.median(h2)), U=float(u.statistic), p=float(u.pvalue)))
    ph = holm([x["p"] for x in h1])
    for x, pv in zip(h1, ph):
        x["p_holm"] = float(pv)
        x["significant"] = int(pv < ALPHA)
    hyp += h1
    # overall best algorithm per space (mean rank and mean relative score)
    best_rows = []
    for sp in ("S2", "H2", "R2", "S2cap"):
        mr = ranks_df[ranks_df["space"] == sp].groupby("algorithm")["mean_rank"].mean()
        mrel = runs[runs["space"] == sp].groupby("algorithm")["relative_score"].mean()
        wins = pw[(pw["space"] == sp)]
        for a in ALG:
            best_rows.append(dict(space=sp, algorithm=a, mean_rank=float(mr[a]), mean_relative_score=float(mrel[a])))
    pd.DataFrame(best_rows).to_csv(f"{DATA}/overall_by_space.csv", index=False, float_format="%.10g")
    # winners per condition by mean score
    wrows = []
    for (sp, cid, n, R), g in summ.groupby(["space", "condition_id", "n", "R"], dropna=False):
        best = g.sort_values("mean_score", ascending=False).iloc[0]["algorithm"]
        wrows.append(dict(space=sp, condition_id=cid, n=n, R=R, best_mean_algorithm=best))
    pd.DataFrame(wrows).to_csv(f"{DATA}/winner_by_condition.csv", index=False)

    # H1c: common formulation (disks in a geodesic ball) in three curvatures; Kruskal-Wallis on per-setting
    # mean paired differences in relative score, Holm over the 3 pairs; plus best mean-rank algorithm per space.
    if "S2cap" in set(runs.space):
        h1c = []
        for a, b in PAIRS:
            d = cm[a] - cm[b]
            grp = {sp: d[d.index.get_level_values("space") == sp].values for sp in ("S2cap", "R2", "H2")}
            kw = stats.kruskal(grp["S2cap"], grp["R2"], grp["H2"])
            h1c.append(dict(hypothesis="H1c", test=f"{a}-{b} across K=+1,0,-1", median_diff_S2cap=float(np.median(grp["S2cap"])),
                            median_diff_R2=float(np.median(grp["R2"])), median_diff_H2=float(np.median(grp["H2"])),
                            chi2=float(kw.statistic), p=float(kw.pvalue)))
        for x, pv in zip(h1c, holm([x["p"] for x in h1c])):
            x["p_holm"] = float(pv)
            x["significant"] = int(pv < ALPHA)
        hyp += h1c
        # paired setting-level contrasts for GD - SA relative to the Euclidean control (exploratory)
        d = cm["gd"] - cm["sa"]
        e = {sp: d[d.index.get_level_values("space") == sp].values for sp in ("S2cap", "R2", "H2")}
        cons = []
        for sp in ("S2cap", "H2"):
            diff = e[sp] - e["R2"]
            try:
                w = stats.wilcoxon(diff)
                pval = float(w.pvalue)
            except ValueError:
                pval = 1.0
            cons.append(dict(hypothesis="H1c", test=f"GD-SA difference, {sp} minus R2, paired over 6 settings", mean_diff=float(diff.mean()), p=pval))
        for x, pv in zip(cons, holm([x["p"] for x in cons])):
            x["p_holm"] = float(pv)
            x["significant"] = int(pv < ALPHA)
        hyp += cons
        bm = {}
        for sp in ("S2cap", "R2", "H2"):
            mr = ranks_df[ranks_df["space"] == sp].groupby("algorithm")["mean_rank"].mean()
            bm[sp] = str(mr.idxmin())
        hyp.append(dict(hypothesis="H1c", test="best mean-rank algorithm per space (S2cap, R2, H2): " + ", ".join(f"{k}={v}" for k, v in bm.items()),
                        supported=int(len(set(bm.values())) > 1)))
    # H2: scaling with N on S2 (N >= 13): per-seed slope of relative score on log10 N
    big = runs[(runs["space"] == "S2") & (runs["n"] >= 13)]
    slopes = {}
    for a in ALG:
        sl = []
        for seed in sorted(big["seed"].unique()):
            g = big[(big["algorithm"] == a) & (big["seed"] == seed)].sort_values("n")
            sl.append(np.polyfit(np.log10(g["n"].values), g["relative_score"].values, 1)[0])
        slopes[a] = np.array(sl)
    pd.DataFrame(slopes).assign(seed=sorted(big["seed"].unique())).to_csv(f"{DATA}/scaling_slopes_per_seed.csv", index=False, float_format="%.10g")
    h2rows = []
    for a, b in (("ls", "gd"), ("ls", "sa")):
        r = wilcoxon_paired(slopes[a], slopes[b])
        h2rows.append(dict(hypothesis="H2", test=f"slope {a} - slope {b}", mean_slope_a=float(slopes[a].mean()),
                           mean_slope_b=float(slopes[b].mean()), mean_diff=r["mean_diff"], p=r["p"], rbc=r["rbc"], dz=r["dz"]))
    ph = holm([x["p"] for x in h2rows])
    for x, pv in zip(h2rows, ph):
        x["p_holm"] = float(pv)
        x["significant"] = int(pv < ALPHA)
    hyp += h2rows
    ch, cp = stats.friedmanchisquare(slopes["gd"], slopes["sa"], slopes["ls"])
    hyp.append(dict(hypothesis="H2", test="Friedman on slopes", chi2=float(ch), p=float(cp)))
    # runtime scaling exponents
    srows = []
    for a in ALG:
        g = summ[(summ["space"] == "S2") & (summ["algorithm"] == a) & (summ["n"] >= 13)]
        k, c = np.polyfit(np.log10(g["n"].values), np.log10(g["mean_time_s"].values), 1)
        srows.append(dict(algorithm=a, time_exponent=float(k), time_intercept=float(c)))
    pd.DataFrame(srows).to_csv(f"{DATA}/runtime_scaling_exponents.csv", index=False, float_format="%.10g")

    # H3: success on verified optima, N = 4..14
    h3 = []
    small = runs[(runs["space"] == "S2") & (runs["n"] <= 14)]
    for a in ALG:
        sr = small[small["algorithm"] == a].groupby("n")["success_0.1pct"].mean()
        h3.append(dict(hypothesis="H3", test=f"{a}: success rate >= 0.90 at every N in 4..14",
                       min_success_rate=float(sr.min()), n_N_below_0p9=int((sr < 0.9).sum()),
                       supported=int((sr >= 0.9).all())))
    hyp += h3
    pd.DataFrame(hyp).to_csv(f"{DATA}/hypothesis_tests.csv", index=False, float_format="%.10g")

    asm = pw[["space", "n", "R", "alg_a", "alg_b", "n_nonzero", "share_zero_diff", "skewness"]].copy()
    asm["wilcoxon_symmetry_flag"] = (asm["skewness"].abs() > 1.0).astype(int)
    asm.to_csv(f"{DATA}/assumption_checks.csv", index=False, float_format="%.10g")
    # ------------------------------------------------------- derived ball quantities
    from geometry import hyperbolic_ball_area
    arows = []
    for R in (2.0, 3.0, 4.0, 6.0):
        s_total = 2 * np.pi * (1 - np.cos(R)) if R <= np.pi else float("nan")
        s_in = 2 * np.pi * (1 - np.cos(R - 1)) if R <= np.pi else float("nan")
        h_total = 2 * np.pi * (np.cosh(R) - 1)
        h_in = 2 * np.pi * (np.cosh(R - 1) - 1)
        e_total = np.pi * R * R
        e_in = np.pi * (R - 1) ** 2
        arows.append(dict(R=R, spherical_area=s_total, spherical_fraction_within_1_of_boundary=1 - s_in / s_total,
                          hyperbolic_area=h_total, hyperbolic_fraction_within_1_of_boundary=1 - h_in / h_total,
                          euclidean_area=e_total, euclidean_fraction_within_1_of_boundary=1 - e_in / e_total))
    pd.DataFrame(arows).to_csv(f"{DATA}/area_fractions.csv", index=False, float_format="%.10g")
    caps = []
    ball = runs[runs["space"] != "S2"]
    for sp in ("S2cap", "H2", "R2"):
        for R in (2.0, 3.0):
            g = ball[(ball["space"] == sp) & (ball["R"] == R)]
            bestn = g.groupby("n")["score"].max()
            for r0 in (0.4, 0.5):
                ok = bestn[bestn >= r0]
                caps.append(dict(space=sp, R=R, target_radius=r0, largest_tested_n_that_fits=int(ok.index.max()) if len(ok) else 0,
                                 best_radius_at_that_n=float(ok.iloc[-1]) if len(ok) else float("nan")))
    pd.DataFrame(caps).to_csv(f"{DATA}/capacity_fixed_radius.csv", index=False, float_format="%.10g")
    print("analysis finished")


if __name__ == "__main__":
    main()
