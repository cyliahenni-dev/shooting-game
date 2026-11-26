"""The levels of the game.

The CAMPAIGN is Forest, Desert and Space, one after the other (worlds written by hand,
Abstract Factory, worlds.py). The Extreme level is NOT part of it: it is a complex level
assembled by a Builder (level_builder.py) and it is played alone.
Both kinds are a World: the game board plays them all the same way."""
from model.level_builder import LevelDirector, ExtremeLevelBuilder
from model.worlds import ForestWorld, DesertWorld, SpaceWorld


def default_worlds(rng):
    """The levels of the campaign, in order."""
    return [ForestWorld(rng), DesertWorld(rng), SpaceWorld(rng)]


def extreme_level(rng):
    """The Extreme level, built step by step by its builder."""
    return LevelDirector(ExtremeLevelBuilder(rng)).construct()
