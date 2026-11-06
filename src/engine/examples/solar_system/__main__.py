from pathlib import Path
from threading import Timer

import pyray

from engine import (
    AnimatedSprite2D,
    Engine,
    Node2D,
    PostProcessingRenderer,
    Scene2D,
    Shader,
    Sprite2D,
    SpriteFrame,
    SpriteSheet,
    Vector2,
)
from engine.ui import UILabel


class Orbit(Node2D):
    def __init__(self, name: str, radius: float, rotation_speed: float) -> None:
        super().__init__(name=name)
        self.radius = radius
        self.rotation_speed = rotation_speed

    def _on_update(self, dt: float) -> None:
        self.rotate(self.rotation_speed * dt)

    def _on_draw(self) -> None:
        pyray.draw_circle_lines(
            int(self.global_transform.position.x),
            int(self.global_transform.position.y),
            int(self.radius),
            pyray.GRAY,
        )


class CelestialBody(Node2D):
    def __init__(
        self,
        name: str,
        radius: float,
        sprite_frame: SpriteFrame,
        rotation_speed: float = 0.0,
    ) -> None:
        super().__init__(name=name)
        self.radius = radius
        self.rotation_speed = rotation_speed

        self.sprite_frame = sprite_frame
        self.sprite = self.sprite_frame.to_sprite2d(name=f"{name} Sprite")
        self.sprite.fit_into(
            self.radius * 2, self.radius * 2, mode=Sprite2D.FitMode.COVER
        )
        self.sprite.origin = Vector2(
            self.sprite.get_draw_size().x / 2,
            self.sprite.get_draw_size().y / 2,
        )
        self.add_child(self.sprite)

    def _on_update(self, dt: float) -> None:
        self.rotate(self.rotation_speed * dt)

    @staticmethod
    def orbiting_factory(
        name: str,
        radius: float,
        orbit_radius: float,
        orbit_speed: float,
        orbit_parent: Node2D,
        rotation_speed: float,
        sprite_frame: SpriteFrame,
    ) -> CelestialBody:

        orbit = Orbit(
            name=f"{name}'s orbit",
            radius=orbit_radius,
            rotation_speed=orbit_speed,
        )
        orbit_parent.add_child(orbit)

        body = CelestialBody(
            name=name,
            radius=radius,
            sprite_frame=sprite_frame,
            rotation_speed=rotation_speed,
        )

        body.position = body.position + Vector2(orbit_radius, 0)
        orbit.add_child(body)

        label = UILabel(x=40, y=0, text=name, text_color=pyray.WHITE, align="center")
        body.add_child(label)

        return body


class SolarSystemScene(Scene2D):
    def _on_enter(self) -> None:

        self.background_sprite = AnimatedSprite2D.from_files(
            name="Background",
            frame_duration=0.5,
            file_paths=[
                Path(__file__).parent / "background1.png",
                Path(__file__).parent / "background2.png",
            ],
        )
        self.background_sprite.fit_into(
            pyray.get_render_width(),
            pyray.get_render_height(),
            mode=Sprite2D.FitMode.COVER,
            # mode=Sprite2D.FitMode.CONTAIN
            # mode=Sprite2D.FitMode.STRETCH
        )
        self.background_sprite.origin = Vector2(0, 100)
        self.background_sprite.tint = pyray.GRAY
        self.root.add_child(self.background_sprite)

        sprite_sheet = SpriteSheet.from_file(
            Path(__file__).parent / "planet_sheet.png",
            frame_width=192,
            frame_height=192,
        )

        self.sun = CelestialBody(
            name="Sun",
            radius=50,
            sprite_frame=sprite_sheet.get_frame_at_index(8),
            rotation_speed=2.0,
        )
        self.root.add_child(self.sun)

        self.sun.position = Vector2(
            pyray.get_render_width() / 2, pyray.get_render_height() / 2
        )

        self.earth = CelestialBody.orbiting_factory(
            name="Earth",
            radius=25,
            orbit_radius=200,
            orbit_speed=10,
            orbit_parent=self.sun,
            sprite_frame=sprite_sheet.get_frame_at_index(3),
            rotation_speed=360,
        )

        self.moon = CelestialBody.orbiting_factory(
            name="Moon",
            radius=5,
            orbit_radius=40,
            orbit_speed=30,
            orbit_parent=self.earth,
            sprite_frame=sprite_sheet.get_frame_at_index(0),
            rotation_speed=0,
        )

        self.mars = CelestialBody.orbiting_factory(
            name="Mars",
            radius=20,
            orbit_radius=300,
            orbit_speed=7,
            orbit_parent=self.sun,
            sprite_frame=sprite_sheet.get_frame_at_index(1),
            rotation_speed=16,
        )

        self.jupiter = CelestialBody.orbiting_factory(
            name="Jupiter",
            radius=30,
            orbit_radius=450,
            orbit_speed=5,
            orbit_parent=self.sun,
            sprite_frame=sprite_sheet.get_frame_at_index(7),
            rotation_speed=8,
        )

        self.jupiter_moon1 = CelestialBody.orbiting_factory(
            name="Jupiter Moon 1",
            radius=8,
            orbit_radius=60,
            orbit_speed=20,
            orbit_parent=self.jupiter,
            sprite_frame=sprite_sheet.get_frame_at_index(4),
            rotation_speed=8.0,
        )

        self.jupiter_moon2 = CelestialBody.orbiting_factory(
            name="Jupiter Moon 2",
            radius=6,
            orbit_radius=90,
            orbit_speed=15,
            orbit_parent=self.jupiter,
            sprite_frame=sprite_sheet.get_frame_at_index(5),
            rotation_speed=6.0,
        )

        self.jupiter_moon3 = CelestialBody.orbiting_factory(
            name="Jupiter Moon 3",
            radius=4,
            orbit_radius=120,
            orbit_speed=10,
            orbit_parent=self.jupiter_moon2,
            sprite_frame=sprite_sheet.get_frame_at_index(6),
            rotation_speed=4.0,
        )

        self.jupiter_moon4 = CelestialBody.orbiting_factory(
            name="Jupiter Moon 4",
            radius=3,
            orbit_radius=150,
            orbit_speed=5,
            orbit_parent=self.jupiter_moon3,
            sprite_frame=sprite_sheet.get_frame_at_index(2),
            rotation_speed=2.0,
        )

        self.jupiter_moon5 = CelestialBody.orbiting_factory(
            name="Jupiter Moon 5",
            radius=2,
            orbit_radius=180,
            orbit_speed=3,
            orbit_parent=self.jupiter_moon4,
            sprite_frame=sprite_sheet.get_frame_at_index(1),
            rotation_speed=1.0,
        )

        self.jupiter_moon6 = CelestialBody.orbiting_factory(
            name="Jupiter Moon 6",
            radius=1,
            orbit_radius=210,
            orbit_speed=2,
            orbit_parent=self.jupiter_moon5,
            sprite_frame=sprite_sheet.get_frame_at_index(0),
            rotation_speed=0.5,
        )

    def _on_update(self, dt: float) -> None:
        y = self.background_sprite.origin.y
        self.background_sprite.origin = Vector2(0, y + 10 * dt)

        if self.background_sprite.origin.y > pyray.get_render_height():
            self.background_sprite.origin = Vector2(0, 0)


class LoadingScene(Scene2D):
    def _on_enter(self) -> None:
        print("Loading...")

        # Simulate loading time
        Timer(1.0, self.finish_loading).start()

    def _on_exit(self) -> None:
        print("Exiting loading scene...")

    def _on_draw(self) -> None:
        pyray.draw_text("Loading...", 20, 20, 30, pyray.WHITE)

    def finish_loading(self) -> None:
        print("Loading complete!")
        if self.manager:
            self.manager.push(SolarSystemScene(name="Solar System"))


class GaussianBlurShader(Shader):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            Path(__file__).parent / "gaussian_blur.fx",
            ["resolution", "direction", "spread"],
        )
        self.spread: float = 1
        self.direction: pyray.Vector2 = pyray.Vector2(1.0, 0.0)

    def apply_values(
        self,
        shader: pyray.Shader,
        source: pyray.Texture,
        scene_texture: pyray.Texture,
    ) -> None:
        self.set_resolution_value("resolution", source)
        self.set_shader_value_vector2("direction", self.direction)
        self.set_shader_value_float("spread", self.spread)


if __name__ == "__main__":
    Node2D.DEBUG_DRAW = True

    engine_config = Engine.Config(
        title="Solar System Simulation",
        virtual_screen_dimensions=(1920, 1080),
        show_fps=True,
        # fps_limit=60,
    )
    engine = Engine(config=engine_config)
    engine.render_pipeline.add_renderer(PostProcessingRenderer([GaussianBlurShader()]))

    loading_scene = LoadingScene(name="Loading Scene")
    engine.scene_manager.push(loading_scene)
    engine.run()
