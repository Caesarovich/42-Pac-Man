from pathlib import Path

import pyray

from engine import Shader


class BloomThresholdShader(Shader):
    def __init__(
        self,
        threshold: float = 0.8,
        knee: float = 0.1,
    ) -> None:
        super().__init__(
            Path(__file__).parents[2] / "resources" / "shaders" / "bloom_threshold.fx",
            ["threshold", "knee"],
        )
        self.threshold: float = threshold
        self.knee: float = knee

    def apply_values(
        self,
        shader: pyray.Shader,
        source: pyray.Texture,
        scene_texture: pyray.Texture,
    ) -> None:
        self.set_shader_value_float("threshold", self.threshold)
        self.set_shader_value_float("knee", self.knee)
