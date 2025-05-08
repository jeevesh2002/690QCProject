"""Quantum memory with exponential fidelity decay."""
import math
from configs import physics

class QuantumMemory:
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
        return f"<QMem F0={self.F0:.3f} born={self.birth:.3f}>"
