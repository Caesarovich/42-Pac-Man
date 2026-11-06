"""Layout base class for widgets that position child widgets."""

from abc import ABC

from engine.ui.ui_widget import UIWidget


class UILayout(UIWidget, ABC):
    """Base widget that recalculates child widget placement.

    Args:
        name: Optional node name.
        x: Initial x position in pixels.
        y: Initial y position in pixels.
        width: Initial layout width in pixels.
        height: Initial layout height in pixels.
        debug: Whether to draw the layout bounds.
    """

    def __init__(
        self,
        name: str | None = None,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        debug: bool = False,
    ) -> None:
        super().__init__(name, x, y, width, height, debug)
        self.layout_dirty = True

    def add(self, widget: UIWidget, **kwargs: object) -> None:
        """Add a child widget and mark the layout as dirty.

        Args:
            widget: Child widget to add.
            **kwargs: Layout-specific options accepted by subclasses.
        """

        super().add(widget, **kwargs)
        self.layout_dirty = True

    def _do_layout(self) -> None:
        """Recalculate child placement for this layout."""

    def do_layout(self) -> None:
        """Recursively update dirty child layouts before this layout."""

        for child in self._children:
            if isinstance(child, UILayout):
                child.do_layout()
        if self.layout_dirty:
            self._do_layout()
            self.layout_dirty = False
