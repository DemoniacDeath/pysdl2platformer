from __future__ import annotations

from core.size import Size
from core.vector2d import Vector2D


class Rect(object):
    size: Size
    center: Vector2D

    def __init__(self, center: Vector2D, size: Size) -> None:
        self.center = center.copy()
        self.size = size.copy()

    @classmethod
    def make(cls, x: float, y: float, width: float, height: float) -> Rect:
        return cls(Vector2D(x, y), Size(width, height))

    def copy(self) -> Rect:
        return Rect(self.center.copy(), self.size.copy())
