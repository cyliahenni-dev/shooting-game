"""The Game Board: owns every object and applies the rules (no pygame window)."""
import random
from player import Player
from monster import Monster
from reward import Reward
import settings as cfg


class GameBoard:
    def __init__(self, width=cfg.WIDTH, height=cfg.HEIGHT, rng=None):
        self.width = width
        self.height = height
        self.rng = rng or random.Random()
        self.reset()

    def reset(self):
        self.player = Player((self.width / 2, self.height / 2))
        self.monsters = []
        self.bullets = []
        self.rewards = []
        self.spawn_timer = 0.0
        self.game_over = False
        self.spawn_monster()

    # ---------------------------------------------------------------- actions
    def spawn_monster(self):
        monster = Monster.spawn_at_edge(
            self.width, self.height, self.rng,
            speed=cfg.MONSTER_SPEED + self.player.score / 20)   # harder with the score
        monster.target = self.player
        self.monsters.append(monster)

    def fire(self):
        bullet = self.player.shoot()
        if bullet is not None:
            self.bullets.append(bullet)

    # ----------------------------------------------------------------- update
    def update(self, dt):
        if self.game_over:
            return
        self.player.update(dt)
        self._spawn_over_time(dt)
        for bullet in self.bullets:
            bullet.update(dt)
        self.bullets = [b for b in self.bullets if not b.is_outside(self.width, self.height)]
        for monster in self.monsters:
            monster.update(dt)
        self._bullets_hit_monsters()
        self._remove_dead_monsters()
        for monster in self.monsters:
            monster.attack_player(self.player)
        self._collect_rewards()
        if not self.player.is_alive:
            self.game_over = True

    def _spawn_over_time(self, dt):
        self.spawn_timer += dt
        interval = max(1.0, 4.0 - self.player.score / 400)
        if self.spawn_timer >= interval:
            self.spawn_timer = 0
            self.spawn_monster()

    def _bullets_hit_monsters(self):
        for bullet in self.bullets[:]:
            for monster in self.monsters:
                if bullet.collides_with(monster):
                    monster.take_damage(bullet.damage)
                    self.bullets.remove(bullet)
                    break

    def _remove_dead_monsters(self):
        for monster in self.monsters[:]:
            if monster.is_dead:
                self.monsters.remove(monster)
                self.player.score += cfg.KILL_POINTS
                if self.rng.random() < cfg.REWARD_DROP_CHANCE:
                    kind = self.rng.choice([Reward.POINTS, Reward.HEALTH])
                    self.rewards.append(Reward(monster.pos, kind))

    def _collect_rewards(self):
        for reward in self.rewards[:]:
            if reward.collides_with(self.player):
                reward.apply(self.player)
                self.rewards.remove(reward)

    # ------------------------------------------------------------------- draw
    def draw(self, screen):
        # polymorphism: every object knows how to draw itself
        for obj in [*self.rewards, *self.bullets, *self.monsters, self.player]:
            obj.draw(screen)
