from abc import ABC
from typing import TYPE_CHECKING, cast

from engine import Node

if TYPE_CHECKING:
    from engine import CharacterBody2D

from pac_man.signals.pacman_events import PacManEvent


class CharacterState(ABC, Node):
    """Base class for states owned by a character state machine."""

    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        """Initialize an unbound character state.

        Args:
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self.character: CharacterBody2D | None = None
        self.state_machine: CharacterStateMachine[CharacterState] | None = None

    def init(self) -> None:
        """Bind the state to its parent state machine and character."""
        from engine import CharacterBody2D

        if isinstance(self.parent, CharacterStateMachine):
            self.state_machine = self.parent
        if isinstance(self.state_machine, CharacterStateMachine) and isinstance(
            self.state_machine.parent, CharacterBody2D
        ):
            self.character = self.state_machine.parent

    def on_enter(self) -> None:
        """Hook called when the state becomes current."""

    def on_exit(self) -> None:
        """Hook called when the state is no longer current."""

    def handle_event(self, entity: Node | None, event: PacManEvent) -> None:
        """Handle a gameplay event while the state is active.

        Args:
            entity: Event source or related entity.
            event: Gameplay event to handle.
        """


class CharacterStateMachine[S: CharacterState](Node):
    """Node that owns character states and updates only the active state."""

    def __init__(
        self,
        name: str | None = None,
        parent: Node | None = None,
        children: list[Node] | None = None,
        enabled: bool = True,
        visible: bool = True,
    ) -> None:
        """Initialize the state machine.

        Args:
            name: Optional node name used in the scene tree.
            parent: Optional parent node.
            children: Optional initial child nodes.
            enabled: Whether the state machine updates with the scene tree.
            visible: Whether the state machine is visible in the scene tree.
        """
        super().__init__(name, parent, children, enabled, visible)
        self.states: list[S] = []
        self.current_state: S | None = None

    def _on_enter_tree(self) -> None:
        """Discover child states and enter the first state."""
        self.states = [
            cast(S, child)
            for child in self.children
            if isinstance(child, CharacterState)
        ]
        for state in self.states:
            state.init()
        if self.states:
            self.current_state = self.states[0]
            self.current_state.on_enter()

    def set_state(self, state_class: type[S]) -> None:
        """Set the current state by class without running transitions.

        Args:
            state_class: State class to activate when present.
        """
        state = self.get_state(state_class)
        if state is not None:
            self.current_state = state

    def add_state(self, state: S) -> None:
        """Add a state as a child of this state machine.

        Args:
            state: State instance to add.
        """
        self.add_child(state)

    def change_to(self, new_state: S) -> None:
        """Transition from the current state to another registered state.

        Args:
            new_state: State instance to make current.
        """
        for state in self.states:
            if state is new_state:
                if self.current_state:
                    self.current_state.on_exit()
                self.current_state = state
                self.current_state.on_enter()

    def on_notify(self, entity: Node | None, event: PacManEvent) -> None:
        """Forward an event to the current state.

        Args:
            entity: Event source or related entity.
            event: Gameplay event to forward.
        """
        if self.current_state:
            self.current_state.handle_event(entity, event)

    def _update(self, dt: float) -> None:
        """Update only the current state.

        Args:
            dt: Frame delta time in seconds.
        """
        # the state machine unlike any other node updates only the
        # current state, this is why update is overriden
        if self.current_state:
            self.current_state._update(dt)

    def get_state(self, state_class: type[S]) -> S | None:
        """Return the first registered state matching a class.

        Args:
            state_class: State class to look up.

        Returns:
            The matching state instance, or ``None`` when absent.
        """
        for state in self.states:
            if isinstance(state, state_class):
                return state
        return None
