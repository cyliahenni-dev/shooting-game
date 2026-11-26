from model.game_object import GameObject


class FloatingText(GameObject):
    """Damage number that floats up and disappears.

    MODEL: it only says HOW the hit went (`effect`). The view chooses the colors."""
    RESISTED, WEAK, NORMAL = "resisted", "weak", "normal"

    def __init__(self, pos, text, effect=NORMAL, life=0.8):
        super().__init__(pos, 0)
        self.text = text
        self.effect = effect
        self.life = life

    @property
    def expired(self):
        return self.life <= 0

    def update(self, dt):
        self.pos.y -= 35 * dt
        self.life -= dt
