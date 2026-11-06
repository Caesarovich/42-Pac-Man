from engine import (
    AnimatedSprite2D,
    CharacterStateMachine,
    CollisionCircle2D,
    DirectionalSprite2D,
    NavAgent,
    NavGraph2D,
    NavNode2D,
    Node,
    Node2D,
    Sprite2D,
    SpriteFrame,
    Vector2,
)
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.assets.models.ghost import GhostColor
from pac_man.entities.collisions.pac_man_collisions_layers import (
    CollisionLayer,
)
from pac_man.entities.state_machine.ghost_states import (
    ChaseState,
    DeadState,
    FrightenedState,
    GhostState,
    ScatterState,
)
from pac_man.signals.pacman_events import PacManEvent

Direction = DirectionalSprite2D.SpriteDirection


class Ghost(Node2D):
    """Autonomous ghost entity driven by a navigation agent.

    A ghost owns directional sprites and collision boxes for each gameplay
    state. Its state machine switches between chase, frightened, and dead
    behaviors based on Pac-Man events.
    """

    DEBUG_DRAW: bool = False
    FREEZE: bool = False

    def __init__(
        self,
        game_resource_manager: GameResourceManager,
        color: GhostColor,
        name: str,
        nav_agent: NavAgent,
        move_speed: float,
        frightened_time: float,
        flash_time: float,
        collision_box_scale: float,
    ) -> None:
        """Initialize a ghost and its state-specific visual resources.

        Args:
            game_resource_manager: Loaded resource manager used for sprites.
            color: Ghost sprite color.
            name: Node name used in the scene tree.
            nav_agent: Agent used to navigate the maze graph.
            move_speed: Base movement speed in pixels per second.
            frightened_time: Duration of frightened mode in seconds.
            flash_time: Time before frightened mode ends when blinking starts.
            collision_box_scale: Scale applied to state collision circles.
        """
        super().__init__(name=name)
        self._move_speed: float = move_speed
        self._game_resource_manager = game_resource_manager
        self.color: GhostColor = color
        self.nav_agent: NavAgent = nav_agent
        self.nav_graph: NavGraph2D = nav_agent.graph
        self.frightened_time = frightened_time
        self.flash_time = flash_time
        self._collision_box_scale = collision_box_scale

        self._normal_sprite: DirectionalSprite2D = self._make_normal_sprite(
            frames=game_resource_manager.entities_assets.ghost_sprites[color]
        )
        self._scatter_sprite = self._normal_sprite.duplicate()
        self._frightened_sprite = AnimatedSprite2D(
            name=f"{self.name}_frightened",
            frames=game_resource_manager.entities_assets.fleeing_ghosts_sprite,
            frame_duration=0.1,
            loop=True,
        )
        self._blinking_sprite = AnimatedSprite2D(
            name=f"{self.name}_blinking",
            frames=(game_resource_manager.entities_assets.blinking_ghosts_sprite),
            frame_duration=0.1,
            loop=True,
        )
        self._dead_sprite = self._make_dead_sprite(
            game_resource_manager.entities_assets.ghost_eyes
        )
        self._state_machine = CharacterStateMachine[GhostState]()
        self._init_state_machine()

    def _init_state_machine(self) -> None:
        """Create ghost states and attach them to the state machine."""
        chase_state = ChaseState(
            self,
            self._normal_sprite,
            self._move_speed,
            CollisionCircle2D(),
            self.nav_agent,
            phase_duration=20,
        )
        chase_state.collision_box.collision_layer = CollisionLayer.CHASE_GHOST
        chase_state.collision_box.collision_mask = CollisionLayer.PACMAN
        chase_state.collision_box.fit_to_sprite(
            self._normal_sprite, self._collision_box_scale
        )
        self._state_machine.add_state(chase_state)

        scatter_state = ScatterState(
            self,
            self._scatter_sprite,
            self._move_speed,
            CollisionCircle2D(),
            self.nav_agent,
            phase_duration=7.0,
        )
        scatter_state.collision_box.collision_layer = CollisionLayer.CHASE_GHOST
        scatter_state.collision_box.collision_mask = CollisionLayer.PACMAN
        scatter_state.collision_box.fit_to_sprite(
            self._scatter_sprite, self._collision_box_scale
        )
        self._state_machine.add_state(scatter_state)

        frightened_state = FrightenedState(
            self,
            self._frightened_sprite,
            self._blinking_sprite,
            self._move_speed,
            CollisionCircle2D(),
            self.nav_agent,
        )
        frightened_state.collision_box.collision_layer = (
            CollisionLayer.FRIGHTENED_GHOSTS
        )
        frightened_state.collision_box.collision_mask = CollisionLayer.PACMAN
        frightened_state.collision_box.fit_to_sprite(
            self._frightened_sprite, self._collision_box_scale
        )
        self._state_machine.add_state(frightened_state)

        dead_state = DeadState(
            self,
            self._dead_sprite,
            self._move_speed,
            CollisionCircle2D(),
            self.nav_agent,
        )
        dead_state.collision_box.collision_layer = CollisionLayer.DEAD_GHOSTS
        dead_state.collision_box.fit_to_sprite(
            self._normal_sprite.current_sprite, self._collision_box_scale
        )
        self._state_machine.add_state(dead_state)

        self.add_child(self._state_machine)

    def on_notify(self, entity: Node | None, event: PacManEvent) -> None:
        """Forward gameplay events to the active ghost state.

        Args:
            entity: Event source or related entity.
            event: Gameplay event to process.
        """
        self._state_machine.on_notify(entity, event)

    @property
    def sprite(self) -> Sprite2D | None:
        """Current sprite exposed by the active ghost state."""
        if self._state_machine.current_state is not None:
            return self._state_machine.current_state.sprite
        return None

    @property
    def collision_box(self) -> CollisionCircle2D | None:
        """Current collision box exposed by the active ghost state."""
        if self._state_machine.current_state is not None:
            return self._state_machine.current_state.collision_box
        return None

    @property
    def move_speed(self) -> float:
        """Current movement speed exposed by the active ghost state."""
        if self._state_machine.current_state is not None:
            return self._state_machine.current_state.move_speed
        return 0.0

    def _make_normal_sprite(
        self, frames: dict[Direction, list[SpriteFrame]]
    ) -> DirectionalSprite2D:
        """Create the directional animated sprite for chase mode.

        Args:
            frames: Animation frames keyed by movement direction.

        Returns:
            Directional sprite using one animation per direction.
        """
        assert len(frames) == 4, "Expected 4 frames for each direction"
        directional_sprites = {
            direction: AnimatedSprite2D(
                name=f"{self.name}{direction.name.capitalize()}",
                frames=[frame for frame in frames[direction]],
                frame_duration=0.2,
                loop=True,
            )
            for i, direction in enumerate(Direction)
        }

        return DirectionalSprite2D(
            name=f"{self.name}Sprite",
            sprites=directional_sprites,
        )

    def _make_dead_sprite(
        self, frames: dict[Direction, SpriteFrame]
    ) -> DirectionalSprite2D:
        """Create the directional eye sprite used by dead ghosts.

        Args:
            frames: Eye sprite frames keyed by movement direction.

        Returns:
            Directional sprite using one static sprite per direction.
        """
        assert len(frames) == 4, "Expected 4 frames for each direction"
        directional_sprites = {
            direction: Sprite2D.from_sprite_frame(
                name=f"{self.name}_dead_{direction.name.capitalize()}",
                sprite_frame=frames[direction],
            )
            for direction in Direction
        }

        return DirectionalSprite2D(
            name=f"{self.name}_dead_Sprite",
            sprites=directional_sprites,
        )

    def _on_enter_tree(self) -> None:
        """Center the normal sprite origin when the ghost enters the tree."""
        draw_size = self._normal_sprite.current_sprite.get_draw_size()
        self._normal_sprite.origin = (
            Vector2.from_pyray_vector2(draw_size) * 0.5 * self.global_transform.scale
        )

    def _on_update(self, dt: float) -> None:
        """Navigate the ghost each frame.

        Args:
            dt: Frame delta time in seconds.
        """
        if self.FREEZE:
            return

        self._navigate(dt)

    def _on_draw(self) -> None:
        if self.DEBUG_DRAW:
            self.nav_agent._debug_draw_route()
            self.nav_agent._debug_draw_target_node()

    def _on_target_node_reached(self) -> None:
        if self._state_machine.current_state is not None:
            self._state_machine.current_state._on_target_node_reached()

    def _on_node_changed(self, old_node: NavNode2D, new_node: NavNode2D) -> None:
        if self._state_machine.current_state is not None:
            self._state_machine.current_state._on_node_changed(old_node, new_node)

    def _direction_to_target_node(self) -> Direction | None:
        """Compute the sprite direction from the next route node.

        Returns:
            Direction toward the next node, or ``None`` when no route is
            currently available.
        """
        if (
            not self.nav_agent
            or not self.nav_agent.current_node
            or not self.nav_agent.route
            or not self.nav_agent.route.nodes
        ):
            return None
        target_node = self.nav_agent.route.nodes[0]
        current_node = self.nav_agent.current_node
        direction_vector = target_node.position - current_node.position
        if abs(direction_vector.x) > abs(direction_vector.y):
            return Direction.RIGHT if direction_vector.x > 0 else Direction.LEFT
        else:
            return Direction.DOWN if direction_vector.y > 0 else Direction.UP

    def _navigate(self, dt: float) -> None:
        """Advance the ghost along its route and update its facing direction.

        Args:
            dt: Frame delta time in seconds.
        """
        if not self.nav_agent:
            return
        if not self.nav_agent.route or not self.nav_agent.route.nodes:
            self._on_target_node_reached()
        if self.nav_agent.route and self.nav_agent.current_node:
            if isinstance(self.sprite, DirectionalSprite2D):
                direction = self._direction_to_target_node()
                if direction is not None:
                    self.sprite.current_direction = direction

            current_node = self.nav_agent.current_node
            self.nav_agent.move_along_route(dt * self.move_speed)
            new_node = self.nav_agent.current_node
            if new_node != current_node:
                self._on_node_changed(current_node, new_node)
            current_position = self.nav_agent.get_current_position_global()
            if current_position:
                self.position = self.convert_global_to_local(current_position)

    def init_position(self) -> None:
        """Place the ghost at the current navigation agent position."""

        assert self.nav_agent.current_node is not None, "Spawn point must be set"
        self.spawn_point = self.nav_agent.current_node
        current_position = self.nav_agent.get_current_position_global()
        if current_position:
            self.position = self.convert_global_to_local(current_position)

    def reset(self) -> None:
        """Return the ghost to its spawn point and scatter state.

        Raises:
            AssertionError: If the scatter state has not been initialized.
        """
        self.nav_agent.set_current_node(self.spawn_point)
        scatter_state = self._state_machine.get_state(ScatterState)
        assert scatter_state is not None, "Scatter state not initialized"
        self._state_machine.change_to(scatter_state)
