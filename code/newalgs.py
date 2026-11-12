"""newalgs.py -- stronger baselines for the confirmatory round (added; algorithms.py is unchanged).

  lbfgsb : SciPy L-BFGS-B on the soft-minimum energy with the exponent p raised in stages (continuation)
  bh     : basin hopping (scipy.optimize.basinhopping) with L-BFGS-B local minimization on the soft-minimum energy
Budget is the same pair-distance-evaluation count as the other methods: each energy-and-gradient evaluation
costs one sweep (plus n wall clearances in ball problems).  Points are optimized in an unconstrained chart:
sphere  x = y/|y| (y in R^3);  hyperboloid  x = (sqrt(1+|u|^2), u);  Euclidean plane  x = u.
"""
import time
import numpy as np
from scipy.optimize import minimize, basinhopping
from algorithms import Problem, _soft_energy, _to_score, RUNNERS, ALG_NAMES


class BudgetExhausted(Exception):
    pass


def to_w(P, X):
    return (X[:, 1:] if P.space.kind == "H2" else X).ravel().copy()


def from_w(P, w):
    k = P.space.kind
    if k == "S2":
        Y = w.reshape(P.n, 3)
        return Y / np.linalg.norm(Y, axis=1, keepdims=True)
    if k == "H2":
        U = w.reshape(P.n, 2)
        return np.c_[np.sqrt(1.0 + (U ** 2).sum(1)), U]
    return w.reshape(P.n, 2)


def grad_w(P, X, G, w):
    """Chain rule from the Riemannian gradient G to the chart coordinates."""
    k = P.space.kind
    if k == "S2":
        Y = w.reshape(P.n, 3)
        return (G / np.linalg.norm(Y, axis=1, keepdims=True)).ravel()
    if k == "H2":
        U = X[:, 1:]
        return (G[:, 1:] - G[:, :1] * U / X[:, :1]).ravel()
    return G.ravel()


class _Obj:
    """Energy-gradient callable in chart coordinates with budget accounting and best-visited tracking."""
    def __init__(self, P, budget):
        self.P, self.budget = P, budget
        self.cost = P.sweep + (P.n if P.ball else 0)
        self.pe = 0.0
        self.best, self.bestX = -np.inf, None
        self.p = 2.0
        self.nev = 0

    def __call__(self, w):
        if self.pe + self.cost > self.budget:
            raise BudgetExhausted
        P = self.P
        X = from_w(P, w)
        E, G, lmin = _soft_energy(P, X, self.p, True)
        self.pe += self.cost
        self.nev += 1
        if P.ball and float(P.space.rho(X).max()) >= P.R:
            pass
        sc = _to_score(P, lmin)
        if sc > self.best and (not P.ball or float(P.lmin(X)) > 0):
            self.best, self.bestX = sc, X.copy()
        return E, grad_w(P, X, G, w)


def run_lbfgsb(P, X0, budget, rng, pmax=150.0, stages=10, p0=2.0):
    """Continuation in p with L-BFGS-B.  L-BFGS-B stops by its own convergence tests, so when a continuation
    finishes with budget left, the method restarts from a new random configuration (same seeded stream) until
    the budget is used; the best configuration visited is returned."""
    obj = _Obj(P, budget)
    start = X0
    first = True
    try:
        while True:
            used0 = obj.pe
            w = to_w(P, start)
            stage_budget = (budget if first else min(budget - obj.pe, budget)) / stages
            for s in range(stages):
                obj.p = p0 * (pmax / p0) ** (s / (stages - 1))
                mf = max(int(stage_budget // obj.cost), 5)
                r = minimize(obj, w, jac=True, method="L-BFGS-B", options=dict(maxfun=mf, maxiter=100000, ftol=1e-13, gtol=1e-11, maxcor=10))
                w = r.x
                X = from_w(P, w)
                if P.ball:
                    X = P.space.clip_to_ball(X, P.R - 1e-6)
                    w = to_w(P, X)
            first = False
            if budget - obj.pe < 0.5 * (obj.pe - used0) or budget - obj.pe < 20 * obj.cost:
                break
            start = P.initial(rng)
    except BudgetExhausted:
        pass
    X = obj.bestX if obj.bestX is not None else X0
    sc = P.score(X)
    return dict(X=X, score=sc, trace=[(0.0, sc)], pe=obj.pe, iters=obj.nev)


def run_bh(P, X0, budget, rng, step=0.2, pbh=60.0, temp=0.02, local_maxfun=60):
    obj = _Obj(P, budget)
    obj.p = pbh
    scale = P.scale

    def take_step(w):
        return w + rng.normal(scale=step * scale, size=w.shape)

    mk = dict(method="L-BFGS-B", jac=True, options=dict(maxfun=local_maxfun, ftol=1e-13, gtol=1e-11))
    w0 = to_w(P, X0)
    try:
        basinhopping(obj, w0, niter=10 ** 6, T=temp, take_step=take_step, minimizer_kwargs=mk, seed=int(rng.integers(2 ** 31)))
    except BudgetExhausted:
        pass
    X = obj.bestX if obj.bestX is not None else X0
    if P.ball:
        X = P.space.clip_to_ball(X, P.R - 1e-6)
    sc = P.score(X)
    return dict(X=X, score=sc, trace=[(0.0, sc)], pe=obj.pe, iters=obj.nev)


NEW_RUNNERS = {"lbfgsb": run_lbfgsb, "bh": run_bh}
ALG_NAMES.update({"lbfgsb": "L-BFGS-B (SciPy)", "bh": "Basin hopping (SciPy)"})


def run_any(name, P, X0, budget, seed_seq, **params):
    """Run any of the six methods; extra keyword parameters override tuned defaults."""
    rng = np.random.default_rng(seed_seq)
    fn = NEW_RUNNERS.get(name) or RUNNERS[name]
    t0 = time.perf_counter()
    res = fn(P, X0, budget, rng, **params)
    res["time"] = time.perf_counter() - t0
    res["final_check"] = P.score(res["X"])
    return res
