class Vector2D(object):
    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    @classmethod
    def Empty(cls) -> 'Vector2D':
        return cls(0, 0)

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
    width: float
    height: float

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    @classmethod
    def Empty(cls) -> 'Size':
        return cls(0, 0)

    def copy(self) -> 'Size':
        return Size(self.width, self.height)

    def times(self, s: float) -> 'Size':
        return Size(self.width * s, self.height * s)

    def div(self, s: float) -> 'Size':
        return Size(self.width / s, self.height / s)


class Rect(object):
    size: Size
    center: Vector2D

    def __init__(self, center: Vector2D, size: Size) -> None:
        self.center = center.copy()
        self.size = size.copy()

    @classmethod
    def Empty(cls) -> 'Rect':
        return cls(Vector2D.Empty(), Size.Empty())

    @classmethod
    def Make(cls, x: float, y: float, width: float, height: float) -> 'Rect':
        return cls(Vector2D(x, y), Size(width, height))

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
