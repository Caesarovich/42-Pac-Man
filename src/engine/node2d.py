import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pyray

from engine import Node, RootNode, Vector2

if TYPE_CHECKING:
    from engine.scene2d import Scene2D


@dataclass
class Transform2D:
    """
    Represents a 2D transformation,
    including position, rotation, scale, and origin.

    Note: Rotation is in radians not degrees
    """

    position: Vector2
    rotation: float
    scale: Vector2
    origin: Vector2

    @classmethod
    def identity(cls) -> Transform2D:
        return cls(
            position=Vector2(0, 0),
            rotation=0.0,
            scale=Vector2(1, 1),
            origin=Vector2(0, 0),
        )

    def combine(self, local: Transform2D) -> Transform2D:
        scaled_local_pos = local.position * self.scale
        rotated_local_pos = scaled_local_pos.rotated(self.rotation)
        world_position = self.position + rotated_local_pos

        world_rotation = self.rotation + local.rotation
        world_scale = self.scale * local.scale

        return Transform2D(
            position=world_position,
            rotation=world_rotation,
            scale=world_scale,
            origin=local.origin,
        )


class Node2D(Node):
    DEBUG_DRAW: bool = False

    # PROPERTIES
    @property
    def position(self) -> Vector2:
        """
        The position of the node relative to its parent.
        """
        return self._local_transform.position

    @position.setter
    def position(self, value: Vector2) -> None:
        self._local_transform.position = value
        self._mark_transform_dirty()

    @property
    def rotation(self) -> float:
        """
        The rotation of the node relative to its parent.
        """
        return self._local_transform.rotation

    @rotation.setter
    def rotation(self, value: float) -> None:
        self._local_transform.rotation = value
        self._mark_transform_dirty()

    @property
    def scale(self) -> Vector2:
        """
        The scale of the node relative to its parent.
        """
        return self._local_transform.scale

    @scale.setter
    def scale(self, value: Vector2) -> None:
        self._local_transform.scale = value
        self._mark_transform_dirty()

    @property
    def origin(self) -> Vector2:
        """
        The origin point for rotation and scaling,
        relative to the node's position.
        """
        return self._local_transform.origin

    @origin.setter
    def origin(self, value: Vector2) -> None:
        self._local_transform.origin = value
        self._mark_transform_dirty()

    @property
    def local_transform(self) -> Transform2D:
        """
        The local transform of the node.
        """
        return self._local_transform

    @local_transform.setter
    def local_transform(self, value: Transform2D) -> None:
        self._local_transform = value
        self._mark_transform_dirty()

    @property
    def global_transform(self) -> Transform2D:
        """
        The global transform of the node,
        combining its local transform with the transforms of its ancestors.
        """
        if self._transform_dirty:
            self._update_global_transform()
        return self._global_transform

    # PUBLIC METHODS
    def rotate(self, deg: float) -> None:
        """
        Rotates this Node2D's tranform using degrees instead of radians.
        """
        self.rotation = self.rotation + math.radians(deg)

    def get_parent_transform(self) -> Transform2D:
        """
        Returns the global transform of the parent Node2D.
        """
        if isinstance(self.parent, Node2D):
            return self.parent.global_transform
        return Transform2D.identity()

    def convert_global_to_local(self, global_position: Vector2) -> Vector2:
        """
        Converts a global position to a local position relative to this Node2D.
        """
        parent_transform = self.get_parent_transform()
        inverse_rotation = -parent_transform.rotation
        inverse_scale = Vector2(
            1 / parent_transform.scale.x, 1 / parent_transform.scale.y
        )

        translated_position = global_position - parent_transform.position

        rotated_position = translated_position.rotated(inverse_rotation)

        local_position = Vector2(
            rotated_position.x * inverse_scale.x,
            rotated_position.y * inverse_scale.y,
        )

        return local_position

    def add_child(self, child: Node) -> None:
        super().add_child(child)
        if isinstance(child, Node2D):
            child._mark_transform_dirty()

    def remove_child(self, child: Node) -> None:
        super().remove_child(child)
        if isinstance(child, Node2D):
            child._mark_transform_dirty()

    # PRIVATE METHODS
    def __init__(
        self,
        name: str | None = None,
        parent: Node | None = None,
        children: list[Node] | None = None,
        enabled: bool = True,
        visible: bool = True,
    ) -> None:
        Node.__init__(
            self,
            name=name,
            parent=parent,
            children=children,
            enabled=enabled,
            visible=visible,
        )
        self._local_transform = Transform2D.identity()
        self._global_transform = Transform2D.identity()
        self._transform_dirty = True

    def _draw(self) -> None:
        super()._draw()

        if self.DEBUG_DRAW:
            self._draw_gizmo()

    def _update_global_transform(self) -> None:
        parent_transform = self.get_parent_transform()
        self._global_transform = parent_transform.combine(self._local_transform)
        self._mark_transform_dirty()
        self._transform_dirty = False

    def _mark_transform_dirty(self) -> None:
        if self._transform_dirty:
            return

        self._transform_dirty = True

        for child in self.children:
            if isinstance(child, Node2D):
                child._mark_transform_dirty()

    def _draw_gizmo(self) -> None:
        transform = self.global_transform
        pyray.draw_circle(
            int(transform.position.x),
            int(transform.position.y),
            5,
            pyray.GREEN,
        )

        pyray.draw_line(
            int(transform.position.x),
            int(transform.position.y),
            int(transform.position.x + 40 * math.cos(transform.rotation)),
            int(transform.position.y + 40 * math.sin(transform.rotation)),
            pyray.BLUE,
        )

        pyray.draw_line(
            int(transform.position.x),
            int(transform.position.y),
            int(transform.position.x + 40 * math.cos(transform.rotation + math.pi / 2)),
            int(transform.position.y + 40 * math.sin(transform.rotation + math.pi / 2)),
            pyray.RED,
        )


class RootNode2D(Node2D, RootNode):
    def __init__(self, scene: Scene2D, name: str | None = None) -> None:
        Node2D.__init__(self, name=name)
        self._is_in_active_tree = True
        self._is_ready = True
        self._scene = scene
