from collections.abc import Iterator
from enum import Enum, IntEnum, auto

import pyray

from engine import SpriteFrame, SpriteSheet
from pac_man.config.resources_config import (
    SpriteSheetConfig,
    StaticSpriteConfig,
)
from pac_man.mazegen_utils.maze_directions import (
    CornerDirection,
    WallDirection,
    WallOrientation,
)


class MazeConsumables(Enum):
    """Consumable sprite variants displayed inside maze paths."""

    SUPER_PAC_GUM = auto()
    PAC_GUM = auto()


class CornerType(Enum):
    """Inner corner variants used when resolving maze cell joins."""

    CELL_CORNER = auto()
    WALL_CORNER = auto()


class MazeTileID(IntEnum):
    """Tile IDs used to identify maze tiles in the tilemap."""

    OUTER_CELL_WALL_TOP = 0
    OUTER_CELL_WALL_BOTTOM = 1
    OUTER_CELL_WALL_LEFT = 2
    OUTER_CELL_WALL_RIGHT = 3
    OUTER_CELL_CORNER_HORIZONTAL_TOP_LEFT = 4
    OUTER_CELL_CORNER_HORIZONTAL_TOP_RIGHT = 5
    OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_LEFT = 6
    OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_RIGHT = 7
    OUTER_CELL_CORNER_VERTICAL_TOP_LEFT = 8
    OUTER_CELL_CORNER_VERTICAL_TOP_RIGHT = 9
    OUTER_CELL_CORNER_VERTICAL_BOTTOM_LEFT = 10
    OUTER_CELL_CORNER_VERTICAL_BOTTOM_RIGHT = 11
    INNER_CELL_TOP = 12
    INNER_CELL_BOTTOM = 13
    INNER_CELL_LEFT = 14
    INNER_CELL_RIGHT = 15
    INNER_CELL_CORNER_CELL_TOP_LEFT = 16
    INNER_CELL_CORNER_CELL_TOP_RIGHT = 17
    INNER_CELL_CORNER_CELL_BOTTOM_LEFT = 18
    INNER_CELL_CORNER_CELL_BOTTOM_RIGHT = 19
    INNER_CELL_CORNER_WALL_TOP_LEFT = 20
    INNER_CELL_CORNER_WALL_TOP_RIGHT = 21
    INNER_CELL_CORNER_WALL_BOTTOM_LEFT = 22
    INNER_CELL_CORNER_WALL_BOTTOM_RIGHT = 23
    PAC_GUM = 24
    SUPER_PAC_GUM = 25
    EMPTY = 26
    MAZE_CORNER_TOP_LEFT = 27
    MAZE_CORNER_TOP_RIGHT = 28
    MAZE_CORNER_BOTTOM_LEFT = 29
    MAZE_CORNER_BOTTOM_RIGHT = 30

    def is_wall(self) -> bool:
        return self not in (self.PAC_GUM, self.SUPER_PAC_GUM, self.EMPTY)

    def is_pac_gum(self) -> bool:
        return self is self.PAC_GUM

    def is_super_pac_gum(self) -> bool:
        return self is self.SUPER_PAC_GUM

    def is_empty(self) -> bool:
        return self is self.EMPTY


class MazeTileset:
    """Tileset for maze tiles and sprite-frame lookup helpers."""

    padding: int = 1

    def __init__(self, atlas: pyray.Texture, tile_size: int) -> None:
        self.atlas = atlas
        self.tile_size = tile_size
        self._tile_rects: dict[int, pyray.Rectangle] = {}
        self._tile_sprites: dict[int, SpriteFrame] = {}
        self._maze_walls: dict[WallDirection, MazeTileID] = {}
        self._maze_corners: dict[CornerDirection, MazeTileID] = {}
        self._outer_cell_corners: dict[
            WallOrientation, dict[CornerDirection, MazeTileID]
        ] = {}
        self._inner_cell_walls: dict[WallDirection, MazeTileID] = {}
        self._inner_cell_corners: dict[
            CornerType, dict[CornerDirection, MazeTileID]
        ] = {}
        self._consumables: dict[MazeConsumables, MazeTileID] = {}

    @classmethod
    def from_sprite_sheet(
        cls,
        sprite_sheet: SpriteSheet,
        sprite_sheet_config: SpriteSheetConfig,
    ) -> MazeTileset:
        """Create a MazeTileset from the maze sprite sheet."""

        def _get_sprite_frame(sprite_name: str) -> SpriteFrame:
            sprite_config = sprite_sheet_config.sprites[sprite_name]
            assert isinstance(sprite_config, StaticSpriteConfig)
            return sprite_sheet.get_frame_at_position(sprite_config.frame)

        def _copy_region(sprite: SpriteFrame) -> pyray.Rectangle:
            return pyray.Rectangle(
                sprite.region.x,
                sprite.region.y,
                sprite.region.width,
                sprite.region.height,
            )

        tile_name_pairs: tuple[tuple[MazeTileID, str], ...] = (
            (MazeTileID.OUTER_CELL_WALL_TOP, "maze_wall_top"),
            (MazeTileID.OUTER_CELL_WALL_BOTTOM, "maze_wall_bottom"),
            (MazeTileID.OUTER_CELL_WALL_LEFT, "maze_wall_left"),
            (MazeTileID.OUTER_CELL_WALL_RIGHT, "maze_wall_right"),
            (
                MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_LEFT,
                "outer_cell_corner_horizontal_top_left",
            ),
            (
                MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_RIGHT,
                "outer_cell_corner_horizontal_top_right",
            ),
            (
                MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_LEFT,
                "outer_cell_corner_horizontal_bottom_left",
            ),
            (
                MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_RIGHT,
                "outer_cell_corner_horizontal_bottom_right",
            ),
            (
                MazeTileID.OUTER_CELL_CORNER_VERTICAL_TOP_LEFT,
                "outer_cell_corner_vertical_top_left",
            ),
            (
                MazeTileID.OUTER_CELL_CORNER_VERTICAL_TOP_RIGHT,
                "outer_cell_corner_vertical_top_right",
            ),
            (
                MazeTileID.OUTER_CELL_CORNER_VERTICAL_BOTTOM_LEFT,
                "outer_cell_corner_vertical_bottom_left",
            ),
            (
                MazeTileID.OUTER_CELL_CORNER_VERTICAL_BOTTOM_RIGHT,
                "outer_cell_corner_vertical_bottom_right",
            ),
            (MazeTileID.INNER_CELL_TOP, "inner_cell_top"),
            (MazeTileID.INNER_CELL_BOTTOM, "inner_cell_bottom"),
            (MazeTileID.INNER_CELL_LEFT, "inner_cell_left"),
            (MazeTileID.INNER_CELL_RIGHT, "inner_cell_right"),
            (
                MazeTileID.INNER_CELL_CORNER_CELL_TOP_LEFT,
                "inner_cell_corner_cell_top_left",
            ),
            (
                MazeTileID.INNER_CELL_CORNER_CELL_TOP_RIGHT,
                "inner_cell_corner_cell_top_right",
            ),
            (
                MazeTileID.INNER_CELL_CORNER_CELL_BOTTOM_LEFT,
                "inner_cell_corner_cell_bottom_left",
            ),
            (
                MazeTileID.INNER_CELL_CORNER_CELL_BOTTOM_RIGHT,
                "inner_cell_corner_cell_bottom_right",
            ),
            (
                MazeTileID.INNER_CELL_CORNER_WALL_TOP_LEFT,
                "inner_cell_corner_wall_top_left",
            ),
            (
                MazeTileID.INNER_CELL_CORNER_WALL_TOP_RIGHT,
                "inner_cell_corner_wall_top_right",
            ),
            (
                MazeTileID.INNER_CELL_CORNER_WALL_BOTTOM_LEFT,
                "inner_cell_corner_wall_bottom_left",
            ),
            (
                MazeTileID.INNER_CELL_CORNER_WALL_BOTTOM_RIGHT,
                "inner_cell_corner_wall_bottom_right",
            ),
            (MazeTileID.PAC_GUM, "pac_gum"),
            (MazeTileID.SUPER_PAC_GUM, "super_pac_gum"),
            (MazeTileID.MAZE_CORNER_TOP_LEFT, "maze_corner_top_left"),
            (MazeTileID.MAZE_CORNER_TOP_RIGHT, "maze_corner_top_right"),
            (MazeTileID.MAZE_CORNER_BOTTOM_LEFT, "maze_corner_bottom_left"),
            (MazeTileID.MAZE_CORNER_BOTTOM_RIGHT, "maze_corner_bottom_right"),
            (MazeTileID.EMPTY, "empty"),
        )
        frames_by_tile: dict[MazeTileID, SpriteFrame] = {
            tile_id: _get_sprite_frame(sprite_name)
            for tile_id, sprite_name in tile_name_pairs
        }

        tileset = cls(
            atlas=sprite_sheet.texture,
            tile_size=sprite_sheet_config.sprite_width,
        )
        tileset._tile_sprites = {
            int(tile_id): frame for tile_id, frame in frames_by_tile.items()
        }
        tileset._tile_rects = {
            int(tile_id): _copy_region(frame)
            for tile_id, frame in frames_by_tile.items()
        }

        tileset._maze_walls = {
            WallDirection.TOP: MazeTileID.OUTER_CELL_WALL_TOP,
            WallDirection.BOTTOM: MazeTileID.OUTER_CELL_WALL_BOTTOM,
            WallDirection.LEFT: MazeTileID.OUTER_CELL_WALL_LEFT,
            WallDirection.RIGHT: MazeTileID.OUTER_CELL_WALL_RIGHT,
        }
        tileset._maze_corners = {
            CornerDirection.TOP_LEFT: (MazeTileID.MAZE_CORNER_TOP_LEFT),
            CornerDirection.TOP_RIGHT: (MazeTileID.MAZE_CORNER_TOP_RIGHT),
            CornerDirection.BOTTOM_LEFT: (MazeTileID.MAZE_CORNER_BOTTOM_LEFT),
            CornerDirection.BOTTOM_RIGHT: (MazeTileID.MAZE_CORNER_BOTTOM_RIGHT),
        }
        tileset._outer_cell_corners = {
            WallOrientation.HORIZONTAL: {
                CornerDirection.TOP_LEFT: (
                    MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_LEFT
                ),
                CornerDirection.TOP_RIGHT: (
                    MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_RIGHT
                ),
                CornerDirection.BOTTOM_LEFT: (
                    MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_LEFT
                ),
                CornerDirection.BOTTOM_RIGHT: (
                    MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_RIGHT
                ),
            },
            WallOrientation.VERTICAL: {
                CornerDirection.TOP_LEFT: (
                    MazeTileID.OUTER_CELL_CORNER_VERTICAL_TOP_LEFT
                ),
                CornerDirection.TOP_RIGHT: (
                    MazeTileID.OUTER_CELL_CORNER_VERTICAL_TOP_RIGHT
                ),
                CornerDirection.BOTTOM_LEFT: (
                    MazeTileID.OUTER_CELL_CORNER_VERTICAL_BOTTOM_LEFT
                ),
                CornerDirection.BOTTOM_RIGHT: (
                    MazeTileID.OUTER_CELL_CORNER_VERTICAL_BOTTOM_RIGHT
                ),
            },
        }
        tileset._inner_cell_walls = {
            WallDirection.TOP: MazeTileID.INNER_CELL_TOP,
            WallDirection.BOTTOM: MazeTileID.INNER_CELL_BOTTOM,
            WallDirection.LEFT: MazeTileID.INNER_CELL_LEFT,
            WallDirection.RIGHT: MazeTileID.INNER_CELL_RIGHT,
        }
        tileset._inner_cell_corners = {
            CornerType.CELL_CORNER: {
                CornerDirection.TOP_LEFT: (MazeTileID.INNER_CELL_CORNER_CELL_TOP_LEFT),
                CornerDirection.TOP_RIGHT: (
                    MazeTileID.INNER_CELL_CORNER_CELL_TOP_RIGHT
                ),
                CornerDirection.BOTTOM_LEFT: (
                    MazeTileID.INNER_CELL_CORNER_CELL_BOTTOM_LEFT
                ),
                CornerDirection.BOTTOM_RIGHT: (
                    MazeTileID.INNER_CELL_CORNER_CELL_BOTTOM_RIGHT
                ),
            },
            CornerType.WALL_CORNER: {
                CornerDirection.TOP_LEFT: (MazeTileID.INNER_CELL_CORNER_WALL_TOP_LEFT),
                CornerDirection.TOP_RIGHT: (
                    MazeTileID.INNER_CELL_CORNER_WALL_TOP_RIGHT
                ),
                CornerDirection.BOTTOM_LEFT: (
                    MazeTileID.INNER_CELL_CORNER_WALL_BOTTOM_LEFT
                ),
                CornerDirection.BOTTOM_RIGHT: (
                    MazeTileID.INNER_CELL_CORNER_WALL_BOTTOM_RIGHT
                ),
            },
        }
        tileset._consumables = {
            MazeConsumables.PAC_GUM: MazeTileID.PAC_GUM,
            MazeConsumables.SUPER_PAC_GUM: MazeTileID.SUPER_PAC_GUM,
        }
        return tileset

    def get_sprite_frame(self, tile_id: MazeTileID | int) -> SpriteFrame:
        try:
            return self._tile_sprites[int(tile_id)]
        except KeyError as exc:
            raise ValueError(f"Missing sprite frame for tile id: {tile_id}") from exc

    def get_outer_wall(self, direction: WallDirection) -> MazeTileID:
        return self._maze_walls[direction]

    def get_outer_corner(self, direction: CornerDirection) -> MazeTileID:
        return self._maze_corners[direction]

    def get_outer_cell_corner(
        self,
        orientation: WallOrientation,
        direction: CornerDirection,
    ) -> MazeTileID:
        return self._outer_cell_corners[orientation][direction]

    def get_inner_wall(self, direction: WallDirection) -> MazeTileID:
        return self._inner_cell_walls[direction]

    def get_inner_corner(
        self,
        corner_type: CornerType,
        direction: CornerDirection,
    ) -> MazeTileID:
        return self._inner_cell_corners[corner_type][direction]

    def get_consumable(self, consumable: MazeConsumables) -> MazeTileID:
        return self._consumables[consumable]

    def __iter__(self) -> Iterator[SpriteFrame]:
        yield from self._tile_sprites.values()

    def get_tile(self, tile_id: int) -> pyray.Rectangle:
        """Get the tile rectangle for a given tile ID.

        Args:
            tile_id: The ID of the tile to retrieve.
        Returns:
            A pyray.Rectangle with the tile's atlas position and size.
        """
        try:
            maze_tile = MazeTileID(tile_id)
        except ValueError as exc:
            raise ValueError(f"Unknown maze tile id: {tile_id}") from exc

        try:
            return self._tile_rects[int(maze_tile)]
        except KeyError as exc:
            raise ValueError(f"Missing rectangle for maze tile id: {tile_id}") from exc
