from __future__ import annotations


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

    @classmethod
    def black(cls) -> Color:
        return Color(0x00, 0x00, 0x00, 0xff)

    @classmethod
    def red(cls) -> Color:
        return Color(0xff, 0x00, 0x00, 0xff)

    @classmethod
    def green(cls) -> Color:
        return Color(0x00, 0xff, 0x00, 0xff)

    @classmethod
    def blue(cls) -> Color:
        return Color(0x00, 0x00, 0xff, 0xff)
