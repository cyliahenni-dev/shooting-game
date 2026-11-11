"""SRP: the Spawner only decides WHICH monster appears (the board decides when and where).
OCP: to add a monster type, add one line to DEFAULT_CATALOG (or pass your own catalog)."""
from monster_types import (NormalMonster, FastMonster, FlyingMonster,
                           StrongMonster, ImmobileMonster)


class Spawner:
    #                    monster class    weight   appears from score
    DEFAULT_CATALOG = [(NormalMonster,    4,       0),
                       (FastMonster,      2,       0),
                       (FlyingMonster,    2,       30),
                       (ImmobileMonster,  1,       50),
                       (StrongMonster,    1,       80)]

    def __init__(self, rng, catalog=None):
        self.rng = rng
        self.catalog = catalog if catalog is not None else self.DEFAULT_CATALOG

    def choose_kind(self, score, monsters):
        options = []
        for kind, weight, from_score in self.catalog:
            if score < from_score:
                continue
            if kind.max_alive is not None and sum(isinstance(m, kind) for m in monsters) >= kind.max_alive:
                continue
            options.append((kind, weight))
        kinds, weights = zip(*options)
        return self.rng.choices(kinds, weights)[0]
