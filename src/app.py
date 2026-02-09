"""
PyGame application for running and displaying ant simulation
"""

import pygame
import numpy as np
import asyncio

from ant import Ant
from simulation import Simulation
from constants import SimulationConstants
import constants


class App:
    """
    PyGame application for visualizing and interacting with the ant simulation.
    Takes a Simulation object as input, runs and displays the simulation,
    and listens for user input to control the simulation and tweak constants.
    """

    # Window
    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080
    WORLD_SIZE = 256
    SCALE = WINDOW_HEIGHT / WORLD_SIZE

    # Input
    KEY_HOLD_DELAY = 300  # milliseconds

    # Frame rate options
    SPEED_OPTIONS = [7, 15, 30, 60, 90]
    SPEED_LABELS = ["0.25x", "0.5x", "1x", "2x", "3x"]

    # Sim constant presets
    PRESET_KEYS = {
        pygame.K_1: constants.FIG_3A,
        pygame.K_2: constants.FIG_3B,
        pygame.K_3: constants.FIG_3C,
        pygame.K_4: constants.FIG_4A,
        pygame.K_5: constants.FIG_4B,
        pygame.K_6: constants.FIG_4C,
        pygame.K_7: constants.FIG_5A,
        pygame.K_8: constants.FIG_5B,
        pygame.K_9: constants.FIG_5C,
        pygame.K_0: constants.FIG_6A,
        pygame.K_MINUS: constants.FIG_6B,
    }

    # Colors
    BG_COLOR = (255, 255, 255)
    TRAIL_VALUE = 60
    TEXT_BLACK = (120,) * 3
    SELECTED_BLACK = (30,) * 3
    ANT_COLOR = (200, 0, 0)

    # Text
    FONT_SIZE = 22
    LINE_HEIGHT = 30
    INDENT_WIDTH = 25

    # Pheromone rendering
    PHEROMONE_INTENSITY_SCALE = 8

    # Layout Constants
    PANEL_X = WINDOW_HEIGHT
    PANEL_DIVIDER_WIDTH = 3
    LEFT_COL_X = PANEL_X + 40
    RIGHT_COL_X = PANEL_X + 440

    TIMESTEP_Y = 40
    SPEED_Y = 70
    INSTRUCTIONS_Y = 130
    PRESETS_TITLE_Y = 280
    PRESETS_START_Y = 310
    CONSTANTS_TITLE_Y = 40
    CONSTANTS_START_Y = 100

    KERNEL_LABEL_ROW = 5.5
    KERNEL_VALUE_GAP = 1.5

    INDICATOR_LEFT_OFFSET = -35
    INDICATOR_RIGHT_OFFSET = 300

    def __init__(self, sim: Simulation):
        """
        Args:
            sim (Simulation): Simulation object to visualize
        """
        self.sim = sim

        # PyGame state
        self.running = True
        self.display_surf: pygame.Surface = None
        self.clock: pygame.time.Clock = None
        self.paused = False

        # Frame rate control
        self.frame_rate = 30
        self.speed_idx = 2

        # Track key holding state
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

        # Track active sim constant preset
        self.active_preset_key: int = None

    # region: PyGame Core
    # PyGame boilerplate from [http://pygametutorials.wikidot.com/tutorials-basic]

    def on_init(self):
        """
        Initialize PyGame, set up display surface and clock
        """
        pygame.init()
        self.display_surf = pygame.display.set_mode(
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT),
            pygame.HWSURFACE | pygame.DOUBLEBUF,
        )
        self.display_surf.fill(self.BG_COLOR)
        self.clock = pygame.time.Clock()
        self._font = pygame.font.SysFont("helvetica", self.FONT_SIZE, bold=True)

        self.running = True

    def on_event(self, event):
        """
        Called each loop: handle PyGame events, listening for quit and keypresses
        """
        if event.type == pygame.QUIT:
            self.running = False

        self.handle_keypress(event)

    def on_loop(self):
        """
        Called each loop: update simulation, handle held inputs, and render ui
        """
        if not self.paused:
            self.sim.step()

        self.handle_key_held()

        self.draw_loop()
        self.clock.tick(self.frame_rate)

    def on_cleanup(self):
        """
        Cleanup PyGame resources on quit
        """
        pygame.quit()

    async def on_execute(self):
        """
        Main application loop
        """
        self.on_init()
        while self.running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            await asyncio.sleep(0)
        self.on_cleanup()

    # region: Key Input

    def handle_keypress(self, event: pygame.event.Event):
        """
        Listens for keypresses and triggers corresponding actions. Also tracks
        key pressing and releasing to know when keys are being held.
        """
        if event.type == pygame.KEYDOWN:
            # Pause
            if event.key == pygame.K_SPACE:
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
                self.active_preset_key = None
                self.modify_constant(-1)
            elif event.key == pygame.K_d:
                self.active_preset_key = None
                self.modify_constant(1)
            # Apply presets
            elif event.key in self.PRESET_KEYS:
                self.active_preset_key = event.key
                self.apply_preset(self.PRESET_KEYS[event.key])
            # Speed control
            elif event.key == pygame.K_q:
                self.speed_idx = max(0, self.speed_idx - 1)
                self.frame_rate = self.SPEED_OPTIONS[self.speed_idx]
            elif event.key == pygame.K_e:
                self.speed_idx = min(len(self.SPEED_OPTIONS) - 1, self.speed_idx + 1)
                self.frame_rate = self.SPEED_OPTIONS[self.speed_idx]

            # Record keypress time to track hold length
            if event.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_a, pygame.K_d]:
                if not self.key_held[event.key]:
                    self.key_hold_time[event.key] = pygame.time.get_ticks()
                    self.key_held[event.key] = True

        # Check for key releases to stop hold tracking
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_RIGHT, pygame.K_LEFT, pygame.K_a, pygame.K_d]:
                self.key_held[event.key] = False

    def handle_key_held(self):
        """
        Handle keys being held down for continuous actions.
        Left and right arrow continuously step through the simulation,
        'a' and 'd' continuously modify the selected constant.
        """
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # Map keys to their actions
        key_actions = {
            pygame.K_RIGHT: self.sim.step,
            pygame.K_LEFT: self.sim.step_backward,
            pygame.K_a: lambda: self.modify_constant(-1),
            pygame.K_d: lambda: self.modify_constant(1),
        }

        for key, action in key_actions.items():
            if (
                keys[key]
                and current_time - self.key_hold_time[key] > self.KEY_HOLD_DELAY
            ):
                action()

    # region: Constants

    def apply_preset(self, preset: SimulationConstants):
        """
        Apply a simulation constant preset, updating user_constants but not
        applying to sim until restart
        """
        self.user_constants["fidelity min"] = preset.fidelity_min
        self.user_constants["fidelity delta"] = preset.fidelity_delta
        self.user_constants["pheromone deposition"] = preset.pheromone_deposition
        self.user_constants["pheromone saturation"] = preset.pheromone_saturation
        for i in range(5):
            self.user_constants[f"B{i}"] = preset.turning_kernel[i]

    def modify_constant(self, polarity: int):
        """
        Modify the selected constant in the direction of the polarity

        Args:
            polarity (int): +1 or -1, direction to change the constant
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

        new_value = current_value + (polarity * step)
        new_value = np.clip(new_value, *clamp)

        self.user_constants[constant_name] = new_value

    def build_constants(self) -> SimulationConstants:
        """
        Convert user_constants dict to SimulationConstants object, used to
        pass constants to Simulation during reset
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
        """
        Main display loop: clear screen, draw pheromones, ants, and control panel
        """
        self.display_surf.fill(self.BG_COLOR)
        self.draw_pheromones(self.sim.world)
        self.draw_ants(self.sim.ants)
        self.draw_control_panel()

        pygame.display.flip()

    def draw_control_panel(self):
        """
        Draw the right-side control panel, displaying keybind instructions and
        allowing user to tweak constants
        """
        self.draw_divider_line()
        self.draw_time_and_speed()
        self.draw_instructions()
        self.draw_constant_presets()
        self.draw_constants()

    def draw_divider_line(self):
        """
        Draw vertical line separating simulation and control panel
        """
        pygame.draw.line(
            self.display_surf,
            self.TEXT_BLACK,
            (self.PANEL_X, 0),
            (self.PANEL_X, self.WINDOW_HEIGHT),
            self.PANEL_DIVIDER_WIDTH,
        )

    def draw_time_and_speed(self):
        """
        Draw text displaying current timestep and simulation speed
        """
        # Draw timestep
        timestep_text = self._font.render(
            f"t : {self.sim.time_step}", True, self.TEXT_BLACK
        )
        self.display_surf.blit(timestep_text, (self.LEFT_COL_X, self.TIMESTEP_Y))

        # Draw speed
        speed_text = self._font.render(
            f"sim speed : {self.SPEED_LABELS[self.speed_idx]}",
            True,
            self.TEXT_BLACK,
        )
        self.display_surf.blit(speed_text, (self.LEFT_COL_X, self.SPEED_Y))

    def draw_instructions(self):
        """
        Draw text displaying keybind instructions
        """
        pause_text = self._font.render("pause : [space]", True, self.TEXT_BLACK)
        step_text = self._font.render("step : [←] [→]", True, self.TEXT_BLACK)
        speed_text = self._font.render("change speed : [q] [e]", True, self.TEXT_BLACK)
        restart_text = self._font.render(
            "restart with new constants : [r]", True, self.TEXT_BLACK
        )

        y_pos = np.arange(4) * self.LINE_HEIGHT + self.INSTRUCTIONS_Y
        self.display_surf.blit(pause_text, (self.LEFT_COL_X, y_pos[0]))
        self.display_surf.blit(step_text, (self.LEFT_COL_X, y_pos[1]))
        self.display_surf.blit(speed_text, (self.LEFT_COL_X, y_pos[2]))
        self.display_surf.blit(restart_text, (self.LEFT_COL_X, y_pos[3]))

    def draw_constant_presets(self):
        """
        Draw text displaying constant preset keybinds
        """
        # Preset keybinds
        preset_title = self._font.render("constant presets :", True, self.TEXT_BLACK)
        self.display_surf.blit(preset_title, (self.LEFT_COL_X, self.PRESETS_TITLE_Y))

        presets_info = [
            "3A : [1]",
            "3B : [2]",
            "3C : [3]",
            "4A : [4]",
            "4B : [5]",
            "4C : [6]",
            "5A : [7]",
            "5B : [8]",
            "5C : [9]",
            "6A : [0]",
            "6B : [-]",
        ]

        for idx, preset_text in enumerate(presets_info):
            # Highlight the active preset
            preset_key = [
                pygame.K_1,
                pygame.K_2,
                pygame.K_3,
                pygame.K_4,
                pygame.K_5,
                pygame.K_6,
                pygame.K_7,
                pygame.K_8,
                pygame.K_9,
                pygame.K_0,
                pygame.K_MINUS,
            ][idx]
            color = (
                self.SELECTED_BLACK
                if preset_key == self.active_preset_key
                else self.TEXT_BLACK
            )
            preset_label = self._font.render(preset_text, True, color)
            y = self.PRESETS_START_Y + idx * self.LINE_HEIGHT
            self.display_surf.blit(
                preset_label, (self.LEFT_COL_X + self.INDENT_WIDTH, y)
            )

    def draw_constants(self):
        """
        Draw current constants and their values, with an indicator for the selected constant
        """

        # Constants section
        const_title = self._font.render("constants : [wasd]", True, self.TEXT_BLACK)
        self.display_surf.blit(const_title, (self.RIGHT_COL_X, self.CONSTANTS_TITLE_Y))

        # Draw each constant
        for i, name in enumerate(self.constant_order):
            value = self.user_constants[name]
            is_selected = i == self.selected_constant_idx
            color = self.SELECTED_BLACK if is_selected else self.TEXT_BLACK

            if not name.startswith("B"):
                value_text = f"{int(value)}"
                pos = (self.RIGHT_COL_X, self.CONSTANTS_START_Y + i * self.LINE_HEIGHT)
            else:
                value_text = f"{value:.2f}"
                pos = (
                    self.RIGHT_COL_X + self.INDENT_WIDTH,
                    self.CONSTANTS_START_Y
                    + (i + self.KERNEL_VALUE_GAP) * self.LINE_HEIGHT,
                )

            if is_selected:
                indicator_left = self._font.render("-", True, color)
                indicator_right = self._font.render("-", True, color)
                self.display_surf.blit(
                    indicator_left,
                    (self.RIGHT_COL_X + self.INDICATOR_LEFT_OFFSET, pos[1]),
                )
                self.display_surf.blit(
                    indicator_right,
                    (self.RIGHT_COL_X + self.INDICATOR_RIGHT_OFFSET, pos[1]),
                )

            const_text = self._font.render(f"{name} : {value_text}", True, color)
            self.display_surf.blit(const_text, pos)

        # Draw kernel label
        kernel_label = self._font.render("turning kernel :", True, self.TEXT_BLACK)
        kernel_y = self.CONSTANTS_START_Y + self.KERNEL_LABEL_ROW * self.LINE_HEIGHT
        self.display_surf.blit(kernel_label, (self.RIGHT_COL_X, kernel_y))

    def draw_pheromones(self, world: np.ndarray):
        """
        Draw pheromone trails as black circles, with opacity based on pheremone amount

        Args:
            world (np.ndarray): 2D array representing pheromone levels, passed from Simulation
        """
        for y in range(self.WORLD_SIZE):
            for x in range(self.WORLD_SIZE):
                v = world[y, x]
                if v > 0:
                    intensity = min(
                        int(v * self.PHEROMONE_INTENSITY_SCALE),
                        255 - self.TRAIL_VALUE,
                    )
                    color = (255 - intensity,) * 3
                    pygame.draw.circle(
                        self.display_surf,
                        color,
                        (x * self.SCALE, y * self.SCALE),
                        self.SCALE,
                    )

    def draw_ants(self, ants: list[Ant]):
        """
        Draw ants as red circles

        Args:
            ants (list[Ant]): List of all ants in simulation, passed from Simulation
        """
        for ant in ants:
            pygame.draw.circle(
                self.display_surf,
                self.ANT_COLOR,
                (ant.position[0] * self.SCALE, ant.position[1] * self.SCALE),
                self.SCALE,
            )
