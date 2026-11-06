from engine import NavAgent, NavGraph2D
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.assets.models.ghost import GhostColor

from .ghost import Ghost


class Blinky(Ghost):
    """Red ghost entity."""

    def __init__(
        self,
        graph: NavGraph2D,
        game_resource_manager: GameResourceManager,
        move_speed: float,
        frightened_time: float,
        flash_time: float,
        collision_box_scale: float,
    ) -> None:
        """Initialize Blinky.

        Args:
            graph: Navigation graph followed by the ghost.
            game_resource_manager: Loaded resource manager used for sprites.
            move_speed: Base movement speed in pixels per second.
            frightened_time: Duration of frightened mode in seconds.
            flash_time: Time before frightened mode ends when blinking starts.
            collision_box_scale: Scale applied to ghost collision circles.
        """
        super().__init__(
            game_resource_manager=game_resource_manager,
            color=GhostColor.RED,
            name="Blinky",
            nav_agent=NavAgent(graph=graph),
            move_speed=move_speed,
            frightened_time=frightened_time,
            flash_time=flash_time,
            collision_box_scale=collision_box_scale,
        )

    @property
    def start_position(self) -> int:
        """Index of the navigation node used as Blinky's spawn point."""
        return 10
