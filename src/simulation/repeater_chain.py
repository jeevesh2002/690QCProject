"""Implements an end‑to‑end entanglement generation run"""
import random
import simpy
from protocols import generation, purification, swapping, filtering
from configs import physics

def generate_end_to_end(env, path_links, strategy, protocol, rounds, filter_threshold):
    """Return (success_time, final_fidelity, raw_pairs_used)."

    The coroutine keeps attempting link‑level generation in parallel
    until an end‑to‑end Bell pair is delivered.
    """
    raw_pairs = 0
    # Containers for current link pairs (None until successful)
    link_pairs = {link: None for link in path_links}

    while True:
        # 1) Attempt generation in *parallel* on all unfinished links
        for link in path_links:
            if link_pairs[link] is None:
                pair = generation.try_generate(env, link)
                raw_pairs += 1
                if pair:
                    link_pairs[link] = pair

        # 2) If every hop has at least one pair, optionally purify
        if all(link_pairs.values()):
            for link in path_links:
                pair = link_pairs[link]
                F = pair.fidelity
                # multiple purification rounds possible
                for _ in range(rounds):
                    F_new, p_succ = (purification.dejmps if protocol=='dejmps'
                                     else purification.bbpssw)(F)
                    # acceptance test
                    if random.random() < p_succ:
                        F = F_new
                    else:
                        # purification failed; discard pair and start over for this link
                        link_pairs[link] = None
                        break
                else:
                    # optional filtering
                    if not filtering.apply_filter(F, filter_threshold):
                        link_pairs[link] = None
                        continue
                    link_pairs[link].fidelity = F   # update fidelity

            if not all(link_pairs.values()):
                continue  # some purification/filter failed; keep loop

            # 3) Perform swapping along the path
            fidelities = [link_pairs[link].fidelity for link in path_links]
            F_end = fidelities[0]
            for F_next in fidelities[1:]:
                F_end = swapping.swap(F_end, F_next)
            return env.now, F_end, raw_pairs

        # Advance time by a small step to avoid busy‑wait
        yield env.timeout(1e-6)
