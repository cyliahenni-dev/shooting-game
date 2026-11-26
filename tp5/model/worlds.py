"""ABSTRACT FACTORY pattern: each world creates a whole FAMILY of compatible objects.

  Abstract factory   World                              create_monster(), create_weapons(), create_reward()
  Concrete factories ForestWorld, DesertWorld, SpaceWorld   each one creates the objects of its own world
  Abstract products  Monster, Weapon, Reward
  Concrete products  Zombie / Dragon..., AcornSling / Blaster..., GoldCoin / RepairKit...

The game board only knows World, Monster, Weapon and Reward. It never names a concrete one:
a new world (a new level) is a new subclass of World and nothing else changes (OCP).

Monsters themselves are made with the Factory Method (monster_factory.py): a world chooses
among ITS monster factories, so the two patterns work together."""
from abc import ABC, abstractmethod
from model.monster_factory import (NormalFactory, FastFactory, FlyingFactory, StrongFactory,
                                   ImmobileFactory, ZombieFactory, DragonFactory, RobotFactory)
from model.reward import (GoldCoin, HealingPotion, AncientRelic, WaterFlask, EnergyCrystal, RepairKit)
from model.spawner import Spawner
from model.weapons import (AcornSling, FireStaff, NatureWand, DesertSling, FireBomb, SunBeam,
                           Blaster, PlasmaCannon, LaserBeam)

SUMMONABLE = ("zombie", "dragon", "robot")       # the monsters that can be called on demand


class World(ABC):
    """The abstract factory."""
    key = "world"          # the name of its look: the view shows the theme folder with this name
    title = "World"

    def __init__(self, rng, catalog=None):
        self.rng = rng
        self.spawner = Spawner(rng, catalog if catalog is not None else self.monster_family())

    # ---- what a concrete world must provide
    @abstractmethod
    def monster_family(self):
        """The monsters of this world: a catalog of (monster factory, weight, appears from progress)."""

    @abstractmethod
    def create_monster(self, arena, player, monsters, progress, factory=None):
        """Create a monster of this world (`factory` = a type asked on demand)."""

    @abstractmethod
    def create_weapons(self):
        """Create the weapons of this world: a list of Weapon."""

    @abstractmethod
    def create_reward(self, pos):
        """Create a reward of this world at `pos`."""

    # ---- optional: what the level places by hand when it starts (nothing for the random worlds)
    spawn_scale = 1.0                  # smaller = the waves come faster

    def opening_monsters(self, arena, player):
        return []

    def opening_rewards(self, arena):
        return []

    # ---- shared helpers
    def _spawn(self, arena, player, monsters, progress, factory):
        factory = factory or self.spawner.choose_factory(progress, monsters)
        return factory.spawn(arena[0], arena[1], self.rng, avoid=player.pos,
                             target=player, score=player.score)

    def monster_names(self):
        return [factory.name for factory, _, _ in self.spawner.catalog]

    def monster_factory(self, name):
        return self.spawner.factory(name)


class ForestWorld(World):
    """Fantasy: zombies and dragons, bows and staffs, coins and potions."""
    key = "forest"
    title = "Enchanted Forest"

    def monster_family(self):
        return [(NormalFactory(), 4, 0), (FastFactory(), 2, 0), (ZombieFactory(), 3, 20),
                (FlyingFactory(), 2, 30), (ImmobileFactory(), 1, 50), (StrongFactory(), 1, 80),
                (DragonFactory(), 1, 120)]

    def create_monster(self, arena, player, monsters, progress, factory=None):
        return self._spawn(arena, player, monsters, progress, factory)

    def create_weapons(self):
        return [AcornSling(), FireStaff(), NatureWand()]

    def create_reward(self, pos):
        return self.rng.choice([GoldCoin, HealingPotion])(pos)


class DesertWorld(World):
    """Ruins in the sand: skeletons, mummies and cacti, slow heavy weapons, relics and water."""
    key = "desert"
    title = "Desert Ruins"

    def monster_family(self):
        return [(NormalFactory(), 3, 0), (FastFactory(), 3, 0), (ZombieFactory(), 3, 20),
                (ImmobileFactory(), 2, 30), (FlyingFactory(), 2, 40), (StrongFactory(), 2, 70)]

    def create_monster(self, arena, player, monsters, progress, factory=None):
        return self._spawn(arena, player, monsters, progress, factory)

    def create_weapons(self):
        return [DesertSling(), FireBomb(), SunBeam()]

    def create_reward(self, pos):
        return self.rng.choice([AncientRelic, WaterFlask])(pos)


class SpaceWorld(World):
    """Deep space: robots and aliens, fast energy weapons, crystals and repair kits."""
    key = "space"
    title = "Deep Space"

    def monster_family(self):
        return [(NormalFactory(), 3, 0), (FastFactory(), 3, 0), (FlyingFactory(), 2, 30),
                (ImmobileFactory(), 2, 40), (RobotFactory(), 3, 50), (StrongFactory(), 1, 90)]

    def create_monster(self, arena, player, monsters, progress, factory=None):
        return self._spawn(arena, player, monsters, progress, factory)

    def create_weapons(self):
        return [Blaster(), PlasmaCannon(), LaserBeam()]

    def create_reward(self, pos):
        return self.rng.choice([EnergyCrystal, RepairKit])(pos)
