import sdl2

from engine.settings import GameSettings


class GameContext(object):
    renderer: sdl2.SDL_Renderer
    settings: GameSettings
    quit: bool = False

    def __init__(self, renderer: sdl2.SDL_Renderer, settings: GameSettings) -> None:
        self.renderer = renderer
        self.settings = settings
        if not self.renderer:
            raise RuntimeError("Renderer could not be created. SDL Error: "
                               + str(sdl2.SDL_GetError()))
        if not self.settings:
            raise RuntimeError("Could not load game settings")
