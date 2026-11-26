"""WEAPONS: one of the product families of the Abstract Factory (see worlds.py).

`damage_type` is what the monsters react to:
  'bullet'  flying monsters resist it
  'fire'    strong monsters are weak to it, dragons resist it
  'laser'   robots are weak to it
Every world has its own weapon for each of the three types, so the rules of the monsters
always stay meaningful: the weapons of a world are COMPATIBLE with its monsters."""


class Weapon:
    """The abstract product: what every weapon of every world has."""
    name = "Weapon"
    damage_type = "bullet"
    damage = 25
    delay = 0.25                 # seconds between two shots

    def describe(self):
        return "%s [%s]" % (self.name, self.damage_type)


# ---- fantasy forest
class AcornSling(Weapon):
    name, damage_type, damage, delay = "Acorn Sling", "bullet", 25, 0.25


class FireStaff(Weapon):
    name, damage_type, damage, delay = "Fire Staff", "fire", 20, 0.35


class NatureWand(Weapon):
    name, damage_type, damage, delay = "Nature Wand", "laser", 12, 0.12


# ---- desert: slow and heavy
class DesertSling(Weapon):
    name, damage_type, damage, delay = "Sling", "bullet", 32, 0.40


class FireBomb(Weapon):
    name, damage_type, damage, delay = "Fire Bomb", "fire", 24, 0.45


class SunBeam(Weapon):
    name, damage_type, damage, delay = "Sun Beam", "laser", 10, 0.09


# ---- space: fast and light
class Blaster(Weapon):
    name, damage_type, damage, delay = "Blaster", "bullet", 20, 0.18


class PlasmaCannon(Weapon):
    name, damage_type, damage, delay = "Plasma Cannon", "fire", 26, 0.40


class LaserBeam(Weapon):
    name, damage_type, damage, delay = "Laser Beam", "laser", 14, 0.10


# ---- extreme: the strongest of all
class ObsidianShard(Weapon):
    name, damage_type, damage, delay = "Obsidian Shard", "bullet", 30, 0.28


class HellfireCannon(Weapon):
    name, damage_type, damage, delay = "Hellfire Cannon", "fire", 28, 0.40


class SoulFlame(Weapon):
    name, damage_type, damage, delay = "Soul Flame", "laser", 16, 0.10


def default_weapons():
    """The weapons used when a Player is created alone (tests, demos)."""
    return [AcornSling(), FireStaff(), NatureWand()]
