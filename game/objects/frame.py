from core.color import Color
from core.rect import Rect
from engine.context import GameContext
from engine.gameobject import GameObject
from engine.render import RenderObject
from game.objects.solid import Solid


class Frame(GameObject):
    width: int
    ceiling: Solid
    wallLeft: Solid
    wallRight: Solid
    floor: Solid

    def __init__(self, context: GameContext, frame: Rect, width: int) -> None:
        super().__init__(context, frame)
        self.width = width
        self.ceiling = Solid(context, Rect.make(
            0,
            -frame.size.height / 2 + width / 2,
            frame.size.width,
            width))
        self.wallLeft = Solid(context, Rect.make(
            -frame.size.width / 2 + width / 2,
            0,
            width,
            frame.size.height - width * 2))
        self.wallRight = Solid(context, Rect.make(
            frame.size.width / 2 - width / 2,
            0,
            width,
            frame.size.height - width * 2))
        self.floor = Solid(context, Rect.make(
            0,
            frame.size.height / 2 - width / 2,
            frame.size.width,
            width))
        self.ceiling.renderObject = RenderObject.render_object_from_color(context.renderer, Color(0, 0, 0, 0xFF))
        self.wallLeft.renderObject = RenderObject.render_object_from_color(context.renderer, Color(0, 0, 0, 0xFF))
        self.wallRight.renderObject = RenderObject.render_object_from_color(context.renderer, Color(0, 0, 0, 0xFF))
        self.floor.renderObject = RenderObject.render_object_from_color(context.renderer, Color(0, 0, 0, 0xFF))
        self.add_child(self.ceiling)
        self.add_child(self.wallLeft)
        self.add_child(self.wallRight)
        self.add_child(self.floor)
