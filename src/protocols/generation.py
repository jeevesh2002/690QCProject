import random
from configs import physics
import simpy

class Pair:
    def __init__(self, fidelity: float):
        self.fidelity = fidelity

def try_generate(env: simpy.Environment, link) -> Pair | None:
    """Attempt heralded single‑click generation on *link* (Bernoulli)."""
    success = random.random() < link.success_prob * physics.DETECTION_EFFICIENCY
    latency = (link.length_km * 1000) / physics.SPEED_OF_LIGHT_FIBER  # one‑way
    yield env.timeout(2 * latency)  # round‑trip
    return Pair(physics.F0_LINK) if success else None
