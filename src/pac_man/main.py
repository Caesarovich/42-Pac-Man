import logging
import sys
import traceback
from pathlib import Path

from engine import Engine, PostProcessingRenderer
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.assets.shaders import (
    BloomCompositeShader,
    BloomThresholdShader,
    CrtNewPixieShader,
    GaussianBlurShader,
)
from pac_man.config.config_loader import ConfigLoader
from pac_man.exceptions import PacManException
from pac_man.scenes.main_menu import MainMenu

from .logging import configure_logging

logger = logging.getLogger(__name__)


def error_handler(
    e: Exception, error_type: str, show_stack_trace: bool = False
) -> None:
    """Log and print an application error in a consistent format.

    Args:
        e: Exception raised by the application.
        error_type: Human-readable error category.
    """
    logger.error(f"{error_type} ({type(e).__name__}): {e!s}")
    if show_stack_trace:
        logger.error(traceback.format_exc())


def main(config_path: Path) -> None:
    """Run the Pac-Man application entry point."""
    try:
        resources_path = Path(__file__).parent / "resources"
        config_loader = ConfigLoader(resources_path)

        app_config = config_loader.load_app_config("app_config.yaml")
        configure_logging(app_config.log_level)

        game_config = config_loader.load_game_config(config_path)

        engine_config = Engine.Config(
            title=app_config.engine.title,
            virtual_screen_dimensions=(
                app_config.engine.virtual_screen_dimensions.x,
                app_config.engine.virtual_screen_dimensions.y,
            ),
            fps_limit=app_config.engine.fps_limit,
            show_fps=app_config.engine.show_fps,
        )
        engine = Engine(engine_config)

        grm = GameResourceManager()

        engine.initialize()
        grm.load()

        engine.render_pipeline.add_renderer(
            PostProcessingRenderer(
                [
                    BloomThresholdShader(threshold=0.8, knee=0.1),
                    GaussianBlurShader(spread=1, direction=(1.0, 0.0)),
                    GaussianBlurShader(spread=1, direction=(0.0, 1.0)),
                    BloomCompositeShader(intensity=0.6),
                    CrtNewPixieShader(),
                ]
            )
        )

        engine.scene_manager.push(
            MainMenu(
                name="MainMenu",
                game_resource_manager=grm,
                game_config=game_config,
            )
        )

        engine.run()
    except PacManException as e:
        error_handler(e, "Processing error")
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception as e:  # noqa: BLE001
        error_handler(e, "Unexpected error", True)
        sys.exit(1)
