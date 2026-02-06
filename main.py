import time

from simulation import Simulation
from app import App

TIME_STEPS = 500
STATIC = False

if __name__ == "__main__":
    s = Simulation(seed=42)

    if STATIC:
        start = time.time()
        for t in range(TIME_STEPS):
            s.step()
        end = time.time()
        print(f"Simulation time: {end - start:.2f} s")
        print("Num remaining ants:", len(s.ants))

    app = App(s, STATIC)
    app.on_execute()
