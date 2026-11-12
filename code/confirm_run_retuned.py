"""confirm_run_retuned.py -- compression (ls) and L-BFGS-B rerun with the re-tuned parameters (tuned_params_retuned.json, hashed before this script ran).
Same conditions, seeds, starting configurations, random streams, and budgets as confirm_run.py. Writes out/conf/retuned/runs_<cid>.csv.
"""
import os
import json
import time
import numpy as np
import pandas as pd
from multiprocessing import Pool
import newalgs
import confirm_design as C
from confirm_run import CONF, PARAM_KEY, problem_of

OUTD = CONF + "/retuned"
ALGS = ["ls", "lbfgsb"]


def job(c):
    t0 = time.time()
    par = json.load(open(CONF + "/tuned_params_retuned.json"))["tuned"]
    P = problem_of(c)
    rows = []
    for bi, B in enumerate(C.BUDGETS):
        for seed in C.EVAL_SEEDS:
            X0 = P.initial(np.random.default_rng([seed, c["cid"], 0]))
            for alg in ALGS:
                res = newalgs.run_any(alg, P, X0, B * P.sweep, [seed, c["cid"], C.ALGS[alg], bi], **{PARAM_KEY[alg]: par[alg]})
                rows.append(dict(condition_id=c["cid"], algorithm=alg, budget=B, seed=seed, score=res["score"], recomputed_score=res["final_check"],
                                 sweeps_used=res["pe"] / P.sweep, time_s=res["time"]))
    pd.DataFrame(rows).to_csv(f"{OUTD}/runs_{c['cid']}.csv", index=False)
    return c["cid"], time.time() - t0


if __name__ == "__main__":
    os.makedirs(OUTD, exist_ok=True)
    cs = sorted([c for c in C.conditions() if not os.path.exists(f"{OUTD}/runs_{c['cid']}.csv")], key=lambda c: -c["n"])
    with Pool(2) as pool:
        for cid, dt in pool.imap_unordered(job, cs):
            print("done", cid, f"{dt:.0f}s", flush=True)
    print("finished")
