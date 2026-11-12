"""confirm_run.py -- confirmatory round: fresh seeds, three budget levels, six methods (resumable per condition).

Usage:  python3 confirm_run.py [--rerun] [--only CID,CID]      writes out/conf/runs_<cid>.csv
Tuned parameters are read from out/conf/tuned_params.json (fixed and hashed before this script is run).
"""
import os
import sys
import json
import time
import numpy as np
import pandas as pd
from multiprocessing import Pool
from algorithms import Problem
import newalgs
import confirm_design as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONF = ROOT + "/out/conf"
PARAM_KEY = {"gd": "pmax", "gdp": "polish_share", "sa": "T0f", "ls": "g0", "lbfgsb": "pmax", "bh": "step"}


def ensure_frozen():
    """The preregistration and its hashes are frozen inputs (code/frozen); copy them into out/conf when absent."""
    import shutil
    os.makedirs(CONF, exist_ok=True)
    for nm in ("PREREGISTRATION.md", "PREREGISTRATION.sha256", "TUNED_AND_ENV.sha256", "packomania_values.csv",
               "PREREGISTRATION_ADDENDUM_1.md", "PREREGISTRATION_MINIROUND.md", "PREREG_ADDENDA.sha256", "RETUNED.sha256",
               "PREREGISTRATION_FOLLOWUP.md", "FOLLOWUP.sha256", "CORRECTION_NOTE_1.md", "CORRECTION.sha256", "FOLLOWUP_RUNTIMES.txt", "PREREGISTRATION_ROUND3.md", "ROUND3.sha256", "ROUND3_START.txt", "ROUND3_END.txt", "PLAN_FILES.sha256"):
        if not os.path.exists(f"{CONF}/{nm}"):
            shutil.copy(os.path.join(os.path.dirname(os.path.abspath(__file__)), "frozen", nm), CONF)


def load_params():
    return json.load(open(CONF + "/tuned_params.json"))["tuned"]


def problem_of(c):
    return Problem("S2" if c["kind"] in ("S2", "S2cap") else c["kind"], c["n"], c["R"])


def run_condition(c):
    params = load_params()
    P = problem_of(c)
    rows = []
    for bi, B in enumerate(C.BUDGETS):
        for seed in C.EVAL_SEEDS:
            X0 = P.initial(np.random.default_rng([seed, c["cid"], 0]))
            for alg, aid in C.ALGS.items():
                kw = {PARAM_KEY[alg]: params[alg]}
                res = newalgs.run_any(alg, P, X0, B * P.sweep, [seed, c["cid"], aid, bi], **kw)
                sc = res["score"]
                rows.append(dict(condition_id=c["cid"], group=c["group"], space=c["kind"], n=c["n"],
                                 R=(c["R"] if c["R"] is not None else float("nan")), area=c["area"], algorithm=alg,
                                 budget=B, seed=seed, score=sc, recomputed_score=res["final_check"],
                                 density=(P.density(sc) if P.ball else float("nan")),
                                 sweeps_used=res["pe"] / P.sweep, time_s=res["time"]))
    return pd.DataFrame(rows)


def _job(c):
    f = f"{CONF}/runs_{c['cid']}.csv"
    t0 = time.time()
    df = run_condition(c)
    df.to_csv(f, index=False)
    return c["cid"], time.time() - t0


def main():
    os.makedirs(CONF, exist_ok=True)
    conds = C.conditions()
    if "--only" in sys.argv:
        keep = {int(x) for x in sys.argv[sys.argv.index("--only") + 1].split(",")}
        conds = [c for c in conds if c["cid"] in keep]
    if "--rerun" not in sys.argv:
        conds = [c for c in conds if not os.path.exists(f"{CONF}/runs_{c['cid']}.csv")]
    conds.sort(key=lambda c: -c["n"])          # longest first
    limit = None
    if "--budget-seconds" in sys.argv:
        limit = float(sys.argv[sys.argv.index("--budget-seconds") + 1])
    t0 = time.time()
    with Pool(2) as pool:
        for cid, dt in pool.imap_unordered(_job, conds):
            print(f"done {cid} in {dt:.0f}s (elapsed {time.time() - t0:.0f}s)", flush=True)
    print("finished", len(conds), "conditions")


if __name__ == "__main__":
    main()
