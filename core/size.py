from __future__ import annotations


class Size(object):
    width: float
    height: float

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    @classmethod
    def empty(cls) -> Size:
        return cls(0, 0)

    def copy(self) -> Size:
        return Size(self.width, self.height)

    def times(self, s: float) -> Size:
        return Size(self.width * s, self.height * s)

    def div(self, s: float) -> Size:
        return Size(self.width / s, self.height / s)
