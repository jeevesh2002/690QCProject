"""Heralded single‑click generation helper."""

import random
from network.pair import EntangledPair
from configs import physics

def try_generate(env, link):
    """Attempt single‑click generation on *link*; yields EntangledPair or None."""
    success, latency = link.attempt_single_click()
    env.timeout(latency)          # advance simulation clock
    if not success:
        return None
    # ideal Bell‑pair with baseline fidelity F0 decayed by propagation time
    fidelity = physics.F0_LINK    # losses already reflected in success_prob
    return EntangledPair(link.a.name, link.b.name, fidelity, env.now)
