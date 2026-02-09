import pygame
import numpy as np

from simulation import Simulation
from constants import SimulationConstants


class App:
    SCALE = 1080 / 256  # Fill full height
    TRAIL_VALUE = 60
    TEXT_VALUE = 120
    TEXT_BLACK = (TEXT_VALUE, TEXT_VALUE, TEXT_VALUE)
    TEXT_SELECTED = (30, 30, 30)
    FONT_SIZE = 22
    KEY_HOLD_DELAY = 300  # milliseconds
    CONSTANT_STEP = 1  # How much to change constant values

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
        self.key_hold_time = {
            pygame.K_RIGHT: 0,
            pygame.K_LEFT: 0,
            pygame.K_a: 0,
            pygame.K_d: 0,
        }
        self.key_held = {
            pygame.K_RIGHT: False,
            pygame.K_LEFT: False,
            pygame.K_a: False,
            pygame.K_d: False,
        }

        # Constants editing
        # self.modified_constants = replace(sim.constants)  # copies
        self.user_constants = {
            "seed": sim.seed,
            "fidelity min": sim.constants.fidelity_min,
            "fidelity delta": sim.constants.fidelity_delta,
            "pheromone deposition": sim.constants.pheromone_deposition,
            "pheromone saturation": sim.constants.pheromone_saturation,
            "B0": sim.constants.turning_kernel[0],
            "B1": sim.constants.turning_kernel[1],
            "B2": sim.constants.turning_kernel[2],
            "B3": sim.constants.turning_kernel[3],
            "B4": sim.constants.turning_kernel[4],
        }
        self.constant_order = list(self.user_constants.keys())
        self.selected_constant_idx = 0

    # region: PyGame Core

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
            # Quit
            if event.key == pygame.K_F8:
                self._running = False
            # Pause
            elif event.key == pygame.K_SPACE:
                self.paused = not self.paused
            # Reset
            elif event.key == pygame.K_r:
                self.sim.reset(self.build_constants(), int(self.user_constants["seed"]))
                self.paused = False
            # Step forward/backward
            elif event.key == pygame.K_RIGHT:
                self.sim.step()
            elif event.key == pygame.K_LEFT:
                self.sim.step_backward()
            # Select constant
            elif event.key == pygame.K_w:
                self.selected_constant_idx = (self.selected_constant_idx - 1) % len(
                    self.constant_order
                )
            elif event.key == pygame.K_s:
                self.selected_constant_idx = (self.selected_constant_idx + 1) % len(
                    self.constant_order
                )
            # Modify constants
            elif event.key == pygame.K_a:
                self.modify_constant(-self.CONSTANT_STEP)
            elif event.key == pygame.K_d:
                self.modify_constant(self.CONSTANT_STEP)

            # Record keypress time to track hold length
            if (
                event.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_a, pygame.K_d]
                and not self.static
            ):
                if not self.key_held[event.key]:
                    self.key_hold_time[event.key] = pygame.time.get_ticks()
                    self.key_held[event.key] = True

        # Check for key releases to stop hold tracking
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_a, pygame.K_d]:
                self.key_held[event.key] = False

    def handle_key_held(self):
        if self.static:
            return

        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # Map keys to their actions
        key_actions = {
            pygame.K_RIGHT: self.sim.step,
            pygame.K_LEFT: self.sim.step_backward,
            pygame.K_a: lambda: self.modify_constant(-self.CONSTANT_STEP),
            pygame.K_d: lambda: self.modify_constant(self.CONSTANT_STEP),
        }

        for key, action in key_actions.items():
            if (
                keys[key]
                and current_time - self.key_hold_time[key] > self.KEY_HOLD_DELAY
            ):
                action()

    # region: Constants

    def modify_constant(self, delta):
        """
        Modify the selected constant by the given delta
        """
        constant_name = self.constant_order[self.selected_constant_idx]
        current_value = self.user_constants[constant_name]

        if constant_name == "seed":
            step = 1
            clamp = (0, 1000)
        elif constant_name in {
            "fidelity min",
            "fidelity delta",
            "pheromone deposition",
            "pheromone saturation",
        }:
            step = 1
            clamp = (0, 256)
        elif constant_name.startswith("B"):
            step = 0.01
            clamp = (0.0, 1.0)

        new_value = current_value + (delta * step)
        new_value = np.clip(new_value, *clamp)

        self.user_constants[constant_name] = new_value

    def build_constants(self) -> SimulationConstants:
        """
        Convert user_constants dict to SimulationConstants object
        """
        kernel = np.array(
            [
                self.user_constants["B0"],
                self.user_constants["B1"],
                self.user_constants["B2"],
                self.user_constants["B3"],
                self.user_constants["B4"],
            ]
        )
        return SimulationConstants(
            fidelity_min=self.user_constants["fidelity min"],
            fidelity_delta=self.user_constants["fidelity delta"],
            pheromone_deposition=self.user_constants["pheromone deposition"],
            pheromone_saturation=self.user_constants["pheromone saturation"],
            turning_kernel=kernel,
        )

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
        RIGHT_COL_X = 1520

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

        # Constants section
        const_title = self._font.render("constants : wasd", True, self.TEXT_BLACK)
        self._display_surf.blit(const_title, (RIGHT_COL_X, 40))

        # Draw each constant
        for i, name in enumerate(self.constant_order):
            value = self.user_constants[name]
            is_selected = i == self.selected_constant_idx
            color = self.TEXT_SELECTED if is_selected else self.TEXT_BLACK

            # Format the name nicely
            if name.startswith("B"):
                value_text = f"{value:.2f}"
            else:
                value_text = f"{int(value)}"
            const_text = self._font.render(f"{name} : {value_text}", True, color)
            self._display_surf.blit(const_text, (RIGHT_COL_X, 100 + i * 30))

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
