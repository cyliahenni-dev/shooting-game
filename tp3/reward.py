import pygame
from game_object import GameObject
import settings as cfg


class Reward(GameObject):
    POINTS = "points"
    HEALTH = "health"

    def __init__(self, pos, kind):
        super().__init__(pos, cfg.REWARD_RADIUS)
        self.type = kind
        self.value = cfg.REWARD_POINTS if kind == self.POINTS else cfg.REWARD_HEALTH

    def apply(self, player):
        if self.type == self.POINTS:
            player.score += self.value
        else:
            player.heal(self.value)

    def update(self, dt):
        pass                                  # a reward stays where it dropped

    def draw(self, screen):
        color = (255, 200, 0) if self.type == self.POINTS else (255, 80, 160)
        pygame.draw.circle(screen, color, self.pos, self.radius)
