from collections.abc import Callable
from typing import Literal

import pyray

from engine import Vector2
from engine.ui.ui_label import UILabel
from engine.ui.ui_widget import UIWidget


class UITextInput(UIWidget):
    """Text input widget that lets users type a string.

    Args:
        name: Optional node name.
        x: Initial x position in pixels.
        y: Initial y position in pixels.
        width: Initial widget width in pixels.
        height: Initial widget height in pixels.
        font_size: Font size used by the text label.
        text_color: Text color.
        align: Horizontal text alignment relative to the widget origin.
        fn_on_enter: Function called with the text when enter is pressed.
        fn_on_change: Function called with the text when it changes.
        debug: Whether to draw the widget bounds.
    """

    def __init__(
        self,
        name: str | None = None,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 100,
        font_size: int = 12,
        text_color: pyray.Color = pyray.WHITE,
        align: Literal["left", "right", "center"] = "left",
        fn_on_enter: Callable[[str], None] = print,
        fn_on_change: Callable[[str], str] = lambda x: x,
        max_length: int | None = None,
        debug: bool = False,
    ) -> None:
        super().__init__(name, x, y, width, height, debug)
        self.font_size = font_size
        self.text_color = text_color
        self.align = align
        self.fn_on_enter = fn_on_enter
        self.fn_on_change = fn_on_change
        self._max_length = max_length
        self._text = ""
        self._label = UILabel(
            text=self._text,
            font_size=self.font_size,
            text_color=self.text_color,
            align=self.align,
            debug=self.debug,
        )
        self.add(self._label)
        if self.align == "center":
            self._label.position = Vector2(self.width / 2, 0)
        elif self.align == "right":
            self._label.position = Vector2(self.width, 0)

    def _update(self, dt: float) -> None:
        self._handle_keyboard_input()
        super()._update(dt)

    def _is_uppercase(self) -> bool:
        if pyray.is_key_down(pyray.KeyboardKey.KEY_LEFT_SHIFT):
            return True
        return bool(pyray.is_key_down(pyray.KeyboardKey.KEY_RIGHT_SHIFT))

    def _handle_keyboard_input(self) -> None:
        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_BACKSPACE):
            self._text = self._text[:-1]
        if pyray.is_key_pressed_repeat(pyray.KeyboardKey.KEY_BACKSPACE):
            self._text = self._text[:-1]
        elif pyray.is_key_pressed(pyray.KeyboardKey.KEY_ENTER):
            self.fn_on_enter(self._text)
        else:
            while key := pyray.get_char_pressed():
                char = chr(key)
                if self._is_uppercase():
                    char = char.upper()
                else:
                    char = char.lower()
                self._text += char
                self._text = self.fn_on_change(self._text)
                if self._max_length is not None:
                    self._text = self._text[: self._max_length]
        self._label.text = self._text
