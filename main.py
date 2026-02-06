import numpy as np
import pygame
import random
import time


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


class App:
    SCALE = 3

    def __init__(self, world, ants):
        self.world = world
        self.ants = ants
        self._running = True
        self._display_surf = None

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            (256 * self.SCALE, 256 * self.SCALE), pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self._display_surf.fill((255, 255, 255))

        self._running = True

        # Draw pheromone trails as circles
        self.draw_pheromones(self.world)

        # Draw ants as red circles
        self.draw_ants(self.ants)

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
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

    def draw_pheromones(self, world):
        for y in range(256):
            for x in range(256):
                v = world[y, x]
                if v > 0:
                    intensity = min(int(v * 10), 255)
                    color = (255 - intensity, 255 - intensity, 255 - intensity)
                    pygame.draw.circle(
                        self._display_surf,
                        color,
                        (x * self.SCALE, y * self.SCALE),
                        self.SCALE,
                    )

    def draw_ants(self, ants):
        for ant in ants:
            pygame.draw.circle(
                self._display_surf,
                (255, 0, 0),
                (ant.position[0] * self.SCALE, ant.position[1] * self.SCALE),
                self.SCALE + 1,
            )


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

    for t in range(500):
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
