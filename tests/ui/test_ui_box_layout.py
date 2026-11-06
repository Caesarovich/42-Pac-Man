from unittest.mock import Mock

import pytest

from engine.ui import UIBoxLayout
from engine.ui.ui_widget import UIWidget


@pytest.fixture
def ui_box_layout() -> UIBoxLayout:
    return UIBoxLayout(width=200, height=150, padding=10, vertical=True, align="left")


@pytest.fixture
def ui_widget() -> UIWidget:
    ui_widget = Mock(spec=UIWidget)
    ui_widget.width = 100
    ui_widget.height = 30
    return ui_widget


class TestUIBoxLayout:
    def test_calculate_x_offset(
        self,
        monkeypatch: pytest.MonkeyPatch,
        ui_box_layout: UIBoxLayout,
        ui_widget: UIWidget,
    ) -> None:
        assert ui_box_layout._calculate_x_offset(ui_widget) == 10
        with monkeypatch.context() as m:
            m.setattr(ui_box_layout, "align", "center")
            assert ui_box_layout._calculate_x_offset(ui_widget) == 50
        with monkeypatch.context() as m:
            m.setattr(ui_box_layout, "align", "right")
            assert ui_box_layout._calculate_x_offset(ui_widget) == 90

    def test_fit_content(
        self, monkeypatch: pytest.MonkeyPatch, ui_box_layout: UIBoxLayout
    ) -> None:
        children = [
            Mock(spec=UIWidget, width=100, height=30),
            Mock(spec=UIWidget, width=150, height=20),
        ]
        monkeypatch.setattr(ui_box_layout, "_children", children)

        ui_box_layout.fit_content()
        assert ui_box_layout.width == 170
        assert ui_box_layout.height == 80

        with monkeypatch.context() as m:
            m.setattr(ui_box_layout, "vertical", False)
            ui_box_layout.fit_content()
            assert ui_box_layout.width == 280
            assert ui_box_layout.height == 50
