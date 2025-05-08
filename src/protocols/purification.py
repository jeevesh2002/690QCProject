"""Purification maps (DEJMPS, BBPSSW)."""
from typing import Tuple

def dejmps(F: float) -> Tuple[float, float]:
    """Return (F', P_success) after one round of DEJMPS on Werner state."""
    F2 = F * F
    G = (1 - F) / 3
    G2 = G * G
    P = F2 + G2 + 2 * F * G
    F_new = (F2 + (G2 / 9)) / P
    return F_new, P

def bbpssw(F: float) -> Tuple[float, float]:
    """Return (F', P_success) after one round of BBPSSW on Werner state."""
    # TODO
    return dejmps(F)

# helper dispatcher
def get_scheme(name: str):
    name = name.lower()
    if name in {'dejmps', 'd'}:
        return dejmps
    if name in {'bbpssw', 'bbp'}:
        return bbpssw
    raise ValueError(name)
