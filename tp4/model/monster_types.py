"""OCP: new monster types are new subclasses. Monster, GameBoard and Spawner are not edited.

  NormalMonster    chases the player (the TP N1 monster)
  FastMonster      chases, but very fast and fragile
  FlyingMonster    flies in zig-zag, resists bullets
  StrongMonster    slow, shielded, weak to fire
  ImmobileMonster  never moves, shoots at the player
Each one only inherits the abilities it has (ISP) and is used as a Monster (LSP).

MODEL only: the look of each type is in view/renderer.py, chosen from `kind`."""
import math
import pygame
from model.game_object import direction
from model.monster import Monster
from model.abilities import Chaser, Flyer, Shooter, Shielded
from model.damage import ResistantDamage, WeaknessDamage
from model.enemy_shot import EnemyShot


class NormalMonster(Monster, Chaser):
    name = "Normal Monster"
    kind = "normal"

    def chase(self, dt):
        self.pos += direction(self.pos, self.target.pos) * self.speed * dt

    def update(self, dt):
        shots = super().update(dt)
        if self.target is not None:
            self.chase(dt)
        return shots


class FastMonster(NormalMonster):
    name = "Fast Monster"
    kind = "fast"
    base_speed = 190
    base_health = 30
    base_attack = 8
    base_radius = 14


class FlyingMonster(Monster, Flyer):
    name = "Flying Monster"
    kind = "flying"
    base_speed = 110
    base_health = 40
    base_radius = 16

    def __init__(self, pos, **kwargs):
        kwargs.setdefault("damage_strategy", ResistantDamage(["bullet"]))
        super().__init__(pos, **kwargs)

    def fly(self, dt):
        d = direction(self.pos, self.target.pos)
        side = pygame.Vector2(-d.y, d.x) * math.sin(self.t * 4)       # zig-zag
        self.pos += (d + side * 0.9).normalize() * self.speed * dt

    def update(self, dt):
        shots = super().update(dt)
        if self.target is not None:
            self.fly(dt)
        return shots


class StrongMonster(NormalMonster, Shielded):
    name = "Strong Monster"
    kind = "strong"
    base_speed = 55
    base_health = 150
    base_attack = 25
    base_radius = 28
    score_value = 30

    def __init__(self, pos, **kwargs):
        kwargs.setdefault("damage_strategy", WeaknessDamage(["fire"]))
        super().__init__(pos, **kwargs)

    def block(self, damage):
        return damage * 0.5                 # the shield halves the damage


class ImmobileMonster(Monster, Shooter):    # cannot move, still a valid Monster
    name = "Immobile Monster"
    kind = "immobile"
    base_speed = 0
    base_health = 80
    base_radius = 22
    max_alive = 2
    SHOOT_DELAY = 2.2

    def __init__(self, pos, **kwargs):
        super().__init__(pos, **kwargs)
        self._shoot_timer = 1.5

    @classmethod
    def spawn(cls, width, height, rng, avoid=None):
        """It never moves, so it appears inside the area, away from the player."""
        for _ in range(20):
            pos = pygame.Vector2(rng.randint(60, width - 60), rng.randint(60, height - 60))
            if avoid is None or pos.distance_to(avoid) > 150:
                break
        return cls(pos)

    def shoot(self):
        return EnemyShot(self.pos, direction(self.pos, self.target.pos))

    def update(self, dt):
        shots = super().update(dt)
        self._shoot_timer -= dt
        if self._shoot_timer <= 0 and self.target is not None:
            shots.append(self.shoot())
            self._shoot_timer = self.SHOOT_DELAY
        return shots
