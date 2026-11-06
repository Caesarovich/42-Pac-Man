from enum import IntFlag, auto


class CollisionLayer(IntFlag):
    """Bit flags used to match collision layers and masks."""

    UNDEFINED = auto()
    MAZE = auto()
    PACMAN = auto()
    CHASE_GHOST = auto()
    FRIGHTENED_GHOSTS = auto()
    DEAD_GHOSTS = auto()
    PAC_GUMS = auto()
    SUPER_PAC_GUMS = auto()
    BOOSTS = auto()
