import logging
from dataclasses import dataclass
from enum import Enum, auto

from engine import Node, Node2D, Subject
from pac_man.config.game_config import GameConfig
from pac_man.entities.score_notification import ScoreNotification
from pac_man.scenes.ui.ui_controller import ScoreEvent
from pac_man.signals.pacman_events import PacManEvent

logger = logging.getLogger(__name__)


class GameState(Enum):
    """Lifecycle states for a playable game level."""

    START = auto()
    READY_CHECK = auto()
    PLAYING = auto()
    PACMAN_DEATH = auto()
    GAME_OVER = auto()
    TIME_S_UP = auto()
    WIN_LEVEL = auto()
    WIN_GAME = auto()
    END_LEVEL = auto()


@dataclass
class GameTimers:
    """Timers used by the game lifecycle state machine.

    Attributes:
        ready_check: Elapsed time before a round starts.
        playing: Remaining gameplay time.
        frightened: Elapsed frightened-mode time.
        pacman_death: Elapsed time in the death sequence.
        end_level: Elapsed time before leaving a finished level.
    """

    ready_check: float = 0.0
    playing: float = 0.0
    frightened: float = 0.0
    pacman_death: float = 0.0
    end_level: float = 0.0

    def update(self, dt: float, game_status: GameState) -> None:
        """Advance the timer associated with the active game state.

        Args:
            dt: Elapsed frame time in seconds.
            game_status: Current lifecycle state.
        """
        match game_status:
            case GameState.READY_CHECK:
                self.ready_check += dt
            case GameState.PLAYING:
                self.playing = max(0.0, self.playing - dt)
            case GameState.PACMAN_DEATH:
                self.pacman_death += dt
            case GameState.GAME_OVER | GameState.WIN_LEVEL | GameState.TIME_S_UP:
                self.end_level += dt

    def reset(self, game_status: GameState) -> None:
        """Reset the timer associated with a state being exited.

        Args:
            game_status: Lifecycle state whose timer must be reset.
        """
        match game_status:
            case GameState.READY_CHECK:
                self.ready_check = 0.0
            case GameState.PACMAN_DEATH:
                self.pacman_death = 0.0


@dataclass
class GameParameters:
    """Mutable gameplay values for the current game session.

    Attributes:
        pac_man_remainig_lives: Remaining Pac-Man lives.
        score: Current player score.
        level: Current one-based level number.
        pacgums_count: Number of regular pac-gums still available.
        super_pacgums_count: Number of super pac-gums still available.
        highscore: Highest score loaded at the start of the game.
    """

    pac_man_remainig_lives: int = 3
    score: int = 0
    level: int = 1
    pacgums_count: int = 0
    super_pacgums_count: int = 0
    highscore: int = 0

    @property
    def win_level(self) -> bool:
        """Return whether all pac-gums have been consumed."""
        return self.pacgums_count + self.super_pacgums_count == 0

    def lose_life(self) -> None:
        """Remove one life without allowing the counter to become negative."""
        self.pac_man_remainig_lives = max(0, self.pac_man_remainig_lives - 1)


class GameManager(Node):
    """Manage level state transitions, timers, score, and remaining lives."""

    class Cheat:
        def __init__(self, game_manager: GameManager) -> None:
            self._game_manager = game_manager

        def force_win_level(self) -> None:
            self._game_manager._change_state(GameState.WIN_LEVEL)

        def add_lives(self, quantity: int) -> None:
            self._game_manager._game_parameters.pac_man_remainig_lives += quantity
            self._game_manager.refresh_hud()

        def add_points(self, quantity: int) -> None:
            self._game_manager._game_parameters.score += quantity
            self._game_manager.refresh_hud()

        def add_time(self, quantity: int) -> None:
            self._game_manager._game_timers.playing += quantity
            self._game_manager.refresh_hud()

    def __init__(
        self,
        game_config: GameConfig,
        name: str | None = None,
    ) -> None:
        """Initialize the game manager.

        Args:
            game_config: Gameplay and lifecycle configuration.
            name: Optional node name used in the scene tree.
        """
        super().__init__(name)
        self._fsm_state = GameState.START
        self._game_parameters = GameParameters(pac_man_remainig_lives=game_config.lives)
        self._game_config = game_config
        self._pacman_eat_ghost_combo = 1
        self._frightened = False
        self._game_timers = GameTimers()
        self._pacman_dead = False

        self.score_event_handler: Subject[ScoreEvent] = Subject()
        self.game_state_event_handler: Subject[GameState] = Subject()

        self.cheat = self.Cheat(self)

    def is_game_playing(self) -> bool:
        return self._fsm_state == GameState.PLAYING

    def set_initial_values(
        self,
        pacgums_count: int,
        super_pacgums_count: int,
        current_score: int,
        time: float,
        highscore: int,
        level: int,
        lives: int,
    ) -> None:
        """Set the values required to start or resume a level.

        Args:
            pacgums_count: Number of regular pac-gums in the level.
            super_pacgums_count: Number of super pac-gums in the level.
            current_score: Score carried into the level.
            time: Initial gameplay time in seconds.
            highscore: Highest persisted score.
            level: Current one-based level number.
            lives: Number of lives carried into the level.
        """
        self._game_parameters.pacgums_count = pacgums_count
        self._game_parameters.super_pacgums_count = super_pacgums_count
        self._game_parameters.score = current_score
        self._game_parameters.highscore = highscore
        self._game_timers.playing = time
        self._game_parameters.level = level
        self._game_parameters.pac_man_remainig_lives = lives

    def _start_frightened_mode(self) -> None:
        """Mark frightened mode as active for score-combo tracking."""
        self._frightened = True

    def _end_frightened_mode(self) -> None:
        """Stop frightened mode and reset its timer and score combo."""
        self._frightened = False
        self._game_timers.frightened = 0.0
        self._pacman_eat_ghost_combo = 1

    def _on_update(self, dt: float) -> None:
        """Advance the game lifecycle and active timers.

        Args:
            dt: Elapsed frame time in seconds.
        """
        self._update_fsm_state()
        self._game_timers.update(dt, self._fsm_state)
        self.score_event_handler.notify(
            None, ("time", f"{self._game_timers.playing:04.1f}")
        )
        if self._frightened:
            self._game_timers.frightened += dt
            if self._game_timers.frightened >= self._game_config.frightened_time:
                self._end_frightened_mode()

    def _change_state(self, new_state: GameState) -> None:
        """Leave the current state and notify observers of the next state.

        Args:
            new_state: Lifecycle state to activate.
        """
        self._game_timers.reset(self._fsm_state)
        self._fsm_state = new_state
        self.game_state_event_handler.notify(None, new_state)
        logger.debug("Changing game state to: %s", new_state)

    def refresh_hud(self) -> None:
        """Publish counters and timer to HUD observers."""
        self.score_event_handler.notify(
            None, ("lives", str(self._game_parameters.pac_man_remainig_lives))
        )
        self.score_event_handler.notify(
            None, ("level", str(self._game_parameters.level))
        )
        self.score_event_handler.notify(
            None, ("current_score", str(self._game_parameters.score))
        )
        self.score_event_handler.notify(
            None, ("high_score", str(self._game_parameters.highscore))
        )
        self.score_event_handler.notify(
            None, ("time", f"{self._game_timers.playing:04.1f}")
        )

    def _update_fsm_state(self) -> None:
        """Evaluate and apply transitions from the current lifecycle state."""
        match self._fsm_state:
            case GameState.START:
                self._change_state(GameState.READY_CHECK)
            case GameState.READY_CHECK:
                if self._game_timers.ready_check > self._game_config.ready_check_timer:
                    self._change_state(GameState.PLAYING)
            case GameState.PLAYING:
                if self._pacman_dead or self._game_timers.playing <= 0:
                    self._change_state(GameState.PACMAN_DEATH)
                elif self._game_parameters.win_level:
                    self._change_state(GameState.WIN_LEVEL)
            case GameState.PACMAN_DEATH:
                if (
                    self._game_timers.pacman_death
                    > self._game_config.pacman_death_timer
                ):
                    if not self._game_parameters.pac_man_remainig_lives:
                        self._change_state(GameState.GAME_OVER)
                    elif self._game_timers.playing <= 0:
                        self._change_state(GameState.TIME_S_UP)
                    else:
                        self._pacman_dead = False
                        self._change_state(GameState.READY_CHECK)
            case GameState.WIN_LEVEL | GameState.GAME_OVER | GameState.TIME_S_UP:
                if self._game_timers.end_level > self._game_config.end_level_timer:
                    self._change_state(GameState.END_LEVEL)

    def on_notify(self, entity: Node | None, event: PacManEvent) -> None:
        """Apply scoring and life changes for a gameplay event.

        Args:
            entity: Event source or related gameplay entity.
            event: Gameplay event to apply to the score state.
        """

        def spawn_score_notification(score: int, entity: Node | None) -> None:
            score_notification = ScoreNotification(score)
            self.add_child(score_notification)

            if entity is not None and isinstance(entity, Node2D):
                score_notification.position = (
                    score_notification.convert_global_to_local(
                        entity.global_transform.position
                    )
                )

        match event:
            case PacManEvent.PACMAN_COLLIDES_WITH_GHOST:
                if not self._pacman_dead:
                    self._game_parameters.lose_life()
                    self._pacman_dead = True
                    self.score_event_handler.notify(
                        None,
                        (
                            "lives",
                            str(self._game_parameters.pac_man_remainig_lives),
                        ),
                    )
                    logger.debug(
                        "Remaining lives: %i",
                        self._game_parameters.pac_man_remainig_lives,
                    )
            case PacManEvent.PACMAN_COLLIDES_WITH_PAC_GUM:
                self._game_parameters.score += self._game_config.points_per_pacgum
                self.score_event_handler.notify(
                    None, ("current_score", str(self._game_parameters.score))
                )
                self._game_parameters.pacgums_count -= 1
                logger.debug("Current score: %i", self._game_parameters.score)
                logger.debug(
                    "Remaining Pac Gums: %i",
                    self._game_parameters.pacgums_count,
                )
            case PacManEvent.PACMAN_COLLIDES_WITH_SUPER_PAC_GUM:
                self._game_parameters.score += self._game_config.points_per_super_pacgum
                self._start_frightened_mode()
                self.score_event_handler.notify(
                    None, ("current_score", str(self._game_parameters.score))
                )
                logger.debug(
                    "Remaining Super Pac Gums: %i",
                    self._game_parameters.super_pacgums_count,
                )
                self._game_parameters.super_pacgums_count -= 1
            case PacManEvent.PACMAN_COLLIDES_WITH_FRIGHTENED_GHOST:
                score_increase = (
                    self._game_config.points_per_ghost * self._pacman_eat_ghost_combo
                )
                self._game_parameters.score += score_increase
                spawn_score_notification(score_increase, entity)
                self._pacman_eat_ghost_combo += 1
                self._start_frightened_mode()
                self.score_event_handler.notify(
                    None, ("current_score", str(self._game_parameters.score))
                )
            case PacManEvent.PACMAN_COLLIDES_WITH_BOOST:
                self._game_parameters.score += self._game_config.points_per_boost
                self.score_event_handler.notify(
                    None, ("current_score", str(self._game_parameters.score))
                )
                spawn_score_notification(self._game_config.points_per_boost, entity)
                logger.debug("Pacman collides with boost")
        logger.debug("Current score: %i", self._game_parameters.score)
        logger.debug(
            "Remaining lives: %i", self._game_parameters.pac_man_remainig_lives
        )

    @property
    def score(self) -> int:
        """Return the current score."""
        return self._game_parameters.score

    @property
    def lives(self) -> int:
        """Return the number of remaining Pac-Man lives."""
        return self._game_parameters.pac_man_remainig_lives
