from collections.abc import Iterator
from dataclasses import dataclass

from engine import DirectionalSprite2D, SpriteFrame, SpriteSheet
from pac_man.assets.models.boost import Boost
from pac_man.assets.models.ghost import GhostColor
from pac_man.config.resources_config import (
    AnimatedSpriteConfig,
    SpriteSheetConfig,
    StaticSpriteConfig,
)

Direction = DirectionalSprite2D.SpriteDirection


@dataclass
class EntitiesAssets:
    """Container for every sprite asset used by the game.

    Attributes:
        ghost_sprites: Directional ghost sprites indexed by color.
        pacman_sprite: Directional Pac-Man sprite.
        fleeing_ghosts_sprite: Blue ghost animation used during frightened
            mode.
        blinking_ghosts_sprite: Blue and white ghost animation used before
            frightened mode expires.
        dead_pacman_sprite: Pac-Man death animation.
        boosts: Bonus item sprites indexed by their boost type.
        ghost_eyes: Ghost eye sprites grouped by direction.
    """

    ghost_sprites: dict[GhostColor, dict[Direction, list[SpriteFrame]]]
    pacman_sprite: list[SpriteFrame]
    dead_pacman_sprite: list[SpriteFrame]
    fleeing_ghosts_sprite: list[SpriteFrame]
    blinking_ghosts_sprite: list[SpriteFrame]
    ghost_eyes: dict[Direction, SpriteFrame]
    boosts: dict[Boost, SpriteFrame]

    @classmethod
    def from_sprite_sheet(
        cls,
        sprite_sheet: SpriteSheet,
        sprite_sheet_config: SpriteSheetConfig,
    ) -> EntitiesAssets:
        """
        Create an EntitiesAssets instance from a sprite sheet and its config.
        """

        def _get_sprite_frames(sprite_name: str) -> list[SpriteFrame]:
            sprite_config = sprite_sheet_config.sprites[sprite_name]
            assert isinstance(sprite_config, AnimatedSpriteConfig)

            return [
                sprite_sheet.get_frame_at_position(frame_pos)
                for frame_pos in sprite_config.frames
            ]

        def _get_sprite_frame(sprite_name: str) -> SpriteFrame:
            sprite_config = sprite_sheet_config.sprites[sprite_name]
            assert isinstance(sprite_config, StaticSpriteConfig)
            return sprite_sheet.get_frame_at_position(sprite_config.frame)

        ghost_sprites = {
            color: {
                direction: _get_sprite_frames(
                    f"ghost_{color.name.lower()}_{direction.name.lower()}"
                )
                for direction in Direction
            }
            for color in GhostColor
        }

        pacman_sprite = _get_sprite_frames("pacman")

        fleeing_ghosts_sprite = _get_sprite_frames("ghost_fleeing")
        blinking_ghosts_sprite = _get_sprite_frames("ghost_blinking")
        dead_pacman_sprite = _get_sprite_frames("pacman_death")

        boosts = {boost: _get_sprite_frame(boost.name.lower()) for boost in Boost}

        ghost_eyes = {
            direction: _get_sprite_frame(f"ghost_eye_{direction.name.lower()}")
            for direction in Direction
        }

        return EntitiesAssets(
            ghost_sprites=ghost_sprites,
            pacman_sprite=pacman_sprite,
            fleeing_ghosts_sprite=fleeing_ghosts_sprite,
            blinking_ghosts_sprite=blinking_ghosts_sprite,
            dead_pacman_sprite=dead_pacman_sprite,
            boosts=boosts,
            ghost_eyes=ghost_eyes,
        )

    def __iter__(self) -> Iterator[SpriteFrame]:
        """Iterate over every sprite in the asset set.

        Yields:
            Drawable game sprites.
        """
        for ghost_sprite in self.ghost_sprites.values():
            for directional_sprite in ghost_sprite.values():
                yield from directional_sprite
        yield from self.pacman_sprite
        yield from self.fleeing_ghosts_sprite
        yield from self.blinking_ghosts_sprite
        yield from self.dead_pacman_sprite
        yield from self.boosts.values()
        yield from self.ghost_eyes.values()
