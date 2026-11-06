from enum import IntEnum, IntFlag, auto


class WallDirection(IntFlag):
    """Bit flags describing the walls present on a maze cell."""

    TOP = auto()
    RIGHT = auto()
    BOTTOM = auto()
    LEFT = auto()


class CornerDirection(IntEnum):
    """Corner directions encoded from their adjacent wall directions."""

    TOP_LEFT = WallDirection.TOP | WallDirection.LEFT
    TOP_RIGHT = WallDirection.TOP | WallDirection.RIGHT
    BOTTOM_LEFT = WallDirection.BOTTOM | WallDirection.LEFT
    BOTTOM_RIGHT = WallDirection.BOTTOM | WallDirection.RIGHT


class WallOrientation(IntEnum):
    """Wall orientation masks used to split corner directions."""

    HORIZONTAL = WallDirection.BOTTOM | WallDirection.TOP
    VERTICAL = WallDirection.RIGHT | WallDirection.LEFT


DX = {
    # Horizontal cell offsets for neighboring cells in each wall direction.
    WallDirection.RIGHT: 1,
    WallDirection.LEFT: -1,
    WallDirection.TOP: 0,
    WallDirection.BOTTOM: 0,
}
DY = {
    # Vertical cell offsets for neighboring cells in each wall direction.
    WallDirection.TOP: -1,
    WallDirection.BOTTOM: 1,
    WallDirection.LEFT: 0,
    WallDirection.RIGHT: 0,
}


ALL_WALLS = (
    # Bit mask for a fully closed maze cell.
    WallDirection.TOP | WallDirection.BOTTOM | WallDirection.LEFT | WallDirection.RIGHT
)
