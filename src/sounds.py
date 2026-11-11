"""Sound effects and background music, powered by pygame.mixer."""

import pygame


class Sounds:
    """Loads and plays all game sound effects and music.

    Attributes:
        pacgum: Sound played when eating a pacgum.
        super_pacgums: Sound played when eating a super pacgum.
        death: Sound played when the player dies.
        ghost_eaten: Sound played when eating an edible ghost.
        game_over: Sound played on game over.
    """

    def __init__(self) -> None:
        """Initialize the mixer and load all sound assets.

        If no audio device is available, or sound files are missing,
        sound is disabled and the game continues silently rather than
        crashing.
        """
        self.enabled = True
        try:
            pygame.mixer.init()
        except pygame.error as error:
            print(f"Warning: audio unavailable ({error}), sound disabled")
            self.enabled = False
            return

        try:
            self.pacgum = pygame.mixer.Sound("assets/sounds/bubbles.wav")
            self.super_pacgums = pygame.mixer.Sound(
                "assets/sounds/superpacgums.wav")
            self.death = pygame.mixer.Sound("assets/sounds/laugh.ogg")
            self.ghost_eaten = pygame.mixer.Sound(
                "assets/sounds/wobbleup.wav")
            self.game_over = pygame.mixer.Sound("assets/sounds/game_over.mp3")
        except (FileNotFoundError, pygame.error) as error:
            print(f"Warning: sound file missing ({error}), sound disabled")
            self.enabled = False

    def play_pacgum(self) -> None:
        """Play the pacgum-eaten sound effect."""
        if self.enabled:
            self.pacgum.play()

    def play_super_pacgums(self) -> None:
        """Play the super-pacgum-eaten sound effect."""
        if self.enabled:
            self.super_pacgums.play()

    def play_death(self) -> None:
        """Play the player-death sound effect."""
        if self.enabled:
            self.death.play()

    def play_ghost_eaten(self) -> None:
        """Play the ghost-eaten sound effect."""
        if self.enabled:
            self.ghost_eaten.play()

    def play_music(self) -> None:
        """Load and loop the background music."""
        if self.enabled:
            pygame.mixer.music.load("assets/sounds/pacman.mp3")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)

    def stop_music(self) -> None:
        """Stop the background music."""
        if self.enabled:
            pygame.mixer.music.stop()
