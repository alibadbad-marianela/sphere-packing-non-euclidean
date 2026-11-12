"""confirm_configs.py -- rerun of the confirmatory round (same seeds, parameters, budgets) that SAVES the final configuration of every run.

Writes out/conf/configs/cfg_<cid>.npz (array X[budget, seed, method, n, dim]) and out/conf/walls_<cid>.csv (wall metrics, ball conditions).
Every score of the rerun must equal the stored score of runs_<cid>.csv to within 1e-9 (assertion; the maximum difference is written to configs/check.csv).
Wall metrics (exploratory, ADDENDUM 1, section 3): for a run with disk radius r, g_i = R - rho_i - r is the gap between disk i and the wall limit;
disk i touches the wall if g_i <= 0.01 r; a wall-ring run has g_i <= r for every disk.
"""
import os
import sys
import time
import numpy as np
import pandas as pd
from multiprocessing import Pool
import newalgs
import confirm_design as C
from confirm_run import CONF, PARAM_KEY, load_params, problem_of

OUTD = CONF + "/configs"


def job(c):
    t0 = time.time()
    params = load_params()
    P = problem_of(c)
    old = pd.read_csv(f"{CONF}/runs_{c['cid']}.csv")
    algs = list(C.ALGS)
    dim = 2 if c["kind"] == "R2" else 3
    X = np.full((len(C.BUDGETS), len(C.EVAL_SEEDS), len(algs), c["n"], dim), np.nan)
    rows, maxdiff = [], 0.0
    for bi, B in enumerate(C.BUDGETS):
        for si, seed in enumerate(C.EVAL_SEEDS):
            X0 = P.initial(np.random.default_rng([seed, c["cid"], 0]))
            for ai, alg in enumerate(algs):
                res = newalgs.run_any(alg, P, X0, B * P.sweep, [seed, c["cid"], C.ALGS[alg], bi], **{PARAM_KEY[alg]: params[alg]})
                X[bi, si, ai] = res["X"]
                sc0 = float(old[(old.budget == B) & (old.seed == seed) & (old.algorithm == alg)].score.iloc[0])
                maxdiff = max(maxdiff, abs(res["score"] - sc0))
                if P.ball:
                    r = res["score"]
                    g = c["R"] - P.space.rho(res["X"]) - r
                    rows.append(dict(condition_id=c["cid"], algorithm=alg, budget=B, seed=seed, score=r,
                                     touch_share=float(np.mean(g <= 0.01 * r)), ring=int(np.all(g <= r)), max_gap_over_r=float(g.max() / r)))
    assert maxdiff <= 1e-9, (c["cid"], maxdiff)
    np.savez_compressed(f"{OUTD}/cfg_{c['cid']}.npz", X=X, budgets=C.BUDGETS, seeds=C.EVAL_SEEDS, algs=algs)
    if rows:
        pd.DataFrame(rows).to_csv(f"{CONF}/walls_{c['cid']}.csv", index=False)
    return c["cid"], maxdiff, time.time() - t0


def main():
    os.makedirs(OUTD, exist_ok=True)
    conds = [c for c in C.conditions() if not os.path.exists(f"{OUTD}/cfg_{c['cid']}.npz")]
    conds.sort(key=lambda c: -c["n"])
    res = []
    with Pool(2) as pool:
        for cid, md, dt in pool.imap_unordered(job, conds):
            print(f"done {cid} maxdiff {md:.1e} in {dt:.0f}s", flush=True)
    allc = []
    for c in C.conditions():
        allc.append(c["cid"])
    print("finished")


if __name__ == "__main__":
    main()
