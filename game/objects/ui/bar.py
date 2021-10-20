from core.rect import Rect
from core.size import Size
from core.vector2d import Vector2D
from engine.context import GameContext
from engine.gameobject import GameObject


class Bar(GameObject):
    value: float
    originalFrame: Rect

    def __init__(self, context: GameContext, frame: Rect) -> None:
        super().__init__(context, frame)
        self.value = 100
        self.originalFrame = frame.copy()

    def set_value(self, new_value: float) -> None:
        if new_value > 100:
            new_value = 100
        if new_value < 0:
            new_value = 0
        self.value = new_value

        self.frame = Rect(
            Vector2D(
                self.originalFrame.center.x + self.originalFrame.size.width * ((new_value - 100) / 200),
                self.originalFrame.center.y
            ),
            Size(
                self.originalFrame.size.width / 100 * new_value,
                self.originalFrame.size.height
            )
        )
