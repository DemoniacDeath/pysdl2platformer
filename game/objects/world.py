import sdl2

from core.rect import Rect
from engine.gameobject import GameObject
from game.objects.camera import Camera


class World(GameObject):
    def __init__(self, context, frame: Rect) -> None:
        super(World, self).__init__(context, frame)
        self.camera = Camera(self.context, Rect(self.frame.center, self.frame.size.div(2)))

    def handle_event(self, e: sdl2.SDL_Event) -> None:
        super(World, self).handle_event(e)
        if e.type == sdl2.SDL_KEYDOWN:
            if e.key.keysym.sym == sdl2.SDLK_q:
                self.context.quit = True
