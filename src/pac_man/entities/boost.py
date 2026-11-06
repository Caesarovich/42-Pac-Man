from engine import (
    CollisionCircle2D,
    Node2D,
    Vector2,
)
from pac_man.assets.game_resource_manager import GameResourceManager
from pac_man.assets.models.boost import Boost
from pac_man.entities.collisions.pac_man_collisions_layers import (
    CollisionLayer,
)


class BoostCollectible(Node2D):
    """
    Boost entity that can be collected
    """

    def __init__(
        self,
        name: str,
        kind: Boost,
        duration: float,
        grm: GameResourceManager,
    ) -> None:
        super().__init__(name)
        self._duration = duration
        self._timer = 0.0
        self._kind = kind
        self._sprite = grm.entities_assets.boosts[kind].to_sprite2d()

        self.collision_box = CollisionCircle2D("boost_collision_box")
        self.collision_box.collision_layer = CollisionLayer.BOOSTS
        self.collision_box.collision_mask = CollisionLayer.PACMAN
        self.collision_box.fit_to_sprite(self._sprite, scale=0.3)

    def _on_enter_tree(self) -> None:
        self._sprite.origin = (
            Vector2.from_pyray_vector2(self._sprite.get_draw_size())
            * 0.5
            * self.global_transform.scale
        )

        self.add_child(self._sprite)
        self.add_child(self.collision_box)

    def _on_exit_tree(self) -> None:
        from pac_man.scenes.game_level import GameLevel

        scene = self.get_scene()
        assert scene is not None, "Scene is not set"
        assert isinstance(scene, GameLevel), "Scene is not a GameLevel"

        scene._collision_system.unregister_boost(self)
        scene._entity_manager.remove_boost(self)

    def _on_update(self, dt: float) -> None:
        self._timer += dt
        if self._timer >= self._duration:
            self.queue_for_deletion()
