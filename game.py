#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TP N1 - Homework : 2D Shooting Game prototype (Pygame)
Story: a space astronaut defends his ship against an alien.

Controls : arrows / WASD = move   |   mouse = aim   |   left click or SPACE = shoot
           R = restart after game over   |   ESC = quit
"""
import math
import random
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60


# ------------------------------------------------------------------ helpers
def direction(from_pos, to_pos):
    """Unit vector pointing from one position to another."""
    v = pygame.Vector2(to_pos) - pygame.Vector2(from_pos)
    return v.normalize() if v.length() > 0 else pygame.Vector2(1, 0)


# ------------------------------------------------------------------ objects
class Player:
    def __init__(self):
        self.pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)   # position
        self.speed = 280                                    # pixels / second
        self.health = 100
        self.weapon_damage = 25                             # weapon
        self.score = 0
        self.radius = 16
        self.cooldown = 0.0                                 # delay between shots

    def move(self, keys, dt):
        d = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            d.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            d.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            d.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            d.y += 1
        if d.length() > 0:
            self.pos += d.normalize() * self.speed * dt
        # movement boundaries: stay inside the game area
        self.pos.x = max(self.radius, min(WIDTH - self.radius, self.pos.x))
        self.pos.y = max(self.radius, min(HEIGHT - self.radius, self.pos.y))

    def shoot(self, target):
        if self.cooldown > 0:
            return None
        self.cooldown = 0.25
        return Bullet(self.pos, direction(self.pos, target), self.weapon_damage)

    def update(self, dt):
        self.cooldown = max(0.0, self.cooldown - dt)

    def draw(self, screen):
        pygame.draw.circle(screen, (60, 160, 255), self.pos, self.radius)
        mouse = pygame.mouse.get_pos()
        tip = self.pos + direction(self.pos, mouse) * (self.radius + 8)
        pygame.draw.line(screen, (255, 255, 255), self.pos, tip, 4)


class Monster:
    def __init__(self, speed=90, health=50, attack=10):
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            self.pos = pygame.Vector2(random.randint(0, WIDTH), -20)
        elif side == "bottom":
            self.pos = pygame.Vector2(random.randint(0, WIDTH), HEIGHT + 20)
        elif side == "left":
            self.pos = pygame.Vector2(-20, random.randint(0, HEIGHT))
        else:
            self.pos = pygame.Vector2(WIDTH + 20, random.randint(0, HEIGHT))
        self.speed = speed
        self.health = health
        self.max_health = health
        self.attack = attack            # damage dealt to the player
        self.radius = 18
        self.hit_cooldown = 0.0

    def update(self, dt, player):
        # pursuit: always walk toward the player
        self.pos += direction(self.pos, player.pos) * self.speed * dt
        self.hit_cooldown = max(0.0, self.hit_cooldown - dt)

    def draw(self, screen):
        pygame.draw.circle(screen, (90, 220, 90), self.pos, self.radius)
        # health bar
        w = 36 * self.health / self.max_health
        pygame.draw.rect(screen, (200, 40, 40), (self.pos.x - 18, self.pos.y - 30, 36, 5))
        pygame.draw.rect(screen, (40, 200, 40), (self.pos.x - 18, self.pos.y - 30, w, 5))


class Bullet:
    def __init__(self, pos, dir_vector, damage):
        self.pos = pygame.Vector2(pos)
        self.dir = dir_vector
        self.speed = 600
        self.damage = damage
        self.radius = 4

    def update(self, dt):
        self.pos += self.dir * self.speed * dt

    def is_outside(self):
        return not (0 <= self.pos.x <= WIDTH and 0 <= self.pos.y <= HEIGHT)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 230, 80), self.pos, self.radius)


class Reward:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.type = random.choice(["points", "health"])
        self.value = 50 if self.type == "points" else 20
        self.radius = 9

    def apply(self, player):
        if self.type == "points":
            player.score += self.value
        else:
            player.health = min(100, player.health + self.value)

    def draw(self, screen):
        color = (255, 200, 0) if self.type == "points" else (255, 80, 160)
        pygame.draw.circle(screen, color, self.pos, self.radius)


# ------------------------------------------------------------------- game
def collide(a, b):
    """Circle collision: distance between centers < sum of radii."""
    return a.pos.distance_to(b.pos) < a.radius + b.radius


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Space Defender - prototype")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 64)
        self.reset()

    def reset(self):
        self.player = Player()
        self.monsters = [Monster()]
        self.bullets = []
        self.rewards = []
        self.spawn_timer = 0.0
        self.game_over = False

    # ---- 1) input handling
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and self.game_over:
                    self.reset()
        if not self.game_over:
            keys = pygame.key.get_pressed()
            self.player.move(keys, self.dt)
            if pygame.mouse.get_pressed()[0] or keys[pygame.K_SPACE]:
                bullet = self.player.shoot(pygame.mouse.get_pos())
                if bullet:
                    self.bullets.append(bullet)
        return True

    # ---- 2) update objects + collisions + state changes
    def update(self):
        if self.game_over:
            return
        dt = self.dt
        self.player.update(dt)

        # spawn: one more monster every few seconds, difficulty grows with score
        self.spawn_timer += dt
        interval = max(1.0, 4.0 - self.player.score / 400)
        if self.spawn_timer >= interval:
            self.spawn_timer = 0
            self.monsters.append(Monster(speed=90 + self.player.score / 20))

        for b in self.bullets:
            b.update(dt)
        self.bullets = [b for b in self.bullets if not b.is_outside()]

        for m in self.monsters:
            m.update(dt, self.player)

        # collision bullet <-> monster
        for b in self.bullets[:]:
            for m in self.monsters:
                if collide(b, m):
                    m.health -= b.damage
                    self.bullets.remove(b)
                    break
        # defeated monsters -> score + reward
        for m in self.monsters[:]:
            if m.health <= 0:
                self.monsters.remove(m)
                self.player.score += 10
                if random.random() < 0.6:
                    self.rewards.append(Reward(m.pos))

        # collision monster <-> player
        for m in self.monsters:
            if collide(m, self.player) and m.hit_cooldown == 0:
                self.player.health -= m.attack
                m.hit_cooldown = 1.0
        if self.player.health <= 0:
            self.player.health = 0
            self.game_over = True

        # collision player <-> reward
        for r in self.rewards[:]:
            if collide(r, self.player):
                r.apply(self.player)
                self.rewards.remove(r)

    # ---- 3) rendering
    def draw(self):
        self.screen.fill((15, 15, 35))
        for r in self.rewards:
            r.draw(self.screen)
        for b in self.bullets:
            b.draw(self.screen)
        for m in self.monsters:
            m.draw(self.screen)
        self.player.draw(self.screen)
        hud = f"Health: {self.player.health}   Score: {self.player.score}"
        self.screen.blit(self.font.render(hud, True, (255, 255, 255)), (10, 10))
        if self.game_over:
            txt = self.big_font.render("GAME OVER", True, (255, 80, 80))
            self.screen.blit(txt, txt.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 20)))
            sub = self.font.render("Press R to restart", True, (255, 255, 255))
            self.screen.blit(sub, sub.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 30)))
        pygame.display.flip()

    # ---- main game loop
    def run(self):
        running = True
        while running:
            self.dt = self.clock.tick(FPS) / 1000.0     # seconds since last frame
            running = self.handle_events()
            self.update()
            self.draw()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
