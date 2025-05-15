"""Entanglement swapping for Werner fidelities."""
def swap(F1: float, F2: float) -> float:
    """Calculates the swapped fidelity for two Werner states.
    
    This function computes the resulting fidelity after entanglement swapping is performed on two Werner states with given fidelities.

    Args:
        F1: Fidelity of the first Werner state.
        F2: Fidelity of the second Werner state.

    Returns:
        The fidelity of the swapped Werner state as a float.
    """
    num = (4*F1 - 1) * (4*F2 - 1)
    return (1 + num/3) / 4
