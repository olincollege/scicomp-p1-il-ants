import numpy as np
import random
import time

from ant import Ant, Direction
from app import App

TIME_STEPS = 500
SPAWN_POINT = np.array([128, 128])

if __name__ == "__main__":
    start = time.time()
    random.seed(42)
    np.random.seed(42)
    world = np.zeros((256, 256))
    ants = []

    for t in range(TIME_STEPS):
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
