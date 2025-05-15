"""Quantum memory with exponential fidelity decay."""
import math
from configs import physics

class QuantumMemory:
    """Stores one qubit entangled with a neighbour and tracks its fidelity.
    
    This class models a quantum memory that holds a single qubit, tracking its fidelity and simulating exponential decay over time.
    """
    def __init__(self, env, fidelity: float | None = None):
        self.env = env
        self.birth = -math.inf
        self.F0 = fidelity or physics.F0_LINK

    def reset(self, fidelity: float):
        """Resets the quantum memory with a new fidelity and updates its birth time.

        Args:
            fidelity: The new initial fidelity for the memory.
        """
        self.birth = self.env.now
        self.F0 = fidelity

    def fidelity(self) -> float:
        """Calculates the current fidelity of the stored qubit.

        Returns:
            The current fidelity as a float, accounting for exponential decay since the last reset.
        """
        dt = self.env.now - self.birth
        return self.F0 * math.exp(-dt / physics.DEFAULT_COHERENCE_TIME_S)

    # pretty
    def __repr__(self):
        """Returns a string representation of the quantum memory, showing fidelity and age.

        Returns:
            A string summarizing the current fidelity and age of the memory.
        """
        age = self.env.now - self.birth
        return f"<QMem F={self.fidelity():.3f} age={age*1e3:.1f}ms>"
