import math
from abc import ABC, abstractmethod

import pyray

from engine import Node2D, Sprite2D, Vector2


class CollisionObject2D(Node2D, ABC):
    """Base node for objects participating in collision resolution."""

    def __init__(self, name: str | None = None) -> None:
        """Initialize collision layer and mask values.

        Args:
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self.collision_layer: int = 0
        self.collision_mask: int = 0

    @abstractmethod
    def collide(self, with_object: CollisionObject2D) -> bool:
        """Return whether this object overlaps another object.

        Args:
            with_object: Other collision object to test.

        Returns:
            ``True`` when both objects overlap.
        """
        ...

    @abstractmethod
    def collide_with_motion(
        self,
        self_motion: Vector2,
        with_object: CollisionObject2D,
        object_motion: Vector2,
    ) -> bool:
        """Return whether objects would overlap after applying motion.

        Args:
            self_motion: Motion applied to this object.
            with_object: Other collision object to test.
            object_motion: Motion applied to the other object.

        Returns:
            ``True`` when the moved objects would overlap.
        """
        ...


class CollisionCircle2D(CollisionObject2D):
    """Circular collision object."""

    DEBUG_DRAW: bool = False

    def __init__(self, name: str | None = None) -> None:
        """Initialize a circle collision object.

        Args:
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self._radius = 0.0

    def fit_to_sprite(self, sprite: Sprite2D, scale: float = 1.0) -> None:
        """Size the circle from a sprite draw size.

        Args:
            sprite: Sprite used as the size reference.
            scale: Multiplier applied to the sprite-derived radius.
        """
        sprite_size = sprite.get_draw_size()
        self._radius = scale * max(sprite_size.x, sprite_size.y) / 2

    @property
    def radius(self) -> float:
        """Current world-scaled collision radius."""
        return (
            max(self.global_transform.scale.x, self.global_transform.scale.y)
            * self._radius
        )

    def collide(self, with_object: CollisionObject2D) -> bool:
        """Return whether this circle overlaps another collision object.

        Args:
            with_object: Other collision object to test.

        Returns:
            ``True`` when both circles overlap.
        """
        if isinstance(with_object, CollisionCircle2D):
            obj_position = self.global_transform.position
            with_obj_position = with_object.global_transform.position
            distance = math.hypot(
                obj_position.x - with_obj_position.x,
                obj_position.y - with_obj_position.y,
            )
            return distance < self.radius + with_object.radius
        return False

    def collide_with_motion(
        self,
        self_motion: Vector2,
        with_object: CollisionObject2D,
        object_motion: Vector2,
    ) -> bool:
        """Return whether this circle would overlap after applying motion.

        Args:
            self_motion: Motion applied to this circle.
            with_object: Other collision object to test.
            object_motion: Motion applied to the other object.

        Returns:
            ``True`` when the moved circles would overlap.
        """
        if isinstance(with_object, CollisionCircle2D):
            obj_position = self.global_transform.position + self_motion
            with_obj_position = with_object.global_transform.position + object_motion
            distance = math.hypot(
                obj_position.x - with_obj_position.x,
                obj_position.y - with_obj_position.y,
            )
            return distance < self.radius + with_object.radius
        return False

    def _on_draw(self) -> None:
        """Draw the debug outline when circle debug drawing is enabled."""
        position = self.global_transform.position
        if self.DEBUG_DRAW:
            pyray.draw_circle_lines(
                int(position.x), int(position.y), self.radius, pyray.BLUE
            )
