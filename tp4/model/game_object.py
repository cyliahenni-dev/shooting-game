"""Base class of everything that lives on the game board.

MODEL only: position, size, collisions, update(). Nothing here knows how an
object looks: the VIEW (view/renderer.py) draws it."""
from abc import ABC, abstractmethod
import pygame


def direction(from_pos, to_pos):
    """Unit vector pointing from one position to another."""
    v = pygame.Vector2(to_pos) - pygame.Vector2(from_pos)
    return v.normalize() if v.length() > 0 else pygame.Vector2(1, 0)


class GameObject(ABC):
    """A circle with a position: Player, Monster, Bullet and Reward inherit it."""

    def __init__(self, pos, radius):
        self.pos = pygame.Vector2(pos)
        self.radius = radius

    def collides_with(self, other):
        """Circle collision: distance between centres < sum of the radii."""
        return self.pos.distance_to(other.pos) < self.radius + other.radius

    @abstractmethod
    def update(self, dt):
        """Move / evolve during dt seconds."""
