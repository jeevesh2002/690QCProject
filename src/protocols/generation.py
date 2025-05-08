"""Heralded single-click entanglement generation that stores qubits in memory."""
import random, logging
import simpy
from configs import physics

logger = logging.getLogger(__name__)

class Pair:
    def __init__(self, fidelity: float):
        self.fidelity = fidelity

def try_generate(env: simpy.Environment, link) -> Pair | None:
    """Attempt one entanglement generation on *link*.

    On success, store each qubit in the respective node's memory list
    and free the communication interface (implicit).
    """
    # mark comm busy
    link.a.set_comm_busy(link.b, True)
    link.b.set_comm_busy(link.a, True)

    success = random.random() < link.success_prob * physics.DETECTION_EFFICIENCY
    latency = (link.length_km * 1000) / physics.SPEED_OF_LIGHT_FIBER
    yield env.timeout(2 * latency)

    # free communication qubit
    link.a.set_comm_busy(link.b, False)
    link.b.set_comm_busy(link.a, False)

    if not success:
        logger.debug("%7.3f s  Generation failed on %s", env.now, link)
        return None

    # store in memory
    link.a.add_memory_qubit(link.b, physics.F0_LINK)
    link.b.add_memory_qubit(link.a, physics.F0_LINK)
    logger.debug("%7.3f s  Generation success on %s (F0=%.2f)",
                 env.now, link, physics.F0_LINK)
    return Pair(physics.F0_LINK)
