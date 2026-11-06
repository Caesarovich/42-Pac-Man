from pathlib import Path

from engine.sprites.sprite2d import Sprite2D
from engine.sprites.sprite_sheet import SpriteFrame, SpriteSheet


class AnimatedSprite2D(Sprite2D):
    def __init__(
        self,
        name: str = "AnimatedSprite2D",
        frames: list[SpriteFrame] | None = None,
        frame_duration: float = 0.1,
        loop: bool = True,
    ) -> None:
        super().__init__(name=name)

        self._frames = frames or []
        self._frame_duration = frame_duration
        self._loop = loop
        self._current_frame_index: int = 0
        self._elapsed_time: float = 0
        self._is_playing: bool = True

        self._update_texture_and_region()

    @classmethod
    def from_files(
        cls,
        name: str,
        file_paths: list[Path],
        frame_duration: float = 0.1,
        loop: bool = True,
    ) -> AnimatedSprite2D:
        """
        Create an AnimatedSprite2D from a list of texture file paths.
        """
        frames = [SpriteFrame.from_file(path) for path in file_paths]
        return cls(name=name, frames=frames, frame_duration=frame_duration, loop=loop)

    @classmethod
    def from_sprite_sheet(
        cls,
        name: str,
        sprite_sheet: SpriteSheet,
        frame_indices_or_positions: list[int] | list[tuple[int, int]],
        frame_duration: float = 0.1,
        loop: bool = True,
    ) -> AnimatedSprite2D:
        """
        Create an AnimatedSprite2D from a list of texture file paths.
        """
        frames = [
            sprite_sheet.get_frame_at_index(index_or_pos)
            if isinstance(index_or_pos, int)
            else sprite_sheet.get_frame_at_position(index_or_pos)
            for index_or_pos in frame_indices_or_positions
        ]
        return cls(name=name, frames=frames, frame_duration=frame_duration, loop=loop)

    # PROPERTIES
    @property
    def frames(self) -> list[SpriteFrame]:
        """
        The list of frames for the animated sprite.
        """
        return self._frames.copy()

    @frames.setter
    def frames(self, value: list[SpriteFrame]) -> None:
        self._frames = value.copy()
        self._current_frame_index = 0
        self._elapsed_time = 0

        if self._frames:
            current_frame = self._frames[self._current_frame_index]
            self.texture = current_frame.texture
            self.region = current_frame.region

    @property
    def frame_duration(self) -> float:
        """
        The duration of each frame in seconds.
        """
        return self._frame_duration

    @frame_duration.setter
    def frame_duration(self, value: float) -> None:
        self._frame_duration = value

    @property
    def loop(self) -> bool:
        """
        Whether the animation should loop.
        """
        return self._loop

    @loop.setter
    def loop(self, value: bool) -> None:
        self._loop = value

    @property
    def current_frame_index(self) -> int:
        """
        The index of the current frame being displayed.
        """
        return self._current_frame_index

    @current_frame_index.setter
    def current_frame_index(self, value: int) -> None:
        assert isinstance(value, int), "Frame index must be an integer."
        assert 0 <= value < len(self._frames), "Frame index out of range."

        self._current_frame_index = value
        current_frame = self._frames[self._current_frame_index]
        self.texture = current_frame.texture
        self.region = current_frame.region

    @property
    def is_playing(self) -> bool:
        """
        Whether the animation is currently playing.
        """
        return self._is_playing

    # PUBLIC METHODS
    def duplicate(self) -> AnimatedSprite2D:
        """
        Create a duplicate of this animated sprite with the same properties.
        """
        return AnimatedSprite2D(
            name=self.name + "_copy" if self.name else "AnimatedSprite2D_copy",
            frames=self._frames.copy(),
            frame_duration=self._frame_duration,
            loop=self._loop,
        )

    def play(self) -> None:
        """
        Start or resume the animation.
        """
        self._is_playing = True

    def pause(self) -> None:
        """
        Pause the animation.
        """
        self._is_playing = False

    # PRIVATE METHODS
    def _update(self, dt: float) -> None:
        """Advance the animation when the sprite is enabled.

        Args:
            dt: Frame delta time in seconds.
        """
        if self.enabled:
            self._update_frame(dt)
        super()._update(dt)

    def _update_frame(self, dt: float) -> None:
        if not self._is_playing or not self._frames:
            return

        self._elapsed_time += dt

        if self._elapsed_time >= self._frame_duration:
            self._elapsed_time -= self._frame_duration
            self._current_frame_index += 1

            if self._current_frame_index >= len(self._frames):
                if self._loop:
                    self._current_frame_index = 0
                else:
                    self._current_frame_index = len(self._frames) - 1
                    self.pause()

            self._update_texture_and_region()

    def _update_texture_and_region(self) -> None:
        """
        Update the texture and region based on the current frame index.
        """
        if self._frames:
            current_frame = self._frames[self._current_frame_index]
            self.texture = current_frame.texture
            self.region = current_frame.region
