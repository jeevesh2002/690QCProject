from dataclasses import dataclass

@dataclass
class EntangledPair:
    """Stores one qubit entangled with a neighbour and tracks its fidelity.

    Represents an entangled pair of nodes with associated fidelity and creation time.
    """
    node1: str
    node2: str
    fidelity: float
    created_at: float
