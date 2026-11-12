"""make_figures.py -- all figures, drawn only from the CSV files, with accuracy assertions.

Colors: gradient descent = blue, simulated annealing = red, compression = green.
Fonts: Times New Roman (Liberation Serif if Times New Roman is not installed).
"""
import os
import subprocess
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Patch
from matplotlib.lines import Line2D
from geometry import Space, euclid_image_disk

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # folder that contains code/ and out/
OUT = os.path.join(ROOT, "out")
DATA = OUT + "/data"
FIG = OUT + "/figures"
COL = {"gd": "#1F4E9E", "sa": "#C62828", "ls": "#2E7D32"}
MARK = {"gd": "o", "sa": "s", "ls": "^"}
LSTY = {"gd": "-", "sa": "--", "ls": "-."}
NAME = {"gd": "Gradient descent", "sa": "Simulated annealing", "ls": "Compression"}
ALG = ["gd", "sa", "ls"]
TOL = 1e-9
ASSERTIONS = []

fams = {f.name for f in matplotlib.font_manager.fontManager.ttflist}
SERIF = "Times New Roman" if "Times New Roman" in fams else "Liberation Serif"
plt.rcParams.update({"font.family": "serif", "font.serif": [SERIF], "mathtext.fontset": "stix",
                     "font.size": 12, "axes.labelsize": 12, "xtick.labelsize": 12, "ytick.labelsize": 12,
                     "legend.fontsize": 12, "axes.titlesize": 12, "figure.dpi": 100, "savefig.dpi": 300,
                     "axes.linewidth": 0.8, "grid.color": "#CCCCCC", "grid.linewidth": 0.5})


def legend_box(ax_or_fig, handles, **kw):
    lg = ax_or_fig.legend(handles=handles, frameon=True, fancybox=False, edgecolor="black", facecolor="white",
                          framealpha=1.0, prop={"family": SERIF, "size": 12}, **kw)
    lg.get_frame().set_linewidth(1.0)
    return lg


def alg_handles():
    return [Line2D([0], [0], color=COL[a], marker=MARK[a], linestyle=LSTY[a], lw=1.6, ms=6, label=NAME[a]) for a in ALG]


def save(fig, name):
    os.makedirs(FIG, exist_ok=True)
    path = f"{FIG}/{name}.png"
    fig.savefig(path, dpi=300, bbox_inches=None)
    plt.close(fig)
    return path


def check(name, ok, detail=""):
    ASSERTIONS.append((name, bool(ok), detail))
    if not ok:
        raise AssertionError(name + " " + detail)


def load():
    runs = pd.read_csv(f"{DATA}/runs_raw.csv")
    cfg = pd.read_csv(f"{DATA}/configurations.csv")
    tr = pd.read_csv(f"{DATA}/convergence_traces.csv")
    summ = pd.read_csv(f"{DATA}/summary_by_condition.csv")
    return runs, cfg, tr, summ


def get_config(cfg, runs, cid, alg, seed):
    g = cfg[(cfg.condition_id == cid) & (cfg.algorithm == alg) & (cfg.seed == seed)].sort_values("index")
    return g[["x0", "x1", "x2"]].values


def best_run(runs, cid, alg=None):
    g = runs[runs.condition_id == cid]
    if alg:
        g = g[g.algorithm == alg]
    return g.sort_values("score", ascending=False).iloc[0]


# ------------------------------------------------------------------ Figure 1
def fig_framework():
    from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon
    W, H = 6.5, 7.6
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
    xa, xb, bw = 1.95, 5.05, 2.7
    ys = [H - 0.62 - 1.07 * k for k in range(7)]
    def box(xc, yc, text, kind="proc", h=0.7):
        if kind == "io":
            ax.add_patch(FancyBboxPatch((xc - bw / 2, yc - h / 2), bw, h, boxstyle="round,pad=0,rounding_size=0.14", fc="white", ec="black", lw=1.0))
        else:
            ax.add_patch(Rectangle((xc - bw / 2, yc - h / 2), bw, h, fc="white", ec="black", lw=1.0))
        ax.text(xc, yc, text, ha="center", va="center", fontsize=12, color="black", family=SERIF, linespacing=1.15)
        return h
    def arrow(p, q):
        ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color="black", lw=1.0, shrinkA=0, shrinkB=0, mutation_scale=11))
    def line(p, q):
        ax.plot([p[0], q[0]], [p[1], q[1]], color="black", lw=1.0, solid_capstyle="butt")
    hs = [0.7, 0.95, 0.7, 0.95, 0.5, 0.5]
    texts = ["Research Problem\n(dense packing under curvature)", "Geometric Spaces\nSphere S\u00b2, Hyperbolic Plane H\u00b2,\nEuclidean Control R\u00b2",
             "Distance Function and\nEnergy or Density Definition", "Three Optimization Algorithms\n(gradient descent, simulated\nannealing, compression)",
             "Implementation", "Unit Tests and Known Optima"]
    kinds = ["io", "proc", "proc", "proc", "proc", "proc"]
    for k in range(6):
        box(xa, ys[k], texts[k], kinds[k], hs[k])
    for k in range(5):
        arrow((xa, ys[k] - hs[k] / 2), (xa, ys[k + 1] + hs[k + 1] / 2))
    # decision diamond
    dy, dw, dh = ys[6], 1.5, 0.8
    ax.add_patch(Polygon([(xa, dy + dh / 2), (xa + dw / 2, dy), (xa, dy - dh / 2), (xa - dw / 2, dy)], closed=True, fc="white", ec="black", lw=1.0))
    ax.text(xa, dy, "Pass?", ha="center", va="center", fontsize=12, family=SERIF)
    arrow((xa, ys[5] - hs[5] / 2), (xa, dy + dh / 2))
    # "No": left, up, into Implementation
    xl = xa - bw / 2 - 0.55
    line((xa - dw / 2, dy), (xl, dy)); line((xl, dy), (xl, ys[4])); arrow((xl, ys[4]), (xa - bw / 2, ys[4]))
    ax.text(xl + 0.08, dy + 0.12, "No", fontsize=12, family=SERIF, ha="left", va="bottom")
    # "Yes": right into Trials, then upward
    bh = [0.7, 0.85, 0.85, 0.7]
    rtexts = ["Repeated Trials With\nFixed Seeds", "Performance Measures\n(distance or density, convergence,\nruntime, success rate)",
              "Statistical Analysis\n(confidence intervals, paired\nnonparametric tests)", "Findings and\nHypothesis Evaluation"]
    rk = ["proc", "io", "proc", "io"]
    ry = [ys[6], ys[5], ys[4], ys[3]]
    for t, k, y, h in zip(rtexts, rk, ry, bh):
        box(xb, y, t, k, h)
    arrow((xa + dw / 2, dy), (xb - bw / 2, dy))
    ax.text((xa + dw / 2 + xb - bw / 2) / 2, dy + 0.12, "Yes", fontsize=12, family=SERIF, ha="center", va="bottom")
    for i in range(3):
        arrow((xb, ry[i] + bh[i] / 2), (xb, ry[i + 1] - bh[i + 1] / 2))
    os.makedirs(FIG, exist_ok=True)
    fig.savefig(f"{FIG}/framework.png", dpi=300)
    plt.close(fig)
    from PIL import Image
    im = Image.open(f"{FIG}/framework.png").convert("RGB")
    arr = np.array(im)
    check("Framework diagram contains only gray levels (no color)", np.all(arr[..., 0] == arr[..., 1]) and np.all(arr[..., 1] == arr[..., 2]))
    return f"{FIG}/framework.png", im.size


# ------------------------------------------------------------------ Figure 2
def ortho_view(az, el):
    ca, sa_ = np.cos(az), np.sin(az)
    ce, se = np.cos(el), np.sin(el)
    Rz = np.array([[ca, -sa_, 0], [sa_, ca, 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, ce, -se], [0, se, ce]])
    return Rx @ Rz


def cap_circle(p, ang, m=200):
    p = p / np.linalg.norm(p)
    a = np.cross(p, [0.3, 0.5, 0.8])
    a /= np.linalg.norm(a)
    b = np.cross(p, a)
    t = np.linspace(0, 2 * np.pi, m)
    return np.cos(ang) * p[None, :] + np.sin(ang) * (np.cos(t)[:, None] * a[None, :] + np.sin(t)[:, None] * b[None, :])


def draw_sphere_panel(ax, X, dmin, color, title):
    check("Sphere points have unit norm (1e-9)", np.max(np.abs(np.linalg.norm(X, axis=1) - 1)) < TOL)
    S = Space("S2")
    D = S.pair_dist(X)
    check("Plotted configuration reproduces min distance", abs(D.min() - dmin) < TOL, f"{D.min()} vs {dmin}")
    V = ortho_view(np.radians(25), np.radians(-70))
    Y = X @ V.T
    th = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(th), np.sin(th), color="black", lw=0.8)
    half = dmin / 2.0
    for p in X:
        c = cap_circle(p, half) @ V.T
        vis = c[:, 2] > 0
        seg = np.where(vis)[0]
        if len(seg):
            cc = np.where(vis[:, None], c[:, :2], np.nan)
            ax.plot(cc[:, 0], cc[:, 1], color=color, lw=0.5, alpha=0.7)
    iu = np.triu_indices(len(X), 1)
    for i, j in zip(*iu):
        if D[i, j] < dmin + 1e-4:
            ts = np.linspace(0, 1, 40)
            om = D[i, j]
            arc = (np.sin((1 - ts) * om)[:, None] * X[i] + np.sin(ts * om)[:, None] * X[j]) / np.sin(om)
            arc = arc @ V.T
            if np.all(arc[:, 2] > -0.02):
                ax.plot(arc[:, 0], arc[:, 1], color="black", lw=0.8)
    front = Y[:, 2] > 0
    ax.scatter(Y[front, 0], Y[front, 1], s=14, color=color, zorder=5)
    ax.scatter(Y[~front, 0], Y[~front, 1], s=14, facecolors="white", edgecolors=color, linewidths=0.7, zorder=4)
    ax.set_aspect("equal")
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.axis("off")
    ax.set_title(title, fontsize=12)


def fig_sphere(runs, cfg):
    sel = [12, 13, 14, 24, 30, 60]
    fig, axs = plt.subplots(2, 3, figsize=(6.5, 4.6))
    for ax, N in zip(axs.ravel(), sel):
        cid = 100 + [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 24, 30, 40, 60].index(N)
        b = best_run(runs, cid)
        X = get_config(cfg, runs, cid, b.algorithm, int(b.seed))
        draw_sphere_panel(ax, X, float(b.score), COL[b.algorithm], f"$N$ = {N}")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.93, bottom=0.01, wspace=0.05, hspace=0.12)
    return save(fig, "fig_sphere_configs")


# ------------------------------------------------------------------ Figure 3
CAP_IDS = {}
BALL_SET = [(2.0, 7), (2.0, 12), (2.0, 19), (3.0, 12), (3.0, 19), (3.0, 30)]


def draw_hyperbolic_panel(ax, X, r, R, color, title):
    S = Space("H2")
    check("Hyperboloid points satisfy the model equation", S.on_manifold_error(X) < 1e-9)
    D = S.pair_dist(X)
    rho = S.rho(X)
    r_re = min(D.min() / 2.0, float((R - rho).min()))
    check("H2: recomputed disk radius matches CSV value (1e-9)", abs(r_re - r) < TOL, f"{r_re} vs {r}")
    check("H2: disks do not overlap (tolerance 1e-9)", D.min() / 2.0 - r > -TOL)
    check("H2: disks lie inside the container (tolerance 1e-9)", float((R - rho).min()) - r > -TOL)
    Z = S.to_plane(X)
    ax.add_patch(Circle((0, 0), np.tanh(R / 2.0), fill=False, ec="black", lw=1.0))
    ax.add_patch(Circle((0, 0), 1.0, fill=False, ec="#888888", lw=0.6, ls=":"))
    for k in range(len(X)):
        zn = np.hypot(*Z[k])
        cen, rad = euclid_image_disk(rho[k], r)
        u = Z[k] / zn if zn > 1e-12 else np.array([1.0, 0.0])
        c_xy = cen * u
        ang = np.linspace(0, 2 * np.pi, 13)
        pts = c_xy[None, :] + rad * np.c_[np.cos(ang), np.sin(ang)]
        P3 = S.from_disk(pts)
        dd = np.array([S.dist(X[k], q) for q in P3])
        check("H2: drawn Euclidean image circle lies at hyperbolic distance r from the center", np.max(np.abs(dd - r)) < 1e-7)
        ax.add_patch(Circle(c_xy, rad, fc=color, alpha=0.25, ec=color, lw=0.8))
        ax.plot([Z[k, 0]], [Z[k, 1]], "o", color=color, ms=2)
    lim = np.tanh(R / 2.0) * 1.04
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=12)


def draw_euclid_panel(ax, X, r, R, color, title):
    S = Space("R2")
    D = S.pair_dist(X)
    rho = S.rho(X)
    r_re = min(D.min() / 2.0, float((R - rho).min()))
    check("R2: recomputed disk radius matches CSV value (1e-9)", abs(r_re - r) < TOL, f"{r_re} vs {r}")
    check("R2: disks do not overlap and lie inside the container (1e-9)", D.min() / 2.0 - r > -TOL and float((R - rho).min()) - r > -TOL)
    ax.add_patch(Circle((0, 0), R, fill=False, ec="black", lw=1.0))
    for k in range(len(X)):
        ax.add_patch(Circle(X[k], r, fc=color, alpha=0.25, ec=color, lw=0.8))
        ax.plot([X[k, 0]], [X[k, 1]], "o", color=color, ms=2)
    lim = R * 1.04
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=12)


def draw_cap_panel(ax, X, r, R, color, title):
    """Spherical cap in azimuthal equidistant projection: plane radius = geodesic distance from the center."""
    S = Space("S2")
    check("Cap points have unit norm (1e-9)", np.max(np.abs(np.linalg.norm(X, axis=1) - 1)) < TOL)
    D = S.pair_dist(X)
    rho = S.rho(X)
    r_re = min(D.min() / 2.0, float((R - rho).min()))
    check("S2 cap: recomputed disk radius matches CSV value (1e-9)", abs(r_re - r) < TOL, f"{r_re} vs {r}")
    check("S2 cap: disks do not overlap and lie inside the cap (1e-9)", D.min() / 2.0 - r > -TOL and float((R - rho).min()) - r > -TOL)
    ax.add_patch(Circle((0, 0), R, fill=False, ec="black", lw=1.0))
    for k in range(len(X)):
        c = cap_circle(X[k], r, 240)
        dd = np.array([S.dist(X[k], q) for q in c[::20]])
        check("S2 cap: every drawn boundary point is at geodesic distance r from its center", np.max(np.abs(dd - r)) < 1e-7)
        rr = np.arccos(np.clip(c[:, 2], -1, 1))
        th = np.arctan2(c[:, 1], c[:, 0])
        ax.fill(rr * np.cos(th), rr * np.sin(th), fc=color, alpha=0.25, ec=color, lw=0.8)
        pr, pt = rho[k], np.arctan2(X[k, 1], X[k, 0])
        ax.plot([pr * np.cos(pt)], [pr * np.sin(pt)], "o", color=color, ms=2)
    lim = R * 1.04
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title(title, fontsize=12)


def fig_curvature(runs, cfg):
    R, n = 3.0, 19
    k = BALL_SET.index((R, n))
    fig, axs = plt.subplots(1, 3, figsize=(6.5, 2.5))
    spec = [("S2cap", 400 + k, draw_cap_panel, "Spherical cap, $K$ = +1"), ("R2", 300 + k, draw_euclid_panel, "Euclidean disk, $K$ = 0"),
            ("H2", 200 + k, draw_hyperbolic_panel, "Hyperbolic disk, $K$ = \u22121")]
    info = []
    for ax, (sp, cid, fn, ttl) in zip(axs, spec):
        b = best_run(runs, cid)
        X = get_config(cfg, runs, cid, b.algorithm, int(b.seed))
        if sp == "R2":
            X = X[:, :2]
        fn(ax, X, float(b.score), R, COL[b.algorithm], f"{ttl}\n$r$ = {b.score:.4f}")
        info.append((sp, b.algorithm, float(b.score)))
    fig.subplots_adjust(left=0.01, right=0.99, top=0.80, bottom=0.01, wspace=0.05)
    return save(fig, "fig_curvature_packing"), info


# ------------------------------------------------------------------ Figure 4
def ci_band(g, col):
    m = g.groupby("budget_fraction")[col].mean()
    s = g.groupby("budget_fraction")[col].std(ddof=1)
    n = g.groupby("budget_fraction")[col].count()
    h = 2.045 * s / np.sqrt(n)
    return m.index.values, m.values, (m - h).values, (m + h).values


def fig_convergence(runs, tr):
    conds = [(100 + 9, "$S^2$ Tammes, $N$ = 13"), (100 + 14, "$S^2$ Tammes, $N$ = 60"), (400 + 4, "Spherical cap, $R$ = 3, $n$ = 19"),
             (300 + 4, "Euclidean disk, $R$ = 3, $n$ = 19"), (200 + 4, "Hyperbolic disk, $R$ = 3, $n$ = 19"), (100 + 12, "$S^2$ Tammes, $N$ = 30")]
    ref = runs.groupby("condition_id")["reference_value"].first()
    fig, axs = plt.subplots(3, 2, figsize=(6.5, 7.4), sharex=True)
    for ax, (cid, title) in zip(axs.ravel(), conds):
        lo_all = []
        for a in ALG:
            g = tr[(tr.condition_id == cid) & (tr.algorithm == a)].copy()
            g["rel"] = g["best_score"] / ref[cid]
            x, m, lo, hi = ci_band(g, "rel")
            ax.plot(x, m, color=COL[a], ls=LSTY[a], marker=MARK[a], ms=3.5, lw=1.4, markevery=5)
            ax.fill_between(x, lo, hi, color=COL[a], alpha=0.18, lw=0)
            lo_all.append(np.nanmin(lo))
        ax.axhline(1.0, color="#333333", ls=":", lw=1.0)
        ax.set_xscale("log")
        ax.set_ylim(max(0.0, min(lo_all) - 0.03), 1.04)
        ax.set_title(title, fontsize=11)
        ax.grid(True)
    for ax in axs[2]:
        ax.set_xlabel("Fraction of budget used")
    for ax in axs[:, 0]:
        ax.set_ylabel("Best score / reference")
    fig.subplots_adjust(left=0.11, right=0.98, top=0.96, bottom=0.17, hspace=0.35, wspace=0.28)
    h = alg_handles() + [Line2D([0], [0], color="#333333", ls=":", lw=1.0, label="Reference value")]
    legend_box(fig, h, loc="lower center", ncol=2, bbox_to_anchor=(0.54, 0.0))
    return save(fig, "fig_convergence")


# ------------------------------------------------------------------ Figure 5
def fig_performance(summ):
    fig, axs = plt.subplots(4, 1, figsize=(6.5, 8.6))
    s2 = summ[summ.space == "S2"]
    for a in ALG:
        g = s2[s2.algorithm == a].sort_values("n")
        axs[0].errorbar(np.arange(len(g)), g.mean_relative, yerr=[g.mean_relative - g.rel_ci95_lo, g.rel_ci95_hi - g.mean_relative],
                        color=COL[a], marker=MARK[a], ls=LSTY[a], ms=5, lw=1.3, capsize=2.5, elinewidth=0.9)
    labs = [str(int(v)) for v in sorted(s2.n.unique())]
    axs[0].set_xticks(np.arange(len(labs)))
    axs[0].set_xticklabels(labs)
    axs[0].set_xlabel("Number of points $N$ (Tammes problem on $S^2$)")
    axs[0].set_ylabel("Distance / reference")
    axs[0].axhline(1.0, color="#333333", ls=":", lw=1.0)
    for ax, sp, t in ((axs[1], "S2cap", "spherical cap, $K$ = +1"), (axs[2], "R2", "Euclidean disk, $K$ = 0"), (axs[3], "H2", "hyperbolic disk, $K$ = \u22121")):
        g0 = summ[summ.space == sp]
        conds = g0.drop_duplicates("condition_id").sort_values("condition_id")
        for a in ALG:
            g = g0[g0.algorithm == a].sort_values("condition_id")
            ax.errorbar(np.arange(len(g)), g.mean_relative, yerr=[g.mean_relative - g.rel_ci95_lo, g.rel_ci95_hi - g.mean_relative],
                        color=COL[a], marker=MARK[a], ls=LSTY[a], ms=5, lw=1.3, capsize=2.5, elinewidth=0.9)
        ax.set_xticks(np.arange(len(conds)))
        ax.set_xticklabels([f"{r:g}, {int(n)}" for r, n in zip(conds.R, conds.n)])
        ax.set_xlabel(f"Ball radius $R$, number of disks $n$ ({t})")
        ax.set_ylabel("Radius / best found")
        ax.axhline(1.0, color="#333333", ls=":", lw=1.0)
    for ax in axs:
        ax.grid(True)
        lo, hi = ax.get_ylim()
        ax.set_ylim(lo, max(hi, 1.01))
    fig.subplots_adjust(left=0.12, right=0.98, top=0.985, bottom=0.17, hspace=0.62)
    h = alg_handles() + [Line2D([0], [0], color="#333333", ls=":", lw=1.0, label="Reference value")]
    legend_box(fig, h, loc="lower center", ncol=2, bbox_to_anchor=(0.54, 0.0))
    return save(fig, "fig_performance_vs_size")


# ------------------------------------------------------------------ Figure 6
def fig_runtime(summ):
    fig, ax = plt.subplots(figsize=(6.0, 3.9))
    s2 = summ[summ.space == "S2"]
    for a in ALG:
        g = s2[s2.algorithm == a].sort_values("n")
        h = 2.045 * g.sd_time_s / np.sqrt(g.n_seeds)
        ax.errorbar(g.n, g.mean_time_s, yerr=h, color=COL[a], marker=MARK[a], ls=LSTY[a], ms=5, lw=1.3, capsize=2.5, elinewidth=0.9)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Number of points $N$ (log scale)")
    ax.set_ylabel("Mean run time (s, log scale)")
    ax.grid(True, which="both")
    fig.subplots_adjust(left=0.13, right=0.97, top=0.97, bottom=0.34)
    legend_box(fig, alg_handles(), loc="lower center", ncol=2, bbox_to_anchor=(0.55, 0.0))
    return save(fig, "fig_runtime_scaling")


# ------------------------------------------------------------------ Figure 7
def fig_distribution(runs):
    conds = [(100 + 9, "$S^2$\n$N$ = 13"), (100 + 12, "$S^2$\n$N$ = 30"), (100 + 14, "$S^2$\n$N$ = 60"),
             (400 + 4, "Cap\n(3, 19)"), (300 + 4, "$R^2$\n(3, 19)"), (200 + 4, "$H^2$\n(3, 19)")]
    fig, ax = plt.subplots(figsize=(6.5, 3.7))
    w = 0.22
    for k, a in enumerate(ALG):
        data = [runs[(runs.condition_id == cid) & (runs.algorithm == a)]["relative_score"].values for cid, _ in conds]
        pos = np.arange(len(conds)) + (k - 1) * (w + 0.03)
        bp = ax.boxplot(data, positions=pos, widths=w, patch_artist=True, showfliers=True,
                        medianprops=dict(color="black", lw=1.2), whiskerprops=dict(color=COL[a]), capprops=dict(color=COL[a]),
                        flierprops=dict(marker=MARK[a], mfc="none", mec=COL[a], ms=3))
        for b_ in bp["boxes"]:
            b_.set_facecolor(COL[a]); b_.set_alpha(0.35); b_.set_edgecolor(COL[a])
    ax.set_xticks(np.arange(len(conds)))
    ax.set_xticklabels([t for _, t in conds])
    ax.set_ylabel("Score / reference")
    ax.axhline(1.0, color="#333333", ls=":", lw=1.0)
    ax.grid(True, axis="y")
    handles = [Patch(facecolor=COL[a], alpha=0.5, edgecolor=COL[a], label=NAME[a]) for a in ALG]
    fig.subplots_adjust(left=0.11, right=0.98, top=0.97, bottom=0.30)
    legend_box(fig, handles, loc="lower center", ncol=3, bbox_to_anchor=(0.54, 0.0))
    return save(fig, "fig_distribution")


def main():
    runs, cfg, tr, summ = load()
    check("All plotted scores are recomputed from coordinates in the CSV files (runs match)",
          np.max(np.abs(runs.score - runs.recomputed_score)) < 1e-9)
    out = {}
    out["framework"] = fig_framework()
    out["sphere"] = fig_sphere(runs, cfg)
    out["curv"] = fig_curvature(runs, cfg)
    out["conv"] = fig_convergence(runs, tr)
    out["perf"] = fig_performance(summ)
    out["runtime"] = fig_runtime(summ)
    out["dist"] = fig_distribution(runs)
    pd.DataFrame(ASSERTIONS, columns=["assertion", "passed", "detail"]).to_csv(f"{DATA}/figure_assertions.csv", index=False)
    print(f"{len(ASSERTIONS)} figure assertions passed; font {SERIF}")
    return out


if __name__ == "__main__":
    main()
