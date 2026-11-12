"""confirm_tune.py -- equal-effort tuning of all six methods on pilot seeds (never used for evaluation).

Each method has ONE tuned parameter with the same number of candidate settings (six); every setting is run on the same
pilot conditions and pilot seeds at the main budget; the setting with the highest mean relative score
(score / best score seen in that pilot condition over all settings and methods) is kept.
Writes out/conf/tuning_runs.csv and out/conf/tuned_params.json.
"""
import os
import json
import numpy as np
import pandas as pd
from multiprocessing import Pool
from algorithms import Problem
import newalgs
import confirm_design as C
from confirm_run import PARAM_KEY, CONF

GRID = {"gd": [40, 80, 150, 250, 400, 700], "gdp": [0.05, 0.10, 0.15, 0.25, 0.35, 0.50], "sa": [0.005, 0.01, 0.02, 0.04, 0.08, 0.16],
        "ls": [0.10, 0.15, 0.25, 0.35, 0.50, 0.70], "lbfgsb": [40, 80, 150, 250, 400, 700], "bh": [0.05, 0.10, 0.20, 0.40, 0.80, 1.50]}
PILOT = [("S2", 11, None), ("S2", 33, None), ("H2", 16, C.radius_for_area("H2", 8.0)), ("R2", 16, C.radius_for_area("R2", 8.0))]


def job(args):
    alg, val, ci, seed = args
    kind, n, R = PILOT[ci]
    P = Problem(kind, n, R)
    X0 = P.initial(np.random.default_rng([seed, 77, ci]))
    res = newalgs.run_any(alg, P, X0, C.MAIN_BUDGET * P.sweep, [seed, 77, ci, C.ALGS[alg]], **{PARAM_KEY[alg]: val})
    return dict(algorithm=alg, value=val, pilot=ci, seed=seed, score=res["score"], time_s=res["time"])


def main():
    tasks = [(a, v, ci, s) for a, g in GRID.items() for v in g for ci in range(len(PILOT)) for s in C.PILOT_SEEDS]
    with Pool(2) as pool:
        rows = pool.map(job, tasks, chunksize=4)
    d = pd.DataFrame(rows)
    d["rel"] = d.score / d.groupby("pilot").score.transform("max")
    d.to_csv(CONF + "/tuning_runs.csv", index=False)
    m = d.groupby(["algorithm", "value"]).rel.mean().reset_index()
    tuned = {}
    for a, g in m.groupby("algorithm"):
        tuned[a] = float(g.loc[g.rel.idxmax(), "value"])
    json.dump(dict(tuned=tuned, grids=GRID, pilot_seeds=C.PILOT_SEEDS, pilot_conditions=[list(map(str, p)) for p in PILOT],
                   budget_sweeps=C.MAIN_BUDGET, mean_relative_by_setting=m.round(5).to_dict("records")), open(CONF + "/tuned_params.json", "w"), indent=1)
    print(m.pivot(index="value", columns="algorithm", values="rel").round(4) if False else tuned)


if __name__ == "__main__":
    os.makedirs(CONF, exist_ok=True)
    main()
