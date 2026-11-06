from typing import cast

import pyray

from engine import Vector2
from engine.render import Renderer


class RenderPipeline:
    def __init__(self, virtual_screen_dimensions: tuple[int, int]) -> None:
        self._virtual_screen_dimensions = virtual_screen_dimensions
        self._virtual_screen_texture: pyray.RenderTexture | None = None
        self._upscale_filter: pyray.TextureFilter = cast(
            pyray.TextureFilter, pyray.TextureFilter.TEXTURE_FILTER_POINT
        )
        self._renderers: list[Renderer] = []
        self._is_initialized: bool = False
        self._show_fps: bool = False

    @property
    def show_fps(self) -> bool:
        """
        Whether to show the FPS counter on the screen.
        """
        return self._show_fps

    @show_fps.setter
    def show_fps(self, value: bool) -> None:
        self._show_fps = value

    @property
    def upscale_filter(self) -> pyray.TextureFilter:
        """
        The texture filter used when scaling
        the virtual screen to the actual window.
        """
        return self._upscale_filter

    @upscale_filter.setter
    def upscale_filter(self, value: pyray.TextureFilter) -> None:
        self._upscale_filter = value
        if self._virtual_screen_texture:
            pyray.set_texture_filter(self._virtual_screen_texture.texture, value)

    @property
    def render_texture(self) -> pyray.RenderTexture:
        """
        The virtual screen render texture.
        """
        return self._initialize_virtual_screen_texture()

    @property
    def renderers(self) -> list[Renderer]:
        """
        The sequence of renderers used in the pipeline.
        The order matters as they are applied in sequence.
        """
        return self._renderers.copy()

    def add_renderer(self, renderer: Renderer) -> None:
        """
        Adds a renderer to the pipeline.
        The order matters as they are applied in sequence.
        """
        self._renderers.append(renderer)
        if self._is_initialized:
            renderer.initialize()

    def remove_renderer(self, renderer: Renderer) -> None:
        """
        Removes a renderer from the pipeline.
        """
        if renderer in self._renderers:
            self._renderers.remove(renderer)
            renderer.dispose()

    def initialize(self) -> None:
        """
        Initializes the pipeline.
        This should be called after the window has been created
        and before any rendering is done.
        """
        if self._is_initialized:
            return

        self._initialize_virtual_screen_texture()

        for renderer in self._renderers:
            renderer.initialize()

        self._is_initialized = True

    def dispose(self) -> None:
        """
        Disposes of the pipeline and its resources.
        This should be called before the window is closed.
        """
        if self._virtual_screen_texture is not None:
            pyray.unload_render_texture(self._virtual_screen_texture)
            self._virtual_screen_texture = None

        for renderer in self._renderers:
            renderer.dispose()

    def render(self) -> None:
        """
        Renders the game using the provided renderers.
        Each renderer is responsible for rendering
        pixels onto the virtual screen.
        """
        current_texture = self.render_texture

        for renderer in self._renderers:
            current_texture = renderer.render(current_texture)

        self._draw_to_window(current_texture.texture)

    def _initialize_virtual_screen_texture(self) -> pyray.RenderTexture:
        """
        Initializes the virtual screen texture
        if it hasn't been initialized yet.
        """
        if self._virtual_screen_texture:
            return self._virtual_screen_texture
        self._virtual_screen_texture = pyray.load_render_texture(
            *self._virtual_screen_dimensions
        )
        pyray.set_texture_filter(
            self._virtual_screen_texture.texture,
            self._upscale_filter,
        )
        return self._virtual_screen_texture

    def _draw_to_window(self, texture: pyray.Texture) -> None:
        """
        Draws the virtual screen texture to the actual window,
        scaling it to fit while maintaining aspect ratio.
        """
        pyray.begin_drawing()
        pyray.clear_background(pyray.BLACK)

        screen_size = Vector2(pyray.get_render_width(), pyray.get_render_height())

        v_screen_size = Vector2(*self._virtual_screen_dimensions)

        scale = min(
            screen_size.x / v_screen_size.x,
            screen_size.y / v_screen_size.y,
        )

        scaled_size = v_screen_size * scale
        offset = (screen_size - scaled_size) // 2

        dest_rec = pyray.Rectangle(*offset, *scaled_size)
        source_rec = pyray.Rectangle(
            0,
            0,
            texture.width,
            -texture.height,
        )
        pyray.draw_texture_pro(
            texture,
            source_rec,
            dest_rec,
            pyray.Vector2(0, 0),
            0.0,
            pyray.WHITE,
        )

        if self.show_fps:
            pyray.draw_fps(10, 10)

        pyray.end_drawing()
