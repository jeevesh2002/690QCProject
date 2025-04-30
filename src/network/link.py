"""Fibre link between two nodes."""
import math
from configs import physics

class FibreLink:
    """Bidirectional optical fibre characterised by its length in km."""

    def __init__(self, env, node_a, node_b, length_km: float, *, attenuation_length_km: float | None = None):
        self.env = env
        self.a = node_a
        self.b = node_b
        self.length_km = length_km
        self._att_len = attenuation_length_km or physics.physics.ATTENUATION_LENGTH_KM
        self.success_prob = math.exp(-length_km / self._att_len)

    # convenience for protocols ----------------
    def other(self, node):
        return self.b if node is self.a else self.a
