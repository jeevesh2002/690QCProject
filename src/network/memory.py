import math
from src.configs import physics

class MemoryRegister:
    """A single‑qubit memory with exponential decoherence F(t)=F0·e^{‑t/T_coh}.

    Parameters
    ----------
    env : simpy.Environment
        Global simulation clock.
    F0  : float
        Initial fidelity at creation.
    T_coh : float
        Coherence time constant in seconds.
    """
    def __init__(self, env, F0=physics.F0_LINK, T_coh=physics.DEFAULT_COHERENCE_TIME_S):
        self.env = env
        self.birth = env.now
        self.F0 = F0
        self.T_coh = T_coh

    def fidelity(self):
        """Return current fidelity after free evolution."""
        age = self.env.now - self.birth
        return self.F0 * math.exp(-age / self.T_coh)

    def reset(self, F_new=None):
        """Overwrite the stored qubit (e.g., after swapping) and reset timer."""
        self.birth = self.env.now
        if F_new is not None:
            self.F0 = F_new
