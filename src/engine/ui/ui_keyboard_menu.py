"""Keyboard-controlled menu widget."""

from collections.abc import Callable
from typing import Literal

import pyray

from engine import Vector2
from engine.ui.ui_box_layout import UIBoxLayout
from engine.ui.ui_label import UILabel
from engine.ui.ui_widget import UIWidget


class UIKeyboardMenu(UIBoxLayout):
    """Menu that lets users select string items with the keyboard.

    Args:
        name: Optional node name.
        x: Initial x position in pixels.
        y: Initial y position in pixels.
        width: Initial menu width in pixels.
        height: Initial menu height in pixels.
        vertical: Whether to stack items vertically.
        align_content: Horizontal alignment for menu item labels.
        padding: Space around and between menu item labels.
        menu_items: Labels to show as selectable menu entries.
        font_size: Font size used by generated labels.
        selection_indicator: Optional widget displayed next to selection.
        callback_fct: Function called with the selected label on enter.
        debug: Whether to draw widget bounds.
    """

    def __init__(
        self,
        name: str | None = None,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        vertical: bool = True,
        align_content: Literal["left", "right", "center"] = "left",
        padding: float = 10,
        menu_items: list[str] | None = None,
        font_size: int = 12,
        selection_indicator: UIWidget | None = None,
        callback_fct: Callable[[str], None] = print,
        debug: bool = False,
    ) -> None:
        super().__init__(
            name, x, y, width, height, vertical, align_content, padding, debug
        )
        self._menu_items: list[str] = menu_items if menu_items is not None else []
        self.selected = 0
        self.selection_indicator: UIWidget
        if selection_indicator is None:
            self.selection_indicator = UILabel(
                text=">", font_size=font_size, debug=self.debug
            )
        else:
            self.selection_indicator = selection_indicator
        self.selection_indicator.set_size(font_size, font_size)
        self.selection_indicator.stretch_content()
        self.selection_indicator.fit_content()
        self.selection_indicator.position -= Vector2(
            self.selection_indicator.width + self.padding, 0
        )
        for i, item in enumerate(self._menu_items):
            new_label = UILabel(
                name=item,
                text=item,
                height=20,
                font_size=font_size,
                debug=self.debug,
            )
            if i == self.selected:
                new_label.add(self.selection_indicator)
            new_label.fit_content()
            self.add(new_label)
        self.callback_fct = callback_fct

    def _update(self, dt: float) -> None:
        self._handle_key_presses()
        super()._update(dt)

    def _is_up_pressed(self) -> bool:
        return (
            pyray.is_key_pressed(pyray.KeyboardKey.KEY_UP)
            or pyray.is_key_pressed(pyray.KeyboardKey.KEY_LEFT)
            or pyray.is_gamepad_button_pressed(
                0, pyray.GamepadButton.GAMEPAD_BUTTON_LEFT_FACE_UP
            )
        )

    def _is_down_pressed(self) -> bool:
        return (
            pyray.is_key_pressed(pyray.KeyboardKey.KEY_DOWN)
            or pyray.is_key_pressed(pyray.KeyboardKey.KEY_RIGHT)
            or pyray.is_gamepad_button_pressed(
                0, pyray.GamepadButton.GAMEPAD_BUTTON_LEFT_FACE_DOWN
            )
        )

    def _is_select_pressed(self) -> bool:
        return pyray.is_key_pressed(
            pyray.KeyboardKey.KEY_ENTER
        ) or pyray.is_gamepad_button_pressed(
            0, pyray.GamepadButton.GAMEPAD_BUTTON_RIGHT_FACE_DOWN
        )

    def _handle_key_presses(self) -> None:
        """Handle keyboard input for menu navigation and selection."""
        if not self._menu_items:
            return
        update_selected = False
        if self._is_up_pressed():
            self.selected = (self.selected - 1) % len(self._menu_items)
            update_selected = True
        if self._is_down_pressed():
            self.selected = (self.selected + 1) % len(self._menu_items)
            update_selected = True
        if update_selected:
            selected_node = self.find_child(self._menu_items[self.selected])
            if selected_node is not None:
                self.selection_indicator.reparent(selected_node)
        if self._is_select_pressed():
            self.callback_fct(self._menu_items[self.selected])
