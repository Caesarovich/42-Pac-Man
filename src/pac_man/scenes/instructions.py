import pyray

from engine import AnimatedSprite2D, Engine, Sprite2D, Vector2
from engine.ui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIImage,
    UIKeyboardMenu,
    UILabel,
    UILayout,
    UIView,
)
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.assets.maze_assets import MazeConsumables


class Instructions(UIView):
    """Instructions scene."""

    def __init__(self, name: str, game_resource_manager: GameResourceManager) -> None:
        super().__init__(name)
        self.game_resource_manager = game_resource_manager

    def _on_enter(self) -> None:
        anchor_layout = UIAnchorLayout(
            width=pyray.get_render_width(),
            height=pyray.get_render_height(),
            padding=50,
        )
        self.ui.add(anchor_layout)

        layout = UIBoxLayout(
            align="center",
            vertical=True,
            padding=24,
            width=pyray.get_render_width() - 100,
            height=pyray.get_render_height() - 100,
        )
        anchor_layout.add(layout, anchor="center")

        label_title = UILabel(
            text="Instructions",
            font_size=48,
            width=layout.width,
            height=50,
            text_color=pyray.YELLOW,
        )
        layout.add(label_title)

        spacer = UILayout(width=layout.width, height=40)
        layout.add(spacer)

        label = UILabel(
            text="Move with arrow keys\n",
            font_size=24,
            width=layout.width,
            height=30,
        )
        layout.add(label)

        pac_man_sprite = AnimatedSprite2D(
            frames=self.game_resource_manager.entities_assets.pacman_sprite,
            frame_duration=0.3,
            loop=True,
        )
        pac_man_sprite.set_height(30)
        pac_man_sprite.position = Vector2(-40, 0)
        pac_man_image = UIImage(sprite=pac_man_sprite, width=30, height=30)
        label.add(pac_man_image)

        label = UILabel(
            text="Eat all the PacGums to win!\n",
            font_size=24,
            width=layout.width,
            height=30,
        )
        layout.add(label)

        gum = self.game_resource_manager.maze_tileset.get_consumable(
            MazeConsumables.PAC_GUM
        )
        gum_sprite = Sprite2D(
            texture=self.game_resource_manager.maze_tileset.atlas,
            region=self.game_resource_manager.maze_tileset.get_tile(gum),
        )
        gum_sprite.set_height(30)
        gum_sprite.position = Vector2(-40, 0)
        gum_image = UIImage(sprite=gum_sprite, width=30, height=30)
        label.add(gum_image)

        label = UILabel(
            text="Avoid getting caught by the ghosts!\n",
            font_size=24,
            width=layout.width,
            height=30,
        )
        layout.add(label)
        assets = self.game_resource_manager.entities_assets
        ghosts_sprite = AnimatedSprite2D(
            "ghost_sprites",
            frames=[
                frame
                for ghost_sprite in assets.ghost_sprites.values()
                for directional_sprite in ghost_sprite.values()
                for frame in directional_sprite
            ],
            frame_duration=0.1,
        )

        ghosts_sprite.set_height(30)
        ghosts_sprite.position = Vector2(-50, 0)
        ghosts_image = UIImage(sprite=ghosts_sprite, width=30, height=30)
        label.add(ghosts_image)

        label = UILabel(
            text="Eat boosts to earn extra points!\n",
            font_size=24,
            width=layout.width,
            height=30,
        )
        layout.add(label)

        boosts_sprite = AnimatedSprite2D(
            frames=[frame for frame in assets.boosts.values()],
            frame_duration=0.7,
        )
        boosts_sprite.set_height(30)
        boosts_sprite.position = Vector2(-50, 0)
        boosts_image = UIImage(sprite=boosts_sprite, width=30, height=30)
        label.add(boosts_image)

        label = UILabel(
            text="Eat Super PacGums to turn the tables!\n",
            font_size=24,
            width=layout.width,
            height=30,
        )
        layout.add(label)

        fleeing_ghosts_sprite = AnimatedSprite2D(
            "fleeing_ghosts_sprite",
            frames=assets.fleeing_ghosts_sprite,
            frame_duration=0.1,
        )
        fleeing_ghosts_sprite.set_height(30)
        fleeing_ghosts_sprite.position = Vector2(-50, 0)

        fleeing_ghosts_image = UIImage(
            sprite=fleeing_ghosts_sprite, width=30, height=30
        )
        label.add(fleeing_ghosts_image)

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
    engine.scene_manager.push(
        Instructions(name="Instructions", game_resource_manager=grm)
    )
    engine.run()
