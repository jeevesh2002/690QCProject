"""Generate an end‑to‑end Bell pair over a chain using various strategies.
"""
from __future__ import annotations
import random
from typing import List
import simpy
from protocols import swapping, filtering, generation
from protocols.purification import get_scheme


def _purify_many(F: float, rounds: int, purify_fn):
    """Run <=rounds purification rounds; return (F', success?)."""
    for _ in range(rounds):
        F_new, p = purify_fn(F)
        if random.random() > p:           # purification failed
            return F, False
        F = F_new
    return F, True


def generate_end_to_end(
    env: simpy.Environment,
    path_links: List,
    *,
    rounds: int = 1,
    filter_threshold: float = 0.9,
    strategy: str = "purify_then_swap",
    protocol: str = "dejmps",
    max_trials: int = 50_000,          # stop-gap
    echo_every: int = 100,            # progress cadence
):
    """
    SimPy *process* that tries until an end-to-end Bell pair is produced.
    Raises RuntimeError if `max_trials` is exceeded.
    """
    purify = get_scheme(protocol)
    raw_pairs = 0
    trials = 0

    while True:
        trials += 1
        if trials % echo_every == 0:
            print(f"[{env.now:>8.3f} s]  trials={trials}  raw={raw_pairs}")

        if trials > max_trials:
            raise RuntimeError(
                f"Exceeded {max_trials} trials without success "
                f"(path length={len(path_links)}, link_len={path_links[0].length_km} km)."
            )

        # 1 ── attempt all hops in parallel
        events = {l: env.process(generation.try_generate(env, l)) for l in path_links}
        failure = False
        hop_F = {}

        for link, ev in events.items():
            pair = yield ev
            if pair is None:
                failure = True
            else:
                hop_F[link] = pair.fidelity

        if failure:
            continue  # at least one link failed

        raw_pairs += len(path_links)

        # 2 ── optional hop-wise purification
        if strategy == "purify_then_swap":
            for link, F in hop_F.items():
                F, ok = _purify_many(F, rounds, purify)
                if not ok:
                    failure = True
                    break
                hop_F[link] = F
            if failure:
                continue

        # 3 ── entanglement swapping
        fidelities = list(hop_F.values())
        F_end = fidelities[0]
        for F_next in fidelities[1:]:
            F_end = swapping.swap(F_end, F_next)

        # 4 ── if swap-then-purify: purify now
        if strategy == "swap_then_purify":
            F_end, ok = _purify_many(F_end, rounds, purify)
            if not ok or not filtering.apply_filter(F_end, filter_threshold):
                continue

        # ── success!
        return env.now, F_end, raw_pairs