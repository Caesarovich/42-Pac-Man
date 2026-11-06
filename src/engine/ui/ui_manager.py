"""Manager node that owns and updates UI widgets."""

from engine import Node
from engine.ui.ui_layout import UILayout
from engine.ui.ui_widget import UIWidget


class UIManager(Node):
    """Root node for UI widgets in a scene.

    Args:
        name: Optional node name.
        parent: Optional parent node.
        children: Optional initial child nodes.
        enabled: Whether this manager receives updates.
        visible: Whether this manager draws its children.
    """

    def __init__(
        self,
        name: str | None = None,
        parent: Node | None = None,
        children: list[Node] | None = None,
        enabled: bool = True,
        visible: bool = True,
    ) -> None:
        super().__init__(name, parent, children, enabled, visible)
        self.widgets: list[UIWidget] = []

    def add(self, widget: UIWidget) -> None:
        """Register and attach a widget.

        Args:
            widget: Widget to add to the manager.
        """

        self.add_child(widget)
        self.widgets.append(widget)

    def clear(self) -> None:
        """Remove all managed widgets from the scene tree."""

        for child in self.children:
            self.remove_child(child)
        self.widgets.clear()

    def _update(self, dt: float) -> None:
        for widget in self.widgets:
            if isinstance(widget, UILayout):
                widget.do_layout()

        super()._update(dt)
