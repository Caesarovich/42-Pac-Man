import pyray
from mazegenerator import MazeGenerator

from engine import Node2D, Vector2
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.maze.maze_tilemap import Maze


class MazeContainer(Node2D):
    """Scene node that generates, owns, and scales a maze tilemap."""

    def __init__(
        self,
        game_resource_manager: GameResourceManager,
        width: int,
        height: int,
        seed: int | None,
        size: Vector2 | None = None,
        name: str = "Mazes",
    ) -> None:
        """Initialize the container and generate maze data.

        Args:
            game_resource_manager: Loaded resource manager used for maze tiles.
            width: Generated maze width in cells.
            height: Generated maze height in cells.
            seed: Deterministic seed passed to the maze generator.
            size: Desired rendered maze size in pixels.
            name: Node name used in the scene tree.
        """
        super().__init__(name=name)

        self.size = size if size is not None else Vector2(900, 900)
        self.maze_data = self._generate_maze(width, height, seed)
        self._game_resource_manager = game_resource_manager
        self._tileset = game_resource_manager.maze_tileset
        self.maze = Maze(maze_data=self.maze_data, tileset=self._tileset)

    @staticmethod
    def _generate_maze(width: int, height: int, seed: int | None) -> list[list[int]]:
        """Generate raw maze data.

        Args:
            width: Maze width in cells.
            height: Maze height in cells.
            seed: Deterministic generation seed.

        Returns:
            Raw maze matrix produced by the maze generator.
        """
        generator = MazeGenerator(size=(width, height))
        generator.generate(seed=seed if seed is not None else 0)
        return generator.maze

    def _on_enter_tree(self) -> None:
        """Scale the maze tilemap to the requested size and attach it."""
        self.maze.scale = Vector2(
            self.size.x / (self.maze.maze_size.x * self._tileset.tile_size),
            self.size.y / (self.maze.maze_size.y * self._tileset.tile_size),
        )

        self.add_child(self.maze)

    def _on_draw(self) -> None:
        """Draw the maze border."""
        thickness = self._tileset.tile_size * self.maze.scale.x * 0.1
        pyray.draw_rectangle_lines_ex(
            pyray.Rectangle(
                self.position.x,
                self.position.y,
                self.size.x,
                self.size.y,
            ),
            thickness,
            pyray.Color(33, 33, 255, 255),
        )
