import numpy as np
import pygame


class Ant:
    def __init__(self, position, heading):
        self.position = position
        self.heading = heading


class App:
    def __init__(self):
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
                v = world[y, x]
                self.surface.set_at((x, y), (v, v, v))

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


world = np.random.rand(256, 256) * 256

if __name__ == "__main__":
    theApp = App()
    theApp.on_execute()
