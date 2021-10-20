from __future__ import annotations


class Vector2D(object):
    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    @classmethod
    def empty(cls) -> Vector2D:
        return cls(0, 0)

    def copy(self) -> Vector2D:
        return Vector2D(self.x, self.y)

    def plus(self, v: Vector2D) -> Vector2D:
        return Vector2D(self.x + v.x, self.y + v.y)

    def minus(self, v: Vector2D) -> Vector2D:
        return Vector2D(self.x - v.x, self.y - v.y)

    def times(self, s: float) -> Vector2D:
        return Vector2D(self.x * s, self.y * s)

    def div(self, s: float) -> Vector2D:
        return Vector2D(self.x / s, self.y / s)
