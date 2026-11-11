"""OCP: new monster types are new subclasses. Monster, GameBoard and Spawner are not edited.

  NormalMonster    chases the player (the TP N1 monster)
  FastMonster      chases, but very fast and fragile
  FlyingMonster    flies in zig-zag, resists bullets
  StrongMonster    slow, shielded, weak to fire
  ImmobileMonster  never moves, shoots at the player
Each one only inherits the abilities it has (ISP) and is used as a Monster (LSP)."""
import math
import pygame
from game_object import direction
from monster import Monster
from abilities import Chaser, Flyer, Shooter, Shielded
from damage import ResistantDamage, WeaknessDamage
from enemy_shot import EnemyShot


class NormalMonster(Monster, Chaser):
    name = "Normal Monster"

    def chase(self, dt):
        self.pos += direction(self.pos, self.target.pos) * self.speed * dt

    def update(self, dt):
        shots = super().update(dt)
        if self.target is not None:
            self.chase(dt)
        return shots


class FastMonster(NormalMonster):
    name = "Fast Monster"
    color = (255, 150, 50)
    base_speed = 190
    base_health = 30
    base_attack = 8
    base_radius = 14

    def draw(self, screen):
        x, y, r = self.pos.x, self.pos.y, self.radius + 3
        pygame.draw.polygon(screen, self.current_color(), [(x, y - r), (x + r, y), (x, y + r), (x - r, y)])
        self.draw_eyes(screen, 4, 2)


class FlyingMonster(Monster, Flyer):
    name = "Flying Monster"
    color = (165, 120, 255)
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

    def draw(self, screen):
        x, y = self.pos.x, self.pos.y
        flap = math.sin(self.t * 14) * 10
        c = self.current_color()
        pygame.draw.polygon(screen, c, [(x, y), (x - 32, y - 8 - flap), (x - 14, y + 8)])
        pygame.draw.polygon(screen, c, [(x, y), (x + 32, y - 8 - flap), (x + 14, y + 8)])
        pygame.draw.circle(screen, c, self.pos, self.radius)
        self.draw_eyes(screen, 5)


class StrongMonster(NormalMonster, Shielded):
    name = "Strong Monster"
    color = (200, 80, 65)
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

    def draw(self, screen):
        r = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        r.center = (self.pos.x, self.pos.y)
        pygame.draw.rect(screen, self.current_color(), r, border_radius=8)
        pygame.draw.arc(screen, (190, 205, 240), r.inflate(14, 14), math.pi / 2, 3 * math.pi / 2, 5)
        self.draw_eyes(screen, 10, 4)


class ImmobileMonster(Monster, Shooter):    # cannot move, still a valid Monster
    name = "Immobile Monster"
    color = (125, 122, 150)
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

    def draw(self, screen):
        x, y, r = self.pos.x, self.pos.y, self.radius
        pts = [(x + r * math.cos(math.pi / 3 * i), y + r * math.sin(math.pi / 3 * i)) for i in range(6)]
        pygame.draw.polygon(screen, self.current_color(), pts)
        pygame.draw.polygon(screen, (80, 78, 100), pts, 3)
        self.draw_eyes(screen, 7, 4)
