import math
from collections.abc import Iterator
from dataclasses import dataclass

import pyray


@dataclass(frozen=True)
class Vector2:
    x: float
    y: float

    @classmethod
    def from_tuple(cls, tup: tuple[float, float]) -> Vector2:
        return cls(*tup)

    @classmethod
    def from_pyray_vector2(cls, vec: pyray.Vector2) -> Vector2:
        return cls(vec.x, vec.y)

    def to_pyray(self) -> pyray.Vector2:
        return pyray.Vector2(self.x, self.y)

    def manhattan_distance(self, other: Vector2) -> float:
        return abs(self.x - other.x) + abs(self.y - other.y)

    def euclidean_distance(self, other: Vector2) -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def __add__(self, other: object) -> Vector2:
        if isinstance(other, Vector2):
            return Vector2.from_pyray_vector2(
                pyray.vector2_add(self.to_pyray(), other.to_pyray())
            )
        return NotImplemented

    def __sub__(self, other: object) -> Vector2:
        if isinstance(other, Vector2):
            return Vector2.from_pyray_vector2(
                pyray.vector2_subtract(self.to_pyray(), other.to_pyray())
            )
        return NotImplemented

    def __mul__(self, scalar: object) -> Vector2:
        if isinstance(scalar, (int, float)):
            return Vector2.from_pyray_vector2(
                pyray.vector2_scale(self.to_pyray(), float(scalar))
            )
        if isinstance(scalar, Vector2):
            return Vector2.from_pyray_vector2(
                pyray.vector2_multiply(self.to_pyray(), scalar.to_pyray())
            )
        return NotImplemented

    def __truediv__(self, scalar: object) -> Vector2:
        if isinstance(scalar, (int, float)):
            return Vector2(self.x / scalar, self.y / scalar)
        if isinstance(scalar, Vector2):
            return Vector2.from_pyray_vector2(
                pyray.vector2_divide(self.to_pyray(), scalar.to_pyray())
            )
        return NotImplemented

    def __floordiv__(self, scalar: object) -> Vector2:
        if isinstance(scalar, (int, float)):
            return Vector2(self.x // scalar, self.y // scalar)
        if isinstance(scalar, Vector2):
            return Vector2.from_pyray_vector2(
                pyray.vector2_divide(self.to_pyray(), scalar.to_pyray())
            )
        return NotImplemented

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def angle_to(self, other: Vector2) -> float:
        return pyray.vector2_angle(self.to_pyray(), other.to_pyray())

    def rotated(self, rad: float) -> Vector2:
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        return Vector2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a,
        )
