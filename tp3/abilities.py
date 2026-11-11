"""ISP: one small interface per ability.

A monster only inherits the abilities it really has. For example the
ImmobileMonster is a Shooter but is never forced to implement chase()."""
from abc import ABC, abstractmethod


class Chaser(ABC):
    @abstractmethod
    def chase(self, dt):
        """Walk toward the target."""


class Flyer(ABC):
    @abstractmethod
    def fly(self, dt):
        """Fly toward the target."""


class Shooter(ABC):
    @abstractmethod
    def shoot(self):
        """Return an EnemyShot aimed at the target."""


class Shielded(ABC):
    @abstractmethod
    def block(self, damage):
        """Return the damage that goes through the shield."""
