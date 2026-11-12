"""confirm_count.py -- count-based version of the disk problem (original element; exploratory).

For a ball of given area in each space and a fixed disk radius r, K = the largest n for which gradient descent with a polishing step
(GD+P, 1,500 sweeps) reaches a disk radius >= r in at least half of 20 fresh seeds (201-220).  n is scanned downward from
n_ref = floor(rho*(r) Area(R) / Area(r)), the number of disks that would fit if the ball were packed at the infinite-space reference density
(a heuristic ceiling, not a theorem for a bounded ball).  Writes out/conf/count_runs.csv and out/conf/count_summary.csv.
"""
import os
import numpy as np
import pandas as pd
from multiprocessing import Pool
from algorithms import Problem
import newalgs
import confirm_design as C
from confirm_run import CONF, load_params

SEEDS = list(range(201, 221))
RADIUS = 0.30
AREAS = [6.0, 12.0]
KINDS = [("S2cap", "cap"), ("R2", "Euclidean"), ("H2", "hyperbolic")]


def job(args):
    kind, A, n, seed = args
    R = C.radius_for_area(kind, A)
    P = Problem("S2" if kind == "S2cap" else kind, n, R)
    X0 = P.initial(np.random.default_rng([seed, 9, n, int(A)]))
    res = newalgs.run_any("gdp", P, X0, C.MAIN_BUDGET * P.sweep, [seed, 9, n, int(A)], polish_share=load_params()["gdp"])
    return dict(space=kind, area=A, n=n, seed=seed, score=res["score"], reached=int(res["score"] >= RADIUS))


def main():
    rows, summ = [], []
    with Pool(2) as pool:
        for kind, lab in KINDS:
            for A in AREAS:
                R = C.radius_for_area(kind, A)
                nref = int(np.floor(C.ref_density(kind, RADIUS) * C.area(kind, R) / C.area(kind, RADIUS)))
                K = 0
                for n in range(nref, 0, -1):
                    out = pool.map(job, [(kind, A, n, s) for s in SEEDS])
                    rows += out
                    share = float(np.mean([o["reached"] for o in out]))
                    if share >= 0.5:
                        K = n
                        break
                summ.append(dict(space=kind, area=A, radius=RADIUS, n_ref=nref, K=K, K_over_n_ref=K / nref, share_at_K=share))
                print(summ[-1], flush=True)
    pd.DataFrame(rows).to_csv(CONF + "/count_runs.csv", index=False)
    pd.DataFrame(summ).to_csv(CONF + "/count_summary.csv", index=False)


if __name__ == "__main__":
    main()
