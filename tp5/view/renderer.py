"""VIEW: draws the model objects on a pygame surface.

It only READS the model (position, radius, kind, weapon...) and never changes it.
For each object it tries the themed image first and falls back to a drawn shape."""
import math
import pygame
from model.game_object import direction
from model.floating_text import FloatingText
from model.reward import Reward

# --- everything about the LOOK of the objects is here, not in the model -------------
MONSTER_COLORS = {"normal": (90, 220, 90), "fast": (255, 150, 50), "flying": (165, 120, 255),
                  "strong": (200, 80, 65), "immobile": (125, 122, 150),
                  "zombie": (110, 168, 92), "dragon": (200, 60, 44), "robot": (150, 160, 184)}
SPRITE_SCALE = {"flying": 3.0, "dragon": 3.0}            # image size = radius * scale (default below)
DEFAULT_SPRITE_SCALE = 2.3
EFFECT_COLORS = {FloatingText.RESISTED: (255, 90, 90),
                 FloatingText.WEAK: (120, 255, 140),
                 FloatingText.NORMAL: (255, 255, 255)}
WEAPON_COLORS = {"bullet": (255, 230, 80), "fire": (255, 140, 50), "laser": (80, 230, 255)}
REWARD_COLORS = {Reward.POINTS: (255, 200, 0), Reward.HEALTH: (255, 80, 160)}


class HealthBar:
    """Only responsible for rendering a Health on the screen."""

    def render(self, screen, health, x, y, width=36, height=5):
        pygame.draw.rect(screen, (200, 40, 40), (x, y, width, height))
        pygame.draw.rect(screen, (40, 200, 40), (x, y, width * health.ratio, height))


class Renderer:
    def __init__(self, assets):
        self.assets = assets
        self.health_bar = HealthBar()
        self._font = None
        self._shapes = {"normal": self._shape_normal, "fast": self._shape_fast,
                        "flying": self._shape_flying, "strong": self._shape_strong,
                        "immobile": self._shape_immobile, "zombie": self._shape_zombie,
                        "dragon": self._shape_dragon, "robot": self._shape_robot}

    # ------------------------------------------------------------------ board
    def draw_board(self, screen, board):
        for reward in board.rewards:
            self.draw_reward(screen, reward)
        for bullet in board.bullets:
            self.draw_bullet(screen, bullet)
        for shot in board.enemy_shots:
            self.draw_enemy_shot(screen, shot)
        for monster in board.monsters:
            self.draw_monster(screen, monster)
        self.draw_player(screen, board.player)
        for monster in board.monsters:
            self.health_bar.render(screen, monster.health,
                                   monster.pos.x - 18, monster.pos.y - monster.radius - 12)
        for text in board.floaters:
            self.draw_floating_text(screen, text)

    # ----------------------------------------------------------------- player
    def draw_player(self, screen, p):
        d = direction(p.pos, p.aim_point)
        if self.assets.blit(screen, "player", "player", p.pos, p.radius * 2.3, -d.as_polar()[1]):
            return
        pygame.draw.circle(screen, (60, 160, 255), p.pos, p.radius)
        tip = p.pos + d * (p.radius + 8)
        pygame.draw.line(screen, WEAPON_COLORS.get(p.weapon.damage_type, (255, 255, 255)), p.pos, tip, 4)

    # --------------------------------------------------------------- monsters
    def draw_monster(self, screen, m):
        """Body only: the health bar is drawn separately (SRP)."""
        if not m.is_flashing:
            scale = SPRITE_SCALE.get(m.kind, DEFAULT_SPRITE_SCALE)
            if self.assets.blit(screen, "monsters", m.kind, m.pos, m.radius * scale):
                return
        color = (255, 255, 255) if m.is_flashing else MONSTER_COLORS.get(m.kind, MONSTER_COLORS["normal"])
        self._shapes.get(m.kind, self._shape_normal)(screen, m, color)

    @staticmethod
    def _eyes(screen, pos, dx=6, size=3):
        for s in (-dx, dx):
            pygame.draw.circle(screen, (255, 255, 255), (pos.x + s, pos.y - 3), size + 1)
            pygame.draw.circle(screen, (20, 20, 20), (pos.x + s, pos.y - 3), size - 1)

    def _shape_normal(self, screen, m, color):
        pygame.draw.circle(screen, color, m.pos, m.radius)
        self._eyes(screen, m.pos, m.radius // 3)

    def _shape_fast(self, screen, m, color):
        x, y, r = m.pos.x, m.pos.y, m.radius + 3
        pygame.draw.polygon(screen, color, [(x, y - r), (x + r, y), (x, y + r), (x - r, y)])
        self._eyes(screen, m.pos, 4, 2)

    def _shape_flying(self, screen, m, color):
        x, y = m.pos.x, m.pos.y
        flap = math.sin(m.t * 14) * 10
        pygame.draw.polygon(screen, color, [(x, y), (x - 32, y - 8 - flap), (x - 14, y + 8)])
        pygame.draw.polygon(screen, color, [(x, y), (x + 32, y - 8 - flap), (x + 14, y + 8)])
        pygame.draw.circle(screen, color, m.pos, m.radius)
        self._eyes(screen, m.pos, 5)

    def _shape_strong(self, screen, m, color):
        r = pygame.Rect(0, 0, m.radius * 2, m.radius * 2)
        r.center = (m.pos.x, m.pos.y)
        pygame.draw.rect(screen, color, r, border_radius=8)
        pygame.draw.arc(screen, (190, 205, 240), r.inflate(14, 14), math.pi / 2, 3 * math.pi / 2, 5)
        self._eyes(screen, m.pos, 10, 4)

    def _shape_immobile(self, screen, m, color):
        x, y, r = m.pos.x, m.pos.y, m.radius
        pts = [(x + r * math.cos(math.pi / 3 * i), y + r * math.sin(math.pi / 3 * i)) for i in range(6)]
        pygame.draw.polygon(screen, color, pts)
        pygame.draw.polygon(screen, (80, 78, 100), pts, 3)
        self._eyes(screen, m.pos, 7, 4)

    def _shape_zombie(self, screen, m, color):
        x, y = m.pos.x, m.pos.y
        pygame.draw.circle(screen, color, m.pos, m.radius)
        pygame.draw.circle(screen, (255, 255, 255), (x - 6, y - 3), 5)          # one big eye...
        pygame.draw.circle(screen, (20, 20, 20), (x - 6, y - 3), 2)
        pygame.draw.circle(screen, (255, 255, 255), (x + 6, y - 2), 3)          # ...one small eye
        pygame.draw.circle(screen, (20, 20, 20), (x + 6, y - 2), 1)
        pygame.draw.line(screen, (60, 24, 24), (x - 7, y + 8), (x + 7, y + 8), 3)       # mouth
        pygame.draw.line(screen, (60, 24, 24), (x + 6, y - 14), (x + 12, y - 6), 2)     # scar

    def _shape_dragon(self, screen, m, color):
        x, y, r = m.pos.x, m.pos.y, m.radius
        flap = math.sin(m.t * 6) * 8
        wing = tuple(max(0, c - 50) for c in color)
        pygame.draw.polygon(screen, wing, [(x, y), (x - 40, y - 12 - flap), (x - 18, y + 12)])
        pygame.draw.polygon(screen, wing, [(x, y), (x + 40, y - 12 - flap), (x + 18, y + 12)])
        pygame.draw.circle(screen, color, m.pos, r)
        for side in (-1, 1):                                                    # horns and eyes
            pygame.draw.polygon(screen, (240, 230, 200), [(x + side * 12, y - r + 6),
                                                          (x + side * 9, y - r - 8), (x + side * 3, y - r + 4)])
            pygame.draw.circle(screen, (255, 220, 60), (x + side * 7, y - 3), 4)
            pygame.draw.line(screen, (20, 10, 10), (x + side * 7, y - 6), (x + side * 7, y), 2)

    def _shape_robot(self, screen, m, color):
        x, y = m.pos.x, m.pos.y
        body = pygame.Rect(0, 0, m.radius * 2, m.radius * 2)
        body.center = (x, y)
        pygame.draw.rect(screen, color, body, border_radius=4)
        pygame.draw.rect(screen, (60, 66, 84), body, 2, border_radius=4)
        visor = pygame.Rect(0, 0, int(m.radius * 1.4), 7)
        visor.center = (x, y - 2)
        pygame.draw.rect(screen, (255, 70, 70), visor, border_radius=3)
        pygame.draw.line(screen, (60, 66, 84), (x, body.top), (x, body.top - 7), 2)      # antenna
        pygame.draw.circle(screen, (255, 70, 70), (x, body.top - 8), 3)

    # ------------------------------------------------------------ projectiles
    def draw_bullet(self, screen, b):
        if self.assets.blit(screen, "bullets", b.weapon, b.pos, b.radius * 3):
            return
        pygame.draw.circle(screen, WEAPON_COLORS.get(b.weapon, (255, 255, 255)), b.pos, b.radius)

    def draw_enemy_shot(self, screen, s):
        if self.assets.blit(screen, "bullets", "enemy_shot", s.pos, s.radius * 3):
            return
        pygame.draw.circle(screen, (255, 70, 70), s.pos, s.radius)
        pygame.draw.circle(screen, (255, 220, 160), s.pos, 3)

    # ---------------------------------------------------------- rewards, text
    def draw_reward(self, screen, r):
        if self.assets.blit(screen, "rewards", r.type, r.pos, r.radius * 3):
            return
        pygame.draw.circle(screen, REWARD_COLORS.get(r.type, (255, 255, 255)), r.pos, r.radius)

    def draw_floating_text(self, screen, t):
        if self._font is None:
            if not pygame.font.get_init():
                pygame.font.init()
            self._font = pygame.font.SysFont(None, 22)
        surf = self._font.render(t.text, True, EFFECT_COLORS.get(t.effect, (255, 255, 255)))
        screen.blit(surf, (t.pos.x - surf.get_width() / 2, t.pos.y))
