import random

import pyray

from engine import (
    Engine,
    NavAgent,
    NavGraph2D,
    NavNode2D,
    NavRegion2D,
    Node2D,
    Scene2D,
    Vector2,
)


def create_random_graph(num_nodes: int, max_edges_per_node: int) -> NavGraph2D:
    graph = NavGraph2D()

    for i in range(num_nodes):
        position = Vector2(
            pyray.get_random_value(0, pyray.get_render_width()),
            pyray.get_random_value(0, pyray.get_render_height()),
        )
        node = NavNode2D(id=i, position=position)
        graph.add_node(node)

    for node in graph.nodes:
        num_edges = pyray.get_random_value(1, max_edges_per_node)
        connected_nodes: set[NavNode2D] = set()
        sorted_nodes = sorted(
            (n for n in graph.nodes if n != node),
            key=lambda n: node.position.euclidean_distance(n.position),
        )
        for target_node in sorted_nodes:
            if len(connected_nodes) >= num_edges:
                break
            if len(target_node.edges) >= max_edges_per_node:
                continue
            if target_node not in connected_nodes:
                graph.link_nodes(node, target_node)
                connected_nodes.add(target_node)

    return graph


class Player(Node2D):
    def __init__(
        self,
        graph: NavGraph2D,
        name: str = "Agent",
    ) -> None:
        super().__init__(name)
        self.size = Vector2(10, 10)
        self.origin = self.size * 0.5
        self.graph = graph
        self.path_agent = NavAgent(graph=graph)
        self.move_speed = 100.0  # Units per second

    def _on_update(self, dt: float) -> None:
        if not self.path_agent.route or not self.path_agent.route.nodes:
            self.path_agent.set_target_node(random.choice(self.graph.nodes))

        if self.path_agent.route and self.path_agent.current_node:
            self.path_agent.move_along_route(dt * self.move_speed)
            current_position = self.path_agent.get_current_position_global()
            if current_position:
                self.position = self.convert_global_to_local(current_position)

    def _on_draw(self) -> None:
        pyray.draw_rectangle_pro(
            pyray.Rectangle(
                self.global_transform.position.x,
                self.global_transform.position.y,
                self.size.x,
                self.size.y,
            ),
            self.origin.to_pyray(),
            0,
            pyray.GREEN,
        )

        target = self.path_agent.target_node
        if target:
            pyray.draw_line(
                int(self.global_transform.position.x),
                int(self.global_transform.position.y),
                int(target.global_transform.position.x),
                int(target.global_transform.position.y),
                pyray.RED,
            )


class MapArena(Node2D):
    def __init__(self, name: str = "MapArena") -> None:
        super().__init__(name)
        self.graph = create_random_graph(num_nodes=100, max_edges_per_node=3)

        graph_max = Vector2(
            max(node.position.x for node in self.graph.nodes),
            max(node.position.y for node in self.graph.nodes),
        )

        self.graph_size = graph_max

        render_size = Vector2(pyray.get_render_width(), pyray.get_render_height())

        self.size = render_size * 0.8

        center_offset = Vector2(
            (render_size.x - self.size.x) / 2,
            (render_size.y - self.size.y) / 2,
        )
        self.position = center_offset

        self.nav_region = NavRegion2D(graph=self.graph, name="MapNavRegion")
        self.add_child(self.nav_region)
        self.nav_region.position = Vector2(self.size.x * 0.05, self.size.y * 0.05)
        self.nav_region.scale = Vector2(
            self.size.x * 0.9 / self.graph_size.x,
            self.size.y * 0.9 / self.graph_size.y,
        )
        # Recalculate edge costs after scaling the nav_region
        self.nav_region.recalculate_costs()

        agent = Player(graph=self.graph, name="Agent")
        agent.path_agent.set_current_node(self.graph.nodes[0])
        agent.path_agent.set_target_node(self.graph.nodes[-1])
        self.add_child(agent)

    def _on_draw(self) -> None:
        pyray.draw_rectangle_pro(
            pyray.Rectangle(
                self.global_transform.position.x,
                self.global_transform.position.y,
                self.size.x,
                self.size.y,
            ),
            Vector2(0, 0).to_pyray(),
            0,
            pyray.ORANGE,
        )


class MainScene(Scene2D):
    def _on_enter(self) -> None:
        map_arena = MapArena(name="MapArena")
        self.root.add_child(map_arena)


if __name__ == "__main__":
    NavRegion2D.DEBUG_DRAW = True
    engine_config = Engine.Config(
        title="Path Finding Example",
        virtual_screen_dimensions=(1920, 1080),
    )
    engine = Engine(config=engine_config)
    engine.scene_manager.push(MainScene(name="Main Scene"))
    engine.run()
