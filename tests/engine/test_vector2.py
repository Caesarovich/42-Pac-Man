import math

import pytest

from engine import Vector2


def assert_vector2_close(
    vector: Vector2,
    expected_x: float,
    expected_y: float,
) -> None:
    assert vector.x == pytest.approx(expected_x)
    assert vector.y == pytest.approx(expected_y)


def test_from_tuple_and_from_pyray_vector2() -> None:
    vector = Vector2.from_tuple((3.5, -2.0))
    clone = Vector2.from_pyray_vector2(vector.to_pyray())

    assert_vector2_close(vector, 3.5, -2.0)
    assert_vector2_close(clone, 3.5, -2.0)


def test_vector_arithmetic_supports_scalars_and_vectors() -> None:
    vector = Vector2(2.0, 4.0)
    other = Vector2(1.0, -2.0)

    assert_vector2_close(vector + other, 3.0, 2.0)
    assert_vector2_close(vector - other, 1.0, 6.0)
    assert_vector2_close(vector * 2, 4.0, 8.0)
    assert_vector2_close(vector * other, 2.0, -8.0)
    assert_vector2_close(vector / 2, 1.0, 2.0)
    assert_vector2_close(vector / other, 2.0, -2.0)


def test_angle_to_and_rotated() -> None:
    vector = Vector2(1.0, 0.0)
    target = Vector2(0.0, 1.0)

    assert vector.angle_to(target) == pytest.approx(math.pi / 2)
    assert_vector2_close(vector.rotated(math.pi / 2), 0.0, 1.0)
