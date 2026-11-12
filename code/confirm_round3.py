"""confirm_round3.py -- final preregistered round (PREREGISTRATION_ROUND3.md).

Part A: equal-area balls (3 spaces x 8 areas x 6 numbers of disks = 144 conditions), GD+P and L-BFGS-B, seeds 501-520, 1,500 sweeps -> rule A1 (curvature, C2 settled), A2.
Part B: predictive rule for the number of disks K (count-based problem): K_pred = floor(n_ref (1 - 0.46 b0) + 0.5), 20 new conditions, GD+P, seeds 601-620 -> rule B1.
Usage: python3 confirm_round3.py runA | runB | analyze
Writes out/conf/r3a_runs.csv, r3a_conditions.csv, r3b_design.csv, r3b_scan.csv, r3b_summary.csv, round3_decisions.json.
"""
import sys
import json
import time
import os
import glob
import numpy as np
import pandas as pd
from multiprocessing import Pool
from algorithms import Problem
import newalgs
import confirm_design as C
import confirm_mini as M
import confirm_followup as F
from confirm_run import CONF

SEEDS_A = list(range(501, 521))
SEEDS_B = list(range(601, 621))
AREAS = [2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0]
NS = [8, 12, 16, 20, 24, 32]
BUDGET = 1500
LAMBDA = 0.46
R0S_B = [0.25, 0.35]
B0S_B = [0.375, 0.425, 0.475, 0.525]
AID = {"gdp": 4, "lbfgsb": 5}


def conditions_A():
    out, cid = [], 4000
    for kind in ("R2", "H2", "S2cap"):
        for A in AREAS:
            for n in NS:
                out.append(dict(cid=cid, space=kind, area=A, n=n, R=C.radius_for_area(kind, A)))
                cid += 1
    return out


def job_A(c):
    t0 = time.time()
    par = json.load(open(CONF + "/tuned_params_retuned.json"))["tuned"]["lbfgsb"]
    P = Problem("S2" if c["space"] == "S2cap" else c["space"], c["n"], c["R"])
    rows = []
    for seed in SEEDS_A:
        X0 = P.initial(np.random.default_rng([seed, c["cid"], 0]))
        for m in ("gdp", "lbfgsb"):
            kw = {"polish_share": 0.25} if m == "gdp" else {"pmax": par}
            res = newalgs.run_any(m, P, X0, BUDGET * P.sweep, [seed, c["cid"], AID[m], 0], **kw)
            rows.append(dict(cid=c["cid"], space=c["space"], area=c["area"], n=c["n"], R=c["R"], method=m, seed=seed, score=res["score"], recomputed=res["final_check"], time_s=res["time"]))
    pd.DataFrame(rows).to_csv(f"{CONF}/r3a_runs_{c['cid']}.csv", index=False)
    return c["cid"], time.time() - t0


def runA():
    cs = [c for c in conditions_A() if not os.path.exists(f"{CONF}/r3a_runs_{c['cid']}.csv")]
    cs.sort(key=lambda c: -c["n"])
    with Pool(2) as pool:
        for cid, dt in pool.imap_unordered(job_A, cs):
            print("A done", cid, f"{dt:.0f}s", flush=True)


def design_B():
    rows, cid = [], 5000
    for kind in ("R2", "H2", "S2cap"):
        for r0 in ([0.30] if kind == "R2" else R0S_B):
            for b0 in B0S_B:
                R = M.radius_for_b(kind, r0, b0)
                A = C.area(kind, R)
                rows.append(dict(cid=cid, space=kind, r0=r0, b0=b0, R=R, area=A, n_ref=int(np.floor(C.ref_density(kind, r0) * A / C.area(kind, r0)))))
                cid += 1
    return pd.DataFrame(rows)


def runB():
    d = design_B()
    d.to_csv(CONF + "/r3b_design.csv", index=False)
    jobs = [(r, "gdp", SEEDS_B) for _, r in d.sort_values("n_ref", ascending=False).iterrows()]
    scans, out = [], []
    with Pool(2) as pool:
        for cid, m, K, rows, dt in pool.imap_unordered(F.scan, jobs):
            print(f"B done {cid} K={K} in {dt:.0f}s", flush=True)
            out.append(dict(cid=cid, K=K))
            scans += rows
    pd.DataFrame(scans).sort_values(["cid", "n", "seed"]).to_csv(CONF + "/r3b_scan.csv", index=False)
    s = d.merge(pd.DataFrame(out), on="cid")
    s["K_pred"] = np.floor(s.n_ref * (1 - LAMBDA * s.b0) + 0.5).astype(int)
    s["deficit0"] = [1 - r.K * C.area(r.space, r.r0) / (r.area * C.ref_density(r.space, r.r0)) for r in s.itertuples()]
    s.to_csv(CONF + "/r3b_summary.csv", index=False)


def analyze():
    rng = np.random.default_rng(20261030)
    d = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(CONF + "/r3a_runs_*.csv"))], ignore_index=True)
    d.to_csv(CONF + "/r3a_runs.csv", index=False)
    cond = d.groupby(["cid", "space", "area", "n", "R", "method"]).score.mean().reset_index()
    best = cond.loc[cond.groupby("cid").score.idxmax()].rename(columns={"score": "r_best", "method": "best_method"})
    best["deficit"] = [C.deficit(r.space, r.R, r.n, r.r_best) for r in best.itertuples()]
    best["b"] = [C.boundary_share(r.space, r.R, r.r_best) for r in best.itertuples()]
    best["cell"] = best.area.astype(str) + "_" + best.n.astype(str)
    n_excluded = int(best.deficit.isna().sum())      # conditions whose reference density is undefined (none expected)
    best = best[best.deficit.notna()].copy()
    best.to_csv(CONF + "/r3a_conditions.csv", index=False)

    def fit(t):
        X = np.c_[np.ones(len(t)), t.b, (t.space == "H2"), (t.space == "S2cap")].astype(float)
        return np.linalg.lstsq(X, t.deficit.values, rcond=None)[0], X
    beta, X = fit(best)
    res = best.deficit.values - X @ beta
    sig = float(np.sqrt(res @ res / (len(best) - 4)))
    cells = best.cell.unique()
    groups = {c: best[best.cell == c] for c in cells}
    bs = []
    for _ in range(10000):
        pick = rng.choice(cells, len(cells))
        t = pd.concat([groups[c] for c in pick], ignore_index=True)
        try:
            bs.append(fit(t)[0])
        except np.linalg.LinAlgError:
            pass
    bs = np.array(bs)
    lo_h, hi_h = np.percentile(bs[:, 2], [2.5, 97.5])
    lo_s, hi_s = np.percentile(bs[:, 3], [2.5, 97.5])
    rule = lambda g, lo, hi: "curvature adds a detectable deficit" if (lo > 0 and g >= 0.02) else ("no detectable curvature effect" if (lo >= -0.02 and hi <= 0.02) else "inconclusive")
    out = dict(A1=dict(n_excluded=n_excluded, n_conditions=len(best), n_cells=len(cells), intercept=float(beta[0]), beta_b=float(beta[1]), g_H=float(beta[2]), g_H_ci=[float(lo_h), float(hi_h)], g_S=float(beta[3]), g_S_ci=[float(lo_s), float(hi_s)],
                      residual_sd=sig, decision=rule(beta[2], lo_h, hi_h), decision_cap_secondary=rule(beta[3], lo_s, hi_s)))
    # A2: paired differences at the same area and n
    pv = best.pivot_table(index=["area", "n"], columns="space", values="deficit")
    dh, ds = (pv.H2 - pv.R2).dropna(), (pv.S2cap - pv.R2).dropna()
    def cell_boot(x):
        v = x.values
        m = [np.mean(rng.choice(v, len(v))) for _ in range(10000)]
        return float(v.mean()), [float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]
    out["A2"] = dict(hyperbolic_minus_euclid=dict(zip(("mean", "ci95"), cell_boot(dh))), cap_minus_euclid=dict(zip(("mean", "ci95"), cell_boot(ds))), n_cells_H=len(dh), n_cells_S=len(ds))
    out["A_methods"] = dict(best_method_counts=best.best_method.value_counts().to_dict(), max_abs_score_vs_recomputed=float((d.score - d.recomputed).abs().max()), n_runs=int(len(d)))
    # B
    s = pd.read_csv(CONF + "/r3b_summary.csv")
    e = s.K - s.K_pred
    ab = e.abs()
    within1, mae, rmae = float((ab <= 1).mean()), float(ab.mean()), float((ab / s.K.clip(lower=1)).mean())
    bias = {k: float(v) for k, v in e.groupby(s.space).mean().items()}
    ok = within1 >= 0.80 and mae <= 1.0 and rmae <= 0.10 and all(abs(v) <= 1.0 for v in bias.values())
    bad = within1 < 0.60 or mae > 1.5
    out["B1"] = dict(n_conditions=len(s), share_within_1=within1, share_exact=float((e == 0).mean()), mean_abs_error_disks=mae, mean_rel_error=rmae, mean_signed_error_by_space=bias,
                     decision="supported" if ok else ("not supported" if bad else "inconclusive"))
    json.dump(out, open(CONF + "/round3_decisions.json", "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    {"runA": runA, "runB": runB, "analyze": analyze}[sys.argv[1]]()
