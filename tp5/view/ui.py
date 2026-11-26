"""VIEW: small clickable widgets."""
import pygame


class Button:
    def __init__(self, rect, label, fill=(45, 45, 90), hover=(80, 80, 140), border=(150, 150, 210)):
        self.rect = pygame.Rect(rect)
        self.label = label                  # a function, so the text can change
        self.fill, self.hover, self.border = fill, hover, border

    def draw(self, screen, font):
        over = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, self.hover if over else self.fill, self.rect, border_radius=10)
        pygame.draw.rect(screen, self.border, self.rect, 2, border_radius=10)
        text = font.render(self.label(), True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=self.rect.center))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


class IconButton:
    """A small square button with an icon drawn in code."""
    def __init__(self, pos, kind, size=36):
        self.rect = pygame.Rect(pos, (size, size))
        self.kind = kind                    # "theme" or "background"

    def draw(self, screen):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(screen, (80, 80, 140) if hover else (45, 45, 90), self.rect, border_radius=8)
        pygame.draw.rect(screen, (150, 150, 210), self.rect, 2, border_radius=8)
        cx, cy = self.rect.center
        if self.kind == "theme":            # paint palette
            pygame.draw.circle(screen, (235, 200, 150), (cx, cy), 12)
            for dx, dy, col in ((-5, -4, (230, 70, 70)), (2, -7, (250, 220, 70)),
                                (7, 0, (90, 200, 90)), (-6, 5, (80, 140, 255))):
                pygame.draw.circle(screen, col, (cx + dx, cy + dy), 3)
        else:                               # little picture: frame, sun, mountains
            frame = pygame.Rect(0, 0, 24, 18)
            frame.center = (cx, cy)
            pygame.draw.rect(screen, (235, 235, 245), frame, 2, border_radius=3)
            pygame.draw.circle(screen, (250, 220, 70), (frame.left + 7, frame.top + 6), 3)
            pygame.draw.polygon(screen, (235, 235, 245), [
                (frame.left + 3, frame.bottom - 3), (frame.left + 10, frame.top + 9),
                (frame.left + 16, frame.bottom - 3)])

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))
