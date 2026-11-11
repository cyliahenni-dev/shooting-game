"""DIP: a monster depends on the abstract DamageStrategy, never on a precise weapon.

To change how a monster is affected by an attack, give it another strategy:
the Monster class is not modified."""
from abc import ABC, abstractmethod


class DamageStrategy(ABC):
    """Abstract damage-calculation mechanism."""

    @abstractmethod
    def compute(self, weapon, base_damage):
        """Damage really received when hit by `weapon` with `base_damage`."""

    @abstractmethod
    def describe(self):
        """Short text for the HUD / documentation."""


class NormalDamage(DamageStrategy):
    def compute(self, weapon, base_damage):
        return base_damage

    def describe(self):
        return "normal damage"


class ResistantDamage(DamageStrategy):
    """Resistant to certain weapons: they hurt less."""

    def __init__(self, resistant_to, factor=0.5):
        self.resistant_to = list(resistant_to)
        self.factor = factor

    def compute(self, weapon, base_damage):
        return base_damage * self.factor if weapon in self.resistant_to else base_damage

    def describe(self):
        return "resists " + ", ".join(self.resistant_to)


class WeaknessDamage(DamageStrategy):
    """Weak to certain weapons: they hurt more."""

    def __init__(self, weak_to, factor=2):
        self.weak_to = list(weak_to)
        self.factor = factor

    def compute(self, weapon, base_damage):
        return base_damage * self.factor if weapon in self.weak_to else base_damage

    def describe(self):
        return "weak to " + ", ".join(self.weak_to)
