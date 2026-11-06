import logging
from abc import ABC
from typing import TYPE_CHECKING

from engine import (
    CharacterState,
    CollisionCircle2D,
    NavAgent,
    NavNode2D,
    Node,
    Sprite2D,
    Vector2,
)

if TYPE_CHECKING:
    from pac_man.entities.ghost import Ghost
from pac_man.entities.pacman import PacMan
from pac_man.signals.pacman_events import PacManEvent

logger = logging.getLogger(__name__)


class GhostState(CharacterState, ABC):
    """Base state for ghost visuals, movement speed, and collisions."""

    def __init__(
        self,
        ghost: Ghost,
        sprite: Sprite2D,
        move_speed: float,
        collision_box: CollisionCircle2D,
        nav_agent: NavAgent,
        name: str | None = None,
    ) -> None:
        """Initialize shared ghost state data.

        Args:
            ghost: Ghost entity controlled by this state.
            sprite: Sprite shown while this state is active.
            move_speed: Base movement speed for this state.
            collision_box: Collision box enabled while this state is active.
            nav_agent: Navigation agent moved by the ghost.
            name: Optional state node name.
        """
        super().__init__(name)
        self._ghost = ghost
        self._move_speed = move_speed
        self._sprite = sprite
        self.collision_box = collision_box
        self.nav_agent = nav_agent

        self._sprite.visible = False
        self.collision_box.enabled = False

    def _on_enter_tree(self) -> None:
        """Attach the state's sprite and collision box to the ghost."""
        draw_size = self._sprite.get_draw_size()
        self._sprite.origin = (
            Vector2.from_pyray_vector2(draw_size) * 0.5 * self._ghost.scale
        )
        self._ghost.add_child(self._sprite)
        self._ghost.add_child(self.collision_box)

    def _on_target_node_reached(self) -> None:
        """Choose a random navigation target when the current route is done."""
        target_node = self._find_random_target_node()
        if target_node is not None:
            self.nav_agent.set_target_node(target_node)

    def _on_node_changed(self, old_node: NavNode2D, new_node: NavNode2D) -> None:
        pass

    def _find_random_target_node(self) -> NavNode2D | None:
        """Find a random node in the navigation graph."""
        import random

        assert self.nav_agent is not None, "nav_agent is not set"
        if not self.nav_agent.graph.nodes:
            return None
        return random.choice(self.nav_agent.graph.nodes)

    def on_enter(self) -> None:
        """Show the state sprite and enable its collision box."""
        self.sprite.visible = True
        self.collision_box.enabled = True

    def on_exit(self) -> None:
        """Hide the state sprite and disable its collision box."""
        self.sprite.visible = False
        self.collision_box.enabled = False

    @property
    def sprite(self) -> Sprite2D:
        """Sprite currently exposed by this state."""
        return self._sprite

    @property
    def move_speed(self) -> float:
        """Movement speed applied while this state is active."""
        return self._move_speed


class ScatterState(GhostState):
    """Placeholder state for future scatter behavior."""

    def __init__(
        self,
        ghost: Ghost,
        sprite: Sprite2D,
        move_speed: float,
        collision_box: CollisionCircle2D,
        nav_agent: NavAgent,
        phase_duration: float,
        name: str | None = None,
    ) -> None:
        """Initialize scatter state with a phase duration.

        Args:
            phase_duration: Duration of the scatter phase in seconds.
            ghost: Ghost entity controlled by this state.
            sprite: Sprite shown while this state is active.
            move_speed: Base movement speed for this state.
            collision_box: Collision box enabled while this state is active.
            nav_agent: Navigation agent moved by the ghost.
            name: Optional state node name.
        """
        super().__init__(ghost, sprite, move_speed, collision_box, nav_agent, name)
        self.phase_duration = phase_duration
        self._timer = 0.0

    def handle_event(self, entity: Node | None, event: PacManEvent) -> None:
        """Handle gameplay events while scattering

        Args:
            entity: Event source or related entity.
            event: Gameplay event to process.
        """
        match event:
            case PacManEvent.PACMAN_COLLIDES_WITH_SUPER_PAC_GUM:
                if self.state_machine is None:
                    return

                frightenend_state = self.state_machine.get_state(FrightenedState)
                if frightenend_state is None:
                    return

                self.state_machine.change_to(frightenend_state)

    def _update(self, dt: float) -> None:
        """Advance the scatter phase timer and transition to chase mode.

        Args:
            dt: Frame delta time in seconds.
        """
        self._timer += dt

    def reset_timer(self) -> None:
        """Reset the scatter phase timer to zero."""
        self._timer = 0.0

    def on_enter(self) -> None:
        """Choose a random navigation target when the state is entered."""
        super().on_enter()
        target_node = self._find_random_target_node()
        if target_node is not None:
            self.nav_agent.set_target_node(target_node)
        self.reset_timer()

    def _on_target_node_reached(self) -> None:
        """Choose a random navigation target when the current route is done."""
        if self._timer >= self.phase_duration and self.state_machine is not None:
            chase_state = self.state_machine.get_state(ChaseState)
            if chase_state is not None:
                self.state_machine.change_to(chase_state)
                return
        target_node = self._find_random_target_node()
        if target_node is not None:
            self.nav_agent.set_target_node(target_node)


class ChaseState(GhostState):
    """Default ghost state that can transition to frightened mode."""

    def __init__(
        self,
        ghost: Ghost,
        sprite: Sprite2D,
        move_speed: float,
        collision_box: CollisionCircle2D,
        nav_agent: NavAgent,
        phase_duration: float,
        name: str | None = None,
    ) -> None:
        """Initialize chase state with a phase duration.

        Args:
            phase_duration: Duration of the chase phase in seconds.
            ghost: Ghost entity controlled by this state.
            sprite: Sprite shown while this state is active.
            move_speed: Base movement speed for this state.
            collision_box: Collision box enabled while this state is active.
            nav_agent: Navigation agent moved by the ghost.
            name: Optional state node name.
        """
        super().__init__(ghost, sprite, move_speed, collision_box, nav_agent, name)
        self.phase_duration = phase_duration
        self._timer = 0.0

    def reset_timer(self) -> None:
        """Reset the chase phase timer to zero."""
        self._timer = 0.0

    def handle_event(self, entity: Node | None, event: PacManEvent) -> None:
        """Handle gameplay events while chasing Pac-Man.

        Args:
            entity: Event source or related entity.
            event: Gameplay event to process.
        """
        match event:
            case PacManEvent.PACMAN_COLLIDES_WITH_SUPER_PAC_GUM:
                if self.state_machine is None:
                    return

                frightenend_state = self.state_machine.get_state(FrightenedState)
                if frightenend_state is None:
                    return

                self.state_machine.change_to(frightenend_state)

    def _update(self, dt: float) -> None:
        """Advance the chase phase timer and transition to scatter mode.

        Args:
            dt: Frame delta time in seconds.
        """
        self._timer += dt

    def on_enter(self) -> None:
        super().on_enter()
        target_node = self._find_target_node()
        self.reset_timer()
        if target_node is not None:
            self.nav_agent.set_target_node(target_node)

    def _on_target_node_reached(self) -> None:
        """Choose a navigation target close to PacMan"""
        target_node = self._find_target_node()
        if target_node is not None:
            self.nav_agent.set_target_node(target_node)

    def _on_node_changed(self, old_node: NavNode2D, new_node: NavNode2D) -> None:
        """Update the navigation target when the ghost changes nodes."""
        import random

        if self._timer >= self.phase_duration and self.state_machine is not None:
            scatter_state = self.state_machine.get_state(ScatterState)
            if scatter_state is not None:
                self.state_machine.change_to(scatter_state)
                return

        target_node = self._find_target_node()
        if target_node is not None and random.random() < 0.2:
            self.nav_agent.set_target_node(target_node)

    def _find_target_node(self) -> NavNode2D | None:
        """
        Finds a node that is closest to pacman.
        """
        pacman = self.get_root().find_child("pacman", recursive=True)
        if pacman is None or not isinstance(pacman, PacMan):
            return None

        pacman_node = pacman.graph_controller._current_node
        if pacman_node is None:
            return None

        return pacman_node


class FrightenedState(GhostState):
    """Ghost state entered after Pac-Man eats a super pac-gum."""

    def __init__(
        self,
        ghost: Ghost,
        sprite: Sprite2D,
        blinking_sprite: Sprite2D,
        move_speed: float,
        collision_box: CollisionCircle2D,
        nav_agent: NavAgent,
        name: str | None = None,
    ) -> None:
        """Initialize frightened sprites and timing state.

        Args:
            ghost: Ghost entity controlled by this state.
            sprite: Base frightened sprite.
            blinking_sprite: Sprite shown during flash mode.
            move_speed: Base movement speed before frightened scaling.
            collision_box: Collision box enabled while frightened.
            nav_agent: Navigation agent moved by the ghost.
            name: Optional state node name.
        """
        super().__init__(ghost, sprite, move_speed, collision_box, nav_agent, name)
        self._blinking_sprite = blinking_sprite
        self._blinking_sprite.visible = False
        self._blinking_state = False
        self._frightened_mode_timer = 0.0

    def _on_enter_tree(self) -> None:
        """Attach the blinking sprite before the base state setup."""
        draw_size = self._sprite.get_draw_size()
        self._blinking_sprite.origin = (
            Vector2.from_pyray_vector2(draw_size) * 0.5 * self._ghost.scale
        )
        self._ghost.add_child(self._blinking_sprite)
        return super()._on_enter_tree()

    def on_enter(self) -> None:
        """Reset frightened timers and show the base frightened sprite."""
        self._blinking_state = False
        self._blinking_sprite.visible = False
        self._blinking_state = False
        self._frightened_mode_timer = 0.0
        target_node = self._find_target_node()
        if target_node is not None:
            self.nav_agent.set_target_node(target_node)
        super().on_enter()

    def on_exit(self) -> None:
        """Hide both frightened sprites and disable collisions."""
        self._sprite.visible = False
        self._blinking_sprite.visible = False
        self.collision_box.enabled = False

    def _update(self, dt: float) -> None:
        """Advance frightened timers and trigger flash/end transitions.

        Args:
            dt: Frame delta time in seconds.
        """
        self._frightened_mode_timer += dt
        if (
            not self._blinking_state
            and self._frightened_mode_timer
            >= self._ghost.frightened_time - self._ghost.flash_time
        ):
            self._start_flash_mode()

    @property
    def sprite(self) -> Sprite2D:
        """Current frightened sprite, including blinking mode."""
        return self._sprite if not self._blinking_state else self._blinking_sprite

    def _start_flash_mode(self) -> None:
        """Switch from the base frightened sprite to the blinking sprite."""
        self._sprite.visible = False
        self._blinking_sprite.visible = True
        self._blinking_state = True

    def _end_frightened_mode(self) -> None:
        """Return the ghost to chase mode after frightened mode expires."""
        if self.state_machine is not None:
            scatter_state = self.state_machine.get_state(ScatterState)

            if scatter_state is not None:
                self.state_machine.change_to(scatter_state)

    def _on_target_node_reached(self) -> None:
        """Choose a navigation target far from PacMan"""
        target_node = self._find_target_node()
        if target_node is not None:
            if target_node == self.nav_agent.current_node:
                target_node = target_node.edges[0].node_to
            self.nav_agent.set_target_node(target_node)

    def _on_node_changed(self, old_node: NavNode2D, new_node: NavNode2D) -> None:
        """Update the navigation target when the ghost changes nodes."""
        if self._frightened_mode_timer >= self._ghost.frightened_time:
            self._end_frightened_mode()

    def _find_target_node(self) -> NavNode2D | None:
        """
        Finds a node that is far from pacman.
        """
        pacman = self.get_root().find_child("pacman", recursive=True)
        if pacman is None or not isinstance(pacman, PacMan):
            return None

        pacman_node = pacman.graph_controller._current_node
        if pacman_node is None:
            return None

        all_nodes = self.nav_agent.graph.nodes

        farthest_node = None
        max_distance: float = -1
        for node in all_nodes:
            distance = pacman_node.position.manhattan_distance(node.position)
            if distance > max_distance:
                max_distance = distance
                farthest_node = node
        return farthest_node

    @property
    def move_speed(self) -> float:
        """Reduced
        movement speed while frightened."""
        return 0.7 * self._move_speed

    def handle_event(self, entity: Node | None, event: PacManEvent) -> None:
        """Handle events while the ghost can be eaten by Pac-Man.

        Args:
            entity: Event source or related ghost entity.
            event: Gameplay event to process.
        """
        match event:
            case PacManEvent.PACMAN_COLLIDES_WITH_FRIGHTENED_GHOST:
                if self.state_machine is None:
                    return

                if self._ghost is not entity:
                    return

                dead_state = self.state_machine.get_state(DeadState)
                if dead_state is None:
                    return

                self.state_machine.change_to(dead_state)
            case PacManEvent.PACMAN_COLLIDES_WITH_SUPER_PAC_GUM:
                if self.state_machine is None:
                    return

                frightenend_state = self.state_machine.get_state(FrightenedState)
                if frightenend_state is None:
                    return

                self.state_machine.change_to(frightenend_state)


class DeadState(GhostState):
    """Ghost state used after Pac-Man eats a frightened ghost."""

    @property
    def move_speed(self) -> float:
        """Increased movement speed while returning as ghost eyes."""
        return 2 * self._move_speed

    def on_enter(self) -> None:
        """Hide the ghost sprite and disable collisions while dead."""
        super().on_enter()
        self.nav_agent.set_target_node(self._ghost.spawn_point)

    def _on_target_node_reached(self) -> None:
        """Choose a random navigation target when the current route is done."""
        if self.state_machine is not None:
            scatter_state = self.state_machine.get_state(ScatterState)
            if scatter_state is not None:
                self.state_machine.change_to(scatter_state)
