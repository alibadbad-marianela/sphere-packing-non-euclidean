"""experiments.py -- runs every experiment and writes the raw CSV files.

Equal budget (pair-distance evaluations), shared seeds, fixed random streams.
"""
import os
import sys
import time
import pickle
import numpy as np
import pandas as pd
from algorithms import Problem, run_algorithm, ALGS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # folder that contains code/ and out/
OUT = os.path.join(ROOT, "out")
DATA = OUT + "/data"
CACHE = OUT + "/cache"
SEEDS = list(range(1, 31))
BUDGET_SWEEPS = 1500          # budget = 1500 x (n choose 2) pair-distance evaluations
S2_N = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 24, 30, 40, 60]
BALL_RN = [(2.0, 7), (2.0, 12), (2.0, 19), (3.0, 12), (3.0, 19), (3.0, 30)]

# Optimal minimum angular distances (degrees) for the Tammes problem, N = 4 to 14 and 24.
# Optimality was proved by: L. Fejes Toth (1943) for N = 3, 4, 6, 12; K. Schutte and B. L. van der Waerden (1951) for N = 5, 7, 8, 9;
# R. M. Robinson (1961) for N = 24; L. Danzer (1963) for N = 10, 11; O. R. Musin and A. S. Tarasov (2012) for N = 13 and
# (2015) for N = 14.  N = 4, 6, 12 are also derived in closed form and checked by the unit tests.  The numerical values
# should be checked against the original papers or Sloane's tables of spherical codes before publication.
BENCH_DEG = {4: float(np.degrees(np.arccos(-1.0 / 3.0))), 5: 90.0, 6: 90.0, 7: 77.8695, 8: 74.8585,
             9: 70.5288, 10: 66.1468, 11: 63.4349, 12: float(np.degrees(np.arctan(2.0))),
             13: 57.1367, 14: 55.6706, 24: 43.6908}
BENCH_SRC = {4: "Fejes Toth (1943); closed form", 5: "Schutte & van der Waerden (1951)", 6: "Fejes Toth (1943); closed form",
             7: "Schutte & van der Waerden (1951)", 8: "Schutte & van der Waerden (1951)", 9: "Schutte & van der Waerden (1951)",
             10: "Danzer (1963)", 11: "Danzer (1963)", 12: "Fejes Toth (1943); closed form", 13: "Musin & Tarasov (2012)",
             14: "Musin & Tarasov (2015)", 24: "Robinson (1961)"}

# Best-known (not proven) minimum angles from the published tables of spherical codes, used in place of the best value found
# by the runs.  N = 30: cos(theta) = 0.78155187509498732710358610409650 (Clare & Kepert, 1986, as tabulated by H. Cohn;
# 38.597 degrees, the value in Sloane's table).  N = 40 and 60: values supplied by the author from Sloane's tables.
BEST_KNOWN_DEG = {30: 38.5971159, 40: 33.1583563, 60: 27.1928300}
BEST_KNOWN_SRC = {k: "Sloane's tables of spherical codes (as supplied by the author; N = 30 also matches Cohn's compilation)" for k in (30, 40, 60)}

COND_ID = {}
for i, N in enumerate(S2_N):
    COND_ID[("S2", N, None)] = 100 + i
for sp, base in (("H2", 200), ("R2", 300), ("S2cap", 400)):
    for i, (R, n) in enumerate(BALL_RN):
        COND_ID[(sp, n, R)] = base + i


def conditions():
    for N in S2_N:
        yield ("S2", N, None)
    for sp in ("H2", "R2", "S2cap"):
        for R, n in BALL_RN:
            yield (sp, n, R)


def run_condition(cond):
    kind, n, R = cond
    cid = COND_ID[cond]
    P = Problem("S2" if kind == "S2cap" else kind, n, R)
    budget = BUDGET_SWEEPS * P.sweep
    rows, configs, traces = [], [], []
    fr = np.logspace(-3, 0, 41)
    for seed in SEEDS:
        X0 = P.initial(np.random.default_rng([seed, cid, 0]))
        for aid, alg in ALGS.items():
            res = run_algorithm(alg, P, X0, budget, [seed, cid, aid])
            tr = np.array(res["trace"])
            final = res["score"]
            idx = np.where(tr[:, 1] >= 0.99 * final)[0]
            sweeps99 = float(tr[idx[0], 0] / P.sweep) if len(idx) else float("nan")
            r_val = final if P.ball else float("nan")
            rows.append(dict(space=kind, condition_id=cid, n=n, R=(R if R is not None else float("nan")),
                             algorithm=alg, seed=seed, score=final,
                             density=(P.density(final) if P.ball else float("nan")),
                             pair_evals=res["pe"], sweeps_used=res["pe"] / P.sweep, iterations=res["iters"],
                             time_s=res["time"], sweeps_to_99pct=sweeps99,
                             recomputed_score=res["final_check"]))
            X = res["X"]
            for k in range(n):
                configs.append(dict(space=kind, condition_id=cid, n=n, R=(R if R is not None else float("nan")),
                                    algorithm=alg, seed=seed, index=k,
                                    x0=X[k, 0], x1=X[k, 1], x2=(X[k, 2] if X.shape[1] > 2 else float("nan"))))
            pes = tr[:, 0]
            for f in fr:
                j = np.searchsorted(pes, f * budget, side="right") - 1
                j = max(j, 0)
                traces.append(dict(space=kind, condition_id=cid, n=n, R=(R if R is not None else float("nan")),
                                   algorithm=alg, seed=seed, budget_fraction=f, best_score=tr[j, 1]))
    return rows, configs, traces


def main(rerun=False):
    os.makedirs(CACHE, exist_ok=True)
    os.makedirs(DATA, exist_ok=True)
    allrows, allcfg, alltr = [], [], []
    t_all = time.time()
    for cond in conditions():
        f = f"{CACHE}/{cond[0]}_{cond[1]}_{cond[2]}.pkl"
        if os.path.exists(f) and not rerun:
            rows, cfg, tr = pickle.load(open(f, "rb"))
        else:
            t0 = time.time()
            rows, cfg, tr = run_condition(cond)
            pickle.dump((rows, cfg, tr), open(f, "wb"))
            print(f"done {cond} in {time.time() - t0:.1f}s (total {time.time() - t_all:.0f}s)", flush=True)
        allrows += rows
        allcfg += cfg
        alltr += tr
    runs = pd.DataFrame(allrows)
    # reference values: proven optimum where one exists, published best-known value where tabulated, otherwise best found over all runs
    ref_type, ref_val = [], []
    best_found = runs.groupby("condition_id")["score"].max()
    for _, r in runs.iterrows():
        if r["space"] == "S2" and int(r["n"]) in BENCH_DEG:
            ref_type.append("verified optimum")
            ref_val.append(float(np.radians(BENCH_DEG[int(r["n"])])))
        elif r["space"] == "S2" and int(r["n"]) in BEST_KNOWN_DEG:
            ref_type.append("published best known")
            ref_val.append(float(np.radians(BEST_KNOWN_DEG[int(r["n"])])))
        else:
            ref_type.append("best found")
            ref_val.append(float(best_found[r["condition_id"]]))
    runs["reference_type"] = ref_type
    runs["reference_value"] = ref_val
    runs["relative_score"] = runs["score"] / runs["reference_value"]
    runs["gap_to_reference"] = runs["reference_value"] - runs["score"]
    runs["success_0.1pct"] = (runs["relative_score"] >= 0.999).astype(int)
    runs["success_1pct"] = (runs["relative_score"] >= 0.99).astype(int)
    runs.to_csv(f"{DATA}/runs_raw.csv", index=False)
    pd.DataFrame(allcfg).to_csv(f"{DATA}/configurations.csv", index=False, float_format="%.15g")
    pd.DataFrame(alltr).to_csv(f"{DATA}/convergence_traces.csv", index=False, float_format="%.12g")
    pd.DataFrame([{"n": k, "theta_deg": v, "theta_rad": float(np.radians(v)), "status": "proven optimum", "source": BENCH_SRC[k]}
                  for k, v in BENCH_DEG.items()] +
                 [{"n": k, "theta_deg": v, "theta_rad": float(np.radians(v)), "status": "published best known (not proven)", "source": BEST_KNOWN_SRC[k]}
                  for k, v in BEST_KNOWN_DEG.items()]).to_csv(f"{DATA}/benchmark_values.csv", index=False, float_format="%.10g")
    pd.DataFrame({"seed": SEEDS}).to_csv(f"{DATA}/seed_list.csv", index=False)
    print("experiments finished in %.0f s" % (time.time() - t_all))


if __name__ == "__main__":
    main(rerun="--rerun" in sys.argv)
