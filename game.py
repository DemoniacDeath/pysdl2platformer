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

    def handleKeyboard(self, state) -> None:
        if state[sdl2.SDL_SCANCODE_Z]:
            self.frame.size.width = self.originalSize.width * 2
            self.frame.size.height = self.originalSize.height * 2
        else:
            self.frame.size = self.originalSize.copy()


class World(GameObject):
    def __init__(self, context, frame: Rect) -> None:
        super(World, self).__init__(context, frame)
        self.camera = Camera(self.context, Rect(self.frame.center, self.frame.size.div(2)))

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


class Consumable(GameObject):
    def __init__(self, context: 'GameContext', frame: Rect) -> None:
        super().__init__(context, frame)
        self.physics = PhysicsState(self)


class Bar(GameObject):
    value: float
    originalFrame: Rect

    def __init__(self, context: 'GameContext', frame: Rect) -> None:
        super().__init__(context, frame)
        self.value = 100
        self.originalFrame = frame.copy()

    def setValue(self, newValue: float) -> None:
        if newValue > 100:
            newValue = 100
        if newValue < 0:
            newValue = 0
        self.value = newValue

        self.frame = Rect(
            Vector2D(
                self.originalFrame.center.x + self.originalFrame.size.width*((newValue - 100) / 200),
                self.originalFrame.center.y
            ),
            Size(
                self.originalFrame.size.width / 100 * newValue,
                self.originalFrame.size.height
            )
        )


class Text(GameObject):
    font: Optional[sdl2.sdlttf.TTF_Font]
    text: bytes
    color: Optional[sdl2.SDL_Color]

    def __init__(self, context: 'GameContext', frame: Rect) -> None:
        super().__init__(context, frame)
        self.font = None
        self.text = b""
        self.color = None

    def setText(self, newText: bytes) -> None:
        self.text = newText
        self.generate()

    def setFont(self, path: bytes, size: int) -> None:
        self.font = sdl2.sdlttf.TTF_OpenFont(path, size)
        if not self.font:
            raise RuntimeError("Could not load font at "
                               + str(path)
                               + "! SDL_ttf error: "
                               + str(sdl2.sdlttf.TTF_GetError()))
        self.generate()

    def setColor(self, newColor: sdl2.SDL_Color) -> None:
        self.color = newColor
        self.generate()

    def generate(self) -> None:
        if self.font and len(self.text) and self.color:
            surface = sdl2.sdlttf.TTF_RenderText_Solid(self.font, self.text, self.color)
            self.renderObject = RenderObject.RenderObjectFromSurface(self.context.renderer, surface)
            sdl2.SDL_FreeSurface(surface)


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
    powerBar: Optional[Bar]
    healthBar: Optional[Bar]
    deathText: Optional[Text]
    winText: Optional[Text]

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

        if move_left and not move_right:
            self.moveAnimation.turnLeft(True)
            self.crouchAnimation.turnLeft(True)
            self.crouchMoveAnimation.turnLeft(True)
        if move_right and not move_left:
            self.moveAnimation.turnLeft(False)
            self.crouchAnimation.turnLeft(False)
            self.crouchMoveAnimation.turnLeft(False)

        if not move_left and not move_right and not self.jumped and not self.crouched:
            self.animation = self.idleAnimation
        if not move_left and not move_right and not self.jumped and self.crouched:
            self.animation = self.crouchAnimation
        if (move_left or move_right) and not self.jumped and not self.crouched:
            self.animation = self.moveAnimation
        if (move_left or move_right) and not self.jumped and self.crouched:
            self.animation = self.crouchMoveAnimation
        if self.jumped and self.crouched:
            self.animation = self.crouchAnimation
        if self.jumped and not self.crouched:
            self.animation = self.jumpAnimation

        self.frame.center.x += move_vector.x
        self.frame.center.y += move_vector.y

    def dealDamage(self, damage: int) -> None:
        if not self.won:
            self.health -= damage
            self.healthBar.setValue(self.health)
            if self.health < 0:
                self.die()

    def die(self) -> None:
        self.deathText.visible = True
        self.dead = True

    def win(self) -> None:
        self.winText.visible = True
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
            self.powerBar.setValue(self.power)
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
    ui: GameObject

    def __init__(self) -> None:
        if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) < 0:
            raise RuntimeError("SDL could not initialize! SDL Error: "
                               + str(sdl2.SDL_GetError()))

        if not sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, b"1"):
            print("Warning: Linear texture filtering not enabled.")

        img_flags = sdl2.sdlimage.IMG_INIT_PNG
        if not (sdl2.sdlimage.IMG_Init(img_flags) & img_flags):
            raise RuntimeError("SDL_image could not initialize! SDL_image Error: "
                               + str(sdl2.sdlimage.IMG_GetError()))

        if sdl2.sdlttf.TTF_Init() == -1:
            raise RuntimeError("SDL_ttf could not initialize! SDL_ttf Error: "
                               + str(sdl2.sdlttf.TTF_GetError()))

        settings = GameSettings('Test game', 800, 600)

        window = sdl2.SDL_CreateWindow(bytes(settings.name, 'utf-8'),
                                       sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
                                       settings.windowWidth,
                                       settings.windowHeight,
                                       sdl2.SDL_WINDOW_SHOWN
                                       )
        if not window:
            raise RuntimeError("Window could not be created. SDL Error: "
                               + str(sdl2.SDL_GetError()))

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

        self.ui = GameObject(self.context, Rect(Vector2D.Empty(), self.world.camera.originalSize.copy()))

        player = Player(self.context, Rect.Make(0, 20, 10, 20))
        player.idleAnimation = Animation.AnimationWithSingleRenderObject(
            RenderObject.RenderObjectFromFile(self.context.renderer, b"img/idle.png"))
        player.moveAnimation = Animation.AnimationWithSpeedAndTexturePath(
            80, self.context.renderer, b"img/move.png", 40, 80, 6)
        player.jumpAnimation = Animation.AnimationWithSingleRenderObject(
            RenderObject.RenderObjectFromFile(self.context.renderer, b"img/jump.png"))
        player.crouchAnimation = Animation.AnimationWithSingleRenderObject(
            RenderObject.RenderObjectFromFile(self.context.renderer, b"img/crouch.png"))
        player.crouchMoveAnimation = Animation.AnimationWithSingleRenderObject(
            RenderObject.RenderObjectFromFile(self.context.renderer, b"img/crouch.png"))

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
                game_object = Consumable(self.context, rect)
                game_object.renderObject = RenderObject.RenderObjectFromColor(
                    self.context.renderer, Color(0, 0xff, 0, 0x80))
                power_count -= 1
            else:
                game_object = Solid(self.context, rect)
                game_object.renderObject = RenderObject.RenderObjectFromFile(self.context.renderer, b"img/brick.png")
            self.world.addChild(game_object)

        self.world.addChild(player)

        self.ui = GameObject(self.context, Rect(Vector2D.Empty(), self.world.camera.originalSize))

        death_text = Text(self.context, Rect.Make(0, 0, 100, 10))
        death_text.setText(b"You died! Game Over!")
        death_text.setFont(b"fonts/Scratch_.ttf", 28)
        death_text.setColor(sdl2.SDL_Color(0xff, 0, 0))
        death_text.visible = False
        self.ui.addChild(death_text)
        player.deathText = death_text

        win_text = Text(self.context, Rect.Make(0, 0, 100, 10))
        win_text.setText(b"Congratulations! You won!")
        win_text.setFont(b"fonts/Scratch_.ttf", 28)
        win_text.setColor(sdl2.SDL_Color(0, 0xff, 0))
        win_text.visible = False
        self.ui.addChild(win_text)
        player.winText = win_text

        health_bar_holder = GameObject(self.context, Rect.Make(
            -self.world.camera.originalSize.width/2 + 16,
            -self.world.camera.originalSize.height/2 + 2.5,
            30, 3))
        health_bar_holder.renderObject = RenderObject.RenderObjectFromColor(self.context.renderer, Color(0, 0, 0, 0xff))
        self.ui.addChild(health_bar_holder)

        power_bar_holder = GameObject(self.context, Rect.Make(
            self.world.camera.originalSize.width/2 - 16,
            -self.world.camera.originalSize.height/2 + 2.5,
            30, 3))
        power_bar_holder.renderObject = RenderObject.RenderObjectFromColor(self.context.renderer, Color(0, 0, 0, 0xff))
        self.ui.addChild(power_bar_holder)

        health_bar = Bar(self.context, Rect.Make(0, 0, 29, 2))
        health_bar.renderObject = RenderObject.RenderObjectFromColor(self.context.renderer, Color(0xff, 0, 0, 0xff))
        health_bar_holder.addChild(health_bar)
        player.healthBar = health_bar

        power_bar = Bar(self.context, Rect.Make(0, 0, 29, 2))
        power_bar.renderObject = RenderObject.RenderObjectFromColor(self.context.renderer, Color(0, 0xff, 0, 0xff))
        power_bar.setValue(0)
        power_bar_holder.addChild(power_bar)
        player.powerBar = power_bar

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
