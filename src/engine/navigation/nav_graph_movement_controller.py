from engine import (
    Node,
    Vector2,
)
from engine.input_component import KeyPressEvent
from engine.navigation.nav_graph2d import (
    NavDirection,
    NavEdge2D,
    NavGraph2D,
    NavNode2D,
)


class NavGraphMovementController:
    """Keyboard-driven movement controller for a navigation graph."""

    def __init__(self, nav_graph: NavGraph2D) -> None:
        """Initialize graph movement state.

        Args:
            nav_graph: Navigation graph used for movement.
        """
        self._nav_graph = nav_graph
        self._current_node: NavNode2D | None = None
        self._current_direction: NavDirection = NavDirection.RIGHT
        self._buffered_direction: NavDirection = NavDirection.RIGHT
        self._distance_travelled: float = 0.0

    def set_initial_direction(self, direction: NavDirection) -> None:
        """Reset the current and buffered movement directions.

        Args:
            direction: Direction to use for the next movement update.
        """
        self._current_direction = direction
        self._buffered_direction = direction

    def set_current_node(self, node: NavNode2D) -> None:
        """
        Set the current node of the agent.
        This is typically used to initialize the agent's position in the graph.
        """
        self._current_node = node
        self._distance_travelled = 0.0

    def on_notify(self, entity: Node | None, event: KeyPressEvent) -> None:
        """Buffer movement direction from keyboard events.

        Args:
            entity: Event source. It is unused for keyboard movement.
            event: Key press event to translate into a direction.
        """
        match event:
            case KeyPressEvent.KEY_UP:
                self._buffered_direction = NavDirection.UP
            case KeyPressEvent.KEY_DOWN:
                self._buffered_direction = NavDirection.DOWN
            case KeyPressEvent.KEY_LEFT:
                self._buffered_direction = NavDirection.LEFT
            case KeyPressEvent.KEY_RIGHT:
                self._buffered_direction = NavDirection.RIGHT
        if self._buffered_direction.is_opposite(self._current_direction):
            self._make_u_turn()

    def _make_u_turn(self) -> None:
        """Reverse direction while preserving edge progress."""
        if self._current_node is not None:
            next_node = self._get_next_node()
            current_pos = self._current_node.global_transform.position
            next_pos = next_node.global_transform.position
            edge_length = current_pos.euclidean_distance(next_pos)
            self._distance_travelled = edge_length - self._distance_travelled
            self._current_node = self._get_next_node()
        self._current_direction = self._buffered_direction

    def move_along_route(self, distance: float) -> None:
        """
        Move the agent along the current route by a specified distance.
        Updates the current node based on the movement.
        """
        if self._current_node is None:
            return

        remaining_distance = distance
        while remaining_distance > 0:
            next_node = self._get_next_node()
            edge = self._get_next_edge()

            if not next_node or not edge:
                self._current_direction = self._buffered_direction
                break

            current_pos = self._current_node.global_transform.position
            next_pos = next_node.global_transform.position
            edge_length = current_pos.euclidean_distance(next_pos)

            remaining_edge_distance = edge_length - self._distance_travelled
            if remaining_distance >= remaining_edge_distance:
                self._current_node = next_node
                remaining_distance -= remaining_edge_distance
                self._distance_travelled = 0.0
                if (
                    self._current_node.get_next_node(self._buffered_direction)
                    is not None
                ):
                    self._current_direction = self._buffered_direction
            else:
                self._distance_travelled += remaining_distance
                remaining_distance = 0

    def _get_next_node(self) -> NavNode2D:
        assert self._current_node is not None
        try:
            return next(
                edge.node_to
                for edge in self._current_node.edges
                if edge.get_travel_direction() == self._current_direction
            )
        except StopIteration:
            return self._current_node

    def _get_next_edge(self) -> NavEdge2D | None:
        next_node = self._get_next_node()
        if not next_node or not self._current_node:
            return None

        valid_edges = (e for e in self._current_node.edges if e.node_to == next_node)
        return next(valid_edges, None)

    def get_current_position_global(self) -> Vector2 | None:
        """
        Get the current global position of the agent along the route.
        If the agent is at a node, returns that node's position.
        If the agent is moving along an edge,
        returns the interpolated position.
        """
        if not self._current_node:
            return None

        edge = self._get_next_edge()
        if not edge:
            return self._current_node.global_transform.position

        return edge.get_travel_position_distance(self._distance_travelled)
