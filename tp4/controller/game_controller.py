"""CONTROLLER: reads the keyboard and the mouse, updates the model, asks the view to draw.

Main loop: input -> update the model -> draw the view.
The theme can only be changed in the menu, never during a game."""
import pygame
from model.game_board import GameBoard
from view.game_view import GameView
import settings as cfg


class GameController:
    def __init__(self, show_menu=False, board=None, view=None):
        self.view = view or GameView()
        self.board = board or GameBoard()
        self.clock = pygame.time.Clock()
        self.dt = 0.0
        # the tests create GameController() without the menu: it starts playing directly
        self.show_menu = show_menu
        self.state = "menu" if show_menu else "playing"
        self.theme_changed = False

    # ------------------------------------------------------------------ menu
    def change_theme(self):
        self.view.next_theme()
        self.theme_changed = True

    def start_game(self):
        if self.theme_changed:                 # a new look always starts a fresh game
            self.board.reset()
            self.theme_changed = False
        self.state = "playing"

    def handle_menu_event(self, event):
        """Returns False when the player wants to quit."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.start_game()
            elif event.key == pygame.K_t:
                self.change_theme()
        action = self.view.menu_button_at(event)
        if action == "play":
            self.start_game()
        elif action == "theme":
            self.change_theme()
        elif action == "quit":
            return False
        return True

    # ----------------------------------------------------------------- input
    def handle_input(self):
        """Returns False when the game must stop."""
        was_playing = self.state == "playing"
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.state == "menu":
                if not self.handle_menu_event(event):
                    return False
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not self.show_menu:
                        return False
                    self.state = "menu"                      # Esc = back to the menu
                    continue
                if event.key == pygame.K_r and self.board.game_over:
                    self.board.reset()
                if pygame.K_1 <= event.key <= pygame.K_3:
                    self.board.player.select_weapon(list(cfg.WEAPONS)[event.key - pygame.K_1])
        if was_playing and self.state == "playing" and not self.board.game_over:
            self._control_player()
        return True

    def _control_player(self):
        keys = pygame.key.get_pressed()
        move = pygame.Vector2(
            (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a]),
            (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w]))
        self.board.player.move(move, self.dt, self.board.width, self.board.height)
        self.board.player.aim(pygame.mouse.get_pos())
        if pygame.mouse.get_pressed()[0] or keys[pygame.K_SPACE]:
            before = len(self.board.bullets)
            self.board.fire()
            if len(self.board.bullets) > before:             # a bullet was really fired
                self.view.play_sound("shoot")

    # ------------------------------------------------------------------ loop
    def run(self, max_frames=None):
        """Main loop (max_frames is used by the tests)."""
        frames, running = 0, True
        while running and (max_frames is None or frames < max_frames):
            self.dt = self.clock.tick(cfg.FPS) / 1000.0
            running = self.handle_input()
            if self.state == "playing":
                was_over = self.board.game_over
                self.board.update(self.dt)
                if self.board.game_over and not was_over:
                    self.view.play_sound("game_over")
                self.view.draw_game(self.board)
            else:
                self.view.draw_menu()
            frames += 1
        self.view.close()
