import numpy as np
import random


class Ant:

    FIDELITY_MIN = 247  # phi_low
    FIDELITY_DELTA = 0  # delta phi

    PHEROMONE_DEPOSITION = 8  # tau
    PHEROMONE_SATURATION = 0  # C_s

    TURNING_KERNEL_RAW = np.array([0.36, 0.047, 0.008, 0.004])
    TURNING_KERNEL = np.concatenate(
        (np.array([1 - sum(TURNING_KERNEL_RAW)]), TURNING_KERNEL_RAW)
    )

    def __init__(self, position, heading):
        self.position: np.ndarray = position
        self.heading: Direction = heading

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
        if curr < self.PHEROMONE_SATURATION:
            thresh = (
                self.FIDELITY_DELTA / self.PHEROMONE_SATURATION
            ) * curr + self.FIDELITY_MIN
        else:
            thresh = self.FIDELITY_MIN + self.FIDELITY_DELTA
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
        steps = np.random.choice(len(self.TURNING_KERNEL), p=self.TURNING_KERNEL)
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

    @staticmethod
    def rotate(direction: np.ndarray, steps: int) -> np.ndarray:
        """
        Rotates by 45 degrees * steps
        """
        for idx, d in enumerate(Direction.ALL):
            if np.array_equal(d, direction):
                return Direction.ALL[(idx + steps) % 8]
