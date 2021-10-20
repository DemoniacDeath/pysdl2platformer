from __future__ import annotations

from typing import Set, List

import sdl2

from core.rect import Rect
from core.size import Size
from core.vector2d import Vector2D
from engine.animation import Animation
from engine.context import GameContext
from engine.physics import PhysicsState, Collision
from engine.render import RenderObject


class GameObject(object):
    children: Set[GameObject]
    renderObject: RenderObject | None
    animation: Animation | None
    physics: PhysicsState | None
    frame: Rect
    visible: bool
    removed: bool
    parent: GameObject | None
    context: GameContext

    def __init__(self, context: GameContext, frame: Rect) -> None:
        self.children = set()
        self.renderObject = None
        self.animation = None
        self.physics = None
        self.frame = frame
        self.visible = True
        self.removed = False
        self.parent = None
        self.context = context

    def handle_event(self, e: sdl2.SDL_Event) -> None:
        for child in self.children:
            child.handle_event(e)

    def handle_keyboard(self, state) -> None:
        for child in self.children:
            child.handle_keyboard(state)

    def process_physics(self) -> None:
        if self.physics:
            self.physics.change()

        for child in self.children:
            child.process_physics()

    def detect_collisions(self) -> None:
        collected_colliders: List[PhysicsState] = list()
        self.collect_colliders(collected_colliders)
        for i in range(len(collected_colliders)):
            for j in range(i + 1, len(collected_colliders)):
                collected_colliders[i].detect_collision(collected_colliders[j])

    def collect_colliders(self, collected_colliders: List[PhysicsState]) -> None:
        if self.physics:
            collected_colliders.append(self.physics)

        for child in self.children:
            child.collect_colliders(collected_colliders)

    def handle_enter_collision(self, collision: Collision) -> None:
        pass

    def handle_exit_collision(self, collider: GameObject) -> None:
        pass

    def handle_collision(self, collision: Collision) -> None:
        pass

    def animate(self) -> None:
        if self.animation:
            self.renderObject = self.animation.animate()

        for child in self.children:
            child.animate()

    def render(self, local_basis: Vector2D, camera_position: Vector2D, camera_size: Size) -> None:
        global_position = self.frame.center.plus(local_basis)
        if self.visible and self.renderObject:
            self.renderObject.render(self.context, global_position, self.frame.size, camera_position, camera_size)
        for child in self.children:
            child.render(global_position, camera_position, camera_size)

    def add_child(self, child) -> None:
        self.children.add(child)
        child.parent = self

    def clean(self) -> None:
        for child in self.children.copy():
            if child.removed:
                self.children.remove(child)

    def global_position(self) -> Vector2D:
        if self.parent:
            return self.frame.center.plus(self.parent.global_position())
        else:
            return self.frame.center
