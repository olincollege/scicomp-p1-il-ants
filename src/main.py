"""
Main entry point for the ant simulation application.
"""

from simulation import Simulation
from app import App
import constants

TIME_STEPS = 500

if __name__ == "__main__":
    s = Simulation(constants=constants.FIG_3C, seed=42)
    app = App(s)
    app.on_execute()
