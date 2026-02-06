import pygame


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
