import pygame
import numpy as np

from simulation import Simulation


class App:
    SCALE = 1080 / 256  # Fill full height
    TRAIL_VALUE = 60
    TEXT_VALUE = 80
    TEXT_BLACK = (TEXT_VALUE, TEXT_VALUE, TEXT_VALUE)
    FONT_SIZE = 22
    KEY_HOLD_DELAY = 300  # milliseconds

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
        self.paused = False
        self.key_hold_time = {pygame.K_RIGHT: 0, pygame.K_LEFT: 0}
        self.key_held = {pygame.K_RIGHT: False, pygame.K_LEFT: False}

    def on_init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            (1920, 1080), pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        self._display_surf.fill((255, 255, 255))
        self._clock = pygame.time.Clock()
        self._font = pygame.font.SysFont("helvetica", self.FONT_SIZE, bold=True)

        self._running = True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

        self.handle_keypress(event)

    def on_loop(self):
        # Check held keys for continuous stepping (only after hold delay)
        if not self.paused:
            self.sim.step()
        else:
            self.handle_key_held()

        self.draw_loop()
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

    # region: Key Input

    def handle_keypress(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F8:
                self._running = False
            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_r:
                self.sim.reset()
                self.paused = False
            elif event.key == pygame.K_RIGHT:
                self.sim.step()
            elif event.key == pygame.K_LEFT:
                self.sim.step_backward()

            # Record keypress time to track hold length
            if event.key in [pygame.K_RIGHT, pygame.K_LEFT] and not self.static:
                if not self.key_held[event.key]:
                    self.key_hold_time[event.key] = pygame.time.get_ticks()
                    self.key_held[event.key] = True

        # Check for key releases to stop hold tracking
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_RIGHT, pygame.K_LEFT]:
                self.key_held[event.key] = False

    def handle_key_held(self):
        if self.static:
            return

        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            if current_time - self.key_hold_time[pygame.K_RIGHT] > self.KEY_HOLD_DELAY:
                self.sim.step()
        elif keys[pygame.K_LEFT]:
            if current_time - self.key_hold_time[pygame.K_LEFT] > self.KEY_HOLD_DELAY:
                self.sim.step_backward()

    # region: Drawing

    def draw_loop(self):
        self._display_surf.fill((255, 255, 255))
        self.draw_pheromones(self.sim.world)
        self.draw_ants(self.sim.ants)
        self.draw_control_panel()

        pygame.display.flip()

    def draw_control_panel(self):
        pygame.draw.line(
            self._display_surf,
            self.TEXT_BLACK,
            (1080, 0),
            (1080, 1080),
            3,
        )

        LEFT_COL_X = 1120

        # Draw timestep
        timestep_text = self._font.render(
            f"t : {self.sim.time_step}", True, self.TEXT_BLACK
        )
        self._display_surf.blit(timestep_text, (LEFT_COL_X, 40))

        # Instructions
        pause_text = self._font.render("pause : space", True, self.TEXT_BLACK)
        step_text = self._font.render("step : ← →", True, self.TEXT_BLACK)
        restart_text = self._font.render("restart : r", True, self.TEXT_BLACK)

        y_pos = np.arange(3) * 30 + 100
        self._display_surf.blit(pause_text, (LEFT_COL_X, y_pos[0]))
        self._display_surf.blit(step_text, (LEFT_COL_X, y_pos[1]))
        self._display_surf.blit(restart_text, (LEFT_COL_X, y_pos[2]))

    def draw_pheromones(self, world):
        """
        Draw pheromone trails as black circles, with opacity based on pheremone amount
        """
        for y in range(256):
            for x in range(256):
                v = world[y, x]
                if v > 0:
                    intensity = min(int(v * 10), 255 - self.TRAIL_VALUE)
                    color = (255 - intensity, 255 - intensity, 255 - intensity)
                    pygame.draw.circle(
                        self._display_surf,
                        color,
                        (
                            x * self.SCALE,
                            y * self.SCALE,
                        ),
                        self.SCALE,
                    )

    def draw_ants(self, ants):
        """
        Draw ants as red circles
        """
        for ant in ants:
            pygame.draw.circle(
                self._display_surf,
                (200, 0, 0),
                (
                    ant.position[0] * self.SCALE,
                    ant.position[1] * self.SCALE,
                ),
                self.SCALE,
            )
