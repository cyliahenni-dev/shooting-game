"""Base class of every monster (MODEL: data and behaviour, no drawing).

SRP : health is a Health object (the bar is drawn by the view)
DIP : the damage received comes from an injected DamageStrategy
LSP : every subtype honours the same contract
      update(dt) -> list of EnemyShot,  take_hit(weapon, damage)
OCP : this file is NOT modified when a new monster type is added (monster_types.py).

`kind` is the name of the type ("normal", "fast"...). The view uses it to choose the
image / the shape: the monster itself does not know how it looks."""
import pygame
from model.game_object import GameObject
from model.health import Health
from model.damage import DamageStrategy, NormalDamage
from model.abilities import Shielded
import settings as cfg


class Monster(GameObject):
    name = "Monster"
    kind = "normal"
    base_speed = cfg.MONSTER_SPEED
    base_health = cfg.MONSTER_HEALTH
    base_attack = cfg.MONSTER_ATTACK       # damage dealt to the player on contact
    base_radius = cfg.MONSTER_RADIUS
    score_value = cfg.KILL_POINTS
    max_alive = None                       # a type can limit how many exist at once

    def __init__(self, pos, speed=None, health=None, attack=None,
                 damage_strategy: DamageStrategy = None):
        super().__init__(pos, self.base_radius)
        self.speed = self.base_speed if speed is None else speed
        self.health = Health(self.base_health if health is None else health)
        self.attack = self.base_attack if attack is None else attack
        self.damage_strategy = damage_strategy or NormalDamage()      # injected (DIP)
        self.target = None                 # the Player, set by the GameBoard
        self.t = (self.pos.x + self.pos.y) % 10     # animation / zig-zag timer
        self._hit_cooldown = 0.0           # private: time before the next contact hit
        self._flash = 0.0                  # private: "just hurt" timer

    # ------------------------------------------------------------ creation
    @classmethod
    def spawn_at_edge(cls, width, height, rng, **kwargs):
        """Create a monster just outside one side of the game area."""
        side = rng.choice(["top", "bottom", "left", "right"])
        if side == "top":
            pos = (rng.randint(0, width), -20)
        elif side == "bottom":
            pos = (rng.randint(0, width), height + 20)
        elif side == "left":
            pos = (-20, rng.randint(0, height))
        else:
            pos = (width + 20, rng.randint(0, height))
        return cls(pos, **kwargs)

    @classmethod
    def spawn(cls, width, height, rng, avoid=None):
        """Where this type appears. Default: at the edge. A type may override it."""
        return cls.spawn_at_edge(width, height, rng)

    @classmethod
    def spawn_inside(cls, width, height, rng, avoid=None, margin=60, min_distance=150):
        """Appear inside the game area, away from the player (`avoid`)."""
        for _ in range(20):
            pos = pygame.Vector2(rng.randint(margin, width - margin), rng.randint(margin, height - margin))
            if avoid is None or pos.distance_to(avoid) > min_distance:
                break
        return cls(pos)

    def scale_with_score(self, score):
        """Harder with the score: same rule as TP N1 (+score/20 for a speed of 90)."""
        self.speed *= 1 + score / (20 * cfg.MONSTER_SPEED)

    # ------------------------------------------------------------- behaviour
    def update(self, dt):
        """Common timers. Subclasses add their abilities. Returns the shots fired."""
        self.t += dt
        self._hit_cooldown = max(0.0, self._hit_cooldown - dt)
        self._flash = max(0.0, self._flash - dt)
        return []

    def attack_player(self, player):
        if self.collides_with(player) and self._hit_cooldown == 0:
            player.take_damage(self.attack)
            self._hit_cooldown = cfg.MONSTER_HIT_DELAY

    def take_hit(self, weapon, base_damage):
        """Damage from a weapon: the strategy decides, a shield may reduce it. Returns it."""
        dealt = self.damage_strategy.compute(weapon, base_damage)
        if isinstance(self, Shielded):           # only shielded monsters block
            dealt = self.block(dealt)
        self.take_damage(dealt)
        self._flash = 0.12
        return dealt

    def take_damage(self, amount):
        self.health.take(amount)

    @property
    def is_dead(self):
        return not self.health.alive

    @property
    def is_flashing(self):
        """True for a very short time after a hit (the view shows it as a white flash)."""
        return self._flash > 0
