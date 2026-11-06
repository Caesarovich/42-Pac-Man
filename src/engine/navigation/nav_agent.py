import pyray

from engine import Vector2
from engine.navigation.nav_graph2d import (
    NavEdge2D,
    NavGraph2D,
    NavNode2D,
    NavRoute,
)
from engine.navigation.path_finding import AStarPathfinder, Pathfinder


class NavAgent:
    """
    Represents an agent that can navigate through a 2D navigation graph.
    The agent can find routes between nodes and move along those routes.
    """

    def __init__(self, graph: NavGraph2D, pathfinder: Pathfinder | None = None) -> None:
        self.graph = graph
        self.current_node: NavNode2D | None = None
        self.target_node: NavNode2D | None = None
        self.route: NavRoute | None = None
        self.pathfinding_algorithm: Pathfinder = (
            pathfinder if pathfinder is not None else AStarPathfinder()
        )
        self.distance_traveled: float = 0.0

    # PUBLIC METHODS
    def set_current_node(self, node: NavNode2D) -> None:
        """
        Set the current node of the agent.
        This is typically used to initialize the agent's position in the graph.
        """
        self.current_node = node
        self.distance_traveled = 0.0

    def set_target_node(self, node: NavNode2D) -> None:
        """
        Set the target node of the agent.
        This initializes the route finding process.
        """
        self.target_node = node
        self.distance_traveled = 0.0
        if self.current_node and self.target_node:
            self.route = self.find_route(self.current_node, self.target_node)
            if self.route:
                self.route.nodes.pop(0)
            self.distance_traveled = 0.0

    def find_route(self, start_node: NavNode2D, end_node: NavNode2D) -> NavRoute | None:
        """
        Find a route from start_node to end_node using
        the specified pathfinding algorithm.
        Returns a NavRoute if a path is found, otherwise returns None.
        """
        return self.pathfinding_algorithm.find_route(self.graph, start_node, end_node)

    def move_along_route(self, distance: float) -> None:
        """
        Move the agent along the current route by a specified distance.
        Updates the current node based on the movement.
        """
        if not self.route or not self.current_node:
            return

        remaining_distance = distance
        while remaining_distance > 0 and self.route.nodes:
            next_node = self._get_next_node()
            edge = self._get_next_edge()

            if not next_node or not edge:
                break

            current_pos = self.current_node.global_transform.position
            next_pos = next_node.global_transform.position
            edge_length = current_pos.euclidean_distance(next_pos)

            remaining_edge_distance = edge_length - self.distance_traveled
            if remaining_distance >= remaining_edge_distance:
                self.current_node = next_node
                self.route.nodes.pop(0)
                remaining_distance -= remaining_edge_distance
                self.distance_traveled = 0.0
            else:
                self.distance_traveled += remaining_distance
                remaining_distance = 0

    def get_current_position_global(self) -> Vector2 | None:
        """
        Get the current global position of the agent along the route.
        If the agent is at a node, returns that node's position.
        If the agent is moving along an edge,
        returns the interpolated position.
        """
        if not self.current_node:
            return None

        if not self.route or not self.route.nodes:
            return self.current_node.global_transform.position

        edge = self._get_next_edge()
        if not edge:
            return self.current_node.global_transform.position

        return edge.get_travel_position_distance(self.distance_traveled)

    # PRIVATE METHODS
    def _get_next_node(self) -> NavNode2D | None:
        if self.route and self.route.nodes:
            return self.route.nodes[0]
        return None

    def _get_next_edge(self) -> NavEdge2D | None:
        next_node = self._get_next_node()
        if not next_node or not self.current_node:
            return None

        valid_edges = (e for e in self.current_node.edges if e.node_to == next_node)
        return next(valid_edges, None)

    def _debug_draw_route(self) -> None:
        """
        Debug draw the agent's current route using pyray.
        """
        if self.current_node:
            pyray.draw_circle(
                int(self.current_node.global_transform.position.x),
                int(self.current_node.global_transform.position.y),
                5,
                pyray.RED,
            )

        if self.route:
            for i in range(len(self.route.nodes) - 1):
                start_node = self.route.nodes[i]
                end_node = self.route.nodes[i + 1]
                pyray.draw_line(
                    int(start_node.global_transform.position.x),
                    int(start_node.global_transform.position.y),
                    int(end_node.global_transform.position.x),
                    int(end_node.global_transform.position.y),
                    pyray.BLUE,
                )

        if self.route and self.route.nodes:
            last_node = self.route.nodes[-1]
            pyray.draw_circle(
                int(last_node.global_transform.position.x),
                int(last_node.global_transform.position.y),
                5,
                pyray.GREEN,
            )

    def _debug_draw_target_node(self) -> None:
        """
        Debug draw the agent's target and line to the target node using pyray.
        """
        if self.target_node:
            pyray.draw_circle(
                int(self.target_node.global_transform.position.x),
                int(self.target_node.global_transform.position.y),
                5,
                pyray.YELLOW,
            )

        pos = self.get_current_position_global()
        if pos and self.target_node:
            pyray.draw_line(
                int(pos.x),
                int(pos.y),
                int(self.target_node.global_transform.position.x),
                int(self.target_node.global_transform.position.y),
                pyray.YELLOW,
            )
