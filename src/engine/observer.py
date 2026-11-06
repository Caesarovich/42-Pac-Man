from typing import Protocol

from engine import Node


class Observer[E](Protocol):
    """Protocol for objects that receive subject notifications."""

    def on_notify(self, entity: Node | None, event: E) -> None:
        """Handle a notification emitted by a subject.

        Args:
            entity: Optional event source or related node.
            event: Event payload.
        """
        ...


class Subject[E]:
    """Simple typed observer list."""

    def __init__(self) -> None:
        """Initialize the subject with no observers."""
        self.observers: list[Observer[E]] = []

    def add_observer(self, observer: Observer[E]) -> None:
        """Subscribe an observer.

        Args:
            observer: Observer to notify.
        """
        self.observers.append(observer)

    def remove_observer(self, observer: Observer[E]) -> None:
        """Unsubscribe an observer.

        Args:
            observer: Observer to remove.
        """
        self.observers = [obs for obs in self.observers if obs is not observer]

    def notify(self, entity: Node | None, event: E) -> None:
        """Notify all subscribed observers.

        Args:
            entity: Optional event source or related node.
            event: Event payload sent to observers.
        """
        for observer in self.observers:
            observer.on_notify(entity, event)
