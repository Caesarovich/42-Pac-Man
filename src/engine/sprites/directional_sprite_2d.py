from collections.abc import Iterator, Mapping
from enum import IntEnum

import pyray

from engine.sprites.sprite2d import Sprite2D


class DirectionalSprite2D(Sprite2D):
    """Drawable sprite that delegates to a sprite for the current direction.

    Attributes:
        width: Maximum directional sprite width in pixels.
        height: Maximum directional sprite height in pixels.
    """

    class SpriteDirection(IntEnum):
        """Cardinal directions ordered clockwise for directional sprites."""

        RIGHT = 0
        DOWN = 1
        LEFT = 2
        UP = 3

        def __iter__(self) -> Iterator[DirectionalSprite2D.SpriteDirection]:
            return iter((self.RIGHT, self.DOWN, self.LEFT, self.UP))

    def __init__(
        self,
        sprites: Mapping[SpriteDirection, Sprite2D],
        name: str = "DirectionalSprite",
        current_direction: SpriteDirection = SpriteDirection.RIGHT,
    ) -> None:
        """Create a directional sprite group.

        Args:
            sprites: Drawable sprites indexed by direction.
            current_direction: Initial direction to draw.
        """
        super().__init__(name=name)

        self._sprites = sprites

        for sprite in self._sprites.values():
            self.add_child(sprite)

        self._current_direction = current_direction
        self.current_direction = current_direction

    # PROPERTIES
    @property
    def current_direction(self) -> SpriteDirection:
        """The current direction used for drawing."""
        return self._current_direction

    @current_direction.setter
    def current_direction(self, value: SpriteDirection) -> None:
        self._current_direction = value

        for sprite in self._sprites.values():
            sprite.visible = False

        self._sprites[self._current_direction].visible = True

    @property
    def current_sprite(self) -> Sprite2D:
        """The current sprite used for drawing."""
        return self._sprites[self.current_direction]

    def get_draw_size(self) -> pyray.Vector2:
        """Return the draw size of the currently selected sprite.

        Returns:
            Current sprite draw size.
        """
        return self.current_sprite.get_draw_size()

    # PUBLIC METHODS
    def duplicate(self) -> DirectionalSprite2D:
        """
        Create a duplicate of this directional sprite with the same properties.
        """
        duplicated_sprites = {
            dir: sprite.duplicate() for dir, sprite in self._sprites.items()
        }
        return DirectionalSprite2D(
            sprites=duplicated_sprites,
            name=self.name + "_copy" if self.name else "DirectionalSprite2D_copy",
            current_direction=self._current_direction,
        )

    def turn(self, offset: int) -> None:
        """Rotate the current direction by an enum offset.

        Args:
            offset: Signed number of quarter-turns to apply.
        """
        self.current_direction = DirectionalSprite2D.SpriteDirection(
            (self._current_direction + offset) % 4
        )

    def turn_right(self) -> None:
        """Rotate the current direction one quarter-turn to the right."""
        self.turn(1)

    def turn_left(self) -> None:
        """Rotate the current direction one quarter-turn to the left."""
        self.turn(-1)

    def _update_global_transform(self) -> None:
        super()._update_global_transform()

        for sprite in self._sprites.values():
            sprite.origin = self.origin
