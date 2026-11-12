"""confirm_retune.py -- extended candidate grids for compression (ls) and L-BFGS-B (ADDENDUM 1, section 4).

Runs only the NEW settings on the same pilot conditions and seeds as confirm_tune.py, combines them with the stored original pilot runs,
and selects by the same rule (mean score / best pilot score over all settings and methods). Writes out/conf/tuning_runs_extended.csv and tuned_params_retuned.json.
"""
import json
import numpy as np
import pandas as pd
from multiprocessing import Pool
import confirm_design as C
import confirm_tune as T
from confirm_run import CONF

NEW = {"ls": [1.0, 1.4, 2.0], "lbfgsb": [1000, 1500, 2500]}


def main():
    tasks = [(a, v, ci, s) for a, g in NEW.items() for v in g for ci in range(len(T.PILOT)) for s in C.PILOT_SEEDS]
    with Pool(2) as pool:
        rows = pool.map(T.job, tasks, chunksize=2)
    new = pd.DataFrame(rows)
    old = pd.read_csv(CONF + "/tuning_runs.csv").drop(columns=["rel"])
    d = pd.concat([old, new], ignore_index=True)
    d["rel"] = d.score / d.groupby("pilot").score.transform("max")
    d.to_csv(CONF + "/tuning_runs_extended.csv", index=False)
    m = d.groupby(["algorithm", "value"]).rel.mean().reset_index()
    tuned = json.load(open(CONF + "/tuned_params.json"))["tuned"]
    for a in NEW:
        g = m[m.algorithm == a]
        tuned[a] = float(g.loc[g.rel.idxmax(), "value"])
    grids = {a: sorted(m[m.algorithm == a].value.tolist()) for a in NEW}
    json.dump(dict(tuned=tuned, extended_grids=grids, mean_relative_by_setting=m[m.algorithm.isin(NEW)].round(5).to_dict("records"),
                   at_upper_edge={a: bool(tuned[a] == max(grids[a])) for a in NEW}), open(CONF + "/tuned_params_retuned.json", "w"), indent=1)
    print(m[m.algorithm.isin(NEW)].round(4).to_string(), tuned)


if __name__ == "__main__":
    main()
