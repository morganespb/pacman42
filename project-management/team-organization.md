# Team Organization

## Timeline note

The project started on August 11. Léo was unavailable from
August 15 to September 21 due to a personal health matter, which
significantly shifted the workload during that period. Morgane
kept the project moving solo during that time, building the
majority of the game on her own. Léo rejoined on September 21 and
focused the remaining time on gameplay mechanics, robustness, and
project cleanup. Despite the disruption, both contributors stayed
aligned throughout on the game's direction and design choices.

## Contributions

| Area | Owner |
|---|---|
| Initial config parsing (pre-August 15) | Léo |
| Maze/Cell data model, maze_loader (A-Maze-ing integration) | Morgane |
| Core game structure (Game, Player, App state machine) | Morgane |
| Rendering (display.py, graphics.py), UI/menus, neon effects | Morgane |
| Pygame setup, input handling, assets, sound | Morgane |
| Highscore system | Morgane |
| Ghost AI (BFS pursuit, fleeing, staggered activation, difficulty scaling) | Léo |
| Collision detection, pacgum mechanics, countdown system | Léo |
| Config validation, parsing robustness | Léo |
| Error handling / crash prevention | Léo |
| Tooling (Makefile, flake8/mypy setup) | Léo |
| Final structure cleanup, docstrings, linting pass | Léo |
