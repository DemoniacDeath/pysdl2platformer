import sdl2
import sdl2.sdlimage
import sdl2.sdlttf
import ctypes
import random

from core import Rect, Vector2D, Color, Size

from engine import GameObject, GameContext, GameSettings, RenderObject, Animation, PhysicsState, Collision
from typing import Optional

from util import pairRange


class Camera(GameObject):
    def __init__(self, context, frame) -> None:
        super(Camera, self).__init__(context, frame)
        self.originalSize = frame.size.copy()


class World(GameObject):
    def __init__(self, context, frame: Rect) -> None:
        super(World, self).__init__(context, frame)
        self.camera = Camera(self.context, self.frame)

    def handleEvent(self, e: sdl2.SDL_Event) -> None:
        super(World, self).handleEvent(e)
        if e.type == sdl2.SDL_KEYDOWN:
            if e.key.keysym.sym == sdl2.SDLK_q:
                self.context.quit = True


class Solid(GameObject):
    def __init__(self, context: 'GameContext', frame: Rect) -> None:
        super().__init__(context, frame)
        self.physics = PhysicsState(self)

    def handleEnterCollision(self, collision: Collision) -> None:
        if collision.collider.physics.velocity.y > 5 and isinstance(collision.collider, Player):
            collision.collider.dealDamage(round(collision.collider.physics.velocity.y * 10))

    def handleCollision(self, collision: Collision) -> None:
        if abs(collision.collisionVector.x) < abs(collision.collisionVector.y):
            collision.collider.frame.center.x += collision.collisionVector.x
            collision.collider.physics.velocity.x = 0
        else:
            collision.collider.frame.center.y += collision.collisionVector.y
            collision.collider.physics.velocity.y = 0


class Frame(GameObject):
    width: int
    ceiling: Solid
    wallLeft: Solid
    wallRight: Solid
    floor: Solid

    def __init__(self, context: 'GameContext', frame: Rect, width: int) -> None:
        super().__init__(context, frame)
        self.width = width
        self.ceiling = Solid(context, Rect.Make(
            0,
            -frame.size.height / 2 + width / 2,
            frame.size.width,
            width))
        self.wallLeft = Solid(context, Rect.Make(
            -frame.size.width / 2 + width / 2,
            0,
            width,
            frame.size.height - width * 2))
        self.wallRight = Solid(context, Rect.Make(
            frame.size.width / 2 - width / 2,
            0,
            width,
            frame.size.height - width * 2))
        self.floor = Solid(context, Rect.Make(
            0,
            frame.size.height / 2 - width / 2,
            frame.size.width,
            width))
        self.ceiling.renderObject = RenderObject.RenderObjectFromColor(context.renderer, Color(0, 0, 0, 0xFF))
        self.wallLeft.renderObject = RenderObject.RenderObjectFromColor(context.renderer, Color(0, 0, 0, 0xFF))
        self.wallRight.renderObject = RenderObject.RenderObjectFromColor(context.renderer, Color(0, 0, 0, 0xFF))
        self.floor.renderObject = RenderObject.RenderObjectFromColor(context.renderer, Color(0, 0, 0, 0xFF))
        self.addChild(self.ceiling)
        self.addChild(self.wallLeft)
        self.addChild(self.wallRight)
        self.addChild(self.floor)


class UI(GameObject):
    pass


class Consumable(GameObject):
    def __init__(self, context: 'GameContext', frame: Rect) -> None:
        super().__init__(context, frame)
        self.physics = PhysicsState(self)


class Player(GameObject):
    speed: float
    jumpSpeed: float
    power: int
    jumped: bool
    originalSize: Size
    crouched: bool
    health: int
    dead: bool
    won: bool
    idleAnimation: Optional[Animation]
    moveAnimation: Optional[Animation]
    jumpAnimation: Optional[Animation]
    crouchAnimation: Optional[Animation]
    crouchMoveAnimation: Optional[Animation]

    def __init__(self, context: GameContext, frame: Rect) -> None:
        super(Player, self).__init__(context, frame)
        self.speed = 0
        self.jumpSpeed = 0
        self.power = 0
        self.jumped = False
        self.originalSize = frame.size.copy()
        self.crouched = False
        self.health = 100
        self.dead = False
        self.won = False
        self.idleAnimation = None
        self.moveAnimation = None
        self.jumpAnimation = None
        self.crouchAnimation = None
        self.crouchMoveAnimation = None
        self.physics = PhysicsState(self)
        self.physics.gravity = True
        self.physics.still = False

    def handleEvent(self, e: sdl2.SDL_Event) -> None:
        if e.type == sdl2.SDL_KEYDOWN and e.key.keysym.sym == sdl2.SDLK_g:
            self.physics.gravity = not self.physics.gravity
            if not self.physics.gravity:
                self.jumped = True
                self.physics.velocity = Vector2D.Empty()
        super(Player, self).handleEvent(e)

    def handleKeyboard(self, state) -> None:
        super(Player, self).handleKeyboard(state)
        if self.dead:
            return
        sit_down = False
        move_left = False
        move_right = False
        move_vector = Vector2D.Empty()
        if state[sdl2.SDL_SCANCODE_LEFT] or state[sdl2.SDL_SCANCODE_A]:
            move_vector.x -= self.speed
            move_left = True
        if state[sdl2.SDL_SCANCODE_RIGHT] or state[sdl2.SDL_SCANCODE_D]:
            move_vector.x += self.speed
            move_right = True
        if state[sdl2.SDL_SCANCODE_UP] or state[sdl2.SDL_SCANCODE_W] or state[sdl2.SDL_SCANCODE_SPACE]:
            if not self.physics.gravity:
                move_vector.y -= self.speed
            elif not self.jumped:
                self.physics.velocity.y -= self.jumpSpeed
                self.jumped = True
        if state[sdl2.SDL_SCANCODE_DOWN] or state[sdl2.SDL_SCANCODE_S] or state[sdl2.SDL_SCANCODE_LCTRL] or state[sdl2.SDL_SCANCODE_RCTRL]:
            if not self.physics.gravity:
                move_vector.y += self.speed
            else:
                sit_down = True

        self.setCrouched(sit_down)

        self.frame.center.x += move_vector.x
        self.frame.center.y += move_vector.y

    def dealDamage(self, damage: int) -> None:
        if not self.won:
            self.health -= damage
            # TODO: set value for healthBar
            if self.health < 0:
                self.die()

    def die(self) -> None:
        self.dead = True

    def win(self) -> None:
        self.won = True

    def setCrouched(self, crouched: bool) -> None:
        if crouched and not self.crouched:
            self.crouched = True
            self.frame.size.height = self.originalSize.height / 2
            self.frame.center.y += self.frame.size.height / 2
        elif not crouched and self.crouched:
            self.crouched = False
            self.frame.size.height = self.originalSize.height
            self.frame.center.y -= self.frame.size.height / 2

    def handleEnterCollision(self, collision: Collision) -> None:
        if isinstance(collision.collider, Consumable):
            self.power += 1
            # TODO set value for powerBar
            collision.collider.removed = True
            self.speed += 0.01
            self.jumpSpeed += 0.01
            if self.power > 99:
                self.win()

    def handleExitCollision(self, collider: 'GameObject') -> None:
        if not len(self.physics.colliders):
            self.jumped = True

    def handleCollision(self, collision: Collision) -> None:
        if abs(collision.collisionVector.x) > abs(collision.collisionVector.y):
            if collision.collisionVector.y > 0 and self.jumped and self.physics.gravity:
                self.jumped = False


def Exit() -> None:
    sdl2.SDL_Quit()
    sdl2.sdlimage.IMG_Quit()
    sdl2.sdlttf.TTF_Quit()


class Game:
    context: GameContext
    world: World
    ui: UI

    def __init__(self) -> None:
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
            raise RuntimeError("SDL could not initialize! SDL Error: " + sdl2.SDL_GetError())

        if not sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, b"1"):
            print("Warning: Linear texture filtering not enabled.")

        img_flags = sdl2.sdlimage.IMG_INIT_PNG
        if not (sdl2.sdlimage.IMG_Init(img_flags) & img_flags):
            raise RuntimeError("SDL_image could not initialize! SDL_image Error: " + sdl2.sdlimage.IMG_GetError())

        if sdl2.sdlttf.TTF_Init == -1:
            raise RuntimeError("SDL_ttf could not initialize! SDL_ttf Error: " + sdl2.sdlttf.TTF_GetError())

        settings = GameSettings('Test game', 800, 600)

        window = sdl2.SDL_CreateWindow(bytes(settings.name, 'utf-8'),
                                       sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
                                       settings.windowWidth,
                                       settings.windowHeight,
                                       sdl2.SDL_WINDOW_SHOWN
                                       )
        if not window:
            raise RuntimeError("Window could not be created. SDL Error: " + sdl2.SDL_GetError())

        self.context = GameContext(
            sdl2.SDL_CreateRenderer(window, -1, sdl2.SDL_RENDERER_ACCELERATED | sdl2.SDL_RENDERER_PRESENTVSYNC),
            settings)

        sdl2.SDL_SetRenderDrawColor(self.context.renderer, 0xff, 0xff, 0xff, 0xff)

        self.world = World(
            self.context,
            Rect.Make(
                0, 0,
                self.context.settings.windowWidth / 2,
                self.context.settings.windowHeight / 2))

        self.ui = UI(self.context, Rect(Vector2D.Empty(), self.world.camera.originalSize.copy()))

        player = Player(self.context, Rect.Make(0, 20, 10, 20))
        player.renderObject = RenderObject.RenderObjectFromColor(self.context.renderer, Color(0, 0, 0, 255))
        player.speed = 1.3
        player.jumpSpeed = 2.5
        player.physics.gravityForce = 0.1
        player.addChild(self.world.camera)

        self.world.addChild(Frame(self.context, Rect.Make(
            0, 0,
            self.world.frame.size.width,
            self.world.frame.size.height
        ), 10))

        count = 200
        power_count = 100
        x = int(self.world.frame.size.width / 10 - 2)
        y = int(self.world.frame.size.height / 10 - 2)
        pairs = random.sample(set(pairRange(x, y)), count)
        for pair in pairs:
            random_x = pair[0]
            random_y = pair[1]

            rect = Rect.Make(
                    (self.world.frame.size.width / 2) - 15 - random_x * 10,
                    (self.world.frame.size.height / 2) - 15 - random_y * 10,
                    10, 10)
            if power_count:
                object = Consumable(self.context, rect)
                object.renderObject = RenderObject.RenderObjectFromColor(self.context.renderer, Color(0, 0xff, 0, 0x80))
                self.world.addChild(object)
                power_count -= 1
            else:
                object = Solid(self.context, rect)
                object.renderObject = RenderObject.RenderObjectFromColor(self.context.renderer, Color(0, 0, 0, 0))
                self.world.addChild(object)

        self.world.addChild(player)

    def run(self) -> None:
        e = sdl2.SDL_Event()
        while not self.context.quit:
            while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                if e.type == sdl2.SDL_QUIT:
                    self.context.quit = True
                self.world.handleEvent(e)

            self.world.handleKeyboard(sdl2.SDL_GetKeyboardState(None))

            self.world.clean()

            self.world.processPhysics()

            self.world.detectCollisions()

            self.world.animate()

            sdl2.SDL_SetRenderDrawColor(self.context.renderer, 0xff, 0xff, 0xff, 0xff)
            sdl2.SDL_RenderClear(self.context.renderer)

            self.world.render(
                self.world.frame.center,
                self.world.camera.globalPosition(),
                self.world.camera.frame.size)
            self.ui.render(
                self.ui.frame.center,
                Vector2D.Empty(),
                self.world.camera.originalSize)

            sdl2.SDL_RenderPresent(self.context.renderer)

        Exit()
