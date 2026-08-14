import math
import unittest

from network.memory import QuantumMemory
from protocols.purification import dejmps, get_scheme
from protocols.swapping import swap


class _Environment:
    def __init__(self) -> None:
        self.now = 0.0


class QuantumCoreTests(unittest.TestCase):
    def test_memory_fidelity_decays_from_last_reset(self) -> None:
        environment = _Environment()
        memory = QuantumMemory(environment, fidelity=0.8)
        memory.reset(0.8)

        environment.now = 1.0

        self.assertAlmostEqual(memory.fidelity(), 0.8 / math.e)

    def test_dejmps_improves_a_high_fidelity_pair(self) -> None:
        purified, success_probability = dejmps(0.9)

        self.assertGreater(purified, 0.9)
        self.assertGreater(success_probability, 0.0)
        self.assertLessEqual(success_probability, 1.0)

    def test_scheme_alias_and_perfect_swap(self) -> None:
        self.assertIs(get_scheme("d"), dejmps)
        self.assertEqual(swap(1.0, 1.0), 1.0)


if __name__ == "__main__":
    unittest.main()
