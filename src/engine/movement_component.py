from engine import (
    DirectionalSprite2D,
    Node,
    Node2D,
    Vector2,
)
from engine.input_component import KeyPressEvent

Direction = DirectionalSprite2D.SpriteDirection


class MovementComponent(Node):
    def __init__(
        self,
        name: str | None = None,
        parent: Node | None = None,
        children: list[Node] | None = None,
        enabled: bool = True,
        visible: bool = True,
    ) -> None:
        super().__init__(name, parent, children, enabled, visible)
        self.velocity: int = 100
        self.direction: Direction = Direction.RIGHT

    @property
    def character(self) -> Node2D:
        character = self.parent
        assert isinstance(character, Node2D)
        return character

    def _update(self, dt: float) -> None:
        character = self.character
        distance = self.velocity * dt
        if self.direction == Direction.UP:
            character.position += Vector2(0, -distance)
        if self.direction == Direction.DOWN:
            character.position += Vector2(0, distance)
        if self.direction == Direction.LEFT:
            character.position += Vector2(-distance, 0)
        if self.direction == Direction.RIGHT:
            character.position += Vector2(distance, 0)

    def on_notify(self, entity: Node | None, event: KeyPressEvent) -> None:
        if entity is self.parent:
            match event:
                case KeyPressEvent.KEY_UP:
                    self.direction = Direction.UP
                case KeyPressEvent.KEY_DOWN:
                    self.direction = Direction.DOWN
                case KeyPressEvent.KEY_LEFT:
                    self.direction = Direction.LEFT
                case KeyPressEvent.KEY_RIGHT:
                    self.direction = Direction.RIGHT
