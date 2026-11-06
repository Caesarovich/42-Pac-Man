import itertools
import logging
from collections.abc import Callable
from typing import cast

from engine import (
    Tilemap,
    Tileset,
    Vector2,
)
from pac_man.assets.maze_assets import (
    MazeTileID,
    MazeTileset,
)
from pac_man.entities.collisions.pac_man_collisions_layers import (
    CollisionLayer,
)
from pac_man.maze.maze_tile_resolver import MazeTileResolver
from pac_man.mazegen_utils.maze_wrapper import MazeWrapper

logger = logging.getLogger(__name__)


class Maze(Tilemap):
    """Tilemap representation of a generated Pac-Man maze."""

    def __init__(
        self,
        maze_data: list[list[int]],
        tileset: MazeTileset,
    ) -> None:
        """Initialize maze data, resolver, and tilemap dimensions.

        Args:
            maze_data: Raw generated maze matrix.
            tileset: Tileset used to resolve and render maze tiles.
        """
        self.maze_data = maze_data
        self._maze_wrapper = MazeWrapper(maze_data)
        self.maze_size = Vector2(len(maze_data[0]) * 3, len(maze_data) * 3)
        self._tile_resolver = MazeTileResolver(self._maze_wrapper, tileset)
        super().__init__(
            name="MazeTilemap",
            tileset=cast(Tileset, tileset),
            width=int(self.maze_size.x),
            height=int(self.maze_size.y),
            chunk_size=4,
        )

    def _on_enter_tree(self) -> None:
        """Build render layers, collision layers, and navigation graph."""
        self._init_layer("walls", 0, self._is_wall)
        self._init_layer("pac_gums", 1, self._is_pac_gum)
        self._init_layer("super_pac_gums", 2, self._is_super_pac_gum)
        self._init_collider("walls", CollisionLayer.MAZE, self._is_wall)
        self._init_collider("pac_gums", CollisionLayer.PAC_GUMS, self._is_pac_gum)
        self._init_collider(
            "super_pac_gums",
            CollisionLayer.SUPER_PAC_GUMS,
            self._is_super_pac_gum,
        )

        self.nav_region = self.collision_layer_to_navregion("walls")
        self.add_child(self.nav_region)
        logger.info("Maze is ready.")

    @property
    def pacgums_count(self) -> int:
        """Return the number of regular pac-gums currently in the maze."""
        return len(
            [
                tile
                for tile in itertools.chain.from_iterable(
                    self._layers["pac_gums"].tiles
                )
                if self._is_pac_gum(MazeTileID(tile))
            ]
        )

    @property
    def super_pacgums_count(self) -> int:
        """Return the number of super pac-gums currently in the maze."""
        return len(
            [
                tile
                for tile in itertools.chain.from_iterable(
                    self._layers["super_pac_gums"].tiles
                )
                if self._is_super_pac_gum(MazeTileID(tile))
            ]
        )

    @staticmethod
    def _is_wall(tile_id: MazeTileID | None) -> bool:
        """Return whether a tile ID represents a wall.

        Args:
            tile_id: Tile ID to test.

        Returns:
            ``True`` when the tile is a wall.
        """
        if tile_id is None:
            return False
        return tile_id.is_wall()

    @staticmethod
    def _is_pac_gum(tile_id: MazeTileID | None) -> bool:
        """Return whether a tile ID represents a pac-gum.

        Args:
            tile_id: Tile ID to test.

        Returns:
            ``True`` when the tile is a regular pac-gum.
        """
        if tile_id is None:
            return False
        return tile_id.is_pac_gum()

    @staticmethod
    def _is_super_pac_gum(tile_id: MazeTileID | None) -> bool:
        """Return whether a tile ID represents a super pac-gum.

        Args:
            tile_id: Tile ID to test.

        Returns:
            ``True`` when the tile is a super pac-gum.
        """
        if tile_id is None:
            return False
        return tile_id.is_super_pac_gum()

    def _set_tiles(
        self,
        layer_name: str,
        test_fct: Callable[[MazeTileID | None], bool],
        x: int,
        y: int,
        tile_ids: list[list[MazeTileID | None]],
    ) -> None:
        """Set the 3x3 rendered tile block for one maze cell.

        Args:
            layer_name: Render layer to update.
            test_fct: Predicate deciding whether a tile belongs on the layer.
            x: Maze cell x coordinate.
            y: Maze cell y coordinate.
            tile_ids: Resolved 3x3 tile IDs for the cell.
        """
        for j, i in itertools.product(range(3), repeat=2):
            tile_id = tile_ids[j][i]
            self.set_tile(
                layer_name,
                x * 3 + i,
                y * 3 + j,
                int(tile_id)
                if tile_id is not None and test_fct(tile_id)
                else int(MazeTileID.EMPTY),
            )

    def _init_layer(
        self,
        layer_name: str,
        z_index: int,
        test_tile: Callable[[MazeTileID | None], bool],
    ) -> None:
        """Initialize a rendered tile layer from maze data.

        Args:
            layer_name: Render layer name.
            z_index: Layer draw order.
            test_tile: Predicate deciding whether a tile belongs on the layer.
        """
        self.add_layer(layer_name, z_index=z_index)
        for y in range(len(self.maze_data)):
            for x in range(len(self.maze_data[0])):
                tile_ids = self._tile_resolver.get_tile_ids(x, y)
                self._set_tiles(layer_name, test_tile, x, y, tile_ids)

    def _set_collision_tiles(
        self,
        layer_name: str,
        test_tile_fct: Callable[[MazeTileID | None], bool],
        x: int,
        y: int,
        tile_ids: list[list[MazeTileID | None]],
    ) -> None:
        """Set the 3x3 collision tile block for one maze cell.

        Args:
            layer_name: Collision layer to update.
            test_tile_fct: Predicate deciding whether a tile collides.
            x: Maze cell x coordinate.
            y: Maze cell y coordinate.
            tile_ids: Resolved 3x3 tile IDs for the cell.
        """
        for j, i in itertools.product(range(3), repeat=2):
            tile_id = tile_ids[j][i]
            self.set_collision_tile(
                layer_name, x * 3 + i, y * 3 + j, test_tile_fct(tile_id)
            )

    def _init_collider(
        self,
        layer_name: str,
        collision_layer: int,
        test_tile_fct: Callable[[MazeTileID | None], bool],
    ) -> None:
        """Initialize a collision layer from maze data.

        Args:
            layer_name: Collision layer name.
            collision_layer: Bit flag used by collision masks.
            test_tile_fct: Predicate deciding whether a tile collides.
        """
        self.add_collision_layer(layer_name, collision_layer)
        for y in range(len(self.maze_data)):
            for x in range(len(self.maze_data[0])):
                tile_ids = self._tile_resolver.get_tile_ids(x, y)
                self._set_collision_tiles(layer_name, test_tile_fct, x, y, tile_ids)
