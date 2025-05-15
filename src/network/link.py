"""Bidirectional fibre link with one communication qubit per side."""
import math
from configs import physics

class FibreLink:
    """Represents a bidirectional fiber link with one communication qubit per side.

    This class models the connectivity and physical properties of a fiber link between two nodes in a quantum network.
    """
    def __init__(self, env, node_a, node_b, length_km: float, *, attenuation_length_km: float | None = None):
        """Initializes a FibreLink instance with the given nodes and physical parameters.

        Sets up the link between two nodes, calculating the attenuation and success probability based on the provided or default parameters.

        Args:
            env: The simulation environment.
            node_a: The first node connected by the link.
            node_b: The second node connected by the link.
            length_km: The length of the fiber link in kilometers.
            attenuation_length_km: Optional custom attenuation length in kilometers.
        """
        self.env = env
        self.a = node_a
        self.b = node_b
        self.length_km = length_km
        self._att_len = attenuation_length_km or physics.physics.ATTENUATION_LENGTH_KM
        self.success_prob = math.exp(-length_km / self._att_len)

    # convenience for protocols ----------------
    def other(self, node):
        """Returns the node on the opposite end of the link from the given node.

        This method helps identify the other node connected by the fiber link.

        Args:
            node: One of the nodes connected by the link.

        Returns:
            The node on the opposite end of the link.
        """
        return self.b if node is self.a else self.a

    def __repr__(self):
        """Returns a string representation of the FibreLink instance.

        Provides a concise summary of the link's endpoints and length for debugging and logging purposes.

        Returns:
            A string describing the link's endpoints and length.
        """
        return f"Link({self.a.name}-{self.b.name},{self.length_km}km)"
