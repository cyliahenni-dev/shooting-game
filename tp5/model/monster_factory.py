"""FACTORY METHOD pattern: monsters are created by factories, never with a direct constructor call.

  Creator           MonsterFactory                   declares the factory method create_monster()
                                                     and spawn(), which uses it
  Concrete creator  ZombieFactory, DragonFactory...  each one decides WHICH monster it creates
  Product           Monster
  Concrete product  ZombieMonster, DragonMonster...

The game board and the spawner only know MonsterFactory and Monster. To add a new type of
monster: write a Monster subclass and a factory for it. Nothing else changes (OCP)."""
from abc import ABC, abstractmethod
from model.monster_types import (NormalMonster, FastMonster, FlyingMonster, StrongMonster,
                                 ImmobileMonster, ZombieMonster, DragonMonster, RobotMonster)


class MonsterFactory(ABC):
    """The creator. Subclasses only override the factory method."""
    name = "monster"                 # used to ask for a type on demand ('zombie', 'dragon'...)
    monster_class = None             # the type this factory creates (the spawner limits max_alive)

    @abstractmethod
    def create_monster(self, width, height, rng, avoid=None):
        """THE FACTORY METHOD: return a new Monster of this factory's type."""

    def spawn(self, width, height, rng, avoid=None, target=None, score=0):
        """Create a monster with the factory method, then make it ready for the game."""
        monster = self.create_monster(width, height, rng, avoid)
        monster.scale_with_score(score)          # harder with the score
        monster.target = target
        return monster


    def place(self, pos, target=None, score=0):
        """Create a monster at a chosen position (a level that places its monsters by hand)."""
        monster = self.monster_class(pos)
        monster.scale_with_score(score)
        monster.target = target
        return monster


class NormalFactory(MonsterFactory):
    name = "normal"
    monster_class = NormalMonster

    def create_monster(self, width, height, rng, avoid=None):
        return NormalMonster.spawn(width, height, rng, avoid)


class FastFactory(MonsterFactory):
    name = "fast"
    monster_class = FastMonster

    def create_monster(self, width, height, rng, avoid=None):
        return FastMonster.spawn(width, height, rng, avoid)


class FlyingFactory(MonsterFactory):
    name = "flying"
    monster_class = FlyingMonster

    def create_monster(self, width, height, rng, avoid=None):
        return FlyingMonster.spawn(width, height, rng, avoid)


class StrongFactory(MonsterFactory):
    name = "strong"
    monster_class = StrongMonster

    def create_monster(self, width, height, rng, avoid=None):
        return StrongMonster.spawn(width, height, rng, avoid)


class ImmobileFactory(MonsterFactory):
    name = "immobile"
    monster_class = ImmobileMonster

    def create_monster(self, width, height, rng, avoid=None):
        return ImmobileMonster.spawn(width, height, rng, avoid)


class ZombieFactory(MonsterFactory):
    name = "zombie"
    monster_class = ZombieMonster

    def create_monster(self, width, height, rng, avoid=None):
        return ZombieMonster.spawn(width, height, rng, avoid)


class DragonFactory(MonsterFactory):
    name = "dragon"
    monster_class = DragonMonster

    def create_monster(self, width, height, rng, avoid=None):
        return DragonMonster.spawn(width, height, rng, avoid)


class RobotFactory(MonsterFactory):
    name = "robot"
    monster_class = RobotMonster

    def create_monster(self, width, height, rng, avoid=None):
        return RobotMonster.spawn(width, height, rng, avoid)
