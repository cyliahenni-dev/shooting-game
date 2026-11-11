"""The Game Board: owns every object and applies the rules (no pygame window)."""
import random
from player import Player
from reward import Reward
from spawner import Spawner                  # NEW (SRP, OCP)
from health import HealthBar                 # NEW (SRP)
from floating_text import FloatingText       # NEW
import settings as cfg


class GameBoard:
    def __init__(self, width=cfg.WIDTH, height=cfg.HEIGHT, rng=None):
        self.width = width
        self.height = height
        self.rng = rng or random.Random()
        self.spawner = Spawner(self.rng)         # NEW: decides which monster appears
        self.health_bar = HealthBar()            # NEW: draws the monsters' health
        self.reset()

    def reset(self):
        self.player = Player((self.width / 2, self.height / 2))
        self.monsters = []
        self.bullets = []
        self.enemy_shots = []                    # NEW: fired by Shooter monsters
        self.floaters = []                       # NEW: floating damage numbers
        self.rewards = []
        self.spawn_timer = 0.0
        self.game_over = False
        self.spawn_monster()

    # ---------------------------------------------------------------- actions
    def spawn_monster(self):
        kind = self.spawner.choose_kind(self.player.score, self.monsters)      # NEW
        monster = kind.spawn(self.width, self.height, self.rng, avoid=self.player.pos)
        monster.scale_with_score(self.player.score)                            # harder with the score
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
            self.enemy_shots += monster.update(dt)      # NEW (LSP): same call for every type
        for shot in self.enemy_shots:                   # NEW
            shot.update(dt)
        self.enemy_shots = [s for s in self.enemy_shots if not s.is_outside(self.width, self.height)]
        self._bullets_hit_monsters()
        self._remove_dead_monsters()
        for monster in self.monsters:
            monster.attack_player(self.player)
        self._enemy_shots_hit_player()                  # NEW
        self._collect_rewards()
        for text in self.floaters:                      # NEW
            text.update(dt)
        self.floaters = [t for t in self.floaters if not t.expired]
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
                    dealt = monster.take_hit(bullet.weapon, bullet.damage)     # NEW: was take_damage(bullet.damage)
                    self._show_damage(monster, bullet.damage, dealt)
                    self.bullets.remove(bullet)
                    break

    def _remove_dead_monsters(self):
        for monster in self.monsters[:]:
            if monster.is_dead:
                self.monsters.remove(monster)
                self.player.score += monster.score_value     # NEW: was cfg.KILL_POINTS
                if self.rng.random() < cfg.REWARD_DROP_CHANCE:
                    kind = self.rng.choice([Reward.POINTS, Reward.HEALTH])
                    self.rewards.append(Reward(monster.pos, kind))

    def _show_damage(self, monster, base, dealt):          # NEW
        color = (255, 90, 90) if dealt < base else (120, 255, 140) if dealt > base else (255, 255, 255)
        pos = (monster.pos.x, monster.pos.y - monster.radius - 16)
        self.floaters.append(FloatingText(pos, "-%g" % dealt, color))

    def _enemy_shots_hit_player(self):                      # NEW
        for shot in self.enemy_shots[:]:
            if shot.collides_with(self.player):
                self.player.take_damage(shot.damage)
                self.enemy_shots.remove(shot)

    def _collect_rewards(self):
        for reward in self.rewards[:]:
            if reward.collides_with(self.player):
                reward.apply(self.player)
                self.rewards.remove(reward)

    # ------------------------------------------------------------------- draw
    def draw(self, screen):
        # polymorphism: every object knows how to draw itself
        for obj in [*self.rewards, *self.bullets, *self.enemy_shots, *self.monsters, self.player]:
            obj.draw(screen)
        for monster in self.monsters:                                       # NEW (SRP)
            self.health_bar.render(screen, monster.health,
                                   monster.pos.x - 18, monster.pos.y - monster.radius - 12)
        for text in self.floaters:                                          # NEW
            text.draw(screen)
