"""Generate end-to-end entanglement over a chain with dynamic memories."""
from __future__ import annotations
import simpy, logging, random
from typing import List
from protocols import generation, swapping, filtering
from protocols.purification import get_scheme

logger = logging.getLogger(__name__)

def _purify_pair(env, qa, qb, qaux_a, qaux_b, purify_fn):
    """Attempts to purify a pair of quantum memories using auxiliary qubits and a purification function.

    This function computes the average fidelity, applies the purification function, and updates the memories if successful.

    Args:
        env: The simulation environment.
        qa: The first quantum memory to purify.
        qb: The second quantum memory to purify.
        qaux_a: Auxiliary quantum memory for the first node.
        qaux_b: Auxiliary quantum memory for the second node.
        purify_fn: The purification function to apply.

    Returns:
        A tuple (success, new_fidelity) where success is True if purification succeeded, and new_fidelity is the resulting fidelity or None if failed.
    """
    F_in  = qa.fidelity()
    F_aux = qaux_a.fidelity()
    F_avg = (F_in + F_aux) / 2        # simplest symmetric choice
    F_new, Psucc = purify_fn(F_avg)
    if random.random() > Psucc:
        return False, None
    qa.reset(F_new)
    qb.reset(F_new)
    return True, F_new

def _purify_link(env, link, rounds: int, purify_fn):
    """Purifies the first pair in link memories up to a specified number of rounds.

    This function attempts to purify the first entangled pair in the link's memory for a given number of rounds using the provided purification function.

    Args:
        env: The simulation environment.
        link: The link whose memories are to be purified.
        rounds: The number of purification rounds to attempt.
        purify_fn: The purification function to use.

    Returns:
        True if purification succeeds for all rounds, False otherwise.
    """
    a, b = link.a, link.b
    for _ in range(rounds):
        if len(a.memory[b]) < 2 or len(b.memory[a]) < 2:
            return False
        qa, qaux_a = a.pop_memory_qubits(b, 1)[0], a.pop_memory_qubits(b,1)[0]
        qb, qaux_b = b.pop_memory_qubits(a, 1)[0], b.pop_memory_qubits(a,1)[0]
        ok, Fnew = _purify_pair(env, qa, qb, qaux_a, qaux_b, purify_fn)
        if not ok:
            # discard all four qubits
            return False
        # put survivor back to head of list
        a.memory[b].insert(0, qa)
        b.memory[a].insert(0, qb)
    return True

def generate_end_to_end(
    env: simpy.Environment,
    path_links: List,
    *,
    rounds: int = 1,
    filter_threshold: float = 0.9,
    strategy: str = "purify_then_swap",
    protocol: str = "dejmps",
    max_trials: int = 5000,
    echo_every: int = 100,
):
    """Generates end-to-end entanglement over a chain of links with dynamic memories.

    This function orchestrates entanglement generation, purification, swapping, and filtering across a chain of links, returning performance metrics upon success.

    Args:
        env: The simulation environment.
        path_links: List of links forming the entanglement path.
        rounds: Number of purification or swap rounds to perform.
        filter_threshold: Minimum fidelity required to accept the final pair.
        strategy: The entanglement strategy to use ('purify_then_swap' or 'swap_then_purify').
        protocol: The purification protocol to use.
        max_trials: Maximum number of entanglement generation trials.
        echo_every: Frequency of logging progress.

    Returns:
        A tuple (latency, F_end, raw_pairs, rate_pair, rate_norm) with performance metrics.

    Raises:
        RuntimeError: If the maximum number of trials is exceeded.
    """
    purify_fn = get_scheme(protocol)
    trials = 0
    raw_pairs = 0

    while True:
        trials += 1
        if trials % echo_every == 0:
            logger.info("[%7.3f s] trials=%d raw=%d", env.now, trials, raw_pairs)
        if trials > max_trials:
            raise RuntimeError("Exceeded max trials")

        needed = rounds + 1
        # ---------- ensure each link has needed pairs ----------
        gen_processes = []
        for link in path_links:
            # topological symmetry -> check one side
            missing = needed - len(link.a.memory[link.b])
            for _ in range(missing):
                gen_processes.append(env.process(generation.try_generate(env, link)))
                raw_pairs += 1
        if gen_processes:
            yield simpy.events.AllOf(env, gen_processes)
        # verify
        if any(len(l.a.memory[l.b]) < needed for l in path_links):
            continue

        # ---------- optional hop purification ----------
        if strategy == "purify_then_swap":
            if not all(_purify_link(env, link, rounds, purify_fn) for link in path_links):
                continue

        # ---------- sequential swaps ----------
        fidelities = [link.a.peek_memory_fidelity(link.b) for link in path_links]
        F_end = fidelities[0]
        for F_next in fidelities[1:]:
            F_end = swapping.swap(F_end, F_next)
        # remove first pair memories
        for link in path_links:
            link.a.pop_memory_qubits(link.b, 1)
            link.b.pop_memory_qubits(link.a, 1)

        # ---------- swap‑then‑purify additional rounds ----------
        if strategy == "swap_then_purify":
            # accumulate extra end‑to‑end pairs
            end_pairs = [F_end]
            while len(end_pairs) < rounds + 1:
                # need new set of link pairs, then swaps
                gen_processes = []
                for link in path_links:
                    gen_processes.append(env.process(generation.try_generate(env, link)))
                    raw_pairs += 1
                yield simpy.events.AllOf(env, gen_processes)
                if any(len(l.a.memory[l.b]) < 1 for l in path_links):
                    continue
                fidelities = [link.a.peek_memory_fidelity(link.b) for link in path_links]
                F_curr = fidelities[0]
                for F_next in fidelities[1:]:
                    F_curr = swapping.swap(F_curr, F_next)
                end_pairs.append(F_curr)
                for link in path_links:
                    link.a.pop_memory_qubits(link.b,1)
                    link.b.pop_memory_qubits(link.a,1)
            # purification on end pairs
            survivor_F = end_pairs[0]
            for aux_F in end_pairs[1:]:
                F_avg = (survivor_F + aux_F)/2
                survivor_F, Psucc = purify_fn(F_avg)
                if random.random() > Psucc:
                    survivor_F = None
                    break
            if survivor_F is None:
                continue
            F_end = survivor_F

        # ---------- filter ----------
        if not filtering.apply_filter(F_end, filter_threshold):
            continue

        latency = env.now
        rate_pair = 1/latency
        rate_norm = raw_pairs/latency
        return latency, F_end, raw_pairs, rate_pair, rate_norm
