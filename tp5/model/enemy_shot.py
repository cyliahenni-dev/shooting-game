import pygame
from model.game_object import GameObject
import settings as cfg


class EnemyShot(GameObject):
    """Projectile fired by a Shooter monster."""

    def __init__(self, pos, dir_vector):
        super().__init__(pos, cfg.ENEMY_SHOT_RADIUS)
        self.dir = pygame.Vector2(dir_vector)
        self.speed = cfg.ENEMY_SHOT_SPEED
        self.damage = cfg.ENEMY_SHOT_DAMAGE

    def update(self, dt):
        self.pos += self.dir * self.speed * dt

    def is_outside(self, width, height, margin=20):
        return not (-margin <= self.pos.x <= width + margin and -margin <= self.pos.y <= height + margin)
