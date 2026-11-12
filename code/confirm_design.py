"""confirm_design.py -- conditions, reference densities, and boundary shares of the confirmatory round.

Everything here is fixed by the preregistration (PREREGISTRATION.md) before any evaluation seed is run.
"""
import numpy as np

EVAL_SEEDS = list(range(101, 121))          # fresh seeds, never used before
PILOT_SEEDS = [9101, 9102, 9103, 9104]      # tuning only
BUDGETS = [500, 1500, 3000]                 # sweeps; 1 sweep = n(n-1)/2 pair-distance evaluations
MAIN_BUDGET = 1500
ALGS = {"gd": 1, "sa": 2, "ls": 3, "gdp": 4, "lbfgsb": 5, "bh": 6}
TAMMES_N = [9, 13, 14, 24, 30, 40, 60]
EA_AREAS = [3.0, 6.0, 12.0]
EA_N = [12, 24]
LARGE_RH = [2.0, 3.0, 6.0, 8.0]
LARGE_N = {2.0: 24, 3.0: 36, 6.0: 50, 8.0: 70}


def area(kind, R):
    if kind == "S2cap":
        return 2 * np.pi * (1 - np.cos(R))
    if kind == "H2":
        return 2 * np.pi * (np.cosh(R) - 1)
    return np.pi * R * R


def radius_for_area(kind, A):
    if kind == "S2cap":
        return float(np.arccos(1 - A / (2 * np.pi)))
    if kind == "H2":
        return float(np.arccosh(1 + A / (2 * np.pi)))
    return float(np.sqrt(A / np.pi))


def conditions():
    out, cid = [], 1000
    for N in TAMMES_N:
        out.append(dict(cid=cid, group="tammes", kind="S2", n=N, R=None, area=4 * np.pi, label=f"Tammes N = {N}"))
        cid += 1
    for A in EA_AREAS:
        for n in EA_N:
            for kind, lab in (("S2cap", "cap"), ("R2", "Euclidean"), ("H2", "hyperbolic")):
                out.append(dict(cid=cid, group="equal_area", kind=kind, n=n, R=radius_for_area(kind, A), area=A, label=f"A = {A:g}, n = {n}, {lab}"))
                cid += 1
    for Rh in LARGE_RH:
        A = area("H2", Rh)
        n = LARGE_N[Rh]
        for kind, lab in (("R2", "Euclidean"), ("H2", "hyperbolic")):
            R = radius_for_area(kind, A)
            out.append(dict(cid=cid, group="large", kind=kind, n=n, R=R, area=A, label=f"R_H = {Rh:g}, n = {n}, {lab}"))
            cid += 1
    return out


def ref_density(kind, r):
    """Upper bound on the density of any packing of equal disks of radius r in the whole plane/space (Fejes Toth 1943 for the sphere,
    Thue/Fejes Toth for the plane, Boroczky 1978 for the hyperbolic plane): the density of the disks inside the regular
    triangle whose vertices are the centers of three mutually tangent disks."""
    if kind == "R2":
        return float(np.pi / np.sqrt(12.0))
    if kind == "H2":
        c = np.cosh(2 * r)
        al = np.arccos(c / (c + 1.0))
        return float(3 * al * (np.cosh(r) - 1) / (np.pi - 3 * al))
    c = np.cos(2 * r)                     # spherical (cap)
    al = np.arccos(c / (1.0 + c))
    return float(3 * al * (1 - np.cos(r)) / (3 * al - np.pi))


def boundary_share(kind, R, r):
    """Share of the ball's area that lies within distance r of its boundary."""
    return float(1.0 - area(kind, R - r) / area(kind, R))


def deficit(kind, R, n, r):
    """Density deficit  1 - (density achieved) / (reference density for disks of radius r)."""
    dens = n * area(kind, r) / area(kind, R)
    return float(1.0 - dens / ref_density(kind, r))
