"""
Class for simulating a single ant, with helper Dirction class
"""

import numpy as np
import random
from constants import SimulationConstants


class Ant:
    """
    Class representing a single ant. Each hand has a position and heading,
    and moves based on pheromone trails as defined in the paper.
    """

    def __init__(
        self, position: np.ndarray, heading: "Direction", constants: SimulationConstants
    ):
        self.position: np.ndarray = position
        self.heading: Direction = heading
        self.constants: SimulationConstants = constants

    def move(self, world: np.ndarray) -> bool:
        """
        Updates heading and position according to trail following algorithm:
        1. Chance to lose trail fidelity and turn randomly based on kernel
        2. If forward cell has trail, go forward
        3. Follow stronger trail of left and right cells
        4. If tied, turn randomly based on kernel

        Args:
            world (np.ndarray): 2D array representing pheromone levels, passed from Simulation

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

    def fidelity_check(self, world: np.ndarray) -> bool:
        """
        Random chance to lose trail fidelity:
        - Pheromone level less than saturation: linear function from fidelity_min to fidelity_min + fidelity_delta
        - Pheromone level greater than saturation: fidelity_min + fidelity_delta

        Returns:
            bool: Representing if the ant loses the trail and turns randomly based on kernel
        """
        curr = world[self.position[1], self.position[0]]
        if curr < self.constants.pheromone_saturation:
            thresh = (
                self.constants.fidelity_delta / self.constants.pheromone_saturation
            ) * curr + self.constants.fidelity_min
        else:
            thresh = self.constants.fidelity_min + self.constants.fidelity_delta
        return np.random.randint(0, 256) >= thresh

    def turning_kernel(self) -> "Direction":
        """
        Weighted random turn based on turning kernel: [B0, B1, B2, B3, B4].
        - B0: chance to go straight
        - B1: chance to turn 45 degrees
        - B2: chance to turn 90 degrees, etc.
        After turn amount is determined, 50/50 to turn left or right.

        Returns:
            Direction: New heading after turn
        """
        kernel_normalized = self.constants.turning_kernel / np.sum(
            self.constants.turning_kernel
        )
        # Hardcoded 5, 0-4 are possible outputs
        steps = np.random.choice(5, p=kernel_normalized)
        dir = random.choice([-1, 1])
        return Direction.rotate(self.heading, dir * steps)

    def get_pheromone_value(
        self, world: np.ndarray, pos: np.ndarray, default: float = 0
    ) -> float:
        """
        Helper for getting pheromone value, returning default if out of bounds

        Args:
            world (np.ndarray): 2D array representing pheromone levels, passed from Simulation
            pos (np.ndarray): Coordinates to check pheromone level of
            default (float, optional): Value to return if pos is out of bounds. Defaults to 0.

        Returns:
            float: Pheromone value at pos, or default if out of bounds
        """
        x, y = pos
        if 0 <= x < world.shape[1] and 0 <= y < world.shape[0]:
            return world[y, x]
        return default


class Direction:
    """
    Class representing the 8 possible headings of an ant
    """

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
    def rotate(direction: "Direction", steps: int) -> "Direction":
        """
        Rotate a direction by a given number of steps (45 degrees per step)

        Args:
            direction (Direction): Current heading to rotate
            steps (int): Number of 45-degree steps to rotate, positive rotates
                clockwise, negative rotates counterclockwise

        Returns:
            Direction: New heading after rotation
        """
        idx = Direction.INDEX_MAP[tuple(direction)]
        return Direction.ALL[(idx + steps) % 8]
