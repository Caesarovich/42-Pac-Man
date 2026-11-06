from dataclasses import dataclass
from logging import getLogger
from typing import cast

import pyray

from engine import (
    RenderPipeline,
    SceneManager,
    SceneRenderer,
)

DEFAULT_UPSCALE_FILTER: pyray.TextureFilter = cast(
    pyray.TextureFilter, pyray.TextureFilter.TEXTURE_FILTER_BILINEAR
)

logger = getLogger(__name__)


class Engine:
    @dataclass
    class Config:
        virtual_screen_dimensions: tuple[int, int] = (800, 600)
        title: str = "Game Engine"
        upscale_filter: pyray.TextureFilter = DEFAULT_UPSCALE_FILTER
        fps_limit: int | None = None
        show_fps: bool = True

    def __init__(self, config: Engine.Config) -> None:
        self.config = config
        self.running = False
        self.scene_manager = SceneManager(self)
        self.render_pipeline = RenderPipeline(self.config.virtual_screen_dimensions)
        self.render_pipeline.upscale_filter = self.config.upscale_filter
        self.render_pipeline.show_fps = self.config.show_fps
        self.render_pipeline.add_renderer(SceneRenderer(self.scene_manager))

        self._initialized: bool = False

    # PUBLIC METHODS
    def initialize(self) -> None:
        """
        Initializes the game engine.
        This should be called before running the engine.
        """
        if self._initialized:
            return
        logger.info("Initializing game engine...")
        pyray.init_window(*self.config.virtual_screen_dimensions, self.config.title)
        pyray.set_window_state(pyray.ConfigFlags.FLAG_WINDOW_RESIZABLE)
        if self.config.fps_limit is not None:
            pyray.set_target_fps(self.config.fps_limit)

        self.render_pipeline.initialize()

        self._initialized = True
        logger.info("Game engine initialized successfully.")

    def dispose(self) -> None:
        """
        Disposes of the game engine.
        This should be called after running the engine.
        """
        if not self._initialized:
            return
        logger.info("Disposing game engine...")
        self.scene_manager.clear_immediately()
        self.render_pipeline.dispose()
        pyray.close_window()
        self._initialized = False
        logger.info("Game engine disposed successfully.")

    def exit(self) -> None:
        """
        Exits the game engine.
        This will stop the main loop and close the window.
        """
        self.running = False
        logger.info("Exiting game engine...")

    def run(self) -> None:
        """
        Runs the game engine.
        This will start the main loop and block until the window is closed.
        """
        logger.info("Running game engine...")
        self.initialize()

        self.running = True

        while self.running and not pyray.window_should_close():
            dt = pyray.get_frame_time()

            self._process_events()
            self._update(dt)
            self._process_deferred_deletions()
            self._draw()

        self.dispose()

    # PRIVATE METHODS
    def _process_events(self) -> None:
        pass

    def _update(self, dt: float) -> None:
        pyray.begin_texture_mode(self.render_pipeline.render_texture)
        self.scene_manager._apply_pending()
        self.scene_manager._update(dt)
        pyray.end_texture_mode()

    def _process_deferred_deletions(self) -> None:
        self.scene_manager._process_deferred_deletions()

    def _draw(self) -> None:
        self.render_pipeline.render()
