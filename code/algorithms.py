"""algorithms.py -- Problems and the three optimizers (numpy only).

Problem A (S2): place n points to maximize the minimum pairwise geodesic distance.
Problem B (H2, R2): place n equal disks in a ball of radius R centered at the
origin and maximize the common disk radius r.  Disk centers must satisfy
rho_i <= R - r and d_ij >= 2 r, so with  l_min = min( min_ij d_ij , min_i 2(R - rho_i) )
the best common radius is r = l_min / 2.

All three optimizers receive the same budget measured in pair-distance
evaluations (PE), so comparisons do not depend on implementation speed.

  1. gd : gradient descent on a soft-minimum energy with an annealed exponent p
  2. sa : simulated annealing, adaptive step, hard-minimum objective
  3. ls : Lubachevsky-Stillinger-style compression (time-stepped, simplified)
"""
import time
import numpy as np
from geometry import Space

ALGS = {1: "gd", 2: "sa", 3: "ls"}
ALG_NAMES = {"gdp": "Gradient Descent + Polishing", "gd": "Gradient Descent", "sa": "Simulated Annealing", "ls": "Compression"}


class Problem:
    def __init__(self, kind, n, R=None):
        self.space = Space(kind)
        self.kind = kind
        self.n = n
        self.R = R
        self.ball = R is not None          # bounded problem (disks in a geodesic ball)
        self.iu = np.triu_indices(n, 1)
        self.sweep = n * (n - 1) / 2.0
        if kind == "S2" and R is None:
            area = 4.0 * np.pi
        elif kind == "S2":
            area = 2.0 * np.pi * (1.0 - np.cos(R))
        elif kind == "H2":
            area = 2.0 * np.pi * (np.cosh(R) - 1.0)
        else:
            area = np.pi * R * R
        self.scale = float(np.sqrt(area / n))

    def initial(self, rng):
        if not self.ball:
            return self.space.random_points(self.n, rng)
        return self.space.random_points(self.n, rng, R=self.R - 0.05)

    def lmin(self, X, D=None):
        """Minimum of pairwise distances and doubled wall clearances."""
        if D is None:
            D = self.space.pair_dist(X)
        m = float(D.min())
        if self.ball:
            m = min(m, float(2.0 * (self.R - self.space.rho(X)).min()))
        return m

    def score(self, X):
        """Min angular distance (S2) or common disk radius (ball problems)."""
        m = self.lmin(X)
        return m / 2.0 if self.ball else m

    def density(self, r):
        """Fraction of the ball covered by n disks of radius r."""
        if self.kind == "S2":
            return self.n * (1.0 - np.cos(r)) / (1.0 - np.cos(self.R))
        if self.kind == "H2":
            return self.n * (np.cosh(r) - 1.0) / (np.cosh(self.R) - 1.0)
        if self.kind == "R2":
            return self.n * r * r / (self.R * self.R)
        return float("nan")


def _to_score(P, l):
    return l / 2.0 if P.ball else l


# ----------------------------------------------------------------------
# 1. gradient descent with annealed exponent
# ----------------------------------------------------------------------
def _soft_energy(P, X, p, want_grad):
    S = P.space
    D = S.pair_dist(X)
    Lp = D[P.iu]
    if P.ball:
        Lw = np.maximum(2.0 * (P.R - S.rho(X)), 1e-9)
        L = np.concatenate([Lp, Lw])
    else:
        L = Lp
    L = np.maximum(L, 1e-9)
    z = -p * np.log(L)
    zm = z.max()
    w = np.exp(z - zm)
    Z = w.sum()
    E = (zm + np.log(Z)) / p
    lmin = float(L.min())
    if not want_grad:
        return E, None, lmin
    sft = w / Z
    npair = len(Lp)
    Wd = np.zeros((P.n, P.n))
    Wd[P.iu] = -sft[:npair] / L[:npair]
    Wd = Wd + Wd.T
    G = S.grad_pairs(X, D, Wd)
    if P.ball:
        wr = 2.0 * sft[npair:] / L[npair:]
        G = G + S.grad_rho(X, wr)
    return E, G, lmin


def run_gd(P, X0, budget, rng, p0=2.0, pmax=150.0):
    S = P.space
    X = X0.copy()
    pe = 0.0
    cost = P.sweep + (P.n if P.ball else 0)
    trace = [(0.0, P.score(X))]
    best, bestX = trace[0][1], X.copy()
    it = 0
    eta_mult = 0.5
    Rclip = (P.R - 1e-6) if P.ball else None
    while pe + 2 * cost <= budget:
        frac = pe / budget
        p = p0 * (pmax / p0) ** frac
        E, G, lmin = _soft_energy(P, X, p, True)
        pe += cost
        sc = _to_score(P, lmin)
        if sc > best:
            best, bestX = sc, X.copy()
        gnorm = S.tangent_norm(G)
        gmax = max(float(gnorm.max()), 1e-12)
        eta = eta_mult * lmin ** 2 / p
        eta = min(eta, 0.25 * lmin / gmax)
        accepted = False
        for _ in range(5):
            if pe + cost > budget:
                break
            Xn = S.retract(X, -eta * G)
            if P.ball:
                Xn = S.clip_to_ball(Xn, Rclip)
            En, _, _ = _soft_energy(P, Xn, p, False)
            pe += cost
            if En < E:
                accepted = True
                break
            eta *= 0.4
        if accepted:
            X = Xn
            eta_mult = min(eta_mult * 1.3, 2.0)
        else:
            eta_mult = max(eta_mult * 0.5, 1e-3)
        it += 1
        trace.append((pe, best))
    sc_final = P.score(X)
    if sc_final > best:
        best, bestX = sc_final, X.copy()
    trace.append((pe, best))
    return dict(X=bestX, score=best, trace=trace, pe=pe, iters=it)


# ----------------------------------------------------------------------
# 2. simulated annealing
# ----------------------------------------------------------------------
def run_sa(P, X0, budget, rng, T0f=0.02, T1f=1e-5, focus=0.3):
    S = P.space
    n = P.n
    X = X0.copy()
    D = S.pair_dist(X)
    rho = S.rho(X) if P.ball else None
    pe = P.sweep
    nmoves = int(max((budget - pe) // (n - 1), 1))
    scale = P.scale
    T0, T1 = T0f * scale, T1f * scale
    delta = 0.3 * scale

    def current_l():
        m = float(D.min())
        if P.ball:
            m = min(m, float(2.0 * (P.R - rho).min()))
        return m

    lcur = current_l()
    best = _to_score(P, lcur)
    bestX = X.copy()
    trace = [(0.0, best)]
    noise = rng.normal(size=(8192, S.amb))
    unif = rng.random(size=(8192, 3))
    k = 0
    acc = 0
    tried = 0
    log_ratio = np.log(T1 / T0)
    rlimit = (P.R - 1e-6) if P.ball else None
    rec_every = max(nmoves // 400, 1)
    for m in range(nmoves):
        if k >= 8192:
            noise = rng.normal(size=(8192, S.amb))
            unif = rng.random(size=(8192, 3))
            k = 0
        T = T0 * np.exp(log_ratio * m / nmoves)
        # choose the point to move
        if unif[k, 0] < focus:
            flat = int(np.argmin(D))
            i = flat // n if unif[k, 1] < 0.5 else flat % n
            if P.ball:
                iw = int(np.argmax(rho))
                if 2.0 * (P.R - rho[iw]) < D.flat[flat]:
                    i = iw
        else:
            i = int(unif[k, 1] * n) % n
        xi = X[i:i + 1]
        v = S.project_tangent(xi, noise[k:k + 1])
        nv = float(S.tangent_norm(v)[0])
        if nv < 1e-12:
            k += 1
            continue
        step = delta * (0.1 + 0.9 * unif[k, 2])
        xn = S.retract(xi, v * (step / nv))
        if P.ball:
            rn = float(S.rho(xn)[0])
            if rn > rlimit:
                k += 1
                tried += 1
                continue
        row_old = D[i].copy()
        others = np.delete(X, i, axis=0)
        drow = S.dist_to_many(xn[0], others)
        newrow = np.insert(drow, i, np.inf)
        D[i, :] = newrow
        D[:, i] = newrow
        if P.ball:
            rho_old = rho[i]
            rho[i] = rn
        lnew = current_l()
        tried += 1
        if lnew >= lcur or rng.random() < np.exp((lnew - lcur) / T):
            X[i] = xn[0]
            lcur = lnew
            acc += 1
            sc = _to_score(P, lcur)
            if sc > best:
                best = sc
                bestX = X.copy()
        else:
            D[i, :] = row_old
            D[:, i] = row_old
            if P.ball:
                rho[i] = rho_old
        pe += n - 1
        k += 1
        if tried >= 100:
            rate = acc / tried
            delta = delta * (1.15 if rate > 0.4 else 0.87 if rate < 0.25 else 1.0)
            delta = min(max(delta, 1e-7 * scale), 1.0 * scale)
            acc = tried = 0
        if m % rec_every == 0:
            trace.append((pe, best))
    trace.append((pe, best))
    return dict(X=bestX, score=best, trace=trace, pe=pe, iters=nmoves)


# ----------------------------------------------------------------------
# 3. Lubachevsky-Stillinger-style compression (time-stepped, simplified)
# ----------------------------------------------------------------------
def _toward(S, Xi, Xj, d):
    """Unit tangent vectors at Xi pointing to Xj (row-wise)."""
    if S.kind == "R2":
        return (Xj - Xi) / np.maximum(d, 1e-12)[:, None]
    if S.kind == "S2":
        c = (Xi * Xj).sum(-1)
        s = np.maximum(np.sin(d), 1e-9)
    else:
        c = -S.lorentz(Xi, Xj)
        s = np.maximum(np.sinh(d), 1e-9)
    return (Xj - c[:, None] * Xi) / s[:, None]


def _inner(S, A, B):
    return S.lorentz(A, B) if S.kind == "H2" else (A * B).sum(-1)


def run_ls(P, X0, budget, rng, dt_f=0.02, g0=0.25, g1=0.01):
    S = P.space
    n = P.n
    X = X0.copy()
    V = S.project_tangent(X, rng.normal(size=X.shape))
    V = V / np.maximum(S.tangent_norm(V), 1e-12)[:, None]
    dt = dt_f * P.scale
    a = 0.0
    pe = 0.0
    cost = 2 * P.sweep
    Rclip = (P.R - 1e-6) if P.ball else None
    Dn = S.pair_dist(X)
    pe += P.sweep
    best = _to_score(P, P.lmin(X, Dn))
    bestX = X.copy()
    trace = [(0.0, best)]
    steps = 0
    nsteps_total = max(int((budget - pe) // cost), 1)
    rec_every = max(nsteps_total // 400, 1)
    while pe + cost <= budget:
        frac = pe / budget
        gamma = g0 + (g1 - g0) * frac
        # 1. free flight along geodesics
        X, Vdt = S.transport_velocity(X, V * dt)
        V = Vdt / dt
        # 2. wall reflection (ball problems)
        if P.ball:
            rho = S.rho(X)
            out = rho > (P.R - a)
            if out.any():
                u = S.grad_rho(X, np.ones(n))
                un = np.maximum(S.tangent_norm(u), 1e-12)
                u = u / un[:, None]
                vn = _inner(S, V, u)
                refl = out & (vn > 0)
                V[refl] -= 2.0 * vn[refl][:, None] * u[refl]
                over = np.where(out, rho - (P.R - a), 0.0)
                X = S.retract(X, -over[:, None] * u)
        # 3. pair collisions: exchange normal velocity components, separate overlaps
        D = S.pair_dist(X)
        ii, jj = np.where(np.triu(D < 2.0 * a, 1))
        if len(ii):
            d = D[ii, jj]
            uij = _toward(S, X[ii], X[jj], d)
            uji = _toward(S, X[jj], X[ii], d)
            ai = _inner(S, V[ii], uij)
            aj = _inner(S, V[jj], uji)
            appr = (ai + aj) > 0
            if appr.any():
                f = (ai + aj)[appr]
                np.add.at(V, ii[appr], -f[:, None] * uij[appr])
                np.add.at(V, jj[appr], -f[:, None] * uji[appr])
            ov = 0.5 * (2.0 * a - d)
            push = np.zeros_like(X)
            np.add.at(push, ii, -ov[:, None] * uij)
            np.add.at(push, jj, -ov[:, None] * uji)
            X = S.retract(X, push)
            V = S.project_tangent(X, V)
        if P.ball:
            X = S.clip_to_ball(X, Rclip)
        X = S.renormalize(X)
        # keep velocities tangent and the total kinetic energy fixed (guards against drift)
        V = S.project_tangent(X, V)
        ke = float((S.tangent_norm(V) ** 2).mean())
        if ke > 0:
            V = V / np.sqrt(ke)
        # 4. growth limited by the available room
        Dn = S.pair_dist(X)
        pe += cost
        lmin = P.lmin(X, Dn)
        feasible = lmin / 2.0
        a = min(a + gamma * dt, feasible)
        sc = _to_score(P, lmin)
        if sc > best:
            best, bestX = sc, X.copy()
        steps += 1
        if steps % rec_every == 0:
            trace.append((pe, best))
    trace.append((pe, best))
    return dict(X=bestX, score=best, trace=trace, pe=pe, iters=steps)


# ----------------------------------------------------------------------
# 4. gradient descent followed by a max-min polishing step (supplementary variant, not part of the main study)
# ----------------------------------------------------------------------
def _tangent_basis(S, X):
    """Two orthonormal tangent vectors at every point (Gram-Schmidt on the projected coordinate axes)."""
    n, amb = X.shape
    T = np.stack([S.project_tangent(X, np.tile(np.eye(amb)[k], (n, 1))) for k in range(amb)], axis=1)   # (n, amb, amb)
    nrm = np.array([[float(S.tangent_norm(T[:, k, :])[i]) for k in range(amb)] for i in range(n)])
    k1 = nrm.argmax(1)
    e1 = T[np.arange(n), k1, :]
    e1 = e1 / np.maximum(S.tangent_norm(e1), 1e-12)[:, None]
    best, e2 = np.full(n, -1.0), np.zeros_like(e1)
    for k in range(amb):
        r = T[:, k, :] - _inner(S, T[:, k, :], e1)[:, None] * e1
        rn = S.tangent_norm(r)
        better = rn > best
        e2[better] = (r / np.maximum(rn, 1e-12)[:, None])[better]
        best = np.where(better, rn, best)
    return e1, e2


def _polish(P, X, budget_left, eps0=0.25):
    """Sequential linear programming for the max-min problem: maximize t subject to the linearized
    constraints d_ij + (change) >= t and wall clearances >= t inside a trust region; exact re-evaluation decides acceptance."""
    from scipy.optimize import linprog
    S, n = P.space, P.n
    cost = P.sweep + (n if P.ball else 0)
    pe = cost
    D = S.pair_dist(X)
    lcur = P.lmin(X, D)
    eps = eps0 * lcur
    it = 0
    Rclip = (P.R - 1e-6) if P.ball else None
    while pe + cost <= budget_left and eps > 1e-11:
        e1, e2 = _tangent_basis(S, X)
        ii, jj = np.where(np.triu(D < lcur + 3.0 * eps, 1))
        d = D[ii, jj]
        uij, uji = _toward(S, X[ii], X[jj], d), _toward(S, X[jj], X[ii], d)
        rows, rhs = [], []
        for q in range(len(ii)):                                  # t - d - g.a <= 0   (g = -<e_k, u>)
            r = np.zeros(2 * n + 1)
            r[2 * ii[q]] = _inner(S, e1[ii[q]][None], uij[q][None])[0]
            r[2 * ii[q] + 1] = _inner(S, e2[ii[q]][None], uij[q][None])[0]
            r[2 * jj[q]] = _inner(S, e1[jj[q]][None], uji[q][None])[0]
            r[2 * jj[q] + 1] = _inner(S, e2[jj[q]][None], uji[q][None])[0]
            r[-1] = 1.0
            rows.append(r)
            rhs.append(d[q])
        if P.ball:
            rho = S.rho(X)
            w = S.grad_rho(X, np.ones(n))
            w = w / np.maximum(S.tangent_norm(w), 1e-12)[:, None]
            for i in np.where(2.0 * (P.R - rho) < lcur + 3.0 * eps)[0]:
                r = np.zeros(2 * n + 1)
                r[2 * i] = 2.0 * _inner(S, e1[i][None], w[i][None])[0]
                r[2 * i + 1] = 2.0 * _inner(S, e2[i][None], w[i][None])[0]
                r[-1] = 1.0
                rows.append(r)
                rhs.append(2.0 * (P.R - rho[i]))
        c = np.zeros(2 * n + 1)
        c[-1] = -1.0
        sol = linprog(c, A_ub=np.array(rows), b_ub=np.array(rhs), bounds=[(-eps, eps)] * (2 * n) + [(None, None)], method="highs")
        it += 1
        if sol.status != 0:
            eps *= 0.4
            continue
        a = sol.x[:-1].reshape(n, 2)
        V = a[:, :1] * e1 + a[:, 1:] * e2
        Xn = S.retract(X, V)
        if P.ball:
            Xn = S.clip_to_ball(Xn, Rclip)
        Dn = S.pair_dist(Xn)
        ln = P.lmin(Xn, Dn)
        pe += cost
        if ln > lcur:
            X, D, lcur = Xn, Dn, ln
            eps = min(eps * 1.5, 0.5 * lcur)
        else:
            eps *= 0.4
    return X, lcur, pe, it


def run_gdp(P, X0, budget, rng, polish_share=0.15):
    """Gradient descent on the first (1 - polish_share) of the budget, then max-min polishing on the rest."""
    res = run_gd(P, X0, budget * (1.0 - polish_share), rng)
    X, lcur, pe, it = _polish(P, res["X"], budget - res["pe"])
    sc = _to_score(P, lcur)
    if sc < res["score"]:
        X, sc = res["X"], res["score"]
    return dict(X=X, score=sc, trace=[(0.0, sc)], pe=res["pe"] + pe, iters=res["iters"] + it)


RUNNERS = {"gd": run_gd, "sa": run_sa, "ls": run_ls, "gdp": run_gdp}


def run_algorithm(name, P, X0, budget, seed_seq):
    """Run one optimizer; returns result dict including wall-clock time."""
    rng = np.random.default_rng(seed_seq)
    t0 = time.perf_counter()
    res = RUNNERS[name](P, X0, budget, rng)
    res["time"] = time.perf_counter() - t0
    res["final_check"] = P.score(res["X"])
    return res
