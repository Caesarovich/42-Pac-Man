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
from pac_man.highscore import Highscore


class Highscores(UIView):
    """High scores scene."""

    def __init__(self, name: str, game_resource_manager: GameResourceManager) -> None:
        super().__init__(name)
        self.game_resource_manager = game_resource_manager

    def _on_enter(self) -> None:
        scores = Highscore.load()

        anchor_layout = UIAnchorLayout(
            width=pyray.get_render_width(),
            height=pyray.get_render_height(),
            padding=50,
        )
        self.ui.add(anchor_layout)

        layout = UIBoxLayout(
            align="center",
            vertical=True,
            padding=16,
            width=pyray.get_render_width() - 100,
            height=pyray.get_render_height() - 100,
        )
        anchor_layout.add(layout, anchor="center")

        label_title = UILabel(
            text="High Scores",
            font_size=48,
            width=layout.width,
            height=50,
            text_color=pyray.YELLOW,
        )
        layout.add(label_title)

        spacer = UILayout(width=layout.width, height=40)
        layout.add(spacer)

        for i, entry in enumerate(scores):
            label = UILabel(
                text=f"{i + 1}. {entry.name} - {entry.score}",
                font_size=24,
                width=layout.width,
                height=30,
                text_color=pyray.YELLOW,
            )
            layout.add(label)

        spacer = UILayout(width=layout.width, height=40)
        layout.add(spacer)

        menu = UIKeyboardMenu(
            width=250,
            height=200,
            align_content="center",
            menu_items=["Return to Main Menu"],
            font_size=28,
            callback_fct=self._on_back_selected,
        )
        layout.add(menu)

        layout.do_layout()

    def _on_back_selected(self, selected_item: str) -> None:
        """Handle back button selection."""
        if self.manager is not None:
            self.manager.pop()


if __name__ == "__main__":
    engine_config = Engine.Config(
        virtual_screen_dimensions=(900, 900),
        show_fps=True,
    )

    engine = Engine(config=engine_config)
    grm = GameResourceManager()

    engine.initialize()
    grm.load()
    engine.scene_manager.push(Highscores(name="Highscores", game_resource_manager=grm))
    engine.run()
