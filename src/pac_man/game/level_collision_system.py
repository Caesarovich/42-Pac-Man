import logging

from engine import (
    Node,
    ObjectCollisionResolver,
    Tilemap,
    TileMapCollisionResolver,
)
from pac_man.entities.boost import BoostCollectible
from pac_man.entities.collisions.collisions_handler import (
    PacManCollisionHandler,
)
from pac_man.entities.ghost import Ghost
from pac_man.entities.pacman import PacMan
from pac_man.game.game_manager import GameManager

logger = logging.getLogger(__name__)


class LevelCollisionSystem(Node):
    """Own and connect the collision components used by a game level."""

    def __init__(
        self,
        name: str | None = None,
    ) -> None:
        """Initialize object, tile, and gameplay collision handlers.

        Args:
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self.objects_collision_resolver = ObjectCollisionResolver()
        self.tile_collision_resolver = TileMapCollisionResolver()
        self.collision_handler = PacManCollisionHandler()

    def _on_enter_tree(self) -> None:
        """Connect collision event streams and attach collision components."""
        self.objects_collision_resolver.event_handler.add_observer(
            self.collision_handler
        )
        self.tile_collision_resolver.event_handler.add_observer(self.collision_handler)

        self.add_child(self.objects_collision_resolver)
        self.add_child(self.tile_collision_resolver)
        self.add_child(self.collision_handler)

    def set_tile_map(self, tile_map: Tilemap) -> None:
        """Set the tilemap checked for Pac-Man tile collisions.

        Args:
            tile_map: Level tilemap containing collision layers.
        """
        self.tile_collision_resolver.tile_map = tile_map

    def connect_game_manager(self, game_manager: GameManager) -> None:
        """Forward gameplay collision events to the game manager.

        Args:
            game_manager: Manager that updates score, lives, and game state.
        """
        self.collision_handler.add_observer(game_manager)

    def register_pacman(self, pacman: PacMan) -> None:
        """Register Pac-Man for object and tile collision checks.

        Args:
            pacman: Pac-Man entity whose collision box will be registered.

        Raises:
            AssertionError: If Pac-Man has no initialized collision box.
        """
        assert pacman.collision_box is not None, (
            "Pacman collision box is not initialized"
        )
        self.objects_collision_resolver.register(pacman.collision_box)
        self.tile_collision_resolver.register(pacman.collision_box)

    def register_ghosts(self, ghosts: list[Ghost]) -> None:
        """Register ghosts and connect them to gameplay collision events.

        Args:
            ghosts: Ghost entities to register with the collision system.
        """
        for ghost in ghosts:
            self.objects_collision_resolver.recursive_register(ghost)
            self.collision_handler.objects_event_handler.add_observer(ghost)
            self.collision_handler.tiles_event_handler.add_observer(ghost)

    def register_boost(self, boost: BoostCollectible) -> None:
        """Register a boost collectible for object collision checks.

        Args:
            boost: Boost entity to register with the collision system.
        """
        self.objects_collision_resolver.register(boost.collision_box)

    def unregister_boost(self, boost: BoostCollectible) -> None:
        """Unregister a boost collectible from object collision checks.

        Args:
            boost: Boost entity to unregister from the collision system.
        """
        self.objects_collision_resolver.remove(boost.collision_box)
