import time

from simulation import Simulation
from app import App

TIME_STEPS = 500

if __name__ == "__main__":
    start = time.time()
    s = Simulation(seed=42)

    for t in range(TIME_STEPS):
        s.step()

    end = time.time()

    print(f"Simulation time: {end - start:.2f} s")
    print("Num remaining ants:", len(s.ants))

    theApp = App(s.world, s.ants)
    theApp.on_execute()
