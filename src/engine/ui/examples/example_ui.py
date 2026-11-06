"""Runnable example that demonstrates the UI layout widgets."""

from pathlib import Path

import pyray

from engine import Engine, SpriteFrame
from engine.ui.ui_anchor_layout import UIAnchorLayout
from engine.ui.ui_image import UIImage
from engine.ui.ui_keyboard_menu import UIKeyboardMenu
from engine.ui.ui_view import UIView


class ExampleUI(UIView):
    """Example scene that builds a logo and keyboard menu."""

    def _on_enter(self) -> None:
        """Create the example UI when the scene becomes active."""

        debug = True

        anchor_layout = UIAnchorLayout(
            width=pyray.get_render_width(),
            height=pyray.get_render_height(),
            padding=50,
            debug=debug,
        )
        self.ui.add(anchor_layout)

        logo_sprite = SpriteFrame.from_file(
            Path("src/pac_man/resources/pac_man_logo.png")
        ).to_sprite2d()
        logo_sprite.set_width(pyray.get_render_width() / 1.8)
        logo = UIImage(sprite=logo_sprite, debug=debug)
        logo.fit_content()

        anchor_layout.add(logo, anchor_x="center")

        texture = Path("src/pac_man/resources/game_assets_sprite_sheet.png")
        indicator_sprite_frame = SpriteFrame.from_file(texture)
        indicator_sprite_frame.region = pyray.Rectangle(0, 0, 16, 16)
        indicator_sprite = indicator_sprite_frame.to_sprite2d()
        indicator = UIImage(sprite=indicator_sprite, debug=debug)
        menu = UIKeyboardMenu(
            width=250,
            height=200,
            align_content="left",
            menu_items=["Play", "High Scores", "Engine Demo", "Quit"],
            font_size=28,
            selection_indicator=indicator,
            debug=debug,
        )
        menu.fit_content()
        anchor_layout.add(menu, anchor_x="center", anchor_y="middle", align_y=50)


if __name__ == "__main__":
    engine_config = Engine.Config(virtual_screen_dimensions=(1024, 768))
    engine = Engine(engine_config)

    example_ui = ExampleUI("Example UI")

    engine.scene_manager.push(example_ui)

    engine.run()
