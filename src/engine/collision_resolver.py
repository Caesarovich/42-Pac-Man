import itertools
from abc import ABC, abstractmethod
from dataclasses import dataclass

from engine import Node, Tilemap
from engine.collision_object_2d import (
    CollisionObject2D,
)
from engine.observer import Subject
from pac_man.assets.maze_assets import MazeTileID


@dataclass
class ObjectCollisionEvent:
    """Event emitted when two collision objects overlap.

    Attributes:
        first: First collision object involved in the overlap.
        second: Second collision object involved in the overlap.
    """

    first: CollisionObject2D
    second: CollisionObject2D


@dataclass
class TileCollisionEvent:
    """Event emitted when a collision object overlaps a tile collider.

    Attributes:
        obj: Collision object that touched the tile.
        tile_layer: Name of the tilemap layer that was touched.
        tile_id: Tile identifier found at the collision coordinates.
    """

    obj: CollisionObject2D
    tile_layer: str
    tile_id: int


class CollisionResolver[E](Node, ABC):
    """Base node for collision resolvers that publish collision events.

    Collision resolvers keep an explicit registry of collision objects and emit
    typed events through ``event_handler`` during their update hook.
    """

    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        """Initialize the resolver.

        Args:
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self.event_handler = Subject[E]()
        self.collision_objects: list[CollisionObject2D] = []

    def register(self, collision_object: CollisionObject2D) -> None:
        """Register a collision object for future collision checks.

        Args:
            collision_object: Object to include in the resolver registry.
        """
        self.collision_objects.append(collision_object)

    def recursive_register(self, node: Node | None) -> None:
        """Register every collision object contained under a node.

        Args:
            node: Root node to inspect. ``None`` is ignored.
        """
        if node is None:
            return

        if isinstance(node, CollisionObject2D):
            self.register(node)

        for child in node.children:
            self.recursive_register(child)

    def remove(self, collision_object: CollisionObject2D) -> None:
        """Remove a collision object from the resolver registry.

        Args:
            collision_object: Object to remove.
        """
        self.collision_objects = [
            obj for obj in self.collision_objects if obj is not collision_object
        ]

    @abstractmethod
    def _resolve_collisions(self) -> None:
        """Resolve collisions for one frame."""

    def _on_update(self, dt: float) -> None:
        """Run collision resolution during the node update hook.

        Args:
            dt: Frame delta time in seconds. It is unused because collision
                resolution is based on the current transforms.
        """
        self._resolve_collisions()


class ObjectCollisionResolver(CollisionResolver[ObjectCollisionEvent]):
    """Resolver that checks registered collision objects against each other."""

    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        """Initialize an object collision resolver.

        Args:
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self.collision_objects: list[CollisionObject2D] = []

    def _resolve_collisions(self) -> None:
        """Resolve object-to-object collisions for one frame."""
        self._resolve_objects_collision()

    def _resolve_objects_collision(self) -> None:
        """Notify observers for every enabled object pair that overlaps."""
        for first, second in itertools.combinations(self.collision_objects, 2):
            if first.parent is None or second.parent is None:
                continue
            if not (first.enabled and second.enabled):
                continue
            if not (first.parent.enabled and second.parent.enabled):
                continue
            if not (
                first.collision_mask & second.collision_layer
                or second.collision_mask & first.collision_layer
            ):
                continue
            if first.collide(second):
                self.event_handler.notify(None, ObjectCollisionEvent(first, second))


class TileMapCollisionResolver(CollisionResolver[TileCollisionEvent]):
    """Resolver that checks registered objects against tilemap colliders."""

    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        """Initialize a tilemap collision resolver.

        Args:
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self.tile_map: Tilemap | None = None

    def _resolve_collisions(self) -> None:
        """Resolve object-to-tile collisions for one frame."""
        self._resolve_tile_collisions()

    def _resolve_tile_collisions(self) -> None:
        """Notify observers when enabled objects overlap collidable tiles."""
        if self.tile_map is None:
            return
        for obj in self.collision_objects:
            if obj.parent is None:
                continue
            if not obj.enabled:
                continue
            if not obj.parent.enabled:
                continue
            for (
                layer_name,
                tile_collider,
            ) in self.tile_map.collision_layers.items():
                if obj.collision_mask & tile_collider.collision_layer:
                    tile_x, tile_y = self.tile_map.get_current_tile(
                        obj.global_transform.position
                    )
                    collision = tile_collider.get_tile(tile_x, tile_y)
                    if collision:
                        tile_id = self.tile_map.get_tile(layer_name, tile_x, tile_y)
                        self.event_handler.notify(
                            None, TileCollisionEvent(obj, layer_name, tile_id)
                        )
                        tile_collider.set_tile(tile_x, tile_y, False)
                        self.tile_map.set_tile(
                            layer_name, tile_x, tile_y, MazeTileID.EMPTY
                        )
