import pygame
from game_object import GameObject
import settings as cfg


class Bullet(GameObject):
    def __init__(self, pos, dir_vector, damage=cfg.BULLET_DAMAGE):
        super().__init__(pos, cfg.BULLET_RADIUS)
        self.dir = pygame.Vector2(dir_vector)
        self.speed = cfg.BULLET_SPEED
        self.damage = damage

    def update(self, dt):
        self.pos += self.dir * self.speed * dt

    def is_outside(self, width, height):
        return not (0 <= self.pos.x <= width and 0 <= self.pos.y <= height)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 230, 80), self.pos, self.radius)
