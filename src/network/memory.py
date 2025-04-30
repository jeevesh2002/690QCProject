"""Simple exponential‑decay quantum memory."""
import math

from configs import physics

class QuantumMemory:
    """Stores a single qubit with exponentially decaying Werner fidelity."""

    def __init__(self, env):
        self.env = env
        self.birth = -math.inf
        self.F0 = physics.F0_LINK  # overwritten on reset

    def reset(self, F_new: float | None = None):
        """Store a *fresh* qubit of fidelity *F_new* (defaults to physics.F0_LINK)."""
        self.birth = self.env.now
        if F_new is not None:
            self.F0 = F_new

    def fidelity(self) -> float:
        dt = self.env.now - self.birth
        return self.F0 * math.exp(-dt / physics.DEFAULT_COHERENCE_TIME_S)
