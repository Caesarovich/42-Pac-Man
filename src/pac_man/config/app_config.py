from pydantic_settings import BaseSettings

from pac_man.config.engine_config import EngineConfig
from pac_man.config.resources_config import AssetsConfig


class AppConfig(BaseSettings):
    """Runtime configuration loaded from the application YAML file.

    Attributes:
        log_level: Python logging level used by the application.
        assets: Paths to the asset configuration files.
    """

    log_level: str
    assets: AssetsConfig
    engine: EngineConfig
