class GameSettings(object):
    name: str
    windowWidth: int
    windowHeight: int

    def __init__(self, name: str, window_width: int, window_height: int) -> None:
        self.name = name
        self.windowWidth = window_width
        self.windowHeight = window_height
