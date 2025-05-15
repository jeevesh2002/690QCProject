"""Create topologies and initialise memory registers."""
from network.node import Node
from network.link import FibreLink

def build(env, topo: str, n_nodes: int, link_length_km: float):
    """Builds a network topology and initializes memory registers for each node.

    This function creates nodes and links according to the specified topology type, number of nodes, and link length.

    Args:
        env: The simulation environment.
        topo: The topology type ('linear', 'chain', 'ring', or 'star').
        n_nodes: The number of nodes in the network.
        link_length_km: The length of each link in kilometers.

    Returns:
        A tuple containing the list of nodes and the list of links.

    Raises:
        ValueError: If the topology type is not recognized.
    """
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
