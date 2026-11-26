"""BUILDER pattern: a complex level is built progressively, step by step.

  Product            Level                 the finished level (a World the game board can play)
  Abstract builder   LevelBuilder          the steps: background, monsters, weapons, rewards
  Concrete builder   ExtremeLevelBuilder   knows HOW to build the Extreme level
  Director           LevelDirector         knows the ORDER of the steps, not how each one is done

Positions are given as fractions of the arena (0.5, 0.1 = middle, near the top), so a level
does not depend on the size of the window."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from model.monster_factory import (NormalFactory, FastFactory, FlyingFactory, StrongFactory,
                                   ImmobileFactory, ZombieFactory, DragonFactory, RobotFactory)
from model.reward import SoulRuby, VitalFlask
from model.weapons import ObsidianShard, HellfireCannon, SoulFlame
from model.worlds import World


@dataclass
class LevelParts:
    """What the builder collects, step after step."""
    key: str = ""                                            # background (the look folder) and name
    title: str = ""
    catalog: list = field(default_factory=list)              # monsters of the waves
    monster_marks: list = field(default_factory=list)        # monsters placed at the start: (factory, x, y)
    weapons: list = field(default_factory=list)              # weapon classes
    reward_types: list = field(default_factory=list)         # rewards dropped by the dead monsters
    reward_marks: list = field(default_factory=list)         # rewards placed at the start: (class, x, y)
    spawn_scale: float = 1.0


class Level(World):
    """The product. It can be played like any other world."""

    def __init__(self, rng, parts):
        self.key, self.title = parts.key, parts.title
        self.spawn_scale = parts.spawn_scale
        self._parts = parts
        super().__init__(rng, catalog=list(parts.catalog))

    def monster_family(self):
        return list(self._parts.catalog)

    def create_monster(self, arena, player, monsters, progress, factory=None):
        return self._spawn(arena, player, monsters, progress, factory)

    def create_weapons(self):
        return [weapon() for weapon in self._parts.weapons]

    def create_reward(self, pos):
        return self.rng.choice(self._parts.reward_types)(pos)

    def opening_monsters(self, arena, player):
        return [factory.place((x * arena[0], y * arena[1]), target=player, score=player.score)
                for factory, x, y in self._parts.monster_marks]

    def opening_rewards(self, arena):
        return [reward((x * arena[0], y * arena[1])) for reward, x, y in self._parts.reward_marks]


class LevelBuilder(ABC):
    """The abstract builder."""

    def __init__(self, rng):
        self.rng = rng
        self.reset()

    def reset(self):
        self._parts = LevelParts()

    # ---- the steps: each concrete builder defines them
    @abstractmethod
    def build_background(self):
        """Step 1: the background (and the name) of the level."""

    @abstractmethod
    def build_monsters(self):
        """Step 2: the monsters of the waves and the monsters placed at the start."""

    @abstractmethod
    def build_weapons(self):
        """Step 3: the weapons of the player."""

    @abstractmethod
    def build_rewards(self):
        """Step 4: the rewards, dropped or placed on the map."""

    # ---- helpers that record a part (used by the steps)
    def set_background(self, key, title):
        self._parts.key, self._parts.title = key, title

    def add_monster_type(self, factory, weight, from_progress):
        self._parts.catalog.append((factory, weight, from_progress))

    def place_monster(self, factory, x, y):
        self._parts.monster_marks.append((factory, x, y))

    def set_pace(self, spawn_scale):
        self._parts.spawn_scale = spawn_scale

    def add_weapon(self, weapon_class):
        self._parts.weapons.append(weapon_class)

    def add_reward_type(self, reward_class):
        self._parts.reward_types.append(reward_class)

    def place_reward(self, reward_class, x, y):
        self._parts.reward_marks.append((reward_class, x, y))

    def get_level(self):
        """Hand over the finished product, if every part is there, and get ready for the next one."""
        p = self._parts
        missing = [name for name, ok in (("background", p.key), ("monsters", p.catalog),
                                         ("weapons", p.weapons), ("rewards", p.reward_types)) if not ok]
        if missing:
            raise ValueError("incomplete level, missing: " + ", ".join(missing))
        level = Level(self.rng, p)
        self.reset()
        return level


class LevelDirector:
    """Runs the steps in the right order with any builder."""

    def __init__(self, builder):
        self.builder = builder

    def construct(self):
        self.builder.reset()
        self.builder.build_background()
        self.builder.build_monsters()
        self.builder.build_weapons()
        self.builder.build_rewards()
        return self.builder.get_level()


class ExtremeLevelBuilder(LevelBuilder):
    """The Extreme level: a lava world, a crowd waiting at its places, fast waves."""

    def build_background(self):
        self.set_background("extreme", "Extreme Inferno")

    def build_monsters(self):
        # the waves that keep coming: everything, and early
        for factory, weight, from_progress in [(NormalFactory(), 2, 0), (FastFactory(), 3, 0),
                                               (ZombieFactory(), 3, 0), (FlyingFactory(), 2, 10),
                                               (ImmobileFactory(), 1, 20), (StrongFactory(), 2, 20),
                                               (RobotFactory(), 2, 30), (DragonFactory(), 2, 40)]:
            self.add_monster_type(factory, weight, from_progress)
        # the monsters waiting at their places when the level starts
        self.place_monster(ImmobileFactory(), 0.10, 0.14)      # two turrets in the top corners
        self.place_monster(ImmobileFactory(), 0.90, 0.14)
        self.place_monster(StrongFactory(), 0.50, 0.10)        # a guardian at the top
        self.place_monster(ZombieFactory(), 0.12, 0.55)        # zombies on both sides
        self.place_monster(ZombieFactory(), 0.88, 0.55)
        self.place_monster(RobotFactory(), 0.15, 0.88)         # robots in the bottom corners
        self.place_monster(RobotFactory(), 0.85, 0.88)
        self.place_monster(DragonFactory(), 0.75, 0.20)        # and a dragon
        self.set_pace(0.6)                                     # the waves come 40 % faster

    def build_weapons(self):
        for weapon in (ObsidianShard, HellfireCannon, SoulFlame):
            self.add_weapon(weapon)

    def build_rewards(self):
        self.add_reward_type(SoulRuby)
        self.add_reward_type(VitalFlask)
        for x, y in ((0.25, 0.30), (0.75, 0.30), (0.50, 0.78)):        # health flasks around the middle
            self.place_reward(VitalFlask, x, y)
        for x, y in ((0.15, 0.82), (0.85, 0.82)):                      # rubies in the bottom corners
            self.place_reward(SoulRuby, x, y)
