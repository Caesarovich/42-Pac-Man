from typing import TypeVar

from engine import Node, Node2D, Sprite2D
from engine.character_state_machine import (
    CharacterState,
    CharacterStateMachine,
)
from engine.collision_object_2d import CollisionObject2D
from engine.input_component import (
    InputComponent,
)
from engine.movement_component import MovementComponent

N = TypeVar("N", bound=Node)


class CharacterBody2D(Node2D):
    def __init__(
        self,
        input_component: InputComponent | None = None,
        movement_component: MovementComponent | None = None,
        sprite: Sprite2D | None = None,
        collision_box: CollisionObject2D | None = None,
        state_machine: CharacterStateMachine[CharacterState] | None = None,
        name: str | None = None,
    ) -> None:
        super().__init__(name)
        if input_component and movement_component:
            input_component.event_handler.add_observer(movement_component)

        self._input_component = input_component
        self._movement_component = movement_component
        self._sprite = sprite
        self._collision_box = collision_box
        self._state_machine = state_machine

    def _on_enter_tree(self) -> None:
        if self._input_component is not None:
            self.add_child(self._input_component)

        if self._movement_component is not None:
            self.add_child(self._movement_component)

        if self._sprite is not None:
            self.add_child(self._sprite)

        if self._collision_box is not None:
            self.add_child(self._collision_box)

        if self._state_machine is not None:
            self.add_child(self._state_machine)

    @property
    def sprite(self) -> Sprite2D | None:
        return self._sprite

    @sprite.setter
    def sprite(self, sprite: Sprite2D | None) -> None:
        if self._sprite is not None:
            self.remove_child(self._sprite)
        if sprite is not None:
            self.add_child(sprite)
            self._sprite = sprite

    @property
    def movement_component(self) -> MovementComponent | None:
        return self._movement_component

    @movement_component.setter
    def movement_component(self, movement_component: MovementComponent | None) -> None:
        if self._movement_component is not None:
            self.remove_child(self._movement_component)
            if self._input_component:
                self._input_component.event_handler.remove_observer(
                    self._movement_component
                )

        self._movement_component = movement_component
        if self._movement_component is not None:
            self.add_child(self._movement_component)
            if self._input_component:
                self._input_component.event_handler.add_observer(
                    self._movement_component
                )

    @property
    def state_machine(self) -> CharacterStateMachine[CharacterState] | None:
        return self._state_machine

    @property
    def collision_box(self) -> CollisionObject2D | None:
        return self._collision_box

    def get_component(self, node_cls: type[N]) -> N | None:
        for node in self.children:
            if isinstance(node, node_cls):
                return node
        return None
