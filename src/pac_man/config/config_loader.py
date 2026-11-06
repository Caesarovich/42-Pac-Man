import json
import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from pac_man.config.app_config import AppConfig
from pac_man.config.game_config import GameConfig
from pac_man.config.resources_config import SpriteSheetConfig
from pac_man.exceptions import PacManException

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and validate resource-backed configuration files.

    Configuration files are resolved from the resources directory.
    """

    def __init__(self, resources_path: Path) -> None:
        """Initialize the loader.

        Args:
            resources_path: Directory containing application resources.
        """
        self._resources_path = resources_path

    def _load_yaml(self, file_name: str) -> dict[str, Any]:
        """Read a YAML file from the resources directory.

        Args:
            file_name: File name relative to the resources directory.

        Returns:
            Parsed YAML content.

        Raises:
            PacManException: If the file cannot be read or parsed.
        """
        file_path = self._resources_path / file_name
        try:
            content_txt = file_path.read_text()
            content_obj: dict[str, Any] = yaml.safe_load(content_txt)
        except (OSError, yaml.YAMLError) as e:
            raise PacManException(e) from e
        return content_obj

    def load_app_config(self, config_file: str) -> AppConfig:
        """Load and validate the application configuration.

        Args:
            config_file: Application configuration file name.

        Returns:
            Validated application configuration.

        Raises:
            PacManException: If the configuration is invalid.
        """
        content_obj = self._load_yaml(config_file)
        try:
            logger.info(f"Loading AppConfig ({config_file})...")
            config = AppConfig(**content_obj)
            logger.info("AppConfig loaded.")
            return config
        except ValidationError as e:
            raise PacManException(e) from e

    def load_sprite_sheet_config(self, config_file: str) -> SpriteSheetConfig:
        """Load and validate a sprite sheet configuration.

        Args:
            config_file: Sprite sheet configuration file name.

        Returns:
            Validated sprite sheet configuration.

        Raises:
            PacManException: If the configuration is invalid.
        """
        content_obj = self._load_yaml(config_file)
        try:
            logger.info(f"Loading SpriteSheetConfig ({config_file})...")
            config = SpriteSheetConfig(**content_obj)
            logger.info("SpriteSheetConfig loaded.")
            return config
        except ValidationError as e:
            raise PacManException(e) from e

    def _clean_game_config_comments(self, config_file: Path) -> str:
        """Read a game JSON configuration while dropping comment lines.

        Args:
            config_file: Game configuration file name.

        Returns:
            JSON content with lines starting with ``#`` removed.

        Raises:
            OSError: If the configuration file cannot be read.
        """
        file_path = config_file
        with file_path.open() as f:
            lines = (line for line in f.readlines() if not line.strip().startswith("#"))
        return "\n".join(lines)

    def load_game_config(self, config_file: Path) -> GameConfig:
        """Load and validate the gameplay configuration.

        Args:
            config_file: Game configuration file name.

        Returns:
            Validated gameplay configuration.

        Raises:
            PacManException: If the file cannot be read, parsed, or validated.
        """
        try:
            logger.info(f"Loading GameConfig ({config_file})...")
            text = self._clean_game_config_comments(config_file)
            config_dict = json.loads(text)
            game_config = GameConfig(**config_dict)
            logger.debug(
                "Game config:\n%s",
                game_config.model_dump_json(indent=4),
            )
            logger.info("GameConfig loaded.")
            return game_config
        except (ValidationError, OSError, json.JSONDecodeError) as e:
            raise PacManException(f"Game config loading error: {e}") from e
