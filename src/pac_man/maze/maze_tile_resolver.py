import functools

from pac_man.assets.maze_assets import (
    CornerType,
    MazeConsumables,
    MazeTileID,
    MazeTileset,
)
from pac_man.mazegen_utils.maze_directions import (
    CornerDirection,
    WallDirection,
    WallOrientation,
)
from pac_man.mazegen_utils.maze_wrapper import CornerSpec, MazeWrapper


class MazeTileResolver:
    """Resolve the maze tile IDs needed to render each logical cell."""

    def __init__(self, maze: MazeWrapper, maze_tileset: MazeTileset) -> None:
        """Initialize the resolver.

        Args:
            maze: Wrapped maze matrix to inspect.
            maze_tileset: Maze tileset used for resolved maze parts.
        """
        self._maze = maze
        self._maze_tileset = maze_tileset
        self._corner_specs = {corner: CornerSpec(corner) for corner in CornerDirection}

    def _get_center_tile_id(self, x: int, y: int) -> MazeTileID | None:
        """Resolve the tile ID drawn at the center of a maze cell.

        Args:
            x: Cell column index.
            y: Cell row index.

        Returns:
            Consumable tile ID for open cells, or None for fully closed cells.
        """
        if self._maze.cell_specs[y][x].is_closed():
            return None
        if self._maze.is_cell_maze_corner(x, y):
            return self._maze_tileset.get_consumable(MazeConsumables.SUPER_PAC_GUM)
        return self._maze_tileset.get_consumable(MazeConsumables.PAC_GUM)

    def _get_wall_tile_id(
        self, x: int, y: int, direction: WallDirection
    ) -> MazeTileID | None:
        """Resolve the tile ID drawn on one side of a maze cell.

        Args:
            x: Cell column index.
            y: Cell row index.
            direction: Wall side to resolve.

        Returns:
            Wall tile ID when a wall is present, otherwise a pac gum tile ID.
        """
        if self._maze.is_wall_outer_wall(x, y, direction):
            return self._maze_tileset.get_outer_wall(direction)

        cell_spec = self._maze.cell_specs[y][x]
        if cell_spec.has_wall(direction):
            return self._maze_tileset.get_inner_wall(direction)
        return self._maze_tileset.get_consumable(MazeConsumables.PAC_GUM)

    def _get_corner_tile_id(
        self,
        x: int,
        y: int,
        direction: CornerDirection,
    ) -> MazeTileID | None:
        """Resolve the tile ID drawn at one corner of a maze cell.

        Args:
            x: Cell column index.
            y: Cell row index.
            direction: Corner to resolve.

        Returns:
            Corner, wall, or consumable tile ID matching neighboring walls.
        """
        if self._maze.is_corner_outer_corner(x, y, direction):
            return self._maze_tileset.get_outer_corner(direction)

        cell_spec = self._maze.cell_specs[y][x]
        corner_spec = self._corner_specs[direction]

        horizontal_wall = corner_spec.horizontal_wall
        vertical_wall = corner_spec.vertical_wall
        corner = corner_spec.corner

        has_vertical_wall = cell_spec.has_wall(vertical_wall)
        has_horizontal_wall = cell_spec.has_wall(horizontal_wall)

        # outer borders case
        if self._maze.is_wall_outer_wall(x, y, horizontal_wall):
            if not has_vertical_wall:
                return self._maze_tileset.get_outer_wall(horizontal_wall)
            return self._maze_tileset.get_outer_cell_corner(
                WallOrientation.HORIZONTAL,
                corner,
            )
        if self._maze.is_wall_outer_wall(x, y, vertical_wall):
            if not has_horizontal_wall:
                return self._maze_tileset.get_outer_wall(vertical_wall)
            return self._maze_tileset.get_outer_cell_corner(
                WallOrientation.VERTICAL,
                corner,
            )

        # inner border cases
        if has_horizontal_wall and has_vertical_wall:
            return self._maze_tileset.get_inner_corner(CornerType.CELL_CORNER, corner)
        if has_horizontal_wall:
            return self._maze_tileset.get_inner_wall(horizontal_wall)
        if has_vertical_wall:
            return self._maze_tileset.get_inner_wall(vertical_wall)

        horizontal_neighbor_cell_spec = self._maze.get_cell_spec(
            *corner_spec.horizontal_neighbor, (x, y)
        )
        vertical_neighbor_cell_spec = self._maze.get_cell_spec(
            *corner_spec.vertical_neighbor, (x, y)
        )
        if vertical_neighbor_cell_spec.has_wall(
            vertical_wall
        ) or horizontal_neighbor_cell_spec.has_wall(horizontal_wall):
            return self._maze_tileset.get_inner_corner(CornerType.WALL_CORNER, corner)
        return self._maze_tileset.get_consumable(MazeConsumables.PAC_GUM)

    def get_tile_ids(self, x: int, y: int) -> list[list[MazeTileID | None]]:
        """Resolve the 3x3 tile ID block used to render one maze cell.

        Args:
            x: Cell column index.
            y: Cell row index.

        Returns:
            Three rows of three tile IDs representing corners, walls, and
            center.
        """
        corner = functools.partial(self._get_corner_tile_id, x=x, y=y)
        wall = functools.partial(self._get_wall_tile_id, x=x, y=y)
        return [
            [
                corner(direction=CornerDirection.TOP_LEFT),
                wall(direction=WallDirection.TOP),
                corner(direction=CornerDirection.TOP_RIGHT),
            ],
            [
                wall(direction=WallDirection.LEFT),
                self._get_center_tile_id(x, y),
                wall(direction=WallDirection.RIGHT),
            ],
            [
                corner(direction=CornerDirection.BOTTOM_LEFT),
                wall(direction=WallDirection.BOTTOM),
                corner(direction=CornerDirection.BOTTOM_RIGHT),
            ],
        ]
