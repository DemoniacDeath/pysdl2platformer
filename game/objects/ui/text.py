from typing import Optional

import sdl2
import sdl2.sdlttf

from core.rect import Rect
from engine.context import GameContext
from engine.gameobject import GameObject
from engine.render import RenderObject


class Text(GameObject):
    font: Optional[sdl2.sdlttf.TTF_Font]
    text: bytes
    color: Optional[sdl2.SDL_Color]

    def __init__(self, context: GameContext, frame: Rect) -> None:
        super().__init__(context, frame)
        self.font = None
        self.text = b""
        self.color = None

    def set_text(self, new_text: bytes) -> None:
        self.text = new_text
        self.generate()

    def set_font(self, path: bytes, size: int) -> None:
        self.font = sdl2.sdlttf.TTF_OpenFont(path, size)
        if not self.font:
            raise RuntimeError("Could not load font at "
                               + str(path)
                               + "! SDL_ttf error: "
                               + str(sdl2.sdlttf.TTF_GetError()))
        self.generate()

    def set_color(self, new_color: sdl2.SDL_Color) -> None:
        self.color = new_color
        self.generate()

    def generate(self) -> None:
        if self.font and len(self.text) and self.color:
            surface = sdl2.sdlttf.TTF_RenderText_Solid(self.font, self.text, self.color)
            self.renderObject = RenderObject.render_object_from_surface(self.context.renderer, surface)
            sdl2.SDL_FreeSurface(surface)
