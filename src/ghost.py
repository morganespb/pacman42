"""Ghost entity: position, movement, and edible/eaten state."""

from dataclasses import dataclass
from .maze.maze import Direction, Maze
from .constants import GHOST_MOVE_DELAY
import random


@dataclass
class Ghost:
    """An enemy that roams the maze and can become edible.

    Attributes:
        x: Current column.
        y: Current row.
        direction: Direction currently faced (unused by movement logic
            yet, reserved for sprite orientation).
        spawn_x: Column to return to after being eaten.
        spawn_y: Row to return to after being eaten.
        move_timer: Seconds accumulated since the last move.
        move_delay: Seconds required between two moves (controls speed).
        prev_x: Column before the last move, used for visual interpolation.
        prev_y: Row before the last move, used for visual interpolation.
        respawn_timer: Seconds left of immunity after being eaten; the
            ghost stays still and untouchable while this is above 0.
        chase_chance: Probability (0-1) of chasing via BFS instead of
            moving randomly, when active.
        edible: True if the player can currently eat this ghost.
        eaten: True if the ghost has been eaten and is respawning.
        active: True once the ghost has left its corner and starts
            roaming/chasing; inactive ghosts are harmless.
    """
    x: int
    y: int
    direction: Direction
    spawn_x: int
    spawn_y: int
    move_timer: float = 0.0
    move_delay: float = GHOST_MOVE_DELAY
    prev_x: int = 0
    prev_y: int = 0
    respawn_timer: float = 0.0
    chase_chance: float = 0.5
    edible: bool = False
    eaten: bool = False
    active: bool = True

    def update(self, maze: Maze, dt: float, target: tuple[int, int]) -> None:
        """Advance timers and trigger a move once the delay elapses.

        While respawn_timer is above 0, the ghost stays still instead
        of moving.

        Args:
            maze: The maze the ghost moves through.
            dt: Time elapsed since the last frame, in seconds.
            target: The player's current (x, y) position.
        """
        if self.respawn_timer > 0:
            self.respawn_timer -= dt
            return

        self.move_timer += dt

        if self.move_timer >= self.move_delay:
            self.move(maze, target)
            self.move_timer -= self.move_delay

    def move(self, maze: Maze, target: tuple[int, int]) -> None:
        """Move one cell, behavior depending on the ghost's current state.

        If edible, moves away from target half the time and randomly
        the other half. If active, chases target via BFS with
        probability chase_chance, else moves randomly. If inactive,
        always moves randomly.

        Args:
            maze: The maze the ghost moves through.
            target: The player's current (x, y) position.
        """
        neighbors = maze.accessible_neighbors(self.x, self.y)

        if not neighbors:
            return

        if self.edible:
            if random.random() < 0.5:
                best = max(neighbors,
                           key=lambda n: abs(n[0] - target[0])
                           + abs(n[1] - target[1]))
                self.prev_x, self.prev_y = self.x, self.y
                self.x, self.y = best
            else:
                self.prev_x, self.prev_y = self.x, self.y
                self.x, self.y = random.choice(neighbors)

        elif self.active and random.random() < self.chase_chance:
            path = maze.shortest_path_to((self.x, self.y), target)
            if path and len(path) >= 2:
                self.prev_x = self.x
                self.prev_y = self.y
                (self.x, self.y) = path[1]

        else:
            self.prev_x = self.x
            self.prev_y = self.y
            self.x, self.y = random.choice(neighbors)
