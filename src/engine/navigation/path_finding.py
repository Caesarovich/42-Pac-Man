from engine.navigation.nav_graph2d import (
    NavGraph2D,
    NavNode2D,
    NavRoute,
)


class Pathfinder:
    def __init__(self) -> None:
        pass

    def find_route(
        self, graph: NavGraph2D, start_node: NavNode2D, end_node: NavNode2D
    ) -> NavRoute | None:
        """
        Find a route from start_node to end_node.
        Returns a NavRoute if a path is found, otherwise returns None.
        """
        return None


class AStarPathfinder(Pathfinder):
    def __init__(self) -> None:
        super().__init__()

    def heuristic(self, node_a: NavNode2D, node_b: NavNode2D) -> float:
        """
        Heuristic function for A* pathfinding.
        Uses Euclidean distance as the heuristic.
        """
        return node_a.position.euclidean_distance(node_b.position)

    def reconstruct_path(
        self, came_from: dict[NavNode2D, NavNode2D], current: NavNode2D
    ) -> NavRoute:
        """
        Reconstruct the path from the came_from map.
        """
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        total_path.reverse()
        return NavRoute(nodes=total_path)

    def find_route(
        self, graph: NavGraph2D, start_node: NavNode2D, end_node: NavNode2D
    ) -> NavRoute | None:
        visited: set[NavNode2D] = set()
        open_set: set[NavNode2D] = {start_node}
        came_from: dict[NavNode2D, NavNode2D] = {}
        g_score: dict[NavNode2D, float] = {node: float("inf") for node in graph.nodes}
        g_score[start_node] = 0
        f_score: dict[NavNode2D, float] = {node: float("inf") for node in graph.nodes}
        f_score[start_node] = self.heuristic(start_node, end_node)

        while open_set:
            current: NavNode2D = min(open_set, key=lambda node: f_score[node])
            if current == end_node:
                return self.reconstruct_path(came_from, current)

            open_set.remove(current)
            visited.add(current)

            for edge in current.edges:
                neighbor: NavNode2D = edge.node_to
                if neighbor in visited:
                    continue

                tentative_g_score = g_score[current] + edge.cost
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    h_score = self.heuristic(neighbor, end_node)
                    f_score[neighbor] = g_score[neighbor] + h_score
                    if neighbor not in open_set:
                        open_set.add(neighbor)

        return None
