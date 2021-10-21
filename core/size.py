from __future__ import annotations


class Size(object):
    width: float
    height: float

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def copy(self) -> Size:
        return Size(self.width, self.height)

    def __mul__(self, scalar: float) -> Size:
        return Size(self.width * scalar, self.height * scalar)
