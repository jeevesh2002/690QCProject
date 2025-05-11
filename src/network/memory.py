"""Quantum memory with exponential fidelity decay."""
import math
from configs import physics

class QuantumMemory:
    """Stores one qubit entangled with a neighbour and tracks its fidelity."""
    def __init__(self, env, fidelity: float | None = None):
        self.env = env
        self.birth = -math.inf
        self.F0 = fidelity or physics.F0_LINK

    def reset(self, fidelity: float):
        self.birth = self.env.now
        self.F0 = fidelity

    def fidelity(self) -> float:
        dt = self.env.now - self.birth
        return self.F0 * math.exp(-dt / physics.DEFAULT_COHERENCE_TIME_S)

    # pretty
    def __repr__(self):
        age = self.env.now - self.birth
        return f"<QMem F={self.fidelity():.3f} age={age*1e3:.1f}ms>"
