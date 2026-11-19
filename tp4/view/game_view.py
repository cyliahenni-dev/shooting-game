"""VIEW: the window, the background, the HUD, the menu and the game-over screen.

It only reads the model. It never changes it and never reads the keyboard:
the controller does that and calls the methods below.
The look (images, background, sounds) comes from the theme chosen in the menu."""
import pygame
from view.renderer import Renderer
from view.resources import assets as default_assets
from view.ui import Button
import settings as cfg


class GameView:
    def __init__(self, assets=default_assets):
        pygame.init()
        self.assets = assets
        self.screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
        pygame.display.set_caption("Monster Defender - TP N3")
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)
        self.big_font = pygame.font.SysFont(None, 64)
        self.renderer = Renderer(assets)
        self.veil = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
        self.veil.fill((0, 0, 0, 140))                  # darkens the background in the menu
        x = cfg.WIDTH // 2 - 150
        self.buttons = {
            "play": Button((x, 240, 300, 50), lambda: "PLAY"),
            "theme": Button((x, 310, 300, 50), lambda: "Theme: " + assets.theme),
            "quit": Button((x, 380, 300, 50), lambda: "QUIT"),
        }

    # ---------------------------------------------- questions the controller asks
    def menu_button_at(self, event):
        """Name of the menu button that this mouse event clicked, or None."""
        for name, button in self.buttons.items():
            if button.clicked(event):
                return name
        return None

    # ------------------------------------------------------- look and sound
    def next_theme(self):
        """Switch to the next theme (its player, monsters, bullets, background and sounds)."""
        self.assets.next_theme()

    def play_sound(self, name):
        self.assets.play(name)

    def close(self):
        pygame.quit()

    # --------------------------------------------------------------- drawing
    def _draw_background(self):
        bg = self.assets.cover("backgrounds", self.assets.background, (cfg.WIDTH, cfg.HEIGHT))
        if bg:
            self.screen.blit(bg, (0, 0))
        else:
            self.screen.fill((15, 15, 35))

    def draw_menu(self):
        self._draw_background()
        self.screen.blit(self.veil, (0, 0))
        title = self.big_font.render("MONSTER DEFENDER", True, (255, 255, 255))
        self.screen.blit(title, title.get_rect(center=(cfg.WIDTH / 2, 140)))
        for button in self.buttons.values():
            button.draw(self.screen, self.font)
        hint = "Enter = play   T = theme   Esc = quit"
        self.screen.blit(self.small_font.render(hint, True, (170, 170, 200)),
                         (cfg.WIDTH // 2 - 140, cfg.HEIGHT - 40))
        pygame.display.flip()

    def draw_game(self, board):
        self._draw_background()
        self.renderer.draw_board(self.screen, board)
        p = board.player
        hud = "Health: %d   Score: %d   Weapon: %s" % (p.health, p.score, p.weapon)
        self.screen.blit(self.font.render(hud, True, (255, 255, 255)), (10, 10))
        menu_hint = self.small_font.render("Esc = menu", True, (140, 140, 170))
        self.screen.blit(menu_hint, menu_hint.get_rect(topright=(cfg.WIDTH - 10, 14)))
        tips = "1 bullet  2 fire  3 laser  |  Flying resists bullet  |  Strong: weak to fire + shield  |  Immobile shoots"
        self.screen.blit(self.small_font.render(tips, True, (140, 140, 170)), (10, cfg.HEIGHT - 26))
        if board.game_over:
            txt = self.big_font.render("GAME OVER", True, (255, 80, 80))
            self.screen.blit(txt, txt.get_rect(center=(cfg.WIDTH / 2, cfg.HEIGHT / 2 - 20)))
            sub = self.font.render("Press R to restart", True, (255, 255, 255))
            self.screen.blit(sub, sub.get_rect(center=(cfg.WIDTH / 2, cfg.HEIGHT / 2 + 30)))
        pygame.display.flip()
