"""
Main entry point for the ant simulation application.
"""

import time

from simulation import Simulation
from app import App
import constants

TIME_STEPS = 1500
STATIC = True

if __name__ == "__main__":
    s = Simulation(constants=constants.FIG_3C, seed=42)

    if STATIC:
        start = time.time()
        for t in range(TIME_STEPS):
            s.step()
            if t % 200 == 0:
                print(f"Step {t}, running for: {time.time() - start:.2f} s")
        end = time.time()
        print(f"Simulation time: {end - start:.2f} s")
        print("Num remaining ants:", len(s.ants))

    app = App(s)
    if STATIC:
        app.paused = True
    app.on_execute()
