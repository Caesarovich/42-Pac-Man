import pyray

from engine.render import Renderer, Shader


class PostProcessingRenderer(Renderer):
    """
    A renderer that applies post-processing effects to the rendered scene.

    Each shader in the list of shaders is
    applied in sequence to the rendered scene.
    The output of one shader is used as the input for the next shader.
    """

    def __init__(self, shaders: list[Shader]) -> None:
        self._shaders = shaders
        self._render_target_1: pyray.RenderTexture | None = None
        self._render_target_2: pyray.RenderTexture | None = None
        self._swapped = False

    def initialize(self) -> None:
        for shader in self._shaders:
            shader.initialize()

    def dispose(self) -> None:
        for shader in self._shaders:
            shader.dispose()
        if self._render_target_1:
            pyray.unload_render_texture(self._render_target_1)
        if self._render_target_2:
            pyray.unload_render_texture(self._render_target_2)

    @property
    def _from_texture(self) -> pyray.RenderTexture:
        texture = self._render_target_2 if self._swapped else self._render_target_1
        assert texture is not None
        return texture

    @property
    def _to_texture(self) -> pyray.RenderTexture:
        texture = self._render_target_1 if self._swapped else self._render_target_2
        assert texture is not None
        return texture

    def render(self, source_texture: pyray.RenderTexture) -> pyray.RenderTexture:
        self._swapped = False

        self._render_target_1 = self._create_render_texture(
            self._render_target_1, source_texture.texture
        )
        self._render_target_2 = self._create_render_texture(
            self._render_target_2, source_texture.texture
        )

        first = True
        last_texture = source_texture

        for shader in self._shaders:
            from_texture = source_texture if first else self._from_texture

            shader.apply(from_texture.texture, self._to_texture, source_texture.texture)

            last_texture = self._to_texture
            self._swapped = not self._swapped
            first = False

        return last_texture

    def _create_render_texture(
        self,
        target: pyray.RenderTexture | None,
        source_texture: pyray.Texture,
    ) -> pyray.RenderTexture:
        target_changed: bool = False

        if target is None:
            target = pyray.load_render_texture(
                source_texture.width, source_texture.height
            )
            target_changed = True

        if (
            target.texture.width != source_texture.width
            or target.texture.height != source_texture.height
        ):
            pyray.unload_render_texture(target)
            target = pyray.load_render_texture(
                source_texture.width, source_texture.height
            )
            target_changed = True

        if target_changed:
            pyray.set_texture_filter(
                target.texture, pyray.TextureFilter.TEXTURE_FILTER_POINT
            )

        return target
