import logging

import pyray

from engine import (
    AnimatedSprite2D,
    Engine,
    Vector2,
)
from engine.ui import (
    UIAnchorLayout,
    UIBoxLayout,
    UILabel,
    UILayout,
    UITextInput,
    UIView,
)
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.entities.ghost import Direction
from pac_man.highscore import Highscore, HighscoreEntry

logger = logging.getLogger(__name__)


class GameOver(UIView):
    """Game over scene."""

    def __init__(
        self,
        name: str,
        game_resource_manager: GameResourceManager,
        score: int = 0,
        level: int = 0,
    ) -> None:
        super().__init__(name)
        self.game_resource_manager = game_resource_manager
        self.score = score
        self.level = level

    def _on_enter(self) -> None:
        self._setup_ui()
        self._setup_sprites()

    def _setup_ui(self) -> None:
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
            text="GAME OVER",
            font_size=48,
            width=layout.width,
            height=50,
            text_color=pyray.RED,
        )
        layout.add(label_title)

        spacer = UILayout(width=layout.width, height=40)
        layout.add(spacer)

        label_score = UILabel(
            text=f"Score: {self.score}",
            font_size=24,
            width=layout.width,
            height=30,
            text_color=pyray.WHITE,
        )
        layout.add(label_score)

        label_level = UILabel(
            text=f"Level: {self.level}",
            font_size=24,
            width=layout.width,
            height=30,
            text_color=pyray.WHITE,
        )
        layout.add(label_level)

        spacer2 = UILayout(width=layout.width, height=40)
        layout.add(spacer2)

        input_field = UIBoxLayout(
            align="left",
            vertical=False,
            width=layout.width * 0.8,
            height=44,
            padding=10,
        )
        layout.add(input_field)

        input_label = UILabel(
            text="Enter your name: ",
            font_size=int(input_field.height - input_field.padding * 2),
            width=200,
            text_color=pyray.WHITE,
        )
        input_label.fit_content()
        input_field.add(input_label)

        text_input = UITextInput(
            width=input_field.width - input_label.width - input_field.padding * 3,
            height=input_field.height - input_field.padding * 2,
            font_size=int(input_field.height - input_field.padding * 2),
            text_color=pyray.YELLOW,
            align="right",
            fn_on_enter=self._on_name_entered,
            fn_on_change=lambda x: x,
            max_length=10,
        )
        input_field.add(text_input)

    def _setup_sprites(self) -> None:
        """Setup the sprites for the game over scene."""

        anchor = Vector2(pyray.get_render_width() / 2, pyray.get_render_height() * 0.75)

        pac_man_sprite = AnimatedSprite2D(
            frames=self.game_resource_manager.entities_assets.pacman_sprite,
            frame_duration=0.3,
            loop=True,
        )

        pac_man_sprite.position = anchor + Vector2(-150, 0)

        pac_man_sprite.rotate(180)
        pac_man_sprite.scale = Vector2(3, 3)
        pac_man_sprite.origin = (
            Vector2.from_pyray_vector2(pac_man_sprite.get_draw_size()) * 0.5
        ) * 2
        self.root.add_child(pac_man_sprite)

        offset = -50
        for (
            ghost_sprite
        ) in self.game_resource_manager.entities_assets.ghost_sprites.values():
            sprite_frames = ghost_sprite[Direction.LEFT]
            ghost = AnimatedSprite2D(
                frames=sprite_frames,
                frame_duration=0.2,
                loop=True,
            )
            ghost.position = anchor + Vector2(offset, 0)
            ghost.scale = Vector2(3, 3)
            self.root.add_child(ghost)
            offset += 50

    def _validate_input(self, name: str) -> bool:
        """
        Validate the player's name input.

        Player name is limited to alphanumeric characters
        and must not be empty or whitespace.
        """
        if len(name.strip()) < 3:
            return False
        name = name.strip().replace(" ", "")
        if not name.isalnum():
            return False
        return not len(name) > 10

    def _on_name_entered(self, name: str) -> None:
        """Handle the event when the player enters their name.

        Args:
            name: The name entered by the player.
        """
        if not self._validate_input(name):
            logger.warning("Invalid player name. Please enter a valid name.")
            return
        try:
            entry = HighscoreEntry(name=name, score=self.score)
            Highscore.add_entry(entry)
        except OSError as e:
            logger.error(f"Error adding highscore entry: {e}")
        if self.manager:
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
    engine.scene_manager.push(GameOver(name="GameOver", game_resource_manager=grm))
    engine.run()
