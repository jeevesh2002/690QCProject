"""Entanglement swapping for Werner fidelities."""
def swap(F1: float, F2: float) -> float:
    num = (4*F1 - 1) * (4*F2 - 1)
    return (1 + num/3) / 4
