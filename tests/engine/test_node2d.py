import math

import pytest

from engine import Node2D, Vector2


def assert_vector2_close(
    vector: Vector2,
    expected_x: float,
    expected_y: float,
) -> None:
    assert vector.x == pytest.approx(expected_x)
    assert vector.y == pytest.approx(expected_y)


def test_global_transform_defaults_to_local_transform_without_parent() -> None:
    node = Node2D(name="node")
    node.position = Vector2(3.0, 4.0)
    node.rotation = math.pi / 6
    node.scale = Vector2(2.0, 5.0)
    node.origin = Vector2(1.0, 2.0)

    global_transform = node.global_transform

    assert_vector2_close(global_transform.position, 3.0, 4.0)
    assert global_transform.rotation == pytest.approx(math.pi / 6)
    assert_vector2_close(global_transform.scale, 2.0, 5.0)
    assert_vector2_close(global_transform.origin, 1.0, 2.0)


def test_child_global_transform_combines_parent_transform() -> None:
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(10.0, 5.0)
    parent.rotation = math.pi / 2
    parent.scale = Vector2(2.0, 3.0)

    child.position = Vector2(1.0, 0.0)
    child.rotation = math.pi / 4
    child.scale = Vector2(4.0, 6.0)
    child.origin = Vector2(7.0, 8.0)

    parent.add_child(child)

    global_transform = child.global_transform

    assert_vector2_close(global_transform.position, 10.0, 7.0)
    assert global_transform.rotation == pytest.approx(3 * math.pi / 4)
    assert_vector2_close(global_transform.scale, 8.0, 18.0)
    assert_vector2_close(global_transform.origin, 7.0, 8.0)


def test_child_global_transform_updates_when_parent_changes() -> None:
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(0.0, 0.0)
    child.position = Vector2(2.0, 0.0)

    parent.add_child(child)

    assert_vector2_close(child.global_transform.position, 2.0, 0.0)

    parent.position = Vector2(10.0, -3.0)
    parent.rotation = math.pi / 2
    parent.scale = Vector2(1.0, 2.0)

    updated_transform = child.global_transform

    assert_vector2_close(updated_transform.position, 10.0, -1.0)
    assert updated_transform.rotation == pytest.approx(math.pi / 2)
    assert_vector2_close(updated_transform.scale, 1.0, 2.0)


def test_global_transform_with_zero_rotation() -> None:
    """Test that zero rotation doesn't affect position transformation."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(5.0, 10.0)
    parent.rotation = 0.0
    parent.scale = Vector2(2.0, 2.0)

    child.position = Vector2(3.0, 4.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)

    parent.add_child(child)

    global_transform = child.global_transform

    # With no rotation and scale 2x on parent, child position should be scaled
    assert_vector2_close(global_transform.position, 5.0 + 3.0 * 2.0, 10.0 + 4.0 * 2.0)
    assert global_transform.rotation == pytest.approx(0.0)
    assert_vector2_close(global_transform.scale, 2.0, 2.0)


def test_global_transform_with_zero_scale() -> None:
    """Test behavior with zero scale (child should be at parent position)."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(5.0, 10.0)
    parent.rotation = 0.0
    parent.scale = Vector2(0.0, 0.0)

    child.position = Vector2(3.0, 4.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)

    parent.add_child(child)

    global_transform = child.global_transform

    # With zero scale on parent, child's local position contributes nothing
    assert_vector2_close(global_transform.position, 5.0, 10.0)
    assert_vector2_close(global_transform.scale, 0.0, 0.0)


def test_global_transform_with_negative_scale() -> None:
    """Test that negative scale flips the coordinate system."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(0.0, 0.0)
    parent.rotation = 0.0
    parent.scale = Vector2(-1.0, 1.0)

    child.position = Vector2(2.0, 0.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)

    parent.add_child(child)

    global_transform = child.global_transform

    # Negative X scale should flip the child's X position
    assert_vector2_close(global_transform.position, -2.0, 0.0)
    assert_vector2_close(global_transform.scale, -1.0, 1.0)


def test_global_transform_with_180_degree_rotation() -> None:
    """Test that 180 degree rotation flips position correctly."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(0.0, 0.0)
    parent.rotation = math.pi
    parent.scale = Vector2(1.0, 1.0)

    child.position = Vector2(2.0, 0.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)

    parent.add_child(child)

    global_transform = child.global_transform

    # 180 degree rotation should flip X to -X
    assert_vector2_close(global_transform.position, -2.0, 0.0)
    assert global_transform.rotation == pytest.approx(math.pi)


def test_global_transform_with_90_degree_rotation() -> None:
    """Test that 90 degree rotation swaps x and y correctly."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(0.0, 0.0)
    parent.rotation = math.pi / 2
    parent.scale = Vector2(1.0, 1.0)

    child.position = Vector2(2.0, 0.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)

    parent.add_child(child)

    global_transform = child.global_transform

    # 90 degree rotation: (2, 0) should become (0, 2)
    assert_vector2_close(global_transform.position, 0.0, 2.0)
    assert global_transform.rotation == pytest.approx(math.pi / 2)


def test_grandchild_global_transform_three_levels() -> None:
    """Test transform chaining with three levels:
    grandparent -> parent -> child."""
    grandparent = Node2D(name="grandparent")
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    grandparent.position = Vector2(10.0, 0.0)
    grandparent.rotation = 0.0
    grandparent.scale = Vector2(1.0, 1.0)

    parent.position = Vector2(5.0, 0.0)
    parent.rotation = math.pi / 2
    parent.scale = Vector2(2.0, 2.0)

    child.position = Vector2(1.0, 0.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)

    grandparent.add_child(parent)
    parent.add_child(child)

    global_transform = child.global_transform

    # Grandparent: (10, 0)
    # Parent local: (5, 0) -> after grandparent: (10 + 5, 0) = (15, 0)
    # Child local: (1, 0) -> after parent rotation (pi/2) and scale (2x)
    # -> after parent position: (15, 0) + (0, 2) = (15, 2)
    assert_vector2_close(global_transform.position, 15.0, 2.0)
    assert global_transform.rotation == pytest.approx(math.pi / 2)
    assert_vector2_close(global_transform.scale, 2.0, 2.0)


def test_local_to_global_with_origin_offset() -> None:
    """Test that origin offset is correctly
    included in global transform."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(0.0, 0.0)
    parent.rotation = 0.0
    parent.scale = Vector2(1.0, 1.0)
    parent.origin = Vector2(5.0, 5.0)

    child.position = Vector2(2.0, 0.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)
    child.origin = Vector2(1.0, 1.0)

    parent.add_child(child)

    global_transform = child.global_transform

    # Origin should be preserved in global transform
    assert_vector2_close(global_transform.origin, 1.0, 1.0)


def test_child_position_relative_to_parent_origin() -> None:
    """Test child position when parent has an origin offset."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(10.0, 10.0)
    parent.rotation = 0.0
    parent.scale = Vector2(1.0, 1.0)
    parent.origin = Vector2(5.0, 0.0)

    child.position = Vector2(2.0, 0.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)

    parent.add_child(child)

    global_transform = child.global_transform

    # Child position is relative to parent's transformation
    assert_vector2_close(global_transform.position, 12.0, 10.0)


def test_rotation_composition_order() -> None:
    """Test that rotations are composed
    in the correct order (parent + child).
    """
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(0.0, 0.0)
    parent.rotation = math.pi / 6  # 30 degrees
    parent.scale = Vector2(1.0, 1.0)

    child.position = Vector2(1.0, 0.0)
    child.rotation = math.pi / 3  # 60 degrees
    child.scale = Vector2(1.0, 1.0)

    parent.add_child(child)

    global_transform = child.global_transform

    # Total rotation should be 30 + 60 = 90 degrees
    assert global_transform.rotation == pytest.approx(math.pi / 2)


def test_scale_composition_with_non_uniform_scale() -> None:
    """Test scale composition when parent and child have non-uniform scale."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(0.0, 0.0)
    parent.rotation = 0.0
    parent.scale = Vector2(2.0, 3.0)

    child.position = Vector2(1.0, 1.0)
    child.rotation = 0.0
    child.scale = Vector2(4.0, 5.0)

    parent.add_child(child)

    global_transform = child.global_transform

    # Scale should be multiplied: (2*4, 3*5) = (8, 15)
    assert_vector2_close(global_transform.scale, 8.0, 15.0)


def test_global_transform_with_only_position_change() -> None:
    """Test that only position changes propagate correctly."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(0.0, 0.0)
    parent.rotation = 0.0
    parent.scale = Vector2(1.0, 1.0)

    child.position = Vector2(5.0, 5.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)

    parent.add_child(child)

    assert_vector2_close(child.global_transform.position, 5.0, 5.0)

    parent.position = Vector2(3.0, 7.0)

    global_transform = child.global_transform

    assert_vector2_close(global_transform.position, 3.0 + 5.0, 7.0 + 5.0)
    assert global_transform.rotation == pytest.approx(0.0)
    assert_vector2_close(global_transform.scale, 1.0, 1.0)


def test_global_transform_independent_of_child_count() -> None:
    """Test that a node's global transform
    doesn't depend on how many children it has."""
    parent = Node2D(name="parent")
    child1 = Node2D(name="child1")
    child2 = Node2D(name="child2")

    parent.position = Vector2(10.0, 20.0)
    parent.rotation = math.pi / 4
    parent.scale = Vector2(2.0, 2.0)

    child1.position = Vector2(1.0, 0.0)
    child1.rotation = 0.0
    child1.scale = Vector2(1.0, 1.0)

    child2.position = Vector2(1.0, 0.0)
    child2.rotation = 0.0
    child2.scale = Vector2(1.0, 1.0)

    parent.add_child(child1)
    parent.add_child(child2)

    # Both children should have the same global transform
    global1 = child1.global_transform
    global2 = child2.global_transform

    assert_vector2_close(global1.position, global2.position.x, global2.position.y)
    assert global1.rotation == pytest.approx(global2.rotation)
    assert_vector2_close(global1.scale, global2.scale.x, global2.scale.y)


def test_remove_child_updates_global_transform() -> None:
    """Test that removing a child makes its
    global transform equal to local transform."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(10.0, 10.0)
    parent.rotation = math.pi / 2
    parent.scale = Vector2(2.0, 2.0)

    child.position = Vector2(1.0, 0.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)

    parent.add_child(child)

    # With parent
    assert_vector2_close(child.global_transform.position, 10.0, 12.0)

    parent.remove_child(child)

    # Without parent, global should equal local
    global_after_removal = child.global_transform
    assert_vector2_close(global_after_removal.position, 1.0, 0.0)
    assert global_after_removal.rotation == pytest.approx(0.0)
    assert_vector2_close(global_after_removal.scale, 1.0, 1.0)


def test_global_transform_with_pi_rotation_and_scale() -> None:
    """Test complex case: pi rotation with non-uniform scale."""
    parent = Node2D(name="parent")
    child = Node2D(name="child")

    parent.position = Vector2(0.0, 0.0)
    parent.rotation = math.pi
    parent.scale = Vector2(2.0, 3.0)

    child.position = Vector2(1.0, 2.0)
    child.rotation = 0.0
    child.scale = Vector2(1.0, 1.0)

    parent.add_child(child)

    global_transform = child.global_transform

    # Rotation by pi: (1, 2) -> (-1, -2)
    # Scale (2, 3): (-1*2, -2*3) = (-2, -6)
    assert_vector2_close(global_transform.position, -2.0, -6.0)
    assert global_transform.rotation == pytest.approx(math.pi)
    assert_vector2_close(global_transform.scale, 2.0, 3.0)
