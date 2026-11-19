"""Generates placeholder images and sounds for the game.

Run once from the project folder:  python make_placeholders.py
Creates assets/themes/<theme>/{player,monsters,bullets,backgrounds,sounds}/
Replace any generated file with your own art later (same name, same folder).
"""
import math
import os
import random
import struct
import wave

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")   # no window needed
import pygame

ROOT = os.path.join("assets", "themes")
W, H = 800, 600

THEMES = {
    "default": dict(player=(80, 200, 255), normal=(90, 200, 90), flying=(90, 150, 255),
                    strong=(220, 70, 70), immobile=(170, 90, 220),
                    bg_top=(15, 15, 35), bg_bottom=(35, 35, 80)),
    "space":   dict(player=(255, 200, 80), normal=(255, 120, 200), flying=(120, 255, 220),
                    strong=(255, 150, 60), immobile=(200, 200, 255),
                    bg_top=(5, 0, 20), bg_bottom=(50, 0, 70)),
}
BULLETS = {"bullet": (255, 230, 80), "fire": (255, 140, 50),
           "laser": (80, 230, 255), "enemy_shot": (255, 60, 60)}


def darker(c, k=0.6):
    return tuple(int(v * k) for v in c)


def save(surface, *parts):
    path = os.path.join(*parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pygame.image.save(surface, path)


def body(color, size=64):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    c = size // 2
    pygame.draw.circle(s, color, (c, c), c - 4)
    pygame.draw.circle(s, darker(color), (c, c), c - 4, 3)
    return s


def eyes(s):
    c = s.get_width() // 2
    for dx in (-10, 10):
        pygame.draw.circle(s, (255, 255, 255), (c + dx, c - 4), 7)
        pygame.draw.circle(s, (0, 0, 0), (c + dx, c - 3), 3)


def make_player(theme, col):
    s = body(col["player"])
    eyes(s)
    pygame.draw.rect(s, darker(col["player"], 0.4), (30, 44, 4, 16))   # little gun
    save(s, ROOT, theme, "player", "player.png")


def make_monsters(theme, col):
    # normal
    s = body(col["normal"]); eyes(s)
    save(s, ROOT, theme, "monsters", "normal.png")
    # flying: wings
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    wing = darker(col["flying"], 0.8)
    pygame.draw.polygon(s, wing, [(2, 14), (22, 28), (6, 40)])
    pygame.draw.polygon(s, wing, [(62, 14), (42, 28), (58, 40)])
    b = body(col["flying"]); eyes(b)
    s.blit(b, (0, 0))
    save(s, ROOT, theme, "monsters", "flying.png")
    # strong: thick armor ring
    s = body(col["strong"]); eyes(s)
    pygame.draw.circle(s, (230, 230, 230), (32, 32), 28, 4)
    save(s, ROOT, theme, "monsters", "strong.png")
    # immobile: spikes
    s = pygame.Surface((64, 64), pygame.SRCALPHA)
    for i in range(12):
        a = i * math.pi / 6
        pygame.draw.line(s, darker(col["immobile"]), (32, 32),
                         (32 + 30 * math.cos(a), 32 + 30 * math.sin(a)), 5)
    b = body(col["immobile"]); eyes(b)
    s.blit(b, (0, 0))
    save(s, ROOT, theme, "monsters", "immobile.png")


def make_bullets(theme):
    for name, color in BULLETS.items():
        s = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (8, 8), 7)
        pygame.draw.circle(s, (255, 255, 255), (8, 8), 3)
        save(s, ROOT, theme, "bullets", name + ".png")


def make_background(theme, col):
    s = pygame.Surface((W, H))
    top, bot = col["bg_top"], col["bg_bottom"]
    for y in range(H):
        t = y / H
        pygame.draw.line(s, tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3)),
                         (0, y), (W, y))
    rng = random.Random(1)
    for _ in range(80):
        pygame.draw.circle(s, (200, 200, 230), (rng.randrange(W), rng.randrange(H)),
                           rng.choice((1, 1, 2)))
    save(s, ROOT, theme, "backgrounds", "background.png")


def tone(theme, name, freqs, duration=0.12, volume=0.4):
    """Write a short 16-bit mono WAV that steps through the given frequencies."""
    path = os.path.join(ROOT, theme, "sounds", name + ".wav")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rate = 22050
    with wave.open(path, "wb") as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate)
        for freq in freqs:
            n = int(rate * duration)
            for i in range(n):
                fade = 1 - i / n
                v = volume * fade * math.sin(2 * math.pi * freq * i / rate)
                f.writeframes(struct.pack("<h", int(v * 32767)))


def make_sounds(theme):
    shift = 1.0 if theme == "default" else 1.5
    tone(theme, "shoot", [880 * shift], 0.08)
    tone(theme, "hit", [220 * shift], 0.10)
    tone(theme, "game_over", [400 * shift, 300 * shift, 200 * shift, 120 * shift], 0.25)


if __name__ == "__main__":
    pygame.init()
    for theme, col in THEMES.items():
        make_player(theme, col)
        make_monsters(theme, col)
        make_bullets(theme)
        make_background(theme, col)
        make_sounds(theme)
        print("created theme:", theme)
    print("done ->", os.path.abspath(ROOT))
