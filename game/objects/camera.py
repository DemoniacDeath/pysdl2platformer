import sdl2

from engine.gameobject import GameObject


class Camera(GameObject):
    def __init__(self, context, frame) -> None:
        super(Camera, self).__init__(context, frame)
        self.originalSize = frame.size.copy()

    def handle_keyboard(self, state) -> None:
        if state[sdl2.SDL_SCANCODE_Z]:
            self.frame.size.width = self.originalSize.width * 2
            self.frame.size.height = self.originalSize.height * 2
        else:
            self.frame.size = self.originalSize.copy()
