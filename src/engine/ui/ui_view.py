"""Scene type that provides a UI manager."""

import pyray

from engine import Scene2D
from engine.ui.ui_manager import UIManager


class UIView(Scene2D):
    """Scene with a UI manager attached to the root node.

    Args:
        name: Scene name.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.ui = UIManager()
        self.root.add_child(self.ui)

    @property
    def width(self) -> float:
        """Current render surface width in pixels."""

        return pyray.get_render_width()

    @property
    def height(self) -> float:
        """Current render surface height in pixels."""

        return pyray.get_render_height()
