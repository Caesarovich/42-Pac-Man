"""Image widget that wraps a drawable sprite."""

from engine import Sprite2D
from engine.ui.ui_widget import UIWidget


class UIImage(UIWidget):
    """Widget that displays a Sprite2D instance.

    Args:
        name: Optional node name.
        sprite: Optional sprite to display as a child node.
        x: Initial x position in pixels.
        y: Initial y position in pixels.
        width: Initial widget width in pixels.
        height: Initial widget height in pixels.
        debug: Whether to draw the widget bounds.
    """

    def __init__(
        self,
        name: str | None = None,
        sprite: Sprite2D | None = None,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        debug: bool = False,
    ) -> None:
        super().__init__(name, x, y, width, height, debug)
        self.sprite = sprite
        if sprite is not None:
            self.add_child(sprite)

    def fit_content(self) -> None:
        """Resize the widget to match the sprite draw size."""

        if self.sprite is not None:
            sprite_draw_size = self.sprite.get_draw_size()
            if self.sprite.width is not None:
                self.width = self.sprite.width
            else:
                self.width = sprite_draw_size.x
            if self.sprite.height is not None:
                self.height = self.sprite.height
            else:
                self.height = sprite_draw_size.y
        super().fit_content()

    def stretch_content(self) -> None:
        """Resize the sprite to match the widget bounds."""

        if self.sprite is not None:
            self.sprite.set_size(self.width, self.height)
        super().stretch_content()
