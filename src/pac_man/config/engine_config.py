from typing import Annotated

from pydantic import BaseModel, Field

from engine import Engine


class Dimensions(BaseModel):
    x: Annotated[int, Field(gt=0)]
    y: Annotated[int, Field(gt=0)]


class EngineConfig(BaseModel):
    virtual_screen_dimensions: Dimensions = Dimensions(x=800, y=600)
    title: str = "Pac-Man"
    fps_limit: Annotated[int | None, Field(ge=0)]
    show_fps: bool = True

    def to_engine_config(self) -> Engine.Config:
        return Engine.Config(
            virtual_screen_dimensions=(
                self.virtual_screen_dimensions.x,
                self.virtual_screen_dimensions.y,
            ),
            title=self.title,
            fps_limit=self.fps_limit,
            show_fps=self.show_fps,
        )
