import pygame
from game_object import GameObject


class FloatingText(GameObject):
    """Damage number that floats up and disappears (red = resisted, green = weakness)."""
    _font = None

    def __init__(self, pos, text, color=(255, 255, 255), life=0.8):
        super().__init__(pos, 0)
        self.text = text
        self.color = color
        self.life = life

    @property
    def expired(self):
        return self.life <= 0

    def update(self, dt):
        self.pos.y -= 35 * dt
        self.life -= dt

    def draw(self, screen):
        if FloatingText._font is None:
            if not pygame.font.get_init():
                pygame.font.init()
            FloatingText._font = pygame.font.SysFont(None, 22)
        surf = FloatingText._font.render(self.text, True, self.color)
        screen.blit(surf, (self.pos.x - surf.get_width() / 2, self.pos.y))
