"""geometry.py -- Geometry of the three spaces used in the study.

Algorithmic Optimization of Dense Sphere Packings in Non-Euclidean Spaces

Spaces
  S2 : unit 2-sphere, points are unit vectors in R^3 (curvature +1)
  H2 : hyperbolic plane, curvature -1, hyperboloid model; a point is
       X = (x0, x1, x2) with -x0^2 + x1^2 + x2^2 = -1 and x0 > 0.
       The Poincare disk coordinate is (x1, x2) / (1 + x0).
  R2 : Euclidean plane (control), points are vectors in R^2.

All three spaces share one interface so that the optimizers are written
once.  Only numpy is used.
"""
import numpy as np

TINY = 1e-12


class Space:
    """A constant-curvature plane (S2, H2 or R2) with a shared interface."""

    def __init__(self, kind):
        if kind not in ("S2", "H2", "R2"):
            raise ValueError(kind)
        self.kind = kind
        self.amb = 2 if kind == "R2" else 3  # ambient dimension

    # ------------------------------------------------------------------
    # basic algebra
    # ------------------------------------------------------------------
    def lorentz(self, A, B):
        """Row-wise Lorentz product <A,B> = -a0 b0 + a1 b1 + a2 b2."""
        return -A[:, 0] * B[:, 0] + A[:, 1] * B[:, 1] + A[:, 2] * B[:, 2]

    # ------------------------------------------------------------------
    # distances
    # ------------------------------------------------------------------
    def dist_from_c(self, c):
        if self.kind == "S2":
            return 2.0 * np.arcsin(np.sqrt(np.clip((1.0 - c) / 2.0, 0.0, 1.0)))
        # H2
        return 2.0 * np.arcsinh(np.sqrt(np.maximum((c - 1.0) / 2.0, 0.0)))

    def pair_c(self, X):
        """c_ij = cos d_ij (S2) or cosh d_ij (H2)."""
        if self.kind == "S2":
            return X @ X.T
        G = -(X[:, :1] @ X[:, :1].T) + X[:, 1:] @ X[:, 1:].T  # Lorentz product
        return -G

    def pair_dist(self, X):
        """Full n x n distance matrix with +inf on the diagonal."""
        n = len(X)
        if self.kind == "R2":
            diff = X[:, None, :] - X[None, :, :]
            D = np.sqrt((diff ** 2).sum(-1))
        else:
            D = self.dist_from_c(self.pair_c(X))
        D[np.arange(n), np.arange(n)] = np.inf
        return D

    def dist_to_many(self, x, Y):
        """Distance from one point x to each row of Y."""
        if self.kind == "R2":
            return np.sqrt(((Y - x) ** 2).sum(-1))
        if self.kind == "S2":
            c = Y @ x
        else:
            c = -self.lorentz(Y, np.broadcast_to(x, Y.shape))
        return self.dist_from_c(c)

    def dist(self, x, y):
        """Distance between two single points."""
        return float(self.dist_to_many(np.asarray(x, float), np.asarray(y, float)[None, :])[0])

    # ------------------------------------------------------------------
    # radial distance from the origin (ball problems on H2 and R2)
    # ------------------------------------------------------------------
    def origin(self):
        if self.kind == "S2":
            return np.array([0.0, 0.0, 1.0])
        if self.kind == "H2":
            return np.array([1.0, 0.0, 0.0])
        if self.kind == "R2":
            return np.zeros(2)
        raise RuntimeError

    def rho(self, X):
        if self.kind == "R2":
            return np.sqrt((X ** 2).sum(-1))
        if self.kind == "S2":
            return 2.0 * np.arcsin(np.sqrt(np.clip((1.0 - X[:, 2]) / 2.0, 0.0, 1.0)))
        if self.kind == "H2":
            return 2.0 * np.arcsinh(np.sqrt(np.maximum((X[:, 0] - 1.0) / 2.0, 0.0)))
        raise RuntimeError

    def grad_rho(self, X, w):
        """sum_i w_i * grad rho(X_i)  as an (n, amb) array of tangent vectors."""
        r = self.rho(X)
        if self.kind == "R2":
            nrm = np.maximum(r, TINY)[:, None]
            return w[:, None] * X / nrm
        O = self.origin()
        if self.kind == "S2":
            s = np.maximum(np.sin(r), TINY)
            c = X[:, 2]
        else:
            s = np.maximum(np.sinh(r), TINY)
            c = X[:, 0]
        return (w / s)[:, None] * (c[:, None] * X - O[None, :])

    # ------------------------------------------------------------------
    # Riemannian gradient of  sum_{i<j} f(d_ij)  given W_ij = f'(d_ij)
    # ------------------------------------------------------------------
    def grad_pairs(self, X, D, W):
        """Return G with G_i = sum_j W_ij grad_{X_i} d_ij  (tangent at X_i)."""
        n = len(X)
        if self.kind == "R2":
            a = W / np.where(np.isfinite(D), np.maximum(D, TINY), 1.0)
            np.fill_diagonal(a, 0.0)
            return X * a.sum(1)[:, None] - a @ X
        C = self.pair_c(X)
        if self.kind == "S2":
            s = np.sqrt(np.maximum(1.0 - C * C, 1e-18))
        else:
            s = np.sqrt(np.maximum(C * C - 1.0, 1e-18))
        a = W / s
        np.fill_diagonal(a, 0.0)
        return X * (a * C).sum(1)[:, None] - a @ X

    # ------------------------------------------------------------------
    # moving along geodesics
    # ------------------------------------------------------------------
    def tangent_norm(self, V, X=None):
        if self.kind == "H2":
            return np.sqrt(np.maximum(self.lorentz(V, V), 0.0))
        return np.sqrt((V ** 2).sum(-1))

    def project_tangent(self, X, U):
        """Project ambient vectors U onto the tangent space at X (row-wise)."""
        if self.kind == "R2":
            return U
        if self.kind == "S2":
            return U - (U * X).sum(-1, keepdims=True) * X
        return U + self.lorentz(X, U)[:, None] * X

    def retract(self, X, V):
        """Exponential map: move each X_i along the geodesic with initial velocity V_i."""
        if self.kind == "R2":
            return X + V
        nv = self.tangent_norm(V)
        nv_s = np.maximum(nv, TINY)
        if self.kind == "S2":
            Y = np.cos(nv)[:, None] * X + (np.sin(nv) / nv_s)[:, None] * V
            return Y / np.linalg.norm(Y, axis=1, keepdims=True)
        Y = np.cosh(nv)[:, None] * X + (np.sinh(nv) / nv_s)[:, None] * V
        Y[:, 0] = np.sqrt(1.0 + Y[:, 1] ** 2 + Y[:, 2] ** 2)
        return Y

    def transport_velocity(self, X, V):
        """Velocity of the geodesic started at X with velocity V after unit time
        (used by the compression method); returns (X_new, V_new)."""
        if self.kind == "R2":
            return X + V, V.copy()
        nv = self.tangent_norm(V)
        nv_s = np.maximum(nv, TINY)
        if self.kind == "S2":
            Xn = np.cos(nv)[:, None] * X + (np.sin(nv) / nv_s)[:, None] * V
            Vn = -(nv * np.sin(nv))[:, None] * X + np.cos(nv)[:, None] * V
            nrm = np.linalg.norm(Xn, axis=1, keepdims=True)
            Xn = Xn / nrm
            return Xn, Vn
        Xn = np.cosh(nv)[:, None] * X + (np.sinh(nv) / nv_s)[:, None] * V
        Vn = (nv * np.sinh(nv))[:, None] * X + np.cosh(nv)[:, None] * V
        Xn[:, 0] = np.sqrt(1.0 + Xn[:, 1] ** 2 + Xn[:, 2] ** 2)
        return Xn, Vn

    def renormalize(self, X):
        if self.kind == "S2":
            return X / np.linalg.norm(X, axis=1, keepdims=True)
        if self.kind == "H2":
            X = X.copy()
            X[:, 0] = np.sqrt(1.0 + X[:, 1] ** 2 + X[:, 2] ** 2)
        return X

    def clip_to_ball(self, X, Rmax):
        """Radially pull points with rho > Rmax back to rho = Rmax."""
        r = self.rho(X)
        out = r > Rmax
        if not out.any():
            return X
        X = X.copy()
        if self.kind == "R2":
            X[out] *= (Rmax / np.maximum(r[out], TINY))[:, None]
        elif self.kind == "S2":
            u = X[out, :2]
            un = np.maximum(np.linalg.norm(u, axis=1, keepdims=True), TINY)
            X[out, :2] = np.sin(Rmax) * u / un
            X[out, 2] = np.cos(Rmax)
        else:
            u = X[out, 1:]
            un = np.maximum(np.linalg.norm(u, axis=1, keepdims=True), TINY)
            X[out, 1:] = np.sinh(Rmax) * u / un
            X[out, 0] = np.cosh(Rmax)
        return X

    # ------------------------------------------------------------------
    # sampling and conversions
    # ------------------------------------------------------------------
    def random_points(self, n, rng, R=None):
        """n random points: uniform on S2, or uniform in the ball of radius R."""
        if self.kind == "S2" and R is None:
            v = rng.normal(size=(n, 3))
            return v / np.linalg.norm(v, axis=1, keepdims=True)
        th = rng.uniform(0.0, 2.0 * np.pi, n)
        u = rng.uniform(0.0, 1.0, n)
        if self.kind == "R2":
            r = R * np.sqrt(u)
            return np.c_[r * np.cos(th), r * np.sin(th)]
        if self.kind == "S2":
            # cap: area element sin(rho) d rho d theta, cdf = (1 - cos r)/(1 - cos R)
            r = np.arccos(1.0 - u * (1.0 - np.cos(R)))
            return np.c_[np.sin(r) * np.cos(th), np.sin(r) * np.sin(th), np.cos(r)]
        # H2: area element sinh(rho) d rho d theta, cdf = (cosh r - 1)/(cosh R - 1)
        r = np.arccosh(1.0 + u * (np.cosh(R) - 1.0))
        return np.c_[np.cosh(r), np.sinh(r) * np.cos(th), np.sinh(r) * np.sin(th)]

    def from_polar(self, r, th):
        """Point from (radial distance, angle); H2 and R2 only."""
        r = np.atleast_1d(r)
        th = np.atleast_1d(th)
        if self.kind == "R2":
            return np.c_[r * np.cos(th), r * np.sin(th)]
        if self.kind == "S2":
            return np.c_[np.sin(r) * np.cos(th), np.sin(r) * np.sin(th), np.cos(r)]
        return np.c_[np.cosh(r), np.sinh(r) * np.cos(th), np.sinh(r) * np.sin(th)]

    def to_plane(self, X):
        """Planar drawing coordinates: Poincare disk for H2, identity for R2."""
        if self.kind == "H2":
            return X[:, 1:] / (1.0 + X[:, :1])
        return X

    def from_disk(self, Z):
        """Hyperboloid point from Poincare disk coordinates."""
        z2 = (Z ** 2).sum(-1)
        x0 = (1.0 + z2) / (1.0 - z2)
        sp = 2.0 / (1.0 - z2)
        return np.c_[x0, sp * Z[:, 0], sp * Z[:, 1]]

    def on_manifold_error(self, X):
        if self.kind == "S2":
            return float(np.max(np.abs(np.linalg.norm(X, axis=1) - 1.0)))
        if self.kind == "H2":
            return float(np.max(np.abs(-X[:, 0] ** 2 + X[:, 1] ** 2 + X[:, 2] ** 2 + 1.0)))
        return 0.0


# ----------------------------------------------------------------------
# closed-form reference distances (independent of the Space class)
# ----------------------------------------------------------------------
def poincare_distance(z, w):
    """Poincare disk distance (curvature -1) between complex numbers z, w."""
    num = 2.0 * abs(z - w) ** 2
    den = (1.0 - abs(z) ** 2) * (1.0 - abs(w) ** 2)
    return float(np.arccosh(1.0 + num / den))


def sphere_distance_haversine(a, b):
    """Great-circle distance between unit vectors a, b using atan2 form."""
    return float(np.arctan2(np.linalg.norm(np.cross(a, b)), np.dot(a, b)))


def spherical_cap_area(R):
    """Area of a spherical cap of angular radius R on the unit sphere: 2 pi (1 - cos R)."""
    return 2.0 * np.pi * (1.0 - np.cos(R))


def hyperbolic_ball_area(R):
    """Area of a hyperbolic disk of radius R (curvature -1): 2 pi (cosh R - 1)."""
    return 2.0 * np.pi * (np.cosh(R) - 1.0)


def euclid_image_disk(s, r):
    """Euclidean center and radius (in the Poincare disk) of the hyperbolic disk
    of radius r whose center lies at hyperbolic distance s from the origin."""
    lo = np.tanh((s - r) / 2.0) if s >= r else -np.tanh((r - s) / 2.0)
    hi = np.tanh((s + r) / 2.0)
    return 0.5 * (lo + hi), 0.5 * (hi - lo)
