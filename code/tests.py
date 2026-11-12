"""tests.py -- Validation tests (all must pass before any experiment is run)."""
import sys
import numpy as np
from geometry import (Space, poincare_distance, sphere_distance_haversine,
                      hyperbolic_ball_area, spherical_cap_area, euclid_image_disk)
from algorithms import Problem, run_algorithm, _soft_energy

RESULTS = []


def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(("PASS  " if ok else "FAIL  ") + name + (("  [" + detail + "]") if detail else ""))


def test_sphere_distance():
    S = Space("S2")
    rng = np.random.default_rng(101)
    X = S.random_points(200, rng)
    D = S.pair_dist(X)
    err = 0.0
    for _ in range(300):
        i, j = rng.integers(0, 200, 2)
        if i != j:
            err = max(err, abs(D[i, j] - sphere_distance_haversine(X[i], X[j])))
    check("S2 distance matches arctan2(|a x b|, a.b)", err < 1e-9, f"max err {err:.2e}")
    e = np.eye(3)
    ok = (abs(S.dist(e[0], e[1]) - np.pi / 2) < 1e-12 and abs(S.dist(e[0], -e[0]) - np.pi) < 1e-7
          and abs(S.dist(e[0], np.array([np.cos(0.3), np.sin(0.3), 0.0])) - 0.3) < 1e-12)
    check("S2 closed-form distances (quarter turn, antipode, 0.3 rad)", ok)


def test_hyperbolic_distance():
    S = Space("H2")
    rng = np.random.default_rng(102)
    Z = np.sqrt(rng.uniform(0, 0.97, 300)) * np.exp(1j * rng.uniform(0, 2 * np.pi, 300))
    Zr = np.c_[Z.real, Z.imag]
    X = S.from_disk(Zr)
    err = 0.0
    for i in range(0, 298, 2):
        d1 = S.dist(X[i], X[i + 1])
        d2 = poincare_distance(Z[i], Z[i + 1])
        err = max(err, abs(d1 - d2) / max(d2, 1e-12))
    check("H2 hyperboloid distance equals Poincare disk formula", err < 1e-7, f"max rel err {err:.2e}")
    ok = True
    for s in (0.1, 0.5, 1.0, 2.0, 4.0):
        p = S.from_disk(np.array([[np.tanh(s / 2.0), 0.0]]))[0]
        ok &= abs(S.dist(S.origin(), p) - s) < 1e-9 * max(1, s)
    check("H2 point at Euclidean radius tanh(s/2) is at hyperbolic distance s", ok)
    ok = True
    rng2 = np.random.default_rng(103)
    for _ in range(20):
        r1, r2 = rng2.uniform(0.2, 3, 2)
        t = rng2.uniform(0, 2 * np.pi)
        a = S.from_polar(r1, 0.0)[0]
        b = S.from_polar(r2, t)[0]
        d_law = np.arccosh(np.cosh(r1) * np.cosh(r2) - np.sinh(r1) * np.sinh(r2) * np.cos(t))
        ok &= abs(S.dist(a, b) - d_law) < 1e-8
    check("H2 distance equals hyperbolic law of cosines", ok)
    th = np.linspace(0, 2 * np.pi, 7)[:-1]
    A = hyperbolic_ball_area(2.0)
    rr = np.linspace(0, 2.0, 200001)
    num = 2 * np.pi * np.trapezoid(np.sinh(rr), rr)
    check("H2 disk area 2 pi (cosh R - 1) matches numeric integral", abs(A - num) < 1e-6, f"{A:.6f} vs {num:.6f}")


def test_euclidean():
    S = Space("R2")
    check("R2 distance of (0,0) and (3,4) is 5", abs(S.dist([0, 0], [3, 4]) - 5.0) < 1e-12)
    R = 3.0
    P = Problem("R2", 7, R)
    ang = np.arange(6) * np.pi / 3
    X = np.vstack([[0, 0], np.c_[2 * (R / 3) * np.cos(ang), 2 * (R / 3) * np.sin(ang)]])
    check("R2 hexagonal 7-disk arrangement has radius R/3", abs(P.score(X) - R / 3) < 1e-12,
          f"score {P.score(X):.6f}")


def test_metric_axioms():
    ok_all = True
    for kind in ("S2", "H2", "R2"):
        S = Space(kind)
        rng = np.random.default_rng(104)
        X = S.random_points(60, rng) if kind == "S2" else S.random_points(60, rng, R=3.0)
        D = S.pair_dist(X)
        D0 = D.copy()
        np.fill_diagonal(D0, 0.0)
        sym = np.max(np.abs(D0 - D0.T))
        tri = 0.0
        for _ in range(4000):
            i, j, k = rng.integers(0, 60, 3)
            tri = max(tri, D0[i, k] - (D0[i, j] + D0[j, k]))
        ok = sym < 1e-12 and tri < 1e-9
        ok_all &= ok
        check(f"{kind} distance symmetry and triangle inequality (4000 triples)", ok,
              f"sym {sym:.1e}, worst violation {tri:.1e}")


def test_retraction():
    for kind in ("S2", "H2", "R2"):
        S = Space(kind)
        rng = np.random.default_rng(105)
        X = S.random_points(40, rng) if kind == "S2" else S.random_points(40, rng, R=2.0)
        V = S.project_tangent(X, rng.normal(size=X.shape)) * 0.3
        Y = S.retract(X, V)
        d = np.array([S.dist(X[i], Y[i]) for i in range(40)])
        nv = S.tangent_norm(V)
        err = np.max(np.abs(d - nv))
        check(f"{kind} exponential map moves each point by |v| and stays on the manifold",
              err < 1e-7 and S.on_manifold_error(Y) < 1e-9, f"dist err {err:.1e}, manifold err {S.on_manifold_error(Y):.1e}")


def test_gradient():
    for kind, n, R in (("S2", 9, None), ("S2", 8, 2.0), ("H2", 8, 2.0), ("R2", 8, 2.0)):
        P = Problem(kind, n, R)
        rng = np.random.default_rng(106)
        X = P.initial(rng)
        p = 8.0
        E, G, _ = _soft_energy(P, X, p, True)
        S = P.space
        V = S.project_tangent(X, rng.normal(size=X.shape))
        V = V / np.sqrt(np.sum(S.tangent_norm(V) ** 2))
        h = 1e-6
        Ep, _, _ = _soft_energy(P, S.retract(X, h * V), p, False)
        Em, _, _ = _soft_energy(P, S.retract(X, -h * V), p, False)
        fd = (Ep - Em) / (2 * h)
        if kind == "H2":
            an = float(np.sum(-G[:, 0] * V[:, 0] + G[:, 1] * V[:, 1] + G[:, 2] * V[:, 2]))
        else:
            an = float(np.sum(G * V))
        check(f"{kind}{' cap' if R is not None and kind == 'S2' else ''} analytic Riemannian gradient equals finite difference", abs(fd - an) < 1e-5 * max(1, abs(an)),
              f"fd {fd:.8f}, analytic {an:.8f}")


def test_cap():
    S = Space("S2")
    pole, eq, south = np.array([[0.0, 0.0, 1.0]]), np.array([[1.0, 0.0, 0.0]]), np.array([[0.0, 0.0, -1.0]])
    ok = abs(S.rho(pole)[0]) < 1e-12 and abs(S.rho(eq)[0] - np.pi / 2) < 1e-12 and abs(S.rho(south)[0] - np.pi) < 1e-7
    check("S2 cap: distance from the pole is 0, pi/2 at the equator, pi at the antipode", ok)
    rr = np.linspace(0, 2.0, 200001)
    num = 2 * np.pi * np.trapezoid(np.sin(rr), rr)
    check("S2 cap: area 2 pi (1 - cos R) matches numeric integral", abs(spherical_cap_area(2.0) - num) < 1e-6, f"{spherical_cap_area(2.0):.6f} vs {num:.6f}")
    rng = np.random.default_rng(107)
    X = S.random_points(40000, rng, R=2.0)
    frac = float((S.rho(X) <= 1.0).mean())
    exp = (1 - np.cos(1.0)) / (1 - np.cos(2.0))
    se = np.sqrt(exp * (1 - exp) / 40000)
    check("S2 cap: random points are uniform by area (share within R/2 matches theory, 4 s.e.)", abs(frac - exp) < 4 * se and S.rho(X).max() <= 2.0 + 1e-9, f"{frac:.4f} vs {exp:.4f}")
    Rr = 0.05
    ang = np.arange(6) * np.pi / 3
    X7 = np.vstack([[0, 0, 1.0], S.from_polar(np.full(6, 2 * Rr / 3), ang)])
    P7 = Problem("S2", 7, Rr)
    check("S2 cap: Euclidean limit, 7 disks in a cap of radius 0.05 reach R/3 within 0.2%", abs(P7.score(X7) / (Rr / 3) - 1) < 2e-3, f"ratio {P7.score(X7) / (Rr / 3):.5f}")
    Y = S.clip_to_ball(S.random_points(10, rng) * 1.0, 1.0)
    check("S2 cap: clipping moves outside points exactly to the cap boundary", np.allclose(S.rho(Y), 1.0, atol=1e-9) or np.all(S.rho(Y) <= 1.0 + 1e-9))


def test_known_tammes():
    S = Space("S2")
    tet = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], float) / np.sqrt(3)
    octa = np.vstack([np.eye(3), -np.eye(3)])
    ph = (1 + np.sqrt(5)) / 2
    ico = np.array([[0, s1, s2 * ph] for s1 in (1, -1) for s2 in (1, -1)]
                   + [[s1, s2 * ph, 0] for s1 in (1, -1) for s2 in (1, -1)]
                   + [[s2 * ph, 0, s1] for s1 in (1, -1) for s2 in (1, -1)], float)
    ico /= np.linalg.norm(ico, axis=1, keepdims=True)
    for name, X, ref in (("tetrahedron N=4", tet, np.arccos(-1 / 3)),
                         ("octahedron N=6", octa, np.pi / 2),
                         ("icosahedron N=12", ico, np.arctan(2.0))):
        d = Problem("S2", len(X)).score(X)
        check(f"Closed-form Tammes configuration, {name}: min distance {ref:.6f} rad", abs(d - ref) < 1e-12,
              f"computed {d:.12f}")


def test_recover_optima():
    """Pass criterion: the optimizer suite recovers each known optimum (best of the three
    optimizers over 5 test seeds).  Per-optimizer recovery is hypothesis H3 and is
    reported by the main experiment, not treated as a validation criterion."""
    refs = {4: np.arccos(-1 / 3), 6: np.pi / 2, 12: np.arctan(2.0)}
    for n, ref in refs.items():
        P = Problem("S2", n)
        per = {}
        for alg in ("gd", "sa", "ls"):
            gaps = []
            for seed in (9101, 9102, 9103, 9104, 9105):
                X0 = P.initial(np.random.default_rng(seed))
                r = run_algorithm(alg, P, X0, 1500 * P.sweep, [seed, 3])
                gaps.append(ref - r["score"])
            per[alg] = min(gaps)
        best = min(per.values())
        info = ", ".join(f"{k} {v:.1e}" for k, v in per.items())
        check(f"Optimizer suite recovers the N={n} Tammes optimum (best gap < 2e-3 rad over 5 test seeds)",
              best < 2e-3, f"best gap per optimizer: {info}")


def run_all():
    test_sphere_distance()
    test_hyperbolic_distance()
    test_euclidean()
    test_metric_axioms()
    test_retraction()
    test_gradient()
    test_cap()
    test_known_tammes()
    test_recover_optima()
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    print(f"\n{npass} of {len(RESULTS)} tests passed")
    return npass == len(RESULTS)


if __name__ == "__main__":
    sys.exit(0 if run_all() else 1)
