from dataclasses import dataclass
from typing import cast

import pytest

from pac_man.assets.maze_assets import (
    CornerType,
    MazeConsumables,
    MazeTileID,
    MazeTileset,
)
from pac_man.exceptions import PacManException
from pac_man.maze.maze_tile_resolver import MazeTileResolver
from pac_man.maze.maze_tilemap import Maze as MazeTilemap
from pac_man.mazegen_utils.maze_directions import (
    ALL_WALLS,
    CornerDirection,
    WallDirection,
    WallOrientation,
)
from pac_man.mazegen_utils.maze_wrapper import MazeWrapper


@dataclass(frozen=True)
class FakeMazeTileset:
    atlas: object = object()
    tile_size: int = 8

    def get_outer_wall(self, direction: WallDirection) -> MazeTileID:
        top = MazeTileID.OUTER_CELL_WALL_TOP
        bottom = MazeTileID.OUTER_CELL_WALL_BOTTOM
        left = MazeTileID.OUTER_CELL_WALL_LEFT
        right = MazeTileID.OUTER_CELL_WALL_RIGHT
        return {
            WallDirection.TOP: top,
            WallDirection.BOTTOM: bottom,
            WallDirection.LEFT: left,
            WallDirection.RIGHT: right,
        }[direction]

    def get_outer_corner(self, direction: CornerDirection) -> MazeTileID:
        top_left = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_LEFT
        top_right = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_RIGHT
        bottom_left = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_LEFT
        bottom_right = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_RIGHT
        return {
            CornerDirection.TOP_LEFT: top_left,
            CornerDirection.TOP_RIGHT: top_right,
            CornerDirection.BOTTOM_LEFT: bottom_left,
            CornerDirection.BOTTOM_RIGHT: bottom_right,
        }[direction]

    def get_outer_cell_corner(
        self,
        orientation: WallOrientation,
        direction: CornerDirection,
    ) -> MazeTileID:
        horizontal_top_left = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_LEFT
        horizontal_top_right = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_RIGHT
        horizontal_bottom_left = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_LEFT
        horizontal_bottom_right = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_RIGHT
        vertical_top_left = MazeTileID.OUTER_CELL_CORNER_VERTICAL_TOP_LEFT
        vertical_top_right = MazeTileID.OUTER_CELL_CORNER_VERTICAL_TOP_RIGHT
        vertical_bottom_left = MazeTileID.OUTER_CELL_CORNER_VERTICAL_BOTTOM_LEFT
        vertical_bottom_right = MazeTileID.OUTER_CELL_CORNER_VERTICAL_BOTTOM_RIGHT
        return {
            WallOrientation.HORIZONTAL: {
                CornerDirection.TOP_LEFT: horizontal_top_left,
                CornerDirection.TOP_RIGHT: horizontal_top_right,
                CornerDirection.BOTTOM_LEFT: horizontal_bottom_left,
                CornerDirection.BOTTOM_RIGHT: horizontal_bottom_right,
            },
            WallOrientation.VERTICAL: {
                CornerDirection.TOP_LEFT: vertical_top_left,
                CornerDirection.TOP_RIGHT: vertical_top_right,
                CornerDirection.BOTTOM_LEFT: vertical_bottom_left,
                CornerDirection.BOTTOM_RIGHT: vertical_bottom_right,
            },
        }[orientation][direction]

    def get_inner_wall(self, direction: WallDirection) -> MazeTileID:
        top = MazeTileID.INNER_CELL_TOP
        bottom = MazeTileID.INNER_CELL_BOTTOM
        left = MazeTileID.INNER_CELL_LEFT
        right = MazeTileID.INNER_CELL_RIGHT
        return {
            WallDirection.TOP: top,
            WallDirection.BOTTOM: bottom,
            WallDirection.LEFT: left,
            WallDirection.RIGHT: right,
        }[direction]

    def get_inner_corner(
        self, corner_type: CornerType, direction: CornerDirection
    ) -> MazeTileID:
        cell_top_left = MazeTileID.INNER_CELL_CORNER_CELL_TOP_LEFT
        cell_top_right = MazeTileID.INNER_CELL_CORNER_CELL_TOP_RIGHT
        cell_bottom_left = MazeTileID.INNER_CELL_CORNER_CELL_BOTTOM_LEFT
        cell_bottom_right = MazeTileID.INNER_CELL_CORNER_CELL_BOTTOM_RIGHT
        wall_top_left = MazeTileID.INNER_CELL_CORNER_WALL_TOP_LEFT
        wall_top_right = MazeTileID.INNER_CELL_CORNER_WALL_TOP_RIGHT
        wall_bottom_left = MazeTileID.INNER_CELL_CORNER_WALL_BOTTOM_LEFT
        wall_bottom_right = MazeTileID.INNER_CELL_CORNER_WALL_BOTTOM_RIGHT
        return {
            CornerType.CELL_CORNER: {
                CornerDirection.TOP_LEFT: cell_top_left,
                CornerDirection.TOP_RIGHT: cell_top_right,
                CornerDirection.BOTTOM_LEFT: cell_bottom_left,
                CornerDirection.BOTTOM_RIGHT: cell_bottom_right,
            },
            CornerType.WALL_CORNER: {
                CornerDirection.TOP_LEFT: wall_top_left,
                CornerDirection.TOP_RIGHT: wall_top_right,
                CornerDirection.BOTTOM_LEFT: wall_bottom_left,
                CornerDirection.BOTTOM_RIGHT: wall_bottom_right,
            },
        }[corner_type][direction]

    def get_consumable(self, consumable: MazeConsumables) -> MazeTileID:
        return {
            MazeConsumables.SUPER_PAC_GUM: MazeTileID.SUPER_PAC_GUM,
            MazeConsumables.PAC_GUM: MazeTileID.PAC_GUM,
        }[consumable]


@pytest.fixture
def maze_tileset() -> MazeTileset:
    return cast(MazeTileset, FakeMazeTileset())


@pytest.mark.parametrize(
    ("maze", "valid"),
    [
        ([], False),
        ([10], False),
        ([10, 11, 12], False),
        ([[]], False),
        ([[15]], True),
        ([[16]], False),
        ([[-1]], False),
        ([["12"]], False),
        ([[12, 12], [10, 11]], True),
        ([[12, 12], [11]], False),
    ],
)
def test_maze_validation(maze: list[list[int]], valid: bool) -> None:
    if not valid:
        with pytest.raises(PacManException):
            MazeWrapper(maze)
    else:
        MazeWrapper(maze)


@pytest.mark.parametrize(
    ("x", "y", "direction"),
    [
        (1, 0, WallDirection.TOP),
        (0, 1, WallDirection.LEFT),
        (1, 2, WallDirection.BOTTOM),
        (2, 1, WallDirection.RIGHT),
    ],
)
def test_maze_wrapper_detects_outer_walls(
    x: int, y: int, direction: WallDirection
) -> None:
    maze = MazeWrapper([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    assert maze.is_wall_outer_wall(x, y, direction)


@pytest.mark.parametrize(
    ("x", "y", "direction"),
    [
        (1, 1, WallDirection.TOP),
        (1, 1, WallDirection.LEFT),
        (1, 1, WallDirection.BOTTOM),
        (1, 1, WallDirection.RIGHT),
    ],
)
def test_maze_wrapper_detects_inner_walls(
    x: int, y: int, direction: WallDirection
) -> None:
    maze = MazeWrapper([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    assert not maze.is_wall_outer_wall(x, y, direction)


@pytest.mark.parametrize(
    ("x", "y", "expected"),
    [(0, 0, True), (2, 0, True), (0, 2, True), (2, 2, True), (1, 1, False)],
)
def test_maze_wrapper_detects_maze_corners(x: int, y: int, expected: bool) -> None:
    maze = MazeWrapper([[0, 0, 0], [0, 0, 0], [0, 0, 0]])

    assert maze.is_cell_maze_corner(x, y) is expected


def test_maze_wrapper_get_cell_spec_supports_relative_lookup() -> None:
    maze = MazeWrapper([[0, 1, 2], [3, 4, 5], [6, 7, 8]])

    assert maze.get_cell_spec(1, 0, relative_to=(1, 1)).value == 5


def test_maze_tile_resolver_uses_no_center_tile_for_closed_cell(
    maze_tileset: MazeTileset,
) -> None:
    resolver = MazeTileResolver(
        MazeWrapper([[0, 0, 0], [0, ALL_WALLS, 0], [0, 0, 0]]),
        maze_tileset,
    )

    assert resolver.get_tile_ids(1, 1)[1][1] is None


def test_maze_tile_resolver_uses_super_pac_gum_for_corner_cell_center(
    maze_tileset: MazeTileset,
) -> None:
    resolver = MazeTileResolver(MazeWrapper([[0, 0], [0, 0]]), maze_tileset)

    assert resolver.get_tile_ids(0, 0)[1][1] is MazeTileID.SUPER_PAC_GUM


def test_maze_tile_resolver_uses_pac_gum_for_open_inner_cell_center(
    maze_tileset: MazeTileset,
) -> None:
    resolver = MazeTileResolver(
        MazeWrapper([[0, 0, 0], [0, 0, 0], [0, 0, 0]]),
        maze_tileset,
    )

    assert resolver.get_tile_ids(1, 1)[1][1] is MazeTileID.PAC_GUM


def test_maze_tile_resolver_uses_outer_wall_tile_on_border(
    maze_tileset: MazeTileset,
) -> None:
    resolver = MazeTileResolver(
        MazeWrapper([[0, 0, 0], [0, 0, 0], [0, 0, 0]]),
        maze_tileset,
    )

    assert resolver.get_tile_ids(1, 0)[0][1] is MazeTileID.OUTER_CELL_WALL_TOP


def test_maze_tile_resolver_uses_inner_wall_tile_for_cell_wall(
    maze_tileset: MazeTileset,
) -> None:
    resolver = MazeTileResolver(
        MazeWrapper([[0, 0, 0], [0, WallDirection.RIGHT, 0], [0, 0, 0]]),
        maze_tileset,
    )

    assert resolver.get_tile_ids(1, 1)[1][2] is MazeTileID.INNER_CELL_RIGHT


def test_maze_tile_resolver_uses_pac_gum_when_cell_wall_is_missing(
    maze_tileset: MazeTileset,
) -> None:
    resolver = MazeTileResolver(
        MazeWrapper([[0, 0, 0], [0, 0, 0], [0, 0, 0]]),
        maze_tileset,
    )

    assert resolver.get_tile_ids(1, 1)[1][2] is MazeTileID.PAC_GUM


def test_maze_tile_resolver_uses_outer_corner_tile_on_maze_corner(
    maze_tileset: MazeTileset,
) -> None:
    resolver = MazeTileResolver(MazeWrapper([[0, 0], [0, 0]]), maze_tileset)

    assert (
        resolver.get_tile_ids(0, 0)[0][0]
        is MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_LEFT
    )


def test_maze_tile_resolver_uses_cell_corner_for_two_inner_walls(
    maze_tileset: MazeTileset,
) -> None:
    resolver = MazeTileResolver(
        MazeWrapper(
            [
                [0, 0, 0],
                [0, WallDirection.TOP | WallDirection.LEFT, 0],
                [0, 0, 0],
            ]
        ),
        maze_tileset,
    )

    assert (
        resolver.get_tile_ids(1, 1)[0][0] is MazeTileID.INNER_CELL_CORNER_CELL_TOP_LEFT
    )


def test_maze_tile_resolver_uses_wall_corner_for_neighboring_wall(
    maze_tileset: MazeTileset,
) -> None:
    resolver = MazeTileResolver(
        MazeWrapper(
            [
                [0, WallDirection.LEFT, 0],
                [0, 0, 0],
                [0, 0, 0],
            ]
        ),
        maze_tileset,
    )

    assert (
        resolver.get_tile_ids(1, 1)[0][0] is MazeTileID.INNER_CELL_CORNER_WALL_TOP_LEFT
    )


def test_maze_tilemap_expands_each_cell_into_three_by_three_block(
    monkeypatch: pytest.MonkeyPatch,
    maze_tileset: MazeTileset,
) -> None:
    outer_tl = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_LEFT
    outer_tr = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_RIGHT
    outer_bl = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_LEFT
    outer_br = MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_RIGHT
    inner_tl = MazeTileID.INNER_CELL_CORNER_WALL_TOP_LEFT
    inner_tr = MazeTileID.INNER_CELL_CORNER_WALL_TOP_RIGHT
    inner_bl = MazeTileID.INNER_CELL_CORNER_WALL_BOTTOM_LEFT
    inner_br = MazeTileID.INNER_CELL_CORNER_WALL_BOTTOM_RIGHT
    blocks: dict[tuple[int, int], list[list[MazeTileID | None]]] = {
        (0, 0): [
            [outer_tl, MazeTileID.OUTER_CELL_WALL_TOP, outer_tr],
            [
                MazeTileID.OUTER_CELL_WALL_LEFT,
                None,
                MazeTileID.OUTER_CELL_WALL_RIGHT,
            ],
            [outer_bl, MazeTileID.OUTER_CELL_WALL_BOTTOM, outer_br],
        ],
        (1, 0): [
            [outer_tl, MazeTileID.INNER_CELL_TOP, outer_tr],
            [
                MazeTileID.INNER_CELL_LEFT,
                MazeTileID.PAC_GUM,
                MazeTileID.INNER_CELL_RIGHT,
            ],
            [outer_bl, MazeTileID.INNER_CELL_BOTTOM, outer_br],
        ],
        (0, 1): [
            [outer_tl, MazeTileID.INNER_CELL_TOP, outer_tr],
            [
                MazeTileID.INNER_CELL_LEFT,
                MazeTileID.PAC_GUM,
                MazeTileID.INNER_CELL_RIGHT,
            ],
            [outer_bl, MazeTileID.INNER_CELL_BOTTOM, outer_br],
        ],
        (1, 1): [
            [inner_tl, MazeTileID.INNER_CELL_TOP, inner_tr],
            [
                MazeTileID.INNER_CELL_LEFT,
                MazeTileID.EMPTY,
                MazeTileID.INNER_CELL_RIGHT,
            ],
            [inner_bl, MazeTileID.INNER_CELL_BOTTOM, inner_br],
        ],
    }

    def get_sprites(
        self: MazeTileResolver, x: int, y: int
    ) -> list[list[MazeTileID | None]]:
        return blocks[(x, y)]

    monkeypatch.setattr(MazeTileResolver, "get_tile_ids", get_sprites)

    maze = MazeTilemap([[0, 0], [0, 0]], maze_tileset)
    maze._init_layer("walls", 0, maze._is_wall)
    matrix = maze._layers["walls"].tiles

    assert matrix == [
        [
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_LEFT,
            MazeTileID.OUTER_CELL_WALL_TOP,
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_RIGHT,
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_LEFT,
            MazeTileID.INNER_CELL_TOP,
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_RIGHT,
        ],
        [
            MazeTileID.OUTER_CELL_WALL_LEFT,
            MazeTileID.EMPTY,
            MazeTileID.OUTER_CELL_WALL_RIGHT,
            MazeTileID.INNER_CELL_LEFT,
            MazeTileID.EMPTY,
            MazeTileID.INNER_CELL_RIGHT,
        ],
        [
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_LEFT,
            MazeTileID.OUTER_CELL_WALL_BOTTOM,
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_RIGHT,
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_LEFT,
            MazeTileID.INNER_CELL_BOTTOM,
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_RIGHT,
        ],
        [
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_LEFT,
            MazeTileID.INNER_CELL_TOP,
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_TOP_RIGHT,
            MazeTileID.INNER_CELL_CORNER_WALL_TOP_LEFT,
            MazeTileID.INNER_CELL_TOP,
            MazeTileID.INNER_CELL_CORNER_WALL_TOP_RIGHT,
        ],
        [
            MazeTileID.INNER_CELL_LEFT,
            MazeTileID.EMPTY,
            MazeTileID.INNER_CELL_RIGHT,
            MazeTileID.INNER_CELL_LEFT,
            MazeTileID.EMPTY,
            MazeTileID.INNER_CELL_RIGHT,
        ],
        [
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_LEFT,
            MazeTileID.INNER_CELL_BOTTOM,
            MazeTileID.OUTER_CELL_CORNER_HORIZONTAL_BOTTOM_RIGHT,
            MazeTileID.INNER_CELL_CORNER_WALL_BOTTOM_LEFT,
            MazeTileID.INNER_CELL_BOTTOM,
            MazeTileID.INNER_CELL_CORNER_WALL_BOTTOM_RIGHT,
        ],
    ]
