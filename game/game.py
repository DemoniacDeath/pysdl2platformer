import ctypes
import random

import sdl2
import sdl2.sdlimage
import sdl2.sdlttf

from core.color import Color
from core.rect import Rect
from core.vector2d import Vector2D
from engine.animation import Animation
from engine.context import GameContext
from engine.gameobject import GameObject
from engine.render import RenderObject
from engine.settings import GameSettings
from game.objects.consumable import Consumable
from game.objects.frame import Frame
from game.objects.player import Player
from game.objects.solid import Solid
from game.objects.ui.bar import Bar
from game.objects.ui.text import Text
from game.objects.world import World
from util import pair_range


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
            Rect.make(
                0, 0,
                self.context.settings.windowWidth / 2,
                self.context.settings.windowHeight / 2))

        self.ui = GameObject(self.context, Rect(Vector2D(), self.world.camera.originalSize.copy()))

        player = Player(self.context, Rect.make(0, 20, 10, 20))
        player.idleAnimation = Animation.animation_with_single_render_object(
            RenderObject.render_object_from_file(self.context.renderer, b"img/idle.png"))
        player.moveAnimation = Animation.animation_with_speed_and_texture_path(
            80, self.context.renderer, b"img/move.png", 40, 80, 6)
        player.jumpAnimation = Animation.animation_with_single_render_object(
            RenderObject.render_object_from_file(self.context.renderer, b"img/jump.png"))
        player.crouchAnimation = Animation.animation_with_single_render_object(
            RenderObject.render_object_from_file(self.context.renderer, b"img/crouch.png"))
        player.crouchMoveAnimation = Animation.animation_with_single_render_object(
            RenderObject.render_object_from_file(self.context.renderer, b"img/crouch.png"))

        player.speed = 1.3
        player.jumpSpeed = 2.5
        player.physics.gravityForce = 0.1
        player.add_child(self.world.camera)

        self.world.add_child(Frame(self.context, Rect.make(
            0, 0,
            self.world.frame.size.width,
            self.world.frame.size.height
        ), 10))

        count = 200
        power_count = 100
        x = int(self.world.frame.size.width / 10 - 2)
        y = int(self.world.frame.size.height / 10 - 2)
        pairs = random.sample(set(pair_range(x, y)), count)
        for pair in pairs:
            random_x = pair[0]
            random_y = pair[1]

            rect = Rect.make(
                (self.world.frame.size.width / 2) - 15 - random_x * 10,
                (self.world.frame.size.height / 2) - 15 - random_y * 10,
                10, 10)
            if power_count:
                game_object = Consumable(self.context, rect)
                game_object.renderObject = RenderObject.render_object_from_color(
                    self.context.renderer, Color(0, 0xff, 0, 0x80))
                power_count -= 1
            else:
                game_object = Solid(self.context, rect)
                game_object.renderObject = RenderObject.render_object_from_file(self.context.renderer,
                                                                                b"img/brick.png")
            self.world.add_child(game_object)

        self.world.add_child(player)

        self.ui = GameObject(self.context, Rect(Vector2D(), self.world.camera.originalSize))

        death_text = Text(self.context, Rect.make(0, 0, 100, 10))
        death_text.set_text(b"You died! Game Over!")
        death_text.set_font(b"fonts/Scratch_.ttf", 28)
        death_text.set_color(sdl2.SDL_Color(0xff, 0, 0))
        death_text.visible = False
        self.ui.add_child(death_text)
        player.deathText = death_text

        win_text = Text(self.context, Rect.make(0, 0, 100, 10))
        win_text.set_text(b"Congratulations! You won!")
        win_text.set_font(b"fonts/Scratch_.ttf", 28)
        win_text.set_color(sdl2.SDL_Color(0, 0xff, 0))
        win_text.visible = False
        self.ui.add_child(win_text)
        player.winText = win_text

        health_bar_holder = GameObject(self.context, Rect.make(
            -self.world.camera.originalSize.width / 2 + 16,
            -self.world.camera.originalSize.height / 2 + 2.5,
            30, 3))
        health_bar_holder.renderObject = RenderObject.render_object_from_color(self.context.renderer, Color.black())
        self.ui.add_child(health_bar_holder)

        power_bar_holder = GameObject(self.context, Rect.make(
            self.world.camera.originalSize.width / 2 - 16,
            -self.world.camera.originalSize.height / 2 + 2.5,
            30, 3))
        power_bar_holder.renderObject = RenderObject.render_object_from_color(self.context.renderer, Color.black())
        self.ui.add_child(power_bar_holder)

        health_bar = Bar(self.context, Rect.make(0, 0, 29, 2))
        health_bar.renderObject = RenderObject.render_object_from_color(self.context.renderer, Color.red())
        health_bar_holder.add_child(health_bar)
        player.healthBar = health_bar

        power_bar = Bar(self.context, Rect.make(0, 0, 29, 2))
        power_bar.renderObject = RenderObject.render_object_from_color(self.context.renderer, Color.green())
        power_bar.set_value(0)
        power_bar_holder.add_child(power_bar)
        player.powerBar = power_bar

    @staticmethod
    def exit() -> None:
        sdl2.SDL_Quit()
        sdl2.sdlimage.IMG_Quit()
        sdl2.sdlttf.TTF_Quit()

    def run(self) -> None:
        e = sdl2.SDL_Event()
        while not self.context.quit:
            while sdl2.SDL_PollEvent(ctypes.byref(e)) != 0:
                if e.type == sdl2.SDL_QUIT:
                    self.context.quit = True
                self.world.handle_event(e)

            self.world.handle_keyboard(sdl2.SDL_GetKeyboardState(None))

            self.world.clean()

            self.world.process_physics()

            self.world.detect_collisions()

            self.world.animate()

            sdl2.SDL_SetRenderDrawColor(self.context.renderer, 0xff, 0xff, 0xff, 0xff)
            sdl2.SDL_RenderClear(self.context.renderer)

            self.world.render(
                self.world.frame.center,
                self.world.camera.global_position(),
                self.world.camera.frame.size)
            self.ui.render(
                self.ui.frame.center,
                Vector2D(),
                self.world.camera.originalSize)

            sdl2.SDL_RenderPresent(self.context.renderer)

        self.exit()
