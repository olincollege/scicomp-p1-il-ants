import numpy as np
import pygame
import random
import time


class Ant:

    FIDELITY_MIN = 255  # phi_low
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

    def get_or_default(
        self, world: np.ndarray, pos: tuple, default: float = 0
    ) -> float:
        """
        Helper for getting world value with boundary check
        """
        x, y = pos
        if 0 <= x < world.shape[1] and 0 <= y < world.shape[0]:
            return world[y, x]
        return default

    def move(self, world: np.ndarray) -> bool:
        """
        Updates heading and position according to trail following algorithm.

        Returns:
            bool: Representing if the ant is still inside the world
        """

        # pad world to avoid boundary checks
        left_dir: np.ndarray = Direction.rotate(self.heading, 1)
        right_dir: np.ndarray = Direction.rotate(self.heading, -1)

        fwd = self.get_or_default(world, tuple(self.position + self.heading), 0)
        left = self.get_or_default(world, tuple(self.position + left_dir), 0)
        right = self.get_or_default(world, tuple(self.position + right_dir), 0)

        # CHANCE TO LOSE TRAIL AND KERNEL
        if np.random.randint(0, 256) >= self.FIDELITY_MIN:
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


class App:
    def __init__(self, world, ants):
        self.world = world
        self.ants = ants
        self._running = True
        self._display_surf = None
        self.scale = 3
        self.width = self.height = 256 * self.scale
        self.size = self.width, self.height

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size, pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self._running = True

        self.surface = pygame.Surface((256, 256))
        for y in range(256):
            for x in range(256):
                v = 255 - np.clip(self.world[y, x] * 10, 0, 255)
                self.surface.set_at((x, y), (v, v, v))

        for ant in self.ants:
            self.surface.set_at((ant.position[0], ant.position[1]), (255, 0, 0))

        self.surface = pygame.transform.scale(self.surface, (self.width, self.height))

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self._display_surf.blit(self.surface, (0, 0))
        pygame.display.flip()

    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        self.on_init()
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
        self.on_cleanup()


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


SPAWN_POINT = np.array([128, 128])


if __name__ == "__main__":
    start = time.time()
    random.seed(42)
    np.random.seed(42)
    world = np.zeros((256, 256))
    ants = []

    for t in range(800):
        # SPAWN
        ants.append(
            Ant(
                position=SPAWN_POINT.copy(),
                heading=random.choice(
                    [
                        Direction.UP_RIGHT,
                        Direction.DOWN_RIGHT,
                        Direction.DOWN_LEFT,
                        Direction.UP_LEFT,
                    ]
                ),
            )
        )

        for ant in ants.copy():
            # DEPOSIT
            world[ant.position[1], ant.position[0]] += Ant.PHEROMONE_DEPOSITION

            # MOVE
            if not ant.move(world):
                # remove if out of bounds
                ants.remove(ant)

        # EVAPORATE
        world = np.maximum(world - 1, 0)

    end = time.time()

    print(f"Simulation time: {end - start:.2f} s")
    print("Num remaining ants:", len(ants))

    theApp = App(world, ants)
    theApp.on_execute()
