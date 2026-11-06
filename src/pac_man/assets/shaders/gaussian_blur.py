from pathlib import Path

import pyray

from engine import Shader


class GaussianBlurShader(Shader):
    def __init__(
        self,
        spread: float = 1,
        direction: tuple[float, float] = (1.0, 0.0),
    ) -> None:
        super().__init__(
            Path(__file__).parents[2] / "resources" / "shaders" / "gaussian_blur.fx",
            ["resolution", "direction", "spread"],
        )
        self.spread: float = spread
        self.direction: pyray.Vector2 = pyray.Vector2(*direction)

    def apply_values(
        self,
        shader: pyray.Shader,
        source: pyray.Texture,
        scene_texture: pyray.Texture,
    ) -> None:
        self.set_resolution_value("resolution", source)
        self.set_shader_value_vector2("direction", self.direction)
        self.set_shader_value_float("spread", self.spread)
