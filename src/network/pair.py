from dataclasses import dataclass

@dataclass
class EntangledPair:
    """Container for a two‑qubit entangled state (Werner)."""
    node1: str
    node2: str
    fidelity: float
    created_at: float
