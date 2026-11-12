"""confirm_mini.py -- matched-boundary mini-round (PREREGISTRATION_MINIROUND.md): design, runs, and the rules M1 to M3.

Usage: python3 confirm_mini.py run | analyze
Writes out/conf/mini_design.csv, mini_scan.csv, mini_summary.csv, mini_decisions.json.
"""
import os
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
from confirm_run import CONF

SEEDS = list(range(301, 321))
R0S = [0.30, 0.40]
B0S = [0.40, 0.45, 0.50]
SPACES = [("R2", "Euclidean"), ("H2", "hyperbolic"), ("S2cap", "cap")]
BUDGET = 1500
POLISH = 0.25            # as tuned in the confirmatory round (fixed by the mini-round preregistration)
NEED = 10                # successes needed out of 20 seeds


def radius_for_b(kind, r, b0):
    hi = {"R2": 200.0, "H2": 40.0, "S2cap": np.pi - 1e-9}[kind]
    lo = r * (1 + 1e-9)
    f = lambda R: C.boundary_share(kind, R, r) - b0
    if f(lo) < 0 or f(hi) > 0:
        raise ValueError((kind, r, b0))
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)


def design():
    rows, cid = [], 2000
    for r0 in R0S:
        for b0 in B0S:
            for kind, lab in SPACES:
                R = radius_for_b(kind, r0, b0)
                A = C.area(kind, R)
                nref = int(np.floor(C.ref_density(kind, r0) * A / C.area(kind, r0)))
                rows.append(dict(cid=cid, space=kind, label=lab, r0=r0, b0=b0, R=R, area=A, n_ref=nref))
                cid += 1
    return pd.DataFrame(rows)


def one(c, n, seed):
    P = Problem("S2" if c["space"] == "S2cap" else c["space"], n, c["R"])
    X0 = P.initial(np.random.default_rng([seed, c["cid"], n]))
    res = newalgs.run_any("gdp", P, X0, BUDGET * P.sweep, [seed, c["cid"], n, 4], polish_share=POLISH)
    return res["score"]


def scan(c):
    t0 = time.time()
    rows, K = [], 0
    for n in range(int(c["n_ref"]), 0, -1):
        ok, fail = 0, 0
        for seed in SEEDS:
            sc = one(c, n, seed)
            hit = sc >= c["r0"] - 1e-9
            ok += hit
            fail += (not hit)
            rows.append(dict(cid=c["cid"], n=n, seed=seed, score=sc, success=int(hit)))
            if ok >= NEED or fail > len(SEEDS) - NEED:      # decided; remaining seeds cannot change the verdict
                break
        if ok >= NEED:
            K = n
            break
    return c["cid"], K, rows, time.time() - t0


def run():
    d = design()
    d.to_csv(CONF + "/mini_design.csv", index=False)
    cs = [r for _, r in d.sort_values("n_ref", ascending=False).iterrows()]
    out, scans = [], []
    with Pool(2) as pool:
        for cid, K, rows, dt in pool.imap_unordered(scan, cs):
            print(f"done {cid} K={K} in {dt:.0f}s", flush=True)
            out.append(dict(cid=cid, K=K))
            scans += rows
    pd.DataFrame(scans).sort_values(["cid", "n", "seed"]).to_csv(CONF + "/mini_scan.csv", index=False)
    s = d.merge(pd.DataFrame(out), on="cid")
    s["deficit0"] = [1 - r.K * C.area(r.space, r.r0) / (r.area * C.ref_density(r.space, r.r0)) for r in s.itertuples()]
    s.to_csv(CONF + "/mini_summary.csv", index=False)


def perm_p(x, y, nperm=20000, seed=7):
    rng = np.random.default_rng(seed)
    rho = stats.spearmanr(x, y)[0]
    cnt = sum(stats.spearmanr(x, rng.permutation(y))[0] >= rho - 1e-12 for _ in range(nperm))
    return float(rho), float((cnt + 1) / (nperm + 1))


def analyze():
    s = pd.read_csv(CONF + "/mini_summary.csv")
    out = {}
    rho, p = perm_p(s.b0.values, s.deficit0.values)
    out["M1"] = dict(spearman=rho, perm_p_one_sided=p, decision="supported" if (rho >= .5 and p < .05) else ("not supported" if rho < .2 else "inconclusive"))
    X = np.column_stack([np.ones(len(s)), s.b0, (s.space == "H2").astype(float), (s.space == "S2cap").astype(float), (s.r0 == 0.40).astype(float)])
    y = s.deficit0.values
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    df = len(y) - X.shape[1]
    cov = res @ res / df * np.linalg.inv(X.T @ X)
    tq = stats.t.ppf(0.975, df)
    se = np.sqrt(np.diag(cov))
    ci = lambda i: [float(beta[i] - tq * se[i]), float(beta[i] + tq * se[i])]
    def rule(i):
        lo, hi = ci(i)
        if (lo > 0 or hi < 0) and abs(beta[i]) >= .05:
            return "detectable curvature effect"
        if lo >= -.05 and hi <= .05:
            return "no detectable curvature effect"
        return "inconclusive"
    out["M2"] = dict(df=int(df), beta_b0=float(beta[1]), g_H=float(beta[2]), g_H_ci=ci(2), g_S=float(beta[3]), g_S_ci=ci(3), e_r0=float(beta[4]),
                     decision=rule(2), decision_cap_secondary=rule(3))
    e = s[s.space == "R2"]
    lam = float((e.b0 * e.deficit0).sum() / (e.b0 ** 2).sum())
    o = s[s.space != "R2"]
    err = float(np.mean(np.abs(o.deficit0 - lam * o.b0)))
    out["M3"] = dict(lambda_euclid=lam, mean_abs_error=err, decision="describes the other spaces" if err <= .05 else ("does not" if err > .10 else "inconclusive"))
    out["K_by_space"] = {k: [int(v) for v in g.K] for k, g in s.groupby("space")}
    json.dump(out, open(CONF + "/mini_decisions.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    {"run": run, "analyze": analyze}[sys.argv[1]]()
