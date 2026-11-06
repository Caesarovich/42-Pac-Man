import pyray

from engine import Node2D
from engine.navigation.nav_graph2d import NavGraph2D


class NavRegion2D(Node2D):
    """
    Represents a 2D navigation region that contains a navigation graph.
    """

    DEBUG_DRAW: bool = False

    def __init__(
        self,
        graph: NavGraph2D,
        name: str = "NavRegion",
    ) -> None:
        super().__init__(name)
        self.graph = graph

        for node in self.graph.nodes:
            self.add_child(node)

    # PUBLIC METHODS
    def recalculate_costs(self) -> None:
        """
        Recalculate the costs of all edges in the navigation graph.
        This can be useful if the positions of nodes have changed
        or if the NavRegion2D has been moved or scaled.
        """
        for edge in self.graph.edges:
            edge.cost = int(
                edge.node_from.global_transform.position.euclidean_distance(
                    edge.node_to.global_transform.position
                )
            )

    # PRIVATE METHODS
    def _draw(self) -> None:
        super()._draw()
        if self.DEBUG_DRAW:
            self._debug_draw_edges()
            self._debug_draw_nodes()

    def _debug_draw_edges(self) -> None:
        for edge in self.graph.edges:
            t_from = edge.node_from.global_transform
            t_to = edge.node_to.global_transform
            pyray.draw_line(
                int(t_from.position.x),
                int(t_from.position.y),
                int(t_to.position.x),
                int(t_to.position.y),
                pyray.BLUE,
            )

    def _debug_draw_nodes(self) -> None:
        for node in self.graph.nodes:
            transform = node.global_transform
            pyray.draw_circle(
                int(transform.position.x),
                int(transform.position.y),
                5,
                pyray.RED,
            )
