import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from src.maze.maze import Direction  # noqa: E402
from src.player import Player  # noqa: E402
from src.maze.maze_loader import load_maze  # noqa: E402
from src.parsing import from_dict, parsing  # noqa: E402
import sys  # noqa: E402
from src.app import App  # noqa: E402
from src.game import Game  # noqa: E402
from src.display import CELL_SIZE, MARGIN, HUD_HEIGHT  # noqa: E402

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py <config.json>")
        sys.exit(1)

    try:
        data = parsing(sys.argv[1])
    except FileNotFoundError:
        print(f"Error: config file '{sys.argv[1]}' not found.")
        sys.exit(1)
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)

    config = from_dict(data)
    level = config.levels[0]

    maze = load_maze(level.width, level.height, config.seed)
    player = Player(
            maze.width // 2,
            maze.height // 2,
            Direction.EAST,
            config.lives,
            Direction.EAST
        )

    window_width = maze.width * CELL_SIZE + MARGIN * 2
    window_height = maze.height * CELL_SIZE + MARGIN * 2 + HUD_HEIGHT

    game = Game(maze, player, config)
    app = App(window_width, window_height, game)

    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nGood job, you interrupted the game, byebye")
        sys.exit(0)
    except SystemExit:
        raise
    except Exception as error:
        print(f"What did you do to our program ?? "
              f"here's what you did: {error}")
        sys.exit(1)
