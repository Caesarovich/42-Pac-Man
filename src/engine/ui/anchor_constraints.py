"""Anchor constraint types used by UI layouts."""

from dataclasses import dataclass
from typing import Literal

AnchorX = Literal["center", "left", "right"]
AnchorY = Literal["middle", "top", "bottom"]


@dataclass
class AnchorConstraint:
    """Store anchoring data for a widget inside an anchor layout.

    Attributes:
        anchor_x: Horizontal anchor reference inside the parent layout.
        align_x: Horizontal offset from the selected anchor.
        anchor_y: Vertical anchor reference inside the parent layout.
        align_y: Vertical offset from the selected anchor.
    """

    anchor_x: AnchorX
    align_x: float
    anchor_y: AnchorY
    align_y: float
