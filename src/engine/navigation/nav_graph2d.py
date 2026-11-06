from dataclasses import dataclass, field
from enum import Enum, auto

from engine import Node2D, Vector2


class NavDirection(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

    def is_opposite(self, direction: NavDirection) -> bool:
        match self:
            case NavDirection.UP:
                return direction is NavDirection.DOWN
            case NavDirection.DOWN:
                return direction is NavDirection.UP
            case NavDirection.LEFT:
                return direction is NavDirection.RIGHT
            case NavDirection.RIGHT:
                return direction is NavDirection.LEFT


class NavNode2D(Node2D):
    """
    Represents a node in a 2D navigation graph.
    Each node has a unique ID, a position in 2D space,
    and a list of edges that connect it to other nodes.
    """

    def __init__(self, id: int, position: Vector2) -> None:
        super().__init__(name=f"NavNode_{id}")
        self.id = id
        self.position = position
        self.edges: list[NavEdge2D] = []

    def get_next_node(self, direction: NavDirection) -> NavNode2D | None:
        try:
            return next(
                edge.node_to
                for edge in self.edges
                if edge.get_travel_direction() == direction
            )
        except StopIteration:
            return None


@dataclass
class NavEdge2D:
    """
    Represents an edge in a 2D navigation graph.
    Each edge connects two nodes and has a cost associated with it.
    """

    id: int
    cost: float
    node_from: NavNode2D
    node_to: NavNode2D

    def get_travel_position(self, t: float) -> Vector2:
        """
        Get the position along the edge based on a parameter t (0 <= t <= 1).
        t=0 returns the start node's position,
        and t=1 returns the end node's position.
        """
        assert 0 <= t <= 1, "Parameter t must be in the range [0, 1]"
        pos_from = self.node_from.global_transform.position
        pos_to = self.node_to.global_transform.position
        return pos_from * (1 - t) + pos_to * t

    def get_travel_position_distance(self, distance: float) -> Vector2:
        """
        Get the position along the edge based
        on a distance from the start node.
        If the distance exceeds the edge's cost,
        it will return the end node's position.
        """
        from_pos = self.node_from.global_transform.position
        to_pos = self.node_to.global_transform.position
        edge_length = from_pos.euclidean_distance(to_pos)
        if distance >= edge_length:
            return to_pos
        t = distance / edge_length
        return self.get_travel_position(t)

    def get_travel_direction(self) -> NavDirection:
        pos_from = self.node_from.global_transform.position
        pos_to = self.node_to.global_transform.position
        dx = pos_to.x - pos_from.x
        dy = pos_to.y - pos_from.y
        if abs(dx) > abs(dy):
            return NavDirection.RIGHT if dx > 0 else NavDirection.LEFT
        else:
            return NavDirection.DOWN if dy > 0 else NavDirection.UP


@dataclass
class NavGraph2D:
    """
    Represents a 2D navigation graph consisting of nodes and edges.
    Provides methods to add nodes and edges, and to link nodes together.
    """

    nodes: list[NavNode2D] = field(default_factory=list)
    edges: list[NavEdge2D] = field(default_factory=list)

    def add_node(self, node: NavNode2D) -> None:
        self.nodes.append(node)

    def add_edge(self, edge: NavEdge2D) -> None:
        self.edges.append(edge)

    def link_nodes(self, node_from: NavNode2D, node_to: NavNode2D) -> None:
        cost = node_from.global_transform.position.euclidean_distance(
            node_to.global_transform.position
        )

        edge = NavEdge2D(
            id=len(self.edges),
            cost=cost,
            node_from=node_from,
            node_to=node_to,
        )
        self.add_edge(edge)
        node_from.edges.append(edge)
        edge_reverse = NavEdge2D(
            id=len(self.edges),
            cost=cost,
            node_from=node_to,
            node_to=node_from,
        )
        self.add_edge(edge_reverse)
        node_to.edges.append(edge_reverse)


@dataclass
class NavRoute:
    nodes: list[NavNode2D] = field(default_factory=list)
    edges: list[NavEdge2D] = field(default_factory=list)
