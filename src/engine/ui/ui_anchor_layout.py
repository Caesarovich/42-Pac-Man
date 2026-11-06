"""Anchor layout widget for edge and center based child placement."""

from engine import Vector2
from engine.ui.anchor_constraints import AnchorConstraint, AnchorX, AnchorY
from engine.ui.ui_layout import UILayout
from engine.ui.ui_widget import UIWidget


class UIAnchorLayout(UILayout):
    """Lay out child widgets using explicit anchor constraints.

    Args:
        name: Optional node name.
        x: Initial x position in pixels.
        y: Initial y position in pixels.
        width: Initial layout width in pixels.
        height: Initial layout height in pixels.
        padding: Space applied around the layout edges.
        debug: Whether to draw the layout bounds.
    """

    def __init__(
        self,
        name: str | None = None,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        padding: float = 0,
        debug: bool = False,
    ) -> None:
        super().__init__(name, x, y, width, height, debug)
        self.padding = padding

    def add(
        self,
        widget: UIWidget,
        anchor_x: AnchorX = "left",
        align_x: float = 0.0,
        anchor_y: AnchorY = "top",
        align_y: float = 0.0,
        **kwargs: object,
    ) -> None:  # ty: ignore[invalid-method-override]
        """Add a widget with anchor constraints.

        Args:
            widget: Child widget to add.
            anchor_x: Horizontal anchor reference.
            align_x: Horizontal offset from the selected anchor.
            anchor_y: Vertical anchor reference.
            align_y: Vertical offset from the selected anchor.
            **kwargs: Additional options accepted by the parent class.
        """

        super().add(widget, **kwargs)
        widget.anchor_constraint = AnchorConstraint(
            anchor_x, align_x, anchor_y, align_y
        )

    def _calculate_x_offset(
        self, widget_width: float, anchor_x: AnchorX, align_x: float
    ) -> float:
        """Calculate the x offset for an anchored widget.

        Args:
            widget_width: Width of the widget being positioned.
            anchor_x: Horizontal anchor reference.
            align_x: Horizontal offset from the selected anchor.

        Returns:
            Horizontal offset in pixels.
        """

        match anchor_x:
            case "center":
                return (self.width - widget_width) / 2 + align_x
            case "right":
                return self.width - widget_width + align_x - self.padding
        return align_x + self.padding

    def _calculate_y_offset(
        self, widget_height: float, anchor_y: AnchorY, align_y: float
    ) -> float:
        """Calculate the y offset for an anchored widget.

        Args:
            widget_height: Height of the widget being positioned.
            anchor_y: Vertical anchor reference.
            align_y: Vertical offset from the selected anchor.

        Returns:
            Vertical offset in pixels.
        """

        match anchor_y:
            case "middle":
                return (self.height - widget_height) / 2 + align_y
            case "bottom":
                return self.height - widget_height + align_y - self.padding
        return align_y + self.padding

    def _do_layout(self) -> None:
        """Position all child widgets that define anchor constraints."""

        super()._do_layout()
        for child in self._children:
            if isinstance(child, UIWidget) and child.anchor_constraint is not None:
                x_offset = self._calculate_x_offset(
                    child.width,
                    child.anchor_constraint.anchor_x,
                    child.anchor_constraint.align_x,
                )
                y_offset = self._calculate_y_offset(
                    child.height,
                    child.anchor_constraint.anchor_y,
                    child.anchor_constraint.align_y,
                )
                child.position = Vector2(x_offset, y_offset)
