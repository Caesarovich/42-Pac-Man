from engine import AnimatedSprite2D, Engine, Scene2D, Vector2
from pac_man.assets.game_resource_manager import GameResourceManager


class DemoScene(Scene2D):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._game_resource_manager = GameResourceManager()

    def _on_enter(self) -> None:
        self._game_resource_manager.load()
        print("Entering DemoScene...")
        assets = self._game_resource_manager.entities_assets
        sprites = [
            AnimatedSprite2D(
                "pacman_sprite",
                frames=(assets.pacman_sprite),
                frame_duration=0.1,
            ),
            AnimatedSprite2D(
                "fleeing_ghosts_sprite",
                frames=assets.fleeing_ghosts_sprite,
                frame_duration=0.1,
            ),
            AnimatedSprite2D(
                "blinking_ghosts_sprite",
                frames=assets.blinking_ghosts_sprite,
                frame_duration=0.1,
            ),
            AnimatedSprite2D(
                "dead_pacman_sprite",
                frames=assets.dead_pacman_sprite,
                frame_duration=0.1,
            ),
            AnimatedSprite2D(
                "ghost_sprites",
                frames=[
                    frame
                    for ghost_sprite in assets.ghost_sprites.values()
                    for directional_sprite in ghost_sprite.values()
                    for frame in directional_sprite
                ],
                frame_duration=0.1,
            ),
            *[frame.to_sprite2d() for frame in assets.ghost_eyes.values()],
            *[frame.to_sprite2d() for frame in assets.boosts.values()],
        ]

        for i, game_sprite in enumerate(sprites):
            x, y = i % 10, i // 10
            game_sprite.position = Vector2(100 + x * 100, 100 + y * 100)
            game_sprite.scale = Vector2(5, 5)
            self.root.add_child(game_sprite)


if __name__ == "__main__":
    # Node2D.DEBUG_DRAW_GIZMO = True

    engine_config = Engine.Config(
        title="Solar System Simulation",
        virtual_screen_dimensions=(1920, 1080),
        show_fps=True,
        # fps_limit=60,
    )
    engine = Engine(config=engine_config)

    loading_scene = DemoScene(name="Loading Scene")
    engine.scene_manager.push(loading_scene)
    engine.run()
