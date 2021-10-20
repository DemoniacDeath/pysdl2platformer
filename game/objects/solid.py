from core.rect import Rect
from engine.context import GameContext
from engine.gameobject import GameObject
from engine.physics import PhysicsState, Collision
from game.objects.player import Player


class Solid(GameObject):
    def __init__(self, context: GameContext, frame: Rect) -> None:
        super().__init__(context, frame)
        self.physics = PhysicsState(self)

    def handle_enter_collision(self, collision: Collision) -> None:
        if collision.collider.physics.velocity.y > 5 and isinstance(collision.collider, Player):
            collision.collider.deal_damage(round(collision.collider.physics.velocity.y * 10))

    def handle_collision(self, collision: Collision) -> None:
        if abs(collision.collision_vector.x) < abs(collision.collision_vector.y):
            collision.collider.frame.center.x += collision.collision_vector.x
            collision.collider.physics.velocity.x = 0
        else:
            collision.collider.frame.center.y += collision.collision_vector.y
            collision.collider.physics.velocity.y = 0
