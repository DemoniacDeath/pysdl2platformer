from __future__ import annotations

from typing import Set

import engine.gameobject
from core.vector2d import Vector2D


class PhysicsState(object):
    velocity: Vector2D
    gravity: bool
    still: bool
    gravityForce: float
    colliders: Set[engine.gameobject.GameObject]
    game_object: engine.gameobject.GameObject

    def __init__(self, game_object: engine.gameobject.GameObject) -> None:
        self.velocity = Vector2D.empty()
        self.gravity = False
        self.still = True
        self.gravityForce = 0
        self.colliders = set()
        self.game_object = game_object

    def change(self) -> None:
        if self.gravity:
            self.velocity.y += self.gravityForce
        self.game_object.frame.center.x += self.velocity.x
        self.game_object.frame.center.y += self.velocity.y

    def detect_collision(self, collider: PhysicsState) -> None:
        if self.still and collider.still:
            return

        self_position = self.game_object.global_position()
        collider_position = collider.game_object.global_position()
        self_size = self.game_object.frame.size
        collider_size = collider.game_object.frame.size

        dx1 = self_position.x \
              + self_size.width / 2 \
              - (collider_position.x - collider_size.width / 2)
        dy1 = self_position.y \
              + self_size.height / 2 \
              - (collider_position.y - collider_size.height / 2)
        dx2 = self_position.x \
              - self_size.width / 2 \
              - (collider_position.x + collider_size.width / 2)
        dy2 = self_position.y \
              - self_size.height / 2 \
              - (collider_position.y + collider_size.height / 2)

        already_collided = self.colliders.__contains__(collider.game_object) \
                           or collider.colliders.__contains__(self.game_object)
        if dx1 > 0 > dx2 and dy1 > 0 > dy2:
            overlap_area = Vector2D(
                dx1 if abs(dx1) < abs(dx2) else dx2,
                dy1 if abs(dy1) < abs(dy2) else dy2)
            if not already_collided:
                self.colliders.add(collider.game_object)
                collider.colliders.add(self.game_object)

                self.game_object.handle_enter_collision(Collision(collider.game_object, overlap_area))
                collider.game_object.handle_enter_collision(Collision(self.game_object, overlap_area.times(-1)))
            self.game_object.handle_collision(Collision(collider.game_object, overlap_area))
            collider.game_object.handle_collision(Collision(self.game_object, overlap_area.times(-1)))
        elif already_collided:
            self.colliders.remove(collider.game_object)
            collider.colliders.remove(self.game_object)
            self.game_object.handle_exit_collision(collider.game_object)
            collider.game_object.handle_exit_collision(self.game_object)


class Collision(object):
    collider: engine.gameobject.GameObject
    collision_vector: Vector2D

    def __init__(self, collider: engine.gameobject.GameObject, collision_vector: Vector2D):
        self.collider = collider
        self.collision_vector = collision_vector
