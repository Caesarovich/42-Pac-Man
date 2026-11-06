from unittest.mock import Mock

from engine.sprites.sprite_sheet import SpriteSheet


def test_sprite_sheet_get_frame_at_position_uses_grid_position() -> None:
    sprite_sheet = SpriteSheet(
        texture=Mock(width=90, height=140),
        frame_size=Mock(x=16, y=24),
        gap_size=Mock(x=2, y=4),
    )

    frame = sprite_sheet.get_frame_at_position((3, 4))

    assert frame.region.x == 54
    assert frame.region.y == 112
    assert frame.region.width == 16
    assert frame.region.height == 24


def test_sprite_sheet_get_frame_at_index_uses_row_major_order() -> None:
    sprite_sheet = SpriteSheet(
        texture=Mock(width=90, height=140),
        frame_size=Mock(x=16, y=24),
        gap_size=Mock(x=2, y=4),
    )

    frame = sprite_sheet.get_frame_at_index(7)

    assert sprite_sheet.get_frame_count() == 25
    assert frame.region.x == 36
    assert frame.region.y == 28
    assert frame.region.width == 16
    assert frame.region.height == 24
