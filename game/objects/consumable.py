from core.rect import Rect
from engine.context import GameContext
from engine.gameobject import GameObject
from engine.physics import PhysicsState


class Consumable(GameObject):
    def __init__(self, context: GameContext, frame: Rect) -> None:
        super().__init__(context, frame)
        self.physics = PhysicsState(self)
