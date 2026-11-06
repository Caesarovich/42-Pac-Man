import itertools
import logging
from collections.abc import Iterator
from math import sqrt

from engine import (
    NavGraph2D,
    Node,
    Vector2,
)
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.config.game_config import GameConfig
from pac_man.entities.blinky import Blinky
from pac_man.entities.boost import BoostCollectible
from pac_man.entities.clyde import Clyde
from pac_man.entities.ghost import Ghost
from pac_man.entities.inky import Inky
from pac_man.entities.pacman import PacMan
from pac_man.entities.pinky import Pinky
from pac_man.game.level_spawn_points import LevelSpawnPoints

logger = logging.getLogger(__name__)


class LevelEntityManager(Node):
    """Create, spawn, and control the entities belonging to one level."""

    def __init__(
        self,
        name: str = "level_entity_manager",
    ) -> None:
        """Initialize an empty level entity manager.

        Args:
            name: Node name used in the scene tree.
        """
        super().__init__(name=name)
        self.pacman: PacMan | None = None
        self.ghosts: list[Ghost] | None = None
        self.graph: NavGraph2D | None = None
        self.spawn_points: LevelSpawnPoints | None = None
        self.boosts: list[BoostCollectible] | None = None

    def _on_enter_tree(self) -> None:
        """Derive entity spawn points from the configured navigation graph.

        Raises:
            AssertionError: If the navigation graph has not been assigned.
        """
        assert self.graph is not None, "Graph is not set"
        self.spawn_points = LevelSpawnPoints.from_graph(self.graph)

    @property
    def entities(self) -> Iterator[PacMan | Ghost | BoostCollectible]:
        """Iterate over Pac-Man followed by all ghosts.

        Returns:
            An iterator over every managed gameplay entity.

        Raises:
            AssertionError: If the entities have not been created.
        """
        assert self.pacman is not None, "Pacman is not created"
        assert self.ghosts is not None, "Ghosts are not created"
        assert self.boosts is not None, "Boosts are not created"
        return itertools.chain((self.pacman,), self.ghosts, self.boosts)

    def create_entities(
        self,
        game_resource_manager: GameResourceManager,
        game_config: GameConfig,
        scale: Vector2,
        level_id: int,
    ) -> None:
        """Create Pac-Man and all ghosts for the current level.

        Args:
            game_resource_manager: Loaded resources used to build entities.
            game_config: Entity speeds, timers, and collision configuration.
            scale: Scale applied to every created entity.
            level_id: One-based level number used to calculate speed boosts.
        """
        self._create_pacman(game_resource_manager, game_config, scale, level_id)
        self._create_ghosts(game_resource_manager, game_config, scale, level_id)
        self.boosts = []

    def prepare_round(self) -> None:
        """Reset all entities to their visible, disabled spawn state."""
        self._spawn_pacman()
        self._spawn_ghosts()
        self.unhide_all()

    def start_round(self) -> None:
        """Enable every entity when active gameplay starts."""
        for entity in self.entities:
            entity.enabled = True

    def play_pacman_death(self) -> None:
        """Show Pac-Man and start the death animation.

        Raises:
            AssertionError: If Pac-Man has not been created.
        """
        assert self.pacman is not None, "Pacman is not created"
        self.pacman.visible = True
        self.pacman.enabled = True
        self.pacman.run_death_animation()

    def hide_all(self) -> None:
        """Disable and hide every managed entity."""
        for entity in self.entities:
            entity.enabled = False
            entity.visible = False

    def unhide_all(self) -> None:
        """Enable visibility for every managed entity."""
        for entity in self.entities:
            entity.visible = True

    def hide_ghosts(self) -> None:
        """Disable and hide all ghosts.

        Raises:
            AssertionError: If the ghosts have not been created.
        """
        assert self.ghosts is not None, "Ghosts are not created"
        for ghost in self.ghosts:
            ghost.enabled = False
            ghost.visible = False

    def freeze_all(self) -> None:
        """Disable entity updates while keeping current visibility."""
        for entity in self.entities:
            entity.enabled = False

    def add_boost(self, boost: BoostCollectible) -> None:
        """Add a boost to the level entity manager.

        Args:
            boost: Boost collectible to add.

        Raises:
            AssertionError: If the boosts list has not been created.
        """
        assert self.boosts is not None, "Boosts are not created"
        self.boosts.append(boost)

    def remove_boost(self, boost: BoostCollectible) -> None:
        """Remove a boost from the level entity manager.

        Args:
            boost: Boost collectible to remove.

        Raises:
            AssertionError: If the boosts list has not been created.
        """
        assert self.boosts is not None, "Boosts are not created"
        self.boosts.remove(boost)

    def _create_ghosts(
        self,
        game_resource_manager: GameResourceManager,
        game_config: GameConfig,
        scale: Vector2,
        level_id: int,
    ) -> None:
        """Create and attach the four ghosts used by the level.

        Args:
            game_resource_manager: Loaded resources used to build ghosts.
            game_config: Ghost speed, timer, and collision configuration.
            scale: Scale applied to each ghost.
            level_id: One-based level number used to calculate speed.

        Raises:
            AssertionError: If the navigation graph has not been assigned.
        """
        assert self.graph is not None, "Graph is not set"
        self.ghosts = []
        ghost_speed = self._calculate_entity_speed(
            game_config.ghost_base_speed,
            level_id,
            game_config.ghosts_speed_boost_per_level,
        )
        for ghost_cls in (Clyde, Pinky, Blinky, Inky):
            ghost = ghost_cls(
                self.graph,
                game_resource_manager,
                ghost_speed,
                game_config.frightened_time,
                game_config.flash_time,
                game_config.ghost_collision_box_scale,
            )
            ghost.scale = scale
            ghost.enabled = False
            ghost.visible = False
            self.ghosts.append(ghost)
            self.add_child(ghost)

    def _create_pacman(
        self,
        game_resource_manager: GameResourceManager,
        game_config: GameConfig,
        scale: Vector2,
        level_id: int,
    ) -> None:
        """Create and attach Pac-Man for the level.

        Args:
            game_resource_manager: Loaded resources used to build Pac-Man.
            game_config: Pac-Man speed and collision configuration.
            scale: Scale applied to Pac-Man.
            level_id: One-based level number used to calculate speed.

        Raises:
            AssertionError: If the navigation graph has not been assigned.
        """
        assert self.graph is not None, "Graph is not set"
        pacman_speed = self._calculate_entity_speed(
            game_config.pacman_base_speed,
            level_id,
            game_config.pacman_speed_boost_per_level,
        )
        self.pacman = PacMan(
            game_resource_manager,
            self.graph,
            pacman_speed,
            game_config.pacman_collision_box_scale,
        )
        self.pacman.scale = scale
        self.pacman.enabled = False
        self.pacman.visible = False
        self.add_child(self.pacman)

    def _calculate_entity_speed(
        self, base_speed: float, level_id: int, boost_per_level: float
    ) -> float:
        """Calculate an entity speed after applying level progression.

        Args:
            base_speed: Entity speed on the first level.
            level_id: Current one-based level number.
            boost_per_level: Fractional speed increase for each extra level.

        Returns:
            The movement speed for the requested level.
        """
        assert self.graph is not None, "Graph is not set"
        graph_size = sqrt(len(self.graph.nodes))
        return (base_speed * (1 + boost_per_level * (level_id - 1))) / graph_size

    def _spawn_pacman(self) -> None:
        """Reset Pac-Man at the configured spawn point.

        Raises:
            AssertionError: If Pac-Man or the spawn points are unavailable.
        """
        assert self.pacman is not None, "Pacman is not created"
        assert self.spawn_points is not None, "Spawn points are not defined"

        pacman_start_position = self.spawn_points.pacman
        self.pacman.graph_controller.set_current_node(pacman_start_position)
        self.pacman.init_position()
        self.pacman.reset()
        self.pacman.visible = True
        self.pacman.enabled = False

    def _spawn_ghosts(self) -> None:
        """Reset all ghosts at their configured spawn points.

        Raises:
            AssertionError: If the ghosts or spawn points are unavailable.
        """
        assert self.ghosts is not None, "Ghosts are not created"
        assert self.spawn_points is not None, "Spawn points are not defined"

        for ghost in self.ghosts:
            start_position = self.spawn_points.for_ghost(ghost)
            ghost.nav_agent.set_current_node(start_position)
            ghost.init_position()
            ghost.reset()
            ghost.visible = True
            ghost.enabled = False
