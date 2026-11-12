"""confirm_followup.py -- follow-up to the mini-round (PREREGISTRATION_FOLLOWUP.md): design, runs with two methods, and rules F1 to F3.

Usage: python3 confirm_followup.py run | run_mini_lbfgsb | analyze
Writes out/conf/followup_design.csv, followup_scan.csv, followup_summary.csv, followup_decisions.json,
mini_lbfgsb_scan.csv (exploratory: L-BFGS-B on the 18 mini-round conditions).
"""
import sys
import json
import time
import numpy as np
import pandas as pd
from multiprocessing import Pool
from scipy import stats
from algorithms import Problem
import newalgs
import confirm_design as C
import confirm_mini as M
from confirm_run import CONF

SEEDS = list(range(401, 421))
R0S = [0.20, 0.30, 0.40]
B0S = [0.35, 0.40, 0.45, 0.50, 0.55]
BUDGET = 1500
AID = {"gdp": 4, "lbfgsb": 5}


def design():
    rows, cid = [], 3000
    for kind, lab in (("R2", "Euclidean"), ("H2", "hyperbolic"), ("S2cap", "cap")):
        for r0 in R0S:
            if kind == "R2" and r0 != 0.30:
                continue
            for b0 in B0S:
                if b0 == 0.35 and r0 == 0.40:
                    continue
                R = M.radius_for_b(kind, r0, b0)
                A = C.area(kind, R)
                rows.append(dict(cid=cid, space=kind, label=lab, r0=r0, b0=b0, R=R, area=A, n_ref=int(np.floor(C.ref_density(kind, r0) * A / C.area(kind, r0)))))
                cid += 1
    return pd.DataFrame(rows)


def one(c, n, seed, method, par):
    P = Problem("S2" if c["space"] == "S2cap" else c["space"], n, c["R"])
    X0 = P.initial(np.random.default_rng([seed, c["cid"], n]))
    kw = {"polish_share": 0.25} if method == "gdp" else {"pmax": par}
    return newalgs.run_any(method, P, X0, BUDGET * P.sweep, [seed, c["cid"], n, AID[method]], **kw)["score"]


def scan(job):
    c, method, seeds = job
    par = json.load(open(CONF + "/tuned_params_retuned.json"))["tuned"]["lbfgsb"]
    t0, rows, K = time.time(), [], 0
    for n in range(int(c["n_ref"]), 0, -1):
        ok = fail = 0
        for seed in seeds:
            sc = one(c, n, seed, method, par)
            hit = sc >= c["r0"] - 1e-9
            ok += hit
            fail += (not hit)
            rows.append(dict(cid=c["cid"], method=method, n=n, seed=seed, score=sc, success=int(hit)))
            if ok >= M.NEED or fail > len(seeds) - M.NEED:
                break
        if ok >= M.NEED:
            K = n
            break
    return c["cid"], method, K, rows, time.time() - t0


def _run(d, seeds, tag):
    jobs = [(r, m, seeds) for _, r in d.sort_values("n_ref", ascending=False).iterrows() for m in ("gdp", "lbfgsb")]
    out, scans = [], []
    with Pool(2) as pool:
        for cid, m, K, rows, dt in pool.imap_unordered(scan, jobs):
            print(f"done {cid} {m} K={K} in {dt:.0f}s", flush=True)
            out.append(dict(cid=cid, method=m, K=K))
            scans += rows
    pd.DataFrame(scans).sort_values(["cid", "method", "n", "seed"]).to_csv(f"{CONF}/{tag}_scan.csv", index=False)
    k = pd.DataFrame(out).pivot(index="cid", columns="method", values="K").reset_index().rename(columns={"gdp": "K_gdp", "lbfgsb": "K_lbfgsb"})
    s = d.merge(k, on="cid")
    s["K"] = s[["K_gdp", "K_lbfgsb"]].max(axis=1)
    for col, kk in (("deficit0", "K"), ("deficit0_gdp", "K_gdp"), ("deficit0_lbfgsb", "K_lbfgsb")):
        s[col] = [1 - getattr(r, kk) * C.area(r.space, r.r0) / (r.area * C.ref_density(r.space, r.r0)) for r in s.itertuples()]
    return s


def run():
    d = design()
    d.to_csv(CONF + "/followup_design.csv", index=False)
    _run(d, SEEDS, "followup").to_csv(CONF + "/followup_summary.csv", index=False)


def run_mini_lbfgsb():
    d = pd.read_csv(CONF + "/mini_design.csv")
    _run(d, M.SEEDS, "mini_lbfgsb").to_csv(CONF + "/mini_lbfgsb_summary.csv", index=False)


def rules(s, kcol="deficit0", r0dummies=True, euclid_baseline=True):
    """F1-F3 on a summary table with columns space, r0, b0 and a deficit column."""
    out = {}
    y = s[kcol].values
    rho, p = M.perm_p(s.b0.values, y)
    out["F1"] = dict(n=len(s), spearman=rho, perm_p_one_sided=p, decision="supported" if (rho >= .5 and p < .05) else ("not supported" if rho < .2 else "inconclusive"))
    cols = [np.ones(len(s)), s.b0, (s.space == "H2").astype(float), (s.space == "S2cap").astype(float)]
    names = ["a", "b0", "g_H", "g_S"]
    r0s = sorted(s.r0.unique())
    if len(r0s) > 1:
        base = 0.30 if 0.30 in r0s else r0s[0]
        for v in r0s:
            if v != base:
                cols.append((s.r0 == v).astype(float))
                names.append(f"e_{v:.2f}")
    X = np.column_stack(cols)
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    res = y - X @ beta
    df = len(y) - np.linalg.matrix_rank(X)
    se = np.sqrt(np.diag(res @ res / df * np.linalg.pinv(X.T @ X)))
    tq = stats.t.ppf(.975, df)
    def rule(i):
        lo, hi = beta[i] - tq * se[i], beta[i] + tq * se[i]
        if (lo > 0 or hi < 0) and abs(beta[i]) >= .05:
            return "detectable curvature effect"
        return "no detectable curvature effect" if (lo >= -.05 and hi <= .05) else "inconclusive"
    out["F2"] = dict(df=int(df), terms={n: float(b) for n, b in zip(names, beta)}, g_H_ci=[float(beta[2] - tq * se[2]), float(beta[2] + tq * se[2])],
                     g_S_ci=[float(beta[3] - tq * se[3]), float(beta[3] + tq * se[3])], decision=rule(2), decision_cap_secondary=rule(3))
    e = s[s.space == "R2"]
    lam = float((e.b0 * e[kcol]).sum() / (e.b0 ** 2).sum())
    o = s[s.space != "R2"]
    err = float(np.mean(np.abs(o[kcol] - lam * o.b0)))
    out["F3"] = dict(n_euclid=len(e), n_other=len(o), lambda_euclid=lam, mean_abs_error=err,
                     mae_by_space={k: float(v) for k, v in (o[kcol] - lam * o.b0).abs().groupby(o.space).mean().items()},
                     decision="describes the other spaces" if err <= .05 else ("does not" if err > .10 else "inconclusive"))
    return out


def analyze():
    s = pd.read_csv(CONF + "/followup_summary.csv")
    out = dict(primary=rules(s, "deficit0"), gdp_only=rules(s, "deficit0_gdp"), lbfgsb_only=rules(s, "deficit0_lbfgsb"))
    out["method_comparison"] = dict(lbfgsb_larger=int((s.K_lbfgsb > s.K_gdp).sum()), equal=int((s.K_lbfgsb == s.K_gdp).sum()), lbfgsb_smaller=int((s.K_lbfgsb < s.K_gdp).sum()), n=len(s),
                                    mean_K_gdp=float(s.K_gdp.mean()), mean_K_lbfgsb=float(s.K_lbfgsb.mean()))
    m = pd.read_csv(CONF + "/mini_summary.csv")
    md = m[~((m.space == "R2") & (m.r0 == 0.40))]
    out["mini_without_euclid_duplicates"] = rules(md, "deficit0")
    try:
        ml = pd.read_csv(CONF + "/mini_lbfgsb_summary.csv")
        m2 = m.merge(ml[["cid", "K_lbfgsb"]], on="cid")
        m2["K2"] = m2[["K", "K_lbfgsb"]].max(axis=1)
        m2["deficit0_best"] = [1 - r.K2 * C.area(r.space, r.r0) / (r.area * C.ref_density(r.space, r.r0)) for r in m2.itertuples()]
        m2.to_csv(CONF + "/mini_both_methods_summary.csv", index=False)
        out["mini_both_methods"] = dict(rules=rules(m2[~((m2.space == "R2") & (m2.r0 == 0.40))], "deficit0_best"), lbfgsb_larger=int((m2.K_lbfgsb > m2.K).sum()), equal=int((m2.K_lbfgsb == m2.K).sum()), lbfgsb_smaller=int((m2.K_lbfgsb < m2.K).sum()))
    except FileNotFoundError:
        pass
    # pooled, distinct conditions: mini (without duplicates, GD+P K) + follow-up (primary K); a condition appearing in both (same space, r0, b0) is taken from the follow-up
    key = lambda d: set(zip(d.space, d.r0.round(3), d.b0.round(3)))
    extra = md[[k not in key(s) for k in zip(md.space, md.r0.round(3), md.b0.round(3))]]
    pool = pd.concat([s[["space", "r0", "b0", "deficit0"]], extra[["space", "r0", "b0", "deficit0"]]], ignore_index=True)
    out["pooled_distinct"] = rules(pool, "deficit0")
    json.dump(out, open(CONF + "/followup_decisions.json", "w"), indent=1, default=float)
    print(json.dumps({k: (v if k not in ("gdp_only", "lbfgsb_only") else "...") for k, v in out.items()}, indent=1, default=float))


if __name__ == "__main__":
    {"run": run, "run_mini_lbfgsb": run_mini_lbfgsb, "analyze": analyze}[sys.argv[1]]()
