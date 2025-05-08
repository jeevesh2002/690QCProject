"""Create topologies and initialise memory registers."""
from network.node import Node
from network.link import FibreLink

def build(env, topo: str, n_nodes: int, link_length_km: float):
    if topo == 'chain':
        topo = 'linear'
    nodes = [Node(env, chr(65+i)) for i in range(n_nodes)]
    links = []
    if topo == 'linear':
        links.extend(FibreLink(env, nodes[i], nodes[i+1], link_length_km)
                     for i in range(n_nodes-1))
    elif topo == 'ring':
        links.extend(FibreLink(env, nodes[i], nodes[(i+1)%n_nodes], link_length_km)
                     for i in range(n_nodes))
    elif topo == 'star':
        hub = nodes[0]
        links.extend(FibreLink(env, hub, nodes[i], link_length_km)
                     for i in range(1, n_nodes))
    else:
        raise ValueError(topo)
    return nodes, links
