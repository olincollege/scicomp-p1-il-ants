import numpy as np
import random

from ant import Ant, Direction


class Simulation:
    def __init__(
        self,
        world_size=(256, 256),
        spawn_point=(128, 128),
        seed=None,
    ):
        self.world = np.zeros(world_size)
        self.ants = []
        self.spawn_point = np.array(spawn_point)

        self.spawn_directions = [
            Direction.UP_RIGHT,
            Direction.DOWN_RIGHT,
            Direction.DOWN_LEFT,
            Direction.UP_LEFT,
        ]

        if seed is not None:
            np.random.seed(seed)
            random.seed(seed)

    def step(self):
        # SPAWN
        self.ants.append(
            Ant(
                self.spawn_point.copy(),
                random.choice(self.spawn_directions),
            )
        )

        # UPDATE
        for ant in self.ants.copy():
            # DEPOSIT
            self.world[ant.position[1], ant.position[0]] += Ant.PHEROMONE_DEPOSITION

            # MOVE
            if not ant.move(self.world):
                # remove if out of bounds
                self.ants.remove(ant)

        # EVAPORATE
        self.world = np.maximum(self.world - 1, 0)
