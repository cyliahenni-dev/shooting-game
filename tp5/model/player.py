import pygame
from model.game_object import GameObject, direction
from model.bullet import Bullet
from model.weapons import default_weapons
import settings as cfg


class Player(GameObject):
    def __init__(self, pos, weapons=None):
        super().__init__(pos, cfg.PLAYER_RADIUS)
        self.speed = cfg.PLAYER_SPEED
        self.health = cfg.PLAYER_HEALTH
        self.weapons = list(weapons) if weapons else default_weapons()     # given by the world
        self._selected = 0
        self.score = 0
        self._cooldown = 0.0                 # private: time before next shot
        self.aim_point = pygame.Vector2(pos) + (1, 0)

    @property
    def is_alive(self):
        return self.health > 0

    @property
    def weapon(self):
        """The weapon in use."""
        return self.weapons[self._selected]

    def set_weapons(self, weapons):
        """New weapons (a new world). The selected slot is kept."""
        self.weapons = list(weapons)
        self._selected = min(self._selected, len(self.weapons) - 1)

    def select_weapon(self, index):
        if 0 <= index < len(self.weapons):
            self._selected = index

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
        self._cooldown = self.weapon.delay
        return Bullet(self.pos, direction(self.pos, self.aim_point), self.weapon.damage,
                      self.weapon.damage_type)

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def heal(self, amount):
        self.health = min(cfg.PLAYER_HEALTH, self.health + amount)

    def update(self, dt):
        self._cooldown = max(0.0, self._cooldown - dt)
