class Node:
    """Network vertex holding a memory register for every incident edge."""
    def __init__(self, env, name):
        self.env = env
        self.name = name
        self.memories = {}  # neighbour -> MemoryRegister

    def add_memory(self, neighbour, mem):
        self.memories[neighbour] = mem

    def memory(self, neighbour):
        return self.memories[neighbour]

    def __repr__(self):
        return f"Node({self.name})"
