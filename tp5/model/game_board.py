"""The Game Board (MODEL): owns every object and applies the rules.

It knows nothing about the window, the images, the sounds or the keyboard."""
import random
from model.player import Player
from model.levels import default_worlds, extreme_level
from model.floating_text import FloatingText
import settings as cfg


class GameBoard:
    """A game takes place in ONE world (an abstract factory) chosen at the start: the monsters, the
    weapons and the rewards all come from it. The levels do not change the world, they only make
    the game harder. The board only knows the abstract World."""
    LEVEL_SCORE_STEP = getattr(cfg, "LEVEL_SCORE_STEP", 200)      # points needed to go up one level
    LEVEL_HARDNESS = 0.25                                         # each level: monsters 25 % tougher
    LEVEL_PACE = 0.20                                             # each level: waves 20 % faster
    BANNER_TIME = 2.5                                             # seconds of the 'LEVEL n' banner

    def __init__(self, width=cfg.WIDTH, height=cfg.HEIGHT, rng=None, worlds=None, start_world=0,
                 single_level=False):
        self.width = width
        self.height = height
        self.rng = rng or random.Random()
        self.worlds = worlds or default_worlds(self.rng)
        self.start_world = start_world
        self.single_level = single_level            # True: one level played alone, no level-ups
        self.reset()

    @classmethod
    def extreme(cls, rng=None, **kwargs):
        """A game of the Extreme level alone: it is not part of the campaign."""
        rng = rng or random.Random()
        return cls(rng=rng, worlds=[extreme_level(rng)], single_level=True, **kwargs)

    def reset(self):
        self.level = 1
        self.world = self.worlds[self.start_world % len(self.worlds)]
        self.banner_time = self.BANNER_TIME
        self.player = Player((self.width / 2, self.height / 2), self.world.create_weapons())
        self.monsters = []
        self.bullets = []
        self.enemy_shots = []                    # fired by Shooter monsters
        self.floaters = []                       # floating damage numbers
        self.rewards = []
        self.spawn_timer = 0.0
        self.game_over = False
        self._open_level()
        self.spawn_monster()

    # ----------------------------------------------------------------- levels
    @property
    def progress(self):
        """Points won so far: the monsters of the world appear as it grows (it never starts over)."""
        return self.player.score

    @property
    def difficulty(self):
        """1.0 at level 1, then harder at every level."""
        return 1 + self.LEVEL_HARDNESS * (self.level - 1)

    def _check_level_up(self):
        if self.single_level:
            return
        level = self.player.score // self.LEVEL_SCORE_STEP + 1
        if level > self.level:
            self.level = level                   # the SAME world goes on: only the difficulty rises
            self.monsters, self.bullets, self.enemy_shots, self.rewards = [], [], [], []
            self.spawn_timer = 0.0
            self.banner_time = self.BANNER_TIME
            self._open_level()
            self.spawn_monster()

    def _open_level(self):
        """What the world places by hand at the start of a level (the built levels do; the others do not)."""
        arena = (self.width, self.height)
        self.monsters += self.world.opening_monsters(arena, self.player)
        self.rewards += self.world.opening_rewards(arena)

    # ---------------------------------------------------------------- actions
    def spawn_monster(self, factory=None):
        """Ask the world for a monster. `factory` = a type asked on demand."""
        monster = self.world.create_monster((self.width, self.height), self.player,
                                            self.monsters, self.progress, factory)
        monster.health.max_hp = monster.health.hp = round(monster.health.max_hp * self.difficulty)
        self.monsters.append(monster)
        return monster

    def spawn_on_demand(self, name):
        """Create a monster of the named type right now, if this world has it."""
        factory = self.world.monster_factory(name)
        return self.spawn_monster(factory) if factory else None

    def fire(self):
        bullet = self.player.shoot()
        if bullet is not None:
            self.bullets.append(bullet)

    # ----------------------------------------------------------------- update
    def update(self, dt):
        if self.game_over:
            return
        self.banner_time = max(0.0, self.banner_time - dt)
        self.player.update(dt)
        self._spawn_over_time(dt)
        for bullet in self.bullets:
            bullet.update(dt)
        self.bullets = [b for b in self.bullets if not b.is_outside(self.width, self.height)]
        for monster in self.monsters:
            self.enemy_shots += monster.update(dt)      # LSP: same call for every type
        for shot in self.enemy_shots:
            shot.update(dt)
        self.enemy_shots = [s for s in self.enemy_shots if not s.is_outside(self.width, self.height)]
        self._bullets_hit_monsters()
        self._remove_dead_monsters()
        for monster in self.monsters:
            monster.attack_player(self.player)
        self._enemy_shots_hit_player()
        self._collect_rewards()
        for text in self.floaters:
            text.update(dt)
        self.floaters = [t for t in self.floaters if not t.expired]
        self._check_level_up()
        if not self.player.is_alive:
            self.game_over = True

    def _spawn_over_time(self, dt):
        self.spawn_timer += dt
        interval = (max(1.0, 4.0 - self.player.score / 400) * self.world.spawn_scale
                    / (1 + self.LEVEL_PACE * (self.level - 1)))
        if self.spawn_timer >= interval:
            self.spawn_timer = 0
            self.spawn_monster()

    def _bullets_hit_monsters(self):
        for bullet in self.bullets[:]:
            for monster in self.monsters:
                if bullet.collides_with(monster):
                    dealt = monster.take_hit(bullet.weapon, bullet.damage)
                    self._show_damage(monster, bullet.damage, dealt)
                    self.bullets.remove(bullet)
                    break

    def _remove_dead_monsters(self):
        for monster in self.monsters[:]:
            if monster.is_dead:
                self.monsters.remove(monster)
                self.player.score += monster.score_value
                if self.rng.random() < cfg.REWARD_DROP_CHANCE:
                    self.rewards.append(self.world.create_reward(monster.pos))

    def _show_damage(self, monster, base, dealt):
        """Record HOW the hit went; the view decides the colors."""
        if dealt < base:
            effect = FloatingText.RESISTED
        elif dealt > base:
            effect = FloatingText.WEAK
        else:
            effect = FloatingText.NORMAL
        pos = (monster.pos.x, monster.pos.y - monster.radius - 16)
        self.floaters.append(FloatingText(pos, "-%g" % dealt, effect))

    def _enemy_shots_hit_player(self):
        for shot in self.enemy_shots[:]:
            if shot.collides_with(self.player):
                self.player.take_damage(shot.damage)
                self.enemy_shots.remove(shot)

    def _collect_rewards(self):
        for reward in self.rewards[:]:
            if reward.collides_with(self.player):
                reward.apply(self.player)
                self.rewards.remove(reward)
