import pygame
from game_object import GameObject, direction
from bullet import Bullet
import settings as cfg


class Player(GameObject):
    def __init__(self, pos):
        super().__init__(pos, cfg.PLAYER_RADIUS)
        self.speed = cfg.PLAYER_SPEED
        self.health = cfg.PLAYER_HEALTH
        self.weapon_damage = cfg.BULLET_DAMAGE
        self.score = 0
        self._cooldown = 0.0                 # private: time before next shot
        self.aim_point = pygame.Vector2(pos) + (1, 0)

    @property
    def is_alive(self):
        return self.health > 0

    def aim(self, target):
        self.aim_point = pygame.Vector2(target)

    def move(self, move_dir, dt, width, height):
        """move_dir: vector built from the keys; the player stays in the area."""
        d = pygame.Vector2(move_dir)
        if d.length() > 0:
            self.pos += d.normalize() * self.speed * dt
        self.pos.x = max(self.radius, min(width - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(height - self.radius, self.pos.y))

    def shoot(self):
        """Return a Bullet toward the aim point, or None while reloading."""
        if self._cooldown > 0:
            return None
        self._cooldown = cfg.SHOOT_DELAY
        return Bullet(self.pos, direction(self.pos, self.aim_point), self.weapon_damage)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def heal(self, amount):
        self.health = min(cfg.PLAYER_HEALTH, self.health + amount)

    def update(self, dt):
        self._cooldown = max(0.0, self._cooldown - dt)

    def draw(self, screen):
        pygame.draw.circle(screen, (60, 160, 255), self.pos, self.radius)
        tip = self.pos + direction(self.pos, self.aim_point) * (self.radius + 8)
        pygame.draw.line(screen, (255, 255, 255), self.pos, tip, 4)
