import math
from enum import Enum, auto
from typing import TYPE_CHECKING

import pyray

from engine import Node2D, Vector2

if TYPE_CHECKING:
    from engine import SpriteFrame


class Sprite2D(Node2D):
    class FitMode(Enum):
        """
        Fit mode for scaling sprites.
        """

        NONE = auto()
        STRETCH = auto()
        CONTAIN = auto()
        COVER = auto()

    def __init__(
        self,
        name: str = "Sprite2D",
        texture: pyray.Texture | None = None,
        region: pyray.Rectangle | None = None,
    ) -> None:
        super().__init__(name=name)

        self._texture = texture
        self._region = region

        self._width: float | None = None
        self._height: float | None = None
        self._fit_mode = Sprite2D.FitMode.NONE

        self._tint = pyray.WHITE

        self._draw_size = pyray.Vector2(0.0, 0.0)
        self._dest_rect = pyray.Rectangle(0, 0, 0, 0)

    @classmethod
    def from_sprite_frame(
        cls, sprite_frame: SpriteFrame, name: str = "Sprite2D"
    ) -> Sprite2D:
        """Create a sprite from a sprite-frame object.

        Args:
            sprite_frame: Texture and region used by the sprite.
            name: Optional node name used in the scene tree.

        Returns:
            Sprite configured with the frame texture and region.
        """
        return cls(name, sprite_frame.texture, sprite_frame.region)

    # PROPERTIES
    @property
    def texture(self) -> pyray.Texture | None:
        """
        The texture of the sprite.
        """
        return self._texture

    @texture.setter
    def texture(self, value: pyray.Texture | None) -> None:
        self._texture = value
        self._update_dest_rect()

    @property
    def region(self) -> pyray.Rectangle | None:
        """
        The region of the texture to draw.

        If None, the entire texture will be drawn.
        """
        return (
            self._region
            if self._region is not None
            else (
                pyray.Rectangle(0, 0, self.texture.width, self.texture.height)
                if self.texture is not None
                else None
            )
        )

    @region.setter
    def region(self, value: pyray.Rectangle | None) -> None:
        self._region = value
        self._update_dest_rect()

    @property
    def tint(self) -> pyray.Color:
        """
        The tint color to apply to the sprite when drawing.
        """
        return self._tint

    @tint.setter
    def tint(self, value: pyray.Color) -> None:
        self._tint = value

    @property
    def fit_mode(self) -> FitMode:
        """
        The fit mode for scaling the sprite.
        """
        return self._fit_mode

    @property
    def width(self) -> float | None:
        """
        The width of the sprite.
        If None, the natural width of the sprite will be used.
        """
        return self._width

    @property
    def height(self) -> float | None:
        """
        The height of the sprite.
        If None, the natural height of the sprite will be used.
        """
        return self._height

    # PUBLIC METHODS
    def set_size(self, width: float, height: float) -> None:
        """
        Set the size of the sprite.
        This will stretch the sprite to fit the specified width and height.
        """
        self._width = width
        self._height = height
        self._fit_mode = Sprite2D.FitMode.STRETCH
        self._update_dest_rect()

    def set_width(self, width: float, keep_aspect: bool = True) -> None:
        """
        Set the width of the sprite.
        If keep_aspect is True, the height will
        be adjusted to maintain the aspect ratio of the texture.
        Otherwise, the height will remain unchanged and
        the sprite will be stretched to fit the new width.
        """
        self._width = width
        if keep_aspect:
            self._height = None
            self._fit_mode = Sprite2D.FitMode.CONTAIN
        else:
            self._fit_mode = Sprite2D.FitMode.STRETCH
        self._update_dest_rect()

    def set_height(self, height: float, keep_aspect: bool = True) -> None:
        """
        Set the height of the sprite.
        If keep_aspect is True, the width will
        be adjusted to maintain the aspect ratio of the texture.
        Otherwise, the width will remain unchanged and
        the sprite will be stretched to fit the new height.
        """
        self._height = height
        if keep_aspect:
            self._width = None
            self._fit_mode = Sprite2D.FitMode.CONTAIN
        else:
            self._fit_mode = Sprite2D.FitMode.STRETCH
        self._update_dest_rect()

    def fit_into(
        self,
        width: float,
        height: float,
        mode: Sprite2D.FitMode = FitMode.CONTAIN,
    ) -> None:
        """
        Fit the sprite into the specified width and height
        using the specified fit mode.
        """
        self._width = width
        self._height = height
        self._fit_mode = mode
        self._update_dest_rect()

    def reset_size(self) -> None:
        """
        Reset the size of the sprite to its original size.
        The natural size of the sprite is determined by the size of the texture
        or the specified region of the texture.
        """
        self._width = None
        self._height = None
        self._fit_mode = Sprite2D.FitMode.NONE
        self._update_dest_rect()

    def get_draw_size(self) -> pyray.Vector2:
        """
        Get the size that the sprite should be drawn at,
        based on the fit mode and the specified width and height.
        """
        src_size = self._get_source_size()

        if src_size.x == 0 or src_size.y == 0:
            return pyray.Vector2(0.0, 0.0)
        if self.fit_mode == Sprite2D.FitMode.NONE or (
            self.width is None and self.height is None
        ):
            return pyray.vector2_multiply(
                src_size, self.global_transform.scale.to_pyray()
            )
        if self.fit_mode == Sprite2D.FitMode.STRETCH:
            return self._get_stretch_size()
        if self.fit_mode == Sprite2D.FitMode.CONTAIN:
            return self._get_contain_size()
        if self.fit_mode == Sprite2D.FitMode.COVER:
            return self._get_cover_size()
        return src_size

    def get_destination_rectangle(self) -> pyray.Rectangle:
        """
        Get the destination rectangle for drawing the sprite,
        based on the draw size and the global position of the sprite.
        """
        transform = self.global_transform
        return pyray.Rectangle(
            transform.position.x,
            transform.position.y,
            self._draw_size.x,
            self._draw_size.y,
        )

    def duplicate(self) -> Sprite2D:
        """
        Create a duplicate of this sprite with the same properties.
        """
        new_sprite = Sprite2D(
            name=self.name + "_copy" if self.name else "Sprite2D_copy",
            texture=self.texture,
            region=self.region,
        )
        new_sprite._width = self._width
        new_sprite._height = self._height
        new_sprite._fit_mode = self._fit_mode
        new_sprite._tint = self._tint
        return new_sprite

    # PRIVATE METHODS
    def _get_source_size(self) -> pyray.Vector2:
        if self.region is not None:
            return pyray.Vector2(abs(self.region.width), abs(self.region.height))
        if self.texture is not None:
            return pyray.Vector2(float(self.texture.width), float(self.texture.height))
        return pyray.Vector2(0.0, 0.0)

    def _get_stretch_size(self) -> pyray.Vector2:
        src_size = self._get_source_size()

        if src_size.x == 0 or src_size.y == 0:
            return pyray.Vector2(0.0, 0.0)

        return (
            Vector2(
                self.width if self.width is not None else src_size.x,
                self.height if self.height is not None else src_size.y,
            )
            * self.global_transform.scale
        ).to_pyray()

    def _get_cover_size(self) -> pyray.Vector2:
        src_size = self._get_source_size()

        if src_size.x == 0 or src_size.y == 0:
            return pyray.Vector2(0.0, 0.0)

        if self.width is not None and self.height is None:
            aspect = src_size.x / src_size.y
            return pyray.Vector2(self.width, self.width / aspect)

        if self.height is not None and self.width is None:
            aspect = src_size.x / src_size.y
            return pyray.Vector2(self.height * aspect, self.height)

        box_w = self.width if self.width is not None else src_size.x
        box_h = self.height if self.height is not None else src_size.y
        box_aspect = box_w / box_h

        aspect = src_size.x / src_size.y

        size = Vector2(0.0, 0.0)
        if aspect > box_aspect:
            size = Vector2(box_h * aspect, box_h)
        else:
            size = Vector2(box_w, box_w / aspect)

        return (size * self.global_transform.scale).to_pyray()

    def _get_contain_size(self) -> pyray.Vector2:
        src_size = self._get_source_size()

        if src_size.x == 0 or src_size.y == 0:
            return pyray.Vector2(0.0, 0.0)

        if self.width is not None and self.height is None:
            aspect = src_size.x / src_size.y
            return pyray.Vector2(self.width, self.width / aspect)

        if self.height is not None and self.width is None:
            aspect = src_size.x / src_size.y
            return pyray.Vector2(self.height * aspect, self.height)

        box_w = self.width if self.width is not None else src_size.x
        box_h = self.height if self.height is not None else src_size.y
        box_aspect = box_w / box_h

        aspect = src_size.x / src_size.y

        if aspect > box_aspect:
            size = pyray.Vector2(box_w, box_w / aspect)
        else:
            size = pyray.Vector2(box_h * aspect, box_h)

        return (Vector2(size.x, size.y) * self.global_transform.scale).to_pyray()

    def _update_dest_rect(self) -> None:
        self._draw_size = self.get_draw_size()
        self._dest_rect = self.get_destination_rectangle()

    def _update_global_transform(self) -> None:
        super()._update_global_transform()
        self._update_dest_rect()

    def _draw(self) -> None:
        if self.visible:
            self._draw_texture()
        super()._draw()

    def _draw_texture(self) -> None:
        if self.texture is None or self.region is None:
            return

        transform = self.global_transform

        dest_rect = self._dest_rect

        pyray.draw_texture_pro(
            self.texture,
            self.region,
            dest_rect,
            transform.origin.to_pyray(),
            math.degrees(transform.rotation),
            self.tint,
        )
