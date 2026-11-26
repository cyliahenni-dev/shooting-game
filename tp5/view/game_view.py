"""VIEW: the window, the background, the HUD, the menu and the game-over screen.

It only reads the model. It never changes it and never reads the keyboard:
the controller does that and calls the methods below.
The look (images, background, sounds) follows the world of the current level: the theme
folder with the same name as the world (world.key)."""
import pygame
from model.worlds import SUMMONABLE
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
        self.world_title = ""
        self.veil = pygame.Surface((cfg.WIDTH, cfg.HEIGHT), pygame.SRCALPHA)
        self.veil.fill((0, 0, 0, 140))                  # darkens the background in the menu
        x = cfg.WIDTH // 2 - 150
        self.buttons = {
            "play": Button((x, 220, 300, 50), lambda: "PLAY"),
            "world": Button((x, 284, 300, 50), lambda: "World: " + self.world_title),
            "extreme": Button((x, 348, 300, 50), lambda: "EXTREME", fill=(120, 34, 20),
                              hover=(184, 62, 28), border=(255, 150, 60)),
            "quit": Button((x, 412, 300, 50), lambda: "QUIT"),
        }

    # ---------------------------------------------- questions the controller asks
    def menu_button_at(self, event):
        """Name of the menu button that this mouse event clicked, or None."""
        for name, button in self.buttons.items():
            if button.clicked(event):
                return name
        return None

    # ------------------------------------------------------- look and sound
    def show_world(self, world):
        """Use the look of this world (its theme folder)."""
        self.world_title = world.title
        if self.assets.theme != world.key:
            self.assets.set_theme(world.key)

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

    def _text(self, font, text, color, **place):
        surface = font.render(text, True, color)
        self.screen.blit(surface, surface.get_rect(**place))

    def draw_menu(self):
        self._draw_background()
        self.screen.blit(self.veil, (0, 0))
        self._text(self.big_font, "MONSTER DEFENDER", (255, 255, 255), center=(cfg.WIDTH / 2, 140))
        for button in self.buttons.values():
            button.draw(self.screen, self.font)
        self._text(self.small_font, "PLAY: every level in the world you pick, harder each time.  "
                   "EXTREME: a separate level, alone.", (170, 170, 200), center=(cfg.WIDTH / 2, 488))
        self._text(self.small_font, "Enter = play   T = world   E = extreme   Esc = quit", (170, 170, 200),
                   center=(cfg.WIDTH / 2, cfg.HEIGHT - 28))
        pygame.display.flip()

    def draw_game(self, board):
        self.show_world(board.world)
        self._draw_background()
        self.renderer.draw_board(self.screen, board)
        p = board.player
        level = "EXTREME" if board.single_level else "Level: %d" % board.level
        hud = "Health: %d   Score: %d   %s   Weapon: %s" % (p.health, p.score, level, p.weapon.name)
        self.screen.blit(self.font.render(hud, True, (255, 255, 255)), (10, 10))
        self._text(self.small_font, "Esc = menu", (140, 140, 170), topright=(cfg.WIDTH - 10, 14))
        if board.banner_time > 0:                                   # "LEVEL 2" at the start of a level
            title = "EXTREME" if board.single_level else "LEVEL %d" % board.level
            self._text(self.big_font, title, (255, 255, 255), center=(cfg.WIDTH / 2, 110))
            self._text(self.font, board.world.title, (230, 230, 255), center=(cfg.WIDTH / 2, 156))
        summon = ["%d summon %s" % (7 + i, name) for i, name in enumerate(SUMMONABLE)
                  if name in board.world.monster_names()]
        weapons = "   ".join("%d %s [%s]" % (i + 1, w.name, w.damage_type) for i, w in enumerate(p.weapons))
        rules = "Flying: resists bullet  |  Strong: weak to fire  |  Dragon: resists fire  |  Robot: weak to laser"
        for line, y in ((" | ".join(summon), 66), (weapons, 46), (rules, 26)):
            self._text(self.small_font, line, (140, 140, 170), topleft=(10, cfg.HEIGHT - y))
        if board.game_over:
            self._text(self.big_font, "GAME OVER", (255, 80, 80), center=(cfg.WIDTH / 2, cfg.HEIGHT / 2 - 20))
            self._text(self.font, "Press R to restart", (255, 255, 255), center=(cfg.WIDTH / 2, cfg.HEIGHT / 2 + 30))
        pygame.display.flip()
