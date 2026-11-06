import random
from abc import ABC
from enum import Enum, auto

import pyray

from engine import Node
from engine.observer import Subject


class KeyPressEvent(Enum):
    KEY_UP = auto()
    KEY_DOWN = auto()
    KEY_LEFT = auto()
    KEY_RIGHT = auto()


class InputComponent(Node, ABC):
    def __init__(
        self,
        name: str | None = None,
        parent: Node | None = None,
        children: list[Node] | None = None,
        enabled: bool = True,
        visible: bool = True,
    ) -> None:
        super().__init__(name, parent, children, enabled, visible)
        self.event_handler = Subject[KeyPressEvent]()


class PlayerKeyboardInputComponent(InputComponent):
    def _is_up_pressed(self) -> bool:
        return pyray.is_key_down(
            pyray.KeyboardKey.KEY_UP
        ) or pyray.is_gamepad_button_pressed(
            0, pyray.GamepadButton.GAMEPAD_BUTTON_LEFT_FACE_UP
        )

    def _is_down_pressed(self) -> bool:
        return pyray.is_key_down(
            pyray.KeyboardKey.KEY_DOWN
        ) or pyray.is_gamepad_button_pressed(
            0, pyray.GamepadButton.GAMEPAD_BUTTON_LEFT_FACE_DOWN
        )

    def _is_left_pressed(self) -> bool:
        return pyray.is_key_down(
            pyray.KeyboardKey.KEY_LEFT
        ) or pyray.is_gamepad_button_pressed(
            0, pyray.GamepadButton.GAMEPAD_BUTTON_LEFT_FACE_LEFT
        )

    def _is_right_pressed(self) -> bool:
        return pyray.is_key_down(
            pyray.KeyboardKey.KEY_RIGHT
        ) or pyray.is_gamepad_button_pressed(
            0, pyray.GamepadButton.GAMEPAD_BUTTON_LEFT_FACE_RIGHT
        )

    def _update(self, dt: float) -> None:
        assert self.parent is not None
        if self._is_up_pressed():
            self.event_handler.notify(self.parent, KeyPressEvent.KEY_UP)
        if self._is_down_pressed():
            self.event_handler.notify(self.parent, KeyPressEvent.KEY_DOWN)
        if self._is_left_pressed():
            self.event_handler.notify(self.parent, KeyPressEvent.KEY_LEFT)
        if self._is_right_pressed():
            self.event_handler.notify(self.parent, KeyPressEvent.KEY_RIGHT)


class AutomaticInputComponent(InputComponent):
    def __init__(
        self,
        name: str | None = None,
        parent: Node | None = None,
        children: list[Node] | None = None,
        enabled: bool = True,
        visible: bool = True,
    ) -> None:
        super().__init__(name, parent, children, enabled, visible)

    def _update(self, dt: float) -> None:
        assert self.parent is not None
        if random.random() < 0.001:
            new_direction = random.choice(
                (
                    KeyPressEvent.KEY_UP,
                    KeyPressEvent.KEY_DOWN,
                    KeyPressEvent.KEY_LEFT,
                    KeyPressEvent.KEY_RIGHT,
                )
            )
            self.event_handler.notify(self.parent, new_direction)
