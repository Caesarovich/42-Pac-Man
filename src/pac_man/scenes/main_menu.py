from pathlib import Path

import pyray

from engine import AnimatedSprite2D, Engine, SpriteFrame
from engine.ui import UIAnchorLayout, UIImage, UIKeyboardMenu, UIView
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.config.game_config import GameConfig
from pac_man.scenes.game_level import GameLevel
from pac_man.scenes.highscores import Highscores
from pac_man.scenes.instructions import Instructions


class MainMenu(UIView):
    """Main menu scene."""

    def __init__(
        self,
        name: str,
        game_resource_manager: GameResourceManager,
        game_config: GameConfig,
    ) -> None:
        super().__init__(name)
        self.game_resource_manager = game_resource_manager
        self.game_config = game_config

    def _on_enter(self) -> None:
        anchor_layout = UIAnchorLayout(
            width=pyray.get_render_width(),
            height=pyray.get_render_height(),
            padding=50,
        )
        self.ui.add(anchor_layout)

        splash_sprite = SpriteFrame.from_file(
            Path(__file__).parent.parent / "resources" / "pac_man_logo.png"
        ).to_sprite2d()
        splash_sprite.set_width(pyray.get_render_width() * 0.3)
        self._splash_sprite = splash_sprite
        splash = UIImage(sprite=splash_sprite)
        splash.fit_content()

        anchor_layout.add(splash, anchor_x="center")

        pac_man_frames = self.game_resource_manager.entities_assets.pacman_sprite
        pac_man_sprite = AnimatedSprite2D(frames=pac_man_frames)

        indicator = UIImage(sprite=pac_man_sprite)
        menu = UIKeyboardMenu(
            width=250,
            height=200,
            align_content="left",
            menu_items=["Play", "High Scores", "Instructions", "Quit"],
            font_size=28,
            selection_indicator=indicator,
            callback_fct=self._on_menu_selection,
        )
        menu.fit_content()
        anchor_layout.add(menu, anchor_x="center", anchor_y="middle", align_y=50)

    def _on_exit(self) -> None:
        if hasattr(self, "_splash_sprite") and self._splash_sprite.texture is not None:
            pyray.unload_texture(self._splash_sprite.texture)
            del self._splash_sprite

    def _on_menu_selection(self, selected_item: str) -> None:
        """Handle menu selection."""
        if selected_item == "Play":
            if self.manager is not None:
                self.manager.push(
                    GameLevel(
                        game_resource_manager=self.game_resource_manager,
                        game_config=self.game_config,
                    )
                )
        elif selected_item == "High Scores":
            if self.manager is not None:
                self.manager.push(
                    Highscores(
                        name="Highscores",
                        game_resource_manager=self.game_resource_manager,
                    )
                )
        elif selected_item == "Instructions":
            if self.manager is not None:
                self.manager.push(
                    Instructions(
                        name="Instructions",
                        game_resource_manager=self.game_resource_manager,
                    )
                )
        elif selected_item == "Quit" and self.manager is not None:
            self.manager._engine.exit()


if __name__ == "__main__":
    # Node2D.DEBUG_DRAW_GIZMO = True
    # Tilemap.DEBUG_DRAW = True
    # NavRegion2D.DEBUG_DRAW = True

    engine_config = Engine.Config(
        virtual_screen_dimensions=(1920, 1080),
        show_fps=True,
    )

    engine = Engine(config=engine_config)
    grm = GameResourceManager()
    game_config = GameConfig()

    engine.initialize()
    grm.load()
    engine.scene_manager.push(
        MainMenu(name="MainMenu", game_resource_manager=grm, game_config=game_config)
    )
    engine.run()
