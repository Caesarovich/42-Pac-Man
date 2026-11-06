import pyray

from engine.ui import (
    UIAnchorLayout,
    UIBoxLayout,
    UIKeyboardMenu,
    UILabel,
    UILayout,
    UIView,
)
from pac_man.entities.collisions.pac_man_collisions_layers import (
    CollisionLayer,
)
from pac_man.entities.ghost import Ghost
from pac_man.entities.pacman import PacMan
from pac_man.entities.state_machine.ghost_states import (
    ChaseState,
    ScatterState,
)
from pac_man.game.game_manager import GameManager


class CheatMenu(UIView):
    """Cheat menu scene."""

    def __init__(
        self,
        name: str,
        game_manager: GameManager,
        pacman: PacMan,
        ghosts: list[Ghost],
    ) -> None:
        super().__init__(name)
        self._game_manager = game_manager
        self._ghosts = ghosts
        self._pacman = pacman

    @classmethod
    def reset_cheats(cls) -> None:
        Ghost.DEBUG_DRAW = False
        Ghost.FREEZE = False

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
            menu_items=[
                "Skip to next level",
                "Earn 10 lives",
                "Earn 10 000 points",
                "Add 100 seconds",
                "Toggle Pacman invincibility",
                "Toggle ghosts navigation display",
                "Toggle ghosts freeze",
                "Resume",
            ],
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
        elif selected_item == "Skip to next level":
            if self.manager is not None:
                self._game_manager.cheat.force_win_level()
                self.manager.pop()
        elif selected_item == "Earn 10 lives":
            if self.manager is not None:
                self._game_manager.cheat.add_lives(10)
                self.manager.pop()
        elif selected_item == "Add 100 seconds":
            if self.manager is not None:
                self._game_manager.cheat.add_time(100)
                self.manager.pop()
        elif selected_item == "Earn 10 000 points":
            if self.manager is not None:
                self._game_manager.cheat.add_points(10000)
                self.manager.pop()
        elif selected_item == "Toggle ghosts navigation display":
            if self.manager is not None:
                Ghost.DEBUG_DRAW = not Ghost.DEBUG_DRAW
                self.manager.pop()
        elif selected_item == "Toggle Pacman invincibility":
            if self.manager is None:
                return
            for ghost in self._ghosts:
                chase_state = ghost._state_machine.get_state(ChaseState)
                scatter_state = ghost._state_machine.get_state(ScatterState)
                if chase_state is not None and scatter_state is not None:
                    chase_state_collision_box = chase_state.collision_box
                    scatter_state_collision_box = scatter_state.collision_box
                    chase_state_collision_box.collision_mask ^= CollisionLayer.PACMAN
                    scatter_state_collision_box.collision_mask ^= CollisionLayer.PACMAN

            if self._pacman.collision_box is not None:
                self._pacman.collision_box.collision_mask ^= CollisionLayer.CHASE_GHOST

            self.manager.pop()
        elif selected_item == "Toggle ghosts freeze" and self.manager is not None:
            Ghost.FREEZE = not Ghost.FREEZE
            self.manager.pop()
