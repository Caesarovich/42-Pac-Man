from dataclasses import dataclass

from engine import NavGraph2D, NavNode2D
from pac_man.entities.blinky import Blinky
from pac_man.entities.clyde import Clyde
from pac_man.entities.ghost import Ghost
from pac_man.entities.inky import Inky
from pac_man.entities.pinky import Pinky


@dataclass
class LevelSpawnPoints:
    """Navigation nodes used to spawn Pac-Man and each ghost.

    Attributes:
        pacman: Navigation node used as Pac-Man's spawn point.
        ghosts: Spawn nodes indexed by concrete ghost class.
    """

    pacman: NavNode2D
    ghosts: dict[type[Ghost], NavNode2D]

    def for_ghost(self, ghost: Ghost) -> NavNode2D:
        """Return the spawn node assigned to a ghost instance.

        Args:
            ghost: Ghost whose spawn point is requested.

        Returns:
            The navigation node assigned to the ghost's concrete class.

        Raises:
            KeyError: If the ghost class has no configured spawn point.
        """
        ghost_cls = type(ghost)
        return self.ghosts[ghost_cls]

    @classmethod
    def from_graph(cls, graph: NavGraph2D) -> LevelSpawnPoints:
        """Build level spawn points from navigation graph geometry.

        Args:
            graph: Navigation graph representing walkable maze positions.

        Returns:
            Spawn points for Pac-Man and all supported ghost classes.
        """
        pacman = cls._get_pacman_start_position(graph)
        ghosts = cls._get_ghost_start_positions(graph)
        return cls(pacman, ghosts)

    @staticmethod
    def _get_pacman_start_position(graph: NavGraph2D) -> NavNode2D:
        """Select the navigation node closest to the maze center.

        Args:
            graph: Navigation graph containing candidate nodes.

        Returns:
            The node nearest to the graph's geometric center.
        """
        nodes = graph.nodes
        nodes_by_pos = {(node.position.x, node.position.y): node for node in nodes}
        min_x = min(x for x, _ in nodes_by_pos)
        max_x = max(x for x, _ in nodes_by_pos)
        min_y = min(y for _, y in nodes_by_pos)
        max_y = max(y for _, y in nodes_by_pos)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        center_node = min(
            nodes,
            key=lambda node: (
                (node.position.x - center_x) ** 2 + (node.position.y - center_y) ** 2
            ),
        )
        return center_node

    @staticmethod
    def _get_ghost_start_positions(
        graph: NavGraph2D,
    ) -> dict[type[Ghost], NavNode2D]:
        """Assign one extreme graph corner to each ghost class.

        Args:
            graph: Navigation graph containing candidate nodes.

        Returns:
            Spawn nodes indexed by the four supported ghost classes.
        """
        nodes = graph.nodes
        nodes_by_pos = {(node.position.x, node.position.y): node for node in nodes}

        min_x = min(x for x, _ in nodes_by_pos)
        max_x = max(x for x, _ in nodes_by_pos)
        min_y = min(y for _, y in nodes_by_pos)
        max_y = max(y for _, y in nodes_by_pos)

        top_left = nodes_by_pos[(min_x, min_y)]
        top_right = nodes_by_pos[(max_x, min_y)]
        bottom_left = nodes_by_pos[(min_x, max_y)]
        bottom_right = nodes_by_pos[(max_x, max_y)]

        return {
            Clyde: top_left,
            Pinky: top_right,
            Blinky: bottom_left,
            Inky: bottom_right,
        }
