from enum import Enum, auto


class PacManEvent(Enum):
    """Gameplay events exchanged between Pac-Man systems."""

    SET_DIRECTION_UP = auto()
    SET_DIRECTION_DOWN = auto()
    SET_DIRECTION_LEFT = auto()
    SET_DIRECTION_RIGHT = auto()
    PACMAN_COLLIDES_WITH_GHOST = auto()
    PACMAN_COLLIDES_WITH_FRIGHTENED_GHOST = auto()
    PACMAN_COLLIDES_WITH_PAC_GUM = auto()
    PACMAN_COLLIDES_WITH_SUPER_PAC_GUM = auto()
    PACMAN_COLLIDES_WITH_BOOST = auto()
    FRIGHTENED_MODE_START = auto()
    FLASH_MODE_START = auto()
    FRIGHTENED_MODE_END = auto()
    DEAD_MODE_START = auto()
    DEAD_MODE_END = auto()
