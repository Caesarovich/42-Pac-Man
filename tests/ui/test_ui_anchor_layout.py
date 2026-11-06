import pytest

from engine.ui import UIAnchorLayout


@pytest.fixture
def ui_anchor_layout() -> UIAnchorLayout:
    return UIAnchorLayout(width=200, height=150, padding=10)


class TestUIAnchorLayout:
    def test_calculate_x_offset(
        self,
        ui_anchor_layout: UIAnchorLayout,
    ) -> None:
        assert ui_anchor_layout._calculate_x_offset(40, "left", 5) == 15
        assert ui_anchor_layout._calculate_x_offset(40, "center", 5) == 85
        assert ui_anchor_layout._calculate_x_offset(40, "right", 5) == 155

        assert ui_anchor_layout._calculate_y_offset(20, "top", 5) == 15
        assert ui_anchor_layout._calculate_y_offset(20, "middle", 5) == 70
        assert ui_anchor_layout._calculate_y_offset(20, "bottom", 5) == 125
