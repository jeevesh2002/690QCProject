"""Mutable physical constants for sweepable simulations."""
from dataclasses import dataclass

@dataclass
class PhysicsConfig:
    SPEED_OF_LIGHT_FIBER: float = 2e8          # m/s  (≈5 µs per km RTT)
    ATTENUATION_LENGTH_KM: float = 22          # Beer–Lambert attenuation length
    F0_LINK: float = 0.9                      # Baseline fidelity for a fresh link
    DEFAULT_COHERENCE_TIME_S: float = 1.0      # Quantum-memory coherence time
    DETECTION_EFFICIENCY: float = 0.9          # Detector efficiency for single‑click

# Singleton instance that simulation modules may mutate at runtime
physics = PhysicsConfig()

# --- Back‑compatibility re‑exports -----------------------------------
SPEED_OF_LIGHT_FIBER     = physics.SPEED_OF_LIGHT_FIBER
ATTENUATION_LENGTH_KM    = physics.ATTENUATION_LENGTH_KM
F0_LINK                  = physics.F0_LINK
DEFAULT_COHERENCE_TIME_S = physics.DEFAULT_COHERENCE_TIME_S
DETECTION_EFFICIENCY     = physics.DETECTION_EFFICIENCY
