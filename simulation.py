import numpy as np
import random
from dataclasses import dataclass

from ant import Ant, Direction
from constants import SimulationConstants


@dataclass
class State:
    world: np.ndarray
    ants: list[Ant]


class Simulation:
    SPAWN_DIRECTIONS = [
        Direction.UP_RIGHT,
        Direction.DOWN_RIGHT,
        Direction.DOWN_LEFT,
        Direction.UP_LEFT,
    ]

    def __init__(
        self,
        constants: SimulationConstants,
        world_size=(256, 256),
        spawn_point=(128, 128),
        seed=None,
    ):
        self.constants = constants
        self.world: np.ndarray = np.zeros(world_size)
        self.ants: list[Ant] = []
        self.spawn_point: np.ndarray = np.array(spawn_point)
        self.seed = seed

        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

        self.state_history: list[State] = []
        self.cache_state()
        self.time_step = 0

    def reset(self):
        self.world: np.ndarray = np.zeros((256, 256))
        self.ants: list[Ant] = []
        self.state_history: list[State] = []
        if self.seed is not None:
            np.random.seed(self.seed)
            random.seed(self.seed)
        self.cache_state()
        self.time_step = 0

    def cache_state(self):
        """
        Caches current state as a State object
        """
        self.state_history.append(
            State(
                world=self.world.copy(),
                ants=[
                    Ant(ant.position.copy(), ant.heading.copy(), ant.constants)
                    for ant in self.ants
                ],
            )
        )

    def load_state(self, time_step) -> bool:
        """
        Loads cached state at given time step. If time step is out of bounds, does nothing.

        Returns:
            bool: If state was loaded
        """
        if time_step < 0 or time_step >= len(self.state_history):
            return False

        self.time_step = time_step
        state = self.state_history[time_step]
        self.world = state.world.copy()
        self.ants = [
            Ant(ant.position.copy(), ant.heading.copy(), ant.constants)
            for ant in state.ants
        ]
        return True

    def step_backward(self):
        """
        Rollback simulation by one time step
        """
        self.load_state(self.time_step - 1)

    def step(self):
        """
        Advance simulation forward by one time step, attemps to load from
        cached states before simulating new state
        """
        # try to load cached state
        if self.load_state(self.time_step + 1):
            return

        # SPAWN
        self.ants.append(
            Ant(
                self.spawn_point.copy(),
                random.choice(self.SPAWN_DIRECTIONS),
                self.constants,
            )
        )

        ants_to_remove = []

        # UPDATE
        for ant in self.ants:
            # DEPOSIT
            self.world[
                ant.position[1], ant.position[0]
            ] += self.constants.pheromone_deposition

            # MOVE
            if not ant.move(self.world):
                # remove if out of bounds
                ants_to_remove.append(ant)

        for ant in ants_to_remove:
            self.ants.remove(ant)

        # EVAPORATE
        self.world = np.maximum(self.world - 1, 0)

        # CACHE STATE
        self.cache_state()
        self.time_step += 1
