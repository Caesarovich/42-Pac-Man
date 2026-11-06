from typing import TYPE_CHECKING

from engine import Node

if TYPE_CHECKING:
    from pac_man.game.game_manager import GameState
from engine.ui import UILabel

ScoreEvent = tuple[str, str]


class UIScoreController(Node):
    """Update score UI labels from game score events."""

    def __init__(self, name: str | None = None) -> None:
        """Initialize the UI controller.

        Args:
            score_label: Label displaying the score.
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self._score_labels: dict[str, UILabel] = {}

    def add_ui_label(self, score_type: str, ui_label: UILabel) -> None:
        """Register a label for a score or counter event key.

        Args:
            score_type: Event key used to identify the label.
            ui_label: Label whose text will receive event values.
        """
        self._score_labels[score_type] = ui_label

    def on_notify(self, entity: Node | None, event: ScoreEvent) -> None:
        """Apply a score event to the score label.

        Args:
            entity: Event source. It is unused for score updates.
            event: Score event containing the latest counters.
        """
        score_type, value = event
        self._score_labels[score_type].text = value


class UIGameStateController(Node):
    """Control lifecycle message visibility from game state events."""

    def __init__(self, name: str | None = None) -> None:
        """Initialize the game-state UI controller.

        Args:
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self._labels: dict[str, UILabel] = {}

    def add_ui_label(self, score_type: str, ui_label: UILabel) -> None:
        """Register a lifecycle message label under an event key.

        Args:
            score_type: Event key used to identify the label.
            ui_label: Label whose visibility will be controlled.
        """
        self._labels[score_type] = ui_label

    def _display_label(self, name: str) -> None:
        for l_name, status in self._labels.items():
            status.visible = l_name == name

    def _hide_all(self) -> None:
        for status in self._labels.values():
            status.visible = False

    def on_notify(self, entity: Node | None, event: GameState) -> None:
        """Update lifecycle message visibility for a game state.

        Args:
            entity: Event source. It is unused for state updates.
            event: New game lifecycle state.
        """
        from pac_man.game.game_manager import GameState

        match event:
            case GameState.START:
                self._hide_all()
            case GameState.READY_CHECK:
                self._display_label("ready")
            case GameState.PLAYING:
                self._hide_all()
            case GameState.GAME_OVER:
                self._display_label("game_over")
            case GameState.TIME_S_UP:
                self._display_label("time_s_up")
            case GameState.WIN_LEVEL:
                self._display_label("winner")
