"""Box layout widget for linear child placement."""

from typing import Literal

from engine import Vector2
from engine.ui.ui_layout import UILayout
from engine.ui.ui_widget import UIWidget


class UIBoxLayout(UILayout):
    """Lay out child widgets in a vertical or horizontal sequence.

    Args:
        name: Optional node name.
        x: Initial x position in pixels.
        y: Initial y position in pixels.
        width: Initial layout width in pixels.
        height: Initial layout height in pixels.
        vertical: Whether to stack children vertically.
        align: Horizontal alignment used for vertical layouts.
        padding: Space around and between child widgets.
        debug: Whether to draw the layout bounds.
    """

    def __init__(
        self,
        name: str | None = None,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        vertical: bool = True,
        align: Literal["left", "center", "right"] = "left",
        padding: float = 10,
        debug: bool = False,
    ) -> None:
        super().__init__(name, x, y, width, height, debug)
        self.vertical = vertical
        self.align = align
        self.padding = padding

    def _calculate_x_offset(self, widget: UIWidget) -> float:
        """Calculate a child widget x offset from layout settings.

        Args:
            widget: Child widget being positioned.

        Returns:
            Horizontal offset in pixels.
        """

        if self.vertical:
            match self.align:
                case "center":
                    return (self.width - widget.width) / 2
                case "right":
                    return self.width - widget.width - self.padding
        return self.padding

    def fit_content(self) -> None:
        """Resize the layout to tightly contain its widget children."""

        super().fit_content()
        widgets = self.get_widget_children()
        if not widgets:
            return
        if self.vertical:
            self.width = max(w.width for w in widgets) + 2 * self.padding
            self.height = sum(w.height for w in widgets) + self.padding * (
                len(widgets) + 1
            )
        else:
            self.width = sum(w.width for w in widgets) + self.padding * (
                len(widgets) + 1
            )
            self.height = max(w.height for w in widgets) + 2 * self.padding

    def _do_layout(self) -> None:
        """Position child widgets in layout order."""

        super()._do_layout()
        positional_offset = Vector2(0.0, self.padding)
        for child in self._children:
            if isinstance(child, UIWidget):
                x_offset = self._calculate_x_offset(child)
                child.position = positional_offset + Vector2(x_offset, 0)
                if self.vertical:
                    positional_offset += Vector2(0, child.height + self.padding)
                else:
                    positional_offset += Vector2(child.width + self.padding, 0)
