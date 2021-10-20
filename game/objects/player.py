from typing import Optional

import sdl2

from core.rect import Rect
from core.size import Size
from core.vector2d import Vector2D
from engine.animation import Animation
from engine.context import GameContext
from engine.gameobject import GameObject
from engine.physics import PhysicsState, Collision
from game.objects.consumable import Consumable
from game.objects.ui.bar import Bar
from game.objects.ui.text import Text


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

    def handle_event(self, e: sdl2.SDL_Event) -> None:
        if e.type == sdl2.SDL_KEYDOWN and e.key.keysym.sym == sdl2.SDLK_g:
            self.physics.gravity = not self.physics.gravity
            if not self.physics.gravity:
                self.jumped = True
                self.physics.velocity = Vector2D.empty()
        super(Player, self).handle_event(e)

    def handle_keyboard(self, state) -> None:
        super(Player, self).handle_keyboard(state)
        if self.dead:
            return
        sit_down = False
        move_left = False
        move_right = False
        move_vector = Vector2D.empty()

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
        if state[sdl2.SDL_SCANCODE_DOWN] \
                or state[sdl2.SDL_SCANCODE_S] \
                or state[sdl2.SDL_SCANCODE_LCTRL] \
                or state[sdl2.SDL_SCANCODE_RCTRL]:
            if not self.physics.gravity:
                move_vector.y += self.speed
            else:
                sit_down = True

        self.set_crouched(sit_down)

        if move_left and not move_right:
            self.moveAnimation.turn_left(True)
            self.crouchAnimation.turn_left(True)
            self.crouchMoveAnimation.turn_left(True)
        if move_right and not move_left:
            self.moveAnimation.turn_left(False)
            self.crouchAnimation.turn_left(False)
            self.crouchMoveAnimation.turn_left(False)

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

    def deal_damage(self, damage: int) -> None:
        if not self.won:
            self.health -= damage
            self.healthBar.set_value(self.health)
            if self.health < 0:
                self.die()

    def die(self) -> None:
        self.deathText.visible = True
        self.dead = True

    def win(self) -> None:
        self.winText.visible = True
        self.won = True

    def set_crouched(self, crouched: bool) -> None:
        if crouched and not self.crouched:
            self.crouched = True
            self.frame.size.height = self.originalSize.height / 2
            self.frame.center.y += self.frame.size.height / 2
        elif not crouched and self.crouched:
            self.crouched = False
            self.frame.size.height = self.originalSize.height
            self.frame.center.y -= self.frame.size.height / 2

    def handle_enter_collision(self, collision: Collision) -> None:
        if isinstance(collision.collider, Consumable):
            self.power += 1
            self.powerBar.set_value(self.power)
            collision.collider.removed = True
            self.speed += 0.01
            self.jumpSpeed += 0.01
            if self.power > 99:
                self.win()

    def handle_exit_collision(self, collider: GameObject) -> None:
        if not len(self.physics.colliders):
            self.jumped = True

    def handle_collision(self, collision: Collision) -> None:
        if abs(collision.collision_vector.x) > abs(collision.collision_vector.y):
            if collision.collision_vector.y > 0 and self.jumped and self.physics.gravity:
                self.jumped = False
