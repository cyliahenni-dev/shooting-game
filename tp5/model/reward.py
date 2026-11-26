from model.game_object import GameObject
import settings as cfg


class Reward(GameObject):
    """The abstract product: a pickup. Every world has its own rewards (see worlds.py)."""
    POINTS = "points"
    HEALTH = "health"
    name = "Reward"

    def __init__(self, pos, kind):
        super().__init__(pos, cfg.REWARD_RADIUS)
        self.type = kind
        self.value = cfg.REWARD_POINTS if kind == self.POINTS else cfg.REWARD_HEALTH

    def apply(self, player):
        if self.type == self.POINTS:
            player.score += self.value
        else:
            player.heal(self.value)

    def update(self, dt):
        pass                                  # a reward stays where it dropped


# ---- fantasy forest
class GoldCoin(Reward):
    name = "Gold coin"

    def __init__(self, pos):
        super().__init__(pos, Reward.POINTS)
        self.value = 50


class HealingPotion(Reward):
    name = "Healing potion"

    def __init__(self, pos):
        super().__init__(pos, Reward.HEALTH)
        self.value = 25


# ---- desert
class AncientRelic(Reward):
    name = "Ancient relic"

    def __init__(self, pos):
        super().__init__(pos, Reward.POINTS)
        self.value = 70


class WaterFlask(Reward):
    name = "Water flask"

    def __init__(self, pos):
        super().__init__(pos, Reward.HEALTH)
        self.value = 20


# ---- space
class EnergyCrystal(Reward):
    name = "Energy crystal"

    def __init__(self, pos):
        super().__init__(pos, Reward.POINTS)
        self.value = 60


class RepairKit(Reward):
    name = "Repair kit"

    def __init__(self, pos):
        super().__init__(pos, Reward.HEALTH)
        self.value = 30


# ---- extreme
class SoulRuby(Reward):
    name = "Soul ruby"

    def __init__(self, pos):
        super().__init__(pos, Reward.POINTS)
        self.value = 100


class VitalFlask(Reward):
    name = "Vital flask"

    def __init__(self, pos):
        super().__init__(pos, Reward.HEALTH)
        self.value = 35
