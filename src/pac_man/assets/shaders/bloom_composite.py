from pathlib import Path

import pyray

from engine import Shader


class BloomCompositeShader(Shader):
    def __init__(
        self,
        intensity: float = 0.6,
    ) -> None:
        super().__init__(
            Path(__file__).parents[2] / "resources" / "shaders" / "bloom_composite.fx",
            ["sceneTex", "intensity"],
        )
        self.intensity: float = intensity

    def apply_values(
        self,
        shader: pyray.Shader,
        source: pyray.Texture,
        scene_texture: pyray.Texture,
    ) -> None:
        self.set_shader_value_texture("sceneTex", scene_texture)
        self.set_shader_value_float("intensity", self.intensity)
