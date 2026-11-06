from pydantic import BaseModel


class SpriteConfig(BaseModel):
    """Common sprite configuration.

    Attributes:
        size: Number of sprite sheet grid cells covered by the sprite.
    """

    size: int = 1


class StaticSpriteConfig(SpriteConfig):
    """Configuration for a sprite with one frame.

    Attributes:
        frame: Sprite sheet grid position for the frame.
    """

    frame: tuple[int, int]


class AnimatedSpriteConfig(SpriteConfig):
    """Configuration for a sprite with multiple animation frames.

    Attributes:
        frames: Sprite sheet grid positions used in playback order.
        frame_speed: Number of game frames between animation changes.
    """

    frames: tuple[tuple[int, int], ...]
    frame_speed: int
    loop: bool = True


class SpriteSheetConfig(BaseModel):
    """Configuration for loading a sprite sheet and its sprites.

    Attributes:
        file_name: Image file name relative to the resources directory.
        sprite_width: Width of one sprite grid cell in pixels.
        sprite_height: Height of one sprite grid cell in pixels.
        padding_x: Horizontal padding between sprite grid cells in pixels.
        padding_y: Vertical padding between sprite grid cells in pixels.
        sprites: Sprite definitions indexed by asset name.
    """

    file_name: str
    sprite_width: int
    sprite_height: int
    padding_x: int
    padding_y: int
    sprites: dict[str, StaticSpriteConfig | AnimatedSpriteConfig]


class AssetsConfig(BaseModel):
    """Configuration files that describe the game's asset groups.

    Attributes:
        entities_assets_config: File name for entity assets.
        maze_assets_config: File name for maze tile assets.
    """

    entities_assets_config: str
    maze_assets_config: str
