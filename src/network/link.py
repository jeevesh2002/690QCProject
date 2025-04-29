import math, random
from configs import physics

class FibreLink:
    """Bidirectional optical fibre characterised by length and loss.

    Attributes
    ----------
    length_km : float
        Physical length between the two end nodes.
    success_prob : float
        Probability that a single‑click attempt succeeds (Beer–Lambert).
    latency_s : float
        One‑way propagation delay (used for heralding round‑trips).
    """
    def __init__(self, env, node_a, node_b, length_km):
        self.env = env
        self.a = node_a
        self.b = node_b
        self.length_km = length_km

        self.success_prob = math.exp(-length_km / physics.ATTENUATION_LENGTH_KM)
        self.latency_s = (length_km * 1e3) / physics.SPEED_OF_LIGHT_FIBER

        # allocate one memory per end
        from network.memory import MemoryRegister
        self.a.add_memory(self.b, MemoryRegister(env))
        self.b.add_memory(self.a, MemoryRegister(env))

    # ---------------------------------------------------------------------
    #  Elementary entanglement generation
    # ---------------------------------------------------------------------
    def attempt_single_click(self):
        """Stochastic Bernoulli attempt returning (success, latency_s)."""
        success = random.random() < self.success_prob * physics.DETECTION_EFFICIENCY
        # heralding requires a round‑trip; so add both directions
        latency = 2 * self.latency_s
        return success, latency
