"""Text label widget for the UI layer."""

from typing import Literal

import pyray

from engine.ui.ui_widget import UIWidget


class UILabel(UIWidget):
    """Widget that renders a single line of text.

    Args:
        name: Optional node name.
        text: Initial text to render.
        x: Initial x position in pixels.
        y: Initial y position in pixels.
        width: Initial widget width in pixels.
        height: Initial widget height in pixels.
        font_size: Font size in pixels.
        text_color: Text color.
        align: Horizontal text alignment relative to the widget origin.
        auto_size: Whether to fit the widget to its text.
        debug: Whether to draw the widget bounds.
    """

    def __init__(
        self,
        name: str | None = None,
        text: str = "",
        x: float = 0.0,
        y: float = 0.0,
        width: float = 100.0,
        height: float = 100.0,
        font_size: int = 12,
        text_color: pyray.Color = pyray.WHITE,
        align: Literal["left", "right", "center"] = "left",
        auto_size: bool = True,
        debug: bool = False,
    ) -> None:
        super().__init__(name, x, y, width, height, debug)
        self._text = text
        self.font_size = font_size
        self.text_color = text_color
        self.align = align
        self.text_width = pyray.measure_text(text, font_size)
        self.auto_size = auto_size
        if self.auto_size:
            self.fit_content()

    def _on_draw(self) -> None:
        """Draw the label text and optional debug bounds."""
        x, y = self.global_transform.position
        match self.align:
            case "center":
                x -= self.width / 2
            case "right":
                x -= self.width
        pyray.draw_text(self._text, int(x), int(y), self.font_size, self.text_color)

    @property
    def text(self) -> str:
        """Current label text."""

        return self._text

    @text.setter
    def text(self, text: str) -> None:
        """Update label text and refresh the measured size.

        Args:
            text: New text to render.
        """

        self._text = text
        self.text_width = pyray.measure_text(text, self.font_size)
        if self.auto_size:
            self.fit_content()

    def fit_content(self) -> None:
        """Resize the label to the measured text bounds."""

        self.width = self.text_width
        self.height = self.font_size
        super().fit_content()

    def _draw_debug(self) -> None:
        """Draw the optional debug bounds."""
        pos = self.global_transform.position
        x, y = pos.x, pos.y
        if self.align == "center":
            x -= self.width / 2
        elif self.align == "right":
            x -= self.width
        pyray.draw_rectangle_lines(
            int(x - 1),
            int(y - 1),
            int(self.width + 2),
            int(self.height + 2),
            pyray.RED,
        )
