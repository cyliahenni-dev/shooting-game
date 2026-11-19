"""SRP: Health only stores hit points (the bar is drawn by the view)."""


class Health:
    def __init__(self, max_hp):
        self.max_hp = self.hp = max_hp

    def take(self, amount):
        self.hp = max(0, self.hp - amount)

    @property
    def alive(self):
        return self.hp > 0

    @property
    def ratio(self):
        return self.hp / self.max_hp
