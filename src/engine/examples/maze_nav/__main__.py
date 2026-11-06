import pyray
from mazegenerator import MazeGenerator

from engine import (
    Engine,
    Node2D,
    Scene2D,
    Vector2,
)
from engine.navigation import NavGraph2D, NavNode2D, NavRegion2D


def create_nav_graph_from_maze(maze: list[list[int]]) -> NavGraph2D:
    graph = NavGraph2D()
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0

    for row in range(rows):
        for col in range(cols):
            cell = maze[row][col]
            if cell == 0:  # Wall
                continue

            node = NavNode2D(id=len(graph.nodes), position=Vector2(col, row))
            graph.add_node(node)

    for row in range(rows):
        for col in range(cols):
            cell = maze[row][col]
            current_node = graph.nodes[row * cols + col]

            # Check North
            if cell & 0b0001 == 0 and row > 0 and maze[row - 1][col] != 0:
                north_node = graph.nodes[(row - 1) * cols + col]
                graph.link_nodes(current_node, north_node)

            # Check East
            if cell & 0b0010 == 0 and col < cols - 1 and maze[row][col + 1] != 0:
                east_node = graph.nodes[row * cols + (col + 1)]
                graph.link_nodes(current_node, east_node)

            # Check South
            if cell & 0b0100 == 0 and row < rows - 1 and maze[row + 1][col] != 0:
                south_node = graph.nodes[(row + 1) * cols + col]
                graph.link_nodes(current_node, south_node)

            # Check West
            if cell & 0b1000 == 0 and col > 0 and maze[row][col - 1] != 0:
                west_node = graph.nodes[row * cols + (col - 1)]
                graph.link_nodes(current_node, west_node)
    return graph


def clean_maze_graph(graph: NavGraph2D) -> None:
    # Remove nodes that have no edges (isolated nodes)
    graph.nodes = [node for node in graph.nodes if node.edges]


def print_maze(maze: list[list[int]]) -> None:
    for row in maze:
        print("".join(str(cell) for cell in row))


class MazeArena(Node2D):
    def __init__(self, maze: list[list[int]], name: str = "MazeArena") -> None:
        super().__init__(name)
        self.maze = maze
        self.graph = create_nav_graph_from_maze(maze)
        clean_maze_graph(self.graph)

        maze_size = Vector2(len(maze[0]), len(maze))
        render_size = Vector2(pyray.get_render_width(), pyray.get_render_height())

        cell_size = min(
            render_size.x / maze_size.x * 0.8,
            render_size.y / maze_size.y * 0.8,
        )
        self.cell_size = cell_size

        center_offset = Vector2(
            (render_size.x - maze_size.x * cell_size) / 2,
            (render_size.y - maze_size.y * cell_size) / 2,
        )
        print("Center offset for maze arena:", center_offset)
        self.position = center_offset

        self.nav_region = NavRegion2D(graph=self.graph, name="MazeNavRegion")
        self.add_child(self.nav_region)

        print(
            "Moving nav_region to position:",
            Vector2(cell_size / 2, cell_size / 2),
        )
        self.nav_region.position = Vector2(cell_size / 2, cell_size / 2)

        print("Setting nav_region scale to:", Vector2(cell_size, cell_size))
        self.nav_region.scale = Vector2(cell_size, cell_size)

    def _on_draw(self) -> None:
        pyray.draw_rectangle_pro(
            pyray.Rectangle(
                self.global_transform.position.x,
                self.global_transform.position.y,
                len(self.maze[0]) * self.cell_size,
                len(self.maze) * self.cell_size,
            ),
            Vector2(0, 0).to_pyray(),
            0,
            pyray.ORANGE,
        )


class MainScene(Scene2D):
    def _on_enter(self) -> None:
        generator = MazeGenerator(size=(15, 15), perfect=True)
        generator.generate(seed=42)

        maze_arena = MazeArena(maze=generator.maze, name="MazeArena")
        self.root.add_child(maze_arena)

        # nav_region = NavRegion2D(
        #     graph=maze_graph,
        #     name="MazeNavRegion",
        #     graph_scale=60
        # )

        # self.root.add_child(nav_region)


if __name__ == "__main__":
    NavRegion2D.DEBUG_DRAW = True
    engine_config = Engine.Config(
        title="Path Finding Example",
        virtual_screen_dimensions=(1920, 1080),
    )
    engine = Engine(config=engine_config)
    engine.scene_manager.push(MainScene(name="Main Scene"))
    engine.run()
