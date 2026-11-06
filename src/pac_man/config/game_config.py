import logging
from typing import Annotated, Self

from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    ValidatorFunctionWrapHandler,
    WrapValidator,
    model_validator,
)
from pydantic_core import PydanticUseDefault

logger = logging.getLogger(__name__)


def apply_default(value: object, handler: ValidatorFunctionWrapHandler) -> object:
    try:
        return handler(value)
    except ValidationError as e:
        error_details = e.errors()[0]

        error_msg = error_details.get("msg", "Invalid value")
        provided_value = error_details.get("input", value)

        logger.warning(
            f"Validation failed - {error_msg}. "
            f"Provided value: {provided_value} "
            f"({type(provided_value).__name__}). "
            f"Switching to default."
        )

        raise PydanticUseDefault


class LevelConfig(BaseModel):
    """Configuration for one generated maze level.

    Attributes:
        width: Maze width in cells.
        height: Maze height in cells.
        seed: Seed used to generate the maze.
    """

    width: Annotated[int, Field(ge=3, le=30), WrapValidator(apply_default)] = 9
    height: Annotated[int, Field(ge=3, le=30), WrapValidator(apply_default)] = 9
    seed: int = 0

    @model_validator(mode="after")
    def check_level_is_square(self) -> Self:
        """Validate that the generated level is square.

        Returns:
            The validated config instance.

        Raises:
            ValueError: If the configured width and height differ.
        """
        if self.width != self.height:
            logger.warning("Only square maps are accepted, using default value.")
            self.width = self.height
        return self


class GameConfig(BaseModel):
    """Gameplay configuration loaded from the game JSON file.

    Attributes:
        ready_check_timer: Delay before gameplay starts, in seconds.
        game_timer: Available gameplay time per level, in seconds.
        pacman_death_timer: Duration of the death sequence, in seconds.
        end_level_timer: Delay before leaving a completed level, in seconds.
        max_levels: Number of levels required to complete the game.
        levels: Level definitions available to the game.
        lives: Number of player lives at the start of a game.
        points_per_pacgum: Score awarded for eating a regular pacgum.
        points_per_super_pacgum: Score awarded for eating a super pacgum.
        points_per_ghost: Score awarded for eating a frightened ghost.
        points_per_boost: Score awarded for collecting a boost.
        pacman_speed_boost_per_level: Pac-Man speed increase per level.
        ghosts_speed_boost_per_level: Ghost speed increase per level.
        frightened_time: Duration of ghost frightened mode in seconds.
        flash_time: Time before frightened mode ends when flashing starts.
        boost_duration: Duration of the boost effect in seconds.
        boost_spawn_chance: Probability of a boost spawning in a level.
        ghost_base_speed: Base ghost movement speed.
        pacman_base_speed: Base Pac-Man movement speed.
        ghost_collision_box_scale: Collision radius scale for ghosts.
        pacman_collision_box_scale: Collision radius scale for Pac-Man.
    """

    # Timers
    ready_check_timer: Annotated[float, Field(ge=0.0), WrapValidator(apply_default)] = (
        2.0
    )
    game_timer: Annotated[float, Field(ge=0.0), WrapValidator(apply_default)] = 90.0
    pacman_death_timer: Annotated[
        float, Field(ge=0.0), WrapValidator(apply_default)
    ] = 1.0
    end_level_timer: Annotated[float, Field(ge=0.0), WrapValidator(apply_default)] = 3.0

    # Level settings
    max_levels: Annotated[int, Field(ge=1, le=99), WrapValidator(apply_default)] = 10
    levels: Annotated[
        list[LevelConfig], Field(min_length=1), WrapValidator(apply_default)
    ] = [LevelConfig(width=9, height=9, seed=42)]

    # Game design parameters
    lives: Annotated[int, Field(ge=1, le=99), WrapValidator(apply_default)] = 3
    points_per_pacgum: Annotated[
        int, Field(ge=0, le=1000), WrapValidator(apply_default)
    ] = 10
    points_per_super_pacgum: Annotated[
        int, Field(ge=0, le=1000), WrapValidator(apply_default)
    ] = 50
    points_per_ghost: Annotated[
        int, Field(ge=0, le=1000), WrapValidator(apply_default)
    ] = 200
    points_per_boost: Annotated[
        int, Field(ge=0, le=1000), WrapValidator(apply_default)
    ] = 300
    pacman_speed_boost_per_level: Annotated[
        float, Field(ge=0.0, le=1.0), WrapValidator(apply_default)
    ] = 0.05
    ghosts_speed_boost_per_level: Annotated[
        float, Field(ge=0.0, le=1.0), WrapValidator(apply_default)
    ] = 0.05

    # Entities speed
    ghost_base_speed: Annotated[float, Field(ge=0.0), WrapValidator(apply_default)] = (
        2700.0
    )
    pacman_base_speed: Annotated[float, Field(ge=0.0), WrapValidator(apply_default)] = (
        3200.0
    )

    # Collision box parameters
    ghost_collision_box_scale: Annotated[
        float, Field(ge=0.0), WrapValidator(apply_default)
    ] = 0.6
    pacman_collision_box_scale: Annotated[
        float, Field(ge=0.0), WrapValidator(apply_default)
    ] = 0.6

    # Timers
    frightened_time: Annotated[float, Field(ge=0.0), WrapValidator(apply_default)] = 6.0
    flash_time: Annotated[float, Field(ge=0.0), WrapValidator(apply_default)] = 1.0
    boost_duration: Annotated[float, Field(ge=0.0), WrapValidator(apply_default)] = 20

    boost_spawn_chance: Annotated[
        float, Field(ge=0.0, le=1.0), WrapValidator(apply_default)
    ] = 0.1

    @model_validator(mode="after")
    def check_flash_time(self) -> Self:
        """Validate frightened mode timer consistency.

        Returns:
            The validated config instance.

        Raises:
            ValueError: If flash mode would start after frightened mode ends.
        """
        if self.flash_time >= self.frightened_time:
            logger.warning(
                "Invalid value for 'flash_time', it should be less or equal "
                "than 'frightened_time'. Using default value."
            )
            self.flash_time = self.frightened_time / 2
        return self
