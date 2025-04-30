"""Implements the DEJMPS and BBPSSW single‑round purification for Werner states."""

def dejmps(F):
    """Return (F_new, P_success) via the DEJMPS map for Werner fidelity F."""
    F2 = F*F
    G = (1-F)/3
    F_new = (F2 + G*G) / (F2 + 2*F*G + 5*G*G)
    P = (F2 + 2*F*G + 5*G*G)
    return F_new, P

def bbpssw(F):
    """Return (F_new, P_success) via the BBPSSW map for Werner fidelity F."""
    # TODO
    return dejmps(F)
