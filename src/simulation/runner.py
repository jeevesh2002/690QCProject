"""Wrapper to run Monte‑Carlo repetitions and summarise statistics."""
from __future__ import annotations
import simpy, statistics, time, json, inspect
from typing import Dict, Any
from configs import physics as phys
from simulation.repeater_chain import generate_end_to_end
from network import topology

def _call_build(env, params):
    """Calls the topology build function with parameters extracted from a dictionary.

    This function constructs the network topology using the provided simulation environment and parameters.

    Args:
        env: The simulation environment.
        params: A dictionary containing topology, nodes, and link_length.

    Returns:
        The result of the topology.build function.
    """
    return topology.build(env, params['topology'], params['nodes'], params['link_length'])

def _get_path(links, topo):
    """Determines the path of links to use based on the network topology.

    This function selects the appropriate sequence of links for the given topology type.

    Args:
        links: The list of links in the network.
        topo: The topology type ('linear', 'chain', 'ring', or 'star').

    Returns:
        A list of links representing the path for the topology.

    Raises:
        ValueError: If the topology type is not recognized.
    """
    if topo in ('linear', 'chain'):
        return links
    if topo == 'ring':
        return links[:-1]
    if topo == 'star':
        return [links[0], links[-1]]
    raise ValueError(topo)

def run(params: Dict[str, Any], *, collect: bool = False):
    """Runs Monte-Carlo simulations and summarizes the resulting statistics.

    This function executes multiple simulation runs with the provided parameters, collects performance metrics, and either returns or prints a summary.

    Args:
        params: A dictionary of simulation parameters.
        collect: If True, returns the summary dictionary instead of printing.

    Returns:
        The summary dictionary if collect is True; otherwise, prints the summary.
    """
    # tune physics
    if 'coherence_time' in params:
        phys.physics.DEFAULT_COHERENCE_TIME_S = params['coherence_time']
    if 'att_len' in params:
        phys.physics.ATTENUATION_LENGTH_KM = params['att_len']

    per = []
    for _ in range(params['runs']):
        env = simpy.Environment()
        nodes, links = _call_build(env, params)
        path = _get_path(links, params['topology'])
        proc = env.process(generate_end_to_end(
            env, path,
            rounds=params['rounds'],
            filter_threshold=params['filter_threshold'],
            strategy=params['strategy'],
            protocol=params['protocol'],
            ))
        env.run()
        latency, F, raw, r_pair, r_norm = proc.value
        per.append({'latency_s': latency, 'fidelity': F,
                    'raw': raw, 'rate_pair': r_pair, 'rate_norm': r_norm})

    summary = {
        **params,
        'latency_mean': statistics.mean(x['latency_s'] for x in per),
        'fidelity_mean': statistics.mean(x['fidelity'] for x in per),
        'raw_mean': statistics.mean(x['raw'] for x in per),
        'rate_pair_mean': statistics.mean(x['rate_pair'] for x in per),
        'rate_norm_mean': statistics.mean(x['rate_norm'] for x in per),
        'timestamp': time.time(),
    }
    if collect:
        return summary
    print(json.dumps(summary, indent=2))
