from typing import TYPE_CHECKING

import pyray

if TYPE_CHECKING:
    from engine import SceneManager


class SceneRenderer:
    """
    A renderer that renders the scene using the provided SceneManager.
    """

    def __init__(
        self,
        scene_manager: SceneManager,
    ) -> None:
        self._scene_manager = scene_manager

    def initialize(self) -> None:
        pass

    def dispose(self) -> None:
        pass

    def render(self, source_texture: pyray.RenderTexture) -> pyray.RenderTexture:
        pyray.begin_texture_mode(source_texture)
        pyray.clear_background(pyray.BLACK)
        self._scene_manager._draw()
        pyray.end_texture_mode()
        return source_texture
