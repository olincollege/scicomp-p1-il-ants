import numpy as np
import random
from constants import SimulationConstants


class Ant:

    def __init__(self, position, heading, constants: SimulationConstants):
        self.position: np.ndarray = position
        self.heading: Direction = heading
        self.constants = constants

    def get_pheromone_value(
        self, world: np.ndarray, pos: np.ndarray, default: float = 0
    ) -> float:
        """
        Helper for getting world value with boundary check
        """
        x, y = pos
        if 0 <= x < world.shape[1] and 0 <= y < world.shape[0]:
            return world[y, x]
        return default

    def fidelity_check(self, world: np.ndarray) -> bool:
        """
        Returns bool representing whether the ant loses trail fidelity
        """
        curr = world[self.position[1], self.position[0]]
        if curr < self.constants.pheromone_saturation:
            thresh = (
                self.constants.fidelity_delta / self.constants.pheromone_saturation
            ) * curr + self.constants.fidelity_min
        else:
            thresh = self.constants.fidelity_min + self.constants.fidelity_delta
        return np.random.randint(0, 256) >= thresh

    def move(self, world: np.ndarray) -> bool:
        """
        Updates heading and position according to trail following algorithm.

        Returns:
            bool: Representing if the ant is still inside the world
        """
        left_dir: np.ndarray = Direction.rotate(self.heading, 1)
        right_dir: np.ndarray = Direction.rotate(self.heading, -1)

        fwd = self.get_pheromone_value(world, self.position + self.heading)
        left = self.get_pheromone_value(world, self.position + left_dir, 0)
        right = self.get_pheromone_value(world, self.position + right_dir, 0)

        # CHANCE TO LOSE TRAIL AND KERNEL
        if self.fidelity_check(world):
            self.heading = self.turning_kernel()
        # GO FORWARD IF TRAIL
        elif fwd > 0:
            # heading unchanged
            pass
        # FOLLOW STRONGER FORK
        elif left > right:
            self.heading = left_dir
        elif right > left:
            self.heading = right_dir
        # RANDOM IF FORKS TIED
        else:
            self.heading = self.turning_kernel()

        # MOVE
        self.position += self.heading

        if (
            self.position[0] <= 0
            or self.position[1] <= 0
            or self.position[0] >= world.shape[1]
            or self.position[1] >= world.shape[0]
        ):
            return False

        return True

    def turning_kernel(self):
        """
        Returns new heading
        """
        kernel_normalized = self.constants.turning_kernel / np.sum(
            self.constants.turning_kernel
        )
        # Hardcoded 5, 0-4 are possible outputs
        steps = np.random.choice(5, p=kernel_normalized)
        dir = random.choice([-1, 1])
        return Direction.rotate(self.heading, dir * steps)


class Direction:
    UP = np.array([0, -1])
    UP_RIGHT = np.array([1, -1])
    RIGHT = np.array([1, 0])
    DOWN_RIGHT = np.array([1, 1])
    DOWN = np.array([0, 1])
    DOWN_LEFT = np.array([-1, 1])
    LEFT = np.array([-1, 0])
    UP_LEFT = np.array([-1, -1])

    ALL = [UP, UP_RIGHT, RIGHT, DOWN_RIGHT, DOWN, DOWN_LEFT, LEFT, UP_LEFT]

    # Precompute rotation map
    INDEX_MAP = {tuple(d): i for i, d in enumerate(ALL)}

    @staticmethod
    def rotate(direction: np.ndarray, steps: int) -> np.ndarray:
        """
        Rotates by 45 degrees * steps
        """
        idx = Direction.INDEX_MAP[tuple(direction)]
        return Direction.ALL[(idx + steps) % 8]
