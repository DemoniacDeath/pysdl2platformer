import sdl2
from typing import Set, List, Optional

from core import Rect, Vector2D, Size, Color


class GameSettings(object):
    name: str
    windowWidth: int
    windowHeight: int

    def __init__(self, name: str, windowWidth: int, windowHeight: int) -> None:
        self.name = name
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight


class RenderObject(object):
    texture: sdl2.SDL_Texture
    renderFrameSize: sdl2.SDL_Rect
    renderFlip: sdl2.SDL_RendererFlip = sdl2.SDL_FLIP_NONE
    fullRender: bool = True

    def __init__(self, texture: sdl2.SDL_Texture) -> None:
        self.texture = texture

    @staticmethod
    def RenderObjectFromSurface(renderer: sdl2.SDL_Renderer, surface: sdl2.SDL_Surface) -> 'RenderObject':
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, surface)
        if not texture:
            raise RuntimeError("Unable to create texture from surface! SDL Error: " + sdl2.SDL_GetError())
        return RenderObject(texture)

    @staticmethod
    def RenderObjectFromColor(renderer: sdl2.SDL_Renderer, color: Color) -> 'RenderObject':
        texture = sdl2.SDL_CreateTexture(renderer, sdl2.SDL_PIXELFORMAT_RGBA8888, sdl2.SDL_TEXTUREACCESS_TARGET, 1, 1)
        sdl2.SDL_SetRenderTarget(renderer, texture)
        sdl2.SDL_SetRenderDrawColor(renderer, color.r, color.g, color.b, color.a)
        sdl2.SDL_RenderClear(renderer)
        sdl2.SDL_SetRenderTarget(renderer, None)
        return RenderObject(texture)

    def render(self, context, position, size, cameraPosition, cameraSize) -> None:
        render_position = position.plus(
            Vector2D(-size.width / 2, -size.height / 2)
        ).minus(cameraPosition).minus(
            Vector2D(-cameraSize.width / 2, -cameraSize.height / 2)
        )

        rect = sdl2.SDL_Rect()
        rect.x = round(context.settings.windowWidth * (render_position.x / cameraSize.width))
        rect.y = round(context.settings.windowHeight * (render_position.y / cameraSize.height))
        rect.w = round(context.settings.windowWidth * (size.width / cameraSize.width))
        rect.h = round(context.settings.windowHeight * (size.height / cameraSize.height))
        render_frame = None
        if not self.fullRender:
            render_frame = self.renderFrameSize
        sdl2.SDL_RenderCopyEx(context.renderer, self.texture, render_frame, rect, 0, None, self.renderFlip)


class Animation(object):
    def animate(self) -> RenderObject:
        pass


class PhysicsState(object):
    velocity: Vector2D
    gravity: bool
    still: bool
    gravityForce: float
    colliders: Set['GameObject']
    gameObject: 'GameObject'

    def __init__(self, gameObject: 'GameObject') -> None:
        self.velocity = Vector2D.Empty()
        self.gravity = False
        self.still = True
        self.gravityForce = 0
        self.colliders = set()
        self.gameObject = gameObject

    def change(self) -> None:
        if self.gravity:
            self.velocity.y += self.gravityForce
        self.gameObject.frame.center.x += self.velocity.x
        self.gameObject.frame.center.y += self.velocity.y

    def detectCollision(s, c: 'PhysicsState') -> None:
        if s.still and c.still:
            return

        x1 = s.gameObject.globalPosition().x - s.gameObject.frame.size.width / 2
        x2 = c.gameObject.globalPosition().x - c.gameObject.frame.size.width / 2
        X1 = x1 + s.gameObject.frame.size.width
        X2 = x2 + c.gameObject.frame.size.width
        y1 = s.gameObject.globalPosition().y - s.gameObject.frame.size.height / 2
        y2 = c.gameObject.globalPosition().y - c.gameObject.frame.size.height / 2
        Y1 = y1 + s.gameObject.frame.size.height
        Y2 = y2 + c.gameObject.frame.size.height

        dX1 = X1 - x2
        dX2 = x1 - X2
        dY1 = Y1 - y2
        dY2 = y1 - Y2

        already_collided = s.colliders.__contains__(c.gameObject) or c.colliders.__contains__(s.gameObject)
        if dX1 > 0 and dX2 < 0 and dY1 > 0 and dY2 < 0:
            overlap_area = Vector2D(
                dX1 if abs(dX1) < abs(dX2) else dX2,
                dY1 if abs(dY1) < abs(dY2) else dY2)
            if not already_collided:
                s.colliders.add(c.gameObject)
                c.colliders.add(s.gameObject)

                s.gameObject.handleEnterCollision(Collision(c.gameObject, overlap_area))
                c.gameObject.handleEnterCollision(Collision(s.gameObject, overlap_area.times(-1)))
            s.gameObject.handleCollision(Collision(c.gameObject, overlap_area))
            c.gameObject.handleCollision(Collision(s.gameObject, overlap_area.times(-1)))
        elif already_collided:
            s.colliders.remove(c.gameObject)
            c.colliders.remove(s.gameObject)
            s.gameObject.handleExitCollision(c.gameObject)
            c.gameObject.handleExitCollision(s.gameObject)


class Collision(object):
    collider: 'GameObject'
    collisionVector: Vector2D

    def __init__(self, collider: 'GameObject', collisionVector: Vector2D):
        self.collider = collider
        self.collisionVector = collisionVector


class GameObject(object):
    children: Set['GameObject']
    renderObject: Optional[RenderObject]
    animation: Optional[Animation]
    physics: Optional[PhysicsState]
    frame: Rect
    visible: bool
    removed: bool
    parent: Optional['GameObject']
    context: 'GameContext'

    def __init__(self, context: 'GameContext', frame: Rect) -> None:
        self.children = set()
        self.renderObject = None
        self.animation = None
        self.physics = None
        self.frame = frame
        self.visible = True
        self.removed = False
        self.parent = None
        self.context = context

    def handleEvent(self, e: sdl2.SDL_Event) -> None:
        for child in self.children:
            child.handleEvent(e)

    def handleKeyboard(self, state) -> None:
        for child in self.children:
            child.handleKeyboard(state)

    def processPhysics(self) -> None:
        if self.physics:
            self.physics.change()

        for child in self.children:
            child.processPhysics()

    def detectCollisions(self) -> None:
        collected_colliders: List[PhysicsState] = list()
        self.collectColliders(collected_colliders)
        for i in range(len(collected_colliders)):
            for j in range(i + 1, len(collected_colliders)):
                collected_colliders[i].detectCollision(collected_colliders[j])

    def collectColliders(self, collectedColliders: List[PhysicsState]) -> None:
        if self.physics:
            collectedColliders.append(self.physics)

        for child in self.children:
            child.collectColliders(collectedColliders)

    def handleEnterCollision(self, collision: Collision) -> None:
        pass

    def handleExitCollision(self, collider: 'GameObject') -> None:
        pass

    def handleCollision(self, collision: Collision) -> None:
        pass

    def animate(self) -> None:
        if self.animation:
            self.renderObject = self.animation.animate()

        for child in self.children:
            child.animate()

    def render(self, localBasis: Vector2D, cameraPosition: Vector2D, cameraSize: Size) -> None:
        global_position = self.frame.center.plus(localBasis)
        if self.visible and self.renderObject:
            self.renderObject.render(self.context, global_position, self.frame.size, cameraPosition, cameraSize)
        for child in self.children:
            child.render(global_position, cameraPosition, cameraSize)

    def addChild(self, child) -> None:
        self.children.add(child)
        child.parent = self

    def clean(self) -> None:
        for child in self.children.copy():
            if child.removed:
                self.children.remove(child)

    def globalPosition(self) -> Vector2D:
        if self.parent:
            return self.frame.center.plus(self.parent.globalPosition())
        else:
            return self.frame.center


class GameContext(object):
    renderer: sdl2.SDL_Renderer
    settings: GameSettings
    quit: bool = False

    def __init__(self, renderer: sdl2.SDL_Renderer, gameSettings: GameSettings) -> None:
        self.renderer = renderer
        self.settings = gameSettings
        if not self.renderer:
            raise RuntimeError("Renderer could not be created. SDL Error: " + sdl2.SDL_GetError())
        if not self.settings:
            raise RuntimeError("Could not load game settings")
