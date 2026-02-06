import pygame
from simulation import Simulation


class App:
    SCALE = 3

    def __init__(self, sim: Simulation, static: bool, frame_rate: int = 60):
        """
        Args:
            sim (Simulation): Simulation object to visualize
            static (bool): Whether to run simulation or just visualize final state
            frame_rate (int, optional): Frame rate for visualization. Defaults to 60.
        """
        self.sim = sim
        self.static = static
        self.frame_rate = frame_rate
        self._running = True
        self._display_surf = None
        self._clock = None

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            (256 * self.SCALE, 256 * self.SCALE), pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self._display_surf.fill((255, 255, 255))
        self._clock = pygame.time.Clock()

        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        if not self.static:
            self.sim.step()
        self._display_surf.fill((255, 255, 255))
        self.draw_pheromones(self.sim.world)
        self.draw_ants(self.sim.ants)
        pygame.display.flip()
        self._clock.tick(self.frame_rate)

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
        """
        Draw pheromone trails as black circles, with opacity based on pheremone amount
        """
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
        """
        Draw ants as red circles
        """
        for ant in ants:
            pygame.draw.circle(
                self._display_surf,
                (255, 0, 0),
                (ant.position[0] * self.SCALE, ant.position[1] * self.SCALE),
                self.SCALE + 1,
            )
