"""Network node managing communication interfaces and dynamic memory lists."""
from collections import defaultdict
import logging
from network.memory import QuantumMemory
from configs import physics

logger = logging.getLogger(__name__)

class Node:
    """Represents a network node managing communication interfaces and quantum memory.

    This class handles communication qubit reservation, dynamic memory management, and provides methods for interacting with neighboring nodes.
    """
    def __init__(self, env, name: str):
        self.env = env
        self.name = name
        # neighbor -> list[QuantumMemory]
        self.memory = defaultdict(list)
        # communication qubit state: neighbor -> bool (busy)
        self.comm_busy = defaultdict(bool)

    # communication qubit reservation
    def set_comm_busy(self, neighbor, busy: bool):
        """Sets the busy state of the communication qubit for a given neighbor.

        Args:
            neighbor: The neighboring node.
            busy: Boolean indicating if the communication qubit is busy.
        """
        self.comm_busy[neighbor] = busy

    def comm_available(self, neighbor):
        """Checks if the communication qubit for a neighbor is available.

        Args:
            neighbor: The neighboring node.

        Returns:
            True if the communication qubit is available, False otherwise.
        """
        return not self.comm_busy[neighbor]

    # memory operations
    def add_memory_qubit(self, neighbor, fidelity: float):
        """Adds a new quantum memory qubit entangled with a neighbor.

        Args:
            neighbor: The neighboring node.
            fidelity: The initial fidelity of the new memory qubit.

        Returns:
            The created QuantumMemory instance.
        """
        qmem = QuantumMemory(self.env, fidelity)
        qmem.reset(fidelity)
        self.memory[neighbor].append(qmem)
        logger.debug("%7.3f s  %s stores qubit with %s (F=%.3f)",
                     self.env.now, self, neighbor, fidelity)
        return qmem

    def pop_memory_qubits(self, neighbor, n: int):
        """Removes and returns a specified number of memory qubits for a neighbor.

        Args:
            neighbor: The neighboring node.
            n: The number of qubits to remove.

        Returns:
            A list of QuantumMemory instances.

        Raises:
            RuntimeError: If there are not enough memory qubits for the neighbor.
        """
        if len(self.memory[neighbor]) < n:
            raise RuntimeError(f"Node {self} has only {len(self.memory[neighbor])} qubits with {neighbor}")
        qubits = [self.memory[neighbor].pop(0) for _ in range(n)]
        return qubits

    def peek_memory_fidelity(self, neighbor):
        """Returns the fidelity of the first memory qubit for a neighbor.

        Args:
            neighbor: The neighboring node.

        Returns:
            The fidelity of the first memory qubit as a float.

        Raises:
            RuntimeError: If there is no memory qubit for the neighbor.
        """
        if not self.memory[neighbor]:
            raise RuntimeError(f"Node {self} has no memory with {neighbor}")
        return self.memory[neighbor][0].fidelity()

    def __repr__(self):
        """Returns a string representation of the Node instance.

        Returns:
            A string with the node's name.
        """
        return f"Node({self.name})"
