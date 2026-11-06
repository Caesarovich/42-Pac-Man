import math
from typing import Protocol

import pyray

from engine import Node2D, Vector2
from engine.navigation.nav_graph2d import NavGraph2D, NavNode2D
from engine.navigation.nav_region2d import NavRegion2D


class Tileset(Protocol):
    atlas: pyray.Texture
    tile_size: int

    def get_tile(self, tile_id: int) -> pyray.Rectangle:
        """
        Get the rectangle representing the tile in the atlas.
        """
        ...


class TileLayer:
    def __init__(self, width: int, height: int, z_index: int) -> None:
        self.width = width
        self.height = height
        self.z_index = z_index

        self.tiles: list[list[int]] = [
            [-1 for _ in range(width)] for _ in range(height)
        ]

    def get_tile(self, x: int, y: int) -> int:
        """
        Get the tile at the specified position.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        else:
            raise IndexError("Tile position out of bounds.")

    def set_tile(self, x: int, y: int, tile_id: int) -> None:
        """
        Set the tile at the specified position.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = tile_id
        else:
            raise IndexError("Tile position out of bounds.")


class TileCollisionLayer:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.collision_layer: int = 0

        self.tiles: list[list[bool]] = [
            [False for _ in range(width)] for _ in range(height)
        ]

    def get_tile(self, x: int, y: int) -> bool:
        """
        Get the tile at the specified position.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        else:
            raise IndexError("Tile position out of bounds.")

    def set_tile(self, x: int, y: int, collides: bool) -> None:
        """
        Set the tile at the specified position.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self.tiles[y][x] = collides
        else:
            raise IndexError("Tile position out of bounds.")


class Tilemap(Node2D):
    """
    A 2D tilemap node that renders a grid of tiles from a tileset.
    """

    DEBUG_DRAW: bool = False

    def __init__(
        self,
        name: str,
        tileset: Tileset,
        width: int,
        height: int,
        chunk_size: int,
    ) -> None:
        super().__init__(name=name)
        self.tileset = tileset
        self.width = width
        self.height = height
        self.chunk_size = chunk_size

        self._layers: dict[str, TileLayer] = {}
        self._collision_layers: dict[str, TileCollisionLayer] = {}
        self._ordered_layers: list[TileLayer] = []

        self._dirty_chunks: set[tuple[int, int]] = {
            (x, y)
            for x in range((width + chunk_size - 1) // chunk_size)
            for y in range((height + chunk_size - 1) // chunk_size)
        }

        self._render_texture: pyray.RenderTexture | None = None
        self._chunk_render_texture: pyray.RenderTexture | None = None

    # PROPERTIES
    @property
    def render_texture(self) -> pyray.RenderTexture:
        """
        Get the render texture for the tilemap, creating it if necessary.
        """
        if self._render_texture is None:
            self._render_texture = pyray.load_render_texture(
                self.width * self.tileset.tile_size,
                self.height * self.tileset.tile_size,
            )
        return self._render_texture

    @property
    def chunk_render_texture(self) -> pyray.RenderTexture:
        """
        Get the render texture for a single chunk, creating it if necessary.
        """
        if self._chunk_render_texture is None:
            self._chunk_render_texture = pyray.load_render_texture(
                self.chunk_size * self.tileset.tile_size,
                self.chunk_size * self.tileset.tile_size,
            )
        return self._chunk_render_texture

    # PUBLIC METHODS
    def add_layer(self, name: str, z_index: int) -> None:
        """
        Add a new layer to the tilemap.
        """
        if name in self._layers:
            raise ValueError(f"Layer '{name}' already exists.")
        layer = TileLayer(self.width, self.height, z_index)
        self._layers[name] = layer
        self._order_layers()

    def get_tile(self, layer_name: str, x: int, y: int) -> int:
        """
        Get the tile at the specified position in the specified layer.
        """
        if layer_name not in self._layers:
            raise ValueError(f"Layer '{layer_name}' does not exist.")
        return self._layers[layer_name].get_tile(x, y)

    def set_tile(self, layer_name: str, x: int, y: int, tile_id: int) -> None:
        """
        Set the tile at the specified position in the specified layer.
        """
        if layer_name not in self._layers:
            raise ValueError(f"Layer '{layer_name}' does not exist.")
        self._layers[layer_name].set_tile(x, y, tile_id)

        chunk_x = x // self.chunk_size
        chunk_y = y // self.chunk_size
        self._dirty_chunks.add((chunk_x, chunk_y))

    def add_collision_layer(self, name: str, collision_layer: int) -> None:
        """
        Add a new collision layer to the tilemap.
        """
        if name in self._collision_layers:
            raise ValueError(f"Collision layer '{name}' already exists.")
        layer = TileCollisionLayer(self.width, self.height)
        layer.collision_layer = collision_layer
        self._collision_layers[name] = layer

    def get_collision_tile(self, layer_name: str, x: int, y: int) -> bool:
        """
        Get the collision tile at the
        specified position in the specified layer.
        """
        if layer_name not in self._collision_layers:
            raise ValueError(f"Collision layer '{layer_name}' does not exist.")
        return self._collision_layers[layer_name].get_tile(x, y)

    @property
    def collision_layers(self) -> dict[str, TileCollisionLayer]:
        return self._collision_layers

    def collision_layer_to_navregion(self, layer_name: str) -> NavRegion2D:
        """
        Convert a collision layer to a NavRegion2D.
        Each non-collidable tile will become a node in the navigation graph.
        """
        if layer_name not in self._collision_layers:
            raise ValueError(f"Collision layer '{layer_name}' does not exist.")

        collision_layer = self._collision_layers[layer_name]
        nav_graph = NavGraph2D()

        def _create_nodes() -> list[list[NavNode2D | None]]:
            nodes: list[list[NavNode2D | None]] = []

            for y in range(collision_layer.height):
                nodes.append([])
                for x in range(collision_layer.width):
                    if not collision_layer.get_tile(x, y):
                        node_id = len(nav_graph.nodes)
                        position = Vector2(
                            x * self.tileset.tile_size + self.tileset.tile_size / 2,
                            y * self.tileset.tile_size + self.tileset.tile_size / 2,
                        )
                        node = NavNode2D(node_id, position)
                        nav_graph.add_node(node)
                        nodes[y].append(node)
                    else:
                        nodes[y].append(None)
            return nodes

        nodes = _create_nodes()

        def _link_neighbors(x: int, y: int) -> None:
            node = nodes[y][x]
            if node is None:
                return
            if x + 1 < collision_layer.width:
                right_node = nodes[y][x + 1]
                if right_node is not None:
                    nav_graph.link_nodes(node, right_node)

            if y + 1 < collision_layer.height:
                bottom_node = nodes[y + 1][x]
                if bottom_node is not None:
                    nav_graph.link_nodes(node, bottom_node)

        for y in range(collision_layer.height):
            for x in range(collision_layer.width):
                _link_neighbors(x, y)

        return NavRegion2D(nav_graph)

    def set_collision_tile(
        self, layer_name: str, x: int, y: int, collides: bool
    ) -> None:
        """
        Set the collision tile at the
        specified position in the specified layer.
        """
        if layer_name not in self._collision_layers:
            raise ValueError(f"Collision layer '{layer_name}' does not exist.")
        self._collision_layers[layer_name].set_tile(x, y, collides)

    def get_destination_rectangle(self) -> pyray.Rectangle:
        """
        Get the destination rectangle for drawing
        the tilemap based on its global transform and size.
        """
        map_size = self._get_map_size()
        transform = self.global_transform
        return pyray.Rectangle(
            transform.position.x,
            transform.position.y,
            map_size.x * transform.scale.x,
            map_size.y * transform.scale.y,
        )

    def get_current_tile(self, obj_global_position: Vector2) -> tuple[int, int]:
        global_transform = self.global_transform
        global_tile_width = self.tileset.tile_size * global_transform.scale.x
        global_tile_height = self.tileset.tile_size * global_transform.scale.y
        tilemap_global_position = global_transform.position

        obj_local_position = obj_global_position - tilemap_global_position
        obj_x = int(obj_local_position.x // global_tile_width)
        obj_y = int(obj_local_position.y // global_tile_height)
        return obj_x, obj_y

    # PRIVATE METHODS
    def _order_layers(self) -> None:
        """
        Order the layers based on their z-index.
        """
        self._ordered_layers = sorted(
            self._layers.values(), key=lambda layer: layer.z_index
        )

    def _get_map_size(self) -> Vector2:
        """
        Get the size of the tilemap in pixels.
        """
        return Vector2(
            self.width * self.tileset.tile_size,
            self.height * self.tileset.tile_size,
        )

    def _build_chunk(self, x: int, y: int) -> None:
        """
        Build a specific chunk of the tilemap into the render texture.
        """
        offset_x, offset_y = x * self.chunk_size, y * self.chunk_size

        if offset_x >= self.width or offset_y >= self.height:
            raise ValueError(f"Chunk {x},{y} is out of range")

        max_y = min(offset_y + self.chunk_size, self.height)
        max_x = min(offset_x + self.chunk_size, self.width)

        pyray.begin_texture_mode(self.chunk_render_texture)
        pyray.clear_background(pyray.BLACK)

        for tile_y in range(max_y - offset_y):
            for tile_x in range(max_x - offset_x):
                map_x = offset_x + tile_x
                map_y = offset_y + tile_y

                for layer in self._ordered_layers:
                    tile_id = layer.get_tile(map_x, map_y)
                    src_rect = self.tileset.get_tile(tile_id)
                    x_pos = tile_x * self.tileset.tile_size
                    y_pos = tile_y * self.tileset.tile_size

                    dest_rect = pyray.Rectangle(
                        x_pos,
                        y_pos,
                        self.tileset.tile_size,
                        self.tileset.tile_size,
                    )
                    pyray.draw_texture_pro(
                        self.tileset.atlas,
                        src_rect,
                        dest_rect,
                        pyray.Vector2(0, 0),
                        0,
                        pyray.WHITE,
                    )

        pyray.end_texture_mode()

        dest_rect = pyray.Rectangle(
            offset_x * self.tileset.tile_size,
            offset_y * self.tileset.tile_size,
            self.chunk_render_texture.texture.width,
            self.chunk_render_texture.texture.height,
        )

        pyray.begin_texture_mode(self.render_texture)
        pyray.draw_texture_pro(
            self.chunk_render_texture.texture,
            pyray.Rectangle(
                0,
                0,
                self.chunk_render_texture.texture.width,
                -self.chunk_render_texture.texture.height,
            ),
            dest_rect,
            pyray.Vector2(0, 0),
            0,
            pyray.WHITE,
        )
        pyray.end_texture_mode()

    def _build_dirty_chunks(self) -> None:
        """
        Build all dirty chunks of the tilemap into the render texture.
        """
        if not self._dirty_chunks:
            return

        for chunk in self._dirty_chunks:
            self._build_chunk(*chunk)
        self._dirty_chunks.clear()

    def _update(self, dt: float) -> None:
        self._build_dirty_chunks()
        super()._update(dt)

    def _draw(self) -> None:
        src_rect = pyray.Rectangle(
            0,
            0,
            self.render_texture.texture.width,
            -self.render_texture.texture.height,
        )

        dest_rect = self.get_destination_rectangle()

        pyray.draw_texture_pro(
            self.render_texture.texture,
            src_rect,
            dest_rect,
            self.global_transform.origin.to_pyray(),
            math.degrees(self.global_transform.rotation),
            pyray.WHITE,
        )

        super()._draw()

        if self.DEBUG_DRAW:
            self._debug_draw()

    def _debug_draw(self) -> None:
        """
        Draw debug information for the tilemap.
        """
        map_size = self._get_map_size()
        transform = self.global_transform
        pyray.draw_rectangle_lines(
            int(transform.position.x),
            int(transform.position.y),
            int(map_size.x * transform.scale.x),
            int(map_size.y * transform.scale.y),
            pyray.RED,
        )

        for y in range(self.height):
            for x in range(self.width):
                tile_id = self.get_tile("walls", x, y)
                if tile_id != -1:
                    dest_rect = pyray.Rectangle(
                        transform.position.x
                        + x * self.tileset.tile_size * transform.scale.x,
                        transform.position.y
                        + y * self.tileset.tile_size * transform.scale.y,
                        self.tileset.tile_size * transform.scale.x,
                        self.tileset.tile_size * transform.scale.y,
                    )
                    pyray.draw_rectangle_lines_ex(dest_rect, 1, pyray.GREEN)

        for chunk_y in range((self.height + self.chunk_size - 1) // self.chunk_size):
            for chunk_x in range((self.width + self.chunk_size - 1) // self.chunk_size):
                max_x = min((chunk_x + 1) * self.chunk_size, self.width)
                max_y = min((chunk_y + 1) * self.chunk_size, self.height)

                dest_rect = pyray.Rectangle(
                    transform.position.x
                    + chunk_x
                    * self.chunk_size
                    * self.tileset.tile_size
                    * transform.scale.x,
                    transform.position.y
                    + chunk_y
                    * self.chunk_size
                    * self.tileset.tile_size
                    * transform.scale.y,
                    (max_x - chunk_x * self.chunk_size)
                    * self.tileset.tile_size
                    * transform.scale.x,
                    (max_y - chunk_y * self.chunk_size)
                    * self.tileset.tile_size
                    * transform.scale.y,
                )
                pyray.draw_rectangle_lines_ex(dest_rect, 1, pyray.PINK)
