"""Entanglement‑swapping fidelity transformation for Werner states."""
def swap(F1, F2):
    """Return fidelity of resulting pair after swapping two Werner states.

    Formula: Let x=(4F−1)/3.  After a Bell‑state measurement the new
    Werner parameter is x' = x1 * x2.  Therefore
        F' = (1 + 3 x') / 4 = (1 + (4F1-1)(4F2-1)/3) / 4
    """
    num = (4*F1 - 1) * (4*F2 - 1)
    return (1 + num/3) / 4
