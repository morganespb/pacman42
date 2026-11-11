"""Player entity: position, movement, and input-driven direction."""

from .maze.maze import Direction, Maze
from .constants import PACMAN_DEFAULT_MOVE_DELAY
from dataclasses import dataclass


@dataclass
class Player:
    """Pac-Man, moving through the maze one cell at a time.

    Attributes:
        x: Current column.
        y: Current row.
        direction: Direction currently being moved in.
        lives: Remaining lives.
        requested_direction: Direction requested by the player's last
            keypress; applied on the next move if not blocked by a wall.
        move_timer: Seconds accumulated since the last move.
        move_delay: Seconds required between two moves (controls speed).
    """
    x: int
    y: int
    direction: Direction
    lives: int
    requested_direction: Direction | None
    move_timer: float = 0.0
    move_delay: float = PACMAN_DEFAULT_MOVE_DELAY
    prev_x: int = 0
    prev_y: int = 0

    def move(self, maze: Maze) -> None:
        """Advance one cell in the current direction, if not blocked.

        Switches to requested_direction first if that side has no wall,
        then moves forward if the (possibly updated) current direction
        is also open.

        Args:
            maze: The maze the player moves through.
        """
        cell = maze.get_cell(self.x, self.y)
        self.prev_x = self.x
        self.prev_y = self.y

        if self.requested_direction is not None:
            if not cell.walls[self.requested_direction]:
                self.direction = self.requested_direction

        if cell.walls[self.direction]:
            return

        dx, dy = self.direction.value
        new_x = self.x + dx
        new_y = self.y + dy

        if maze.is_inside(new_x, new_y):
            self.x = new_x
            self.y = new_y

    def update(self, maze: Maze, dt: float) -> None:
        """Advance the move timer and trigger a move once the delay elapses.

        Args:
            maze: The maze the player moves through.
            dt: Time elapsed since the last frame, in seconds.
        """
        if self.requested_direction is None:
            return
        self.move_timer += dt

        if self.move_timer >= self.move_delay:
            self.move(maze)
            self.move_timer -= self.move_delay
