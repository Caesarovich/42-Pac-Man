import logging
import random

import pyray
from pydantic.dataclasses import dataclass

from engine import (
    CollisionCircle2D,
    Engine,
    NavRegion2D,
    Node,
    Scene2D,
    Vector2,
)
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.assets.models.boost import Boost
from pac_man.config.game_config import GameConfig
from pac_man.entities.boost import BoostCollectible
from pac_man.entities.ghost import Ghost
from pac_man.entities.pacman import PacMan
from pac_man.game.game_manager import GameManager, GameState
from pac_man.game.level_collision_system import LevelCollisionSystem
from pac_man.game.level_entity_manager import LevelEntityManager
from pac_man.highscore import Highscore
from pac_man.maze.maze_container import MazeContainer
from pac_man.scenes.cheat_menu import CheatMenu
from pac_man.scenes.game_over import GameOver
from pac_man.scenes.pause_menu import PauseMenu
from pac_man.scenes.ui.game_level_hud import GameLevelHUD
from pac_man.scenes.victory import Victory

logger = logging.getLogger(__name__)


@dataclass
class LevelParameters:
    """Values carried into a playable level.

    Attributes:
        level_id: Current one-based level number.
        initial_lives: Number of lives available at level start.
        current_score: Score carried into the level.
        high_score: Highest persisted score.
        width: Generated maze width in cells.
        height: Generated maze height in cells.
        seed: Optional deterministic maze-generation seed.
    """

    level_id: int
    initial_lives: int
    current_score: int
    high_score: int
    width: int
    height: int
    seed: int | None


class GameLevel(Scene2D):
    """Playable maze scene containing Pac-Man, ghosts, and collisions."""

    def __init__(
        self,
        game_resource_manager: GameResourceManager,
        game_config: GameConfig,
        level_parameters: LevelParameters | None = None,
        name: str = "GameLevel",
    ) -> None:
        """Initialize the game level scene.

        Args:
            game_resource_manager: Loaded resource manager used by entities.
            game_config: Gameplay and level configuration.
            level_parameters: Optional values carried over from a prior level.
            name: Scene name.
        """
        super().__init__(name=name)
        self._game_resource_manager = game_resource_manager
        self._game_config = game_config
        self._level_parameters = (
            level_parameters
            if level_parameters is not None
            else self._new_level_parameters()
        )

        self._game_manager = GameManager(
            name="game_level_game_score_manager", game_config=self._game_config
        )
        self._game_manager.game_state_event_handler.add_observer(self)

        self._hud = GameLevelHUD(
            game_config=self._game_config,
            game_manager=self._game_manager,
            name="game_level_hud",
        )

        self._entity_manager = LevelEntityManager()
        self._collision_system = LevelCollisionSystem()

        self._next_scene: Scene2D | None = None

    @property
    def pacman(self) -> PacMan:
        """Return the Pac-Man entity managed by the level.

        Raises:
            AssertionError: If Pac-Man has not been initialized.
        """
        assert self._entity_manager.pacman is not None, "Pacman is not initialized"
        return self._entity_manager.pacman

    @property
    def ghosts(self) -> list[Ghost]:
        """Return the ghost entities managed by the level.

        Raises:
            AssertionError: If the ghosts have not been initialized.
        """
        assert self._entity_manager.ghosts is not None, "Ghosts are not initialized"
        return self._entity_manager.ghosts

    def _new_level_parameters(self) -> LevelParameters:
        """Build parameters for the first level of a new game.

        Returns:
            Initial lives, scores, level number, and maze settings.
        """
        high_scores_entries = Highscore.load()
        high_score = high_scores_entries[0].score if high_scores_entries else 0

        maze_settings = self._game_config.levels[0]
        return LevelParameters(
            level_id=1,
            initial_lives=self._game_config.lives,
            current_score=0,
            high_score=high_score,
            width=maze_settings.width,
            height=maze_settings.height,
            seed=maze_settings.seed,
        )

    def _on_enter(self) -> None:
        """Build the maze, collision resolvers, ghosts, and Pac-Man."""
        assert self._level_parameters is not None, "Level parameters is not set"

        min_length = min(pyray.get_render_width(), pyray.get_render_height())
        self._maze_container = MazeContainer(
            game_resource_manager=self._game_resource_manager,
            width=self._level_parameters.width,
            height=self._level_parameters.height,
            seed=self._level_parameters.seed,
            size=Vector2(min_length * 0.8, min_length * 0.8),
        )
        self.root.add_child(self._maze_container)

        self._maze_container.position = Vector2(
            (pyray.get_render_width() - self._maze_container.size.x) / 2,
            (pyray.get_render_height() - self._maze_container.size.y) / 2,
        )
        self._init_hud()
        self._init_collision_system()
        self._init_game_manager()
        self._init_entity_manager()

        CheatMenu.reset_cheats()

    def _init_collision_system(self) -> None:
        """Attach the maze tilemap and collision system to the scene."""
        self._collision_system.set_tile_map(self._maze_container.maze)
        self.root.add_child(self._collision_system)

    def _init_entity_manager(self) -> None:
        """Create level entities and register their collision objects."""
        self._entity_manager.graph = self._maze_container.maze.nav_region.graph
        self.root.add_child(self._entity_manager)
        self._entity_manager.create_entities(
            self._game_resource_manager,
            self._game_config,
            self._maze_container.maze.scale,
            self._level_parameters.level_id,
        )
        self._collision_system.register_pacman(self.pacman)
        self._collision_system.register_ghosts(self.ghosts)

    def _init_hud(self) -> None:
        """Configure the HUD around the maze and add it to the scene."""
        maze_area = self._maze_container.maze.get_destination_rectangle()
        self._hud.maze_area = maze_area
        self.root.add_child(self._hud)

    def _init_game_manager(self) -> None:
        """Initialize gameplay values, HUD counters, and event connections."""
        self._collision_system.connect_game_manager(self._game_manager)
        self._game_manager.set_initial_values(
            pacgums_count=self._maze_container.maze.pacgums_count,
            super_pacgums_count=self._maze_container.maze.super_pacgums_count,
            current_score=self._level_parameters.current_score,
            time=self._game_config.game_timer,
            highscore=self._level_parameters.high_score,
            level=self._level_parameters.level_id,
            lives=self._level_parameters.initial_lives,
        )
        self._game_manager.refresh_hud()
        self.root.add_child(self._game_manager)

    def _spawn_random_boost(self, boost_kind: Boost) -> None:
        available_tiles: list[tuple[int, int]] = []

        for y in range(self._maze_container.maze.height):
            for x in range(self._maze_container.maze.width):
                if x % 3 != 1 or y % 3 != 1:
                    continue
                tile = self._maze_container.maze.get_collision_tile("walls", x, y)
                if not tile:
                    available_tiles.append((x, y))

        if not available_tiles:
            logger.warning("No available tiles to spawn a boost.")
            return

        position = random.choice(available_tiles)

        ts = self._maze_container.maze.tileset.tile_size
        instance_position = Vector2(
            position[0] * ts + ts / 2,
            position[1] * ts + ts / 2,
        )

        boost = BoostCollectible(
            name=f"boost_{boost_kind.name}",
            kind=boost_kind,
            duration=self._game_config.boost_duration,
            grm=self._game_resource_manager,
        )

        boost.position = instance_position
        self._maze_container.maze.add_child(boost)
        self._collision_system.register_boost(boost)
        self._entity_manager.add_boost(boost)

    def on_notify(self, entity: Node | None, event: GameState) -> None:
        """Apply scene changes requested by the game lifecycle manager.

        Args:
            entity: Event source. It is unused for lifecycle transitions.
            event: New game lifecycle state.
        """
        match event:
            case GameState.READY_CHECK:
                self._entity_manager.prepare_round()
            case GameState.PLAYING:
                self._entity_manager.start_round()
            case GameState.PACMAN_DEATH:
                self._entity_manager.hide_all()
                self._entity_manager.play_pacman_death()
            case GameState.WIN_LEVEL:
                self._entity_manager.freeze_all()
                self._entity_manager.hide_ghosts()
                if self._level_parameters.level_id == self._game_config.max_levels:
                    self._next_scene = self._winner_scene()
                else:
                    self._next_scene = self._next_level_scene()

            case GameState.GAME_OVER | GameState.TIME_S_UP:
                self._entity_manager.freeze_all()
                self._next_scene = self._game_over_scene()
            case GameState.END_LEVEL:
                if self.manager is not None:
                    if self._next_scene is not None:
                        self.manager.replace(self._next_scene)
                    else:
                        self.manager.pop()

    def _game_over_scene(self) -> Scene2D:
        """Create the game-over scene for the current result.

        Returns:
            A game-over scene containing the current score and level.
        """
        return GameOver(
            "game_over_scene",
            self._game_resource_manager,
            self._game_manager.score,
            self._level_parameters.level_id,
        )

    def _winner_scene(self) -> Scene2D:
        """Create the victory scene for the completed game.

        Returns:
            A victory scene containing the final score and level.
        """
        return Victory(
            "victory_scene",
            self._game_resource_manager,
            self._game_manager.score,
            self._level_parameters.level_id,
        )

    def _next_level_scene(self) -> Scene2D:
        """Create the next level while preserving session progress.

        Returns:
            A configured game-level scene for the next level.
        """
        next_level_id = self._level_parameters.level_id + 1
        if len(self._game_config.levels) >= next_level_id:
            maze_settings = self._game_config.levels[next_level_id - 1]
            width = maze_settings.width
            height = maze_settings.height
            seed = maze_settings.seed
        else:
            width = self._level_parameters.width
            height = self._level_parameters.height
            seed = None

        next_level_parameters = LevelParameters(
            level_id=self._level_parameters.level_id + 1,
            initial_lives=self._game_manager.lives,
            current_score=self._game_manager.score,
            high_score=self._level_parameters.high_score,
            width=width,
            height=height,
            seed=seed,
        )
        return GameLevel(
            name=f"game_level_scene_{next_level_parameters.level_id}",
            game_resource_manager=self._game_resource_manager,
            game_config=self._game_config,
            level_parameters=next_level_parameters,
        )

    def _on_update(self, dt: float) -> None:
        """Handle per-frame scene input.

        Args:
            dt: Frame delta time in seconds.
        """
        self._handle_input()
        self._maybe_spawn_boost(dt)

    def _handle_input(self) -> None:
        """Open the pause menu when the pause key is pressed."""
        if pyray.is_key_pressed(pyray.KeyboardKey.KEY_P):
            if self.manager is not None:
                self.manager.push(
                    PauseMenu(
                        name="PauseMenu",
                        game_resource_manager=self._game_resource_manager,
                    ),
                )
        elif (
            pyray.is_key_pressed(pyray.KeyboardKey.KEY_C)
            and self._game_manager.is_game_playing()
        ) and self.manager is not None:
            self.manager.push(
                CheatMenu(
                    name="CheatMenu",
                    game_manager=self._game_manager,
                    pacman=self.pacman,
                    ghosts=self.ghosts,
                ),
            )

    def _maybe_spawn_boost(self, dt: float) -> None:
        """Randomly spawn a boost collectible in the maze."""
        if random.random() < self._game_config.boost_spawn_chance * dt:
            boost_kind = random.choice(list(Boost))
            self._spawn_random_boost(boost_kind=boost_kind)


if __name__ == "__main__":
    # Node2D.DEBUG_DRAW_GIZMO = True
    # Tilemap.DEBUG_DRAW = True
    NavRegion2D.DEBUG_DRAW = True
    CollisionCircle2D.DEBUG_DRAW = True

    engine_config = Engine.Config(
        virtual_screen_dimensions=(1920, 1080),
        show_fps=True,
    )

    engine = Engine(config=engine_config)
    grm = GameResourceManager()
    game_config = GameConfig()

    engine.initialize()
    grm.load()
    engine.scene_manager.push(
        GameLevel(
            name="GameLevel",
            game_resource_manager=grm,
            game_config=game_config,
        )
    )
    engine.run()
