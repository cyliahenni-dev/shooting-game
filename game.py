"""The Game: window, main loop, keyboard/mouse input and HUD."""
import pygame
from game_board import GameBoard
import settings as cfg


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.WIDTH, cfg.HEIGHT))
        pygame.display.set_caption("Space Defender - OOP version")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 28)
        self.big_font = pygame.font.SysFont(None, 64)
        self.board = GameBoard()
        self.dt = 0.0

    # 1) input
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_r and self.board.game_over:
                    self.board.reset()
        if not self.board.game_over:
            keys = pygame.key.get_pressed()
            move = pygame.Vector2(
                (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a]),
                (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w]))
            self.board.player.move(move, self.dt, self.board.width, self.board.height)
            self.board.player.aim(pygame.mouse.get_pos())
            if pygame.mouse.get_pressed()[0] or keys[pygame.K_SPACE]:
                self.board.fire()
        return True

    # 3) rendering
    def draw(self):
        self.screen.fill((15, 15, 35))
        self.board.draw(self.screen)
        p = self.board.player
        hud = "Health: %d   Score: %d" % (p.health, p.score)
        self.screen.blit(self.font.render(hud, True, (255, 255, 255)), (10, 10))
        if self.board.game_over:
            txt = self.big_font.render("GAME OVER", True, (255, 80, 80))
            self.screen.blit(txt, txt.get_rect(center=(cfg.WIDTH / 2, cfg.HEIGHT / 2 - 20)))
            sub = self.font.render("Press R to restart", True, (255, 255, 255))
            self.screen.blit(sub, sub.get_rect(center=(cfg.WIDTH / 2, cfg.HEIGHT / 2 + 30)))
        pygame.display.flip()

    def run(self, max_frames=None):
        """Main loop: input -> update -> draw (max_frames is used by the tests)."""
        frames, running = 0, True
        while running and (max_frames is None or frames < max_frames):
            self.dt = self.clock.tick(cfg.FPS) / 1000.0
            running = self.handle_input()
            self.board.update(self.dt)          # 2) update objects + collisions
            self.draw()
            frames += 1
        pygame.quit()
