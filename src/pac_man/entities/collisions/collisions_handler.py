import logging

from engine import (
    Node,
    ObjectCollisionEvent,
    Observer,
    Subject,
    TileCollisionEvent,
)
from pac_man.entities.collisions.pac_man_collisions_layers import (
    CollisionLayer,
)
from pac_man.entities.ghost import Ghost
from pac_man.signals.pacman_events import PacManEvent

logger = logging.getLogger(__name__)


class PacManCollisionHandler(Node):
    """Translate low-level collision events into Pac-Man gameplay events."""

    def __init__(self, name: str | None = None) -> None:
        """Initialize object and tile gameplay event subjects.

        Args:
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self.objects_event_handler: Subject[PacManEvent] = Subject()
        self.tiles_event_handler: Subject[PacManEvent] = Subject()

    def add_observer(self, observer: Observer[PacManEvent]) -> None:
        """Subscribe an observer to both object and tile gameplay events.

        Args:
            observer: Observer to notify when gameplay collisions occur.
        """
        self.objects_event_handler.add_observer(observer)
        self.tiles_event_handler.add_observer(observer)

    def _get_ghost(self, obj1: Node, obj2: Node) -> Ghost | None:
        """Return the ghost parent involved in a collision pair.

        Args:
            obj1: First collision node.
            obj2: Second collision node.

        Returns:
            The ghost parent when one object belongs to a ghost, otherwise
            ``None``.
        """
        if isinstance(obj1.parent, Ghost):
            return obj1.parent
        if isinstance(obj2.parent, Ghost):
            return obj2.parent
        return None

    def on_notify(
        self,
        entity: Node | None,
        event: ObjectCollisionEvent | TileCollisionEvent,
    ) -> None:
        """Dispatch engine collision events to the matching handler.

        Args:
            entity: Event source. It is unused for collision resolver events.
            event: Collision event emitted by a resolver.
        """
        if isinstance(event, ObjectCollisionEvent):
            self.handle_object_collision(entity, event)
        elif isinstance(event, TileCollisionEvent):
            self.handle_tile_collision(entity, event)

    def handle_object_collision(
        self, entity: Node | None, event: ObjectCollisionEvent
    ) -> None:
        """Handle collisions between Pac-Man and ghost collision objects.

        Args:
            entity: Event source. It is unused for object collisions.
            event: Object collision event to translate.
        """
        layers = {event.first.collision_layer, event.second.collision_layer}
        if layers == {CollisionLayer.PACMAN, CollisionLayer.CHASE_GHOST}:
            self.objects_event_handler.notify(
                self, PacManEvent.PACMAN_COLLIDES_WITH_GHOST
            )
            logger.debug("Pacman collides with ghost")
        elif layers == {
            CollisionLayer.PACMAN,
            CollisionLayer.FRIGHTENED_GHOSTS,
        }:
            ghost = self._get_ghost(event.first, event.second)
            self.objects_event_handler.notify(
                ghost, PacManEvent.PACMAN_COLLIDES_WITH_FRIGHTENED_GHOST
            )
            logger.debug("Pacman collides with frightened ghost")
        elif layers == {CollisionLayer.PACMAN, CollisionLayer.BOOSTS}:
            boost = event.first
            if event.second.collision_layer == CollisionLayer.BOOSTS:
                boost = event.second
            assert boost.parent is not None, "Boost parent is None"
            boost.parent.queue_for_deletion()
            self.objects_event_handler.notify(
                boost, PacManEvent.PACMAN_COLLIDES_WITH_BOOST
            )
            logger.debug("Pacman collides with boost")

    def handle_tile_collision(
        self, entity: Node | None, event: TileCollisionEvent
    ) -> None:
        """Handle collisions between Pac-Man and tilemap collectibles.

        Args:
            entity: Event source. It is unused for tile collisions.
            event: Tile collision event to translate.
        """
        if event.tile_layer == "super_pac_gums":
            self.tiles_event_handler.notify(
                event.obj.parent,
                PacManEvent.PACMAN_COLLIDES_WITH_SUPER_PAC_GUM,
            )
            logger.debug("Pacman collides with Super Pac-Gum")
        if event.tile_layer == "pac_gums":
            self.tiles_event_handler.notify(
                event.obj.parent,
                PacManEvent.PACMAN_COLLIDES_WITH_PAC_GUM,
            )
            logger.debug("Pacman collides with Pac-Gum")
