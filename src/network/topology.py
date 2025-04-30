"""Helpers to build network graphs."""
from network.node import Node
from network.link import FibreLink

def build(env, topo, n_nodes, link_length_km):
    """Return (nodes: list[Node], links: list[FibreLink])"""
    if topo == 'chain':
        topo = 'linear'
    nodes = [Node(env, chr(65+i)) for i in range(n_nodes)]
    links = []
    if topo == 'linear':
        links.extend(
            FibreLink(env, nodes[i], nodes[i + 1], link_length_km)
            for i in range(n_nodes - 1)
        )
    elif topo == 'ring':
        links.extend(
            FibreLink(env, nodes[i], nodes[(i + 1) % n_nodes], link_length_km)
            for i in range(n_nodes)
        )
    elif topo == 'star':
        hub = nodes[0]
        links.extend(
            FibreLink(env, hub, nodes[i], link_length_km)
            for i in range(1, n_nodes)
        )
    else:
        raise ValueError(f"Unknown topology {topo}")
    return nodes, links

def get_path(links, topo, *, n_nodes=None):
    """
    Return an *ordered list of FibreLink* objects that connect Alice (node 0)
    to Bob (node N-1).  Works for the three built-in topologies.
    """
    if topo in ["linear", "chain"]:
        # links were created in order (0-1, 1-2, …) so they already form the path
        return links

    if topo == "ring":
        # choose clockwise path from node 0 to node N-1
        # links are [0-1, 1-2, …, N-2-(N-1), (N-1)-0]
        # → drop the last link to avoid going the long way round
        return links[:-1]

    if topo == "star":
        # path is (0 ↔ hub ↔ N-1) =>  two links: (0-hub) and (hub-N-1)
        # our construction put node 0 as hub, so links[0] is 0-1, links[-1] is 0-(N-1)
        return [links[0], links[-1]]

    raise ValueError(f"Unknown topology {topo}")