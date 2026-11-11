"""Core game state and rules: score, pacgums, ghosts, level progression."""

import pygame
from .maze.maze import Maze, Direction
from .maze.maze_loader import load_maze
from .constants import (PACMAN_DEFAULT_MOVE_DELAY, GHOST_MOVE_DELAY,
                        PACMAN_CHEAT_MODE_MOVE_DELAY, EDIBLE_DURATION,
                        COUNTDOWN_TIMER)
from .graphics import interpolated_position, distance_between
from .player import Player
from .ghost import Ghost
from .sounds import Sounds
from enum import Enum
from .config import Config
import random


class GhostMode(Enum):
    """Cosmetic ghost skin set: default (PC) or the '42 staff' theme."""
    CLASSIC = 1
    STAFF = 2


class Game:
    """Owns the current maze, player, ghosts, score, and level flow.

    Attributes:
        maze: The current level's Maze.
        player: The current Player.
        score: Current run score.
        config: The loaded game configuration.
        points_per_pacgum: Points awarded per pacgum eaten.
        level_index: Index of the current level in config.levels.
        pacgums: Coordinates of remaining pacgums.
        super_pacgums: Coordinates of remaining super pacgums.
        points_per_super_pacgum: Points awarded per super pacgum eaten.
        points_per_ghost: Points awarded per ghost eaten.
        ghosts: List of active ghosts.
        sounds: Sound effects and music player.
        ghost_mode: Current cosmetic ghost skin set.
        countdown_timer: Seconds left before gameplay resumes (start of
            game, start of level, or after losing a life).
        level_start_score: Score at the start of the current level, used
            to restore it on restart.
        lives: Remaining lives for the current run.
        cheat_mode: True if cheat mode is active.
        edible_timer: Seconds elapsed since ghosts became edible.
        edible_duration: Seconds ghosts stay edible after a super pacgum.
        level_time: Seconds elapsed in the current level.
    """

    def __init__(self, maze: Maze, player: Player, config: Config) -> None:
        """Initialize a new game from a starting maze, player, and config.

        Args:
            maze: The maze for the first level.
            player: The starting player.
            config: The loaded game configuration.
        """
        self.maze = maze
        self.player = player
        self.score = 0
        self.config = config
        self.points_per_pacgum = config.points_per_pacgum
        self.level_index = 0
        self.pacgums = self.create_pacgums()
        self.super_pacgums = self.create_super_pacgums()
        self.pacgums -= self.super_pacgums
        self.points_per_super_pacgum = config.points_per_super_pacgum
        self.points_per_ghost = config.points_per_ghost
        self.ghosts = self.create_ghosts()
        self.sounds = Sounds()
        self.sounds.play_music()
        self.ghost_mode = GhostMode.CLASSIC
        self.countdown_timer = 0.0
        self.level_start_score = 0
        self.lives = config.lives
        self.cheat_mode = False
        self.edible_timer = 0.0
        self.edible_duration = EDIBLE_DURATION
        self.level_time = 0.0
        self.laugh = pygame.mixer.Sound("assets/sounds/laugh.ogg")

    def create_pacgums(self) -> set[tuple[int, int]]:
        """Place pacgums on random playable cells, scaled by level.

        The target count grows by 5 per level index, clamped to the
        number of available cells (excluding '42' cells and the
        player's spawn).

        Returns:
            Coordinates of the cells that should hold a pacgum.
        """
        available: list[tuple[int, int]] = []

        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.get_cell(x, y)

                if cell.is_42:
                    continue
                if (x, y) == (self.player.x, self.player.y):
                    continue

                available.append((x, y))

        target = self.config.pacgum + self.level_index * 5
        count = min(target, len(available))
        return set(random.sample(available, count))

    def create_super_pacgums(self) -> set[tuple[int, int]]:
        """Place a super pacgum in each of the maze's four corners.

        Returns:
            Coordinates of the four corner cells.
        """
        return {
            (0, 0),
            (self.maze.width - 1, 0),
            (0, self.maze.height - 1),
            (self.maze.width - 1, self.maze.height - 1),
        }

    def create_ghosts(self) -> list[Ghost]:
        """Spawn one ghost in each corner, with level-scaled difficulty.

        Ghost speed increases and the chase-vs-random chance grows
        with level_index. Only the first ghost starts active; the
        rest activate progressively as pacgums are eaten (see
        ghost_activation).

        Returns:
            The four newly created ghosts.
        """
        ghost_delay = max(GHOST_MOVE_DELAY - self.level_index * 0.03, 0.25)
        chase_chance = min(0.6 + self.level_index * 0.05, 0.9)
        positions = [
            (0, 0),
            (self.maze.width - 1, 0),
            (0, self.maze.height - 1),
            (self.maze.width - 1, self.maze.height - 1),
        ]

        ghosts: list[Ghost] = []

        for x, y in positions:
            ghosts.append(Ghost(
                    x=x,
                    y=y,
                    direction=Direction.EAST,
                    spawn_x=x,
                    spawn_y=y,
                    prev_x=x,
                    prev_y=y,
                    move_delay=ghost_delay,
                    chase_chance=chase_chance,
                )
            )
        ghosts[0].active = True
        return ghosts

    def check_pacgum(self) -> None:
        """Eat the pacgum under the player, if any, and award points."""
        position = (self.player.x, self.player.y)

        if position in self.pacgums:
            self.pacgums.remove(position)
            self.score += self.points_per_pacgum
            self.sounds.play_pacgum()

    def check_super_pacgum(self) -> None:
        """Eat the super pacgum under the player, if any.

        Awards points and makes all ghosts edible for edible_duration
        seconds.
        """
        position = (self.player.x, self.player.y)

        if position in self.super_pacgums:
            self.super_pacgums.remove(position)
            self.score += self.points_per_super_pacgum
            self.sounds.play_super_pacgums()
            self.edible_timer = 0.0
            for ghost in self.ghosts:
                ghost.edible = True

    def is_touching_ghost(self, ghost: Ghost) -> bool:
        """Check whether the player's visual position overlaps a ghost's.

        Uses interpolated (visually rendered) positions rather than
        raw cell coordinates, so collisions line up with what the
        player actually sees on screen.

        Args:
            ghost: The ghost to check against the player.

        Returns:
            True if the player and ghost are visually close enough
            to count as touching.
        """
        player_x, player_y = interpolated_position(
            self.player.x, self.player.y,
            self.player.prev_x, self.player.prev_y,
            self.player.move_timer, self.player.move_delay)

        ghost_x, ghost_y = interpolated_position(
            ghost.x, ghost.y, ghost.prev_x, ghost.prev_y,
            ghost.move_timer, ghost.move_delay)

        return distance_between(player_x, player_y, ghost_x, ghost_y) < 0.5

    def check_ghost_collision(self) -> None:
        """Resolve collisions between the player and each ghost.

        An edible ghost is eaten: the player scores points and the
        ghost respawns at its corner with temporary immunity. A
        non-edible, active ghost costs the player a life (unless
        cheat mode is on, or the ghost is still immune after
        respawning), then both the player and a countdown reset.
        """
        for ghost in self.ghosts:
            if self.is_touching_ghost(ghost):
                if ghost.edible:
                    self.score += self.points_per_ghost
                    ghost.x, ghost.y = ghost.spawn_x, ghost.spawn_y
                    ghost.prev_x, ghost.prev_y = ghost.spawn_x, ghost.spawn_y
                    ghost.edible = False
                    ghost.respawn_timer = 6.0

                elif (not self.cheat_mode and ghost.respawn_timer <= 0):
                    self.player.lives -= 1
                    self.laugh.play()
                    self.player.x, self.player.y = self.player_spawn()
                    self.player.prev_x, self.player.prev_y = (
                        self.player.x, self.player.y)
                    self.ghosts = self.create_ghosts()
                    self.start_countdown()

    def update(self, dt: float) -> None:
        """Advance game rules by one frame: pacgums, ghosts, timers.

        Args:
            dt: Time elapsed since the last frame, in seconds.
        """
        self.check_pacgum()
        self.check_super_pacgum()
        self.check_ghost_collision()
        self.ghost_activation()
        self.level_time += dt
        if self.level_time >= self.config.level_max_time:
            self.restart_level()

        self.edible_timer += dt
        if self.edible_timer >= self.edible_duration:
            for ghost in self.ghosts:
                ghost.edible = False

        for ghost in self.ghosts:
            ghost.update(self.maze, dt, (self.player.x, self.player.y))

    def load_level(self, index: int) -> None:
        """Generate and load the level at the given index.

        Regenerates the maze, resets the player's position (keeping
        lives), respawns ghosts, resets pacgums and all per-level
        timers, and starts the pre-level countdown. Reapplies cheat
        mode if it was active.

        Args:
            index: Index into config.levels of the level to load.
        """
        self.level_index = index
        self.level_start_score = self.score
        level_config = self.config.levels[index]

        self.maze = load_maze(
            level_config.width,
            level_config.height,
            self.config.seed,
        )

        spawn_x, spawn_y = self.player_spawn()

        self.player = Player(
            spawn_x,
            spawn_y,
            Direction.EAST,
            self.lives,
            Direction.EAST,
            prev_x=spawn_x,
            prev_y=spawn_y,
        )

        self.ghosts = self.create_ghosts()
        self.pacgums = self.create_pacgums()
        self.super_pacgums = self.create_super_pacgums()
        self.level_time = 0.0
        self.edible_timer = 0.0

        if self.cheat_mode:
            self.cheat()
        else:
            self.start_countdown()

    def start_countdown(self) -> None:
        """Start (or restart) the 3-second pre-play countdown."""
        self.countdown_timer = COUNTDOWN_TIMER

    def start_game(self) -> None:
        """Reset score and lives, then load the first level."""
        self.score = 0
        self.lives = self.config.lives
        self.load_level(0)

    def restart_level(self) -> None:
        """Reload the current level, restoring score and lives to their
        values at the start of this level."""
        self.score = self.level_start_score
        self.lives = self.config.lives
        self.load_level(self.level_index)

    def level_complete(self) -> bool:
        """Check whether all pacgums and super pacgums have been eaten.

        Returns:
            True if the current level is complete.
        """
        return not self.pacgums and not self.super_pacgums

    def next_level(self) -> bool:
        """Advance to the next level, if one exists.

        Returns:
            True if a next level was loaded, False if this was the last
            level.
        """
        next_index = self.level_index + 1

        if next_index >= len(self.config.levels):
            return False

        self.load_level(next_index)
        return True

    def cheat(self) -> None:
        """Apply or revert cheat-mode effects (currently: player speed)."""
        if self.cheat_mode:
            self.player.move_delay = PACMAN_CHEAT_MODE_MOVE_DELAY
        else:
            self.player.move_delay = PACMAN_DEFAULT_MOVE_DELAY

    def player_spawn(self) -> tuple[int, int]:
        """Find a spawn cell near the maze center, outside the '42' shape.

        Searches outward from the center by increasing Manhattan distance
        until a non-'42' cell is found.

        Returns:
            Coordinates of a valid spawn cell.

        Raises:
            ValueError: If no valid spawn cell exists in the maze.
        """
        center_x = self.maze.width // 2
        center_y = self.maze.height // 2

        for distance in range(
            self.maze.width + self.maze.height
        ):
            for y in range(self.maze.height):
                for x in range(self.maze.width):
                    dist = (
                        abs(x - center_x)
                        + abs(y - center_y)
                    )

                    if dist != distance:
                        continue

                    cell = self.maze.get_cell(x, y)

                    if not cell.is_42:
                        return x, y

        raise ValueError("No valid player spawn")

    def ghost_activation(self) -> None:
        """Activate ghosts 2-4 progressively as pacgums are eaten.

        Ghost 1 is active from the start. Ghost 2 activates at 25%
        of pacgums eaten, ghost 3 at 50%, ghost 4 at 75%.
        """
        total = self.config.pacgum
        eaten = total - len(self.pacgums)
        percent_eaten = eaten / total if total > 0 else 0

        if percent_eaten >= 0.25:
            self.ghosts[1].active = True
        if percent_eaten >= 0.50:
            self.ghosts[2].active = True
        if percent_eaten >= 0.75:
            self.ghosts[3].active = True

    def time_left(self) -> int:
        """Return the remaining seconds for the current level."""
        remaining = self.config.level_max_time - self.level_time
        return max(0, int(remaining))

    def is_game_over(self) -> bool:
        """Check whether the player has run out of lives."""
        return self.player.lives <= 0
