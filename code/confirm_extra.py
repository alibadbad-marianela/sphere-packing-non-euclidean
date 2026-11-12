"""confirm_extra.py -- post-hoc analyses of ADDENDUM 1 (retuned baselines, wall metrics) and the exploratory boundary-loss model on the round-1 data.
Writes out/conf/decisions_retuned.json, out/data/conf_retuned_vs_original.csv, conf_walls_by_method.csv, conf_walls_by_condition.csv, out/conf/extra.json.
"""
import glob
import io
import json
import os
import shutil
import contextlib
import numpy as np
import pandas as pd
import confirm_analyze as ca
import confirm_design as C

CONF, DATA = ca.CONF, ca.DATA
ALG = ["ls", "lbfgsb"]


def retuned():
    tmp = CONF + "_retuned"
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp + "/_data")
    shutil.copy(CONF + "/packomania_values.csv", tmp)
    key = ["condition_id", "algorithm", "budget", "seed"]
    comp = []
    for f in sorted(glob.glob(CONF + "/runs_*.csv")):
        o = pd.read_csv(f)
        n = pd.read_csv(CONF + "/retuned/" + os.path.basename(f))
        m = o.merge(n[key + ["score", "recomputed_score", "sweeps_used", "time_s"]], on=key, how="left", suffixes=("", "_new"))
        m["old"] = o.merge(m[key], on=key, how="right").score.values
        for col in ["score", "recomputed_score", "sweeps_used", "time_s"]:
            m[col] = np.where(m.algorithm.isin(ALG), m[col + "_new"], m[col])
        m.drop(columns=[c for c in m.columns if c.endswith("_new")]).to_csv(f"{tmp}/{os.path.basename(f)}", index=False)
        comp.append(m[m.algorithm.isin(ALG)].assign(new=lambda x: x.score_new))
    ca.CONF, ca.DATA = tmp, tmp + "/_data"
    with contextlib.redirect_stdout(io.StringIO()):
        ca.main()
    ca.CONF, ca.DATA = CONF, DATA
    dec = json.load(open(tmp + "/decisions.json"))
    json.dump(dec, open(CONF + "/decisions_retuned.json", "w"), indent=1)
    c = pd.concat(comp)
    ref = pd.read_csv(DATA + "/conf_runs.csv").groupby("condition_id").reference_value.first()
    c["rel_old"], c["rel_new"] = c.old / c.condition_id.map(ref), c.new / c.condition_id.map(ref)
    s = c.groupby(["condition_id", "algorithm", "budget"])[["rel_old", "rel_new"]].mean().reset_index()
    s.to_csv(DATA + "/conf_retuned_vs_original.csv", index=False)
    shutil.rmtree(tmp)
    return dec, s


def walls():
    w = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(CONF + "/walls_*.csv"))], ignore_index=True)
    conds = {c["cid"]: c for c in C.conditions()}
    w["space"] = w.condition_id.map(lambda c: conds[c]["kind"])
    w["group"] = w.condition_id.map(lambda c: conds[c]["group"])
    a = w.groupby(["budget", "algorithm"]).agg(runs=("ring", "size"), mean_touch_share=("touch_share", "mean"), ring_share=("ring", "mean"), median_max_gap_over_r=("max_gap_over_r", "median")).reset_index()
    a.to_csv(DATA + "/conf_walls_by_method.csv", index=False)
    b = w.groupby(["condition_id", "budget", "algorithm"]).agg(mean_touch_share=("touch_share", "mean"), ring_share=("ring", "mean")).reset_index()
    b.to_csv(DATA + "/conf_walls_by_condition.csv", index=False)
    return w, a, b


def boundary_model():
    t = pd.read_csv(DATA + "/conf_deficit_boundary.csv")
    e = t[t.space == "R2"]
    lam = float((e.boundary_share * e.deficit).sum() / (e.boundary_share ** 2).sum())
    o = t[t.space != "R2"]
    err = (o.deficit - lam * o.boundary_share).abs()
    return dict(lambda_euclid=lam, n_euclid=len(e), n_other=len(o), mae_other=float(err.mean()), mae_by_space={k: float(v) for k, v in err.groupby(o.space).mean().items()},
                mae_euclid_in_sample=float((e.deficit - lam * e.boundary_share).abs().mean()))


if __name__ == "__main__":
    dec, s = retuned()
    w, a, b = walls()
    bm = boundary_model()
    old = json.load(open(CONF + "/decisions.json"))
    ex = dict(boundary_model_round1=bm, retuned_vs_original={k: dec[k] for k in ("C1", "C2", "C3", "C4", "C5", "C6")},
              original={k: old[k] for k in ("C1", "C2", "C3", "C4", "C5", "C6")},
              retuned_mean_rel_change=s.assign(d=s.rel_new - s.rel_old).groupby(["algorithm", "budget"]).d.mean().round(4).reset_index().to_dict("records"),
              walls_overall=dict(runs=int(len(w)), mean_touch_share=float(w.touch_share.mean()), ring_share=float(w.ring.mean())))
    json.dump(ex, open(CONF + "/extra.json", "w"), indent=1, default=float)
    print(json.dumps(ex, indent=1, default=float)[:6000])
    print(a.round(3).to_string())
