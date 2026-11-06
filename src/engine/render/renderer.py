from typing import Protocol

import pyray


class Renderer(Protocol):
    """
    A protocol for a renderers.
    A renderer is responsible for rendering pixels onto renter.
    """

    def initialize(self) -> None:
        """
        Initializes the renderer.
        This should be called after the window has been created.
        """
        ...

    def dispose(self) -> None:
        """
        Disposes of the renderer and its resources.
        This should be called before the window is closed.
        """
        ...

    def render(self, source_texture: pyray.RenderTexture) -> pyray.RenderTexture:
        """
        Renders onto a canvas and returns the resulting texture.
        The source_texture contains the pixels rendered
        by the previous renderer in the chain.
        """
        ...
