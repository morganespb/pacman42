"""Our own maze representation: cells, walls, and pathfinding.

Flow: an external MazeGenerator produces a raw grid -> maze_loader.py
converts it into Cell/Maze objects -> the game and renderer work only
with these objects, never with the raw grid.
"""

from dataclasses import dataclass, field
from collections import deque
from enum import Enum


class Direction(Enum):
    """Cardinal direction as a (dx, dy) offset usable for grid movement."""
    NORTH = (0, -1)
    SOUTH = (0, 1)
    WEST = (-1, 0)
    EAST = (1, 0)


@dataclass
class Cell:
    """A single maze cell.

    Attributes:
        walls: Maps each Direction to True if a wall blocks that side.
        is_42: True if this cell is part of the "42" decorative shape.
    """
    walls: dict[Direction, bool]
    is_42: bool = False


@dataclass
class Maze:
    """A generated maze exposed as a 2D grid of Cell objects.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        cells: 2D grid of Cell, indexed as cells[y][x].
        cells_42: Coordinates of cells belonging to the "42" shape.
    """
    width: int
    height: int
    cells: list[list[Cell]]
    cells_42: set[tuple[int, int]] = field(default_factory=set)

    def is_inside(self, x: int, y: int) -> bool:
        """Check whether (x, y) lies within the maze bounds.

        Args:
            x: Column index.
            y: Row index.

        Returns:
            True if the coordinates are inside the maze.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Cell:
        """Return the cell at (x, y).

        Args:
            x: Column index.
            y: Row index.

        Returns:
            The Cell at the given coordinates.

        Raises:
            IndexError: If (x, y) is outside the maze.
        """
        if not self.is_inside(x, y):
            raise IndexError(f"Cell ({x}, {y}) is outside the maze.")
        return self.cells[y][x]

    def accessible_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        """List neighbors reachable from (x, y) (no wall in between).

        Args:
            x: Column index.
            y: Row index.

        Returns:
            Coordinates of each neighboring cell with no wall in between.
        """
        cell = self.get_cell(x, y)
        neighbors = []

        for direction in Direction:
            dx, dy = direction.value
            nx = x + dx
            ny = y + dy

            if not cell.walls[direction] and self.is_inside(nx, ny):
                neighbors.append((nx, ny))

        return neighbors

    def shortest_path_to(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
    ) -> list[tuple[int, int]] | None:
        """Find the shortest path from start to goal using BFS.

        Args:
            start: Starting coordinates.
            goal: Target coordinates.

        Returns:
            The path as a list of coordinates from start to goal
            (inclusive), or None if no path exists.
        """
        if start == goal:
            return [start]

        queue = deque([start])
        came_from: dict[tuple[int, int], tuple[int, int]] = {start: start}

        while queue:
            current = queue.popleft()

            if current == goal:
                break

            for neighbor in self.accessible_neighbors(*current):
                if neighbor not in came_from:
                    came_from[neighbor] = current
                    queue.append(neighbor)

        if goal not in came_from:
            return None

        path = [goal]
        while path[-1] != start:
            path.append(came_from[path[-1]])

        path.reverse()
        return path
