from pathlib import Path

import pyray

from engine import Shader


class CrtNewPixieShader(Shader):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            Path(__file__).parents[2] / "resources" / "shaders" / "crt_newpixie.fx",
            [
                "resolution",
                "time",
                "curvature",
                "wiggleToggle",
                "scanroll",
                "vignette",
                "ghosting",
            ],
        )
        self.curvature: float = 2.0
        self.wiggle_toggle: float = 0
        self.scanroll: float = 1.5
        self.vignette: float = 1.01
        self.ghosting: float = 0.5
        self.time: float = 0.0

    def apply_values(
        self,
        shader: pyray.Shader,
        source: pyray.Texture,
        scene_texture: pyray.Texture,
    ) -> None:
        self.time += pyray.get_frame_time()

        self.set_resolution_value("resolution", source)
        self.set_shader_value_float("time", self.time)
        self.set_shader_value_float("curvature", self.curvature)
        self.set_shader_value_float("wiggleToggle", self.wiggle_toggle)
        self.set_shader_value_float("scanroll", self.scanroll)
        self.set_shader_value_float("vignette", self.vignette)
        self.set_shader_value_float("ghosting", self.ghosting)
