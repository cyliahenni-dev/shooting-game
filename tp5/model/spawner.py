"""SRP: the Spawner only decides WHICH factory is used next (the board decides when and where).
OCP: to add a monster type, write its factory and add one line to DEFAULT_CATALOG."""
from model.monster_factory import (NormalFactory, FastFactory, FlyingFactory, StrongFactory,
                                   ImmobileFactory, ZombieFactory, DragonFactory, RobotFactory)


class Spawner:
    #                    factory            weight   appears from score
    DEFAULT_CATALOG = [(NormalFactory(),    4,       0),
                       (FastFactory(),      2,       0),
                       (ZombieFactory(),    3,       20),
                       (FlyingFactory(),    2,       30),
                       (ImmobileFactory(),  1,       50),
                       (RobotFactory(),     2,       60),
                       (StrongFactory(),    1,       80),
                       (DragonFactory(),    1,       120)]

    def __init__(self, rng, catalog=None):
        self.rng = rng
        self.catalog = catalog if catalog is not None else self.DEFAULT_CATALOG

    def choose_factory(self, score, monsters):
        """A random factory among the ones allowed now (score reached, limit not reached)."""
        options = []
        for factory, weight, from_score in self.catalog:
            if score < from_score:
                continue
            limit = factory.monster_class.max_alive
            if limit is not None and sum(isinstance(m, factory.monster_class) for m in monsters) >= limit:
                continue
            options.append((factory, weight))
        factories, weights = zip(*options)
        return self.rng.choices(factories, weights)[0]

    def factory(self, name):
        """The factory of a type, asked by name ('zombie', 'dragon'...), or None."""
        for factory, _, _ in self.catalog:
            if factory.name == name:
                return factory
        return None
