from logging import getLogger
from pathlib import Path

import pyray

from engine import SpriteSheet
from pac_man.assets.entities_assets import EntitiesAssets
from pac_man.assets.maze_assets import MazeTileset
from pac_man.config.config_loader import ConfigLoader

logger = getLogger(__name__)


class GameResourceManager:
    def __init__(self) -> None:
        self._loaded = False
        self._resources_path = Path(__file__).parents[1] / "resources"
        self._config_loader = ConfigLoader(self._resources_path)

    def _load_configs(self) -> None:
        logger.info("Loading game resource configurations...")
        self.app_config = self._config_loader.load_app_config("app_config.yaml")
        self.entities_assets_config = self._config_loader.load_sprite_sheet_config(
            self.app_config.assets.entities_assets_config
        )
        self.maze_assets_config = self._config_loader.load_sprite_sheet_config(
            self.app_config.assets.maze_assets_config
        )
        logger.info("Game resource configurations loaded.")

    def _load_sprite_sheets(self) -> None:
        logger.info("Loading sprite sheets...")
        self.entities_sprite_sheet = SpriteSheet.from_file(
            self._resources_path / self.entities_assets_config.file_name,
            self.entities_assets_config.sprite_width,
            self.entities_assets_config.sprite_height,
            self.entities_assets_config.padding_x,
            self.entities_assets_config.padding_y,
        )
        self.entities_assets = EntitiesAssets.from_sprite_sheet(
            self.entities_sprite_sheet, self.entities_assets_config
        )
        self.maze_sprite_sheet = SpriteSheet.from_file(
            self._resources_path / self.maze_assets_config.file_name,
            self.maze_assets_config.sprite_width,
            self.maze_assets_config.sprite_height,
            self.maze_assets_config.padding_x,
            self.maze_assets_config.padding_y,
        )
        self.maze_tileset = MazeTileset.from_sprite_sheet(
            self.maze_sprite_sheet, self.maze_assets_config
        )
        logger.info("Sprite sheets loaded.")

    def load(self) -> None:
        logger.info("Loading game resources...")
        if not self._loaded:
            self._load_configs()
            self._load_sprite_sheets()
            self._loaded = True

    def dispose(self) -> None:
        """
        Dispose of all game resources.
        """
        logger.info("Disposing of game resources...")
        if self._loaded:
            pyray.unload_texture(self.entities_sprite_sheet.texture)
            pyray.unload_texture(self.maze_sprite_sheet.texture)
            self._loaded = False
