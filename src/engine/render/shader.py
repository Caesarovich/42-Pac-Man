import logging
from abc import ABC, abstractmethod
from pathlib import Path

import pyray

logger = logging.getLogger(__name__)


class Shader(ABC):
    def __init__(self, fx_file_path: Path, shader_values: list[str]) -> None:
        if not fx_file_path.exists():
            raise FileNotFoundError(f"Shader file not found: {fx_file_path}")

        self._fx_file_path = fx_file_path
        self._shader: pyray.Shader | None
        self._shader_locations: dict[str, int] = {}
        self._is_loaded: bool = False
        self._is_disposed: bool = False
        self._shader_locations_loaded: bool = False

        for key in shader_values:
            self._shader_locations.setdefault(key, 0)

    def initialize(self) -> None:
        if self._is_loaded:
            return

        self._shader = pyray.load_shader("", str(self._fx_file_path))
        self._load_shader_locations()
        self._is_loaded = True

    def apply(
        self,
        source: pyray.Texture,
        target: pyray.RenderTexture,
        scene_texture: pyray.Texture,
    ) -> None:
        assert self._shader is not None
        pyray.begin_texture_mode(target)
        pyray.begin_shader_mode(self._shader)

        self.apply_values(self._shader, source, scene_texture)

        source_rect = pyray.Rectangle(
            0, 0, target.texture.width, -target.texture.height
        )
        dest_rect = pyray.Rectangle(0, 0, target.texture.width, target.texture.height)
        pyray.draw_texture_pro(
            source, source_rect, dest_rect, pyray.Vector2(0, 0), 0, pyray.WHITE
        )
        pyray.end_shader_mode()
        pyray.end_texture_mode()

    @abstractmethod
    def apply_values(
        self,
        shader: pyray.Shader,
        source: pyray.Texture,
        scene_texture: pyray.Texture,
    ) -> None:
        pass

    def set_shader_value_texture(self, name: str, texture: pyray.Texture) -> None:
        location = self._get_location(name)
        assert location is not None
        assert self._shader is not None
        pyray.set_shader_value_texture(self._shader, location, texture)

    def set_shader_value_floats(self, name: str, value: list[float]) -> None:
        location = self._get_location(name)
        if location is None:
            return
        assert self._shader is not None
        pyray.set_shader_value(
            self._shader,
            location,
            pyray.ffi.new(f"float[{len(value)}]", value),
            pyray.ShaderUniformDataType.SHADER_UNIFORM_FLOAT,
        )

    def set_shader_value_float(self, name: str, value: float) -> None:
        location = self._get_location(name)
        if location is None:
            return
        assert self._shader is not None
        pyray.set_shader_value(
            self._shader,
            location,
            pyray.ffi.new("float[1]", [value]),
            pyray.ShaderUniformDataType.SHADER_UNIFORM_FLOAT,
        )

    def set_shader_value_int(self, name: str, value: int) -> None:
        location = self._get_location(name)
        assert location is not None
        assert self._shader is not None
        pyray.set_shader_value(
            self._shader,
            location,
            pyray.ffi.new("int[1]", [value]),
            pyray.ShaderUniformDataType.SHADER_UNIFORM_INT,
        )

    def set_shader_value_vector2(self, name: str, value: pyray.Vector2) -> None:
        location = self._get_location(name)
        assert location is not None
        assert self._shader is not None
        pyray.set_shader_value(
            self._shader,
            location,
            pyray.ffi.new("float[2]", [value.x, value.y]),
            pyray.ShaderUniformDataType.SHADER_UNIFORM_VEC2,
        )

    def set_shader_value_vector3(self, name: str, value: pyray.Vector3) -> None:
        location = self._get_location(name)
        assert location is not None
        assert self._shader is not None
        pyray.set_shader_value(
            self._shader,
            location,
            pyray.ffi.new("float[3]", [value.x, value.y, value.z]),
            pyray.ShaderUniformDataType.SHADER_UNIFORM_VEC3,
        )

    def set_shader_value_color(
        self, name: str, value: pyray.Color, include_alpha: bool = True
    ) -> None:
        location = self._get_location(name)
        assert location is not None
        assert self._shader is not None
        if include_alpha:
            pyray.set_shader_value(
                self._shader,
                location,
                pyray.ffi.new("float[4]", [value.r, value.g, value.b, value.a]),
                pyray.ShaderUniformDataType.SHADER_UNIFORM_VEC4,
            )
        else:
            pyray.set_shader_value(
                self._shader,
                location,
                pyray.ffi.new("float[3]", [value.r, value.g, value.b]),
                pyray.ShaderUniformDataType.SHADER_UNIFORM_VEC3,
            )

    def set_resolution_value(self, name: str, texture: pyray.Texture) -> None:
        location = self._get_location(name)
        assert location is not None
        assert self._shader is not None
        pyray.set_shader_value(
            self._shader,
            location,
            pyray.ffi.new("float[2]", [texture.width, texture.height]),
            pyray.ShaderUniformDataType.SHADER_UNIFORM_VEC2,
        )

    def dispose(self) -> None:
        if self._is_disposed:
            return

        if self._shader is not None:
            pyray.unload_shader(self._shader)
            self._shader = None

        self._is_disposed = True

    def _load_shader_locations(self) -> None:
        logger.info(f"Loading shader locations for: {self._fx_file_path}")
        if self._shader_locations_loaded:
            return

        assert self._shader is not None

        for key in self._shader_locations:
            self._shader_locations[key] = pyray.get_shader_location(self._shader, key)

        self._shader_locations_loaded = True

    def _get_location(self, key: str) -> int | None:
        if key not in self._shader_locations:
            return None
        location = self._shader_locations[key]
        if location < 0:
            return None
        return location
