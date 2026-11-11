"""Convert a raw MazeGenerator grid into our own Maze/Cell objects."""

from .maze import Maze, Cell, Direction
from mazegenerator import MazeGenerator


def load_maze(width: int, height: int, seed: int) -> Maze:
    """Generate a maze and convert it into a Maze object.

    Runs the external MazeGenerator package, then decodes each cell's
    bitmask (1=North, 2=East, 4=South, 8=West wall) into a Cell with
    explicit walls per Direction.

    Args:
        width: Number of columns to generate.
        height: Number of rows to generate.
        seed: Random seed passed to MazeGenerator for reproducibility.

    Returns:
        A Maze populated with Cell objects and the set of "42" cell
        coordinates.
    """
    generator = MazeGenerator(
        size=(width, height),
        perfect=False,
        seed=seed,
    )

    raw_maze = generator.maze
    cells: list[list[Cell]] = []
    cells_42: set[tuple[int, int]] = set()

    for y, row in enumerate(raw_maze):
        maze_row: list[Cell] = []

        for x, value in enumerate(row):
            is_42 = value == 15

            cell = Cell(
                walls={
                    Direction.NORTH: bool(value & 1),
                    Direction.EAST: bool(value & 2),
                    Direction.SOUTH: bool(value & 4),
                    Direction.WEST: bool(value & 8),
                },
                is_42=is_42,
            )

            if is_42:
                cells_42.add((x, y))

            maze_row.append(cell)

        cells.append(maze_row)

    return Maze(width, height, cells, cells_42)
