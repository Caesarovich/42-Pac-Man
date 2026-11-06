import pyray

from engine import (
    Engine,
)
from engine.ui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIKeyboardMenu,
    UILabel,
    UILayout,
    UIView,
)
from pac_man.assets.game_resource_manager import GameResourceManager


class PauseMenu(UIView):
    """Pause menu scene."""

    def __init__(self, name: str, game_resource_manager: GameResourceManager) -> None:
        super().__init__(name)
        self.game_resource_manager = game_resource_manager

    def _on_enter(self) -> None:
        anchor_layout = UIAnchorLayout(
            width=pyray.get_render_width(),
            height=pyray.get_render_height(),
            padding=150,
        )
        self.ui.add(anchor_layout)

        layout = UIBoxLayout(
            align="center",
            vertical=True,
            padding=16,
            width=anchor_layout.width - (anchor_layout.padding * 2),
            height=anchor_layout.height - (anchor_layout.padding * 2),
        )
        anchor_layout.add(layout, anchor="center")

        label_title = UILabel(
            text="Pause",
            font_size=48,
            width=layout.width,
            height=50,
            text_color=pyray.YELLOW,
        )
        layout.add(label_title)

        spacer = UILayout(width=layout.width, height=80)
        layout.add(spacer)

        menu = UIKeyboardMenu(
            width=250,
            height=200,
            align_content="left",
            menu_items=["Resume", "Main Menu"],
            font_size=28,
            callback_fct=self._on_menu_selection,
        )
        menu.fit_content()
        layout.add(menu, anchor_x="center", anchor_y="middle", align_y=50)

    def _on_menu_selection(self, selected_item: str) -> None:
        """Handle menu selection."""
        if selected_item == "Resume":
            if self.manager is not None:
                self.manager.pop()
        elif selected_item == "Main Menu" and self.manager is not None:
            self.manager.pop()
            self.manager.pop()


if __name__ == "__main__":
    engine_config = Engine.Config(
        virtual_screen_dimensions=(1920, 1080),
        show_fps=True,
    )

    engine = Engine(config=engine_config)
    grm = GameResourceManager()

    engine.initialize()
    grm.load()
    engine.scene_manager.push(PauseMenu(name="PauseMenu", game_resource_manager=grm))
    engine.run()
