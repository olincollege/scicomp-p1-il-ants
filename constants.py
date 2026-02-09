import numpy as np
from dataclasses import dataclass


@dataclass
class SimulationConstants:
    fidelity_min: float  # phi_low
    fidelity_delta: float  # delta phi
    pheromone_deposition: float  # tau
    pheromone_saturation: float  # C_s
    turning_kernel: np.ndarray


DEFAULT_KERNEL = np.array([0.581, 0.36, 0.047, 0.008, 0.004])
NARROW_KERNEL = np.array([0.822, 0.135, 0.031, 0.008, 0.004])

FIG_3A = SimulationConstants(
    fidelity_min=255,
    fidelity_delta=0,
    pheromone_deposition=8,
    pheromone_saturation=0,
    turning_kernel=DEFAULT_KERNEL,
)

FIG_3B = SimulationConstants(
    fidelity_min=251,
    fidelity_delta=0,
    pheromone_deposition=8,
    pheromone_saturation=0,
    turning_kernel=DEFAULT_KERNEL,
)

FIG_3C = SimulationConstants(
    fidelity_min=247,
    fidelity_delta=0,
    pheromone_deposition=8,
    pheromone_saturation=0,
    turning_kernel=DEFAULT_KERNEL,
)

FIG_4A = SimulationConstants(
    fidelity_min=247,
    fidelity_delta=0,
    pheromone_deposition=12,
    pheromone_saturation=0,
    turning_kernel=DEFAULT_KERNEL,
)

FIG_4B = SimulationConstants(
    fidelity_min=247,
    fidelity_delta=0,
    pheromone_deposition=8,
    pheromone_saturation=0,
    turning_kernel=DEFAULT_KERNEL,
)

FIG_4C = SimulationConstants(
    fidelity_min=247,
    fidelity_delta=0,
    pheromone_deposition=4,
    pheromone_saturation=0,
    turning_kernel=DEFAULT_KERNEL,
)

FIG_5A = SimulationConstants(
    fidelity_min=255,
    fidelity_delta=0,
    pheromone_deposition=8,
    pheromone_saturation=0,
    turning_kernel=NARROW_KERNEL,
)

FIG_5B = SimulationConstants(
    fidelity_min=251,
    fidelity_delta=0,
    pheromone_deposition=8,
    pheromone_saturation=0,
    turning_kernel=NARROW_KERNEL,
)

FIG_5C = SimulationConstants(
    fidelity_min=247,
    fidelity_delta=0,
    pheromone_deposition=8,
    pheromone_saturation=0,
    turning_kernel=NARROW_KERNEL,
)

FIG_6A = SimulationConstants(
    fidelity_min=20,
    fidelity_delta=235,
    pheromone_deposition=6,
    pheromone_saturation=6,
    turning_kernel=DEFAULT_KERNEL,
)

FIG_6B = SimulationConstants(
    fidelity_min=20,
    fidelity_delta=235,
    pheromone_deposition=6,
    pheromone_saturation=18,
    turning_kernel=DEFAULT_KERNEL,
)
