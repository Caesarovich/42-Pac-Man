"""Base widget type shared by all UI components."""

from abc import ABC

import pyray

from engine import Node2D, Vector2
from engine.ui.anchor_constraints import AnchorConstraint


class UIWidget(Node2D, ABC):
    """Base node for rectangular UI elements.

    Args:
        name: Optional node name.
        x: Initial x position in pixels.
        y: Initial y position in pixels.
        width: Initial widget width in pixels.
        height: Initial widget height in pixels.
        debug: Whether to draw the widget bounds.
    """

    def __init__(
        self,
        name: str | None = None,
        x: float = 0.0,
        y: float = 0.0,
        width: float = 100.0,
        height: float = 100.0,
        debug: bool = False,
    ) -> None:
        super().__init__(name)
        self.position = Vector2(x, y)
        self.width = width
        self.height = height
        self.debug = debug
        self.anchor_constraint: AnchorConstraint | None = None

    def center_on_screen(self) -> None:
        """Move the widget origin to the current render surface center."""

        self.position = Vector2(
            pyray.get_render_width() / 2, pyray.get_render_height() / 2
        )

    def fit_content(self) -> None:
        """Resize the widget to its content when supported."""

        self.invalidate_layout()

    def stretch_content(self) -> None:
        """Stretch the widget content to the current widget bounds."""

        self.invalidate_layout()

    def invalidate_layout(self) -> None:
        """Mark parent layouts as dirty after a geometry change."""

        from engine.ui.ui_layout import UILayout

        parent = self.parent
        while parent is not None:
            if isinstance(parent, UILayout):
                parent.layout_dirty = True
            parent = parent.parent

    def set_size(self, width: float, height: float) -> None:
        """Set the widget size and invalidate parent layouts.

        Args:
            width: New widget width in pixels.
            height: New widget height in pixels.
        """

        self.width = width
        self.height = height
        self.invalidate_layout()

    def add(self, widget: UIWidget, **kwargs: object) -> None:
        """Add a child widget.

        Args:
            widget: Child widget to attach to this widget.
            **kwargs: Layout-specific options accepted by subclasses.
        """

        self.add_child(widget)
        self.invalidate_layout()

    def get_widget_children(self) -> list[UIWidget]:
        """Return direct children that are UI widgets.

        Returns:
            Direct children filtered to UI widget instances.
        """

        return [w for w in self.children if isinstance(w, UIWidget)]

    def _draw(self) -> None:
        """Draw the optional debug bounds."""
        super()._draw()
        if self.debug:
            self._draw_debug()

    def _draw_debug(self) -> None:
        """Draw the widget bounds if debug is enabled."""
        if self.debug:
            pyray.draw_rectangle_lines(
                int(self.global_transform.position.x - 1),
                int(self.global_transform.position.y - 1),
                int(self.width + 2),
                int(self.height + 2),
                pyray.RED,
            )
