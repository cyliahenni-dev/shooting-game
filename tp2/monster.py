import pygame
from game_object import GameObject, direction
import settings as cfg


class Monster(GameObject):
    def __init__(self, pos, speed=cfg.MONSTER_SPEED, health=cfg.MONSTER_HEALTH,
                 attack=cfg.MONSTER_ATTACK):
        super().__init__(pos, cfg.MONSTER_RADIUS)
        self.speed = speed
        self.health = health
        self.max_health = health
        self.attack = attack
        self._hit_cooldown = 0.0
        self.target = None                   # the Player it chases

    @classmethod
    def spawn_at_edge(cls, width, height, rng, **kwargs):
        """Alternative constructor: a monster entering from a random side."""
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

    @property
    def is_dead(self):
        return self.health <= 0

    def take_damage(self, amount):
        self.health -= amount

    def attack_player(self, player):
        """Hurt the player if the monster touches him and is not recovering."""
        if self._hit_cooldown == 0 and self.collides_with(player):
            player.take_damage(self.attack)
            self._hit_cooldown = cfg.MONSTER_HIT_DELAY

    def update(self, dt):
        self._hit_cooldown = max(0.0, self._hit_cooldown - dt)
        if self.target is not None:          # pursuit
            self.pos += direction(self.pos, self.target.pos) * self.speed * dt

    def draw(self, screen):
        pygame.draw.circle(screen, (90, 220, 90), self.pos, self.radius)
        w = 36 * max(self.health, 0) / self.max_health
        pygame.draw.rect(screen, (200, 40, 40), (self.pos.x - 18, self.pos.y - 30, 36, 5))
        pygame.draw.rect(screen, (40, 200, 40), (self.pos.x - 18, self.pos.y - 30, w, 5))
