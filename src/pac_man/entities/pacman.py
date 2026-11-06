import math

from engine import (
    AnimatedSprite2D,
    CharacterBody2D,
    CollisionCircle2D,
    NavDirection,
    NavGraph2D,
    NavGraphMovementController,
    PlayerKeyboardInputComponent,
    SpriteFrame,
    Vector2,
)
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.entities.collisions.pac_man_collisions_layers import (
    CollisionLayer,
)


class PacMan(CharacterBody2D):
    """Player-controlled Pac-Man entity.

    Pac-Man owns the keyboard-driven navigation controller, the gameplay
    collision circle, the animated movement sprite, and the death animation.
    """

    def __init__(
        self,
        game_resource_manager: GameResourceManager,
        nav_graph: NavGraph2D,
        move_speed: float,
        collision_box_scale: float,
    ) -> None:
        """Initialize Pac-Man with navigation, input, and collision settings.

        Args:
            game_resource_manager: Loaded resource manager used for sprites.
            nav_graph: Navigation graph followed by Pac-Man.
            move_speed: Movement speed in pixels per second.
            collision_box_scale: Scale applied to the sprite-sized collision
                circle.
        """
        self._game_resource_manager = game_resource_manager
        self._nav_graph = nav_graph
        self._move_speed = move_speed
        self._start_position = 10
        self._alive = True

        sprite = self._make_sprite(game_resource_manager.entities_assets.pacman_sprite)

        input_component = PlayerKeyboardInputComponent()
        collision_box = CollisionCircle2D("pacman_collision_box")
        collision_box.collision_layer = CollisionLayer.PACMAN
        collision_box.collision_mask = (
            CollisionLayer.CHASE_GHOST
            | CollisionLayer.FRIGHTENED_GHOSTS
            | CollisionLayer.PAC_GUMS
            | CollisionLayer.SUPER_PAC_GUMS
        )
        collision_box.fit_to_sprite(sprite, collision_box_scale)
        self.graph_controller = NavGraphMovementController(self._nav_graph)
        input_component.event_handler.add_observer(self.graph_controller)

        super().__init__(
            name="pacman",
            input_component=input_component,
            sprite=sprite,
            collision_box=collision_box,
        )

    def _init_death_sprite(self) -> None:
        """Create and attach the disabled death animation sprite."""
        self._death_sprite = AnimatedSprite2D(
            frames=(self._game_resource_manager.entities_assets.dead_pacman_sprite),
            frame_duration=0.2,
            loop=False,
        )
        draw_size = self._death_sprite.get_draw_size()
        self._death_sprite.origin = (
            Vector2.from_pyray_vector2(draw_size) * 0.5 * self.global_transform.scale
        )
        self._death_sprite.enabled = False
        self._death_sprite.visible = False
        self.add_child(self._death_sprite)

    def run_death_animation(self) -> None:
        """Disable normal movement visuals and show the death animation."""
        self._alive = False
        if self._sprite is not None:
            self._sprite.enabled = False
            self._sprite.visible = False
        self._death_sprite.current_frame_index = 0
        self._death_sprite.enabled = True
        self._death_sprite.visible = True
        self._death_sprite.play()

    def reset(self) -> None:
        """Restore Pac-Man to the alive visual state."""
        self._death_sprite.enabled = False
        self._death_sprite.visible = False
        self._alive = True
        if self._sprite is not None:
            self._sprite.enabled = True
            self._sprite.visible = True
        self.graph_controller.set_initial_direction(NavDirection.RIGHT)

    def _make_sprite(self, frames: list[SpriteFrame]) -> AnimatedSprite2D:
        """Create the looping Pac-Man movement sprite.

        Args:
            frames: Sprite frames used by the animation.

        Returns:
            Configured animated sprite.
        """
        return AnimatedSprite2D(
            name="pacman_sprite",
            frames=frames,
            frame_duration=0.1,
            loop=True,
        )

    def _on_enter_tree(self) -> None:
        """Center sprite origins and create the death sprite on tree entry."""
        assert self._sprite is not None
        draw_size = self._sprite.get_draw_size()
        self._sprite.origin = (
            Vector2.from_pyray_vector2(draw_size) * 0.5 * self.global_transform.scale
        )
        self._init_death_sprite()
        return super()._on_enter_tree()

    def _on_update(self, dt: float) -> None:
        """Move Pac-Man while alive.

        Args:
            dt: Frame delta time in seconds.
        """
        if self._alive:
            self._navigate(dt)

    def _navigate(self, dt: float) -> None:
        """Advance Pac-Man on the navigation graph and orient the sprite.

        Args:
            dt: Frame delta time in seconds.
        """
        self.graph_controller.move_along_route(dt * self._move_speed)
        current_position = self.graph_controller.get_current_position_global()
        if current_position:
            self.position = self.convert_global_to_local(current_position)
        direction = self.graph_controller._current_direction
        if self.sprite is not None:
            match direction:
                case NavDirection.UP:
                    self.sprite.local_transform.rotation = 3 * math.pi / 2
                case NavDirection.RIGHT:
                    self.sprite.local_transform.rotation = 0.0
                case NavDirection.DOWN:
                    self.sprite.local_transform.rotation = math.pi / 2
                case NavDirection.LEFT:
                    self.sprite.local_transform.rotation = math.pi

    def init_position(self) -> None:
        """Place Pac-Man at the current navigation controller position."""
        current_position = self.graph_controller.get_current_position_global()
        if current_position:
            self.position = self.convert_global_to_local(current_position)

    @property
    def start_position(self) -> int:
        """Index of the navigation node used as Pac-Man's spawn point."""
        return 200
