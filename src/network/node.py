"""Network node managing communication interfaces and dynamic memory lists."""
from collections import defaultdict
import logging
from network.memory import QuantumMemory
from configs import physics

logger = logging.getLogger(__name__)

class Node:
    def __init__(self, env, name: str):
        self.env = env
        self.name = name
        # neighbor -> list[QuantumMemory]
        self.memory = defaultdict(list)
        # communication qubit state: neighbor -> bool (busy)
        self.comm_busy = defaultdict(bool)

    # communication qubit reservation
    def set_comm_busy(self, neighbor, busy: bool):
        self.comm_busy[neighbor] = busy

    def comm_available(self, neighbor):
        return not self.comm_busy[neighbor]

    # memory operations
    def add_memory_qubit(self, neighbor, fidelity: float):
        qmem = QuantumMemory(self.env, fidelity)
        qmem.reset(fidelity)
        self.memory[neighbor].append(qmem)
        logger.debug("%7.3f s  %s stores qubit with %s (F=%.3f)",
                     self.env.now, self, neighbor, fidelity)
        return qmem

    def pop_memory_qubits(self, neighbor, n: int):
        if len(self.memory[neighbor]) < n:
            raise RuntimeError(f"Node {self} has only {len(self.memory[neighbor])} qubits with {neighbor}")
        qubits = [self.memory[neighbor].pop(0) for _ in range(n)]
        return qubits

    def peek_memory_fidelity(self, neighbor):
        if not self.memory[neighbor]:
            raise RuntimeError(f"Node {self} has no memory with {neighbor}")
        return self.memory[neighbor][0].fidelity()

    def __repr__(self):
        return f"Node({self.name})"
