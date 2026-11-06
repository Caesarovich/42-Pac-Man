from dataclasses import dataclass

from pac_man.exceptions import PacManException
from pac_man.mazegen_utils.maze_directions import (
    ALL_WALLS,
    DX,
    DY,
    CornerDirection,
    WallDirection,
    WallOrientation,
)


@dataclass
class CornerSpec:
    """Precomputed wall and neighbor directions for a maze corner.

    Attributes:
        corner: Corner direction to describe.
    """

    corner: CornerDirection

    def __post_init__(self) -> None:
        """Derive adjacent walls and neighbor offsets from the corner mask."""
        self.horizontal_wall = WallDirection(self.corner & WallOrientation.HORIZONTAL)
        self.vertical_wall = WallDirection(self.corner & WallOrientation.VERTICAL)
        self.horizontal_neighbor = (
            DX[self.vertical_wall],
            DY[self.vertical_wall],
        )
        self.vertical_neighbor = (
            DX[self.horizontal_wall],
            DY[self.horizontal_wall],
        )


@dataclass
class CellSpec:
    """Description of the wall bit mask stored for one maze cell.

    Attributes:
        value: Bit mask containing the walls present on the cell.
    """

    value: int

    def has_wall(self, direction: WallDirection) -> bool:
        """Return whether the cell contains a wall in a direction.

        Args:
            direction: Wall direction to test.

        Returns:
            True when the wall bit is set for the direction.
        """
        return bool(self.value & direction)

    def is_closed(self) -> bool:
        """Return whether the cell contains every wall direction.

        Returns:
            True when the cell is fully closed.
        """
        return self.value == ALL_WALLS


class MazeWrapper:
    """Typed helper around the raw maze matrix.

    The wrapper exposes maze dimensions and converts raw integer wall masks
    into CellSpec instances used by the sprite resolver.
    """

    def __init__(self, maze: list[list[int]]) -> None:
        """Initialize the wrapper.

        Args:
            maze: Raw maze matrix containing wall bit masks.

        Raises:
            PacManException: If the maze has no rows.
        """
        self._validate_maze(maze)
        self.height = len(maze)
        self.width = len(maze[0])
        self.cell_specs = [[CellSpec(cell) for cell in row] for row in maze]

    def _validate_maze(self, maze: list[list[int]]) -> None:
        try:
            if not maze or not maze[0]:
                raise PacManException("Maze cannot be empty.")
            width = len(maze[0])
            for row in maze:
                if len(row) != width:
                    raise PacManException("Rows must be of equal size.")
                if any(cell < 0 or cell > ALL_WALLS for cell in row):
                    raise PacManException("Invalid cell value.")
        except TypeError:
            raise PacManException("Invalid maze format")

    def is_wall_outer_wall(self, x: int, y: int, direction: WallDirection) -> bool:
        """Return whether a cell wall is on the outer maze border.

        Args:
            x: Cell column index.
            y: Cell row index.
            direction: Wall direction to test.

        Returns:
            True when the wall direction touches the maze boundary.
        """
        match direction:
            case WallDirection.TOP:
                return y == 0
            case WallDirection.LEFT:
                return x == 0
            case WallDirection.BOTTOM:
                return y == self.height - 1
            case WallDirection.RIGHT:
                return x == self.width - 1
        return False

    def is_cell_maze_corner(self, x: int, y: int) -> bool:
        """Return whether a cell sits in one of the maze corners.

        Args:
            x: Cell column index.
            y: Cell row index.

        Returns:
            True when the cell is at both a horizontal and vertical boundary.
        """
        return x in (0, self.width - 1) and y in (0, self.height - 1)

    def is_corner_outer_corner(
        self, x: int, y: int, corner_direction: CornerDirection
    ) -> bool:
        """Return whether a cell corner is also an outer maze corner.

        Args:
            x: Cell column index.
            y: Cell row index.
            corner_direction: Corner direction to test.

        Returns:
            True when the requested corner matches the maze boundary corner.
        """
        match corner_direction:
            case CornerDirection.TOP_LEFT:
                return x == 0 and y == 0
            case CornerDirection.TOP_RIGHT:
                return x == self.width - 1 and y == 0
            case CornerDirection.BOTTOM_LEFT:
                return x == 0 and y == self.height - 1
            case CornerDirection.BOTTOM_RIGHT:
                return x == self.width - 1 and y == self.height - 1

    def get_cell_spec(
        self, x: int, y: int, relative_to: tuple[int, int] = (0, 0)
    ) -> CellSpec:
        """Return a cell spec with an optional relative offset.

        Args:
            x: Cell column index, or horizontal offset when relative_to is set.
            y: Cell row index, or vertical offset when relative_to is set.
            relative_to: Base cell coordinate used for relative lookups.

        Returns:
            Cell specification at the resolved coordinate.
        """
        rel_x, rel_y = relative_to
        return self.cell_specs[y + rel_y][x + rel_x]

    def __getitem__(self, index: int) -> list[CellSpec]:
        """Return a row of cell specifications.

        Args:
            index: Maze row index.

        Returns:
            Cell specifications for the requested row.
        """
        return self.cell_specs[index]
