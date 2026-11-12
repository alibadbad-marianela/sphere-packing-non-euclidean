"""conf_figures.py -- figures of the confirmatory round, drawn only from out/data/conf_*.csv."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import make_figures as MF          # same fonts, legend style, save()

ROOT = MF.ROOT
DATA = MF.DATA
SP_COL = {"R2": "#D55E00", "H2": "#7B3294", "S2cap": "#0072B2"}
SP_MARK = {"R2": "o", "H2": "s", "S2cap": "^"}
SP_NAME = {"R2": "Euclidean", "H2": "Hyperbolic", "S2cap": "Spherical cap"}
M_COL = {"gd": "#1F4E9E", "sa": "#C62828", "ls": "#2E7D32", "gdp": "#6A1B9A", "lbfgsb": "#EF6C00", "bh": "#6D4C41"}
M_MARK = {"gd": "o", "sa": "s", "ls": "^", "gdp": "D", "lbfgsb": "v", "bh": "P"}
M_NAME = {"gd": "GD", "gdp": "GD+P", "sa": "SA", "ls": "CP", "lbfgsb": "L-BFGS-B", "bh": "Basin hopping"}


def fig_deficit(t, dec):
    fig, ax = plt.subplots(figsize=(6.0, 4.6))
    for sp in ("R2", "H2", "S2cap"):
        g = t[t.space == sp]
        for grp, fill in (("equal_area", True), ("large", False)):
            h = g[g.group == grp]
            if len(h):
                ax.scatter(h.boundary_share, h.deficit, s=48, marker=SP_MARK[sp], edgecolor=SP_COL[sp], linewidth=1.4,
                           facecolor=SP_COL[sp] if fill else "white", zorder=3)
    xs = np.linspace(t.boundary_share.min(), t.boundary_share.max(), 50)
    c2 = dec["C2"]
    for sp in ("R2", "H2", "S2cap"):
        if (t.space == sp).any():
            a = c2["intercept"] + (c2["gamma_hyperbolic"] if sp == "H2" else 0) + (c2["gamma_cap"] if sp == "S2cap" else 0)
            ax.plot(xs, a + c2["beta_boundary"] * xs, color=SP_COL[sp], lw=1.2, ls="--", zorder=2)
    ax.set_xlabel("Boundary share  b  (share of ball area within one disk radius of the wall)")
    ax.set_ylabel("Density deficit  δ")
    ax.grid(True)
    h = [Line2D([0], [0], marker=SP_MARK[s], color="w", markeredgecolor=SP_COL[s], markerfacecolor=SP_COL[s], ms=8, label=SP_NAME[s]) for s in ("R2", "H2", "S2cap")]
    h += [Line2D([0], [0], marker="o", color="w", markeredgecolor="black", markerfacecolor="black", ms=8, label="Equal-area balls"),
          Line2D([0], [0], marker="o", color="w", markeredgecolor="black", markerfacecolor="white", ms=8, label="Large balls"),
          Line2D([0], [0], color="black", ls="--", lw=1.2, label="Fitted line (Equation in text)")]
    fig.subplots_adjust(left=0.13, right=0.97, top=0.97, bottom=0.34)
    MF.legend_box(fig, h, loc="lower center", ncol=2, bbox_to_anchor=(0.55, 0.0))
    return MF.save(fig, "conf_deficit_boundary")


def fig_budget(m, conds):
    groups = [("Tammes problem", lambda c: c["group"] == "tammes"), ("Equal-area balls", lambda c: c["group"] == "equal_area"), ("Large balls", lambda c: c["group"] == "large")]
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 3.6), sharey=True)
    for ax, (title, fn) in zip(axs, groups):
        ids = [cid for cid, c in conds.items() if fn(c)]
        g = m[m.condition_id.isin(ids)].groupby(["algorithm", "budget"]).mean_rel.mean().reset_index()
        for a in M_COL:
            h = g[g.algorithm == a].sort_values("budget")
            ax.plot(range(3), h.mean_rel.values, color=M_COL[a], marker=M_MARK[a], ms=5, lw=1.4)
        ax.set_xticks(range(3))
        ax.set_xticklabels(["500", "1,500", "3,000"])
        ax.set_title(title)
        ax.grid(True)
    axs[0].set_ylabel("Mean relative score")
    fig.text(0.5, 0.30, "Budget (sweeps)", ha="center")
    fig.subplots_adjust(left=0.10, right=0.99, top=0.91, bottom=0.40, wspace=0.08)
    h = [Line2D([0], [0], color=M_COL[a], marker=M_MARK[a], lw=1.4, ms=5, label=M_NAME[a]) for a in M_COL]
    MF.legend_box(fig, h, loc="lower center", ncol=3, bbox_to_anchor=(0.55, 0.0))
    return MF.save(fig, "conf_budget")


def fig_rank(mr, conds):
    """Heat map of the mean rank (1 = best) of the six methods in each of the 33 conditions at 1,500 sweeps, with the mean over conditions at the bottom."""
    order = [a for a in mr.mean().sort_values().index.str.replace("mean_rank_", "")]
    cols = ["mean_rank_" + a for a in order]
    gname = {"tammes": "Tammes", "equal_area": "Equal area", "large": "Large ball"}
    rows = sorted(mr.index, key=lambda c: (["tammes", "equal_area", "large"].index(conds[c]["group"]), c))
    lab = [f"{gname[conds[c]['group']]}: " + conds[c]["label"].replace("Tammes ", "").replace("R_H", "R_H") for c in rows]
    Z = np.vstack([mr.loc[rows, cols].values, mr[cols].mean().values[None, :]])
    fig, ax = plt.subplots(figsize=(6.4, 7.4))
    im = ax.imshow(Z, cmap="Blues_r", vmin=1, vmax=6, aspect="auto")
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            ax.text(j, i, f"{Z[i, j]:.1f}", ha="center", va="center", fontsize=6.5, color="white" if Z[i, j] < 3.4 else "black", fontweight="bold" if i == Z.shape[0] - 1 else "normal")
    ax.set_xticks(range(len(order)))
    ax.set_xticklabels([M_NAME[a] for a in order], fontsize=7.5)
    ax.xaxis.tick_top()
    ax.set_yticks(range(Z.shape[0]))
    ax.set_yticklabels(lab + ["Mean over the 33 conditions"], fontsize=6.3)
    ax.axhline(Z.shape[0] - 1.5, color="black", lw=1.2)
    for k in (sum(conds[c]["group"] == "tammes" for c in rows) - 0.5, sum(conds[c]["group"] != "large" for c in rows) - 0.5):
        ax.axhline(k, color="white", lw=2.0)
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label("Mean rank within seeds (1 = best)", fontsize=7.5)
    cb.ax.tick_params(labelsize=7)
    fig.subplots_adjust(left=0.40, right=0.93, top=0.94, bottom=0.02)
    return MF.save(fig, "conf_rank")


def fig_r3(best, dec):
    """Density deficit against boundary share for the 144 equal-area conditions of the final round, with the three fitted lines."""
    fig, ax = plt.subplots(figsize=(6.0, 4.6))
    for sp in ("R2", "H2", "S2cap"):
        g = best[best.space == sp]
        ax.scatter(g.b, g.deficit, s=22, marker=SP_MARK[sp], edgecolor=SP_COL[sp], facecolor="none", linewidth=1.0, zorder=3, alpha=0.9)
    a1 = dec["A1"]
    xs = np.linspace(best.b.min(), best.b.max(), 50)
    for sp in ("R2", "H2", "S2cap"):
        a = a1["intercept"] + (a1["g_H"] if sp == "H2" else 0) + (a1["g_S"] if sp == "S2cap" else 0)
        ax.plot(xs, a + a1["beta_b"] * xs, color=SP_COL[sp], lw=1.6, zorder=2)
    ax.set_xlabel("Boundary share  b")
    ax.set_ylabel("Density deficit  δ")
    ax.grid(True)
    h = [Line2D([0], [0], marker=SP_MARK[s], color=SP_COL[s], markeredgecolor=SP_COL[s], markerfacecolor="none", ms=7, lw=1.6, label=SP_NAME[s]) for s in ("R2", "H2", "S2cap")]
    MF.legend_box(fig, h, loc="lower center", ncol=3, bbox_to_anchor=(0.55, 0.0))
    fig.subplots_adjust(left=0.12, right=0.98, top=0.97, bottom=0.25)
    return MF.save(fig, "conf_r3")
