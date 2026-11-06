from engine.ui import UIBoxLayout, UILabel


class TestUIWidget:
    def test_invalidate_layout(self) -> None:
        ui_layout_1 = UIBoxLayout()
        ui_layout_2 = UIBoxLayout()
        ui_widget = UILabel()
        ui_layout_1.add(ui_layout_2)
        ui_layout_2.add(ui_widget)

        assert ui_layout_1.layout_dirty
        assert ui_layout_2.layout_dirty
        ui_layout_1.do_layout()
        assert not ui_layout_1.layout_dirty
        assert not ui_layout_2.layout_dirty

        ui_widget.set_size(10, 10)
        assert ui_layout_1.layout_dirty
        assert ui_layout_2.layout_dirty
        ui_layout_1.do_layout()
        assert not ui_layout_1.layout_dirty
        assert not ui_layout_2.layout_dirty

        ui_widget.fit_content()
        assert ui_layout_1.layout_dirty
        assert ui_layout_2.layout_dirty
        ui_layout_1.do_layout()
        assert not ui_layout_1.layout_dirty
        assert not ui_layout_2.layout_dirty
