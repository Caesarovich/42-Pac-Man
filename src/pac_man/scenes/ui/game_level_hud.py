import logging
from typing import Literal

import pyray

from engine import Node
from engine.ui import UIAnchorLayout, UIBoxLayout, UILabel, UIManager
from pac_man.config.game_config import GameConfig
from pac_man.game.game_manager import GameManager
from pac_man.scenes.ui.ui_controller import (
    UIGameStateController,
    UIScoreController,
)

logger = logging.getLogger(__name__)


class GameLevelHUD(Node):
    """Display gameplay counters and lifecycle messages around the maze."""

    BASE_FONT_SIZE = 28

    def __init__(
        self,
        game_config: GameConfig,
        game_manager: GameManager,
        name: str = "GameLevel",
    ) -> None:
        """Initialize the HUD and its event controllers.

        Args:
            game_config: Gameplay configuration associated with the level.
            game_manager: Manager that publishes counter and state events.
            name: Node name used in the scene tree.
        """
        super().__init__(name=name)
        self._game_manager = game_manager
        self._game_config = game_config
        self._maze_area: pyray.Rectangle | None = None

        self._ui = UIManager(name="game_level_ui_manager")
        self._score_ui_controller = UIScoreController(name="score_ui_controller")
        self._game_state_ui_controller = UIGameStateController(
            name="game_state_ui_controller"
        )

    @property
    def maze_area(self) -> pyray.Rectangle:
        """Return the maze rectangle used to position HUD elements.

        Raises:
            AssertionError: If the maze area has not been assigned.
        """
        assert self._maze_area is not None, "Maze area is not set"
        return self._maze_area

    @maze_area.setter
    def maze_area(self, maze_area: pyray.Rectangle) -> None:
        """Set the maze rectangle used to position HUD elements.

        Args:
            maze_area: Render-space rectangle occupied by the maze.
        """
        self._maze_area = maze_area

    def _on_enter_tree(self) -> None:
        """Build the HUD when it enters the active scene tree."""
        self._init()
        logger.info("HUD is ready")

    def _init(self) -> None:
        """Create HUD layouts and subscribe controllers to game events."""
        self.add_child(self._ui)
        ui_layout = UIAnchorLayout(
            "game_level_ui_layout",
            width=pyray.get_render_width(),
            height=pyray.get_render_height(),
        )
        self._ui.add(ui_layout)

        self._create_hud_labels(ui_layout)
        self._create_event_labels(ui_layout)

        self._game_manager.score_event_handler.add_observer(self._score_ui_controller)
        self._game_manager.game_state_event_handler.add_observer(
            self._game_state_ui_controller
        )

    def _create_hud_labels(self, ui_layout: UIAnchorLayout) -> None:
        """Create and position persistent gameplay counter labels.

        Args:
            ui_layout: Root layout receiving the counter layouts.
        """
        width = self.maze_area.width
        height = (pyray.get_render_height() - self.maze_area.height) / 2
        top_layout = UIAnchorLayout(
            "top_layout",
            width=width,
            height=height,
        )
        bottom_layout = UIAnchorLayout(
            "bottom_layout",
            width=width,
            height=height,
        )

        hud_widgets: list[
            tuple[
                str,
                str,
                str,
                UIAnchorLayout,
                Literal["left", "center", "right"],
            ]
        ] = [
            ("high_score", "Highscore:", "0", top_layout, "left"),
            ("current_score", "Score:", "0", top_layout, "center"),
            ("time", "Time:", "0.00", top_layout, "right"),
            ("level", "Level:", "0", bottom_layout, "right"),
            ("lives", "Lives:", "0", bottom_layout, "left"),
        ]
        for name, text_label, text_value, layout, anchor_x in hud_widgets:
            widget_layout = UIBoxLayout(f"{name}_layout", vertical=False)
            ui_label = UILabel(
                name=f"{name}_label",
                text=text_label,
                font_size=self.BASE_FONT_SIZE,
            )
            ui_value = UILabel(
                name=f"{name}_value",
                text=text_value,
                font_size=self.BASE_FONT_SIZE,
            )
            widget_layout.add(ui_label)
            widget_layout.add(ui_value)
            widget_layout.fit_content()

            anchor_y: Literal["bottom", "top"] = (
                "bottom" if layout is top_layout else "top"
            )
            align_y = -5 if layout is top_layout else 5
            layout.add(
                widget_layout,
                anchor_x=anchor_x,
                anchor_y=anchor_y,
                align_y=align_y,
            )

            self._score_ui_controller.add_ui_label(name, ui_value)

        top_layout.fit_content()
        bottom_layout.fit_content()

        ui_layout.add(top_layout, anchor_x="center")
        ui_layout.add(bottom_layout, anchor_x="center", anchor_y="bottom")

    def _create_event_labels(self, ui_layout: UIAnchorLayout) -> None:
        """Create centered labels for lifecycle events.

        Args:
            ui_layout: Root layout receiving the event labels.
        """
        events = [
            ("ready", "Ready!", pyray.YELLOW),
            ("game_over", "Game Over!", pyray.RED),
            ("time_s_up", "Time's Up", pyray.RED),
            ("winner", "Winner!", pyray.YELLOW),
        ]
        ui_labels = {
            label: UILabel(
                name=label,
                text=text,
                font_size=int(1.5 * self.BASE_FONT_SIZE),
                text_color=color,
            )
            for label, text, color in events
        }
        for label, ui_label in ui_labels.items():
            ui_label.visible = False
            ui_layout.add(
                ui_label,
                anchor_x="center",
                anchor_y="middle",
                align_y=-self.maze_area.height / 6,
            )
            self._game_state_ui_controller.add_ui_label(label, ui_label)
