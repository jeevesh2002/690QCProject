"""Run multiple Monte‑Carlo repetitions and dump JSON summary."""
from __future__ import annotations
import json, time, statistics, inspect
import simpy
from configs import physics as phys
from simulation.repeater_chain import generate_end_to_end
from network import topology

# ---------- adaptive helpers ------------------------------------------------
def _call_build(env, params):
    sig = inspect.signature(topology.build)
    if len(sig.parameters) == 2:                 # (env, params)
        return topology.build(env, params)
    if len(sig.parameters) == 4:                 # (env, topo, n_nodes, link_len)
        return topology.build(env, params['topology'], params['nodes'], params['link_length'])
    # kwargs fallback
    kw = {}
    if 'topology_type' in sig.parameters:
        kw['topology_type'] = params['topology']
    if 'n_nodes' in sig.parameters:
        kw['n_nodes'] = params['nodes']
    if 'link_length_km' in sig.parameters:
        kw['link_length_km'] = params['link_length']
    return topology.build(env, **kw)

def _default_path(links, topo):
    if topo in ('linear', 'chain'):
        return links
    if topo == 'ring':
        return links[:-1]
    if topo == 'star':
        return [links[0], links[-1]]
    raise ValueError(topo)

def _get_path(links, params):
    if hasattr(topology, 'get_path'):
        try:
            return topology.get_path(links, params.get('topology'))
        except TypeError:
            return topology.get_path(links)
    return _default_path(links, params['topology'])

# ---------- main API --------------------------------------------------------
def run(params: dict, *, collect: bool = False):
    """Run Monte‑Carlo repetitions; print or return summary."""
    # Update mutable physics
    if params.get('coherence_time'):
        phys.physics.DEFAULT_COHERENCE_TIME_S = params['coherence_time']
    if params.get('att_len'):
        phys.physics.ATTENUATION_LENGTH_KM = params['att_len']

    per = []
    for _ in range(params['runs']):
        env = simpy.Environment()
        nodes, links = _call_build(env, params)
        path = _get_path(links, params)
        proc = env.process(generate_end_to_end(
            env, path,
            rounds=params['rounds'],
            filter_threshold=params['filter_threshold'],
            strategy=params['strategy'],
            protocol=params['protocol'],
        ))
        env.run()
        t, F, raw = proc.value
        per.append({'latency_s': t, 'fidelity': F, 'raw': raw})

    summary = {
        **params,
        'latency_mean': statistics.mean(x['latency_s'] for x in per),
        'fidelity_mean': statistics.mean(x['fidelity'] for x in per),
        'raw_mean': statistics.mean(x['raw'] for x in per),
        'timestamp': time.time(),
    }
    if collect:
        return summary
    print(json.dumps(summary))
