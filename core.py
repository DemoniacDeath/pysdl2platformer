class Vector2D(object):
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    @staticmethod
    def Empty() -> 'Vector2D':
        return Vector2D(0, 0)

    def copy(self) -> 'Vector2D':
        return Vector2D(self.x, self.y)

    def plus(self, v: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + v.x, self.y + v.y)

    def minus(self, v: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - v.x, self.y - v.y)

    def times(self, s: float) -> 'Vector2D':
        return Vector2D(self.x * s, self.y * s)

    def div(self, s: float) -> 'Vector2D':
        return Vector2D(self.x / s, self.y / s)


class Size(object):
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    @staticmethod
    def Empty() -> 'Size':
        return Size(0, 0)

    def copy(self) -> 'Size':
        return Size(self.width, self.height)


class Rect(object):
    def __init__(self, center: Vector2D, size: Size) -> None:
        self.center = center
        self.size = size

    @staticmethod
    def Empty() -> 'Rect':
        return Rect(Vector2D.Empty(), Size.Empty())

    @staticmethod
    def Make(x: float, y: float, width: float, height: float) -> 'Rect':
        return Rect(Vector2D(x, y), Size(width, height))

    def copy(self) -> 'Rect':
        return Rect(self.center.copy(), self.size.copy())


class Color(object):
    r: int
    g: int
    b: int
    a: int

    def __init__(self, r: int, g: int, b: int, a: int) -> None:
        self.r = r
        self.g = g
        self.b = b
        self.a = a
