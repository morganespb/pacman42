"""Pygame application shell: window, event loop, and all screen states."""

from enum import Enum

import pygame

from .constants import (FONT, CELL_SIZE, MARGIN, HUD_HEIGHT, LOGO,
                        BACKGROUND, HUD_COLOR)
from .display import (draw_maze, draw_player, draw_hud, draw_pacgums,
                      draw_super_pacgums, draw_ghosts)
from .game import Game, GhostMode
from .highscores import load_high_scores, save_high_scores
from .maze.maze import Direction
from .sounds import Sounds
from .graphics import neon


class AppState(Enum):
    """The distinct screens/phases the app can be in."""
    WELCOME = 1
    MENU = 2
    PLAYING = 3
    PAUSED = 4
    LEVEL_COMPLETE = 5
    GAME_OVER = 6
    GAME_WON = 7
    HIGHSCORES = 8


class App:
    """Owns the pygame window, main loop, and all screen rendering/input.

    Attributes:
        screen: The pygame display surface.
        clock: Frame-rate limiting clock.
        running: True while the main loop should keep running.
        game: The current Game instance.
        sounds: Sound effects and music player for app-level sounds.
        state: The current AppState (which screen is shown).
        menu_choice: Currently highlighted menu option (unused/reserved).
        music_on: Whether background music is enabled.
        player_name: Name being typed on the end screen, for highscores.
    """

    def __init__(self, width: int, height: int, game: Game) -> None:
        """Initialize pygame, the window, and the app's starting state.

        Args:
            width: Window width in pixels.
            height: Window height in pixels.
            game: The Game instance to drive.
        """
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Pacman")

        self.clock = pygame.time.Clock()
        self.running = True
        self.game = game
        self.sounds = Sounds()
        self.state = AppState.WELCOME
        self.menu_choice = 0
        self.music_on = True
        self.player_name = ""

    def run(self) -> None:
        """Run the main loop: handle input, update, and draw until quit.

        While a pre-play countdown is active, the game is frozen: no
        input is handled and no state is updated, only the countdown
        overlay advances.
        """
        while self.running:
            dt = self.clock.tick(60) / 1000.0

            if (self.state == AppState.PLAYING
                    and self.game.countdown_timer > 0):
                self.game.countdown_timer -= dt
                self.draw_game()
                self.draw_countdown()
                pygame.display.flip()
                continue

            self.handle_events()

            if self.state == AppState.WELCOME:
                self.draw_welcome()
            elif self.state == AppState.MENU:
                self.draw_menu()
            elif self.state == AppState.PLAYING:
                self.update_game(dt)
                self.draw_game()
            elif self.state == AppState.LEVEL_COMPLETE:
                self.draw_level_complete()
            elif self.state == AppState.PAUSED:
                self.draw_pause_menu()
            elif self.state == AppState.GAME_WON:
                self.draw_end_screen(True)
            elif self.state == AppState.GAME_OVER:
                self.draw_end_screen(False)
            elif self.state == AppState.HIGHSCORES:
                self.draw_high_scores()

            pygame.display.flip()
        pygame.quit()

    def handle_events(self) -> None:
        """Dispatch pygame events to the handler for the current state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type != pygame.KEYDOWN:
                continue

            if self.state == AppState.WELCOME:
                if event.key == pygame.K_RETURN:
                    self.state = AppState.MENU

            elif self.state == AppState.MENU:
                self.handle_menu_keys(event)

            elif self.state == AppState.PLAYING:
                if event.key == pygame.K_ESCAPE:
                    self.state = AppState.PAUSED
                else:
                    self.handle_game_keys(event)

            elif self.state == AppState.PAUSED:
                self.handle_pause_keys(event)
                if event.key == pygame.K_c:
                    self.game.cheat_mode = not self.game.cheat_mode
                    self.game.cheat()

            elif self.state == AppState.LEVEL_COMPLETE:
                if event.key == pygame.K_RETURN:
                    if self.game.next_level():
                        self.state = AppState.PLAYING
                    else:
                        self.state = AppState.GAME_WON

            elif self.state in (AppState.GAME_OVER, AppState.GAME_WON):
                self.handle_end_screen_keys(event)

            elif self.state == AppState.HIGHSCORES:
                if event.key == pygame.K_m:
                    self.state = AppState.MENU
                elif event.key == pygame.K_q:
                    self.running = False

    def handle_game_keys(self, event: pygame.event.Event) -> None:
        """Handle keypresses while playing: movement and cheat toggles.

        Args:
            event: The pygame KEYDOWN event to handle.
        """
        if event.key == pygame.K_c:
            self.game.cheat_mode = not self.game.cheat_mode
            self.game.cheat()

        if event.key == pygame.K_n and self.game.cheat_mode:
            if self.game.next_level():
                self.resize_window()
                self.state = AppState.PLAYING
            else:
                self.state = AppState.GAME_WON
        if event.key == pygame.K_UP:
            self.game.player.requested_direction = Direction.NORTH
        elif event.key == pygame.K_DOWN:
            self.game.player.requested_direction = Direction.SOUTH
        elif event.key == pygame.K_LEFT:
            self.game.player.requested_direction = Direction.WEST
        elif event.key == pygame.K_RIGHT:
            self.game.player.requested_direction = Direction.EAST

    def handle_menu_keys(self, event: pygame.event.Event) -> None:
        """Handle keypresses on the start menu: ghost mode, music, start.

        Args:
            event: The pygame KEYDOWN event to handle.
        """
        if event.key == pygame.K_m:
            self.music_on = not self.music_on

        if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            if self.game.ghost_mode == GhostMode.CLASSIC:
                self.game.ghost_mode = GhostMode.STAFF
            else:
                self.game.ghost_mode = GhostMode.CLASSIC

        elif event.key == pygame.K_RETURN:
            self.game.start_game()
            self.state = AppState.PLAYING
        elif event.key == pygame.K_q:
            self.running = False

        if self.music_on:
            self.game.sounds.play_music()
        else:
            self.game.sounds.stop_music()

    def handle_pause_keys(self, event: pygame.event.Event) -> None:
        """Handle keypresses on the pause menu: resume, restart, quit.

        Args:
            event: The pygame KEYDOWN event to handle.
        """
        if event.key == pygame.K_ESCAPE:
            self.state = AppState.PLAYING

        elif event.key == pygame.K_r:
            self.game.restart_level()
            self.state = AppState.PLAYING

        elif event.key == pygame.K_n and self.game.cheat_mode:
            if self.game.next_level():
                self.state = AppState.PLAYING
            else:
                self.state = AppState.GAME_WON

        elif event.key == pygame.K_m:
            self.state = AppState.MENU
            self.game.sounds.stop_music()

        elif event.key == pygame.K_q:
            self.running = False

    def update_game(self, dt: float) -> None:
        """Advance player/game state by one frame; check game end states.

        Args:
            dt: Time elapsed since the last frame, in seconds.
        """
        self.game.player.update(self.game.maze, dt)
        self.game.update(dt)

        if self.game.is_game_over():
            if self.sounds.enabled:
                self.sounds.game_over.play()
            self.state = AppState.GAME_OVER
        elif self.game.level_complete():
            self.state = AppState.LEVEL_COMPLETE

    def handle_end_screen_keys(self, event: pygame.event.Event) -> None:
        """Handle name entry on the game-over/game-won screen.

        Args:
            event: The pygame KEYDOWN event to handle.
        """
        if event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]

        elif event.key == pygame.K_RETURN:
            if self.player_name:
                self.save_score()
                self.state = AppState.HIGHSCORES

        elif len(self.player_name) < 12:
            if event.unicode.isprintable():
                self.player_name += event.unicode

    def draw_game(self) -> None:
        """Draw the gameplay screen: maze, pacgums, ghosts, player, HUD."""
        self.screen.fill(BACKGROUND)

        draw_maze(self.screen, self.game.maze)
        draw_pacgums(self.screen, self.game.pacgums)
        draw_super_pacgums(self.screen, self.game.super_pacgums)
        draw_ghosts(self.screen, self.game.ghosts, self.game.ghost_mode)
        draw_player(self.screen, self.game.player)
        draw_hud(
            self.screen,
            self.game.score,
            self.game.player.lives,
            self.game.level_index + 1,
            self.game.time_left(),
            self.game.cheat_mode
        )

        if self.game.cheat_mode:
            overlay = pygame.Surface(
                self.screen.get_size(),
                pygame.SRCALPHA,
            )
            overlay.fill((180, 0, 0, 45))
            self.screen.blit(overlay, (0, 0))

            self.draw_cheat_mode()

    def draw_welcome(self) -> None:
        """Draw the welcome/splash screen with the game logo."""
        self.screen.fill(BACKGROUND)

        menu_font = pygame.font.Font(FONT, 20)
        center_x = self.screen.get_width() // 2
        logo = pygame.image.load(LOGO).convert_alpha()
        logo_width = int(self.screen.get_width() * 0.8)
        ratio = logo_width / logo.get_width()
        logo = pygame.transform.smoothscale(
            logo,
            (
                logo_width,
                int(logo.get_height() * ratio),
            ),
        )

        logo_rect = logo.get_rect(
            center=(center_x, 190)
        )
        self.screen.blit(logo, logo_rect)
        start = menu_font.render(
                "PRESS ENTER TO START", True, (255, 255, 255))
        start_rect = start.get_rect(center=(center_x, 330))
        self.screen.blit(start, start_rect)

    def draw_menu(self) -> None:
        """Draw the start menu: ghost mode, music toggle, start prompt."""
        self.screen.fill(BACKGROUND)
        center_x = self.screen.get_width() // 2
        title_font = pygame.font.Font(FONT, 40)
        menu_font = pygame.font.Font(FONT, 18)
        small_font = pygame.font.Font(FONT, 16)
        score_font = pygame.font.Font(FONT, 20)
        
        # PRESS ENTER TO PLAY
        start = title_font.render(
            "PRESS ENTER TO PLAY",
            True,
            (100, 180, 255),
        )
        pulse = neon(2.5)
        start.set_alpha(int(80 + pulse * 175))
        start_rect = start.get_rect(center=(center_x, 180))
        box_rect = start_rect.inflate(40, 24)
        pygame.draw.rect(self.screen, (100,180, 255), box_rect, 2, 12)
        self.screen.blit(start, start_rect)

        # GHOST MODES
        mode = "POLITICALLY CORRECT"
        if self.game.ghost_mode == GhostMode.STAFF:
            mode = "UNHINGED"
        mode_text = menu_font.render(
            f"GHOST MODE   < {mode} >",
            True,
            (255, 255, 255),
        )
        mode_rect = mode_text.get_rect(center=(center_x, 580))
        self.screen.blit(mode_text, mode_rect)


        # HIGHSCORES
        scores = load_high_scores(self.game.config.highscore_filename)
        score_title = score_font.render(
                "HIGH SCORES",
                True,
                (180, 250, 255),
        )
        score_title_rect = score_title.get_rect(center=(center_x, 320))
        self.screen.blit(score_title, score_title_rect)

        for i, entry in enumerate(scores[:3]):
            score_text = score_font.render(f"{i + 1}. {entry['name']}   {entry['score']}",
                                           True,
                                           (220, 245, 255),
                                        )
            score_rect = score_text.get_rect(center=(center_x, 360 + i * 28))
            self.screen.blit(score_text, score_rect)

        # MUSIC 
        music = "ON" if self.music_on else "OFF"
        music_text = small_font.render(
            f"PRESS M FOR MUSIC   < {music} >",
            True,
            (220, 245, 255),
        )
        music_rect = music_text.get_rect(center=(
                    center_x, 625))
        self.screen.blit(music_text, music_rect)

        # quit render
        quit_text = small_font.render(
                "PRESS Q TO QUIT",
                True,
                (255, 255, 255),
            )
        quit_rect = quit_text.get_rect(
                center=(center_x, self.screen.get_height() - 50))
        self.screen.blit(quit_text, quit_rect)

    def draw_level_complete(self) -> None:
        """Draw the level-complete announcement screen."""
        self.screen.fill(BACKGROUND)

        font = pygame.font.Font(FONT, 32)
        text = font.render(
            f"LEVEL {self.game.level_index + 1} COMPLETE",
            True,
            (180, 250, 255),
        )

        rect = text.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() // 2,
            )
        )

        self.screen.blit(text, rect)

    def draw_pause_menu(self) -> None:
        """Draw the pause overlay on top of the frozen game screen.

        Includes resume/restart/menu/quit options plus a commands
        reference box showing controls and the current cheat state.
        """
        self.draw_game()

        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        self.screen.blit(overlay, (0, 0))

        center_x = self.screen.get_width() // 2

        title_font = pygame.font.Font(FONT, 34)
        me_font = pygame.font.Font(FONT, 22)
        small_font = pygame.font.Font(FONT, 15)

        title = title_font.render("PAUSED", True, (180, 250, 255))
        title_rect = title.get_rect(center=(center_x, 130))
        self.screen.blit(title, title_rect)

        options = [
            "ESC     RESUME",
            "R       RESTART LEVEL",
            "M       MAIN MENU",
            "Q       QUIT GAME",
        ]

        y = 190

        for option in options:
            text = me_font.render(option, True, (230, 245, 255))
            rect = text.get_rect(center=(center_x, y))
            self.screen.blit(text, rect)
            y += 34

        box_width = 380
        box_height = 190
        box_x = center_x - box_width // 2
        box_y = 350

        command_box = pygame.Rect(box_x, box_y, box_width, box_height)

        pygame.draw.rect(self.screen, (20, 30, 45), command_box, 8)
        pygame.draw.rect(self.screen, (70, 190, 255), command_box, 2, 8)

        command_title = me_font.render("GAME COMMANDS", True, (120, 220, 255))
        title_rect = command_title.get_rect(center=(center_x, box_y + 28))
        self.screen.blit(command_title, title_rect)

        cheat = "ON" if self.game.cheat_mode else "OFF"

        commands = [
            "ARROWS      MOVE",
            f"C          CHEAT MODE < {cheat} >",
            "N           NEXT LEVEL",
            "ESC         PAUSE / RESUME",
        ]

        y = box_y + 65

        for command in commands:
            text = small_font.render(command, True, (210, 230, 240))
            self.screen.blit(text, (box_x + 32, y))
            y += 28

    def draw_cheat_mode(self) -> None:
        """Draw a large, translucent 'CHEAT MODE' watermark over the screen."""
        font = pygame.font.Font(FONT, 64)

        text = font.render("CHEAT MODE", True, (255, 70, 70))

        text.set_alpha(45)

        rect = text.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() // 2,
            )
        )
        self.screen.blit(text, rect)

    def draw_countdown(self) -> None:
        """Draw the pre-play countdown number over the frozen game screen."""
        font = pygame.font.Font(FONT, 80)
        seconds_left = int(self.game.countdown_timer) + 1
        text = font.render(str(seconds_left), True, (180, 250, 255))
        text.set_alpha(80)

        rect = text.get_rect(
            center=(
                self.screen.get_width() // 2,
                self.screen.get_height() // 2,
            )
        )
        self.screen.blit(text, rect)

    def resize_window(self) -> None:
        """Resize the game window to fit the current level's maze size."""
        width = self.game.maze.width * CELL_SIZE + MARGIN * 2
        height = (
            self.game.maze.height * CELL_SIZE + HUD_HEIGHT + MARGIN * 2)
        self.screen = pygame.display.set_mode((width, height))

    def draw_game_won(self) -> None:
        """Draw a simple 'you won' screen.

        Currently unused by the main loop; draw_end_screen(True) is
        used instead. Kept available for potential future use.
        """
        self.screen.fill(BACKGROUND)

        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        title_font = pygame.font.Font(FONT, 36)
        menu_font = pygame.font.Font(FONT, 18)

        title = title_font.render("YOU WON!", True, (180, 250, 255))
        score = menu_font.render(
                f"FINAL SCORE: {self.game.score}", True, (230, 245, 255))
        menu = menu_font.render(
                "PRESS M FOR MAIN MENU", True, (120, 200, 255))

        self.screen.blit(
                title, title.get_rect(center=(center_x, center_y - 70)))
        self.screen.blit(score, score.get_rect(center=(center_x, center_y)))
        self.screen.blit(
                menu, menu.get_rect(center=(center_x, center_y + 70)))

    def draw_end_screen(self, won: bool) -> None:
        """Draw the game-over or game-won screen with name entry.

        Args:
            won: True to show the "won" variant, False for "game over".
        """
        self.screen.fill(BACKGROUND)

        center_x = self.screen.get_width() // 2
        center_y = self.screen.get_height() // 2

        title_font = pygame.font.Font(FONT, 38)
        font = pygame.font.Font(FONT, 18)

        title_text = "YOU WON!" if won else "GAME OVER"
        title_color = HUD_COLOR if won else (255, 80, 120)

        title = title_font.render(title_text, True, title_color)

        score = font.render(
                f"FINAL SCORE  {self.game.score}", True, HUD_COLOR)

        prompt = font.render("ENTER YOUR NAME", True, HUD_COLOR)

        name = font.render(self.player_name + "_", True, (255, 255, 255))

        help_text = font.render("ENTER TO SAVE", True, HUD_COLOR)

        self.screen.blit(
            title,
            title.get_rect(center=(center_x, center_y - 130)),
        )
        self.screen.blit(
            score,
            score.get_rect(center=(center_x, center_y - 70)),
        )
        self.screen.blit(
            prompt,
            prompt.get_rect(center=(center_x, center_y)),
        )
        self.screen.blit(
            name,
            name.get_rect(center=(center_x, center_y + 45)),
        )
        self.screen.blit(
            help_text,
            help_text.get_rect(center=(center_x, center_y + 110))
        )

    def draw_high_scores(self) -> None:
        """Draw the top-10 highscores screen loaded from disk."""
        self.screen.fill(BACKGROUND)

        center_x = self.screen.get_width() // 2

        title_font = pygame.font.Font(FONT, 36)
        score_font = pygame.font.Font(FONT, 18)
        small_font = pygame.font.Font(FONT, 14)

        title = title_font.render("HIGH SCORES", True, HUD_COLOR)

        self.screen.blit(
            title,
            title.get_rect(center=(center_x, 80)))

        scores = load_high_scores(self.game.config.highscore_filename)

        start_y = 150
        gap = 35

        for index, entry in enumerate(scores[:10], start=1):
            name = entry["name"]
            score = entry["score"]

            text = score_font.render(
                f"{index:02}.  {name:<12}  {score}", True, HUD_COLOR)

            self.screen.blit(text, text.get_rect(
                    center=(center_x, start_y + (index - 1) * gap)))

        menu = score_font.render("M - MAIN MENU", True, HUD_COLOR)

        self.screen.blit(menu, menu.get_rect(
                center=(center_x, self.screen.get_height() - 55)))

        quit_text = small_font.render("Q - QUIT", True, HUD_COLOR)
        quit_rect = quit_text.get_rect(
                center=(center_x, self.screen.get_height() - 25))
        self.screen.blit(quit_text, quit_rect)

    def save_score(self) -> None:
        """Save the current player_name and score to the highscore file."""
        save_high_scores(
            self.game.config.highscore_filename,
            self.player_name,
            self.game.score,
        )
