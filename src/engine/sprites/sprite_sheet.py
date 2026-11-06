from dataclasses import dataclass, field
from pathlib import Path

import pyray

from engine.sprites.sprite2d import Sprite2D


@dataclass
class SpriteFrame:
    texture: pyray.Texture
    region: pyray.Rectangle

    @classmethod
    def from_file(cls, file_path: Path) -> SpriteFrame:
        """
        Create a SpriteFrame from a texture file.
        """
        texture = pyray.load_texture(str(file_path))
        region = pyray.Rectangle(0, 0, texture.width, texture.height)
        return cls(texture=texture, region=region)

    def to_sprite2d(self, name: str = "SpriteFrame") -> Sprite2D:
        """
        Convert the SpriteFrame to a Sprite2D instance.
        """
        return Sprite2D(name=name, texture=self.texture, region=self.region)


@dataclass
class SpriteSheet:
    texture: pyray.Texture = field()
    frame_size: pyray.Vector2 = field()
    gap_size: pyray.Vector2 = field(default_factory=lambda: pyray.Vector2(0, 0))

    @classmethod
    def from_file(
        cls,
        file_path: Path,
        frame_width: int,
        frame_height: int,
        gap_width: int = 0,
        gap_height: int = 0,
    ) -> SpriteSheet:
        """
        Create a SpriteSheet from a texture file and frame dimensions.
        """
        texture = pyray.load_texture(str(file_path))
        frame_size = pyray.Vector2(frame_width, frame_height)
        gap_size = pyray.Vector2(gap_width, gap_height)
        return cls(texture=texture, frame_size=frame_size, gap_size=gap_size)

    def get_frame_count(self) -> int:
        """
        Calculate the total number of frames in the sprite sheet
        based on the texture size and frame size.
        """
        return self._get_frames_per_row() * self._get_frames_per_col()

    def get_frame_at_position(self, position: tuple[int, int]) -> SpriteFrame:
        """
        Get the frame at a specific position in the sprite sheet.
        The position is given in terms of frame coordinates (not pixels).
        """
        assert 0 <= position[0] < self._get_frames_per_row(), (
            "Frame X position out of range"
        )
        assert 0 <= position[1] < self._get_frames_per_col(), (
            "Frame Y position out of range"
        )

        region = pyray.Rectangle(
            position[0] * self.frame_size.x + position[0] * self.gap_size.x,
            position[1] * self.frame_size.y + position[1] * self.gap_size.y,
            self.frame_size.x,
            self.frame_size.y,
        )
        return SpriteFrame(texture=self.texture, region=region)

    def get_frame_at_index(self, index: int) -> SpriteFrame:
        """
        Get the frame at a specific index in the sprite sheet.
        The index is calculated in a row-major order.
        """
        assert 0 <= index < self.get_frame_count(), "Frame index out of range"

        frames_per_row = self._get_frames_per_row()
        row = index // frames_per_row
        col = index % frames_per_row

        region = pyray.Rectangle(
            col * self.frame_size.x + col * self.gap_size.x,
            row * self.frame_size.y + row * self.gap_size.y,
            self.frame_size.x,
            self.frame_size.y,
        )

        return SpriteFrame(texture=self.texture, region=region)

    # PRIVATE METHODS
    def _get_frames_per_row(self) -> int:
        """
        Get the number of frames per row in the sprite sheet.
        """
        return int(self.texture.width / (self.frame_size.x + self.gap_size.x))

    def _get_frames_per_col(self) -> int:
        """
        Get the number of frames per column in the sprite sheet.
        """
        return int(self.texture.height / (self.frame_size.y + self.gap_size.y))
