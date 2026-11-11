"""SRP: Health only stores hit points, HealthBar only draws them.

A monster no longer draws its own health bar: it owns a Health,
and the board asks a HealthBar to render it."""
import pygame


class Health:
    def __init__(self, max_hp):
        self.max_hp = self.hp = max_hp

    def take(self, amount):
        self.hp = max(0, self.hp - amount)

    @property
    def alive(self):
        return self.hp > 0

    @property
    def ratio(self):
        return self.hp / self.max_hp


class HealthBar:
    """Only responsible for rendering a Health on the screen."""

    def render(self, screen, health, x, y, width=36, height=5):
        pygame.draw.rect(screen, (200, 40, 40), (x, y, width, height))
        pygame.draw.rect(screen, (40, 200, 40), (x, y, width * health.ratio, height))
