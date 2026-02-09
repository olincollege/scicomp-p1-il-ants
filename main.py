# /// script
# dependencies = ["numpy"]
# ///

"""
Main entry point for the ant simulation application.
"""

import asyncio

from simulation import Simulation
from app import App
import constants


async def main():
    s = Simulation(constants=constants.FIG_3C, seed=42)
    app = App(s)
    await app.on_execute()


asyncio.run(main())
