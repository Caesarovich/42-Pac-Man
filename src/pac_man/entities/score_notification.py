import pyray

from engine import Node2D, Vector2
from engine.ui import UILabel


class ScoreNotification(Node2D):
    def __init__(self, score: int) -> None:
        super().__init__()
        self._score = score
        self._timer = 0.0

        self._label = UILabel(
            text=f"+{score}",
            font_size=24,
            text_color=pyray.BLUE,
            align="center",
        )
        self._label.origin = Vector2(self._label.width / 2, self._label.height / 2)
        self.add_child(self._label)

    def _on_update(self, dt: float) -> None:
        self._timer += dt
        if self._timer >= 1.5:
            self.queue_for_deletion()
